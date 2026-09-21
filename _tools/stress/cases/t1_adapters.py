#!/usr/bin/env python3
"""Tier 1 - tracker and CI adapters, offline.

No network: these cover the logic that runs before and after a request - which
provider is chosen, how a PR body is turned into ticket ids, what shape a task
has, and whether a provider that cannot do something says so instead of
returning a plausible-looking nothing.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq, raises  # noqa: E402

sys.path.insert(0, harness.TOOLS)
import ci  # noqa: E402
import trackers  # noqa: E402

TITLE = "adapters: dispatch, link parsing, refusals"

PR_BODY = """Fixes the staging build.

Tickets:
- https://app.clickup.com/t/9008123/abc123xy
- https://acme.atlassian.net/browse/BILL-42
- also BILL-77 in passing
- https://linear.app/acme/issue/ENG-9/some-title
- and ENG-12
"""

CLICKUP = {"tracker": "clickup", "board_id": "1100770000001008"}
JIRA = {"tracker": "jira", "board_id": "BILL", "tracker_base_url": "https://acme.atlassian.net"}
LINEAR = {"tracker": "linear", "board_id": "ENG"}


def _linear():
    tk = trackers.for_project(LINEAR, "tok")
    tk._team = {"key": "ENG", "id": "u", "name": "Eng", "states": {"nodes": []}}   # avoid the network
    return tk


def dispatch_picks_the_declared_provider():
    for f, kind in ((CLICKUP, "clickup"), (JIRA, "jira"), (LINEAR, "linear"),
                    ({"tracker": "none"}, "none")):
        eq(trackers.for_project(f, "t").kind, kind, f"for_project must honour tracker={f['tracker']}")


def an_unknown_tracker_is_refused_by_name():
    e = raises(RuntimeError, lambda: trackers.for_project({"tracker": "asana"}, "t"),
               "an unknown tracker must be refused")
    contains(str(e), "asana", "the refusal must name the tracker it was given")


def clickup_links_only_its_own():
    eq(trackers.for_project(CLICKUP, "t").links_in_text(PR_BODY), ["abc123xy"],
       "ClickUp must link its task URLs and nothing else")


def jira_links_urls_and_bare_keys():
    eq(trackers.for_project(JIRA, "t").links_in_text(PR_BODY), ["BILL-42", "BILL-77"],
       "Jira must link a browse URL and a bare PROJ-123 in prose")


def linear_links_urls_and_bare_keys():
    eq(_linear().links_in_text(PR_BODY), ["ENG-9", "ENG-12"],
       "Linear must link an issue URL and a bare ENG-12")


def no_tracker_links_nothing_and_reads_empty():
    tk = trackers.for_project({"tracker": "none"}, None)
    eq(tk.links_in_text(PR_BODY), [], "a project with no tracker links no tickets")
    eq(tk.tasks(), {}, "a project with no tracker has no tasks")


def no_tracker_refuses_writes_with_a_reason():
    tk = trackers.for_project({"tracker": "none"}, None)
    for fn, what in ((lambda: tk.set_status("X", "done"), "set_status"),
                     (lambda: tk.create_task("t"), "create_task"),
                     (lambda: tk.get_task("X"), "get_task")):
        e = raises(RuntimeError, fn, f"NoTracker.{what} must raise, not return something plausible")
        contains(str(e), "no tracker", f"NoTracker.{what} must say why")


def optional_capabilities_refuse_loudly():
    """Silently skipping an attachment means a spec whose screenshots never uploaded."""
    for f, kind in ((JIRA, "jira"), (LINEAR, "linear")):
        tk = trackers.for_project(f, "tok")
        e = raises(trackers.Unsupported, lambda: tk.attach("X", "/tmp/x", "x.png"),
                   f"{kind} cannot attach, and must say so")
        contains(str(e), kind, "the refusal names the provider")
        raises(trackers.Unsupported, lambda: tk.link_tasks("A", "B"),
               f"{kind} cannot link tickets, and must say so")


def clickup_implements_the_optional_capabilities():
    tk = trackers.for_project(CLICKUP, "t")
    for m in ("attach", "link_tasks", "update_task"):
        if not callable(getattr(tk, m, None)):
            raise AssertionError(f"ClickUp must implement {m}")


def api_errors_carry_the_providers_reason():
    e = trackers.ApiError(401, "Unauthorized", "Oauth token not found")
    contains(str(e), "401", "an ApiError states the status")
    contains(str(e), "Oauth token not found", "an ApiError carries the API's own message")


def error_bodies_never_leak_the_request():
    """An error body can echo the request, which carried the Authorization header."""
    leaky = '{"message": "bad", "request": {"headers": {"Authorization": "pk_SECRET"}}}'
    eq(trackers._reason(leaky), "bad",
       "only the known message field may be surfaced, never the whole body")


def ci_dispatch_picks_the_declared_provider():
    class Host:
        def gh(self, *a):
            return {"workflow_runs": []}

        def gcloud(self, *a):
            return []
    for sig, name in (("none", "NoCI"), ("cloud-build", "CloudBuild"), ("github-actions", "GitHubActions")):
        f = {"flow": {"deploy_signal": sig}, "gcp_project_id": "p", "github_repo": "o/r"}
        eq(type(ci.for_project(f, Host())).__name__, name, f"deploy_signal={sig}")


def no_ci_reports_no_runs():
    class Host:
        pass
    eq(ci.for_project({"flow": {"deploy_signal": "none"}}, Host()).runs("main"), [],
       "Deploy signal `none` means the merge is the signal; there are no runs to read")


CASES = [
    ("tracker dispatch", dispatch_picks_the_declared_provider),
    ("unknown tracker refused by name", an_unknown_tracker_is_refused_by_name),
    ("clickup link parsing", clickup_links_only_its_own),
    ("jira link parsing (url + bare key)", jira_links_urls_and_bare_keys),
    ("linear link parsing (url + bare key)", linear_links_urls_and_bare_keys),
    ("no-tracker reads are empty", no_tracker_links_nothing_and_reads_empty),
    ("no-tracker writes refuse", no_tracker_refuses_writes_with_a_reason),
    ("jira/linear refuse attach + link", optional_capabilities_refuse_loudly),
    ("clickup implements optional caps", clickup_implements_the_optional_capabilities),
    ("ApiError carries the reason", api_errors_carry_the_providers_reason),
    ("error bodies never leak the request", error_bodies_never_leak_the_request),
    ("ci dispatch", ci_dispatch_picks_the_declared_provider),
    ("no-ci reports no runs", no_ci_reports_no_runs),
]
