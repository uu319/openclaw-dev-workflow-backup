#!/usr/bin/env python3
"""One git worktree per task, for any onboarded project. The only sanctioned way agents
create, hand off and remove code checkouts.

Usage:
  worktree.py <slug> create <branch> [--agent <id>] [--task "<one line>"]
  worktree.py <slug> finish <branch> [--pr <url>]
  worktree.py <slug> sweep
  worktree.py <slug> list
  worktree.py <slug> path <branch>

Lifecycle (see the shared `worktree-lifecycle` skill for the why):
  create  git fetch --prune, then a NEW branch from origin/<Flow PR base> (default: Default branch), or - if
          origin/<branch> already exists (review fixes, QA, code review) - a checkout of
          that remote branch. Verifies HEAD equals the start SHA and prints a preparation
          receipt. Copies gitignored files listed in the repo's .worktreeinclude, if any.
  finish  Removes the worktree right after the PR is opened, but ONLY if nothing in it
          exists only locally: no modified/untracked files, an upstream is set, and no
          commits ahead of it. Otherwise it keeps the folder and says why (exit 2).
  sweep   git fetch --prune + git worktree prune. A branch whose remote is gone
          (GitHub "Automatically delete head branches" after merge) is marked merged in
          the ledger and its local branch is deleted if its tip is the SHA we pushed.
          Active worktrees whose remote branch is gone are removed under the same safety
          rule as finish. Worktrees not created by this tool are reported, never touched.

Layout, derived from PROJECT_CONTEXT.md (single source of truth):
  primary checkout  Code (CWD)                      never edited by agents
  worktrees         <parent of Code (CWD)>/.worktrees/<slug>/<branch with / -> __>
  ledger            <Internal Artifacts>/worktrees.jsonl   (source of truth, append/replace)
  PR list           <Internal Artifacts>/prs.md             (generated from the ledger)

Every git call is non-interactive. Nothing here pushes, merges, force-removes, or touches a
branch with unpushed commits. Standard library only.
"""
import datetime
import fcntl
import fnmatch
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

# The workspace root. `OPENCLAW_WORKSPACE` overrides it so the tools can be run
# against an isolated copy (tests, a dry run of a new project) without touching
# the live tree - which the heartbeat scans every 15 minutes and acts on.
WORKSPACE = os.environ.get("OPENCLAW_WORKSPACE", "/home/openclaw/.openclaw/workspace")
VALIDATOR = f"{WORKSPACE}/projects/_tools/validate_context.py"
KEEP = 2  # exit code: refused to remove, work kept


def die(m, code=1):
    print(f"worktree: {m}", file=sys.stderr)
    sys.exit(code)


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- project context

class Project:
    def __init__(self, slug):
        ctx = f"{WORKSPACE}/projects/{slug}/PROJECT_CONTEXT.md"
        if not os.path.isfile(ctx):
            die(f"no PROJECT_CONTEXT.md for '{slug}' at {ctx}")
        spec = importlib.util.spec_from_file_location("vc", VALIDATOR)
        vc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(vc)
        fields, errors = vc.parse(ctx)
        if errors:
            die(f"invalid {ctx}: " + "; ".join(errors))
        self.slug = slug
        self.ctx = ctx
        self.primary = os.path.realpath(fields["code_cwd"])
        if not os.path.isdir(os.path.join(self.primary, ".git")):
            die(f"Code (CWD) {self.primary} is not a git checkout")
        self.artifacts = fields["artifacts_dir"].rstrip("/")
        os.makedirs(self.artifacts, exist_ok=True)
        self.root = os.path.join(os.path.dirname(self.primary), ".worktrees", slug)
        self.ledger = os.path.join(self.artifacts, "worktrees.jsonl")
        self.prs_md = os.path.join(self.artifacts, "prs.md")
        self.default_branch = fields.get("default_branch") or self._origin_head()
        # new task branches start from the Flow PR base (the branch PRs go into); defaults to Default branch
        self.pr_base = (fields.get("flow") or {}).get("pr_base") or self.default_branch
        self.branch_prefixes = fields.get("branch_prefixes") or []
        self.github = bool(fields.get("github_repo") and fields.get("git_secret"))

    def _origin_head(self):
        r = git(self.primary, "symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
        if r.returncode != 0:
            die(f"{self.ctx} has no '**Default branch:**' and origin/HEAD is unset")
        return r.stdout.strip().split("/", 1)[1]

    def path_for(self, branch):
        return os.path.join(self.root, branch.replace("/", "__"))


# ---------------------------------------------------------------- git helpers

def git(cwd, *args, check=True):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_OPTIONAL_LOCKS="0")
    r = subprocess.run(["git", "-C", cwd, *args], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True, env=env)
    if check and r.returncode != 0:
        die(f"git {' '.join(args)} failed in {cwd}:\n{r.stderr.strip()}")
    return r


