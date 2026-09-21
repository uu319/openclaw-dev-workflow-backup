#!/usr/bin/env python3
"""Tier 4 - the worktree ledger under damage and contention.

`worktrees.jsonl` is the source of truth for which agent holds which branch. It
is read and rewritten under an exclusive flock, so a fault in the READ path leaves
the lock held: `__enter__` takes the lock and then parses, and a `with` block only
calls `__exit__` when `__enter__` returned. Nothing here is theoretical - the
ledger is appended to by every create/finish/sweep on every project.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq, not_contains  # noqa: E402

TITLE = "worktree ledger: damage, locking, atomicity"


def _ledger(art, *lines):
    p = os.path.join(art, "worktrees.jsonl")
    open(p, "w", encoding="utf-8").write("".join(l + "\n" for l in lines))
    return p


GOOD = json.dumps({"branch": "feature/a", "slug": "demo-state", "status": "active", "events": []})


def a_malformed_ledger_line_fails_clearly_and_does_not_hang():
    """One bad line must name the file and the line, not raise inside the lock."""
    root, ctx, art = harness.project_sandbox()
    _ledger(art, GOOD, "{ this is not json", GOOD)
    try:
        r = harness.tool(root, "worktree.py", "demo-state", "list", timeout=45)
    except subprocess.TimeoutExpired:
        raise AssertionError(
            "worktree.py HUNG on a malformed ledger line. `__enter__` takes the flock "
            "before parsing, so a parse error skips `__exit__` and the lock is never "
            "released - every later worktree command blocks with no timeout.")
    out = r.stdout + r.stderr
    not_contains(out, "Traceback",
                 "a damaged ledger must be reported, not raised as a traceback")
    contains(out, "worktrees.jsonl", "the error must name the file")
    contains(out, "2", "the error must name the offending line number")


def the_lock_is_released_after_a_ledger_error():
    """Whatever the first call does, the next one must not block."""
    root, ctx, art = harness.project_sandbox()
    _ledger(art, GOOD, "{ broken", GOOD)
    try:
        harness.tool(root, "worktree.py", "demo-state", "list", timeout=45)
        r2 = harness.tool(root, "worktree.py", "demo-state", "list", timeout=45)
    except subprocess.TimeoutExpired:
        raise AssertionError("a second worktree.py call blocked after a ledger parse error - "
                             "the exclusive lock was not released")
    if r2.returncode not in (0, 1, 2):
        raise AssertionError(f"unexpected exit {r2.returncode}: {(r2.stdout + r2.stderr)[:200]}")


def a_healthy_ledger_still_lists():
    root, ctx, art = harness.project_sandbox()
    _ledger(art, GOOD)
    r = harness.tool(root, "worktree.py", "demo-state", "list", timeout=45)
    contains(r.stdout + r.stderr, "feature/a", "a valid ledger must still list its branches")


def the_ledger_temp_file_is_not_a_fixed_name():
    """Two concurrent writers sharing one `.tmp` interleave and one wins a half file.

    Same defect already fixed in the watcher's state file.
    """
    src = open(os.path.join(harness.TOOLS, "worktree.py"), encoding="utf-8").read()
    if 'ledger + ".tmp"' in src or "ledger + '.tmp'" in src:
        raise AssertionError(
            "the ledger is rewritten through a FIXED temp filename; two concurrent "
            "writers interleave in it and os.replace publishes whichever finishes last. "
            "Make it per-process, as delivery_watch.write_state does.")


def prs_md_is_written_atomically():
    """`prs.md` is what a person reads to find a PR; a crash mid-write truncates it."""
    src = open(os.path.join(harness.TOOLS, "worktree.py"), encoding="utf-8").read()
    i = src.find("def _render")
    body = src[i:i + 900]
    if 'open(' in body and 'os.replace' not in body:
        raise AssertionError(
            "prs.md is truncated in place with a plain open(...,'w') and no tmp+rename, "
            "so an interrupted render leaves a half-written file that agents then read.")


def sweep_never_deletes_when_github_could_not_be_asked():
    """`git push` uses the SSH key; `gh` uses the PAT. A PAT expiring (capped at 90
    days) leaves git working while the API goes dark. In that state "no PR" and
    "could not ask" must not look the same, because one of them deletes.
    """
    wt = harness.load("wt_stress", os.path.join(harness.TOOLS, "worktree.py"))
    eq(hasattr(wt, "ASK_FAILED"), True,
       "pr_for must have a distinct answer for 'GitHub could not be asked'")

    src = open(os.path.join(harness.TOOLS, "worktree.py"), encoding="utf-8").read()
    i = src.find("pr = pr_for(p, b)")
    window = src[i:]
    a, b_ = window.find("ASK_FAILED"), window.find('r["pushed_sha"] == tip')
    if a < 0:
        raise AssertionError("sweep does not branch on the could-not-ask answer at all")
    if b_ < 0:
        raise AssertionError("could not locate the git-only fallback to compare against")
    if a > b_:
        raise AssertionError("the could-not-ask check comes AFTER the git-only fallback that "
                             "deletes the worktree and branch - it must come first")
    contains(window[max(0, a - 200):a + 500], "KEPT",
             "an unanswered question must KEEP the worktree, not remove it")


def pr_for_separates_its_three_answers():
    wt = harness.load("wt_stress2", os.path.join(harness.TOOLS, "worktree.py"))

    class NoGitHub:
        github = False
    eq(wt.pr_for(NoGitHub(), "feature/x"), None,
       "a project with no GitHub configured returns None, not the failure sentinel")
    if wt.ASK_FAILED is None or wt.ASK_FAILED == {}:
        raise AssertionError("ASK_FAILED must be distinguishable from None and from {}")


CASES = [
    ("malformed ledger line fails clearly", a_malformed_ledger_line_fails_clearly_and_does_not_hang),
    ("lock released after a ledger error", the_lock_is_released_after_a_ledger_error),
    ("healthy ledger still lists", a_healthy_ledger_still_lists),
    ("ledger temp file is per-process", the_ledger_temp_file_is_not_a_fixed_name),
    ("prs.md written atomically", prs_md_is_written_atomically),
    ("sweep keeps when GitHub cannot be asked", sweep_never_deletes_when_github_could_not_be_asked),
    ("pr_for separates its three answers", pr_for_separates_its_three_answers),
]
