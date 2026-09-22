#!/usr/bin/env python3
"""Push a feature-breakdown spec to ClickUp: one parent task + lane subtasks.

Usage:
  tracker_push.py --context PROJECT_CONTEXT.md --spec artifacts/specs/<feature>.md [--dry-run]

Reads the list id, secret ref name and status names from PROJECT_CONTEXT.md,
parses the spec (see reference/spec-format.md), creates the parent first, then
subtasks with `parent`, then task links for depends_on.

A ticket is matched to its board ticket by the `id:` the push writes back into
the spec's own `---ticket` header the first time it creates it. The title is
only a fallback for a ticket that has no id yet: matching by title meant that
editing a `title:` made the ticket look new, so the next push created a
duplicate and left the original's subtasks hanging off a ticket the spec no
longer described (2026-09-22).

Tickets with `figma:`/`screenshots:`/`assets:` get their PNGs
uploaded as ClickUp attachments and a generated `## Design` section (Figma
links + embedded screenshots + asset list) at the top of the description. Writes
<spec>.clickup.json as the completion marker (ClickUp's declared marker suffix;
`.tracker.json` is read too, so a spec never needs migrating). Standard library only.

Tracker support: **ClickUp, Jira and Linear** (2026-09-21). Creating tickets from a spec needs
attachments (Figma screenshots), task-to-task dependency links, markdown
descriptions and per-ticket estimates, and those are shaped very differently on
Jira and Linear. Rather than half-create tickets and silently drop the parts it
cannot do, this script refuses any other tracker and says so.

A Jira or Linear project is not blocked by this: set `Ticket source: human` in
its Flow (the default for `teammate` and `maintenance`), let the team write the
tickets, and adopt them with `tracker_scan.py` + `existing_id:`. Status moves and
reads already work on every tracker through `tracker_status.py`.
"""
import argparse
import difflib
import hashlib
import subprocess
import json
import mimetypes
import os
import re
import sys
import uuid
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.clickup.com/api/v2"
PRIORITY = {"urgent": 1, "high": 2, "normal": 3, "low": 4}
LANES = {"FEATURE", "FE", "BE", "DB", "INT", "QA", "SPIKE"}
MAX_HOURS = 8
DESIGN_LANES = {"FEATURE", "FE"}  # must carry figma links + screenshots when the project has a Figma file
MIN_AC = 3
AC_RX = re.compile(r"^given\b.+\bwhen\b.+\bthen\b.+", re.I | re.S)
FILLER = (
    "looks good", "works correctly", "matches the design", "primary ui elements",
    "basic interactions", "standard stack conventions", "use the system effectively",
    "unrelated features", "functionality, so that",
)


