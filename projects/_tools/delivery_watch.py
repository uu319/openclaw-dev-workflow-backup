#!/usr/bin/env python3
"""Delivery watcher: GitHub PRs -> CI (staging) -> the tracker, for one onboarded project.

Read-only. It looks, then prints the ACTIONS the orchestrator (heartbeat) must carry out. It never
writes to GitHub, the CI or the tracker itself; ticket moves stay VanPM's, code stays VanDev's.

Usage:
  delivery_watch.py <slug>                 # print pending actions (and remember them)
  delivery_watch.py <slug> --json          # same, machine-readable
  delivery_watch.py <slug> --ack <id> ...  # mark actions handled (after doing them)
  delivery_watch.py <slug> --dry --since 2026-09-18T00:00:00Z   # test on history, writes nothing

The flow it drives (statuses are the project's; see the project-orchestration skill):
  PR open + new GitHub comment/review  -> PR_FEEDBACK   (VanDev fixes, internal review, push, reply)
  PR merged                            -> wait for the project's CI on the Flow PR base
  every build of the first commit that contains the merge commit succeeded
                                       -> DEPLOYED      (VanPM: linked tickets -> `qa`)
  the PR's OWN merge commit is red     -> BUILD_FAILED  (report + bug ticket, normal flow)
                                          Only the newest red is raised (staging is red once), and only
                                          against the PR that introduced it - never every ancestor PR.
                                          A red commit with no PR on this base is reported on its own.
  merged, no build after 45 min        -> NO_BUILD
  PR closed without merge              -> PR_CLOSED
  ticket moved to `rejected` by QA     -> REJECTED      (VanDev picks it up again)
  every ticket of a spec `complete`    -> FEATURE_COMPLETE (archive, clean up, note)
  worktree older than 3 days           -> STALE_WORKTREE; once a day SWEEP_DUE
  once a day, first project only      -> LINT (lint_workspace.py found FIX lines; report, never delete)

Per-project Flow (PROJECT_CONTEXT `## Flow`, parsed by validate_context.py):
  - `delivery-watch` not in Stages     -> only SWEEP_DUE / STALE_WORKTREE / LINT are reported
  - Deploy signal `none`               -> a merged PR gives MERGED (tickets -> `staged` if the board has it, else `done`)
  - statuses are the board's own names through the Status map; PRs are watched on the Flow PR base

Only PRs authored by the project token's own account are acted on (branch prefixes are the
fallback if that lookup fails). Anyone else's PR is watched for a red build on the base and
still moves our tickets when its body links them, but is never pushed to or replied to.

Linking a PR to tickets: the tracker's own references in the PR body (ClickUp task URLs,
Jira browse URLs or bare KEY-123, Linear issue URLs or bare ENG-12), plus every
ticket of `specs/<feature-slug>.md` when the branch is `<prefix>/<feature-slug>[--<suffix>]`.
Agent replies on GitHub start with the AGENT_MARK so they are not read back as new feedback.
Comments by `*[bot]` accounts and by the PROJECT_CONTEXT line `- **GitHub bots:** `name`` are ignored.

State: <Internal Artifacts>/delivery_state.json (watch_since, acked ids, seen feedback ids).
PRs merged before watch_since (set on first run) are history and never acted on.
"""
import argparse, datetime, glob, importlib.util, json, os, re, shutil, subprocess, sys, urllib.error, urllib.request

TOOLS = os.path.dirname(os.path.abspath(__file__))
VALIDATOR = os.path.join(TOOLS, "validate_context.py")
WORKSPACE = "/home/openclaw/.openclaw/workspace"

sys.path.insert(0, TOOLS)
import ci  # noqa: E402
import trackers  # noqa: E402
AGENT_MARK = "🤖"
# Status sets are per project (Flow Status map); these are filled in Ctx.__init__.
QA_FROM, REJECTED, CLOSED = set(), set(), set()
NO_BUILD_AFTER_MIN = 45
STALE_DAYS = 3


