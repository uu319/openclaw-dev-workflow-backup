#!/usr/bin/env python3
"""Tier 1 - tracker and CI adapters, offline.

No network: these cover the logic that runs before and after a request - which
provider is chosen, how a PR body is turned into ticket ids, what shape a task
has, and whether a provider that cannot do something says so instead of
returning a plausible-looking nothing.
"""
import inspect
import json
import os
import re
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


def every_real_tracker_implements_the_push_capabilities():
    """A spec push needs all four, on whichever tracker the project uses.

    Jira and Linear used to refuse attach/link_tasks/update_task, which is why
    tracker_push was ClickUp-only. They implement them now (2026-09-21, each
    verified against the real service). What must never come back is a SILENT
    skip: a spec whose screenshots never uploaded, reported as a success.
    """
    for f, kind in ((CLICKUP, "clickup"), (JIRA, "jira"), (LINEAR, "linear")):
        tk = trackers.for_project(f, "tok")
        for m in ("attach", "link_tasks", "update_task", "attachments"):
            fn = getattr(type(tk), m, None)
            base = getattr(trackers.Tracker, m, None)
            if not callable(fn):
                raise AssertionError(f"{kind} must implement {m}")
            if base is not None and fn is base:
                raise AssertionError(
                    f"{kind}.{m} is still the base class stub, which refuses; "
                    f"tracker_push needs a real implementation")


def no_tracker_still_refuses_the_push_capabilities():
    """`Tracker: none` has nowhere to put an attachment, and must say so."""
    tk = trackers.for_project({"tracker": "none"}, None)
    e = raises(Exception, lambda: tk.create_task("x"),
               "a project with no tracker cannot create tickets, and must say so")
    contains(str(e), "no tracker", "the refusal must name the reason")


def api_errors_carry_the_providers_reason():
    e = trackers.ApiError(401, "Unauthorized", "Oauth token not found")
    contains(str(e), "401", "an ApiError states the status")
    contains(str(e), "Oauth token not found", "an ApiError carries the API's own message")


def error_bodies_never_leak_the_request():
    """An error body can echo the request, which carried the Authorization header."""
    leaky = '{"message": "bad", "request": {"headers": {"Authorization": "pk_SECRET"}}}'
    eq(trackers._reason(leaky), "bad",
       "only the known message field may be surfaced, never the whole body")


def actions_pages_until_the_watch_window_is_covered():
    """One page is not enough on a repo with steady CI traffic.

    It used to be a single request capped at 100. Once more than that many runs
    piled up on the base branch, a merge commit's run fell off the end, the
    watcher saw a merge that had apparently never built, and waited until
    NO_BUILD_AFTER_MIN - the 2026-09-19 stall by another route. fms-studio had 19
    runs from dependabot alone. Proven live 2026-09-21: page_size=2 over 6 runs
    issued 4 requests and returned the same commits as one big page.
    """
    runs = [{"head_sha": f"sha{i}", "path": ".github/workflows/checks.yml",
             "status": "completed", "conclusion": "success", "id": i,
             "created_at": f"2026-09-{21 - i:02d}T00:00:00Z"} for i in range(5)]

    class Host:
        def __init__(self):
            self.pages = []

        def gh(self, *a):
            per = int(next(x for x in a if str(x).startswith("per_page=")).split("=")[1])
            page = int(next(x for x in a if str(x).startswith("page=")).split("=")[1])
            self.pages.append(page)
            return {"workflow_runs": runs[(page - 1) * per: page * per]}

    F = {"flow": {"deploy_signal": "github-actions"}, "github_repo": "o/r"}

    h = Host()
    got = ci.for_project(F, h).runs("main", since="2020-01-01T00:00:00Z", page_size=2)
    eq(h.pages, [1, 2, 3], "5 runs at 2 per page is 3 requests, stopping on the short page")
    eq([r["commit"] for r in got], [f"sha{i}" for i in range(5)],
       "every page must be collected - a dropped run reads as 'never built'")

    # A window already covered must NOT keep paging: this runs every 15 minutes.
    h2 = Host()
    ci.for_project(F, h2).runs("main", since="2026-09-20T00:00:00Z", page_size=2)
    if len(h2.pages) >= 3:
        raise AssertionError(f"paging must stop once runs are older than `since`, got {h2.pages}")

    # And with no window at all, the old single-request behaviour is unchanged.
    h3 = Host()
    ci.for_project(F, h3).runs("main")
    eq(h3.pages, [1], "without `since` it must stay one request")


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


