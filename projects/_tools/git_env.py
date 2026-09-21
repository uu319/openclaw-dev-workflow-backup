#!/usr/bin/env python3
"""Run a git/gh command with ONE project's GitHub token. Never touches global git/gh state.

Usage:
  git_env.py <slug> -- <command> [args...]
      e.g. git_env.py <slug> -- gh pr create --base <pr-base> --head fix/x --title "..." --body "..."
           git_env.py <slug> -- gh pr view 42
           git_env.py <slug> -- git push origin HEAD
  git_env.py <slug> --check            # verify the token works for this project's repo
  git_env.py <slug> --review-status <pr> [--dry]
                                       # VanReviewer, after saving its review file: sets the commit status
                                       # `openclaw/review` on the PR head (success = APPROVED, failure =
                                       # CHANGES REQUESTED) only if a review file names that exact head SHA

Sibling of gcloud_env.py and figma_mcp.py: same rule, same shape. The project's
PROJECT_CONTEXT.md is the single source of truth. This reads it, takes the vault entry named
under 'GitHub Token:' (a repo-scoped fine-grained PAT) and execs the command with it injected
into the CHILD ENVIRONMENT ONLY:

  GH_TOKEN / GITHUB_TOKEN  -> gh and the GitHub API
  GH_REPO=<owner/repo>     -> gh cannot infer the repo from an SSH host alias remote
                              (git@<alias>.github.com:...), so it is set explicitly
  GH_PROMPT_DISABLED=1, GIT_TERMINAL_PROMPT=0 -> fail instead of waiting for input
  one-shot credential.helper via GIT_CONFIG_COUNT -> HTTPS git remotes, if any

git push over the project's SSH alias keeps using its deploy key; the token is for gh/PRs.
Nothing is written to ~/.gitconfig, ~/.config/gh, ~/.bashrc or the repo config. `gh auth login`
is never run. If the project has no GitHub token this exits non-zero naming the field to fill.

Standard library only.
"""
import importlib.util
import os
import shutil
import subprocess
import sys

# The workspace root. `OPENCLAW_WORKSPACE` overrides it so the tools can be run
# against an isolated copy (tests, a dry run of a new project) without touching
# the live tree - which the heartbeat scans every 15 minutes and acts on.
WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", "/home/openclaw/.openclaw/workspace")
VALIDATOR = f"{WORKSPACE}/projects/_tools/validate_context.py"


def die(m):
    print(f"git_env: {m}", file=sys.stderr)
    sys.exit(1)


def load_fields(slug):
    ctx = f"{WORKSPACE}/projects/{slug}/PROJECT_CONTEXT.md"
    if not os.path.isfile(ctx):
        die(f"no PROJECT_CONTEXT.md for '{slug}' at {ctx}")
    spec = importlib.util.spec_from_file_location("vc", VALIDATOR)
    vc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vc)
    fields, errors = vc.parse(ctx)
    if errors:
        die(f"invalid {ctx}: " + "; ".join(errors))
    return ctx, fields


def read_token(ctx, fields):
    name = fields.get("git_secret")
    if not fields.get("github_repo") or not name:
        die(f"project has no GitHub API access configured: {ctx} needs '**GitHub Repo:** `owner/repo`' "
            f"and a 'GitHub Token:' SecretRef line. Refusing to fall back to any other credential.")
    openclaw = shutil.which("openclaw") or "/usr/bin/openclaw"
    r = subprocess.run([openclaw, "secrets", "store", "get", "--plain", name],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    tok = r.stdout.strip()
    if r.returncode != 0 or not tok:
        die(f"could not read vault entry {name} (exit {r.returncode}): {r.stderr.strip()[:300]}")
    return tok


def build_env(fields, tok):
    env = {k: v for k, v in os.environ.items()
           if k not in ("GITHUB_TOKEN", "GH_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN",
                        "GH_REPO", "GH_HOST") and not k.startswith("GIT_CONFIG_")}
    env.update({
        "GH_TOKEN": tok,
        "GITHUB_TOKEN": tok,
        "GH_REPO": fields["github_repo"],
        "GH_PROMPT_DISABLED": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "credential.https://github.com.helper",
        "GIT_CONFIG_VALUE_0": '!f() { echo "username=x-access-token"; echo "password=$GITHUB_TOKEN"; }; f',
    })
    return env


# ---------------------------------------------------------------- workflow guard
# Enforced here, not in prompts (2026-09-19: main opened PRs #33/#34 unreviewed; later the same day an
# agent deleted a prompt-only review rule). What this file enforces:
# - `gh pr merge` / the merge API: refused. Merging is Van's.
# - `gh pr create`: only into the Flow PR base, only for a branch that exists on origin.
# - Commit statuses: written only by `--review-status` (below), never by a raw `gh api .../statuses/...`.
# The review itself happens on the open PR (VanReviewer, GitHub-native). Its result is the commit status
# REVIEW_CONTEXT on the PR head SHA; a GitHub ruleset that requires that status is what blocks a merge of
# unreviewed or changed-after-review code. A new push = a new SHA without the status = review again.

REVIEW_CONTEXT = "openclaw/review"


def _sha_of(ref, cwd):
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref + "^{commit}"], cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return r.stdout.strip() or None


