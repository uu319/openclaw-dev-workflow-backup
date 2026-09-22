#!/usr/bin/env python3
"""Tier 1 - a ticket is its id, not its title.

The bug these cases pin: tracker_push matched a spec ticket to its board ticket
by exact title. Editing a `title:` therefore made the ticket look new - the push
created a second one, and the first kept the subtasks, so a feature ended up
split across two parents with nothing saying so (2026-09-22).

The fix is a stable `id:` written back into the spec's own `---ticket` header on
the push that creates the ticket. Every case here is about that id surviving
something: a rename, a re-push, a half-finished push, a deleted ticket.

The second half covers the other end of the same problem - ClickUp's task PUT,
where `parent` used to be filtered out and the task name was sent under a key
ClickUp ignores.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, eq, raises  # noqa: E402

sys.path.insert(0, harness.TOOLS)
import trackers  # noqa: E402

PUSH = os.path.join(harness.WS, "project-manager/skills/feature-breakdown/scripts/tracker_push.py")
push = harness.load("tracker_push_ids", PUSH)


# --------------------------------------------------------------- a spec to push

def spec_text(parent_title="[Feature] Password step", fe_title="[FE] Password form"):
    """Two tickets that pass the real validator, so the real push runs."""
    def body(what):
        return f"""## Context
Parent: {parent_title} · Lane: see header

## User story
As an organizer, I want {what}, so that guests cannot open a private album.

## In scope
- The password step in the wizard
- Persisting the hash on the draft

## Out of scope (do NOT build)
- The guest-side prompt
- Password reset

## Acceptance criteria
- Given the organizer is on the step, when the field has 8 characters and Continue is clicked, then `PATCH /api/events/:id/draft` is called and the wizard moves on.
- Given fewer than 8 characters, when the field is blurred, then 'Use at least 8 characters' shows and Continue is disabled.
- Given the API returns 5xx, when Continue is clicked, then the error text shows and the typed value is kept.

## Technical notes
- Files/paths: frontend/src/app/events/new/step-3-1/

## Depends on / blocks
- Depends on: none

## Test notes (how QA verifies)
- Run the E2E scenario.
"""
    return f"""# Spec: password step

---ticket
title: {parent_title}
lane: FEATURE
priority: high

{body("a password on my event")}
---end

---ticket
title: {fe_title}
lane: FE
parent: {parent_title}
estimate_hours: 4
priority: normal

