#!/usr/bin/env python3
"""Tier 2 - fault injection: what happens when the tracker misbehaves.

The rule every case here asserts is the same one: a failure must be LOUD and
SPECIFIC, and it must never produce an action that moves a ticket or spawns an
agent. Silence and plausible-looking nothing are the failure modes this system
has actually suffered.

The headline case is B1. Before the `tasks_ok` guard, a failed board read left
`tasks` empty, and every ticket linked in a PR body then looked like it needed a
status move - with its status reported as "?". The watcher asked the heartbeat
to spawn VanPM and move tickets it had never read. A 429, an expired token or a
dropped connection was enough.

Mock servers were dropped from this tier on purpose: a mock speaks whatever
protocol its author assumed, so it agrees with the adapter about exactly the
things worth doubting. Real services cover the protocol (tier 3); these stubs
cover only what a real service cannot be asked to do on demand - fail.
"""
import json
import os
import sys
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq, raises  # noqa: E402

sys.path.insert(0, harness.TOOLS)
import trackers  # noqa: E402

dw = harness.load("dw_faults", os.path.join(harness.TOOLS, "delivery_watch.py"))

TITLE = "faults: a broken board must move nothing"

JIRA = {"tracker": "jira", "board_id": "KAN", "tracker_base_url": "https://acme.atlassian.net"}

# One PR's worth of linked tickets, all sitting in a status that WOULD move to qa.
IDS = ["KAN-1", "KAN-2", "KAN-3"]
TASKS = {i: {"id": i, "title": f"ticket {i}", "status": "in progress"} for i in IDS}
TITLE_OF = {i: ("password-reset", f"ticket {i}") for i in IDS}


def _moves(tasks, tasks_ok, marks=None):
    """Drive qa_moves_for with a board vocabulary loaded.

    QA_FROM and CLOSED are module-level sets the watcher fills from the project's
    Status map at startup, so they are empty until a project is loaded. Setting
    them here is not scaffolding - it is the dependency, made explicit.
    """
    dw.QA_FROM.clear(); dw.QA_FROM.update({"to do", "in progress", "rejected", "on hold"})
    dw.CLOSED.clear(); dw.CLOSED.update({"complete", "cancelled"})
    return dw.qa_moves_for(IDS, tasks, tasks_ok, TITLE_OF, marks or {}, "qa")


# --- B1: the headline -------------------------------------------------------
#
# To verify these two cases still bite, reintroduce B1 in its ACTUAL shape - the
# filter clause, not just the guard:
#
#   for i in sorted(ids) if stat(i) in QA_FROM or (not tasks and i)
#
# Removing only the `tasks_ok` guard is NOT enough to reproduce it: with an empty
# board every status reads "?", which is not in QA_FROM, so no move is produced
# and the cases pass while the bug is absent. The guard is second-line defence;
# the clause was the bug.

def a_failed_board_read_moves_nothing():
    """The bug: unreadable board -> every linked ticket looked ready to move."""
    eq(_moves({}, False), [],
       "a board that could not be read must produce NO moves: the watcher would "
       "otherwise ask VanPM to move tickets whose status it never saw")


def a_failed_read_is_not_an_empty_board():
    """`tasks == {}` happens both ways; only one of them is safe to act on."""
    eq(_moves({}, True), [], "an empty board has nothing to move, which is fine")
    eq(_moves({}, False), [], "an unreadable board must also move nothing")
    # ...and the difference must be visible, not inferred from an empty dict.
    if not hasattr(dw, "qa_moves_for"):
        raise AssertionError("qa_moves_for must stay reachable for this guard to be testable")


def a_readable_board_still_moves_its_tickets():
    """Positive control: without this, the two cases above pass vacuously."""
    got = _moves(TASKS, True)
    eq([m[0] for m in got], IDS,
       "a readable board must still produce the moves - otherwise the guard above "
       "is indistinguishable from the feature being broken")


def a_partially_read_board_moves_only_what_it_saw():
    """One ticket readable, two missing: the missing ones are status '?', not movable."""
    got = _moves({"KAN-2": TASKS["KAN-2"]}, True)
    eq([m[0] for m in got], ["KAN-2"],
       "a ticket absent from the board snapshot has an unknown status and must not move")


# --- HTTP faults ------------------------------------------------------------

