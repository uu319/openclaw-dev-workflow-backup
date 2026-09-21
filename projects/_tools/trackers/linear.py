#!/usr/bin/env python3
"""Linear. Board = a team id (UUID) or team key (ENG). One GraphQL endpoint.

Linear calls a status a workflow state, and states belong to the team, so a move
resolves the state name against that team's states.
"""
import json
import mimetypes
import os
import urllib.request
import os
import re

from . import Tracker, http_json

# Overridable so tests can point at a local mock; unset, this is the real API.
API = os.environ.get("LINEAR_API_URL", "https://api.linear.app/graphql")
CLOSED_TYPES = {"completed", "canceled"}


class Linear(Tracker):
    kind = "linear"

    def __init__(self, fields, token=None):
        super().__init__(fields, token)
        self._team = None
        self._urlkey = None

    def _h(self):
        return {"Authorization": self.token, "Content-Type": "application/json"}

    def _q(self, query, **variables):
        res = http_json(API, self._h(),
                        data=json.dumps({"query": query, "variables": variables}).encode())
        if res.get("errors"):
            raise RuntimeError(f"Linear API: {res['errors'][0].get('message')}")
        return res.get("data") or {}

    def team(self):
        """Resolve the board id (UUID or key) to {id, key, name, states}."""
        if self._team is not None:
            return self._team
        bid = self.board_id or ""
        if re.fullmatch(r"[0-9a-fA-F-]{20,}", bid):
            d = self._q("query($id:String!){team(id:$id){id key name "
                        "states{nodes{id name type}}}}", id=bid)
            t = d.get("team")
        else:
            d = self._q("query($k:String!){teams(filter:{key:{eq:$k}},first:1){nodes{id key name "
                        "states{nodes{id name type}}}}}", k=bid)
            nodes = ((d.get("teams") or {}).get("nodes") or [])
            t = nodes[0] if nodes else None
        if not t:
            raise RuntimeError(f"no Linear team matches '{bid}'")
        self._team = t
        return t

    def _task(self, i):
        st = i.get("state") or {}
        return {
            "id": i.get("identifier"),
            "title": i.get("title"),
            "status": st.get("name") or "",
            "url": i.get("url"),
            "assignees": [x for x in [(i.get("assignee") or {}).get("email")
                                      or (i.get("assignee") or {}).get("name")] if x],
            "parent": (i.get("parent") or {}).get("identifier"),
            "closed": (st.get("type") or "") in CLOSED_TYPES,
            "updated": i.get("updatedAt"),
            "description": i.get("description") or "",
            "_uuid": i.get("id"),
        }

    def board_info(self):
        t = self.team()
        return t["name"], [s["name"] for s in (t.get("states") or {}).get("nodes", [])], "Linear"

    def tasks(self, page_size=100):
        """Every issue on the team, cursor-paged.

        `page_size` is injectable so a test can force real multi-page paging
        without creating 100 issues - the same reason it exists on the Jira
        adapter. Silent truncation at one page is the failure mode that made the
        old Jira `/search` endpoint dangerous.
        """
        t, out, after, page = self.team(), {}, None, (
            "query($id:String!,$after:String,$n:Int!){team(id:$id){issues(first:$n,after:$after,"
            "includeArchived:true){pageInfo{hasNextPage endCursor}"
            "nodes{id identifier title url updatedAt description "
            "state{name type} assignee{name email} parent{identifier}}}}}")
        while True:
            d = self._q(page, id=t["id"], after=after, n=page_size)
            iss = ((d.get("team") or {}).get("issues") or {})
            for i in iss.get("nodes", []):
                out[i["identifier"]] = self._task(i)
            info = iss.get("pageInfo") or {}
            if not info.get("hasNextPage"):
                return out
            after = info.get("endCursor")

    def get_task(self, tid):
        d = self._q("query($id:String!){issue(id:$id){id identifier title url updatedAt description "
                    "state{name type} assignee{name email} parent{identifier}}}", id=tid)
        i = d.get("issue")
        if not i:
            raise RuntimeError(f"Linear issue '{tid}' not found")
        return self._task(i)

    def comments(self, tid, limit=3):
        d = self._q("query($id:String!){issue(id:$id){comments(first:%d){nodes{body user{name}}}}}" % limit,
                    id=tid)
        nodes = (((d.get("issue") or {}).get("comments") or {}).get("nodes") or [])
        return [{"by": (c.get("user") or {}).get("name"), "text": (c.get("body") or "")[:800]}
                for c in nodes[:limit]]

    def task_url(self, tid):
        """The canonical issue URL, workspace slug included.

        This used to build `https://linear.app/issue/<id>`, without the
        workspace. Linear's own `url` field always carries the slug
        (`https://linear.app/<urlKey>/issue/<id>/<title-slug>`), and these links
        go into PR bodies and ticket comments where a human clicks them. The
        short form could not be verified: linear.app is a single-page app and
        returns HTTP 200 for every path, including issues that do not exist, so
        a status check proves nothing either way. Asking the API for the slug
        removes the guess.
        """
        if self._urlkey is None:
            try:
                self._urlkey = ((self._q("{organization{urlKey}}").get("organization") or {})
                                .get("urlKey") or "")
            except Exception:  # noqa: BLE001 - a link is not worth failing a status move over
                self._urlkey = ""
        return (f"https://linear.app/{self._urlkey}/issue/{tid}" if self._urlkey
                else f"https://linear.app/issue/{tid}")

    def links_in_text(self, text):
        text = text or ""
        key = (self.team().get("key") if self.board_id else None) or r"[A-Z][A-Z0-9]*"
        ids = re.findall(r"linear\.app/[^/\s]+/issue/([A-Z][A-Z0-9]*-\d+)", text)
        ids += re.findall(rf"\b({re.escape(key)}-\d+)\b", text)
        seen, out = set(), []
        for i in ids:
            if i not in seen:
                seen.add(i); out.append(i)
        return out

    def _state_id(self, name):
        for s in (self.team().get("states") or {}).get("nodes", []):
            if s["name"].lower() == (name or "").lower():
                return s["id"]
        avail = [s["name"] for s in (self.team().get("states") or {}).get("nodes", [])]
        raise RuntimeError(f"no Linear state named '{name}'; this team has: {avail}")

    def set_status(self, tid, status):
        uuid = self._q("query($id:String!){issue(id:$id){id}}", id=tid).get("issue", {}).get("id")
        if not uuid:
            raise RuntimeError(f"Linear issue '{tid}' not found")
        d = self._q("mutation($id:String!,$s:String!){issueUpdate(id:$id,input:{stateId:$s}){success}}",
                    id=uuid, s=self._state_id(status))
        # Linear answers 200 with success:false for a rejected write (permission,
        # workflow rule). Unchecked, a refused status move reported as done.
        if not ((d.get("issueUpdate") or {}).get("success")):
            raise RuntimeError(f"Linear refused the status move of {tid} to '{status}' (success: false)")

    # --- capabilities tracker_push needs -------------------------------------

    def _uuid(self, tid):
        u = (self._q("query($id:String!){issue(id:$id){id}}", id=tid).get("issue") or {}).get("id")
        if not u:
            raise RuntimeError(f"Linear issue '{tid}' not found")
        return u

    def _label_ids(self, names):
        """Label names -> ids, creating any the team does not have yet.

        Linear takes label IDs, not names, so a tag has to be resolved or made
        first. Lane tags (`FE`, `BE`) repeat across every spec, so this is a
        lookup far more often than a create.
        """
        t = self.team()
        have = {l["name"].lower(): l["id"] for l in
                ((self._q("query($id:String!){team(id:$id){labels(first:250){nodes{id name}}}}",
                          id=t["id"]).get("team") or {}).get("labels") or {}).get("nodes", [])}
        out = []
        for n in names or []:
            key = str(n).lower()
            if key not in have:
                d = self._q("mutation($i:IssueLabelCreateInput!){issueLabelCreate(input:$i){success issueLabel{id}}}",
                            i={"name": str(n), "teamId": t["id"]})
                res = d.get("issueLabelCreate") or {}
                if not res.get("success"):
                    continue                      # a label is not worth failing the push over
                have[key] = (res.get("issueLabel") or {})["id"]
            out.append(have[key])
        return out

    def update_task(self, tid, **fields):
        inp = {}
        if fields.get("title"):
            inp["title"] = fields["title"]
        if fields.get("description") is not None:
            inp["description"] = fields["description"]      # Linear takes markdown natively
        if fields.get("tags") is not None:
            inp["labelIds"] = self._label_ids(fields["tags"])
        if not inp:
            return {}
        d = self._q("mutation($id:String!,$i:IssueUpdateInput!){issueUpdate(id:$id,input:$i){success}}",
                    id=self._uuid(tid), i=inp)
        if not ((d.get("issueUpdate") or {}).get("success")):
            raise RuntimeError(f"Linear refused to update {tid} (success: false)")
        return {"id": tid, "ok": True}

    def link_tasks(self, tid, other, kind="blocks"):
        d = self._q("mutation($i:IssueRelationCreateInput!){issueRelationCreate(input:$i){success}}",
                    i={"issueId": self._uuid(tid), "relatedIssueId": self._uuid(other), "type": kind})
        if not ((d.get("issueRelationCreate") or {}).get("success")):
            raise RuntimeError(f"Linear refused to link {tid} -> {other}")
        return {"from": tid, "to": other, "type": kind}

    def attach(self, tid, path, filename):
        """Two steps: Linear signs an upload URL, the bytes go straight to storage,
        then the returned asset URL is attached to the issue."""
        size = os.path.getsize(path)
        ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        d = self._q("mutation($c:String!,$f:String!,$s:Int!){fileUpload(contentType:$c,filename:$f,size:$s)"
                    "{success uploadFile{uploadUrl assetUrl headers{key value}}}}",
                    c=ctype, f=filename, s=size)
        up = (d.get("fileUpload") or {})
        if not up.get("success") or not up.get("uploadFile"):
            raise RuntimeError(f"Linear refused an upload slot for {filename}")
        uf = up["uploadFile"]
        with open(path, "rb") as fh:
            blob = fh.read()
        headers = {h["key"]: h["value"] for h in (uf.get("headers") or [])}
        headers["Content-Type"] = ctype
        req = urllib.request.Request(uf["uploadUrl"], data=blob, headers=headers, method="PUT")
        with urllib.request.urlopen(req, timeout=120):
            pass
        asset = uf["assetUrl"]
        self._q("mutation($i:AttachmentCreateInput!){attachmentCreate(input:$i){success}}",
                i={"issueId": self._uuid(tid), "title": filename, "url": asset})
        return {"title": filename, "url": asset}

    def attachments(self, tid):
        d = self._q("query($id:String!){issue(id:$id){attachments(first:50){nodes{title url}}}}", id=tid)
        return [{"title": a.get("title"), "url": a.get("url")}
                for a in (((d.get("issue") or {}).get("attachments") or {}).get("nodes") or [])]

    def create_task(self, title, description="", status=None, parent=None, **kw):
        t = self.team()
        inp = {"teamId": t["id"], "title": title, "description": description or ""}
        if status:
            inp["stateId"] = self._state_id(status)
        if parent:
            puuid = self._q("query($id:String!){issue(id:$id){id}}", id=parent).get("issue", {}).get("id")
            if puuid:
                inp["parentId"] = puuid
        d = self._q("mutation($i:IssueCreateInput!){issueCreate(input:$i){success issue{id identifier title url "
                    "updatedAt description state{name type} assignee{name email} parent{identifier}}}}", i=inp)
        res = d.get("issueCreate") or {}
        if not res.get("success") or not res.get("issue"):
            raise RuntimeError(f"Linear refused to create '{title}' (success: {res.get('success')})")
        return self._task(res["issue"])
