#!/usr/bin/env python3
"""Tier 4 - watcher state under concurrency.

The heartbeat runs the watcher every 15 minutes for every project, and the same
session issues `--ack` for the actions it carried out. Those two touch one file
with no lock, so the interleaving below is not hypothetical - it is the normal
operating pattern.

A lost ack is not a cosmetic bug: the action fires again next heartbeat, which
means a second VanDev spawned at the same build, or a duplicate bug ticket.
"""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq  # noqa: E402

TITLE = "watcher state: concurrent runs and acks"

WATCH = os.path.join(harness.TOOLS, "delivery_watch.py")


def _sandbox():
    """A minimal project tree the watcher can resolve by slug."""
    root = tempfile.mkdtemp(prefix="stress-state-")
    art = os.path.join(root, "projects", "demo-state", "artifacts")
    os.makedirs(os.path.join(art, "specs"), exist_ok=True)
    code = os.path.join(root, "code")
    os.makedirs(code, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", code], check=True)
    subprocess.run(["git", "-C", code, "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-q", "--allow-empty", "-m", "init"], check=True)
    ctx = os.path.join(root, "projects", "demo-state", "PROJECT_CONTEXT.md")
    open(ctx, "w").write(harness.BASE
                         .replace("`harness`", "`demo-state`")
                         .replace("- **Tracker:** `clickup`", "- **Tracker:** `none`")
                         .replace("- **Tracker Board ID:** `1100770000001008`\n", "")
                         .replace("- **Tracker MCP server:** `tracker-harness`\n", "")
                         .replace("  - Tracker: `CLICKUP_API_TOKEN_HARNESS`\n", "")
                         .replace("- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`\n", "")
                         .replace("- **Create status:** `to do`\n", "")
                         .replace("- **Profile:** `factory`",
                                  "- **Profile:** `custom`\n- **Stages:** `review`, `merge-gate`")
                         .replace("/tmp/harness-code", code)
                         .replace("/tmp/harness-artifacts/", art + "/"))
    return root, os.path.join(art, "delivery_state.json")


def _run(root, *args):
    env = dict(os.environ, OPENCLAW_WORKSPACE=root)
    return subprocess.run([sys.executable, WATCH, "demo-state", *args],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                          env=env, timeout=120)


def an_ack_survives_a_concurrent_watch_run():
    """The interleaving the heartbeat actually produces.

    A watch run loads state, spends a minute on network calls, then saves. An
    --ack in that window is written and then overwritten by the stale copy.
    """
    root, path = _sandbox()
    json.dump({"watch_since": "2026-09-01T00:00:00Z",
               "acked": {"old-1": "2026-09-01T00:00:00Z"},
               "pending": {"deployed-pr9": {"kind": "DEPLOYED"}},
               "seen_feedback": []}, open(path, "w"))

    stale = json.load(open(path))          # process A loads

    r = _run(root, "--ack", "deployed-pr9")  # process B acks, for real
    if r.returncode != 0:
        raise AssertionError(f"the ack itself failed: {r.stderr.strip()[:200]}")
    eq("deployed-pr9" in json.load(open(path))["acked"], True, "sanity: the ack was written")

    # process A now saves the copy it loaded before the ack
    dw = harness.load("dw_state", WATCH)
    with dw.state_lock(path):
        disk, _ = dw.read_state(path)
        dw.write_state(path, dw.merge_state(disk, stale))

    final = json.load(open(path))
    if "deployed-pr9" not in final.get("acked", {}):
        raise AssertionError(
            "a concurrent watch run overwrote the ack with its stale copy. The action "
            "will fire again next heartbeat - a second VanDev spawned at the same build. "
            "save() must merge with what is on disk, under a lock, not clobber it.")


def a_corrupt_state_file_does_not_silently_reset_the_window():
    """`watch_since` silently resetting to now makes every past merge 'history'.

    The watcher then reports NO_ACTIONS - confidently, wrongly - and every ticket
    waiting on a merged PR stops moving with no error anywhere.
    """
    root, path = _sandbox()
    open(path, "w").write("{ this is not json")
    r = _run(root, "--dry")
    out = r.stdout + r.stderr
    if "NO_ACTIONS" in out and "state" not in out.lower():
        raise AssertionError(
            "a corrupt state file was swallowed: the watcher reset watch_since to now "
            "and reported NO_ACTIONS with no mention of the problem. It must say the "
            "state file was unreadable.")
    contains(out, "state", "an unreadable state file must be reported, not silently reset")


CASES = [
    ("ack survives a concurrent watch run", an_ack_survives_a_concurrent_watch_run),
    ("corrupt state file is reported", a_corrupt_state_file_does_not_silently_reset_the_window),
]
