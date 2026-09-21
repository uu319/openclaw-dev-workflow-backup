#!/usr/bin/env python3
"""List tracker tickets that no spec knows about (made by a person, or by an agent outside the workflow).

Usage:
  tracker_scan.py --context PROJECT_CONTEXT.md

Reads every <spec>.tracker.json / <spec>.clickup.json marker under specs/,
specs/_done/ and specs/_superseded/, then lists live, non-closed tickets whose id
is in none of them. Run it before planning: a listed ticket that covers the same
work is adopted with `existing_id: <id>` in the spec instead of creating a new one.

This is the entry point for `teammate` and `maintenance` projects, where the team
writes the tickets and we only ever adopt them. Works against whichever tracker
the project declares. Read-only. Standard library only.
"""
import argparse
import glob
import importlib.util
import json
import os
import sys

WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", "/home/openclaw/.openclaw/workspace")
TOOLS = os.path.join(WORKSPACE, "projects/_tools")
VALIDATOR = os.path.join(TOOLS, "validate_context.py")
sys.path.insert(0, TOOLS)
import trackers  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True)
    a = ap.parse_args()

    spec = importlib.util.spec_from_file_location("vc", VALIDATOR)
    vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
    fields, errors = vc.parse(a.context)
    if errors:
        sys.exit("ERROR: " + "; ".join(errors))
    if fields.get("tracker", "none") == "none":
        sys.exit("ERROR: this project has no tracker (Tracker: none); there is nothing to scan")

    token = os.environ.get(fields["tracker_secret"])
    if not token:
        sys.exit(f"env var {fields['tracker_secret']} not set")
    tk = trackers.for_project(fields, token)

    known = set()
    specs = os.path.join(os.path.realpath(fields["artifacts_dir"]), "specs")
    for pat in ("**/*.tracker.json", "**/*.clickup.json"):
        for m in glob.glob(os.path.join(specs, pat), recursive=True):
            for k, v in json.load(open(m)).items():
                if isinstance(v, dict) and v.get("id"):
                    known.add(v["id"])
                elif k == "_cancelled" and isinstance(v, dict):
                    known.update(x.get("id") for x in v.values() if isinstance(x, dict))

    # `closed` comes from the provider's own status type, so a board that calls it
    # "Won't do" or "Resolved" needs no configuration here.
    who_filter = (fields.get("flow") or {}).get("assignee_filter", "any")
    foreign = []
    for tid, t in sorted(tk.tasks().items()):
        if tid in known or t.get("closed"):
            continue
        mine = who_filter != "any" and any(
            str(who_filter).lower() in str(x).lower() for x in (t.get("assignees") or []))
        note = "  <-- assigned to the Flow Assignee filter" if mine else ""
        foreign.append(f"- {tid} [{t.get('status')}] {t.get('title')} {t.get('url') or ''}{note}")

    print(f"{len(foreign)} ticket(s) not in any spec:")
    print("\n".join(foreign) or "- none")


if __name__ == "__main__":
    main()