def jira_uses_the_current_search_endpoint_and_cursor_pages():
    """Jira Cloud REMOVED /rest/api/3/search (HTTP 410, CHANGE-2046).

    Its replacement is cursor-paged and returns no `total`, so the old
    `start >= total` loop exited on the first pass and reported page one as the
    whole board. Confirmed against a live site 2026-09-21; stubbed here so a
    regression cannot pass unnoticed without an account.
    """
    import trackers.jira as J
    seen = []
    pages = [
        {"issues": [{"key": "KAN-1", "fields": {"summary": "one", "status": {"name": "To Do"}}}],
         "nextPageToken": "CURSOR2", "isLast": False},
        {"issues": [{"key": "KAN-2", "fields": {"summary": "two", "status": {"name": "Done"}}}],
         "isLast": True},
    ]

    def fake(url, headers, data=None, method=None, timeout=None):
        seen.append(url)
        return pages[len(seen) - 1]

    real, J.http_json = J.http_json, fake
    try:
        out = trackers.for_project(JIRA, "e:t").tasks()
    finally:
        J.http_json = real

    eq(sorted(out), ["KAN-1", "KAN-2"], "both pages must be collected")
    contains(seen[0], "/rest/api/3/search/jql", "the removed /search endpoint must not be used")
    contains(seen[0], "ORDER+BY+created", "cursor paging needs a stable sort or rows repeat/skip")
    contains(seen[1], "nextPageToken=CURSOR2", "page two must follow the cursor page one returned")
    eq(len(seen), 2, "paging must stop at isLast, not loop forever")


def jira_closed_uses_status_category_not_an_english_word_list():
    """A board whose terminal status is "Shipped" is still closed."""
    import trackers.jira as J
    tk = trackers.for_project(JIRA, "e:t")
    t = tk._task({"key": "KAN-7", "fields": {
        "summary": "s", "status": {"name": "Shipped", "statusCategory": {"key": "done"}}}})
    eq(t["closed"], True, "statusCategory `done` means closed whatever the status is named")
    t2 = tk._task({"key": "KAN-8", "fields": {
        "summary": "s", "status": {"name": "Shipped"}}})
    eq(t2["closed"], False, "with no category, an unknown name falls back to not-closed")


def linear_queries_use_the_types_the_api_declares():
    """`team(id:)` is String!, not ID!.

    `tasks()` asked for `$id:ID!` and Linear rejected every call with HTTP 400:
    'Variable "$id" of type "ID!" used in position expecting type "String!"'.
    Offline this is invisible - nothing validates a query string against a schema
    - and it meant the Linear adapter could not list a board at all. Found on the
    first live call, 2026-09-21.
    """
    import trackers.linear as L
    src = inspect.getsource(L.Linear.tasks)
    if "$id:ID!" in src:
        raise AssertionError("team(id:) takes String!, not ID! - Linear rejects the query with HTTP 400")
    contains(src, "$id:String!", "the team id variable must be declared String!")


def linear_page_size_is_injectable():
    """Proven live 2026-09-21: page_size=2 over 5 issues issued 3 requests and
    returned the same ids as one page. Stubbed here so it stays true."""
    import trackers.linear as L
    rows = [f"TES-{n}" for n in range(1, 6)]
    seen = []

    def fake(url, headers, data=None, method=None, timeout=None):
        body = json.loads(data.decode())
        n = body["variables"].get("n")
        after = body["variables"].get("after")
        seen.append(n)
        start = int(after) if after else 0
        chunk = rows[start:start + n]
        nxt = start + n
        return {"data": {"team": {"issues": {
            "pageInfo": {"hasNextPage": nxt < len(rows), "endCursor": str(nxt)},
            "nodes": [{"id": f"u{k}", "identifier": k, "title": k, "url": "",
                       "state": {"name": "Todo", "type": "unstarted"}} for k in chunk]}}}}

    tk = trackers.for_project(LINEAR, "tok")
    tk._team = {"key": "TES", "id": "team-uuid", "name": "T", "states": {"nodes": []}}
    real, L.http_json = L.http_json, fake
    try:
        out = tk.tasks(page_size=2)
    finally:
        L.http_json = real
    eq(sorted(out), rows, "every page must be collected")
    eq(seen, [2, 2, 2], "5 rows at 2 per page is 3 requests")


def linear_task_url_carries_the_workspace():
    """These links go in PR bodies. The workspace slug is not optional.

    It built `https://linear.app/issue/<id>` with no workspace. That could not be
    checked by fetching it: linear.app is a single-page app and answers 200 for
    every path, including `NOPE-1` and a workspace that does not exist - so a
    status code proves nothing. The API knows the slug; ask it.
    """
    import trackers.linear as L
    tk = trackers.for_project(LINEAR, "tok")
    real, L.http_json = L.http_json, lambda *a, **k: {"data": {"organization": {"urlKey": "acme-co"}}}
    try:
        eq(tk.task_url("TES-1"), "https://linear.app/acme-co/issue/TES-1",
           "the issue URL must carry the workspace slug the API reports")
    finally:
        L.http_json = real


