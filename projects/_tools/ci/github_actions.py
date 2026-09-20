#!/usr/bin/env python3
"""GitHub Actions. Runs are read through git_env.py, so the project's own
repo-scoped PAT is used and `gh` never needs a login.

A workflow run carries `status` (queued | in_progress | completed) and, once
completed, `conclusion`. Both matter: a completed run with a null conclusion does
not exist, but an in-progress run has no conclusion yet, so `status` is checked
first. `skipped` and `neutral` are treated as green because a path-filtered
workflow legitimately did not need to run; `cancelled` is treated as failed,
because a cancelled deploy did not deploy and should be visible rather than
silently counted as success.
"""
from . import CI, OK, FAILED, RUNNING

GREEN = {"success", "skipped", "neutral"}
RED = {"failure", "timed_out", "startup_failure", "action_required", "cancelled", "stale"}


class GitHubActions(CI):
    kind = "github-actions"

    def runs(self, branch, limit=60):
        repo = self.f.get("github_repo")
        if not repo:
            return []
        d = self.host.gh("api", "-X", "GET", f"repos/{repo}/actions/runs",
                         "-f", f"branch={branch}", "-f", f"per_page={min(limit, 100)}") or {}
        out = []
        for r in d.get("workflow_runs", []):
            commit = r.get("head_sha")
            if not commit:
                continue
            if r.get("status") != "completed":
                st = RUNNING
            else:
                concl = (r.get("conclusion") or "").lower()
                st = OK if concl in GREEN else (FAILED if concl in RED else FAILED)
            out.append({
                "commit": commit,
                "check": r.get("name") or (r.get("path") or "").rsplit("/", 1)[-1] or "?",
                "status": st,
                "at": r.get("created_at") or "",
                "id": str(r.get("id") or ""),
                "url": r.get("html_url") or "",
                "raw_status": r.get("conclusion") or r.get("status"),
            })
        return out