def sha(cwd, ref):
    r = git(cwd, "rev-parse", "--verify", "--quiet", ref + "^{commit}", check=False)
    return r.stdout.strip() if r.returncode == 0 else None


def worktrees(primary):
    """git worktree list --porcelain -> [{path, branch, head}]"""
    out, cur = [], {}
    for line in git(primary, "worktree", "list", "--porcelain").stdout.splitlines():
        if not line:
            if cur:
                out.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur["path"] = os.path.realpath(line[9:])
        elif line.startswith("HEAD "):
            cur["head"] = line[5:]
        elif line.startswith("branch "):
            cur["branch"] = line[7:].removeprefix("refs/heads/")
    if cur:
        out.append(cur)
    return out


def local_only_work(wt, start_sha=None):
    """Reasons this worktree holds work that exists nowhere else. Empty list = safe to remove.
    A never-pushed branch still counts as safe when it is clean and HEAD is its start SHA
    (the task was abandoned before any work)."""
    reasons = []
    st = git(wt, "status", "--porcelain", "--untracked-files=all").stdout.strip()
    if st:
        n = len(st.splitlines())
        reasons.append(f"{n} modified/untracked file(s): " + "; ".join(st.splitlines()[:5]))
    up = git(wt, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}", check=False)
    if up.returncode != 0:
        if not reasons and start_sha and sha(wt, "HEAD") == start_sha:
            return []
        unpushed = git(wt, "rev-list", "--count", "HEAD", "--not", "--remotes").stdout.strip()
        if unpushed == "0" and sha(wt, "HEAD") != start_sha:
            return reasons  # pushed without -u: every commit is already on origin
        reasons.append("branch has no upstream and has commits that are on no remote "
                       "(push with `git push -u origin <branch>`)")
        return reasons
    remote_branch = up.stdout.strip().split("/", 1)[1]
    git(wt, "fetch", "--quiet", "origin", remote_branch, check=False)
    if sha(wt, "@{u}") is None:
        reasons.append(f"upstream {up.stdout.strip()} no longer exists on origin and commits may be unpushed")
        return reasons
    ahead = git(wt, "rev-list", "--count", "@{u}..HEAD").stdout.strip()
    if ahead != "0":
        reasons.append(f"{ahead} commit(s) not pushed to {up.stdout.strip()}")
    return reasons


# ---------------------------------------------------------------- ledger

