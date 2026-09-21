#!/usr/bin/env python3
"""Push a feature-breakdown spec to ClickUp: one parent task + lane subtasks.

Usage:
  tracker_push.py --context PROJECT_CONTEXT.md --spec artifacts/specs/<feature>.md [--dry-run]

Reads the list id, secret ref name and status names from PROJECT_CONTEXT.md,
parses the spec (see reference/spec-format.md), dedupes by exact title against
the list, creates the parent first, then subtasks with `parent`, then task
links for depends_on. Tickets with `figma:`/`screenshots:` get their PNGs
uploaded as ClickUp attachments and a generated `## Design` section (Figma
links + embedded screenshots) at the top of the description. Writes
<spec>.clickup.json as the completion marker (ClickUp's declared marker suffix;
`.tracker.json` is read too, so a spec never needs migrating). Standard library only.

Tracker support: **ClickUp only, for now.** Creating tickets from a spec needs
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

VALIDATOR = "/home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py"


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
    return {"tracker": fields.get("tracker", "none"),
            "list_id": fields["list_id"], "secret_ref": fields["tracker_secret"],
            "statuses": fields["statuses"], "create_status": fields["create_status"],
            "cancelled": (fields.get("status") or {}).get("cancelled") or "cancelled",
            "artifacts_dir": os.path.realpath(fields["artifacts_dir"]), "has_figma": has_figma}


def parse_spec(path):
    text = open(path, encoding="utf-8").read()
    blocks = re.findall(r"^---ticket\s*\n(.*?)^---end\s*$", text, re.S | re.M)
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
                    and os.path.exists(full[:-3] + ".clickup.json"):
                yield os.path.join(sub, f) if sub else f, parse_spec(full), active


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
        if (task.get("status") or {}).get("status", "").lower() in ("cancelled", "closed"):
            continue
        r = difflib.SequenceMatcher(None, mine, " ".join(norm_title(task["name"]))).ratio()
        if r >= SIMILAR:
            tags = {x.get("name") for x in task.get("tags") or []}
            who = "agent" if "agent-created" in tags else "a person"
            out.append(f"{task['id']} '{task['name']}' (by {who}, {r:.0%} similar)")
    return out


def desc_hash(task):
    d = task.get("markdown_description") or task.get("description") or ""
    return hashlib.sha256(d.strip().encode()).hexdigest()[:16]


def validate(tickets, ctx, spec_path=None):
    errors = cross_spec_errors(tickets, spec_path) if spec_path else []
    titles = [t.get("title") for t in tickets]
    if len(set(titles)) != len(titles):
        errors.append("duplicate titles in spec")
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
        # A spec with no [FE] ticket has no screen (CI, backend, data work): its parent needs no Figma.
        # Before 2026-09-19 it did, and agents pasted dummy PNGs + a fake node-id to get past this check.
        needs_design = lane == "FE"
        if ctx["has_figma"] and lane in DESIGN_LANES and needs_design:
            if not links:
                errors.append(f"{title}: {lane} ticket needs 'figma:' (the frame link(s) it implements)")
            if not shots:
                errors.append(f"{title}: {lane} ticket needs 'screenshots:' (PNG from download_figma_images)")
    if errors:
        print("Spec rejected:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(2)


def deps_of(t):
    return [d.strip() for d in t.get("depends_on", "").split(",") if d.strip()]


# ---------- ClickUp ----------

class ClickUp:
    def __init__(self, token, dry):
        self.token = token
        self.dry = dry

    def _req(self, method, path, body=None, query=None):
        url = f"{API}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Authorization": self.token,
                                              "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            die(f"{method} {path} -> {e.code}: {e.read().decode()[:500]}")

    def get_list(self, list_id):
        return self._req("GET", f"/list/{list_id}")

    def list_tasks(self, list_id):
        tasks, page = [], 0
        while True:
            r = self._req("GET", f"/list/{list_id}/task",
                          query={"include_closed": "true", "subtasks": "true", "page": page})
            tasks += r.get("tasks", [])
            if r.get("last_page", True) or not r.get("tasks"):
                return tasks
            page += 1

    def create(self, list_id, payload):
        if self.dry:
            print(f"DRY-RUN create: {json.dumps(payload, indent=2)[:1200]}")
            return {"id": f"dry-{abs(hash(payload['name'])) % 10**6}", "url": "(dry-run)"}
        return self._req("POST", f"/list/{list_id}/task", payload)

    def update(self, task_id, payload):
        payload = {k: v for k, v in payload.items() if k != "parent"}  # parent is immutable via PUT
        if self.dry:
            print(f"DRY-RUN update {task_id}: {json.dumps(payload, indent=2)[:1200]}")
            return {"id": task_id, "url": "(dry-run)"}
        return self._req("PUT", f"/task/{task_id}", payload)

    def link(self, task_id, links_to):
        if self.dry:
            print(f"DRY-RUN link {task_id} -> {links_to}")
            return
        self._req("POST", f"/task/{task_id}/link/{links_to}", {})

    def get_task(self, task_id, markdown=False):
        q = {"include_subtasks": "true"}
        if markdown:
            q["include_markdown_description"] = "true"
        return self._req("GET", f"/task/{task_id}", query=q)

    def upload(self, task_id, path, filename):
        if self.dry:
            print(f"DRY-RUN upload {task_id} <- {filename} ({os.path.getsize(path)} bytes)")
            return {"url": f"(dry-run)/{filename}", "title": filename}
        boundary = uuid.uuid4().hex
        ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            content = f.read()
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"attachment\"; "
                f"filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n").encode() + content + \
               f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(f"{API}/task/{task_id}/attachment", data=body, method="POST",
                                     headers={"Authorization": self.token,
                                              "Content-Type": f"multipart/form-data; boundary={boundary}"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            die(f"POST /task/{task_id}/attachment ({filename}) -> {e.code}: {e.read().decode()[:500]}")


def resolve_status(wanted, list_obj, fallback):
    names = [s["status"] for s in list_obj.get("statuses", [])]
    for w in (wanted, fallback):
        if not w:
            continue
        for n in names:
            if n.lower() == w.lower():
                return n
    die(f"status '{wanted or fallback}' not in list statuses {names}; fix PROJECT_CONTEXT.md")


def attachment_name(raw):
    """Attachment title = file name (e.g. 9884-4390.png); also the per-task dedupe key."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.basename(raw))


