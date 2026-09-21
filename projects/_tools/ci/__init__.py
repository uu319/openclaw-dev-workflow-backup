#!/usr/bin/env python3
"""One CI interface, one module per provider.

The delivery watcher asks "which commits on this branch are green?" and must get
the same answer whether the project builds on Cloud Build or GitHub Actions.

`for_project(fields, host)` returns the adapter named by the Flow **Deploy
signal**. `host` is the caller (delivery_watch.Ctx), which supplies the
credential-scoped runners - `host.gh(*args)` and `host.gcloud(*args)` - so no CI
adapter ever holds a token or decides which project it is talking to.

A run is normalised to:

    {commit, check, status: ok|failed|running, at: iso8601, id, url}

`check` is the name the project lists in **Deploy checks** (a Cloud Build trigger
name, or a workflow name for Actions). The watcher requires every listed check to
be green before it calls a commit deployed.

Standard library only.
"""

# Provider status vocabularies are normalised here so the watcher never sees them.
OK, FAILED, RUNNING = "ok", "failed", "running"


class CI:
    kind = "none"

    def __init__(self, fields, host):
        self.f = fields
        self.host = host

    def runs(self, branch, limit=60, since=None, page_size=None):
        """-> [normalised run] for the given branch, newest first-ish.

        `since` (ISO8601) lets a provider page far enough back to cover the
        watch window instead of guessing with a fixed count.
        """
        return []


class NoCI(CI):
    """Deploy signal `none`: the merge is the signal, so there is nothing to read."""
    kind = "none"


def for_project(fields, host):
    signal = ((fields or {}).get("flow") or {}).get("deploy_signal", "none")
    if signal == "none":
        return NoCI(fields, host)
    from . import cloud_build, github_actions  # noqa: F401
    impl = {"cloud-build": cloud_build.CloudBuild,
            "github-actions": github_actions.GitHubActions}.get(signal)
    if impl is None:
        raise RuntimeError(f"unknown deploy signal '{signal}'")
    return impl(fields, host)