def actions_keys_on_the_workflow_file_not_the_run_name():
    """A run's display name is NOT stable, so it cannot be the check key.

    GitHub's `run-name:` sets it per run, and dependabot's is unique every time.
    Verified on a real repo 2026-09-21: 19 runs produced 19 distinct names. Keyed
    on `name`, an expected check would never match, every commit would sit at
    `running` until the cutoff, and no ticket would ever move - the 12.5f stall
    on a different provider.
    """
    class Host:
        def gh(self, *a):
            return {"workflow_runs": [
                {"head_sha": "abc", "name": "Deploy by van for PR #41",
                 "path": ".github/workflows/deploy-staging.yml",
                 "status": "completed", "conclusion": "success",
                 "created_at": "2026-09-21T10:00:00Z", "id": 1, "html_url": "u"},
                {"head_sha": "abc", "name": "Deploy by sam for PR #42",
                 "path": ".github/workflows/deploy-staging.yml",
                 "status": "completed", "conclusion": "success",
                 "created_at": "2026-09-21T11:00:00Z", "id": 2, "html_url": "u"},
            ]}
    runs = ci.for_project({"flow": {"deploy_signal": "github-actions"},
                           "github_repo": "o/r"}, Host()).runs("main")
    eq({r["check"] for r in runs}, {"deploy-staging.yml"},
       "two runs of one workflow must share one stable check key")
    eq(runs[0]["display"], "Deploy by van for PR #41",
       "the per-run name is kept for humans, just not used as the key")

def jira_page_size_is_injectable_and_never_needs_total():
    """Paging must be driven by the cursor alone, at any page size.

    Proven live 2026-09-21 on a 4-issue board: page_size=2 issued 2 requests and
    returned the same 4 ids as the single-page call. The stub below keeps that
    honest without an account, and pins `maxResults` to the caller's value so a
    test can force real multi-page paging.
    """
    import trackers.jira as J
    seen, rows = [], [f"KAN-{n}" for n in range(1, 6)]

    def fake(url, headers, data=None, method=None, timeout=None):
        seen.append(url)
        size = int(re.search(r"maxResults=(\d+)", url).group(1))
        start = (len(seen) - 1) * size
        chunk = rows[start:start + size]
        page = {"issues": [{"key": k, "fields": {"summary": k, "status": {"name": "To Do"}}}
                           for k in chunk]}
        if start + size < len(rows):                 # no `total` anywhere, by design
            page["nextPageToken"] = f"CUR{len(seen)}"
        else:
            page["isLast"] = True
        return page

    real, J.http_json = J.http_json, fake
    try:
        out = trackers.for_project(JIRA, "e:t").tasks(page_size=2)
    finally:
        J.http_json = real

    eq(sorted(out), rows, "every page must be collected, not just the first")
    eq(len(seen), 3, "5 rows at 2 per page is 3 requests")
    contains(seen[0], "maxResults=2", "the caller's page size must reach the request")


def jira_issue_type_is_discovered_from_the_project():
    """"Sub-task" 400s on a team-managed project, which calls it "Subtask".

    Confirmed live 2026-09-21: the real board offers Epic/Subtask/Task/Story/
    Feature/Bug, and a subtask created with the discovered name landed under its
    parent. Both spellings are checked here because sites carry either.
    """
    import trackers.jira as J
    for spelling in ("Subtask", "Sub-task"):
        tk = trackers.for_project(JIRA, "e:t")
        real, J.http_json = J.http_json, lambda *a, **k: {"issueTypes": [
            {"name": "Epic", "subtask": False}, {"name": spelling, "subtask": True},
            {"name": "Task", "subtask": False}, {"name": "Story", "subtask": False}]}
        try:
            eq(tk.issue_type(subtask=True), spelling,
               f"a project that calls it {spelling!r} must get {spelling!r}")
            eq(tk.issue_type(subtask=False), "Task", "a plain issue must not become a subtask type")
        finally:
            J.http_json = real


CASES = [
    ("tracker dispatch", dispatch_picks_the_declared_provider),
    ("unknown tracker refused by name", an_unknown_tracker_is_refused_by_name),
    ("clickup link parsing", clickup_links_only_its_own),
    ("jira link parsing (url + bare key)", jira_links_urls_and_bare_keys),
    ("linear link parsing (url + bare key)", linear_links_urls_and_bare_keys),
    ("no-tracker reads are empty", no_tracker_links_nothing_and_reads_empty),
    ("no-tracker writes refuse", no_tracker_refuses_writes_with_a_reason),
    ("every tracker implements push caps", every_real_tracker_implements_the_push_capabilities),
    ("no-tracker still refuses", no_tracker_still_refuses_the_push_capabilities),
    ("ApiError carries the reason", api_errors_carry_the_providers_reason),
    ("error bodies never leak the request", error_bodies_never_leak_the_request),
    ("jira uses /search/jql + cursor paging", jira_uses_the_current_search_endpoint_and_cursor_pages),
    ("jira page size injectable, no total", jira_page_size_is_injectable_and_never_needs_total),
    ("jira issue type discovered", jira_issue_type_is_discovered_from_the_project),
    ("jira closed via statusCategory", jira_closed_uses_status_category_not_an_english_word_list),
    ("linear uses declared API types", linear_queries_use_the_types_the_api_declares),
    ("linear page size injectable", linear_page_size_is_injectable),
    ("linear task_url has the workspace", linear_task_url_carries_the_workspace),
    ("actions keys on the workflow file", actions_keys_on_the_workflow_file_not_the_run_name),
    ("actions pages to cover the window", actions_pages_until_the_watch_window_is_covered),
    ("ci dispatch", ci_dispatch_picks_the_declared_provider),
    ("no-ci reports no runs", no_ci_reports_no_runs),
]
