#!/usr/bin/env python3
"""Jira Cloud. Board = a project key (BILL). Auth = Basic `email:api_token`.

The vault entry holds both halves separated by a colon, because Basic auth needs
the account email as well as the token. A status move is a transition, so the
name in the status map is resolved against the issue's available transitions.
"""
import base64
import json
import re
import urllib.parse

from . import Tracker, http_json

CLOSED = {"done", "closed", "resolved", "cancelled", "canceled", "won't do", "wont do"}


class Jira(Tracker):
    kind = "jira"

    def __init__(self, fields, token=None):
        super().__init__(fields, token)
        self.base = (fields.get("tracker_base_url") or "").rstrip("/")
        self._types = None

    def _h(self):
        if not self.token or ":" not in self.token:
            raise RuntimeError("the Jira vault entry must hold `email:api_token` (Basic auth needs both)")
        auth = base64.b64encode(self.token.encode()).decode()
        return {"Authorization": f"Basic {auth}", "Accept": "application/json",
                "Content-Type": "application/json"}

    def _task(self, it):
        f = it.get("fields") or {}
        status = f.get("status") or {}
        st = status.get("name") or ""
        # Jira marks terminal statuses with statusCategory.key == "done", whatever
        # the status is called. The English word list below is only a fallback for
        # a response that did not carry the category.
        cat = (status.get("statusCategory") or {}).get("key")
        parent = (f.get("parent") or {}).get("key")
        assignee = f.get("assignee") or {}
        desc = f.get("description")
        if isinstance(desc, dict):        # Atlassian Document Format
            desc = _adf_text(desc)
        return {
            "id": it.get("key"),
            "title": f.get("summary"),
            "status": st,
            "url": f"{self.base}/browse/{it.get('key')}",
            "assignees": [x for x in [assignee.get("emailAddress") or assignee.get("displayName")] if x],
            "parent": parent,
            "closed": (cat == "done") if cat else (st.lower() in CLOSED),
            "updated": f.get("updated"),
            "description": desc or "",
        }

    def board_info(self):
        proj = http_json(f"{self.base}/rest/api/3/project/{self.board_id}", self._h())
        types = http_json(f"{self.base}/rest/api/3/project/{self.board_id}/statuses", self._h())
        names = []
        for it in types:
            for st in it.get("statuses", []):
                if st["name"] not in names:
                    names.append(st["name"])
        return proj.get("name"), names, f"Jira site {self.base}"

    def tasks(self):
        """Every issue on the project, paged.

        `/rest/api/3/search` was REMOVED by Jira Cloud (HTTP 410, CHANGE-2046).
        Its replacement `/search/jql` is cursor-paged and returns no `total`, so
        the old `start >= total` loop would have exited on the first pass and
        reported the first page as the whole board. `isLast` / `nextPageToken`
        are the contract now - confirmed against a live site 2026-09-21.

        `ORDER BY created ASC` is required: cursor paging over an unsorted query
        can repeat or skip rows between pages.
        """
        out, cursor = {}, None
        while True:
            params = {
                "jql": f"project = {self.board_id} ORDER BY created ASC",
                "maxResults": 100,
                "fields": "summary,status,assignee,parent,updated,description",
            }
            if cursor:
                params["nextPageToken"] = cursor
            d = http_json(f"{self.base}/rest/api/3/search/jql?{urllib.parse.urlencode(params)}",
                          self._h())
            for it in d.get("issues", []):
                out[it["key"]] = self._task(it)
            cursor = d.get("nextPageToken")
            if d.get("isLast") or not cursor:
                return out

    def get_task(self, tid):
        return self._task(http_json(
            f"{self.base}/rest/api/3/issue/{tid}"
            f"?fields=summary,status,assignee,parent,updated,description", self._h()))

    def comments(self, tid, limit=3):
        d = http_json(f"{self.base}/rest/api/3/issue/{tid}/comment?orderBy=-created&maxResults={limit}",
                      self._h())
        out = []
        for c in d.get("comments", [])[:limit]:
            body = c.get("body")
            out.append({"by": (c.get("author") or {}).get("displayName"),
                        "text": (_adf_text(body) if isinstance(body, dict) else str(body or ""))[:800]})
        return out

    def task_url(self, tid):
        return f"{self.base}/browse/{tid}"

    def links_in_text(self, text):
        """Both a browse URL and a bare KEY-123 count as a reference."""
        text = text or ""
        ids = re.findall(r"/browse/([A-Z][A-Z0-9_]+-\d+)", text)
        ids += re.findall(rf"\b({re.escape(self.board_id)}-\d+)\b", text) if self.board_id else []
        seen, out = set(), []
        for i in ids:
            if i not in seen:
                seen.add(i); out.append(i)
        return out

    def set_status(self, tid, status):
        """Jira moves by transition id, so find the transition that lands on `status`."""
        tr = http_json(f"{self.base}/rest/api/3/issue/{tid}/transitions", self._h())
        for t in tr.get("transitions", []):
            if (t.get("to") or {}).get("name", "").lower() == status.lower():
                http_json(f"{self.base}/rest/api/3/issue/{tid}/transitions", self._h(),
                          data=json.dumps({"transition": {"id": t["id"]}}).encode())
                return
        avail = [(t.get("to") or {}).get("name") for t in tr.get("transitions", [])]
        raise RuntimeError(f"{tid}: no transition to '{status}'; available from here: {avail}")

    def issue_type(self, subtask=False):
        """The project's own name for a (sub)task type.

        Hardcoding "Sub-task" 400s on a team-managed project, which calls it
        "Subtask", and sites rename these freely. Ask the project instead.
        """
        if self._types is None:
            d = http_json(f"{self.base}/rest/api/3/project/{self.board_id}", self._h())
            self._types = d.get("issueTypes") or []
        names = [t["name"] for t in self._types if bool(t.get("subtask")) == subtask]
        if not names:
            return "Subtask" if subtask else "Task"
        for preferred in (("Subtask", "Sub-task") if subtask else ("Task", "Story")):
            if preferred in names:
                return preferred
        return names[0]

    def create_task(self, title, description="", status=None, parent=None, **kw):
        f = {"project": {"key": self.board_id}, "summary": title,
             "issuetype": {"name": kw.get("issue_type") or self.issue_type(subtask=bool(parent))},
             "description": {"type": "doc", "version": 1, "content": [
                 {"type": "paragraph", "content": [{"type": "text", "text": description or ""}]}]}}
        if parent:
            f["parent"] = {"key": parent}
        it = http_json(f"{self.base}/rest/api/3/issue", self._h(),
                       data=json.dumps({"fields": f}).encode())
        # the create response is minimal; read it back so the caller gets a full task
        return self._task(http_json(
            f"{self.base}/rest/api/3/issue/{it['key']}"
            f"?fields=summary,status,assignee,parent,updated,description", self._h()))


def _adf_text(node):
    """Flatten Atlassian Document Format to plain text."""
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text", "")
    return "".join(_adf_text(c) for c in node.get("content", []) or [])
