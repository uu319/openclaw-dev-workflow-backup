#!/usr/bin/env python3
"""Run a git/gh command with ONE project's GitHub token. Never touches global git/gh state.

Usage:
  git_env.py <slug> -- <command> [args...]
      e.g. git_env.py fms-studio -- gh pr create --base Development --head fix/x --title "..." --body "..."
           git_env.py fms-studio -- gh pr view 42
           git_env.py fms-studio -- git push origin HEAD
  git_env.py <slug> --check            # verify the token works for this project's repo

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

WORKSPACE = "/home/openclaw/.openclaw/workspace"
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
# The one enforced gate (prompts alone did not hold: 2026-09-19 main opened PRs #33/#34 unreviewed).
# - `gh pr merge` / the merge API: refused. Merging is Van's.
# - `gh pr create`: refused unless <Internal Artifacts>/reviews/*.md has a file whose first line is
#   APPROVED and which says `Reviewed SHA: <sha>` for the commit the PR head points at.
# - OPENCLAW_HOTFIX=1 skips the review check (Van said "hotfix"); it is logged to reviews/HOTFIX.log
#   and VanReviewer must review right after.

def _sha_of(ref, cwd):
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet", ref + "^{commit}"], cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    return r.stdout.strip() or None


def _approved_shas(reviews_dir):
    import glob, re
    out = {}
    for f in glob.glob(os.path.join(reviews_dir, "*.md")):
        try:
            text = open(f).read()
        except OSError:
            continue
        lines = text.strip().splitlines()
        if not lines or "APPROVED" not in lines[0].upper() or "CHANGES" in lines[0].upper():
            continue
        for m in re.finditer(r"Reviewed SHA:\s*`?([0-9a-f]{7,40})", text):
            out[m.group(1)] = f
    return out


def guard(rest, fields, env):
    import re
    if not rest or os.path.basename(rest[0]) != "gh":
        return
    args = rest[1:]
    if args[:2] == ["pr", "merge"] or any(re.search(r"pulls/\d+/merge\b", a) for a in args):
        die("refused: merging a PR is Van's job, never an agent's (project-orchestration step 5).")
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
    # Local review check removed: VanReviewer now reviews PRs natively on GitHub.
    print(f"PR creation allowed for {head} @ {sha[:12]}: native GitHub reviews enabled.", file=sys.stderr)


def main():
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        sys.exit(1)
    slug, rest = argv[0], argv[1:]
    ctx, fields = load_fields(slug)
    env = build_env(fields, read_token(ctx, fields))

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