def die(m):
    print(f"ERROR: {m}", file=sys.stderr); sys.exit(1)


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_t(s):
    if not s:
        return None
    s = re.sub(r"\.\d+", "", s).replace("Z", "+00:00")
    return datetime.datetime.fromisoformat(s)


def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return r.returncode, r.stdout, r.stderr


class Ctx:
    def __init__(self, slug):
        self.slug = slug
        self.path = f"{WORKSPACE}/projects/{slug}/PROJECT_CONTEXT.md"
        if not os.path.isfile(self.path):
            die(f"no PROJECT_CONTEXT.md for {slug}")
        spec = importlib.util.spec_from_file_location("vc", VALIDATOR)
        vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
        self.f, errors = vc.parse(self.path)
        if errors:
            die("; ".join(errors))
        self.primary = os.path.realpath(self.f["code_cwd"])
        self.art = self.f["artifacts_dir"].rstrip("/")
        self.specs = os.path.join(self.art, "specs")
        self.flow = self.f.get("flow") or {}
        self.st = self.f.get("status") or {}
        # PRs are watched on the Flow PR base; builds on the same branch
        self.branch = self.flow.get("pr_base") or self.f.get("default_branch") or "main"
        # Only the project's own Status map decides these. Literal board names used to
        # live here ("for development", "closed") - fms-studio's, in a tool shared by
        # every project. A board whose statuses differ is handled by the map, not here.
        low = lambda *ks: {self.st[k].lower() for k in ks if self.st.get(k)}
        QA_FROM.clear(); QA_FROM.update(low("todo", "doing", "rejected", "hold"))
        REJECTED.clear(); REJECTED.update(low("rejected"))
        CLOSED.clear(); CLOSED.update(low("done", "cancelled"))
        self.staged = self.st.get("staged")
        self.done = self.st.get("done")
        self.prefixes = self.f.get("branch_prefixes") or []
        m = re.search(r"^- \*\*GitHub bots:\*\*(.*)$", open(self.path).read(), re.M)
        self.bots = set(re.findall(r"`([^`]+)`", m.group(1))) if m else set()

    # ---- GitHub (through git_env.py: the project's own token) ----
    def gh(self, *args):
        rc, out, err = run([sys.executable, os.path.join(TOOLS, "git_env.py"), self.slug, "--", "gh", *args],
                           cwd=self.primary)
        if rc != 0:
            raise RuntimeError(f"gh {' '.join(args[:3])}: {err.strip()[:300]}")
        return json.loads(out) if out.strip() else None

    # ---- GCP (through gcloud_env.py: the project's own service account) ----
    def gcloud(self, *args):
        rc, out, err = run([sys.executable, os.path.join(TOOLS, "gcloud_env.py"), self.slug, "--",
                            "gcloud", *args], cwd=self.primary)
        if rc != 0:
            raise RuntimeError(f"gcloud {' '.join(args[:2])}: {err.strip()[:300]}")
        return json.loads(out or "[]")

    # ---- CI (whichever this project uses; see ci/) ----
    def ci(self):
        if getattr(self, "_ci", None) is None:
            self._ci = ci.for_project(self.f, self)
        return self._ci

    def ci_runs(self, limit=60):
        return self.ci().runs(self.branch, limit)

    # ---- tracker (read-only; token from env, else the vault, like the other launchers) ----
    def tracker(self):
        """The adapter for whatever tracker this project uses. `none` -> NoTracker."""
        if getattr(self, "_tk", None) is None:
            token = None
            if self.f.get("tracker", "none") != "none":
                name = self.f["tracker_secret"]
                token = os.environ.get(name)
                if not token:
                    rc, out, err = run([shutil.which("openclaw") or "/usr/bin/openclaw",
                                        "secrets", "store", "get", "--plain", name])
                    if rc != 0 or not out.strip():
                        raise RuntimeError(f"could not read vault entry {name}")
                    token = out.strip()
            self._tk = trackers.for_project(self.f, token)
        return self._tk

    def is_ancestor(self, a, b):
        return run(["git", "merge-base", "--is-ancestor", a, b], cwd=self.primary)[0] == 0