{body("the password form to validate")}
---end
"""


class FakeBoard:
    """A board that remembers what it was asked to do, and nothing else.

    Deliberately not a ClickUp mock: these cases are about which ticket the push
    decides to write to, which is the push's own logic.
    """

    kind, marker_suffix = "clickup", ".clickup.json"

    def __init__(self):
        self.t, self.n, self.calls = {}, 0, []

    def board_info(self):
        return "Board", ["to do", "in progress", "qa", "complete", "cancelled"], "sandbox"

    def tasks(self):
        return {k: dict(v) for k, v in self.t.items()}

    def get_task(self, tid):
        if tid not in self.t:
            raise RuntimeError(f"no ticket {tid} on this board")
        return dict(self.t[tid])

    def task_url(self, tid):
        return f"https://board.test/t/{tid}"

    def create_task(self, title, description="", status=None, parent=None, **kw):
        self.n += 1
        tid = f"t{self.n}"
        self.t[tid] = {"id": tid, "title": title, "description": description,
                       "status": status or "to do", "url": self.task_url(tid),
                       "parent": parent, "closed": False, "assignees": [], "updated": None}
        self.calls.append(("create", tid, title))
        return dict(self.t[tid])

    def update_task(self, tid, **f):
        self.get_task(tid)
        if f.get("title"):
            self.t[tid]["title"] = f["title"]
        if f.get("description") is not None:
            self.t[tid]["description"] = f["description"]
        if f.get("parent"):
            self.t[tid]["parent"] = f["parent"]
        self.calls.append(("update", tid, f.get("title")))
        return {"id": tid, "ok": True}

    def set_status(self, tid, status):
        self.get_task(tid)
        self.t[tid]["status"] = status
        self.calls.append(("status", tid, status))

    def link_tasks(self, tid, other):
        return None

    def attachments(self, tid):
        return []

    def attach(self, tid, path, filename):
        return {"title": filename, "url": f"https://board.test/f/{filename}"}


RETITLE = (("[Feature] Password step", "[Feature] Set event password"),
           ("[FE] Password form", "[FE] Set password: form + validation"))


def retitle(spec):
    """Edit the titles in place, the way a person editing the spec would.

    Rewriting the whole file would also drop the `id:` lines the push wrote, and
    then these cases would pass for the wrong reason.
    """
    text = open(spec, encoding="utf-8").read()
    for old, new in RETITLE:
        text = text.replace(old, new)
    open(spec, "w", encoding="utf-8").write(text)


def sandbox(text):
    """A real project tree with one spec in it. -> (root, ctx, spec path)."""
    root, ctx, art = harness.project_sandbox(slug="pushids", tracker="clickup")
    code = harness.BASE.split("- **Code (CWD):** `")[1].split("`")[0]
    body = (harness.BASE
            .replace("`harness`", "`pushids`")
            .replace("- **Tracker MCP server:** `tracker-harness`", "- **Tracker MCP server:** `tracker-pushids`")
            .replace(code, os.path.join(root, "code"))
            .replace("/tmp/harness-artifacts/", art + "/"))
    open(ctx, "w", encoding="utf-8").write(body)
    spec = os.path.join(art, "specs", "password-step.md")
    open(spec, "w", encoding="utf-8").write(text)
    return root, ctx, spec


def run_push(root, ctx, spec, board, *extra):
    """Drive the real main() against a FakeBoard. -> captured stdout."""
    argv, real_for = sys.argv, trackers.for_project
    trackers.for_project = lambda fields, token=None: board
    sys.argv = ["tracker_push.py", "--context", ctx, "--spec", spec, *extra]
    env_ws, env_tok = os.environ.get("OPENCLAW_WORKSPACE"), os.environ.get("CLICKUP_API_TOKEN_HARNESS")
    os.environ["OPENCLAW_WORKSPACE"], os.environ["CLICKUP_API_TOKEN_HARNESS"] = root, "tok"
    try:
        with harness.captured() as out:
            push.main()
        return out.getvalue()
    finally:
        sys.argv, trackers.for_project = argv, real_for
        for k, v in (("OPENCLAW_WORKSPACE", env_ws), ("CLICKUP_API_TOKEN_HARNESS", env_tok)):
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)


# --------------------------------------------------------------- the headline

def a_renamed_ticket_is_updated_not_duplicated():
    """The bug, end to end: rename both titles, push again, get no new tickets."""
    root, ctx, spec = sandbox(spec_text())
    board = FakeBoard()
    run_push(root, ctx, spec, board)
    eq(len(board.t), 2, "the first push creates the parent and its one subtask")
    first = sorted(board.t)

    # Rename both titles in place - the ids the first push stamped stay where they are.
    retitle(spec)
    stamped = push.parse_spec(spec)
    eq([bool(t.get("id")) for t in stamped], [True, True],
       "the first push must have written `id:` into both headers - without it the rename "
       "below is exactly the old bug")
    run_push(root, ctx, spec, board)

    eq(sorted(board.t), first,
       "a renamed ticket must be UPDATED in place. New ids here mean the push matched by "
       "title, created duplicates, and orphaned the original's subtasks")
    eq(board.t[first[0]]["title"], "[Feature] Set event password",
       "the rename must reach the board, not just the spec")
    eq(board.t[first[1]]["parent"], first[0],
       "the subtask must still hang off the same parent after the rename")


def the_marker_follows_the_rename():
    """One entry per ticket, under the new title. A leftover old key reads as stale."""
    root, ctx, spec = sandbox(spec_text())
    board = FakeBoard()
    run_push(root, ctx, spec, board)
    retitle(spec)
    out = run_push(root, ctx, spec, board)

    marker = json.load(open(spec[:-3] + ".clickup.json"))
    keys = sorted(k for k in marker if not k.startswith("_"))
    eq(keys, ["[FE] Set password: form + validation", "[Feature] Set event password"],
       "the marker must hold one entry per ticket, keyed by its CURRENT title")
    contains(out, "renamed", "the rename must be reported, not done silently")
    harness.not_contains(out, "STALE",
                         "the ticket under its old title is not stale - it is the same ticket")


def a_half_finished_push_still_stamps_what_it_made():
    """The parent exists, the subtask never got made: the parent keeps its id."""
    root, ctx, spec = sandbox(spec_text())

    class DiesOnTheSubtask(FakeBoard):
        def create_task(self, title, *a, **kw):
            if title.startswith("[FE]"):
                raise RuntimeError("board went away")
            return FakeBoard.create_task(self, title, *a, **kw)

    board = DiesOnTheSubtask()
    try:
        run_push(root, ctx, spec, board)
    except RuntimeError:
        pass
    # The push died, so nothing was stamped - and that is the case the next push must
    # survive without duplicating the parent it did create.
    board2 = FakeBoard()
    board2.t, board2.n = dict(board.t), board.n
    out = run_push(root, ctx, spec, board2)
    eq(len(board2.t), 2, "the next push must adopt the parent that already exists, not make a second "
                         f"one: {out}")


def an_id_the_board_does_not_have_stops_the_push():
    """Falling back to the title here is what made duplicates. Stop and say so instead."""
    root, ctx, spec = sandbox(spec_text().replace("lane: FEATURE", "id: nope-9999\nlane: FEATURE"))
    board = FakeBoard()
    e = raises(SystemExit, lambda: run_push(root, ctx, spec, board),
               "a spec id that the board cannot read must stop the push")
    eq(e.code, 5, "a dangling id needs its own exit code, not the generic one")
    eq(board.calls, [], "nothing may be written when an id does not resolve")


def two_tickets_may_not_claim_one_id():
    """Otherwise the second silently overwrites the first on every push."""
    dup = spec_text().replace("lane: FEATURE", "id: t1\nlane: FEATURE").replace("lane: FE\n", "id: t1\nlane: FE\n")
    root, ctx, spec = sandbox(dup)
    e = raises(SystemExit, lambda: run_push(root, ctx, spec, FakeBoard()),
               "two spec tickets pointing at one board ticket must be rejected")
    eq(e.code, 2, "that is a spec error, so it is the validator's exit code")


def a_placeholder_id_is_not_an_id():
    """`id: <ticket id>` copied from the template must not be sent to the board."""
    root, ctx, spec = sandbox(spec_text().replace("lane: FEATURE", "id: <ticket id>\nlane: FEATURE"))
    e = raises(SystemExit, lambda: run_push(root, ctx, spec, FakeBoard()),
               "an unreplaced placeholder must be rejected, not treated as a ticket id")
    eq(e.code, 2, "a placeholder is a spec error")


def prune_really_cancels_the_ticket():
    """--prune used to crash on an undefined name; once reachable it must not no-op.

    `update({"status": ...})` is dropped by the payload filter, so the old line
    would have printed "pruned" and left the ticket open on the board.
    """
    root, ctx, spec = sandbox(spec_text())
    board = FakeBoard()
    run_push(root, ctx, spec, board)
    # Drop the subtask from the spec, keeping the parent and its stamped id.
    text = open(spec, encoding="utf-8").read()
    open(spec, "w", encoding="utf-8").write(text[:text.index("---ticket", text.index("---end"))])
    out = run_push(root, ctx, spec, board, "--prune")

    contains(out, "pruned", "the dropped ticket has to be reported")
    eq(board.t["t2"]["status"], "cancelled",
       "a pruned ticket must actually be cancelled on the board, not only in the marker")
    marker = json.load(open(spec[:-3] + ".clickup.json"))
    eq(list(marker.get("_cancelled", {})), ["[FE] Password form"],
       "and the marker records which ticket that was")


# --------------------------------------------------------------- the write-back

def the_id_lands_in_the_right_header():
    """Two blocks, two ids, each under its own title - and the body is untouched."""
    root, ctx, spec = sandbox(spec_text())
    board = FakeBoard()
    run_push(root, ctx, spec, board)
    got = push.parse_spec(spec)
    eq([t["id"] for t in got], ["t1", "t2"],
       "each header gets the id of ITS ticket, in document order")
    eq(got[0]["lane"], "FEATURE", "the rest of the header must survive the rewrite")
    contains(got[1]["body"], "## Acceptance criteria", "the body must survive the rewrite")


def the_write_back_refuses_a_spec_that_moved_under_it():
    """Someone editing the file mid-push must not get an id written into the wrong ticket."""
    root, ctx, spec = sandbox(spec_text())
    tickets = push.parse_spec(spec)
    open(spec, "w", encoding="utf-8").write(spec_text().split("---ticket")[0] + "# only prose now\n")
    with harness.captured():
        wrote = push.inject_ids(spec, tickets, {t["title"]: "t9" for t in tickets})
    eq(wrote, [], "when the block count no longer matches, nothing may be written")
    harness.not_contains(open(spec).read(), "id: t9",
                         "an id written into a spec the push no longer recognises could land "
                         "on the wrong ticket")


def a_dry_run_never_touches_the_spec():
    root, ctx, spec = sandbox(spec_text())
    before = open(spec).read()
    out = run_push(root, ctx, spec, FakeBoard(), "--dry-run")
    eq(open(spec).read(), before, "--dry-run must leave the spec file byte-identical")
    contains(out, "would write", "a dry run still has to say the spec would be stamped")


def existing_id_is_still_how_a_ticket_is_adopted():
    """The hand-written form keeps working, and becomes an `id:` afterwards."""
    board = FakeBoard()
    board.create_task("A ticket a person made")
    root, ctx, spec = sandbox(spec_text().replace("lane: FEATURE", "existing_id: t1\nlane: FEATURE"))
    run_push(root, ctx, spec, board)
    eq(board.t["t1"]["title"], "[Feature] Password step",
       "the adopted ticket is updated in place, not duplicated")
    eq(len(board.t), 2, "only the subtask is new")


# --------------------------------------------------------------- clickup's PUT

def _clickup(handler):
    """A ClickUp adapter whose HTTP is `handler(method, url, body) -> dict`."""
    tk = trackers.for_project({"tracker": "clickup", "board_id": "1"}, "tok")
    seen = []

    def fake(url, headers, data=None, method=None, timeout=30):
        body = json.loads(data.decode()) if data else None
        seen.append((method or ("POST" if data is not None else "GET"), url, body))
        return handler(method or ("POST" if data is not None else "GET"), url, body)

    import trackers.clickup as cu
    real = cu.http_json
    cu.http_json = fake
    return tk, seen, (lambda: setattr(cu, "http_json", real))


def clickup_sends_the_name_field_not_title():
    """ClickUp's task field is `name`; a body that said `title` got a 200 and changed nothing."""
    state = {"name": "old"}

    def h(method, url, body):
        if method == "PUT":
            state.update(body or {})
            return {}
        return {"id": "abc", "name": state["name"], "status": {"status": "to do"}}

    tk, seen, restore = _clickup(h)
    try:
        tk.update_task("abc", title="new name")
    finally:
        restore()
    puts = [b for m, _u, b in seen if m == "PUT"]
    eq(puts, [{"name": "new name"}],
       "the rename must go out as `name` - `title` is a key ClickUp ignores, so the ticket "
       "kept its old name while the push reported success")