class Ledger:
    """worktrees.jsonl: one JSON object per branch, rewritten under an exclusive lock."""

    def __init__(self, project):
        self.p = project
        self.lock = open(project.ledger + ".lock", "a")

    def __enter__(self):
        fcntl.flock(self.lock, fcntl.LOCK_EX)
        self.rows = []
        if os.path.isfile(self.p.ledger):
            with open(self.p.ledger) as fh:
                self.rows = [json.loads(l) for l in fh if l.strip()]
        return self

    def get(self, branch):
        for r in self.rows:
            if r["branch"] == branch:
                return r
        return None

    def upsert(self, branch, **kw):
        r = self.get(branch)
        if r is None:
            r = {"branch": branch, "slug": self.p.slug, "events": []}
            self.rows.append(r)
        ev = kw.pop("event", None)
        r.update({k: v for k, v in kw.items() if v is not None})
        r["updated_at"] = now()
        if ev:
            r["events"].append(f"{now()} {ev}")
        return r

    def __exit__(self, *exc):
        if exc[0] is None:
            tmp = self.p.ledger + ".tmp"
            with open(tmp, "w") as fh:
                for r in self.rows:
                    fh.write(json.dumps(r, sort_keys=True) + "\n")
            os.replace(tmp, self.p.ledger)
            self._render()
        fcntl.flock(self.lock, fcntl.LOCK_UN)
        self.lock.close()

    def _render(self):
        lines = [
            f"# Pull requests and worktrees - {self.p.slug}",
            "",
            f"<!-- GENERATED by projects/_tools/worktree.py from worktrees.jsonl. Do not edit by hand. -->",
            "",
            "| Branch | Status | PR | Opened by | Task | Updated |",
            "|---|---|---|---|---|---|",
        ]
        for r in sorted(self.rows, key=lambda r: r.get("created_at", ""), reverse=True):
            lines.append("| `{}` | {} | {} | {} | {} | {} |".format(
                r["branch"], r.get("status", "?"), r.get("pr_url", ""), r.get("agent", ""),
                (r.get("task") or "").replace("|", "/")[:80], r.get("updated_at", "")[:10]))
        with open(self.p.prs_md, "w") as fh:
            fh.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------- commands

def copy_worktreeinclude(p, dest):
    inc = os.path.join(p.primary, ".worktreeinclude")
    if not os.path.isfile(inc):
        return []
    pats = [l.strip() for l in open(inc) if l.strip() and not l.startswith("#")]
    ignored = git(p.primary, "ls-files", "--others", "--ignored", "--exclude-standard").stdout.split("\n")
    copied = []
    for rel in filter(None, ignored):
        if "node_modules/" in rel:
            continue
        if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(os.path.basename(rel), pat) for pat in pats):
            os.makedirs(os.path.dirname(os.path.join(dest, rel)) or dest, exist_ok=True)
            shutil.copy2(os.path.join(p.primary, rel), os.path.join(dest, rel))
            copied.append(rel)
    return copied


def _owner(p, branch):
    """Agent recorded in the ledger for this branch's current worktree (read-only, no lock needed)."""
    try:
        with open(p.ledger) as fh:
            rows = [json.loads(x) for x in fh if x.strip()]
    except FileNotFoundError:
        return None
    rec = next((r for r in reversed(rows) if r.get("branch") == branch), None) or {}
    return rec.get("agent") if rec.get("status") in ("active", "kept") else None


