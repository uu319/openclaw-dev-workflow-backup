#!/usr/bin/env python3
"""Ask a tracker what its board is called and which statuses it has.

    tracker_probe.py --tracker jira --board KAN --secret JIRA_API_TOKEN_X \
                     --base-url https://site.atlassian.net

Used during onboarding, BEFORE a PROJECT_CONTEXT.md exists, so it takes its
arguments directly instead of reading one. It prints the board name, the real
statuses, and the `**Statuses:**` / `**Status map:**` lines to paste into the
file - with every canonical key it could not match called out, and what that
absence costs.

Onboarding used to ask a human to type the statuses and do the mapping in their
head, against a default that was one project's board. The tracker knows; ask it.

Reads the secret VALUE from the vault by name, exactly like the other launchers,
and never prints it. Standard library only.
"""
import argparse
import importlib.util
import os
import shutil
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import trackers  # noqa: E402

_spec = importlib.util.spec_from_file_location("vc_probe", os.path.join(TOOLS, "validate_context.py"))
vc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vc)


def die(m):
    print(f"ERROR: {m}", file=sys.stderr)
    sys.exit(1)


def token_for(name):
    tok = os.environ.get(name)
    if tok:
        return tok
    r = subprocess.run([shutil.which("openclaw") or "/usr/bin/openclaw",
                        "secrets", "store", "get", "--plain", name],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        die(f"could not read vault entry {name}: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def propose(statuses):
    """-> (mapping, unmatched) using the validator's own inference table."""
    low = {s.lower(): s for s in statuses}
    smap = {}
    for key in vc.CANON:
        smap[key] = next((low[a] for a in vc.ALIASES[key] if a in low), None)
    return smap, [k for k, v in smap.items() if not v]


COSTS = {
    "todo": "tickets not yet started are not recognised",
    "doing": "REQUIRED - a claim has nothing to set",
    "staged": "nothing can be marked as reaching staging",
    "rejected": "QA rejections are not detected",
    "done": "REQUIRED - a finished feature is never recognised",
    "cancelled": "nothing is treated as cancelled",
    "hold": "nothing can be parked",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracker", required=True, choices=sorted(vc.TRACKERS))
    ap.add_argument("--board", required=True)
    ap.add_argument("--secret", required=True, help="vault entry NAME, not a value")
    ap.add_argument("--base-url", help="Jira only")
    a = ap.parse_args()

    if a.tracker == "jira" and not a.base_url:
        die("--base-url is required for jira (https://<site>.atlassian.net)")

    fields = {"tracker": a.tracker, "board_id": a.board, "tracker_base_url": a.base_url}
    tk = trackers.for_project(fields, token_for(a.secret))
    try:
        name, statuses, where = tk.board_info()
    except Exception as e:  # noqa: BLE001
        die(f"{a.tracker} board {a.board}: {e}")

    print(f"board   : {name}   ({where})")
    print(f"statuses: {statuses}\n")
    if not statuses:
        die("the board reported no statuses; check the board id and the token's permissions")

    smap, unmatched = propose(statuses)
    print("Paste these into PROJECT_CONTEXT.md:\n")
    print("- **Tracker Board name:** " + (name or ""))
    print("- **Statuses:** " + ", ".join(f"`{s}`" for s in statuses))
    print("- **Create status:** `" + (smap.get("todo") or statuses[0]) + "`")
    print("- **Status map:** " + ", ".join(f"`{k}={v}`" for k, v in smap.items() if v))

    if unmatched:
        print("\nNot matched automatically:")
        for k in unmatched:
            required = k in vc.REQUIRED_STATUS
            mark = "  !! " if required else "     "
            print(f"{mark}`{k}` - {COSTS.get(k, '')}")
        if any(k in vc.REQUIRED_STATUS for k in unmatched):
            print("\nAdd the `!!` ones to the Status map by hand (`<key>=<status on this board>`); "
                  "the rest are optional and the project works without them.")
        else:
            print("\nAll of these are optional. Add any of them to the Status map if the board "
                  "does have an equivalent under another name.")
    print("\nConfirm the board name above is the right board before continuing.")


if __name__ == "__main__":
    main()