def die(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------- parsing ----------

WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", "/home/openclaw/.openclaw/workspace")
VALIDATOR = os.path.join(WORKSPACE, "projects/_tools/validate_context.py")


def parse_context(path):
    """Delegate to the shared validator so every tool reads PROJECT_CONTEXT.md the same way."""
    import importlib.util
    if not os.path.exists(VALIDATOR):
        die(f"shared validator missing: {VALIDATOR}")
    spec = importlib.util.spec_from_file_location("validate_context", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fields, errors = mod.parse(path)
    if errors:
        die(f"{path} is invalid: " + "; ".join(errors) + f"  (run {VALIDATOR} {path})")
    has_figma = fields.get("figma_file", "none").lower().strip("<>") not in ("none", "")
    return {"tracker": fields.get("tracker", "none"), "fields": fields,
            "list_id": fields["list_id"], "secret_ref": fields["tracker_secret"],
            "statuses": fields["statuses"], "create_status": fields["create_status"],
            "cancelled": (fields.get("status") or {}).get("cancelled") or "cancelled",
            "artifacts_dir": os.path.realpath(fields["artifacts_dir"]), "has_figma": has_figma}


# The parser and the `id:` write-back must agree on where a ticket block starts
# and ends, or the push would write an id into the wrong header.
TICKET_RX = re.compile(r"^---ticket\s*\n(.*?)^---end\s*$", re.S | re.M)


def parse_spec(path):
    text = open(path, encoding="utf-8").read()
    blocks = TICKET_RX.findall(text)
    n_open = len(re.findall(r"^---ticket\s*$", text, re.M))
    n_close = len(re.findall(r"^---end\s*$", text, re.M))
    if not blocks:
        die(f"no ---ticket/---end blocks in {path}")
    if n_open != n_close or n_open != len(blocks):
        die(f"unbalanced markers in {path}: {n_open} '---ticket' vs {n_close} '---end' "
            f"({len(blocks)} parsed). Every ticket needs its own ---end.")
    tickets = []
    for raw in blocks:
        lines = raw.splitlines()
        t, i = {}, 0
        # header = leading 'key: value' lines; stops at first blank or markdown line
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
            k, sep, v = lines[i].partition(":")
            if not sep:
                break
            # A value the author wrapped in quotes is the quotes' fault, not the title's:
            # `title: "[Feature] Fix X"` created a ClickUp task literally named with the
            # quotes, keyed the marker file by the quoted form, and so never matched the
            # unquoted title in duplicate detection (2026-09-19). Strip one matched pair;
            # a bracketed value like `tags: ["a", "b"]` is left alone.
            val = v.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1].strip()
            t[k.strip().lower()] = val
            i += 1
        t["body"] = "\n".join(lines[i:]).strip()
        tickets.append(t)
    return tickets


def spec_id(t):
    """The board id this ticket already carries in its own header, if any.

    `id:` is written back by this script on the push that created the ticket.
    `existing_id:` is the hand-written form, used to adopt a ticket a person
    made; both name the same thing, so both resolve here.
    """
    v = (t.get("id") or t.get("existing_id") or "").strip()
    return v or None


def with_spec_id(block, tid):
    """One `---ticket` block's text with `id: <tid>` added to its header."""
    lines = block.splitlines()
    at = next((i for i, ln in enumerate(lines) if ln.split(":", 1)[0].strip().lower() == "title"), -1)
    lines.insert(at + 1, f"id: {tid}")
    return "\n".join(lines) + "\n"


def inject_ids(spec_path, tickets, ids):
    """Write `id: <board id>` into every `---ticket` header that has none.

    This is what makes the spec, not the title, the stable link to the board. It
    runs after the tickets exist, so a push that died half way leaves the ids of
    what it did create - the next run adopts those instead of duplicating them.

    Returns the titles it wrote an id for.
    """
    text = open(spec_path, encoding="utf-8").read()
    blocks = list(TICKET_RX.finditer(text))
    if len(blocks) != len(tickets):
        print(f"WARNING: {spec_path} changed on disk during the push ({len(blocks)} blocks, "
              f"{len(tickets)} tickets); `id:` was NOT written back. Add it by hand from the "
              f"marker file, or the next push will match by title again.", file=sys.stderr)
        return []
    out, written, at = [], [], 0
    for m, t in zip(blocks, tickets):
        tid = ids.get(t["title"])
        if t.get("id") or not tid or str(tid).startswith("dry-"):
            continue
        out.append(text[at:m.start(1)])
        out.append(with_spec_id(m.group(1), tid))
        at = m.end(1)
        written.append(t["title"])
    if not written:
        return []
    out.append(text[at:])
    tmp = spec_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("".join(out))
    os.replace(tmp, spec_path)
    return written


def split_list(v):
    return [x.strip() for x in (v or "").split(",") if x.strip()]


def screenshot_paths(t, ctx):
    """Resolve `screenshots:` entries; relative paths are relative to Internal Artifacts."""
    out = []
    for p in split_list(t.get("screenshots")):
        if p.lower() == "none":
            continue
        full = os.path.realpath(p if os.path.isabs(p) else os.path.join(ctx["artifacts_dir"], p))
        out.append((p, full))
    return out


def asset_manifest(t, ctx):
    """Resolve `assets:` to (raw, full, manifest-or-None, error-or-None).

    The manifest is the machine-checkable half of `## Design fidelity`: it names
    every file `download_figma_images` wrote for this feature and where the code
    should put it. `"assets": []` is valid and means the screen is CSS only.
    """
    raw = (t.get("assets") or "").strip()
    if not raw or raw.lower() == "none":
        return None, None, None, None
    full = os.path.realpath(raw if os.path.isabs(raw) else os.path.join(ctx["artifacts_dir"], raw))
    if not full.startswith(ctx["artifacts_dir"] + os.sep):
        return raw, full, None, "asset manifest outside Internal Artifacts"
    if not os.path.isfile(full):
        return raw, full, None, "asset manifest file not found"
    try:
        data = json.load(open(full, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return raw, full, None, f"asset manifest is not readable JSON ({e})"
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        return raw, full, None, "asset manifest needs an 'assets' list (use [] when the screen is CSS only)"
    return raw, full, data, None


def asset_entry_errors(title, raw, full, data):
    """Every listed file must exist, be non-empty, and stay inside the feature folder.

    `file` is relative to the feature folder (`specs/_figma/<feature-slug>/`), not
    to the manifest's own `assets/` directory: that is the form the ticket's
    `## Design fidelity` section quotes, so the two always read the same.
    """
    errors = []
    feature_dir = os.path.dirname(os.path.dirname(full))  # .../<feature-slug>/assets/manifest.json
    # The binaries beside the manifest are a gitignored, reproducible cache (.gitignore).
    # A whole folder that was never materialised - fresh clone, or `worktree.py sweep` after
    # 30 days - is not the same defect as one missing file, and it has a different fix.
    cache = os.path.dirname(full)
    present = {f for f in os.listdir(cache) if f != "manifest.json"} if os.path.isdir(cache) else set()
    if data["assets"] and not present:
        return [f"{title}: the asset cache for {raw} is empty - re-create it with download_figma_images "
                f"using the manifest's file_key, png_scale and per-asset download blocks "
                f"(localPath = that assets/ folder), then push again"]
    for i, a in enumerate(data["assets"]):
        where = f"{title}: asset manifest {raw} entry {i}"
        if not isinstance(a, dict):
            errors.append(f"{where} is not an object")
            continue
        for key in ("file", "node", "repo_path"):
            if not str(a.get(key, "")).strip():
                errors.append(f"{where} has no '{key}'")
        f = str(a.get("file", "")).strip()
        if not f:
            continue
        fp = os.path.realpath(os.path.join(feature_dir, f))
        if not (fp == feature_dir or fp.startswith(feature_dir + os.sep)):
            errors.append(f"{where}: file escapes the feature folder: {f}")
        elif not os.path.isfile(fp):
            errors.append(f"{where}: file not found: {f}")
        elif os.path.getsize(fp) == 0:
            errors.append(f"{where}: file is 0 bytes (the download failed): {f}")
    return errors


def section(body, heading):
    m = re.search(rf"^## {re.escape(heading)}[^\n]*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return m.group(1) if m else ""


def ac_bullets(body):
    items, cur = [], None
    for line in section(body, "Acceptance criteria").splitlines():
        if re.match(r"^\s*[-*] ", line):
            cur = re.sub(r"^\s*[-*] ", "", line).strip()
            items.append(cur)
        elif cur is not None and line.strip():
            items[-1] += " " + line.strip()
    return items


HEDGES = (" (or ", "(if ", "if missing", "if not present", "if applicable", "assuming",
          "later db ticket", "later ticket", "a separate ticket")
HEDGE_SECTIONS = ("Acceptance criteria", "In scope", "Technical notes")
NODE_RX = re.compile(r"node-id=([0-9]+[-:][0-9]+)")
TABLE_RX = re.compile(r"\bcreat\w*\s+(?:the\s+|an?\s+)?`(\w+)`\s+table", re.I)
ORM_RX = re.compile(r"\b(set ?up|choose)\b[^\n]{0,40}\bORM\b", re.I)
OTHER_DEP_RX = re.compile(r"^- Depends on \(other feature\):\s*(.+)$", re.M)


def specs_root(spec_path):
    d = os.path.dirname(os.path.realpath(spec_path))
    return os.path.dirname(d) if os.path.basename(d) in ("_done", "_superseded") else d


def other_specs(spec_path):
    """Pushed specs (have a .clickup.json marker): active ones in specs/, finished ones in specs/_done/.
    Specs in specs/_superseded/ were cancelled and are ignored. Yields (name, tickets, is_active)."""
    root, me = specs_root(spec_path), os.path.realpath(spec_path)
    for sub, active in (("", True), ("_done", False)):
        d = os.path.join(root, sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            full = os.path.join(d, f)
            if f.endswith(".md") and not f.startswith("_") and full != me \
                    and any(os.path.exists(full[:-3] + s)
                            for s in (".tracker.json", ".clickup.json")):
                try:
                    parsed = parse_spec(full)
                except SystemExit:
                    # This scan exists to warn about duplicate titles across specs.
                    # One unparseable spec elsewhere in the folder must not block
                    # the push of THIS one - it used to die here, so a single
                    # malformed file stopped every later push on the project.
                    print(f"note: skipping unreadable spec {f} in the duplicate check",
                          file=sys.stderr)
                    continue
                yield os.path.join(sub, f) if sub else f, parsed, active


def cross_spec_errors(tickets, spec_path):
    """Catch overlap with other features: same Figma screen, second ORM setup, same table, dangling cross-feature deps."""
    errors = []
    others = list(other_specs(spec_path))
    all_titles = {t.get("title") for _, ts, _a in others for t in ts} | {t.get("title") for t in tickets}
    mine_nodes = set(NODE_RX.findall(tickets[0].get("figma", "")))
    my_db = " ".join(section(t["body"], "In scope") for t in tickets if t.get("lane") == "DB")
    for f, ts, active in others:
        overlap = mine_nodes & set(NODE_RX.findall(ts[0].get("figma", ""))) if active else set()
        if overlap:
            errors.append(f"Figma node(s) {sorted(overlap)} are already the feature of {f}: update that spec, "
                          f"or move the superseded one to specs/_superseded/ after cancelling its tickets")
        their_db = " ".join(section(t["body"], "In scope") for t in ts if t.get("lane") == "DB")
        if ORM_RX.search(my_db) and ORM_RX.search(their_db):
            errors.append(f"ORM/database setup is already a [DB] ticket in {f}: depend on it instead")
        for tbl in set(TABLE_RX.findall(my_db)) & set(TABLE_RX.findall(their_db)):
            errors.append(f"table `{tbl}` is already created in {f}: add columns with a migration instead")
    for t in tickets:
        for dep in OTHER_DEP_RX.findall(t["body"]):
            name = re.sub(r"\s*\([^)]*\)\s*$", "", dep).strip()
            if name not in all_titles:
                errors.append(f"{t.get('title')}: 'Depends on (other feature): {name}' is not a ticket in any pushed spec")
        text = " ".join(section(t["body"], h) for h in HEDGE_SECTIONS).lower()
        for h in HEDGES:
            if h in text:
                errors.append(f"{t.get('title')}: vague wording '{h.strip()}' in AC/scope/notes: decide it, "
                              f"name the exact ticket, or make it an open question / [SPIKE]")
    return errors

SIMILAR = 0.82  # title similarity (0-1) that counts as "probably the same ticket"


def norm_title(t):
    return re.sub(r"[^a-z0-9 ]+", " ", re.sub(r"^\[[A-Za-z]+\]\s*", "", t.lower())).split()


def similar_tickets(title, live, skip_ids):
    """Live tickets (any author, not cancelled) whose title is close to `title` but not identical."""
    mine = " ".join(norm_title(title))
    out = []
    for task in live:
        if task["id"] in skip_ids or task["name"] == title:
            continue
        # The adapters normalise a ticket to `closed` + a plain `status` string;
        # this used to read ClickUp's raw `{"status": {"status": ...}}` shape.
        if task.get("closed"):
            continue
        r = difflib.SequenceMatcher(None, mine, " ".join(norm_title(task["name"]))).ratio()
        if r >= SIMILAR:
            raw = task.get("tags") or []
            tags = {x.get("name") if isinstance(x, dict) else str(x) for x in raw}
            who = "agent" if "agent-created" in tags else "a person"
            out.append(f"{task['id']} '{task['name']}' (by {who}, {r:.0%} similar)")
    return out


def desc_hash(task):
    d = task.get("markdown_description") or task.get("description") or ""  # adapter uses `description`
    return hashlib.sha256(d.strip().encode()).hexdigest()[:16]


def validate(tickets, ctx, spec_path=None):
    errors = cross_spec_errors(tickets, spec_path) if spec_path else []
    fe_design = []  # (title, claimed repo paths, manifest path, manifest) per [FE] ticket
    titles = [t.get("title") for t in tickets]
    if len(set(titles)) != len(titles):
        errors.append("duplicate titles in spec")
    # Two tickets pointing at one board ticket would have the second overwrite the
    # first every push, which reads as "my ticket keeps changing" and never as an error.
    seen_ids = {}
    for t in tickets:
        tid = spec_id(t)
        if not tid:
            continue
        if tid.startswith("<") or tid.endswith(">"):
            errors.append(f"{t.get('title')}: `id: {tid}` is still the template placeholder - "
                          f"put the real ticket id there, or delete the line and let the push create it")
        elif tid in seen_ids:
            errors.append(f"{t.get('title')}: id {tid} is also claimed by '{seen_ids[tid]}' - "
                          f"one spec ticket per board ticket")
        else:
            seen_ids[tid] = t.get("title")
    parent = tickets[0]
    if parent.get("lane") != "FEATURE":
        errors.append("first ticket must have lane: FEATURE")
    for t in tickets:
        title = t.get("title") or "<untitled>"
        if not t.get("title"):
            errors.append("a ticket has no title")
        lane = t.get("lane", "")
        if lane not in LANES:
            errors.append(f"{title}: lane must be one of {sorted(LANES)}")
        if t is not parent:
            if t.get("parent") != parent["title"]:
                errors.append(f"{title}: parent must equal '{parent['title']}'")
            try:
                h = float(t.get("estimate_hours", ""))
                if h > MAX_HOURS or h <= 0:
                    errors.append(f"{title}: estimate_hours {h} not in (0, {MAX_HOURS}] — split it")
            except ValueError:
                errors.append(f"{title}: estimate_hours missing or not a number")
        if t.get("priority") and t["priority"].lower() not in PRIORITY:
            errors.append(f"{title}: priority must be one of {list(PRIORITY)}")
        for dep in deps_of(t):
            if dep not in titles:
                errors.append(f"{title}: depends_on '{dep}' is not a ticket in this spec")
        body = t["body"]
        if "## Acceptance criteria" not in body:
            errors.append(f"{title}: body lacks '## Acceptance criteria'")
        if "## Out of scope" not in body:
            errors.append(f"{title}: body lacks '## Out of scope'")
        if len(body) < 200:
            errors.append(f"{title}: body is too short to be a real ticket ({len(body)} chars)")
        for bad in FILLER:
            if bad in body.lower():
                errors.append(f"{title}: contains filler/unverifiable phrase '{bad}'")
        acs = ac_bullets(body)
        if len(acs) < MIN_AC:
            errors.append(f"{title}: needs at least {MIN_AC} acceptance criteria bullets (found {len(acs)})")
        for ac in acs:
            if not AC_RX.match(ac):
                errors.append(f"{title}: AC not in 'Given <state>, when <action>, then <result>' form: {ac[:90]}")
        links = [u for u in split_list(t.get("figma")) if u.lower() != "none"]
        for u in links:
            if not re.match(r"https://www\.figma\.com/(design|file)/[A-Za-z0-9]+/.*node-id=", u):
                errors.append(f"{title}: figma link must be a figma.com design URL with node-id: {u}")
        shots = screenshot_paths(t, ctx)
        for raw, full in shots:
            if not full.startswith(ctx["artifacts_dir"] + os.sep):
                errors.append(f"{title}: screenshot outside Internal Artifacts: {raw}")
            elif not os.path.isfile(full):
                errors.append(f"{title}: screenshot file not found: {raw}")
            elif not full.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
                errors.append(f"{title}: screenshot must be png/jpg/gif: {raw}")
            # A failed download leaves a 0-byte file behind and every later check passes:
            # 9794-6547.png sat empty in fms-studio for five days (2026-09-21 audit).
            elif os.path.getsize(full) == 0:
                errors.append(f"{title}: screenshot is 0 bytes (the download failed): {raw}")
        a_raw, a_full, a_data, a_err = asset_manifest(t, ctx)
        if a_err:
            errors.append(f"{title}: {a_err}: {a_raw}")
        elif a_data:
            errors.extend(asset_entry_errors(title, a_raw, a_full, a_data))
        # A spec with no [FE] ticket has no screen (CI, backend, data work): its parent needs no Figma.
        # Before 2026-09-19 it did, and agents pasted dummy PNGs + a fake node-id to get past this check.
        needs_design = lane == "FE"
        if ctx["has_figma"] and lane in DESIGN_LANES and needs_design:
            if not links:
                errors.append(f"{title}: {lane} ticket needs 'figma:' (the frame link(s) it implements)")
            if not shots:
                errors.append(f"{title}: {lane} ticket needs 'screenshots:' (PNG from download_figma_images)")
            # The screenshot is a picture OF the screen; it is not the artwork the code ships.
            # Without these two the coding agent invents placeholders - it did for every
            # fms-studio screen built before 2026-09-21 (a text "Logo", a grey collage box).
            if not a_raw:
                errors.append(f"{title}: {lane} ticket needs 'assets:' (the asset manifest from "
                              f"download_figma_images; use one with \"assets\": [] if the screen is CSS only)")
            if "## Design fidelity" not in body:
                errors.append(f"{title}: {lane} ticket needs a '## Design fidelity' section "
                              f"(exact tokens + the asset list with repo paths)")
            else:
                fid = section(body, "Design fidelity")
                if not re.search(r"#[0-9A-Fa-f]{3,8}\b", fid):
                    errors.append(f"{title}: '## Design fidelity' names no colour as hex "
                                  f"(\"orange\" is not a token, `#FF6100` is)")
                # Which of the feature's assets THIS ticket ships. A feature usually has
                # several [FE] tickets (layout, states, wiring, a copy fix) sharing one
                # manifest, and only some of them ship artwork - so ownership is checked
                # across the spec below, not ticket by ticket.
                known = {str(a.get("repo_path", "")).strip() for a in (a_data or {}).get("assets", [])}
                claimed = {rp for rp in known if rp and rp in fid}
                for rp in re.findall(r"`([^`]+\.(?:png|jpe?g|gif|svg|webp|avif))`", fid):
                    if rp not in known and not any(rp == str(a.get("file", "")).strip()
                                                   for a in (a_data or {}).get("assets", [])):
                        errors.append(f"{title}: '## Design fidelity' names {rp}, which is not in the "
                                      f"asset manifest - download it first, or fix the path")
                fe_design.append((title, claimed, a_raw, a_data))
    # Asset ownership, across the spec: every asset the feature downloaded is shipped by
    # exactly one [FE] ticket. One ticket owning none is fine (a copy fix, a wiring ticket);
    # an asset owned by NOBODY is how a logo stays in Internal Artifacts forever, and one
    # owned by two tickets is two developers writing the same file.
    for manifest_path in {p for _, _, p, _ in fe_design if p}:
        entries = next((d for _, _, p, d in fe_design if p == manifest_path and d), None)
        for a in (entries or {}).get("assets", []):
            rp = str(a.get("repo_path", "")).strip()
            if not rp:
                continue
            owners = [t for t, claimed, p, _ in fe_design if p == manifest_path and rp in claimed]
            if not owners:
                errors.append(f"asset {rp} ({manifest_path}) is in no ticket's '## Design fidelity': "
                              f"nothing will ever copy it into the repo")
            elif len(owners) > 1:
                errors.append(f"asset {rp} is claimed by {len(owners)} tickets ({', '.join(owners)}): "
                              f"exactly one ticket ships each file")
    if errors:
        print("Spec rejected:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(2)


def deps_of(t):
    return [d.strip() for d in t.get("depends_on", "").split(",") if d.strip()]


# ---------- the board, through the shared tracker adapters ----------

class Board:
    """The spec push expressed in terms any tracker adapter can answer.

    This script used to carry its own ClickUp REST client, which is the only
    reason it was ClickUp-only. Everything now goes through
    projects/_tools/trackers, so a project on Jira or Linear can run the full
    `factory` flow - spec in, tickets out - instead of being told to have humans
    write the tickets by hand.

    Dry-run stays in the shim rather than the adapters: the adapters are shared
    with the watcher and the MCP server, and a tracker that quietly does nothing
    is exactly what they must never be.
    """

    def __init__(self, tk, dry):
        self.tk, self.dry = tk, dry

    def statuses(self):
        return self.tk.board_info()[1] or []

    def list_tasks(self):
        """Live tickets as the push loop wants them: `name` is the dedupe key."""
        return [dict(v, name=v.get("title")) for v in self.tk.tasks().values()]

    def create(self, payload):
        if self.dry:
            print(f"DRY-RUN create: {payload['title']}  status={payload.get('status')!r} "
                  f"tags={payload.get('tags')} parent={payload.get('parent')}")
            return {"id": f"dry-{abs(hash(payload['title'])) % 10**6}", "url": "(dry-run)"}
        t = self.tk.create_task(payload["title"],
                                description=payload.get("description", ""),
                                status=payload.get("status"),
                                parent=payload.get("parent"),
                                tags=payload.get("tags"),
                                estimate_hours=payload.get("estimate_hours"),
                                priority=payload.get("priority"))
        return {"id": t["id"], "url": t.get("url", "")}

    def update(self, tid, payload):
        fields = {k: v for k, v in payload.items() if k in ("title", "description", "tags")}
        if self.dry:
            print(f"DRY-RUN update {tid}: {sorted(fields)}")
            return {"id": tid, "url": "(dry-run)"}
        self.tk.update_task(tid, **fields)
        return {"id": tid, "url": self.tk.task_url(tid)}

    def set_status(self, tid, status):
        """Status is its own call on every adapter.

        `update({"status": ...})` looks like it would work and does not: update()
        only forwards the description fields, so --prune printed "pruned" while
        the ticket stayed open on the board.
        """
        if self.dry:
            print(f"DRY-RUN status {tid} -> {status}")
            return
        self.tk.set_status(tid, status)

    def link(self, tid, other):
        if self.dry:
            print(f"DRY-RUN link {tid} -> {other}")
            return
        try:
            self.tk.link_tasks(tid, other)
        except Exception as e:  # noqa: BLE001
            # A dependency link is worth reporting, never worth losing the push over:
            # the tickets exist and the marker is about to be written.
            print(f"WARNING: could not link {tid} -> {other}: {e}", file=sys.stderr)

    def get_task(self, tid, markdown=False):
        return self.tk.get_task(tid)

    def attachments(self, tid):
        try:
            return self.tk.attachments(tid)
        except Exception:  # noqa: BLE001 - absent is the same as none for idempotency
            return []

    def upload(self, tid, path, filename):
        if self.dry:
            print(f"DRY-RUN upload {tid} <- {filename} ({os.path.getsize(path)} bytes)")
            return {"url": f"(dry-run)/{filename}", "title": filename}
        return self.tk.attach(tid, path, filename)


def resolve_status(wanted, names, fallback):
    """The board's own spelling of the status a new ticket starts in.

    `names` is the plain list the adapter's board_info() returns, so this is the
    same check on ClickUp, Jira and Linear.
    """
    for w in (wanted, fallback):
        if not w:
            continue
        for n in names:
            if n.lower() == w.lower():
                return n
    die(f"status '{wanted or fallback}' not in board statuses {names}; fix PROJECT_CONTEXT.md")


def attachment_name(raw):
    """Attachment title = file name (e.g. 9884-4390.png); also the per-task dedupe key."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(raw))


def design_section(t, uploaded, manifest=None):
    """Generated header: Figma links, the embedded screenshots, and the asset list.

    The asset list is what someone reading the ticket on the board needs to see:
    which files the design ships and where they belong in the repo. The ticket's
    own `## Design fidelity` section (written by VanPM) carries the tokens.
    """
    links = split_list(t.get("figma"))
    assets = (manifest or {}).get("assets") or []
    if not links and not uploaded and not assets:
        return ""
    lines = ["## Design"]
    lines += [f"- Figma: {u}" for u in links]
    if manifest is not None:
        if assets:
            lines += ["", "Assets to ship (from the Figma file, already downloaded):"]
            for a in assets:
                label = str(a.get("name") or a.get("file") or "").strip()
                lines.append(f"- `{a.get('file')}` -> `{a.get('repo_path')}`" + (f" - {label}" if label else ""))
        else:
            lines += ["", "Assets to ship: none (this screen is CSS only)."]
    for name, url in uploaded:
        lines += ["", f"![{name}]({url})"]
    return "\n".join(lines) + "\n\n"


def strip_design(body):
    return re.sub(r"^## Design\n.*?(?=^## |\Z)", "", body, flags=re.S | re.M).lstrip()


def build_payload(t, status, parent_id=None):
    lane = t["lane"]
    tags = ["agent-created", lane.lower()] + [x.strip() for x in t.get("tags", "").split(",") if x.strip()]
    p = {
        "title": t["title"],
        "description": t["body"],
        "status": status,
        "tags": sorted(set(tags)),
        "priority": t.get("priority", "normal").lower(),
    }
    if t.get("estimate_hours"):
        p["estimate_hours"] = float(t["estimate_hours"])
    if parent_id:
        p["parent"] = parent_id
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prune", action="store_true",
                    help="move tickets from a previous push of this spec that are no longer in it to the 'cancelled' status")
    ap.add_argument("--allow-similar", action="store_true",
                    help="create tickets even if a live ticket has a similar title (after checking it is not the same work)")
    ap.add_argument("--overwrite-edits", action="store_true",
                    help="overwrite tickets whose description someone edited in ClickUp since the last push")
    a = ap.parse_args()

    ctx = parse_context(a.context)
    if ctx["tracker"] == "none":
        die("this project has `Tracker: none`; there is no board to create tickets on.", 4)
    tickets = parse_spec(a.spec)
    validate(tickets, ctx, a.spec)

    token = os.environ.get(ctx["secret_ref"])
    if not token and not a.dry_run:
        die(f"token not found in env: {ctx['secret_ref']} (the Tracker SecretRef in {a.context})")
    sys.path.insert(0, os.path.dirname(VALIDATOR))
    import trackers                                        # noqa: E402
    cu = Board(trackers.for_project(ctx["fields"], token), a.dry_run)

    # The marker keeps whichever name it already has; a new one uses the
    # provider's own suffix (ClickUp keeps `.clickup.json` so live specs are
    # never orphaned).
    base = re.sub(r"\.md$", "", a.spec)
    marker_path = next((base + s for s in (".tracker.json", ".clickup.json")
                        if os.path.exists(base + s)), base + cu.tk.marker_suffix)
    marker = json.load(open(marker_path)) if os.path.exists(marker_path) else {}

    if a.dry_run and not token:
        print("DRY-RUN without token: skipping list lookup, status mapping unverified")
        status = ctx["create_status"] or "to do"
        existing, live_tasks = {}, []
    else:
        status = resolve_status(ctx["create_status"], cu.statuses(), "to do")
        live_tasks = cu.list_tasks()
        existing = {t["name"]: t for t in live_tasks}

    print(f"list={ctx['list_id']} status='{status}' tickets={len(tickets)} existing_in_list={len(existing)}")

    # The marker stays keyed by title - spec_index.py and delivery_watch.py read it
    # that way - but the push resolves through this index, because the id is the
    # half that survives someone rewriting a `title:`.
    by_id = {m["id"]: (title, m) for title, m in marker.items()
             if isinstance(m, dict) and m.get("id") and not title.startswith("_")}

    # A declared id that names nothing is the one case where falling back to the
    # title would recreate the very duplicate this id exists to prevent. Check them
    # all first, and say which, rather than failing on the first write.
    if not (a.dry_run and not token):
        live_by_id = {t["id"]: t for t in live_tasks}
        gone = []
        for t in tickets:
            tid = spec_id(t)
            if not tid or tid in live_by_id:
                continue
            try:
                cu.get_task(tid)          # may sit outside this list and still be real
            except Exception as e:        # noqa: BLE001 - any read failure is the same answer
                gone.append(f"  - '{t['title']}' declares id {tid}, which {ctx['tracker']} "
                            f"cannot read ({e})")
        if gone:
            print("Ticket ids in the spec that the board does not have (nothing was written):",
                  file=sys.stderr)
            print("\n".join(gone), file=sys.stderr)
            print("If the ticket was deleted, remove that `id:` line and the push will create a "
                  "fresh one. If it moved to another board, fix the id. Do not leave it: matching "
                  "by title instead is what created duplicates.", file=sys.stderr)
            sys.exit(5)

    ids = {}
    created = updated = 0
    # Before any write: a NEW ticket whose title is close to a live one (anyone's) is probably a duplicate.
    known = {m.get("id") for m in marker.values() if isinstance(m, dict)}
    known |= {spec_id(t) for t in tickets if spec_id(t)}
    clashes = []
    for t in tickets:
        if spec_id(t) or marker.get(t["title"]) or existing.get(t["title"]):
            continue
        for hit in similar_tickets(t["title"], live_tasks, known):
            clashes.append(f"  - new '{t['title']}' ~ {hit}")
    if clashes and not a.allow_similar:
        print("Possible duplicates in the list (nothing was written):", file=sys.stderr)
        print("\n".join(clashes), file=sys.stderr)
        print("Same work → put `existing_id: <id>` in that ticket's header to adopt it. Different work → "
              "rename it so the difference is clear, or re-run with --allow-similar and say why in your report.",
              file=sys.stderr)
        sys.exit(3)

    skipped = []
    for i, t in enumerate(tickets):
        parent_id = None if i == 0 else ids[tickets[0]["title"]]
        payload = build_payload(t, t.get("status") or status, parent_id)
        # id first, title only for a ticket that has never been pushed.
        target = (spec_id(t) or marker.get(t["title"], {}).get("id")
                  or (existing.get(t["title"]) or {}).get("id"))
        # ...and the marker entry comes from the same id, so a renamed ticket keeps
        # its uploaded attachments and its edit fingerprint instead of looking new.
        prev_title, prev = by_id.get(target) or (t["title"], marker.get(t["title"]) or {})
        prev_hash = prev.get("desc_hash")
        if target and prev_hash and not a.dry_run and not a.overwrite_edits:
            if desc_hash(cu.get_task(target, markdown=True)) != prev_hash:
                ids[t["title"]] = target
                skipped.append(t["title"])
                print(f"skipped  {t['lane']:7} {target:14} {t['title']} (description edited on the board since "
                      f"the last push; merge the edit into the spec, or re-run with --overwrite-edits)")
                continue
        if target:
            # re-push never changes status: a spec `status:` header only applies when the ticket is
            # created. Workflow statuses move only through clickup_status.py.
            payload.pop("status", None)
            r = cu.update(target, payload)
            updated += 1
            action = "updated"
        else:
            r = cu.create(payload)
            created += 1
            action = "created"
        ids[t["title"]] = r["id"]
        done = dict(prev.get("attachments", {}))  # attachment name -> url (idempotency)
        if not a.dry_run and target:
            for att in cu.attachments(r["id"]):
                if att.get("title") and att.get("url"):
                    done.setdefault(att["title"], att["url"])
        shots = []
        for raw, full in screenshot_paths(t, ctx):
            name = attachment_name(raw)
            if name not in done:
                up = cu.upload(r["id"], full, name)
                done[name] = up.get("url", "")
                print(f"uploaded {name}")
            shots.append((name, done[name]))
        _, _, a_data, _ = asset_manifest(t, ctx)
        if split_list(t.get("figma")) or shots or a_data:
            body = design_section(t, shots, a_data) + strip_design(t["body"])
            cu.update(r["id"], {"description": body})
        marker[t["title"]] = {"id": r["id"], "url": r.get("url", ""), "lane": t["lane"],
                              "attachments": {n: u for n, u in done.items() if n in dict(shots)}}
        if prev_title != t["title"] and prev_title in marker:
            # The ticket was renamed in the spec. Drop the entry under the old title,
            # or it would sit in the marker for ever and read as a stale ticket.
            del marker[prev_title]
            print(f"renamed  {t['lane']:7} {r['id']:14} '{prev_title}' -> '{t['title']}'")
        if not a.dry_run:  # fingerprint what ClickUp now holds, to detect later hand edits
            marker[t["title"]]["desc_hash"] = desc_hash(cu.get_task(r["id"], markdown=True))
        print(f"{action:8} {t['lane']:7} {r['id']:14} {t['title']}")

    # Stamp the spec with the ids before anything else can fail: the marker, the
    # dependency links and the verify pass are all recoverable, an unstamped
    # ticket is what the next push turns into a duplicate.
    if a.dry_run:
        need = [t["title"] for t in tickets if not t.get("id")]
        if need:
            print(f"DRY-RUN would write `id:` into {len(need)} ticket header(s) in "
                  f"{os.path.basename(a.spec)}")
    else:
        stamped = inject_ids(a.spec, tickets, ids)
        if stamped:
            print(f"spec stamped with {len(stamped)} ticket id(s): {os.path.basename(a.spec)} "
                  f"(commit it - it is how the next push finds these tickets)")

    for t in tickets:
        for dep in deps_of(t):
            cu.link(ids[t["title"]], ids[dep])

    # tickets from an earlier push of this spec that the rewrite no longer contains
    live_ids = set(ids.values())
    stale = {title: m for title, m in marker.items()
             if title not in ids and m.get("id") not in live_ids and not title.startswith("_")}
    for title, m in stale.items():
        if a.prune:
            cancel = (ctx["cancelled"] if (a.dry_run and not token)
                      else resolve_status(ctx["cancelled"], cu.statuses(), None))
            cu.set_status(m["id"], cancel)
            marker.setdefault("_cancelled", {})[title] = m
            del marker[title]
            print(f"pruned   {m.get('lane', ''):7} {m['id']:14} {title} -> {cancel}")
        else:
            print(f"STALE    {m.get('lane', ''):7} {m['id']:14} {title} (not in spec; re-run with --prune to cancel it)")

    if not a.dry_run:
        with open(marker_path, "w", encoding="utf-8") as f:
            json.dump(marker, f, indent=2)
        # Count children by asking which tickets NAME this parent, rather than
        # reading a provider-specific `subtasks` array. ClickUp returns one,
        # Jira puts it under fields.subtasks and Linear calls them sub-issues, so
        # the old read found 0 on Jira and printed MISMATCH for a push that had
        # in fact created both subtasks correctly. A false failure is worse than
        # no check.
        parent_id = ids[tickets[0]["title"]]
        parent = cu.get_task(parent_id)
        found = sum(1 for t2 in tickets[1:]
                    if (cu.get_task(ids[t2["title"]]).get("parent") or "") == parent_id)
        expected = len(tickets) - 1
        ok = "OK" if found >= expected else "MISMATCH"
        print(f"VERIFY {ok}: parent {parent.get('id', parent_id)} {parent.get('url','')} "
              f"children found={found} expected={expected}")
        for t in tickets:
            names = [attachment_name(raw) for raw, _ in screenshot_paths(t, ctx)]
            if not names and not split_list(t.get("figma")):
                continue
            live = cu.get_task(ids[t["title"]], markdown=True)
            have = {x.get("title") for x in cu.attachments(ids[t["title"]])}
            desc = live.get("markdown_description") or live.get("description") or ""
            missing = [n for n in names if n not in have]
            links_ok = all(u in desc for u in split_list(t.get("figma")))
            embedded = sum(1 for n in names if n in desc)
            state = "OK" if not missing and links_ok and "Design" in desc else "MISMATCH"
            print(f"VERIFY {state}: {t['title']} attachments={len(names) - len(missing)}/{len(names)} "
                  f"figma_links_in_description={'yes' if links_ok else 'NO'} screenshots_referenced_in_description={embedded}/{len(names)}")
        print(f"marker written: {marker_path}")
        slug = os.path.basename(os.path.dirname(os.path.realpath(a.context)))
        subprocess.run([sys.executable, os.path.join(WORKSPACE, "projects/_tools/spec_index.py"), slug])
    if skipped:
        print(f"SKIPPED (edited by someone in ClickUp): {len(skipped)}: " + "; ".join(skipped))
    print(f"done: created={created} updated={updated}")


if __name__ == "__main__":
    main()