def cmd_create(p, branch, agent, task):
    if git(p.primary, "check-ref-format", "--branch", branch, check=False).returncode != 0:
        die(f"invalid branch name: {branch}")
    if branch == p.default_branch:
        die(f"refusing to create a worktree on the default branch {branch}; pick a task branch")
    if p.branch_prefixes and not any(branch.startswith(x) for x in p.branch_prefixes):
        if sha(p.primary, f"origin/{branch}") is None:  # existing remote branches keep their name
            die(f"branch '{branch}' must start with one of the project's Branch Prefixes "
                f"{p.branch_prefixes} (PROJECT_CONTEXT.md), e.g. {p.branch_prefixes[0]}<feature-slug>")
    path = p.path_for(branch)
    for wt in worktrees(p.primary):
        if wt.get("branch") == branch:
            if os.path.realpath(wt["path"]) == p.primary:
                die(f"{branch} is checked out in the PRIMARY checkout {p.primary}. Someone edited the "
                    f"primary checkout; tell Van. Do not work there.")
            owner = _owner(p, branch)
            if agent and owner and owner != agent:
                die(f"{branch} is checked out in {owner}'s worktree {wt['path']}. Agents never share a folder: "
                    f"{owner} must commit, `git push -u origin {branch}` and run `finish {branch}` first "
                    f"(VanDev pushes the task branch and opens the PR right after each lane commit).")
            print(f"exists: {wt['path']} (branch {branch}, HEAD {wt.get('head', '')[:12]}) - reusing it")
            return
    git(p.primary, "fetch", "--prune", "--quiet", "origin")
    remote = f"origin/{branch}"
    local_sha, remote_sha = sha(p.primary, f"refs/heads/{branch}"), sha(p.primary, remote)
    os.makedirs(p.root, exist_ok=True)
    if remote_sha:
        if local_sha and local_sha != remote_sha:
            if git(p.primary, "merge-base", "--is-ancestor", local_sha, remote_sha, check=False).returncode != 0:
                die(f"local branch {branch} has commits not on {remote}; resolve that before reusing the name")
        git(p.primary, "worktree", "add", "--quiet", "-B", branch, path, remote)
        git(path, "branch", "--quiet", f"--set-upstream-to={remote}")
        start_ref, start_sha, kind = remote, remote_sha, "existing remote branch"
    else:
        if local_sha:
            die(f"local branch {branch} exists but was never pushed; use a new branch name or push it first")
        base = f"origin/{p.pr_base}"
        base_sha = sha(p.primary, base) or die(f"{base} not found after fetch")
        git(p.primary, "worktree", "add", "--quiet", "--no-track", "-b", branch, path, base)
        start_ref, start_sha, kind = base, base_sha, "new branch"
    head = sha(path, "HEAD")
    if head != start_sha:
        die(f"worktree HEAD {head} != start {start_ref} {start_sha}; not using it")
    copied = copy_worktreeinclude(p, path)
    with Ledger(p) as led:
        led.upsert(branch, status="active", worktree=path, agent=agent, task=task,
                   start_ref=start_ref, start_sha=start_sha,
                   created_at=(led.get(branch) or {}).get("created_at") or now(),
                   event=f"create ({kind}) by {agent or '?'} at {start_sha[:12]}")
    print("Preparation receipt")
    print(f"  project         {p.slug}")
    print(f"  worktree        {path}")
    print(f"  branch          {branch} ({kind})")
    print(f"  started from    {start_ref} @ {start_sha}  (fetched just now, HEAD verified)")
    print(f"  primary         {p.primary}  (read-only for agents)")
    if copied:
        print(f"  copied          {', '.join(copied)} (from .worktreeinclude)")
    if kind == "new branch":
        print(f"  first push      git -C {path} push -u origin {branch}")
    print(f"  after the PR    python3 {os.path.abspath(__file__)} {p.slug} finish {branch} --pr <url>   (REQUIRED)")


def cmd_finish(p, branch, pr):
    wt = next((w for w in worktrees(p.primary) if w.get("branch") == branch), None)
    if wt is None:
        die(f"no worktree for {branch}. Nothing to finish.")
    if os.path.realpath(wt["path"]) == p.primary:
        die(f"{branch} is the primary checkout; finish only removes task worktrees")
    with Ledger(p) as led:
        rec = led.get(branch) or {}
        reasons = local_only_work(wt["path"], rec.get("start_sha"))
        unused = not reasons and sha(wt["path"], "HEAD") == rec.get("start_sha")
        if reasons:
            led.upsert(branch, status="kept", pr_url=pr, event="finish refused: " + " | ".join(reasons))
        else:
            head = sha(wt["path"], "HEAD")
            r = git(p.primary, "worktree", "remove", wt["path"], check=False)
            if r.returncode != 0:
                reasons = [f"git worktree remove refused: {r.stderr.strip()}"]
                led.upsert(branch, status="kept", pr_url=pr, event="finish refused: " + reasons[0])
            elif unused and sha(p.primary, f"origin/{branch}") is not None:
                # QA / review / no-op checkout of a branch that is already on origin: the branch's
                # row (pushed / pr_open) must survive, or close-on-merge loses track of the PR.
                git(p.primary, "branch", "-D", branch)
                led.upsert(branch, status=rec.get("status") if rec.get("status") not in (None, "active", "kept")
                           else ("pr_open" if (pr or rec.get("pr_url")) else "pushed"), pr_url=pr, worktree=None,
                           event="finish: no new commits (branch already on origin); removed worktree")
            elif unused:
                git(p.primary, "branch", "-D", branch)
                led.upsert(branch, status="abandoned", worktree=None,
                           event="finish: no work was done; removed worktree and local branch")
            else:
                led.upsert(branch, status="pr_open" if (pr or rec.get("pr_url")) else "pushed", pr_url=pr,
                           pushed_sha=head, worktree=None,
                           event=f"finish: removed worktree, pushed {head[:12]}")
    if reasons:
        print(f"KEPT {wt['path']} - it holds work that exists only here:")
        for x in reasons:
            print(f"  - {x}")
        print("Push or commit it (or tell Van), then run finish again. Nothing was deleted.")
        sys.exit(KEEP)
    print(f"removed {wt['path']} ({'no new commits; local branch deleted' + (f', origin/{branch} untouched' if sha(p.primary, f'origin/{branch}') else '') if unused else f'everything is on origin/{branch}'}); "
          f"recorded in {p.prs_md}")


