#!/usr/bin/env python3
"""One tracker interface, one module per provider.

Every tool that touches a ticket goes through `for_project(fields, token)`, which
returns the adapter named by the context file's `**Tracker:**` line. Nothing
outside this package knows which tracker a project uses, and `none` is a real
answer: `NoTracker` satisfies the whole interface by doing nothing.

A task is normalised to a plain dict so callers never see a provider's payload:

    {id, title, status, url, assignees: [str], parent: id|None,
     closed: bool, updated: iso8601|None, description: str}

`status` is the board's own name. Callers translate through the Flow status map
(canonical keys: todo doing staged rejected done cancelled hold) and never
hardcode a board's vocabulary.

Standard library only.
"""
import json
import re
import urllib.error
import urllib.request

TIMEOUT = 30


def http_json(url, headers, data=None, method=None, timeout=TIMEOUT):
    """GET, or POST/PUT when `data` is given. Raises urllib HTTPError as-is."""
    req = urllib.request.Request(
        url, headers=headers, data=data,
        method=method or ("POST" if data is not None else "GET"))
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read().decode()
    return json.loads(body) if body.strip() else {}


class Tracker:
    """Base class. A provider overrides what it can actually do."""

    kind = "none"
    marker_suffix = ".tracker.json"

    def __init__(self, fields, token=None):
        self.f = fields
        self.token = token
        self.board_id = fields.get("board_id")

    # --- read ---------------------------------------------------------------
    def board_info(self):
        """-> (board name, [status names], where). Used by validate --live."""
        raise NotImplementedError

    def tasks(self):
        """-> {id: task dict} for the whole board, including closed ones."""
        return {}

    def get_task(self, tid):
        """-> one task dict, read live. Raises if the tracker cannot find it."""
        raise NotImplementedError

    def comments(self, tid, limit=3):
        """-> [{'by': str, 'text': str}], newest first."""
        return []

    def task_url(self, tid):
        raise NotImplementedError

    def links_in_text(self, text):
        """Ticket ids this text refers to - used to read a PR body."""
        return []

    # --- write --------------------------------------------------------------
    def set_status(self, tid, status):
        raise NotImplementedError(f"{self.kind} cannot set a status")

    def create_task(self, title, description="", status=None, parent=None, **kw):
        raise NotImplementedError(f"{self.kind} cannot create tasks")

    def update_task(self, tid, **fields):
        """Change title/description/tags/estimate. `parent` is never moved here."""
        raise NotImplementedError(f"{self.kind} cannot update tasks")

    # --- optional capabilities -------------------------------------------------
    # A provider that cannot do one of these raises Unsupported, and the caller
    # decides whether that is fatal. Silently doing nothing is not an option: a
    # spec whose screenshots never uploaded must say so.
    def link_tasks(self, tid, other):
        raise Unsupported(f"{self.kind} cannot link tickets to each other yet")

    def attach(self, tid, path, filename):
        raise Unsupported(f"{self.kind} cannot upload attachments yet")


class Unsupported(NotImplementedError):
    """This provider does not implement an optional capability."""


class NoTracker(Tracker):
    """A project with no ticket system. Every read is empty, every write refused."""

    kind = "none"

    def board_info(self):
        return None, [], "no tracker"

    def get_task(self, tid):
        raise RuntimeError("this project has no tracker (Tracker: none); there is no ticket to read")

    def task_url(self, tid):
        return ""

    def set_status(self, tid, status):
        raise RuntimeError("this project has no tracker (Tracker: none); there is no ticket to move")

    def create_task(self, *a, **kw):
        raise RuntimeError("this project has no tracker (Tracker: none); there is no board to create on")


def for_project(fields, token=None):
    """Return the adapter for this project's `**Tracker:**` line."""
    kind = (fields or {}).get("tracker", "none")
    if kind == "none":
        return NoTracker(fields, token)
    from . import clickup, jira, linear          # noqa: F401  (local, avoids import cost)
    impl = {"clickup": clickup.ClickUp, "jira": jira.Jira, "linear": linear.Linear}.get(kind)
    if impl is None:
        raise RuntimeError(f"unknown tracker '{kind}'; expected clickup, jira, linear or none")
    return impl(fields, token)
