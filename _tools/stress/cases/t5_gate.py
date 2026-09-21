#!/usr/bin/env python3
"""Tier 5 - the merge gate must describe what it actually checked.

`git_env.py --readiness <pr>` is the gate that replaced "an agent eyeballs the
PR". It exists because of a real incident: on fms-studio PR #39 the PR Checks
workflow failed and nothing in the pipeline noticed, because the old path looked
only for the `openclaw/review` stamp.

The case that matters most here is the quiet one. When a project has no PR CI at
all - which is fms-studio today, with the Cloud Build PR trigger deliberately not
created - there is nothing to fail, so the gate passes. It used to announce that
as "reviewed, and every check on this head is green". No check was green. No
check existed. Claiming verification that did not happen is the exact failure
this gate was built to stop, so a gate that does it about itself is worse than
none.

The three `gh` calls are stubbed: a live PR cannot be made to sit in each of
these states on demand.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, not_contains  # noqa: E402

ge = harness.load("ge_gate", os.path.join(harness.TOOLS, "git_env.py"))

TITLE = "merge gate: it must not claim checks it never saw"

FIELDS = {"github_repo": "acme/harness"}
HEAD = "b69c015beea7b69c015beea7b69c015beea7b69c"


class _R:
    def __init__(self, out="", rc=0, err=""):
        self.stdout, self.returncode, self.stderr = out, rc, err


def _gate(statuses, runs):
    """Run readiness() against stubbed gh output -> (exit code, printed text)."""
    def fake_run(cmd, **kw):
        if cmd[:3] == ["gh", "pr", "view"]:
            return _R(json.dumps({"headRefOid": HEAD, "url": "https://x/pull/1",
                                  "state": "OPEN", "title": "t"}))
        if "/status" in cmd[-1]:
            return _R(json.dumps({"statuses": statuses}))
        if "/actions/runs" in cmd[-1]:
            return _R(json.dumps({"workflow_runs": runs}))
        raise AssertionError(f"unexpected gh call: {cmd}")

    real, ge.subprocess.run = ge.subprocess.run, fake_run
    code = 0
    try:
        with harness.captured() as buf:
            try:
                ge.readiness(FIELDS, {}, "1")
            except SystemExit as e:
                code = e.code or 0
        return code, buf.getvalue()
    finally:
        ge.subprocess.run = real


REVIEWED = [{"context": ge.REVIEW_CONTEXT, "state": "success"}]


def a_green_review_with_no_ci_must_not_claim_green_checks():
    """The quiet failure: nothing ran, so nothing can be green."""
    code, out = _gate(REVIEWED, [])
    if code not in (0, None):
        raise AssertionError(f"a reviewed PR with no CI is still mergeable; got exit {code}")
    not_contains(out, "every check on this head is green",
                 "with zero runs there is no check to call green - saying so is the "
                 "confident-wrong claim this gate exists to prevent")
    contains(out, "NO CI ran", "the verdict must say that no CI ran")
    contains(out, "review ONLY", "the verdict must say what it actually checked")


def a_green_review_with_green_ci_says_so_plainly():
    """Positive control: the honest message must not swallow the real one."""
    code, out = _gate(REVIEWED, [{"path": ".github/workflows/pr-checks.yml",
                                  "status": "completed", "conclusion": "success",
                                  "created_at": "2026-09-21T10:00:00Z", "html_url": "u"}])
    if code not in (0, None):
        raise AssertionError(f"reviewed + green CI must be READY; got exit {code}")
    contains(out, "every check on this head is green",
             "when checks really are green the gate should say the strong thing")
    not_contains(out, "NO CI ran", "this PR had CI, so the no-CI caveat must not appear")


def a_red_check_blocks_even_with_a_green_review():
    """PR #39's actual incident: reviewed, CI failed, old gate saw only the review."""
    code, out = _gate(REVIEWED, [{"path": ".github/workflows/pr-checks.yml",
                                  "status": "completed", "conclusion": "failure",
                                  "created_at": "2026-09-21T10:00:00Z", "html_url": "u"}])
    if code != 2:
        raise AssertionError(f"a red check must block the merge (exit 2), got {code}")
    contains(out, "NOT READY", "a red check must be reported as not ready")
    contains(out, "pr-checks.yml", "the blocker must name the workflow that failed")


def a_review_on_an_older_sha_does_not_count():
    """A push after a review is a new SHA and needs a new review."""
    code, out = _gate([], [])
    if code != 2:
        raise AssertionError(f"an unreviewed head must block (exit 2), got {code}")
    contains(out, "not set on this head", "the gate must say the review is missing for THIS sha")


def an_unreadable_check_is_never_called_ready():
    """A token without the right permission must not read as 'nothing wrong'."""
    def fake_run(cmd, **kw):
        if cmd[:3] == ["gh", "pr", "view"]:
            return _R(json.dumps({"headRefOid": HEAD, "url": "u", "state": "OPEN", "title": "t"}))
        if "/status" in cmd[-1]:
            return _R(json.dumps({"statuses": REVIEWED}))
        return _R(rc=1, err="Resource not accessible by personal access token")

    real, ge.subprocess.run = ge.subprocess.run, fake_run
    try:
        with harness.captured() as buf:
            code = 0
            try:
                ge.readiness(FIELDS, {}, "1")
            except SystemExit as e:
                code = e.code or 0
    finally:
        ge.subprocess.run = real
    if code != 3:
        raise AssertionError(f"an unreadable check must exit 3 (unknown), got {code}")
    contains(buf.getvalue(), "UNKNOWN", "what could not be checked must be named")


CASES = [
    ("no CI: gate must not claim green checks", a_green_review_with_no_ci_must_not_claim_green_checks),
    ("green CI: gate says so plainly", a_green_review_with_green_ci_says_so_plainly),
    ("red check blocks a reviewed PR", a_red_check_blocks_even_with_a_green_review),
    ("review on an older sha does not count", a_review_on_an_older_sha_does_not_count),
    ("unreadable check is never ready", an_unreadable_check_is_never_called_ready),
]
