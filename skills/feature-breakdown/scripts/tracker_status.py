#!/usr/bin/env python3
"""Set the status of tickets recorded in a spec's tracker marker.

Usage:
  tracker_status.py --context PROJECT_CONTEXT.md --spec <spec.md> --status "<status>" (--only "<title>" | --all) [--dry-run]
  tracker_status.py --context PROJECT_CONTEXT.md --spec <spec.md> --get   [--only "<title>"]   # read-only
  tracker_status.py --context PROJECT_CONTEXT.md --spec <spec.md> --claim --only "<title>"     # GO / SKIP

Reads ticket ids from <spec>.tracker.json (or the older <spec>.clickup.json), written
by tracker_push.py; falls back to specs/_done/ after close-on-merge archived it.
Works against whichever tracker the project declares - the work is done by
projects/_tools/trackers/, so this script names no vendor.

--claim reads the live status first: already doing, staged or done -> prints SKIP and changes
nothing; anything else -> sets the project's `doing` status and prints GO. When the project's
Flow has an Assignee filter (teammate/maintenance profiles), a ticket not assigned to it is SKIP.

--status takes a canonical key from the project's Flow Status map (todo doing staged rejected done
cancelled hold) or a literal status name from Statuses. Prefer the canonical key: boards differ.
"""
import argparse
import importlib.util
import json
import os
import re
import sys

TOOLS = "/home/openclaw/.openclaw/workspace/projects/_tools"
VALIDATOR = os.path.join(TOOLS, "validate_context.py")
sys.path.insert(0, TOOLS)
import trackers  # noqa: E402


def die(m):
    print(f"ERROR: {m}", file=sys.stderr); sys.exit(1)


def marker_for(spec_path):
    """The spec's marker, new name first, then the pre-rename one, then _done/."""
    base = re.sub(r"\.md$", "", spec_path)
    for cand in (base + ".tracker.json", base + ".clickup.json"):
        if os.path.exists(cand):
            return cand
        done = os.path.join(os.path.dirname(cand), "_done", os.path.basename(cand))
        if os.path.exists(done):
            return done
    die(f"no marker for {spec_path} (.tracker.json or .clickup.json, here or in _done/); "
        f"tickets were never pushed")


def assigned_to(task, who):
    """who = tracker user id, username or email from the Flow Assignee filter."""
    w = str(who).lower()
    return any(w == str(a).lower() or w in str(a).lower() for a in (task.get("assignees") or []))


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
        if not a.only:
            die("--claim needs --only \"<title>\"")
        a.status = "doing"
    if not a.get and not a.status:
        die("pass --status, --get or --claim")
    if not a.get and not a.only and not a.all:
        die("pass --only \"<title>\" (one ticket) or --all (every ticket in the spec)")

    spec = importlib.util.spec_from_file_location("vc", VALIDATOR)
    vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
    fields, errors = vc.parse(a.context)
    if errors:
        die("; ".join(errors))
    if fields.get("tracker", "none") == "none":
        die("this project has no tracker (Tracker: none); there are no statuses to set")

    marker_path = marker_for(a.spec)
    marker = json.load(open(marker_path))
    token = os.environ.get(fields["tracker_secret"])
    if not token and not a.dry_run:
        die(f"env var {fields['tracker_secret']} not set")
    tk = trackers.for_project(fields, token)

    smap = fields.get("status") or {}
    if a.status:
        if a.status in smap:                      # canonical key -> this board's name
            if not smap[a.status]:
                die(f"this project's board has no `{a.status}` status (Flow Status map); nothing to set")
            a.status = smap[a.status]
        match = [x for x in fields.get("statuses", []) if x.lower() == a.status.lower()]
        if not match:
            die(f"status '{a.status}' not in {fields.get('statuses')} (canonical keys: {sorted(smap)})")
        a.status = match[0]

    busy = {v.lower() for k, v in smap.items() if k in ("doing", "staged", "done") and v}
    who = (fields.get("flow") or {}).get("assignee_filter", "any")
    if a.only and a.only not in marker:
        die(f"'{a.only}' is not in {marker_path}; titles: {list(marker)}")

    for title, info in marker.items():
        if title.startswith("_"):      # bookkeeping keys like _cancelled
            continue
        if a.only and title != a.only:
            continue
        if a.get or a.claim:
            if not token:
                die(f"env var {fields['tracker_secret']} not set")
            try:
                task = tk.get_task(info["id"])
            except Exception as e:  # noqa: BLE001
                die(f"read {info['id']}: {e}")
            cur = task.get("status") or "?"
            if a.get:
                print(f"{cur:12} {info['id']}  {title}"); continue
            if cur.lower() in busy:
                print(f"SKIP  {info['id']} is already '{cur}'  {title}"); return
            if who != "any" and not assigned_to(task, who):
                print(f"SKIP  {info['id']} is not assigned to {who} (Flow Assignee filter)  {title}"); return
        if a.dry_run:
            print(f"DRY-RUN {info['id']} -> {a.status}  {title}"); continue
        try:
            tk.set_status(info["id"], a.status)
        except Exception as e:  # noqa: BLE001
            die(f"set {info['id']} -> {a.status}: {e}")
        print(f"{'GO    ' if a.claim else ''}updated {info['id']} -> {a.status}  {title}")


if __name__ == "__main__":
    main()