# ---------------------------------------------------------------- linking PRs to tickets

def markers(ctx, include_done=True):
    """feature-slug -> (marker path, {title: info})"""
    out = {}
    # `.tracker.json` is the name going forward; `.clickup.json` markers written
    # before the rename are still read, so no live feature loses its ticket link.
    dirs = [ctx.specs] + ([os.path.join(ctx.specs, "_done")] if include_done else [])
    pats = [os.path.join(d, f"*{sfx}") for d in dirs for sfx in (".tracker.json", ".clickup.json")]
    for p in pats:
        for m in glob.glob(p):
            slug = re.sub(r"\.(tracker|clickup)\.json$", "", os.path.basename(m))
            try:
                out.setdefault(slug, (m, json.load(open(m))))
            except (OSError, ValueError):
                pass
    return out


def tickets_for_pr(ctx, pr, marks):
    ids, spec = set(ctx.tracker().links_in_text(pr.get("body") or "")), None
    head = pr.get("headRefName", "")
    for pre in ctx.prefixes:
        if head.startswith(pre):
            feature = head[len(pre):].split("--")[0]
            if feature in marks:
                spec = feature
                ids |= {v["id"] for k, v in marks[feature][1].items() if not k.startswith("_") and isinstance(v, dict)}
    return ids, spec


# ---------------------------------------------------------------- builds

def commits_from_runs(ctx, runs):
    """commit -> {'status': ok|running|failed, 'runs': [latest per check], 'at': first start}

    Provider-independent: `runs` are already normalised by ci/. Every check the
    project lists in **Deploy checks** must be green before a commit counts as
    deployed, which is what stops a monorepo's frontend build alone from moving a
    backend ticket (2026-09-19).
    """
    by = {}
    for r in runs:
        c, check = r["commit"], r["check"]
        cur = by.setdefault(c, {}).get(check)
        if cur is None or (r.get("at") or "") > (cur.get("at") or ""):
            by[c][check] = r

    expected = set(ctx.f.get("deploy_checks") or [])

    out = {}
    for c, checks in by.items():
        rs = list(checks.values())
        sts = {r["status"] for r in rs}
        missing = sorted(expected - set(checks.keys()))
        # A check we expect but have not seen usually means it is still queued, so we
        # wait. But "wait" must not be forever: a check that never fires (path filter,
        # disabled trigger, or the run falling out of the `limit` window) would pin the
        # commit on "running" and silently stop every ticket move. After NO_BUILD_AFTER_MIN
        # we judge the commit on the runs that did happen and say which check is missing.
        last = parse_t(max((r.get("at") or "") for r in rs))
        waiting = missing and last and now() - last <= datetime.timedelta(minutes=NO_BUILD_AFTER_MIN)

        if "running" in sts or waiting:
            st = "running"
        else:
            st = "ok" if sts == {"ok"} else "failed"

        out[c] = {"status": st, "runs": rs, "missing": [] if waiting else missing,
                  "at": min(r.get("at") or "" for r in rs)}
    return out


def is_ours(pr, prefixes, me):
    """A PR this team's agents may act on.

    Without this, every open PR on the base branch - including a human teammate's -
    produced PR_FEEDBACK, which spawns VanDev onto their branch to push commits
    (2026-09-19). Someone else's PR is still watched for a red build on the base, and
    still moves our tickets when it carries them; it is just never acted on directly.

    The account the project token belongs to is the real signal. Branch naming is only
    the fallback for when that lookup failed: our own PRs are not always named to the
    convention (`fix-chokidar-deps`), so naming alone would skip work that is ours.
    """
    if me:
        return (pr.get("author") or {}).get("login") == me
    head = pr.get("headRefName", "")
    return not prefixes or any(head.startswith(p) for p in prefixes)