def clickup_moves_a_task_under_a_parent():
    """`parent` used to be filtered out of update_task entirely."""
    state = {"parent": "old-parent"}

    def h(method, url, body):
        if method == "PUT":
            state.update(body or {})
            return {}
        return {"id": "abc", "name": "t", "parent": state["parent"], "status": {"status": "to do"}}

    tk, seen, restore = _clickup(h)
    try:
        out = tk.update_task("abc", parent="new-parent")
    finally:
        restore()
    eq(state["parent"], "new-parent", "the parent must actually be sent to ClickUp")
    eq(out.get("parent"), "new-parent", "the caller must be told which parent it now has")


def clickup_refuses_to_report_a_move_that_did_not_happen():
    """ClickUp answers 200 whether or not it applied `parent`. Read it back."""
    def h(method, url, body):
        if method == "PUT":
            return {}                                    # accepted...
        return {"id": "abc", "name": "t", "parent": None, "status": {"status": "to do"}}  # ...and ignored

    tk, seen, restore = _clickup(h)
    try:
        e = raises(RuntimeError, lambda: tk.update_task("abc", parent="p1"),
                   "a parent ClickUp silently dropped must raise, not return ok")
        contains(str(e), "still has parent",
                 "the error has to say what the board actually reports, so the reader knows "
                 "the move did not happen")
    finally:
        restore()


