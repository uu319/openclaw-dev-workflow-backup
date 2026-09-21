#!/usr/bin/env python3
"""ClickUp. Board = a list id (digits). Auth = the raw token, not Bearer."""
import json
import os
import re

from . import Tracker, http_json

# Overridable so tests can point at a local mock; unset, this is the real API.
API = os.environ.get("CLICKUP_API_BASE", "https://api.clickup.com/api/v2")


class ClickUp(Tracker):
    kind = "clickup"
    marker_suffix = ".clickup.json"      # pre-existing markers keep their name

    def _h(self):
        return {"Authorization": self.token, "Content-Type": "application/json"}

    def _get(self, path):
        return http_json(API + path, self._h())

    @staticmethod
    def _task(t):
        return {
            "id": t["id"],
            "title": t.get("name"),
            "status": ((t.get("status") or {}).get("status") or ""),
            "url": t.get("url"),
            "assignees": [a.get("username") or a.get("email") for a in t.get("assignees", [])],
            "parent": t.get("parent"),
            "closed": bool((t.get("status") or {}).get("type") == "closed"),
            "updated": t.get("date_updated"),
            "description": t.get("description") or "",
        }

    def board_info(self):
        lst = self._get(f"/list/{self.board_id}")
        where = (f"folder '{(lst.get('folder') or {}).get('name')}'"
                 f" / space '{(lst.get('space') or {}).get('name')}'")
        return lst.get("name"), [s["status"] for s in lst.get("statuses", [])], where

    def tasks(self):
        out, page = {}, 0
        while True:
            d = self._get(f"/list/{self.board_id}/task"
                          f"?include_closed=true&subtasks=true&page={page}")
            for t in d.get("tasks", []):
                out[t["id"]] = self._task(t)
            if d.get("last_page", True) or not d.get("tasks"):
                return out
            page += 1

    def get_task(self, tid):
        return self._task(self._get(f"/task/{tid}"))

    def attachments(self, tid):
        """[{title, url}] already on the task - so a re-push does not re-upload."""
        return [{"title": a.get("title"), "url": a.get("url")}
                for a in (self._get(f"/task/{tid}").get("attachments") or [])]

    def comments(self, tid, limit=3):
        cs = self._get(f"/task/{tid}/comment").get("comments", [])
        return [{"by": (c.get("user") or {}).get("username"),
                 "text": (c.get("comment_text") or "")[:800]} for c in cs[:limit]]

    def task_url(self, tid):
        return f"https://app.clickup.com/t/{tid}"

    def links_in_text(self, text):
        return re.findall(r"app\.clickup\.com/t/(?:\d+/)?([a-z0-9]+)", text or "")

    def set_status(self, tid, status):
        http_json(f"{API}/task/{tid}", self._h(),
                  data=json.dumps({"status": status}).encode(), method="PUT")

    def update_task(self, tid, **fields):
        body = {k: v for k, v in fields.items() if k != "parent" and v is not None}
        if not body:
            return {}
        return http_json(f"{API}/task/{tid}", self._h(),
                         data=json.dumps(body).encode(), method="PUT")

    def link_tasks(self, tid, other):
        http_json(f"{API}/task/{tid}/link/{other}", self._h(), data=b"{}")

    def attach(self, tid, path, filename):
        import mimetypes
        import urllib.request
        import uuid
        boundary = uuid.uuid4().hex
        ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            content = f.read()
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"attachment\"; "
                f"filename=\"{filename}\"\r\nContent-Type: {ctype}\r\n\r\n").encode() + content + \
               f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(
            f"{API}/task/{tid}/attachment", data=body, method="POST",
            headers={"Authorization": self.token,
                     "Content-Type": f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode() or "{}")

    def create_task(self, title, description="", status=None, parent=None, **kw):
        body = {"name": title, "description": description}
        if status:
            body["status"] = status
        if parent:
            body["parent"] = parent
        for k in ("tags", "priority", "time_estimate", "assignees"):
            if kw.get(k) is not None:
                body[k] = kw[k]
        return self._task(http_json(f"{API}/list/{self.board_id}/task", self._h(),
                                    data=json.dumps(body).encode()))
