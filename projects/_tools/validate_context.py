#!/usr/bin/env python3
"""Validate a PROJECT_CONTEXT.md and print its parsed fields.

Usage:
  validate_context.py <PROJECT_CONTEXT.md> [--json] [--live]

--json   print the parsed fields as JSON (used by other tools)
--live   also call ClickUp GET /list/{id} with the Tracker secret from the
         environment, print the list name and statuses, and fail if the
         statuses in the file are not all present on the list.

The optional `## Flow` section says how THIS project works (see OPENCLAW_ARCHITECTURE.md §4).
It is parsed into fields["flow"] and fields["status"]:
  fields["flow"]   profile, stages, ticket_source, assignee_filter, branch_model, pr_base,
                   merge_by, deploy_signal, chat_channel, pr_conventions
  fields["status"] canonical key -> this board's status name (or None when the board has none):
                   todo doing staged rejected done cancelled hold
Tools use the canonical keys and never hardcode a board's status names. A context without
`## Flow` gets the `factory` profile and a status map inferred from its Statuses (warning only).

Exit codes: 0 ok · 1 file/field errors · 3 live check failed.
Standard library only.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request

REQUIRED = {
    "slug": r"\*\*Slug:\*\*\s*`([^`]+)`",
    "repo_url": r"\*\*Git SSH Clone URL:\*\*\s*`([^`<>]+)`",
    "list_id": r"\*\*ClickUp List ID:\*\*\s*`?([^`\n]+?)`?\s*$",
    "tracker_secret": r"Tracker:\s*`([^`]+)`",
    "statuses": r"\*\*Statuses:\*\*\s*(.+)",
    "create_status": r"\*\*Create status:\*\*\s*`?([^`\n]+?)`?\s*$",
    "code_cwd": r"\*\*Code \(CWD\):\*\*\s*`([^`<>]+)`",
    "artifacts_dir": r"\*\*Internal Artifacts:\*\*\s*`([^`<>]+)`",
}
OPTIONAL = {
    "design_secret": r"Design:\s*`([^`]+)`",   # required only when a Figma file is set (checked below)
    "list_name": r"\*\*ClickUp List name:\*\*\s*(.+)",
    "figma_file": r"\*\*Figma file:\*\*\s*(\S+)",
    "figma_mcp_server": r"\*\*Figma MCP server:\*\*\s*`([^`]+)`",
    "database": r"\*\*Database:\*\*\s*(.+)",
    "layout": r"\*\*Layout:\*\*\s*(.+)",
    "gcp_project_id": r"\*\*GCP Project ID:\*\*\s*`?([^`\n]+?)`?\s*$",
    "gcp_region": r"\*\*GCP Region:\*\*\s*`?([^`\n]+?)`?\s*$",
    "gcp_key_secret": r"GCP Key Vault:\s*`([^`]+)`",
    "gcp_key_json": r"GCP Key JSON:\s*`([^`<>]+)`",
    "branch_prefixes": r"\*\*Branch Prefixes:\*\*\s*(.+)",
    "default_branch": r"\*\*Default branch:\*\*\s*`([^`<>]+)`",
    "github_repo": r"\*\*GitHub Repo:\*\*\s*`?([^`\n]+?)`?\s*$",
    "git_secret": r"GitHub Token:\s*`([^`]+)`",
    "deploy_triggers": r"\*\*Deploy triggers:\*\*\s*(.+)",
}
PLACEHOLDER = re.compile(r"<[^>]*>")

# ---------------------------------------------------------------- Flow profile
STAGES = ["spec", "tickets", "review", "internal-qa", "merge-gate", "delivery-watch"]
CANON = ["todo", "doing", "staged", "rejected", "done", "cancelled", "hold"]
REQUIRED_STATUS = ["todo", "doing", "done", "cancelled"]
ALIASES = {   # used only to infer a status map the file does not spell out
    "todo": ["to do", "todo", "open", "backlog", "new", "ready"],
    "doing": ["in progress", "in dev", "in development", "doing", "wip"],
    "staged": ["qa", "staging", "in qa", "ready for qa", "deployed"],
    "rejected": ["rejected", "for development", "qa failed", "reopened"],
    "done": ["complete", "completed", "done", "closed"],
    "cancelled": ["cancelled", "canceled", "won't do", "wont do"],
    "hold": ["on hold", "blocked", "hold"],
}
PRESETS = {
    "factory":     dict(stages=STAGES[:], ticket_source="agent", assignee_filter="any", branch_model="feature-branch",
                        merge_by="van", deploy_signal="cloud-build"),
    "teammate":    dict(stages=["review", "merge-gate", "delivery-watch"], ticket_source="human", assignee_filter=None,
                        branch_model="ticket-branch", merge_by="humans", deploy_signal="none"),
    "maintenance": dict(stages=["review", "merge-gate"], ticket_source="human", assignee_filter=None,
                        branch_model="ticket-branch", merge_by="humans", deploy_signal="none"),
    "custom":      dict(stages=None, ticket_source="agent", assignee_filter="any", branch_model="feature-branch",
                        merge_by="van", deploy_signal="none"),
}
FLOW_LABELS = {
    "profile": "Profile", "stages": "Stages", "ticket_source": "Ticket source", "assignee_filter": "Assignee filter",
    "branch_model": "Branch model", "pr_base": "PR base", "merge_by": "Merge by", "deploy_signal": "Deploy signal",
    "status_map": "Status map", "chat_channel": "Chat channel", "pr_conventions": "PR conventions",
}
CHOICES = {"ticket_source": {"agent", "human", "both"}, "branch_model": {"feature-branch", "ticket-branch"},
           "merge_by": {"van", "humans"}, "deploy_signal": {"cloud-build", "none"}}


def _ticks(v):
    t = re.findall(r"`([^`]*)`", v)
    return t if t else [x.strip() for x in v.split(",") if x.strip()]


def parse_flow(text, fields, errors):
    """Fill fields['flow'] and fields['status'] from the `## Flow` section (or defaults)."""
    sec = re.search(r"^## Flow\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    raw = {}
    if sec:
        for key, label in FLOW_LABELS.items():
            m = re.search(r"^- \*\*" + re.escape(label) + r":\*\*\s*(.+)$", sec.group(1), re.M)
            if m and not PLACEHOLDER.fullmatch(_ticks(m.group(1).strip())[0] if _ticks(m.group(1).strip()) else ""):
                raw[key] = m.group(1).strip()      # an unfilled `<placeholder>` means "use the default"
    else:
        fields.setdefault("warnings", []).append(
            "no '## Flow' section: using the `factory` profile and a status map inferred from Statuses")
    profile = _ticks(raw["profile"])[0] if raw.get("profile") else "factory"
    if profile not in PRESETS:
        errors.append(f"Flow Profile must be one of {sorted(PRESETS)}: {profile}")
        profile = "factory"
    flow = dict(PRESETS[profile]); flow["profile"] = profile
    if raw.get("stages"):
        flow["stages"] = _ticks(raw["stages"])
    for k in ("ticket_source", "assignee_filter", "branch_model", "merge_by", "deploy_signal", "chat_channel", "pr_conventions", "pr_base"):
        if raw.get(k):
            flow[k] = _ticks(raw[k])[0]
    flow.setdefault("pr_base", None); flow.setdefault("chat_channel", None); flow.setdefault("pr_conventions", "none")
    if not flow.get("pr_base"):
        flow["pr_base"] = fields.get("default_branch")
    # validate
    if flow["stages"] is None:
        errors.append("Flow Profile `custom` needs an explicit **Stages:** line")
        flow["stages"] = []
    bad = [x for x in flow["stages"] if x not in STAGES]
    if bad:
        errors.append(f"Flow Stages has unknown stage(s) {bad}; allowed: {STAGES}")
    flow["stages"] = [x for x in STAGES if x in flow["stages"]]   # canonical order
    for k, allowed in CHOICES.items():
        if flow.get(k) not in allowed:
            extra = " (github-actions is not supported by delivery_watch.py yet)" if flow.get(k) == "github-actions" else ""
            errors.append(f"Flow {FLOW_LABELS[k]} must be one of {sorted(allowed)}: {flow.get(k)}{extra}")
    if profile in ("teammate", "maintenance") and (not flow.get("assignee_filter") or flow["assignee_filter"] == "any"):
        errors.append(f"Flow Profile `{profile}` needs **Assignee filter:** (Van's tracker user id or email): "
                      "agents only pick up tickets assigned to Van")
    if flow["assignee_filter"] is None:
        flow["assignee_filter"] = "any"
    if "tickets" in flow["stages"] and flow["ticket_source"] == "human":
        errors.append("Flow Stages include `tickets` but Ticket source is `human`: agents would create tickets humans own")
    if flow["deploy_signal"] == "cloud-build" and not fields.get("gcp_project_id"):
        errors.append("Flow Deploy signal `cloud-build` needs **GCP Project ID:** (the watcher reads Cloud Build)")
    if "delivery-watch" in flow["stages"] and not fields.get("github_repo"):
        errors.append("Flow Stages include `delivery-watch` but **GitHub Repo:** is not set")
    if flow.get("pr_base") and not re.fullmatch(r"[A-Za-z0-9._/-]+", flow["pr_base"]):
        errors.append(f"Flow PR base is not a branch name: {flow['pr_base']}")
    # status map: explicit entries, then inference from Statuses
    statuses = fields.get("statuses") or []
    low = {x.lower(): x for x in statuses}
    smap = {}
    if raw.get("status_map"):
        for pair in _ticks(raw["status_map"]):
            if "=" not in pair:
                errors.append(f"Flow Status map entry must be key=status: {pair}"); continue
            k, v = (x.strip() for x in pair.split("=", 1))
            if k not in CANON:
                errors.append(f"Flow Status map key `{k}` unknown; allowed: {CANON}"); continue
            if v in ("-", "none", ""):
                smap[k] = None
            elif v.lower() in low:
                smap[k] = low[v.lower()]
            else:
                errors.append(f"Flow Status map `{k}={v}`: '{v}' is not in Statuses {statuses}")
    for k in CANON:
        if k not in smap:
            smap[k] = next((low[a] for a in ALIASES[k] if a in low), None)
    for k in REQUIRED_STATUS:
        if not smap.get(k):
            errors.append(f"Flow Status map has no `{k}` status (add `{k}=<status>` to **Status map:**)")
    if flow["deploy_signal"] != "none" and not smap.get("staged"):
        errors.append("Flow Deploy signal is set but the Status map has no `staged` status to move deployed tickets to")
    fields["flow"], fields["status"] = flow, smap


def parse(path):
    text = open(path, encoding="utf-8").read()
    fields, errors = {}, []
    for key, rx in {**REQUIRED, **OPTIONAL}.items():
        m = re.search(rx, text, re.M)
        if not m:
            if key in REQUIRED:
                errors.append(f"missing required field: {key}")
            continue
        val = m.group(1).strip()
        if PLACEHOLDER.search(val) and key in REQUIRED:
            errors.append(f"{key} still has a placeholder: {val}")
        fields[key] = val
    if "slug" in fields and not re.fullmatch(r"[a-z0-9][a-z0-9-]*", fields["slug"]):
        errors.append(f"slug must be lowercase letters, digits, hyphens: {fields['slug']}")
    if "list_id" in fields and not re.fullmatch(r"\d{6,}", fields["list_id"]):
        errors.append(f"ClickUp List ID must be digits only: {fields['list_id']}")
    for k in ("tracker_secret", "design_secret"):
        if k in fields and not re.fullmatch(r"[A-Z0-9_]+", fields[k]):
            errors.append(f"{k} must be UPPER_SNAKE: {fields[k]}")
    if "branch_prefixes" in fields:
        fields["branch_prefixes"] = re.findall(r"`([^`]+)`", fields["branch_prefixes"])
    if "deploy_triggers" in fields:
        # `a, b` and `a`, `b` and bare a, b all mean the same list. Backticks left in
        # here become trigger names that match nothing, which wedges the watcher on
        # "still building" forever (2026-09-19), so split them out and drop placeholders.
        raw = fields["deploy_triggers"]
        fields["deploy_triggers"] = [] if PLACEHOLDER.search(raw) else [
            t for part in _ticks(raw) for t in (x.strip() for x in part.split(",")) if t]
    if "statuses" in fields:
        fields["statuses"] = [s.strip(" `") for s in fields["statuses"].split(",") if s.strip(" `")]
    # Stack section must exist and not be entirely placeholders
    stack = re.search(r"## Stack\n(.*?)\n## ", text, re.S)
    if not stack:
        errors.append("missing '## Stack' section")
    elif not re.search(r"\*\*[A-Za-z/]+:\*\*\s*[^<\n]", stack.group(1)):
        errors.append("'## Stack' is unfilled (all placeholders). VanPM fills it by inspecting the repo.")
    # secret naming rule
    slug_upper = fields.get("slug", "").replace("-", "").upper()
    for k in ("tracker_secret", "design_secret"):
        v = fields.get(k, "")
        if v and slug_upper and not v.endswith("_" + slug_upper):
            fields.setdefault("warnings", []).append(
                f"{k} '{v}' does not follow <KIND>_{slug_upper}; allowed only if the vault really uses this name")
    # Figma MCP server is per project: mcp.servers["figma-<slug>"] -> projects/_tools/figma_mcp.py <slug>
    has_figma = fields.get("figma_file", "none").lower().strip("<>") not in ("none", "")
    if has_figma and not fields.get("design_secret"):
        errors.append("Figma file is set, so a 'Design:' SecretRef line (FIGMA_API_KEY_<SLUGUPPER>) is required")
    if has_figma and "slug" in fields and fields.get("figma_mcp_server") != f"figma-{fields['slug']}":
        errors.append(f"Figma file is set, so '**Figma MCP server:** `figma-{fields['slug']}`' is required "
                      f"(found: {fields.get('figma_mcp_server', 'missing')})")
    # GCP is per project: no ambient gcloud default is allowed to stand in for these.
    # If a project has a GCP environment it must name its own project id, its own vault
    # entry and its own key file; agents reach them through _tools/gcloud_env.py <slug>.
    has_gcp = fields.get("gcp_project_id", "none").lower().strip("<>") not in ("none", "")
    if has_gcp:
        for k, label in (("gcp_key_secret", "GCP Key Vault"), ("gcp_key_json", "GCP Key JSON")):
            if not fields.get(k):
                errors.append(f"GCP Project ID is set, so a '{label}:' SecretRef line is required")
        if fields.get("gcp_key_secret") and not re.fullmatch(r"[A-Z0-9_]+", fields["gcp_key_secret"]):
            errors.append(f"gcp_key_secret must be UPPER_SNAKE: {fields['gcp_key_secret']}")
        if fields.get("gcp_key_secret") and slug_upper and not re.search(r"_" + slug_upper + r"(_|$)", fields["gcp_key_secret"]):
            fields.setdefault("warnings", []).append(
                f"gcp_key_secret '{fields['gcp_key_secret']}' does not contain _{slug_upper}; "
                f"allowed only if the vault really uses this name")
        expect = f"/home/openclaw/.openclaw/workspace/credentials/gcp/{fields.get('slug', '')}.json"
        if fields.get("gcp_key_json") and fields["gcp_key_json"] != expect:
            errors.append(f"GCP Key JSON must be the project's own key at {expect} "
                          f"(found: {fields['gcp_key_json']})")
        if fields.get("gcp_key_json") and not os.path.isfile(fields["gcp_key_json"]):
            fields.setdefault("warnings", []).append(
                f"GCP key file does not exist yet: {fields['gcp_key_json']}")
    elif any(fields.get(k) for k in ("gcp_key_secret", "gcp_key_json", "gcp_region")):
        errors.append("GCP SecretRefs/Region are set but '**GCP Project ID:**' is missing; "
                      "agents cannot resolve which GCP project to act on")
    # GitHub API access (gh, PRs) is per project: a repo-scoped fine-grained PAT named here,
    # reached only through _tools/git_env.py <slug>. Git push itself may still use the SSH alias.
    has_gh = fields.get("github_repo", "none").lower().strip("<>") not in ("none", "")
    if has_gh:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", fields["github_repo"]):
            errors.append(f"GitHub Repo must be <owner>/<repo>: {fields['github_repo']}")
        if not fields.get("git_secret"):
            errors.append("GitHub Repo is set, so a 'GitHub Token:' SecretRef line is required")
        elif not re.fullmatch(r"[A-Z0-9_]+", fields["git_secret"]):
            errors.append(f"git_secret must be UPPER_SNAKE: {fields['git_secret']}")
        elif slug_upper and not fields["git_secret"].endswith("_" + slug_upper):
            fields.setdefault("warnings", []).append(
                f"git_secret '{fields['git_secret']}' does not follow GITHUB_TOKEN_{slug_upper}; "
                f"allowed only if the vault really uses this name")
    elif fields.get("git_secret"):
        errors.append("'GitHub Token:' SecretRef is set but '**GitHub Repo:**' is missing; "
                      "gh cannot resolve which repository to act on")
    if "create_status" in fields and "statuses" in fields:
        if fields["create_status"].lower() not in [s.lower() for s in fields["statuses"]]:
            errors.append(f"create_status '{fields['create_status']}' is not in Statuses")
    parse_flow(text, fields, errors)
    for k in ("code_cwd", "artifacts_dir"):
        if k in fields and not os.path.isdir(fields[k]):
            fields.setdefault("warnings", []).append(f"{k} directory does not exist yet: {fields[k]}")
    return fields, errors


def live_check(fields):
    token = os.environ.get(fields["tracker_secret"])
    if not token:
        return [f"live check: env var {fields['tracker_secret']} is not set (run inside the agent with the secret injected)"]
    req = urllib.request.Request(f"https://api.clickup.com/api/v2/list/{fields['list_id']}",
                                 headers={"Authorization": token})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            lst = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return [f"live check: GET /list/{fields['list_id']} -> {e.code}: {e.read().decode()[:300]}"]
    names = [s["status"] for s in lst.get("statuses", [])]
    print(f"LIVE list {fields['list_id']} = '{lst.get('name')}' in folder '{(lst.get('folder') or {}).get('name')}' / space '{(lst.get('space') or {}).get('name')}'")
    print(f"LIVE statuses: {names}")
    errs = []
    missing = [s for s in fields["statuses"] if s.lower() not in [n.lower() for n in names]]
    if missing:
        errs.append(f"live check: statuses in file not on the list: {missing}")
    if fields.get("list_name") and fields["list_name"].strip() != (lst.get("name") or "").strip():
        errs.append(f"live check: file says list name '{fields['list_name']}', ClickUp says '{lst.get('name')}'")
    return errs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); sys.exit(1)
    fields, errors = parse(args[0])
    if "--json" in sys.argv:
        print(json.dumps(fields, indent=2))
    else:
        for k, v in fields.items():
            if k != "warnings":
                print(f"{k:16} {v}")
        for w in fields.get("warnings", []):
            print(f"WARNING          {w}")
    if errors:
        print("INVALID PROJECT_CONTEXT:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    if "--live" in sys.argv:
        errs = live_check(fields)
        if errs:
            for e in errs:
                print(f"  - {e}", file=sys.stderr)
            sys.exit(3)
        print("LIVE OK")
    print("VALID")


if __name__ == "__main__":
    main()
