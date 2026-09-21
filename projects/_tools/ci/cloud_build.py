#!/usr/bin/env python3
"""Google Cloud Build. Runs are read through gcloud_env.py, so the project's own
service account is used and there is no ambient gcloud default."""
from . import CI, OK, FAILED, RUNNING

DONE = {"SUCCESS"}
INFLIGHT = {"QUEUED", "WORKING", "PENDING", "STATUS_UNKNOWN"}


class CloudBuild(CI):
    kind = "cloud-build"

    def runs(self, branch, limit=60, since=None, page_size=None):
        # `since` is accepted for interface parity. gcloud has no cursor here, so
        # the ceiling is --limit; a window needing more than that is not covered.
        # Untested against a real overflow, unlike the Actions path - see 5.9.
        if not self.f.get("gcp_project_id"):
            return []
        builds = self.host.gcloud(
            "builds", "list", f"--limit={limit}", "--format=json",
            f"--filter=substitutions.BRANCH_NAME={branch}") or []
        out = []
        for b in builds:
            s = b.get("substitutions") or {}
            commit = s.get("COMMIT_SHA")
            if not commit:
                continue
            st = b.get("status")
            out.append({
                "commit": commit,
                "check": s.get("TRIGGER_NAME") or b.get("buildTriggerId") or "?",
                "status": RUNNING if st in INFLIGHT else (OK if st in DONE else FAILED),
                "at": b.get("createTime") or "",
                "id": b.get("id") or "",
                "url": b.get("logUrl") or "",
                "raw_status": st,
            })
        return out