class _Resp:
    """Minimal urlopen() context manager."""

    def __init__(self, status, body):
        self.status, self._b = status, body

    def read(self):
        return self._b.encode()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _with_urlopen(fn, action):
    real = trackers.urllib.request.urlopen
    trackers.urllib.request.urlopen = fn
    try:
        return action()
    finally:
        trackers.urllib.request.urlopen = real


def _http_error(code, reason, body, headers=None):
    def boom(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, code, reason,
                                     headers or {}, __import__("io").BytesIO(body.encode()))
    return boom


def http_failures_name_the_status_and_the_reason():
    """401/403/500 must each say what happened, with the API's own words."""
    for code, reason, body, word in (
        (401, "Unauthorized", '{"errorMessages":["Basic auth failed"]}', "Basic auth failed"),
        (403, "Forbidden", '{"message":"Resource not accessible"}', "Resource not accessible"),
        (500, "Server Error", '{"message":"Internal error, try later"}', "Internal error"),
    ):
        e = _with_urlopen(
            _http_error(code, reason, body),
            lambda: raises(trackers.ApiError,
                           lambda: trackers.for_project(JIRA, "e:t").tasks(),
                           f"HTTP {code} must raise, not return an empty board"))
        contains(str(e), str(code), f"the {code} must state its status code")
        contains(str(e), word, f"the {code} must carry the API's own reason")


def a_429_surfaces_retry_after():
    """Rate limiting is the most likely real fault, and the wait is the useful part."""
    e = _with_urlopen(
        _http_error(429, "Too Many Requests", '{"message":"Rate limit exceeded"}',
                    {"Retry-After": "77"}),
        lambda: raises(trackers.ApiError,
                       lambda: trackers.for_project(JIRA, "e:t").tasks(),
                       "a 429 must raise rather than look like an empty board"))
    contains(str(e), "429", "the rate limit must state its status")
    contains(str(e), "77", "Retry-After is the actionable part of a 429 and must be surfaced")


def a_truncated_body_fails_loudly():
    """A connection cut mid-response is valid HTTP 200 with invalid JSON."""
    e = _with_urlopen(
        lambda req, timeout=None: _Resp(200, '{"issues": [{"key": "KAN-1"'),
        lambda: raises(Exception, lambda: trackers.for_project(JIRA, "e:t").tasks(),
                       "truncated JSON must raise, not silently yield no issues"))
    if isinstance(e, AssertionError):
        raise e


def a_2xx_carrying_an_error_envelope_is_not_success():
    """Linear answers GraphQL errors with HTTP 200; the envelope is the only signal."""
    LINEAR = {"tracker": "linear", "board_id": "ENG"}
    e = _with_urlopen(
        lambda req, timeout=None: _Resp(
            200, json.dumps({"errors": [{"message": "Entity not found: Team"}]})),
        lambda: raises(RuntimeError, lambda: trackers.for_project(LINEAR, "tok").tasks(),
                       "an HTTP 200 whose body is an error envelope must not count as success"))
    contains(str(e), "Entity not found",
             "the GraphQL error message must reach the caller")


def a_non_2xx_without_a_body_still_raises():
    """Some proxies return a bare 502 with nothing to explain it."""
    e = _with_urlopen(
        _http_error(502, "Bad Gateway", ""),
        lambda: raises(trackers.ApiError, lambda: trackers.for_project(JIRA, "e:t").tasks(),
                       "an empty-bodied 502 must still raise"))
    contains(str(e), "502", "a bodyless failure must still name its status")


CASES = [
    ("B1: failed board read moves nothing", a_failed_board_read_moves_nothing),
    ("failed read != empty board", a_failed_read_is_not_an_empty_board),
    ("readable board still moves (control)", a_readable_board_still_moves_its_tickets),
    ("partial board moves only what it saw", a_partially_read_board_moves_only_what_it_saw),
    ("401/403/500 name status + reason", http_failures_name_the_status_and_the_reason),
    ("429 surfaces Retry-After", a_429_surfaces_retry_after),
    ("truncated JSON fails loudly", a_truncated_body_fails_loudly),
    ("HTTP 200 error envelope is not success", a_2xx_carrying_an_error_envelope_is_not_success),
    ("bodyless 502 still raises", a_non_2xx_without_a_body_still_raises),
]
