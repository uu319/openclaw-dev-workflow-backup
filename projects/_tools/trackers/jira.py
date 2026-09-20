#!/usr/bin/env python3
"""Jira Cloud. Board = a project key (BILL). Auth = Basic `email:api_token`.

The vault entry holds both halves separated by a colon, because Basic auth needs
the account email as well as the token. A status move is a transition, so the
name in the status map is resolved against the issue's available transitions.
"""
import base64
import json
import re

from . import Tracker, http_json

CLOSED = {"done", "closed", "resolved", "cancelled", "canceled", "won't do", "wont do"}


class Jira(Tracker):
    kind = "jira"

    def __init__(self, fields, token=None):
        super().__init__(fields, token)
        self.base = (fields.get("tracker_base_url") or "").rstrip("/")

    def _h(self):
        if not self.token or ":" not in self.token:
            raise RuntimeError("the Jira vault entry must hold `email:api_token` (Basic auth needs both)")
        auth = base64.b64encode(self.token.encode()).decode()
        return {"Authorization": f"Basic {auth}", "Accept": "application/json",
                "Content-Type": "application/json"}

    def _task(self, it):
        f = it.get("fields") or {}
        st = ((f.get("status") or {}).get("name") or "")
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
            "closed": st.lower() in CLOSED,
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
        out, start = {}, 0
        while True:
            q = (f"{self.base}/rest/api/3/search?jql=project%3D{self.board_id}"
                 f"&maxResults=100&startAt={start}"
                 f"&fields=summary,status,assignee,parent,updated,description")
            d = http_json(q, self._h())
            for it in d.get("issues", []):
                out[it["key"]] = self._task(it)
            start += len(d.get("issues", []))
            if start >= d.get("total", 0) or not d.get("issues"):
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

    def create_task(self, title, description="", status=None, parent=None, **kw):
        f = {"project": {"key": self.board_id}, "summary": title,
             "issuetype": {"name": kw.get("issue_type") or ("Sub-task" if parent else "Task")},
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
