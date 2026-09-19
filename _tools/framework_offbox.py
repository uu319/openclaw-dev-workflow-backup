#!/usr/bin/env python3
"""Off-box copy of the framework git repos (architecture Decision I). Van runs it from a real terminal.

Usage:
  framework_offbox.py status                          # per repo: last off-box commit, commits since
  framework_offbox.py push <private repo url> [--dry] [--allow-rotated]
      e.g. framework_offbox.py push git@openclaw-backup.github.com:<owner>/openclaw-framework.git

What push does, per framework repo (the linter's framework_repos(): workspace, the four agent workspaces,
the shared skills):
  1. Scans the repo's FULL history for token-shaped strings (the linter's TOKEN_RX). Any hit stops the push
     and is listed masked (commit, file, first 6 chars, length). A credential that ever sat in history is
     only safe to push once it has been rotated: re-run with --allow-rotated after rotating every listed one.
  2. `git push <url> HEAD:refs/heads/<name>`: one private repo, one branch per framework repo. No git remote
     is configured (the linter flags remotes on framework repos) and nothing is force-pushed: history is
     append-only, a rewritten history is refused by git.
  3. Records the pushed commit as refs/offbox/<name>; the linter reports repos never copied off the box.

Not in scope: ~/Backups/openclaw-git (OpenClaw's database backup). Its history holds plaintext secrets from
before --exclude-secrets was enabled, so it must never go to a hosted git remote; copy it off the box with a
pull from Van's own machine instead (see ~/OPENCLAW_ARCHITECTURE.md §7, phase C).
Standard library only.
"""
import importlib.util
import os
import re
import subprocess
import sys

LINT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lint_workspace.py")


def die(m):
    print(f"framework_offbox: {m}", file=sys.stderr)
    sys.exit(1)


def lint():
    spec = importlib.util.spec_from_file_location("lint_workspace", LINT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args, check=True):
    r = subprocess.run(["git", *args], cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and r.returncode != 0:
        die(f"git {' '.join(args[:3])} in {repo} failed: {r.stderr.strip()[:300]}")
    return r


def token_hits(repo, rx):
    """[(commit, file, masked)] for every added or removed history line that looks like a credential."""
    out = git(repo, "log", "-p", "--all", "--format=COMMIT %h", check=False).stdout
    hits, commit, path = [], "?", "?"
    for line in out.splitlines():
        if line.startswith("COMMIT "):
            commit = line.split()[1]
        elif line.startswith("+++ ") or line.startswith("--- "):
            if line[4:] != "/dev/null":
                path = line[6:] if line[4:6] in ("a/", "b/") else line[4:]
        elif line[:1] in "+-":
            for m in re.finditer(rx, line):
                hits.append((commit, path, f"{m.group(0)[:6]}…({len(m.group(0))} chars)"))
    return sorted(set(hits))


def repos(L):
    return [(n, p) for n, p in L.framework_repos() if os.path.isdir(os.path.join(p, ".git"))]


def status(L):
    for name, repo in repos(L):
        head = git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        ref = git(repo, "rev-parse", "--verify", "--quiet", "--short", f"refs/offbox/{name}", check=False).stdout.strip()
        if not ref:
            print(f"{name:26} HEAD {head}  never copied off the box")
            continue
        n = git(repo, "rev-list", "--count", "HEAD", f"^refs/offbox/{name}").stdout.strip()
        print(f"{name:26} HEAD {head}  off-box {ref}  {n} commit(s) since")


def push(L, url, dry, allow_rotated):
    todo, blocked = [], []
    for name, repo in repos(L):
        dirty = [l for l in git(repo, "status", "--porcelain").stdout.splitlines() if l.strip()]
        if dirty:
            print(f"note: {name} has {len(dirty)} uncommitted path(s); only committed work is pushed")
        hits = token_hits(repo, L.TOKEN_RX)
        if hits:
            blocked.append(name)
            print(f"{name}: {len(hits)} token-shaped line(s) in history:")
            for c, f, m in hits[:20]:
                print(f"    {c}  {f}  {m}")
        todo.append((name, repo))
    if blocked and not allow_rotated:
        die(f"refused: credentials in the history of {', '.join(blocked)}. Rotate every one listed above, "
            f"then re-run with --allow-rotated. (Nothing was pushed.)")
    for name, repo in todo:
        sha = git(repo, "rev-parse", "HEAD").stdout.strip()
        if dry:
            print(f"DRY {name}: would push {sha[:12]} to {url} refs/heads/{name}")
            continue
        r = git(repo, "push", url, f"{sha}:refs/heads/{name}", check=False)
        if r.returncode != 0:
            die(f"push of {name} failed (nothing forced): {r.stderr.strip()[:400]}")
        git(repo, "update-ref", f"refs/offbox/{name}", sha)
        print(f"OK  {name} {sha[:12]} -> {url} ({name})")


def main():
    a = sys.argv[1:]
    L = lint()
    if a[:1] == ["status"]:
        return status(L)
    if a[:1] == ["push"] and len(a) >= 2 and not a[1].startswith("-"):
        return push(L, a[1], "--dry" in a, "--allow-rotated" in a)
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    main()