def review_for(reviews_dir, head_sha):
    """Newest review file in reviews_dir whose `Reviewed SHA:` is head_sha -> (verdict, path), else (None, None).
    verdict is 'APPROVED' or 'CHANGES REQUESTED' from line 1; any other line 1 is ignored."""
    import glob, re
    best = None
    for f in glob.glob(os.path.join(reviews_dir, "*.md")):
        try:
            text = open(f).read()
        except OSError:
            continue
        lines = text.strip().splitlines()
        if not lines:
            continue
        first = lines[0].strip().strip("*#` ").upper()
        if first.startswith("CHANGES REQUESTED"):
            verdict = "CHANGES REQUESTED"
        elif first.startswith("APPROVED"):
            verdict = "APPROVED"
        else:
            continue
        shas = re.findall(r"Reviewed SHA:\s*`?([0-9a-f]{7,40})", text)
        if not any(head_sha.startswith(s) for s in shas):
            continue
        mtime = os.path.getmtime(f)
        if best is None or mtime > best[0]:
            best = (mtime, verdict, f)
    return (best[1], best[2]) if best else (None, None)


def review_status(fields, env, pr, dry=False):
    """Mirror the saved review of the PR's CURRENT head commit into the commit status REVIEW_CONTEXT."""
    import json
    r = subprocess.run(["gh", "pr", "view", pr, "--json", "headRefOid,url,state"], env=env,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        die(f"could not read PR {pr}: {r.stderr.strip()[:300]}")
    info = json.loads(r.stdout)
    if info.get("state") != "OPEN":
        die(f"PR {info.get('url')} is {info.get('state')}; statuses are only set on open PRs.")
    head = info["headRefOid"]
    reviews = os.path.join(fields["artifacts_dir"], "reviews")
    verdict, path = review_for(reviews, head)
    if not verdict:
        die(f"refused: no review file in {reviews} says `Reviewed SHA: {head}` with APPROVED or CHANGES REQUESTED "
            f"on line 1. The PR head moved or the review was not saved: review this commit first.")
    state = "success" if verdict == "APPROVED" else "failure"
    desc = f"{verdict} by VanReviewer ({os.path.basename(path)})"[:140]
    call = ["gh", "api", "-X", "POST", f"repos/{fields['github_repo']}/statuses/{head}",
            "-f", f"state={state}", "-f", f"context={REVIEW_CONTEXT}",
            "-f", f"description={desc}", "-f", f"target_url={info['url']}"]
    if dry:
        print(f"DRY {REVIEW_CONTEXT}={state} on {head[:12]} ({info['url']}) from {path}")
        return
    r = subprocess.run(call, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        err = (r.stdout + r.stderr).strip()
        if "not accessible" in err or "403" in err:
            die(f"GitHub refused the status (403): the token {fields.get('git_secret')} lacks the fine-grained "
                f"permission 'Commit statuses: Read and write'. The review on GitHub still counts; tell the "
                f"orchestrator this line so Van can add the permission.")
        die(f"setting the status failed: {err[:300]}")
    print(f"OK {REVIEW_CONTEXT}={state} on {head[:12]} ({info['url']}) from {path}")


def guard(rest, fields, env):
    import re
    if not rest or os.path.basename(rest[0]) != "gh":
        return
    args = rest[1:]
    if args[:2] == ["pr", "merge"] or any(re.search(r"pulls/\d+/merge\b", a) for a in args):
        die("refused: merging a PR is Van's job, never an agent's (project-orchestration step 5).")
    if args[:1] == ["api"] and any(re.search(r"(^|/)statuses(/|$)", a) for a in args[1:]):
        die(f"refused: commit statuses are written only by `git_env.py <slug> --review-status <pr>`. "
            f"To read them: `git_env.py <slug> -- gh pr view <pr> --json statusCheckRollup`.")
    if args[:2] != ["pr", "create"]:
        return
    base = None
    for i, a in enumerate(args):
        if a in ("--base", "-B") and i + 1 < len(args):
            base = args[i + 1]
        elif a.startswith("--base="):
            base = a.split("=", 1)[1]
    want = (fields.get("flow") or {}).get("pr_base") or fields.get("default_branch")
    if want and base != want:
        die(f"refused: PRs go into the Flow PR base `{want}` (PROJECT_CONTEXT); pass --base {want}"
            + (f", not `{base}`." if base else "."))
    head = None
    for i, a in enumerate(args):
        if a in ("--head", "-H") and i + 1 < len(args):
            head = args[i + 1]
        elif a.startswith("--head="):
            head = a.split("=", 1)[1]
    cwd = os.getcwd()
    if head is None:
        r = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, text=True)
        head = r.stdout.strip()
    subprocess.run(["git", "fetch", "--quiet", "origin", head], cwd=cwd, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, env=env)
    sha = _sha_of(f"origin/{head}", cwd)
    if not sha:
        die(f"refused: origin/{head} does not exist. Push the reviewed branch first.")
    print(f"PR creation allowed for {head} @ {sha[:12]} into {want}. Review happens on the PR; "
          f"its result is the `{REVIEW_CONTEXT}` status.", file=sys.stderr)


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)
    slug, rest = argv[0], argv[1:]
    ctx, fields = load_fields(slug)
    env = build_env(fields, read_token(ctx, fields))

    if rest and rest[0] == "--review-status":
        if len(rest) < 2 or rest[1].startswith("-"):
            die("usage: git_env.py <slug> --review-status <pr number or URL> [--dry]")
        review_status(fields, env, rest[1], dry="--dry" in rest[2:])
        return
    if rest and rest[0] == "--check":
        rest = ["gh", "repo", "view", fields["github_repo"], "--json", "nameWithOwner,viewerPermission"]
    elif rest and rest[0] == "--":
        rest = rest[1:]
    if not rest:
        die("nothing to run: use 'git_env.py <slug> -- <command> [args...]' or '--check'")

    guard(rest, fields, env)
    exe = shutil.which(rest[0], path=env.get("PATH", os.defpath))
    if not exe:
        die(f"command not found: {rest[0]}")
    os.execve(exe, rest, env)


if __name__ == "__main__":
    main()