def clickup_will_not_pretend_to_un_parent():
    tk, seen, restore = _clickup(lambda *a: {})
    try:
        raises(ValueError, lambda: tk.update_task("abc", parent=""),
               "ClickUp cannot turn a subtask back into a task; accepting an empty parent "
               "would look like it had")
        eq(seen, [], "and nothing may be sent for it")
    finally:
        restore()


def the_mcp_tool_takes_a_parent():
    """The schema is the only thing an agent can see, so the parameter has to be in it."""
    mcp = harness.load("tracker_mcp_ids", os.path.join(harness.TOOLS, "tracker_mcp.py"))
    tool = next(t for t in mcp.TrackerMCP.TOOLS if t["name"] == "tracker_update_task")
    props = tool["inputSchema"]["properties"]
    if "parent" not in props:
        raise AssertionError("tracker_update_task must declare a `parent` parameter, or no agent "
                             "can re-link a subtask no matter what the adapter supports")
    eq(props["parent"]["type"], "string", "parent is a ticket id")
    eq(tool["inputSchema"]["required"], ["task_id"], "parent stays optional")


def the_mcp_tool_routes_parent_to_the_adapter():
    calls = []

    class Fake:
        def update_task(self, tid, **f):
            calls.append(("update", tid, f)); return {}

        def set_status(self, tid, s):
            calls.append(("status", tid, s))

    mcp = harness.load("tracker_mcp_ids2", os.path.join(harness.TOOLS, "tracker_mcp.py"))
    srv = mcp.TrackerMCP.__new__(mcp.TrackerMCP)
    srv.tk, srv.error, srv.kind = Fake(), None, "clickup"
    out = srv.update_task("abc", parent="p1", status="qa")
    eq(calls, [("update", "abc", {"parent": "p1"}), ("status", "abc", "qa")],
       "parent goes through update_task, status through set_status, in that order")
    eq(out, {"id": "abc", "ok": True, "parent": "p1", "status": "qa"},
       "the result must name both changes")
    eq(srv.update_task("abc").get("error") is not None, True,
       "an update with neither field is still a no-op with a reason")