def pr_for(p, branch):
    """Latest GitHub PR for a head branch via git_env.py -> dict(state, headRefOid, url) or None.
    Returns None when the project has no GitHub token or GitHub cannot be reached."""
    if not p.github:
        return None
    launcher = os.path.join(os.path.dirname(os.path.abspath(__file__)), "git_env.py")
    r = subprocess.run([sys.executable, launcher, p.slug, "--", "gh", "pr", "list", "--head", branch,
                        "--state", "all", "--limit", "1", "--json", "state,headRefOid,url,number"],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=p.primary)
    if r.returncode != 0:
        return None
    rows = json.loads(r.stdout or "[]")
    return rows[0] if rows else {}


def cmd_sweep(p):
    """Clean up after merged/closed work, whether or not `finish` was run.
    A branch is done when origin/<branch> is gone AND either GitHub reports its PR MERGED/CLOSED
    with the PR head == the local tip, or (no GitHub) the local tip == the SHA `finish` recorded.
    Only then, and only if the worktree has no uncommitted/untracked files, is anything deleted."""
    git(p.primary, "fetch", "--prune", "--quiet", "origin")
    git(p.primary, "worktree", "prune")
    report = []
    live = {w.get("branch"): w for w in worktrees(p.primary)}
    with Ledger(p) as led:
        for r in led.rows:
            b = r["branch"]
            if r.get("status") in ("merged_or_closed", "abandoned"):
                continue
            if sha(p.primary, f"origin/{b}") is not None:
                continue  # still on GitHub: open PR or work in progress
            wt = live.get(b)
            wt_path = wt["path"] if wt and os.path.realpath(wt["path"]) != p.primary else None
            tip = sha(wt_path, "HEAD") if wt_path else sha(p.primary, f"refs/heads/{b}")
            if tip is None:
                led.upsert(b, status="merged_or_closed", worktree=None, event="sweep: no worktree, no branch")
                continue
            pr = pr_for(p, b)
            if pr and pr.get("state") in ("MERGED", "CLOSED"):
                verified = pr.get("headRefOid") == tip
                how = f"PR #{pr.get('number')} {pr['state'].lower()}"
                if not verified:
                    report.append(f"KEPT   {b}: {how} but local tip {tip[:12]} != PR head "
                                  f"{(pr.get('headRefOid') or '')[:12]} - local commits were never in the PR; tell Van")
                    continue
            elif pr and pr.get("state") == "OPEN":
                report.append(f"KEPT   {b}: PR #{pr.get('number')} is open but origin/{b} is gone - tell Van")
                continue
            elif r.get("pushed_sha") and r["pushed_sha"] == tip:
                how, verified = "remote branch deleted (git-only check)", True
            else:
                if tip != r.get("start_sha"):
                    report.append(f"ACTIVE {b}: not on GitHub yet ({r.get('agent') or '?'}, created {r.get('created_at', '?')[:16]})")
                continue
            if wt_path:
                dirty = git(wt_path, "status", "--porcelain", "--untracked-files=all").stdout.strip()
                if dirty:
                    report.append(f"KEPT   {b}: {how}, but the worktree has files that were never committed "
                                  f"(so they are NOT in the PR): {'; '.join(dirty.splitlines()[:5])} - tell Van")
                    led.upsert(b, status="kept", pr_url=(pr or {}).get("url"),
                               event=f"sweep: {how}; uncommitted files kept")
                    continue
                if git(p.primary, "worktree", "remove", wt_path, check=False).returncode:
                    report.append(f"KEPT   {b}: git worktree remove refused")
                    continue
            git(p.primary, "branch", "-D", b, check=False)
            led.upsert(b, status="merged_or_closed", worktree=None, pr_url=(pr or {}).get("url"),
                       event=f"sweep: {how}; worktree and local branch removed")
            report.append(f"DONE   {b}: {how}; worktree and local branch removed")
        known = {r["branch"] for r in led.rows}
    for b, w in live.items():
        if os.path.realpath(w["path"]) == p.primary:
            continue
        if b not in known:
            report.append(f"UNMANAGED {w['path']} ({b or 'detached'}) - not created by worktree.py; left alone")
    dirty = git(p.primary, "status", "--porcelain").stdout.strip()
    cur = git(p.primary, "branch", "--show-current").stdout.strip()
    if dirty or cur != p.default_branch:
        report.append(f"PRIMARY {p.primary} is on '{cur}' with {len(dirty.splitlines())} changed file(s); "
                      f"agents must not edit it - tell Van")
    report += retention(p)
    print("\n".join(report) if report else "sweep: nothing to do")


