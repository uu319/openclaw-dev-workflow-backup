#!/usr/bin/env python3
"""List tracker tickets that no spec knows about (made by a person, or by an agent outside the workflow).

Usage:
  clickup_scan.py --context PROJECT_CONTEXT.md

Reads every <spec>.clickup.json marker under specs/, specs/_done/ and
specs/_superseded/, then lists live, non-cancelled tickets whose id is in none
of them. Run it before planning: a listed ticket that covers the same work is
adopted with `existing_id: <id>` in the spec instead of creating a new one.
Read-only. Standard library only.
"""
import argparse, glob, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.realpath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--context", required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("push", os.path.join(HERE, "clickup_push.py"))
    push = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(push)
    ctx = push.parse_context(a.context)
    token = os.environ.get(ctx["secret_ref"])
    if not token:
        sys.exit(f"env var {ctx['secret_ref']} not set")
    known = set()
    specs = os.path.join(ctx["artifacts_dir"], "specs")
    for m in glob.glob(os.path.join(specs, "**", "*.clickup.json"), recursive=True):
        for k, v in json.load(open(m)).items():
            if isinstance(v, dict) and v.get("id"):
                known.add(v["id"])
            elif k == "_cancelled" and isinstance(v, dict):
                known.update(x.get("id") for x in v.values() if isinstance(x, dict))
    cu = push.ClickUp(token, False)
    foreign = []
    for t in cu.list_tasks(ctx["list_id"]):
        status = (t.get("status") or {}).get("status", "")
        if t["id"] in known or status.lower() in ("cancelled", "closed"):
            continue
        tags = {x.get("name") for x in t.get("tags") or []}
        who = "agent, outside the workflow" if "agent-created" in tags else "person"
        foreign.append(f"- {t['id']} [{status}] {t['name']} (by {who}) {t.get('url', '')}")
    print(f"{len(foreign)} ticket(s) not in any spec:")
    print("\n".join(foreign) or "- none")


if __name__ == "__main__":
    main()