def design_section(t, uploaded):
    links = split_list(t.get("figma"))
    if not links and not uploaded:
        return ""
    lines = ["## Design"]
    lines += [f"- Figma: {u}" for u in links]
    for name, url in uploaded:
        lines += ["", f"![{name}]({url})"]
    return "\n".join(lines) + "\n\n"


def strip_design(body):
    return re.sub(r"^## Design\n.*?(?=^## |\Z)", "", body, flags=re.S | re.M).lstrip()


def build_payload(t, status, parent_id=None):
    lane = t["lane"]
    tags = ["agent-created", lane.lower()] + [x.strip() for x in t.get("tags", "").split(",") if x.strip()]
    p = {
        "name": t["title"],
        "markdown_content": t["body"],
        "status": status,
        "tags": sorted(set(tags)),
        "priority": PRIORITY[t.get("priority", "normal").lower()],
    }
    if t.get("estimate_hours"):
        p["time_estimate"] = int(float(t["estimate_hours"]) * 3600 * 1000)
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
    if ctx["tracker"] != "clickup":
        die(f"this project's tracker is `{ctx['tracker']}`; creating tickets from a spec is "
            f"implemented for ClickUp only. Set `Ticket source: human` in its Flow, let the team "
            f"write the tickets, and adopt them with tracker_scan.py + `existing_id:`. "
            f"tracker_status.py works on every tracker.", 4)
    tickets = parse_spec(a.spec)
    validate(tickets, ctx, a.spec)

    token = os.environ.get(ctx["secret_ref"])
    if not token and not a.dry_run:
        die(f"token not found in env: {ctx['secret_ref']} (the Tracker SecretRef in {a.context})")
    cu = ClickUp(token or "dry", a.dry_run)

    marker_path = re.sub(r"\.md$", "", a.spec) + ".clickup.json"
    marker = json.load(open(marker_path)) if os.path.exists(marker_path) else {}

    if a.dry_run and not token:
        print("DRY-RUN without token: skipping list lookup, status mapping unverified")
        status = ctx["create_status"] or "to do"
        existing, live_tasks = {}, []
    else:
        list_obj = cu.get_list(ctx["list_id"])
        status = resolve_status(ctx["create_status"], list_obj, "to do")
        live_tasks = cu.list_tasks(ctx["list_id"])
        existing = {t["name"]: t for t in live_tasks}

    print(f"list={ctx['list_id']} status='{status}' tickets={len(tickets)} existing_in_list={len(existing)}")

    ids = {}
    created = updated = 0
    # Before any write: a NEW ticket whose title is close to a live one (anyone's) is probably a duplicate.
    known = {m.get("id") for m in marker.values() if isinstance(m, dict)}
    clashes = []
    for t in tickets:
        if t.get("existing_id") or marker.get(t["title"]) or existing.get(t["title"]):
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
        target = (t.get("existing_id") or marker.get(t["title"], {}).get("id")
                  or (existing.get(t["title"]) or {}).get("id"))
        prev_hash = (marker.get(t["title"]) or {}).get("desc_hash")
        if target and prev_hash and not a.dry_run and not a.overwrite_edits:
            if desc_hash(cu.get_task(target, markdown=True)) != prev_hash:
                ids[t["title"]] = target
                skipped.append(t["title"])
                print(f"skipped  {t['lane']:7} {target:14} {t['title']} (description edited in ClickUp since "
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
            r = cu.create(ctx["list_id"], payload)
            created += 1
            action = "created"
        ids[t["title"]] = r["id"]
        prev = marker.get(t["title"], {})
        done = dict(prev.get("attachments", {}))  # attachment name -> url (idempotency)
        if not a.dry_run and target:
            for att in (cu.get_task(r["id"]).get("attachments") or []):
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
        if split_list(t.get("figma")) or shots:
            body = design_section(t, shots) + strip_design(t["body"])
            cu.update(r["id"], {"markdown_content": body})
        marker[t["title"]] = {"id": r["id"], "url": r.get("url", ""), "lane": t["lane"],
                              "attachments": {n: u for n, u in done.items() if n in dict(shots)}}
        if not a.dry_run:  # fingerprint what ClickUp now holds, to detect later hand edits
            marker[t["title"]]["desc_hash"] = desc_hash(cu.get_task(r["id"], markdown=True))
        print(f"{action:8} {t['lane']:7} {r['id']:14} {t['title']}")

    for t in tickets:
        for dep in deps_of(t):
            cu.link(ids[t["title"]], ids[dep])

    # tickets from an earlier push of this spec that the rewrite no longer contains
    live_ids = set(ids.values())
    stale = {title: m for title, m in marker.items()
             if title not in ids and m.get("id") not in live_ids and not title.startswith("_")}
    for title, m in stale.items():
        if a.prune:
            cancel = resolve_status(ctx["cancelled"], list_obj, None) if not (a.dry_run and not token) else ctx["cancelled"]
            cu.update(m["id"], {"status": cancel})
            marker.setdefault("_cancelled", {})[title] = m
            del marker[title]
            print(f"pruned   {m.get('lane', ''):7} {m['id']:14} {title} -> {cancel}")
        else:
            print(f"STALE    {m.get('lane', ''):7} {m['id']:14} {title} (not in spec; re-run with --prune to cancel it)")

    if not a.dry_run:
        with open(marker_path, "w", encoding="utf-8") as f:
            json.dump(marker, f, indent=2)
        parent = cu.get_task(ids[tickets[0]["title"]])
        found = len(parent.get("subtasks", []))
        expected = len(tickets) - 1
        ok = "OK" if found >= expected else "MISMATCH"
        print(f"VERIFY {ok}: parent {parent['id']} {parent.get('url','')} subtasks found={found} expected={expected}")
        for t in tickets:
            names = [attachment_name(raw) for raw, _ in screenshot_paths(t, ctx)]
            if not names and not split_list(t.get("figma")):
                continue
            live = cu.get_task(ids[t["title"]], markdown=True)
            have = {x.get("title") for x in (live.get("attachments") or [])}
            desc = live.get("markdown_description") or live.get("description") or ""
            missing = [n for n in names if n not in have]
            links_ok = all(u in desc for u in split_list(t.get("figma")))
            embedded = sum(1 for n in names if n in desc)
            state = "OK" if not missing and links_ok and "Design" in desc else "MISMATCH"
            print(f"VERIFY {state}: {t['title']} attachments={len(names) - len(missing)}/{len(names)} "
                  f"figma_links_in_description={'yes' if links_ok else 'NO'} screenshots_referenced_in_description={embedded}/{len(names)}")
        print(f"marker written: {marker_path}")
        slug = os.path.basename(os.path.dirname(os.path.realpath(a.context)))
        subprocess.run([sys.executable, "/home/openclaw/.openclaw/workspace/projects/_tools/spec_index.py", slug])
    if skipped:
        print(f"SKIPPED (edited by someone in ClickUp): {len(skipped)}: " + "; ".join(skipped))
    print(f"done: created={created} updated={updated}")


if __name__ == "__main__":
    main()
