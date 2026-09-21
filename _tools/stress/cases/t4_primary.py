#!/usr/bin/env python3
"""Tier 4 - the primary checkout must not go stale, or be trampled.

PROJECT_CONTEXT describes this directory as "Primary checkout, read-only for
agents and kept on the Default branch". Nothing kept it there. A plain
`git fetch` moves remote-tracking refs and leaves the working tree where it was,
so the files an agent reads are whatever was checked out last.

Found 15 commits - two days - behind on the live project. Reading it produced a
bug report for a test that had not been failing for two days: the old file used a
TestingModule and failed on decorator metadata, while the current one constructs
the controller directly and passes. A full pipeline ran on that report and opened
a PR. Nothing anywhere said the files were old.

The other half matters as much. "Read-only for agents" means anything
uncommitted, or any branch other than the Default one, is a person's work in
progress. It must be reported and left alone, never fast-forwarded over.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq  # noqa: E402

dw = harness.load("dw_primary", os.path.join(harness.TOOLS, "delivery_watch.py"))

TITLE = "primary checkout: keep it current, never trample it"


def _git(cwd, *a):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *a],
                          cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


class _Ctx:
    """Only what refresh_primary reads."""

    def __init__(self, primary, branch):
        self.primary, self.branch = primary, branch


def _repo(behind=2):
    """A primary checkout `behind` commits behind origin/main -> (ctx, origin path)."""
    root = harness._mkdtemp("stress-prim-")
    origin, primary = os.path.join(root, "origin"), os.path.join(root, "primary")
    os.makedirs(origin)
    _git(origin, "init", "-q", "-b", "main", ".")
    open(os.path.join(origin, "f.txt"), "w").write("base\n")
    _git(origin, "add", "-A"); _git(origin, "commit", "-q", "-m", "base")
    _git(root, "clone", "-q", origin, primary)
    for i in range(behind):                       # origin moves on; the clone does not
        open(os.path.join(origin, "f.txt"), "a").write(f"line {i}\n")
        _git(origin, "add", "-A"); _git(origin, "commit", "-q", "-m", f"c{i}")
    _git(primary, "fetch", "-q", "origin")        # refs current, working tree is not
    return _Ctx(primary, "main"), origin


def _head(p):
    return _git(p, "rev-parse", "HEAD").stdout.strip()


def _behind(p):
    return int(_git(p, "rev-list", "--count", "HEAD..origin/main").stdout.strip() or 0)


def a_stale_checkout_is_fast_forwarded():
    """The whole point: the files on disk must become the current ones."""
    ctx, _ = _repo(behind=3)
    eq(_behind(ctx.primary), 3, "fixture: the checkout starts behind")
    errors = []
    with harness.captured():          # a successful fast-forward says so on stdout
        dw.refresh_primary(ctx, errors)
    eq(_behind(ctx.primary), 0, "a clean checkout on the Default branch must be brought current")
    eq(errors, [], "a successful fast-forward is not an error")
    eq(open(os.path.join(ctx.primary, "f.txt")).read().count("line"), 3,
       "the working FILES must be updated, not just the refs - reading them is the point")


def dry_run_reports_staleness_without_moving():
    """--dry is read-only, but silence would hide the very problem it should name."""
    ctx, _ = _repo(behind=2)
    before, errors = _head(ctx.primary), []
    dw.refresh_primary(ctx, errors, dry=True)
    eq(_head(ctx.primary), before, "--dry must not move the checkout")
    contains(" ".join(errors), "behind", "--dry must still say the checkout is stale")


def uncommitted_work_is_never_overwritten():
    """Read-only by contract, so anything uncommitted is a person's, not ours."""
    ctx, _ = _repo(behind=2)
    open(os.path.join(ctx.primary, "f.txt"), "a").write("someone's unsaved work\n")
    before, errors = _head(ctx.primary), []
    dw.refresh_primary(ctx, errors)
    eq(_head(ctx.primary), before, "a dirty checkout must not be moved")
    contains(open(os.path.join(ctx.primary, "f.txt")).read(), "someone's unsaved work",
             "the uncommitted change must survive")
    contains(" ".join(errors), "uncommitted", "the reason must be reported, not swallowed")


def another_branch_is_reported_not_switched():
    """Someone checked out a branch here; say so, do not yank it back."""
    ctx, _ = _repo(behind=2)
    _git(ctx.primary, "checkout", "-q", "-b", "someones-debugging")
    errors = []
    dw.refresh_primary(ctx, errors)
    eq(_git(ctx.primary, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip(), "someones-debugging",
       "the checked-out branch must be left alone")
    contains(" ".join(errors), "not the Default branch", "the reason must name the problem")


def a_diverged_checkout_is_reported_not_forced():
    """A local commit here cannot fast-forward; a reset would destroy it."""
    ctx, _ = _repo(behind=2)
    open(os.path.join(ctx.primary, "local.txt"), "w").write("local commit\n")
    _git(ctx.primary, "add", "-A"); _git(ctx.primary, "commit", "-q", "-m", "local only")
    before, errors = _head(ctx.primary), []
    dw.refresh_primary(ctx, errors)
    eq(_head(ctx.primary), before, "a diverged checkout must not be force-moved")
    contains(" ".join(errors), "diverged", "divergence must be named")


def an_up_to_date_checkout_says_nothing():
    """No news when there is no news - this runs every 15 minutes, per project."""
    ctx, _ = _repo(behind=0)
    errors = []
    dw.refresh_primary(ctx, errors)
    eq(errors, [], "an up-to-date checkout must not produce noise every heartbeat")


CASES = [
    ("stale checkout is fast-forwarded", a_stale_checkout_is_fast_forwarded),
    ("--dry reports but does not move", dry_run_reports_staleness_without_moving),
    ("uncommitted work is never overwritten", uncommitted_work_is_never_overwritten),
    ("another branch is reported, not switched", another_branch_is_reported_not_switched),
    ("diverged checkout is reported, not forced", a_diverged_checkout_is_reported_not_forced),
    ("up-to-date checkout is silent", an_up_to_date_checkout_says_nothing),
]