def bdesc(r):
    """One line about a CI run, whichever provider produced it."""
    return f"{r.get('check', '?')} {r.get('raw_status') or r['status']} run {r.get('id', '')} ({r.get('url', '')})"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("--json", action="store_true")
    ap.add_argument("--ack", nargs="+"); ap.add_argument("--dry", action="store_true", help="write no state")
    ap.add_argument("--since", help="ISO time; overrides watch_since (use with --dry to test on history)")
    a = ap.parse_args()
    ctx = Ctx(a.slug)
    state_path = os.path.join(ctx.art, "delivery_state.json")
    try:
        state = json.load(open(state_path))
    except (OSError, ValueError):
        state = {}
    state.setdefault("watch_since", iso(now())); state.setdefault("acked", {})
    state.setdefault("pending", {}); state.setdefault("seen_feedback", [])

    def save():
        if not a.dry:
            tmp = state_path + ".tmp"
            json.dump(state, open(tmp, "w"), indent=1, sort_keys=True); os.replace(tmp, state_path)

    if a.ack:
        unknown = [i for i in a.ack if i not in state["pending"] and i not in state["acked"]]
        if unknown:
            die(f"unknown action id(s) {unknown}: ack only the exact `ack:` ids the watcher printed "
                f"(pending: {sorted(state['pending'])})")
        for i in a.ack:
            p = state["pending"].pop(i, None)
            if p and p.get("feedback_ids"):
                state["seen_feedback"] = sorted(set(state["seen_feedback"]) | set(p["feedback_ids"]))
            if i.startswith("sweep-"):
                state["last_sweep"] = iso(now())
            state["acked"][i] = iso(now())
        save(); print(f"acked {len(a.ack)}"); return

    since = parse_t(a.since or state["watch_since"])
    actions, notes, errors = [], [], []

    def act(aid, kind, summary, do, **data):
        if aid in state["acked"]:
            return
        dup = next((x for x in actions if x["id"] == aid), None)
        if dup:   # e.g. one failed build shared by several merged PRs: one action, all PRs + tickets
            dup["summary"] += f" | also {summary.split(':')[0]}"
            dup["tickets"] = sorted(set(dup.get("tickets") or []) | set(data.get("tickets") or []))
            return
        actions.append({"id": aid, "kind": kind, "summary": summary, "do": do, **data})

    run(["git", "fetch", "--quiet", "--prune", "origin"], cwd=ctx.primary)
    marks = markers(ctx)
    status_cmd = (f"python3 {WORKSPACE}/project-manager/skills/feature-breakdown/scripts/tracker_status.py "
                  f"--context {ctx.path} --spec <spec> --only \"<title>\" --status "
                  f"{'staged' if ctx.staged else 'done'}")
    stages = ctx.flow.get("stages") or []
    watching = "delivery-watch" in stages

    # ---- tracker snapshot (normalised by trackers/; `none` yields {})
    tasks = {}
    try:
        tasks = ctx.tracker().tasks()
    except Exception as e:  # noqa: BLE001 - report, keep watching the rest
        errors.append(f"{ctx.f.get('tracker', 'tracker')}: {e}")
    stat = lambda tid: ((tasks.get(tid) or {}).get("status") or "?").lower()
    title_of = {v["id"]: (slug, k) for slug, (_, m) in marks.items() for k, v in m.items()
                if not k.startswith("_") and isinstance(v, dict)}

    def qa_moves(ids):
        """[(ticket id, spec slug, title, current status)] that should go to qa, parents included."""
        moves = [(i, *title_of.get(i, (None, (tasks.get(i) or {}).get("name", i))), stat(i))
                 for i in sorted(ids) if stat(i) in QA_FROM or (not tasks and i)]
        moved = {m[0] for m in moves}
        for slug, (_, m) in marks.items():                 # parent -> qa when all its children are qa+
            kids = [v["id"] for k, v in m.items() if not k.startswith("_") and isinstance(v, dict)]
            if not kids or not (set(kids) & moved):
                continue
            parent, children = kids[0], kids[1:]
            staged = {ctx.staged.lower()} if ctx.staged else set()
            if children and stat(parent) in QA_FROM and all(c in moved or stat(c) in staged | CLOSED for c in children):
                moves.append((parent, slug, title_of[parent][1], stat(parent)))
        return moves

    # ---- PRs + builds (only when the project's Flow has the delivery-watch stage)
    if not watching:
        prs = []
        notes.append(f"delivery-watch is not in this project's Flow Stages {stages}; PRs and builds are not watched")
    else:
      try:
        prs = ctx.gh("pr", "list", "--state", "all", "--base", ctx.branch, "--limit", "40", "--json",
                     "number,title,state,headRefName,mergedAt,closedAt,mergeCommit,url,body,author,updatedAt") or []
      except RuntimeError as e:
        errors.append(str(e)); prs = []
    try:
        commits = commits_from_runs(ctx, ctx.ci_runs()) if watching and ctx.flow.get("deploy_signal") != "none" else {}
    except RuntimeError as e:
        errors.append(str(e)); commits = {}

    me = None
    if watching:
        try:
            me = (ctx.gh("api", "user") or {}).get("login") or None
        except RuntimeError as e:
            errors.append(f"gh api user: {e}")

    def build_failed(c, d, where, ids):
        bad = [r for r in d["runs"] if r["status"] != "ok"]
        why = "; ".join(bdesc(b) for b in bad)
        if d.get("missing"):
            why += f"; never ran: {', '.join(d['missing'])}"
        act(f"build-{c[:12]}", "BUILD_FAILED",
            f"{where}: staging build of {c[:10]} failed: {why}",
            f"Tell Van in one line with the build id and log link. If `{ctx.specs}/staging-build-{c[:10]}.md` does not "
            f"exist yet, spawn VanPM (it only writes the spec and pushes tickets; it never spawns agents): file "
            f"the bug ticket there. Then YOU spawn VanDev (project-orchestration step 2, no worktree/cwd) to fix it "
            f"on `bug/staging-build-{c[:10]}`, then VanReviewer, then ask Van for the PR. The original tickets stay "
            f"`in progress` and move to `qa` by themselves once a later build containing them succeeds. Ack only "
            f"after VanDev has started on the fix.", tickets=ids)

    # Merge commits of every PR on this base, so a red commit that belongs to one of them
    # is reported against that PR and a red commit that belongs to nobody (a direct push,
    # or another team merging outside this base) is still reported rather than lost.
    pr_merges = {(p.get("mergeCommit") or {}).get("oid") for p in prs if p.get("mergeCommit")}
    reds = []       # (commit, build info, where, ticket ids) - resolved to one action below

    for pr in prs:
        n, head = pr["number"], pr.get("headRefName", "")
        if (pr.get("author") or {}).get("login", "").endswith("[bot]") or head.startswith("dependabot/"):
            continue
        ids, spec = tickets_for_pr(ctx, pr, marks)
        where = f"PR #{n} `{head}` {pr['url']}"
        ours = is_ours(pr, ctx.prefixes, me)
        if pr["state"] == "OPEN":
            if not ours:
                notes.append(f"{where}: open PR by {(pr.get('author') or {}).get('login')}; not ours, left alone")
                continue
            try:
                v = ctx.gh("pr", "view", str(n), "--json", "comments,reviews") or {}
                inline = ctx.gh("api", f"repos/{ctx.f['github_repo']}/pulls/{n}/comments") or []
            except RuntimeError as e:
                errors.append(str(e)); continue
            items = []
            for c in v.get("comments", []):
                items.append(("c" + str(c.get("id") or c.get("url")), c.get("author", {}).get("login"), c.get("body", ""), c.get("createdAt")))
            for r in v.get("reviews", []):
                if r.get("body") or r.get("state") == "CHANGES_REQUESTED":
                    items.append(("r" + str(r.get("id")), r.get("author", {}).get("login"),
                                  f"[{r.get('state')}] " + (r.get("body") or ""), r.get("submittedAt")))
            for c in inline:
                items.append(("i" + str(c["id"]), (c.get("user") or {}).get("login"),
                              f"{c.get('path')}:{c.get('line') or c.get('original_line')}: {c.get('body', '')}", c.get("created_at")))
            new = [x for x in items if x[0] not in state["seen_feedback"]
                   and not (x[2] or "").lstrip().startswith(AGENT_MARK)
                   and not (x[1] or "").endswith("[bot]") and (x[1] or "") not in ctx.bots]
            if new:
                aid = f"feedback-pr{n}-" + "-".join(sorted(x[0] for x in new))[-40:]
                act(aid, "PR_FEEDBACK", f"{where}: {len(new)} new comment(s)/review(s)",
                    f"sessions_send/spawn VanDev: pull the review feedback directly from the PR using `gh pr view {pr.get('url')} --comments`, address the feedback on branch `{head}` (own worktree: "
                    f"`create {head}`), push to the same branch, then reply on the PR "
                    f"with a comment that starts with '{AGENT_MARK} VanDev:' directly on the threads you fixed. Ack when the fix is pushed.",
                    feedback=[{"by": x[1], "at": x[3], "text": (x[2] or "")[:800]} for x in new],
                    feedback_ids=[x[0] for x in new])
            continue
        if pr["state"] == "CLOSED":
            if ours and parse_t(pr.get("closedAt")) and parse_t(pr["closedAt"]) >= since:
                act(f"closed-pr{n}", "PR_CLOSED", f"{where} was closed without merging",
                    "Tell Van and ask: drop it (VanPM -> `cancelled`) or redo it (VanPM -> `in progress`).",
                    tickets=sorted(ids))
            continue
        merged_at = parse_t(pr.get("mergedAt"))
        if not merged_at or merged_at < since:
            continue
        msha = (pr.get("mergeCommit") or {}).get("oid")
        if not msha:
            continue
        if ctx.flow.get("deploy_signal") == "none":        # no deploy pipeline: the merge is the signal
            moves = qa_moves(ids)
            target = "staged" if ctx.staged else "done"
            if moves:
                act(f"merged-pr{n}", "MERGED", f"{where} was merged (this project has no deploy signal)",
                    f"Spawn VanPM: set each ticket below to `{target}` (the board's `{ctx.st.get(target)}`; one "
                    f"tracker_status.py --only call each). Only tickets of this Flow's Assignee filter "
                    f"(`{ctx.flow.get('assignee_filter')}`) may be moved; list any other ticket for Van instead. "
                    f"Post one line in the channel. Ack after VanPM confirms.",
                    tickets=[{"id": i, "spec": sp and f"{ctx.specs}/{sp}.md", "title": t, "status": st} for i, sp, t, st in moves],
                    command=status_cmd)
            else:
                notes.append(f"{where}: merged; no linked ticket needs moving")
            continue
        cands = sorted(((c, d) for c, d in commits.items() if ctx.is_ancestor(msha, c)), key=lambda x: x[1]["at"])
        ok = next(((c, d) for c, d in cands if d["status"] == "ok"), None)
        if ok:
            moves = qa_moves(ids)
            builds = "; ".join(bdesc(r) for r in ok[1]["runs"])
            if moves:
                act(f"deployed-pr{n}", "DEPLOYED", f"{where} is on staging (commit {ok[0][:10]}: {builds})",
                    f"Spawn VanPM: set each ticket below to `staged` (the board's `{ctx.staged}`; one tracker_status.py --only call each), then post "
                    "one line in the channel: what is ready for testing on staging. Ack after VanPM confirms.",
                    tickets=[{"id": i, "spec": s and f"{ctx.specs}/{s}.md", "title": t, "status": st} for i, s, t, st in moves],
                    command=status_cmd)
            elif not ids and ours:
                act(f"deployed-pr{n}", "DEPLOYED", f"{where} is on staging (commit {ok[0][:10]}); no ticket is linked",
                    "Tell Van in one line (no ticket to move). Ack.")
            elif not ours:
                notes.append(f"{where}: on staging (not ours; no action)")
            else:
                notes.append(f"{where}: on staging; its tickets are already qa/complete")
            continue
        failed = [(c, d) for c, d in cands if d["status"] == "failed"]
        running = [(c, d) for c, d in cands if d["status"] == "running"]
        # Blame only the commit that INTRODUCED the failure - this PR's own merge commit.
        # Every earlier PR is an ancestor of it too, and blaming all of them turned one
        # person's red build into one bug ticket carrying five unrelated tasks' tickets
        # (2026-09-19). Those PRs just wait; the `ok` branch above deploys them by itself
        # as soon as any later build containing them is green.
        own = next((x for x in failed if x[0] == msha), None)
        if own:
            reds.append((own[0], own[1], where, sorted(ids)))
        elif failed and not running:
            notes.append(f"{where}: merged and green is pending; staging is red at {failed[-1][0][:10]}, "
                         f"a later commit that is not this PR. Its tickets move on the next green build.")
        elif running or failed:
            notes.append(f"{where}: staging build running for {(running or failed)[-1][0][:10]}")
        elif now() - merged_at > datetime.timedelta(minutes=NO_BUILD_AFTER_MIN):
            act(f"nobuild-pr{n}", "NO_BUILD", f"{where} merged {iso(merged_at)} and no {ctx.ci().kind} run on "
                f"`{ctx.branch}` contains it yet", "Tell Van in one line (the check may be off). Ack.")
        else:
            notes.append(f"{where}: merged, waiting for {ctx.ci().kind}")

    # ---- staging is red on a commit no PR on this base accounts for (direct push, other team)
    greens = [c for c, d in commits.items() if d["status"] == "ok"]
    for c, d in sorted(((c, d) for c, d in commits.items()
                        if d["status"] == "failed" and c not in pr_merges
                        and (parse_t(d["at"]) or now()) >= since), key=lambda x: x[1]["at"]):
        if any(ctx.is_ancestor(c, g) for g in greens):
            continue        # a later build containing it is green, so staging is no longer red on it
        reds.append((c, d, f"commit {c[:10]} on `{ctx.branch}` (pushed with no PR on this base)", []))

    # Staging is one environment, so it is red once. Several un-green commits in a row are
    # one outage (usually a fix attempt that did not take), and raising a BUILD_FAILED for
    # each would file several bug tickets and spawn several VanDevs at the same breakage.
    # Act on the newest; the rest are history and become notes.
    reds.sort(key=lambda x: x[1]["at"])
    for i, (c, d, where, ids) in enumerate(reds):
        if i == len(reds) - 1:
            build_failed(c, d, where, ids)
        else:
            notes.append(f"{where}: build of {c[:10]} also failed, superseded by {reds[-1][0][:10]}")

    # ---- tracker: rejected by QA, features completed
    for tid, t in (tasks.items() if watching else []):
        st = stat(tid)
        if st in REJECTED:
            upd = t.get("updated") or ""
            aid = f"rejected-{tid}-{upd}"
            if aid in state["acked"]:
                continue
            comments = []
            try:
                comments = ctx.tracker().comments(tid, 3)
            except Exception as e:  # noqa: BLE001
                errors.append(f"tracker comments {tid}: {e}")
            slug, title = title_of.get(tid, (None, t.get("title")))
            branch_hint = f"bug/{slug}--{tid}" if slug else f"bug/{tid}"
            act(aid, "REJECTED", f"QA rejected ticket '{title}' ({t.get('url')})",
                f"Tell Van in one line. Spawn VanPM to claim it (--claim moves it to `in progress`), then VanDev fixes "
                f"it on branch `{branch_hint}` using QA's comments below; the PR body must contain the ticket URL. "
                f"Normal flow after that; it returns to `qa` when the fix is on staging. Ack after VanDev started.",
                ticket={"id": tid, "spec": slug and f"{ctx.specs}/{slug}.md", "title": title}, comments=comments)
    for slug, (mpath, m) in markers(ctx, include_done=False).items():
        ids = [v["id"] for k, v in m.items() if not k.startswith("_") and isinstance(v, dict)]
        if watching and tasks and ids and all(stat(i) in CLOSED for i in ids) and ctx.done and any(stat(i) == ctx.done.lower() for i in ids):
            act(f"complete-{slug}", "FEATURE_COMPLETE", f"every ticket of `{slug}` is complete",
                "Spawn VanPM: archive the feature (project-orchestration step 6: move spec + marker to specs/_done/, "
                "update _planned-data.md, run spec_index.py). Run `worktree.py <slug> sweep`. Append one line to "
                "MEMORY.md and post one line in the channel. Ack after the spec is in _done/.", spec=f"{ctx.specs}/{slug}.md")

    # ---- worktrees
    ledger = os.path.join(ctx.art, "worktrees.jsonl")
    if os.path.isfile(ledger):
        for line in open(ledger):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            born = parse_t(r.get("created_at"))
            if r.get("status") in ("active", "kept") and born and now() - born > datetime.timedelta(days=STALE_DAYS):
                act(f"stale-{r['branch']}-{now():%Y%m%d}", "STALE_WORKTREE",
                    f"worktree `{r['branch']}` ({r.get('worktree')}) is {(now() - born).days} days old, status {r['status']}: "
                    f"{(r.get('events') or ['?'])[-1][:200]}",
                    "Tell Van what it holds (never delete it yourself). Ack.")
    last = parse_t(state.get("last_sweep"))
    if not last or now() - last > datetime.timedelta(hours=24):
        act(f"sweep-{now():%Y%m%d}", "SWEEP_DUE", "daily worktree sweep",
            f"Run `python3 {TOOLS}/worktree.py {ctx.slug} sweep` (removes only merged + clean worktrees). "
            "Relay any KEPT/UNMANAGED/PRIMARY line to Van. Ack.")

    # ---- daily architecture lint (reported once, from the first project only: the check is global)
    projects = sorted(d for d in os.listdir(f"{WORKSPACE}/projects") if not d.startswith("_")
                      and os.path.isdir(f"{WORKSPACE}/projects/{d}"))
    if projects and ctx.slug == projects[0]:
        aid = f"lint-{now():%Y%m%d}"
        if aid not in state["acked"]:
            rc, out, err = run([sys.executable, f"{WORKSPACE}/_tools/lint_workspace.py", "--json"])
            try:
                fixes = [r for r in json.loads(out) if r["status"] == "FIX"]
            except ValueError:
                fixes = [{"area": "lint", "message": f"lint_workspace.py failed: {(err or out)[:300]}", "fix": ""}]
            if fixes:
                act(aid, "LINT", f"architecture lint found {len(fixes)} thing(s) to fix",
                    "Post the lines below in ONE message in the channel, prefixed 'Daily lint:'. Never delete, move or "
                    "edit files from a heartbeat; Van or a Claude Code session fixes them. Ack after posting.",
                    lint=[f"[{r['area']}] {r['message'].splitlines()[0]} -> {r['fix']}" for r in fixes])

    for x in actions:
        state["pending"][x["id"]] = {k: v for k, v in x.items() if k == "feedback_ids"}
    save()
    if a.json:
        print(json.dumps({"slug": ctx.slug, "watch_since": iso(since), "actions": actions, "notes": notes,
                          "errors": errors}, indent=1)); return
    print(f"delivery_watch {ctx.slug}  (watching merges since {iso(since)})")
    for e in errors:
        print(f"ERROR   {e}")
    for x in actions:
        print(f"\nACTION  {x['id']}  [{x['kind']}]\n  {x['summary']}\n  do: {x['do']}")
        for k in ("tickets", "ticket", "feedback", "comments", "lint"):
            if x.get(k):
                print(f"  {k}: {json.dumps(x[k], ensure_ascii=False)[:1500]}")
        if x.get("command"):
            print(f"  command: {x['command']}")
        print(f"  ack: python3 {os.path.abspath(__file__)} {ctx.slug} --ack {x['id']}")
    for n in notes:
        print(f"note    {n}")
    if not actions:
        print("NO_ACTIONS")


if __name__ == "__main__":
    main()