RETAIN_DAYS = 30   # Decision J (2026-09-19): run logs, and screenshots of archived features


def retention(p):
    """Delete agent run logs older than RETAIN_DAYS, and specs/_figma/<feature>/ folders whose spec has been in
    specs/_done/ for longer than RETAIN_DAYS. Nothing else. Loose files in specs/_figma/ are left alone."""
    out, cutoff = [], datetime.datetime.now().timestamp() - RETAIN_DAYS * 86400
    runs = os.path.join(p.artifacts, "runs")
    old = [f for f in glob_files(runs, ".log") if os.path.getmtime(f) < cutoff]
    for f in old:
        os.remove(f)
    if old:
        out.append(f"RETAIN removed {len(old)} run log(s) older than {RETAIN_DAYS} days from {runs}")
    figma, done = os.path.join(p.artifacts, "specs", "_figma"), os.path.join(p.artifacts, "specs", "_done")
    if os.path.isdir(figma):
        for d in sorted(os.listdir(figma)):
            folder, spec = os.path.join(figma, d), os.path.join(done, d + ".md")
            if os.path.isdir(folder) and os.path.isfile(spec) and os.path.getmtime(spec) < cutoff:
                shutil.rmtree(folder)
                out.append(f"RETAIN removed screenshots {folder} (feature archived over {RETAIN_DAYS} days ago)")
    return out


def glob_files(folder, suffix):
    if not os.path.isdir(folder):
        return []
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(suffix) and os.path.isfile(os.path.join(folder, f))]


def cmd_list(p):
    live = {w.get("branch"): w for w in worktrees(p.primary)}
    with Ledger(p) as led:
        rows = list(led.rows)
    print(f"{'BRANCH':42} {'STATUS':17} {'WORKTREE ON DISK':6} PR")
    for r in sorted(rows, key=lambda r: r.get("created_at", ""), reverse=True):
        print(f"{r['branch'][:42]:42} {r.get('status', '?'):17} {'yes' if r['branch'] in live else 'no':6} {r.get('pr_url', '')}")
    for b, w in live.items():
        if b not in {r['branch'] for r in rows} and os.path.realpath(w["path"]) != p.primary:
            print(f"{(b or 'detached')[:42]:42} {'UNMANAGED':17} {'yes':6} {w['path']}")


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        sys.exit(1)
    slug, cmd, rest = a[0], a[1], a[2:]

    def opt(name):
        if name in rest:
            i = rest.index(name)
            if i + 1 >= len(rest):
                die(f"{name} needs a value")
            v = rest[i + 1]
            del rest[i:i + 2]
            return v
        return None

    agent, task, pr = opt("--agent"), opt("--task"), opt("--pr")
    p = Project(slug)
    if cmd == "sweep":
        cmd_sweep(p)
    elif cmd == "list":
        cmd_list(p)
    elif cmd in ("create", "finish", "path"):
        if len(rest) != 1:
            die(f"usage: worktree.py <slug> {cmd} <branch>")
        branch = rest[0]
        if cmd == "create":
            cmd_create(p, branch, agent or os.environ.get("OPENCLAW_AGENT_ID"), task)
        elif cmd == "finish":
            cmd_finish(p, branch, pr)
        else:
            print(p.path_for(branch))
    else:
        die(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
