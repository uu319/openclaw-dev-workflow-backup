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

# Never crawl a busy repo forever. 500 runs is far past any sane watch window
# and still one bounded number rather than "until GitHub runs out".
MAX_RUNS = 500

GREEN = {"success", "skipped", "neutral"}
RED = {"failure", "timed_out", "startup_failure", "action_required", "cancelled", "stale"}


class GitHubActions(CI):
    kind = "github-actions"

    def runs(self, branch, limit=60, since=None, page_size=None):
        """Runs on `branch`, newest first.

        With `since` (ISO8601) this PAGES until it has runs older than that time,
        because one page is not enough on a repo with steady CI traffic. It used
        to be a single request capped at 100: once more than that many runs piled
        up on the base branch, a merge commit's run fell off the end, the watcher
        saw a merge that had apparently never built, and it waited until
        NO_BUILD_AFTER_MIN before giving up. That is the 2026-09-19 stall reached
        by a different route. fms-studio had 19 runs from dependabot alone.

        Without `since` the behaviour is unchanged: one page of `limit`.
        """
        repo = self.f.get("github_repo")
        if not repo:
            return []
        per = min(page_size or (100 if since else limit), 100)
        out, page, fetched = [], 1, 0
        while True:
            d = self.host.gh("api", "-X", "GET", f"repos/{repo}/actions/runs",
                             "-f", f"branch={branch}", "-f", f"per_page={per}",
                             "-f", f"page={page}") or {}
            batch = d.get("workflow_runs", [])
            out.extend(self._one(r) for r in batch if r.get("head_sha"))
            fetched += len(batch)
            if not since or not batch or len(batch) < per or fetched >= MAX_RUNS:
                break
            oldest = batch[-1].get("created_at") or ""
            if oldest and oldest <= since:      # the window is covered
                break
            page += 1
        return out

    def _one(self, r):
        """One API run -> the normalised shape every CI adapter returns."""
        if r.get("status") != "completed":
            st = RUNNING
        else:
            concl = (r.get("conclusion") or "").lower()
            st = OK if concl in GREEN else (FAILED if concl in RED else FAILED)
        # The check key must be STABLE across runs, because a project lists the
        # checks it waits for by name in `Deploy checks`. `run.name` is NOT
        # stable: GitHub's `run-name:` makes it per-run, and dependabot's is
        # unique every time - 19 runs on fms-studio produced 19 distinct names
        # (verified 2026-09-21). An expected name would then never match, and
        # every commit would sit at `running` until NO_BUILD_AFTER_MIN: the
        # 12.5f stall, reproduced on another provider. `path` is the workflow
        # file, which is stable and is what a person would name anyway.
        path = (r.get("path") or "").rsplit("/", 1)[-1]
        return {
            "commit": r.get("head_sha"),
            "check": path or r.get("name") or "?",
            "display": r.get("name") or path,
            "status": st,
            "at": r.get("created_at") or "",
            "id": str(r.get("id") or ""),
            "url": r.get("html_url") or "",
            "raw_status": r.get("conclusion") or r.get("status"),
        }
