#!/usr/bin/env python3
"""Tier 1 - `gh pr create` is verified against the remote, not against $PWD.

The bug these cases pin: git_env's PR guard fetched and resolved `origin/<head>`
in `os.getcwd()`. A correct `gh pr create` run from anywhere but the worktree
holding the branch therefore searched an unrelated directory and died with
"refused: origin/<branch> does not exist. Push the reviewed branch first." -
while the branch was pushed and named explicitly with --head. VanDev met this
often enough to propose a skill documenting the workaround (2026-09-22); the
guard was fixed instead, and these cases keep it fixed.

The branch is checked against the REMOTE, so any checkout of the project's repo
can answer. The guard now uses the project's Code (CWD), and only falls back to
$PWD when that is not a checkout. Offline: "origin" is a local bare repo.
"""
import contextlib
import io
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness  # noqa: E402
from harness import contains, raises  # noqa: E402

GIT_ENV = os.path.join(harness.TOOLS, "git_env.py")
BRANCH = "fix/pr-guard"


def git(*args):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def sandbox(pushed=True):
    """A project whose Code (CWD) is a checkout of a local bare 'origin'."""
    root, _ctx, _art = harness.project_sandbox(slug="git-env")
    code = os.path.join(root, "code")
    origin = os.path.join(root, "origin.git")
    git("init", "-q", "--bare", "-b", "main", origin)
    git("-C", code, "remote", "add", "origin", origin)
    git("-C", code, "push", "-q", "origin", "main")
    git("-C", code, "checkout", "-q", "-b", BRANCH)
    git("-C", code, "commit", "-q", "--allow-empty", "-m", "work")
    if pushed:
        git("-C", code, "push", "-q", "origin", BRANCH)
    git("-C", code, "checkout", "-q", "main")
    os.environ["OPENCLAW_WORKSPACE"] = root
    ge = harness.load("git_env_case", GIT_ENV)
    _ctx_path, fields = ge.load_fields("git-env")
    return ge, fields, root, code


class Refused(Exception):
    """A guard refusal, carrying what git_env printed before it exited."""


def pr_create(ge, fields, *extra):
    """Run the guard for `gh pr create` -> its stderr, or Refused(stderr)."""
    base = (fields.get("flow") or {}).get("pr_base") or fields.get("default_branch")
    argv = ["gh", "pr", "create", "--base", base, *extra, "--title", "t", "--body", "b"]
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            ge.guard(argv, fields, dict(os.environ))
    except SystemExit as exit_:
        raise Refused(err.getvalue()) from exit_
    return err.getvalue()


# ------------------------------------------------------------------ the cases

def a_pushed_branch_passes_from_outside_the_worktree():
    since = harness.mark()
    ge, fields, root, _code = sandbox()
    here = os.getcwd()
    try:
        os.chdir(root)                       # not a checkout of anything
        out = pr_create(ge, fields, "--head", BRANCH)
        contains(out, "PR creation allowed", "a pushed branch must pass from any directory")
        contains(out, BRANCH, "the allowed line names the branch")
    finally:
        os.chdir(here)
        harness.drop(since)


def it_still_passes_from_inside_the_checkout():
    since = harness.mark()
    ge, fields, _root, code = sandbox()
    here = os.getcwd()
    try:
        os.chdir(code)
        contains(pr_create(ge, fields, "--head", BRANCH), "PR creation allowed",
                 "the ordinary in-checkout path must keep working")
    finally:
        os.chdir(here)
        harness.drop(since)


def an_unpushed_branch_is_still_refused():
    since = harness.mark()
    ge, fields, root, _code = sandbox(pushed=False)
    here = os.getcwd()
    try:
        os.chdir(root)
        refused = raises(Refused, lambda: pr_create(ge, fields, "--head", BRANCH),
                         "a branch that is not on the remote must still be refused")
        contains(str(refused), "does not exist",
                 "the refusal still says the branch is not on the remote")
    finally:
        os.chdir(here)
        harness.drop(since)


def the_refusal_names_the_checkout_it_searched():
    since = harness.mark()
    ge, fields, root, code = sandbox(pushed=False)
    here = os.getcwd()
    try:
        os.chdir(root)
        refused = raises(Refused, lambda: pr_create(ge, fields, "--head", BRANCH), "refused")
        contains(str(refused), os.path.realpath(code),
                 "a refusal must name where it looked, or the next agent cd's at random")
    finally:
        os.chdir(here)
        harness.drop(since)


def no_head_outside_a_branch_says_so():
    since = harness.mark()
    ge, fields, root, _code = sandbox()
    here = os.getcwd()
    try:
        os.chdir(root)                       # no git branch to infer
        refused = raises(Refused, lambda: pr_create(ge, fields),
                         "a missing --head outside a checkout must be refused")
        contains(str(refused), "no --head given",
                 "the refusal must name the real problem, not the branch it could not find")
    finally:
        os.chdir(here)
        harness.drop(since)


CASES = [
    ("pushed branch passes from anywhere", a_pushed_branch_passes_from_outside_the_worktree),
    ("in-checkout path still works", it_still_passes_from_inside_the_checkout),
    ("unpushed branch still refused", an_unpushed_branch_is_still_refused),
    ("refusal names the checkout", the_refusal_names_the_checkout_it_searched),
    ("missing --head says so", no_head_outside_a_branch_says_so),
]
