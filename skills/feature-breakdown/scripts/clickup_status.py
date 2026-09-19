#!/usr/bin/env python3
"""Set the status of tickets recorded in a spec's .clickup.json marker.

Usage:
  clickup_status.py --context PROJECT_CONTEXT.md --spec <spec.md> --status "<status>" (--only "<title>" | --all) [--dry-run]
  clickup_status.py --context PROJECT_CONTEXT.md --spec <spec.md> --get   [--only "<title>"]   # read-only
  clickup_status.py --context PROJECT_CONTEXT.md --spec <spec.md> --claim --only "<title>"       # GO / SKIP

Reads ticket ids from <spec>.clickup.json (written by clickup_push.py; falls back to
specs/_done/ after close-on-merge archived it). The status name is matched
case-insensitively against PROJECT_CONTEXT's Statuses and sent in that spelling.
--claim reads the live status first: already doing, staged or done -> prints SKIP and changes
nothing; anything else -> sets the project's `doing` status and prints GO. When the project's
Flow has an Assignee filter (teammate/maintenance profiles), a ticket not assigned to it is SKIP.

--status takes a canonical key from the project's Flow Status map (todo doing staged rejected done
cancelled hold) or a literal status name from Statuses. Prefer the canonical key: boards differ.
"""
import argparse, importlib.util, json, os, re, sys, urllib.error, urllib.request

VALIDATOR = "/home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py"
API = "https://api.clickup.com/api/v2"


def die(m):
    print(f"ERROR: {m}", file=sys.stderr); sys.exit(1)


def live_task(task_id, token):
    req = urllib.request.Request(f"{API}/task/{task_id}", headers={"Authorization": token})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        die(f"GET /task/{task_id} -> {e.code}: {e.read().decode()[:300]}")


def live_status(task_id, token):
    return (live_task(task_id, token).get("status") or {}).get("status", "?")


def assigned_to(task, who):
    """who = tracker user id, username or email from the Flow Assignee filter."""
    w = str(who).lower()
    for u in task.get("assignees") or []:
        if w in {str(u.get("id", "")).lower(), str(u.get("username", "")).lower(), str(u.get("email", "")).lower()}:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True); ap.add_argument("--spec", required=True)
    ap.add_argument("--status"); ap.add_argument("--only")
    ap.add_argument("--get", action="store_true", help="print live status, change nothing")
    ap.add_argument("--claim", action="store_true", help="GO/SKIP claim of one ticket (needs --only)")
    ap.add_argument("--all", action="store_true", help="move every ticket in the marker")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.claim:
        if not a.only: die("--claim needs --only \"<title>\"")
        a.status = "doing"
    if not a.get and not a.status: die("pass --status, --get or --claim")
    if not a.get and not a.only and not a.all: die("pass --only \"<title>\" (one ticket) or --all (every ticket in the spec)")
    spec = importlib.util.spec_from_file_location("vc", VALIDATOR); vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
    fields, errors = vc.parse(a.context)
    if errors: die("; ".join(errors))
    marker_path = re.sub(r"\.md$", "", a.spec) + ".clickup.json"
    if not os.path.exists(marker_path):
        done = os.path.join(os.path.dirname(marker_path), "_done", os.path.basename(marker_path))
        if not os.path.exists(done): die(f"no marker {marker_path} (or in _done/); tickets were never pushed")
        marker_path = done
    marker = json.load(open(marker_path))
    token = os.environ.get(fields["tracker_secret"])
    if not token and not a.dry_run: die(f"env var {fields['tracker_secret']} not set")
    smap = fields.get("status") or {}
    if a.status:
        if a.status in smap:                      # canonical key -> this board's name
            if not smap[a.status]:
                die(f"this project's board has no `{a.status}` status (Flow Status map); nothing to set")
            a.status = smap[a.status]
        match = [x for x in fields["statuses"] if x.lower() == a.status.lower()]
        if not match: die(f"status '{a.status}' not in {fields['statuses']} (canonical keys: {sorted(smap)})")
        a.status = match[0]
    busy = {v.lower() for k, v in smap.items() if k in ("doing", "staged", "done") and v}
    who = (fields.get("flow") or {}).get("assignee_filter", "any")
    if a.only and a.only not in marker: die(f"'{a.only}' is not in {marker_path}; titles: {list(marker)}")
    for title, info in marker.items():
        if title.startswith("_"): continue  # bookkeeping keys like _cancelled
        if a.only and title != a.only: continue
        if a.get or a.claim:
            if not token: die(f"env var {fields['tracker_secret']} not set")
            task = live_task(info["id"], token)
            cur = (task.get("status") or {}).get("status", "?")
            if a.get:
                print(f"{cur:12} {info['id']}  {title}"); continue
            if cur.lower() in busy:
                print(f"SKIP  {info['id']} is already '{cur}'  {title}"); return
            if who != "any" and not assigned_to(task, who):
                print(f"SKIP  {info['id']} is not assigned to {who} (Flow Assignee filter)  {title}"); return
        if a.dry_run:
            print(f"DRY-RUN {info['id']} -> {a.status}  {title}"); continue
        req = urllib.request.Request(f"{API}/task/{info['id']}", data=json.dumps({"status": a.status}).encode(),
                                     method="PUT", headers={"Authorization": token, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r: r.read()
            print(f"{'GO    ' if a.claim else ''}updated {info['id']} -> {a.status}  {title}")
        except urllib.error.HTTPError as e:
            die(f"PUT /task/{info['id']} -> {e.code}: {e.read().decode()[:300]}")


if __name__ == "__main__":
    main()
