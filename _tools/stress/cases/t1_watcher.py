#!/usr/bin/env python3
"""Tier 1 - delivery watcher logic, offline.

`commits_from_runs` decides whether a commit is on staging, and its rules are the
2026-09-19 incident turned into code (guide 12.5f). They are provider-independent,
so they can be driven with synthetic runs and must hold exactly.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq  # noqa: E402

dw = harness.load("dw_stress", os.path.join(harness.TOOLS, "delivery_watch.py"))

TITLE = "delivery watcher: build grouping and status translation"

NOW = datetime.datetime.now(datetime.timezone.utc)


def _at(mins_ago):
    return (NOW - datetime.timedelta(minutes=mins_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(commit, check, status, mins_ago, rid="1"):
    return {"commit": commit, "check": check, "status": status, "at": _at(mins_ago),
            "id": rid, "url": "u", "raw_status": status.upper()}


class _Ctx:
    def __init__(self, checks):
        self.f = {"deploy_checks": checks}


def _group(checks, runs):
    out = dw.commits_from_runs(_Ctx(checks), runs)
    return out[next(iter(out))] if out else None


def every_expected_check_green_is_deployed():
    eq(_group(["fe", "be"], [_run("a", "fe", "ok", 5), _run("a", "be", "ok", 4)])["status"], "ok",
       "all expected checks green = deployed")


def one_red_check_fails_the_commit():
    eq(_group(["fe", "be"], [_run("b", "fe", "ok", 5), _run("b", "be", "failed", 4)])["status"], "failed",
       "one red check must fail the commit; a monorepo's green frontend is not a deploy")


def one_running_check_is_not_green_yet():
    eq(_group(["fe", "be"], [_run("c", "fe", "ok", 5), _run("c", "be", "running", 4)])["status"], "running",
       "a check still running means the commit is not judged yet")


def a_missing_check_waits_but_not_forever():
    """The 12.5f stall: an expected check that never fires pinned every commit `running` forever."""
    recent = _group(["fe", "be"], [_run("d", "fe", "ok", 5)])
    eq(recent["status"], "running", "a missing check is assumed queued at first")
    eq(recent["missing"], [], "while waiting, nothing is blamed")

    stale = _group(["fe", "be"], [_run("e", "fe", "ok", dw.NO_BUILD_AFTER_MIN + 30)])
    eq(stale["status"], "ok", "after the cutoff the commit is judged on the checks that did run")
    eq(stale["missing"], ["be"], "and the check that never fired is named")


def a_later_run_supersedes_an_earlier_one_for_the_same_check():
    eq(_group(["fe", "be"], [_run("f", "fe", "failed", 60), _run("f", "fe", "ok", 5),
                             _run("f", "be", "ok", 5)])["status"], "ok",
       "a re-run of the same check supersedes the older attempt")


def no_expected_checks_means_every_run_must_be_green():
    """With Deploy checks unset there is nothing to wait for, so one red is still red."""
    eq(_group([], [_run("g", "any", "ok", 5)])["status"], "ok", "unlisted checks: green is green")
    eq(_group([], [_run("h", "any", "failed", 5)])["status"], "failed", "unlisted checks: red is red")


def bdesc_names_the_check_and_the_run():
    line = dw.bdesc(_run("a", "deploy-frontend-staging", "failed", 1, "abc-123"))
    for bit in ("deploy-frontend-staging", "abc-123"):
        contains(line, bit, "a build line must name the check and the run so it can be found")


def canonical_status_keys_translate_through_the_map():
    """Scripts pass canonical keys; a board's own vocabulary lives only in the map."""
    f, errs = harness.parsed(
        ("- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`",
         "- **Statuses:** `Backlog`, `In Dev`, `Staging`, `QA Failed`, `Blocked`, `Done`, `Won't do`"),
        ("- **Create status:** `to do`", "- **Create status:** `Backlog`"))
    eq(errs, [], "a board with entirely custom names must still validate")
    eq(f["status"], {"todo": "Backlog", "doing": "In Dev", "staged": "Staging",
                     "rejected": "QA Failed", "done": "Done", "cancelled": "Won't do",
                     "hold": "Blocked"},
       "every canonical key must map onto this board with no configuration")


CASES = [
    ("all checks green = deployed", every_expected_check_green_is_deployed),
    ("one red check fails the commit", one_red_check_fails_the_commit),
    ("one running check is not green", one_running_check_is_not_green_yet),
    ("missing check waits, then is named", a_missing_check_waits_but_not_forever),
    ("re-run supersedes the earlier attempt", a_later_run_supersedes_an_earlier_one_for_the_same_check),
    ("no expected checks: red is still red", no_expected_checks_means_every_run_must_be_green),
    ("build line names check and run", bdesc_names_the_check_and_the_run),
    ("status map inference on a custom board", canonical_status_keys_translate_through_the_map),
]