CASES = [
    ("rename updates, never duplicates", a_renamed_ticket_is_updated_not_duplicated),
    ("marker follows the rename", the_marker_follows_the_rename),
    ("half-finished push is adoptable", a_half_finished_push_still_stamps_what_it_made),
    ("dangling id stops the push", an_id_the_board_does_not_have_stops_the_push),
    ("one spec ticket per board ticket", two_tickets_may_not_claim_one_id),
    ("placeholder id refused", a_placeholder_id_is_not_an_id),
    ("id lands in the right header", the_id_lands_in_the_right_header),
    ("write-back refuses a moved spec", the_write_back_refuses_a_spec_that_moved_under_it),
    ("dry run never edits the spec", a_dry_run_never_touches_the_spec),
    ("existing_id still adopts", existing_id_is_still_how_a_ticket_is_adopted),
    ("--prune really cancels", prune_really_cancels_the_ticket),
    ("clickup renames via `name`", clickup_sends_the_name_field_not_title),
    ("clickup moves a parent", clickup_moves_a_task_under_a_parent),
    ("clickup proves the move", clickup_refuses_to_report_a_move_that_did_not_happen),
    ("clickup will not un-parent", clickup_will_not_pretend_to_un_parent),
    ("mcp schema takes parent", the_mcp_tool_takes_a_parent),
    ("mcp routes parent", the_mcp_tool_routes_parent_to_the_adapter),
]
