#!/usr/bin/env python3
"""ClickUp. Board = a list id (digits). Auth = the raw token, not Bearer."""
import json
import os
import re

from . import PRIORITY_RANK, Tracker, http_json

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

    def _set_parent(self, tid, parent):
        """Move a task under another task, and prove it moved.

        ClickUp takes `parent` on the task PUT, but it answers 200 whether or not
        the move happened - and it only re-parents something that is ALREADY a
        subtask. So the parent is read back: a silent no-op raises here rather
        than being reported to the caller as a successful move.

        Un-parenting is deliberately not offered: ClickUp's API cannot turn a
        subtask back into a top-level task, and accepting `parent: null` would
        look like it had.
        """
        parent = str(parent or "").strip()
        if not parent:
            raise ValueError(f"no parent id given for {tid}; ClickUp cannot un-parent a "
                             f"subtask through the API (do it in the UI)")
        if parent == tid:
            raise ValueError(f"task {tid} cannot be its own parent")
        http_json(f"{API}/task/{tid}", self._h(),
                  data=json.dumps({"parent": parent}).encode(), method="PUT")
        now = (self.get_task(tid).get("parent") or "")
        if now != parent:
            raise RuntimeError(
                f"ClickUp accepted the request but {tid} still has parent "
                f"{now or 'none'}, not {parent}: ClickUp only moves a task that is already a "
                f"subtask. Convert it to a subtask in the UI, or re-create it with `parent`.")
        return {"id": tid, "parent": parent, "ok": True}

    def update_task(self, tid, **fields):
        """Change name/description/estimate, and/or move the task under another.

        `parent` is handled separately because it needs reading back; everything
        else is one PUT. The task name is `name` on ClickUp - a body that said
        `title` was accepted with a 200 and changed nothing, so a renamed ticket
        silently kept its old name on the board (2026-09-22).
        """
        parent = fields.pop("parent", None)
        if "title" in fields:
            fields["name"] = fields.pop("title")
        body = {k: v for k, v in fields.items() if v is not None}
        out = {}
        if body:
            out = http_json(f"{API}/task/{tid}", self._h(),
                            data=json.dumps(body).encode(), method="PUT")
        if parent is not None:
            out = {**(out or {}), **self._set_parent(tid, parent)}
        return out

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
        if kw.get("tags") is not None:
            body["tags"] = list(kw["tags"])
        if kw.get("estimate_hours"):
            body["time_estimate"] = int(float(kw["estimate_hours"]) * 3600 * 1000)
        if kw.get("priority"):
            body["priority"] = PRIORITY_RANK.get(str(kw["priority"]).lower(), 3)
        for k in ("time_estimate", "assignees"):            # still accepted raw
            if kw.get(k) is not None:
                body[k] = kw[k]
        return self._task(http_json(f"{API}/list/{self.board_id}/task", self._h(),
                                    data=json.dumps(body).encode()))
