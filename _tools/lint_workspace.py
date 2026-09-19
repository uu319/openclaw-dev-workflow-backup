#!/usr/bin/env python3
"""Architecture linter for the OpenClaw dev factory. READ-ONLY: prints OK / FIX lines, changes nothing.

Usage:
  lint_workspace.py            # human report, exit 1 if anything needs fixing
  lint_workspace.py --json     # machine-readable

What it checks (the MANIFEST below is the architecture; anything not in it is clutter):
  1. Framework files: every path under ~/.openclaw/workspace matches an allowed pattern.
  2. Required files exist (agent bootstrap files, shared tools, skills, template).
  3. Per project: PROJECT_CONTEXT.md validates, artifacts layout is the standard one, no stray files.
  4. Code roots: ~/projects holds only <slug> checkouts + .worktrees/<slug>/; primary checkouts are clean
     and on the default branch; no OpenClaw managed worktrees of the settings repo.
  5. openclaw.json desired state: main deny [], loop detection on, heartbeat isolated, no specialist bots,
     specialist deny lists, MCP servers per project, only the intended skills enabled.
  6. Host: /tmp size, gateway TMPDIR/PATH, gcloud + gh on the gateway PATH, backup sprawl.
Standard library only. Run it from the orchestrator (read-only shell) or by hand.
"""
import fnmatch, glob, importlib.util, json, os, re, subprocess, sys

HOME = "/home/openclaw"
OC = f"{HOME}/.openclaw"
WS = f"{OC}/workspace"
CODE = f"{HOME}/projects"
AGENTS = ["project-manager", "developer", "qa-engineer", "code-reviewer"]
SHARED_TOOLS = ["clickup_mcp.py", "delivery_watch.py", "figma_mcp.py", "gcloud_env.py", "git_env.py",
                "spec_index.py", "validate_context.py", "worktree.py"]
PM_SCRIPTS = ["clickup_push.py", "clickup_scan.py", "clickup_status.py"]

# ---- MANIFEST: allowed paths, relative to the workspace. Globs; ** matches any depth. ----
ALLOWED = [
    "AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md", "MEMORY.md", "TOOLS.md", ".gitignore",
    "DREAMS.md",                       # written by OpenClaw's dreaming feature (see Decision G)
    "memory/**", ".clawhub/**", "media/**", ".git/**",
    "_tools/validate_team.py", "_tools/lint_workspace.py", "_tools/framework_offbox.py",
    "docs/*.md",                       # the architecture doc and the guide (~/OPENCLAW_*.md are symlinks here)
    "skills/project-onboarding/**", "skills/project-orchestration/**",
    "credentials/gcp/*.json",
    "projects/_template/**",
    *[f"projects/_tools/{t}" for t in SHARED_TOOLS],
    "projects/*/PROJECT_CONTEXT.md",
    "projects/*/artifacts/specs/**", "projects/*/artifacts/patches/**", "projects/*/artifacts/reviews/**",
    "projects/*/artifacts/qa/**", "projects/*/artifacts/runs/**",
    "projects/*/artifacts/worktrees.jsonl", "projects/*/artifacts/worktrees.jsonl.lock",
    "projects/*/artifacts/prs.md", "projects/*/artifacts/delivery_state.json",
]
for a in AGENTS:
    ALLOWED += [f"{a}/AGENTS.md", f"{a}/SOUL.md", f"{a}/USER.md", f"{a}/IDENTITY.md", f"{a}/DREAMS.md",
                f"{a}/memory/**", f"{a}/media/**", f"{a}/.git/**", f"{a}/.gitignore"]
SHARED_SKILLS_DIR = os.path.expanduser("~/.openclaw/skills")
SHARED_SKILLS = ["worktree-lifecycle"]   # shared by all agents; each one is its own git repo
ALLOWED += ["project-manager/skills/feature-breakdown/**", "developer/skills/agy-coding/**",
            "developer/skills/coding-delegation/**", "code-reviewer/skills/code-review/**",
            "qa-engineer/skills/qa-verification/**"]
REQUIRED = ["AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md", "MEMORY.md",
            "_tools/validate_team.py", "skills/project-onboarding/SKILL.md", "skills/project-orchestration/SKILL.md",
            "projects/_template/PROJECT_CONTEXT.md", "projects/_template/specs/_planned-data.md",
            *[f"projects/_tools/{t}" for t in SHARED_TOOLS],
            *[f"{a}/AGENTS.md" for a in AGENTS],
            *[f"project-manager/skills/feature-breakdown/scripts/{s}" for s in PM_SCRIPTS]]
# Token shapes that must never sit in a framework file (checked in every repo's working tree, ignored files included,
# except credentials/, which holds the restored GCP key files by design).
TOKEN_RX = (r"ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|pk_[0-9]+_[A-Z0-9]{20,}|figd_[A-Za-z0-9_-]{20,}"
            r"|AIza[0-9A-Za-z_-]{30,}|sk-ant-[A-Za-z0-9_-]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY")


def framework_repos():
    """(name, path) of every framework git repo; the off-box copy uses the same list."""
    out = [("workspace", WS)] + [(a, f"{WS}/{a}") for a in AGENTS]
    return out + [(f"skill-{n}", os.path.join(SHARED_SKILLS_DIR, n)) for n in SHARED_SKILLS]


ARTIFACT_DIRS = ["specs", "specs/_done", "specs/_superseded", "patches", "reviews", "qa", "runs"]

R = []  # (status, area, message, fix)


def ok(area, msg, how=""): R.append(("OK", area, msg, ""))
def fix(area, msg, how=""): R.append(("FIX", area, msg, how))


def allowed(rel):
    parts = rel.split("/")
    for pat in ALLOWED:
        if fnmatch.fnmatch(rel, pat):
            return True
        if pat.endswith("/**"):
            base = pat[:-3]
            if fnmatch.fnmatch(rel, base) or any(fnmatch.fnmatch("/".join(parts[:i]), base) for i in range(1, len(parts))):
                return True
    return False


def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
        return r.returncode, r.stdout.strip()
    except Exception as e:
        return 1, str(e)


def check_framework_files():
    strays, pyc = [], []
    for root, dirs, files in os.walk(WS):
        rel_root = os.path.relpath(root, WS)
        if rel_root.split("/")[0] in (".git",) or "/.git" in rel_root or rel_root.endswith(".git"):
            dirs[:] = []
            continue
        for f in files:
            rel = os.path.normpath(os.path.join(rel_root, f)) if rel_root != "." else f
            if "__pycache__" in rel:
                pyc.append(rel); continue
            if not allowed(rel):
                strays.append(rel)
    for req in REQUIRED:
        if not os.path.exists(f"{WS}/{req}"):
            fix("framework", f"required file missing: {req}", "restore from git / backups or the guide")
    if strays:
        fix("framework", f"{len(strays)} file(s) outside the manifest:\n      " + "\n      ".join(sorted(strays)),
            "move into place (artifacts/, a skill, _tools) or delete; nothing lives outside the manifest")
    else:
        ok("framework", "every workspace file matches the manifest")
    if pyc and not open(f"{WS}/.gitignore").read().count("__pycache__"):
        fix("framework", f"{len(pyc)} __pycache__ file(s) (python bytecode; regenerated on every run)",
            "add __pycache__/ to .gitignore and delete: find ~/.openclaw/workspace -name __pycache__ -type d")
    for skill in glob.glob(f"{WS}/skills/*") + glob.glob(f"{WS}/*/skills/*"):
        rel = os.path.relpath(skill, WS)
        if not allowed(rel + "/SKILL.md"):
            fix("framework", f"skill not in the manifest: {rel}", "delete it, or add it to the manifest with an owner")
    # git hygiene: the framework = the main workspace repo + one repo per agent workspace (each has its
    # own .git; the main .gitignore excludes them). An uncommitted change in any of them is a FIX.
    # The shared skills dir (~/.openclaw/skills, visible to every agent) holds only SHARED_SKILLS; each is its own repo.
    for d in sorted(glob.glob(os.path.join(SHARED_SKILLS_DIR, "*"))):
        if os.path.basename(d) not in SHARED_SKILLS:
            fix("framework", f"shared skill not in the manifest: {d} (loads for every agent)",
                "Van decides: add it to SHARED_SKILLS with an owner, or move it out of ~/.openclaw/skills")
    for rel in ["."] + AGENTS + [os.path.relpath(os.path.join(SHARED_SKILLS_DIR, n), WS) for n in SHARED_SKILLS]:
        repo = os.path.normpath(os.path.join(WS, rel))
        name = "main" if rel == "." else (f"shared skill {os.path.basename(repo)}" if rel.startswith("..") else rel)
        if not os.path.isdir(os.path.join(repo, ".git")):
            fix("framework", f"{name} workspace is not a git repo", f"cd {repo} && git init && git add -A && git commit -m baseline")
            continue
        rc, out = run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=repo)
        lines = [l for l in out.splitlines() if l and not re.search(r"(^|/)(memory|media|__pycache__)/|DREAMS\.md", l)]
        # Agent artifacts (project layer) change on every run and agents never commit: counted, not a FIX.
        arts = [l for l in lines if re.search(r"\bprojects/[^/]+/artifacts/", l)]
        lines = [l for l in lines if l not in arts]
        if arts:
            ok("project", f"{name} repo: {len(arts)} agent artifact change(s) not committed yet (commit them in a Claude Code session)")
        if lines:
            fix("framework", f"{name} repo has {len(lines)} uncommitted/untracked path(s) (first 15):\n      "
                + "\n      ".join(lines[:15]), f"cd {repo} && git add -A && git commit -m '<what changed>'")
        else:
            ok("framework", f"{name} repo is clean (git status empty)")
        rc, out = run(["git", "grep", "-I", "-l", "-E", "--untracked", "--no-exclude-standard", TOKEN_RX, "--",
                       ".", ":(exclude)credentials/**", ":(exclude).git/**"], cwd=repo)
        hits = [l for l in out.splitlines() if l.strip()] if rc == 0 else []
        if hits:
            fix("framework", f"{name}: token-shaped string in {len(hits)} file(s): {', '.join(hits[:5])}",
                "remove the file (git rm), rotate that credential, tell Van; values live only in the vault")
        rc, out = run(["git", "remote", "-v"], cwd=repo)
        if out.strip():
            fix("framework", f"{name} repo has a remote:\n      {out}", f"git -C {repo} remote remove <name>; framework repos never push from an agent")


def check_offbox():
    """Decision I: every framework repo has a copy off this box (refs/offbox/<name> = last pushed HEAD)."""
    never, behind = [], []
    for name, repo in framework_repos():
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        rc, _ = run(["git", "rev-parse", "--verify", "--quiet", f"refs/offbox/{name}"], cwd=repo)
        if rc != 0:
            never.append(name); continue
        rc, n = run(["git", "rev-list", "--count", "HEAD", f"^refs/offbox/{name}"], cwd=repo)
        if rc == 0 and n.isdigit() and int(n):
            behind.append(f"{name} +{n}")
    if never:
        fix("framework", f"no off-box copy yet for: {', '.join(never)} (Decision I)",
            "Van, from a real terminal: python3 ~/.openclaw/workspace/_tools/framework_offbox.py push <private repo url>")
    else:
        ok("framework", "off-box copy exists for every framework repo" + (f"; commits since: {', '.join(behind)}" if behind else ""))


def load_validator():
    spec = importlib.util.spec_from_file_location("vc", f"{WS}/projects/_tools/validate_context.py")
    vc = importlib.util.module_from_spec(spec); spec.loader.exec_module(vc)
    return vc


def projects():
    return sorted(d for d in os.listdir(f"{WS}/projects") if not d.startswith("_") and os.path.isdir(f"{WS}/projects/{d}"))


def check_projects():
    vc = load_validator()
    slugs = projects()
    if not slugs:
        ok("projects", "no projects onboarded"); return {}
    ctxs = {}
    for slug in slugs:
        ctx = f"{WS}/projects/{slug}/PROJECT_CONTEXT.md"
        if not os.path.isfile(ctx):
            fix(f"project:{slug}", "PROJECT_CONTEXT.md missing", "run the project-onboarding skill"); continue
        fields, errors = vc.parse(ctx)
        ctxs[slug] = fields
        if errors:
            fix(f"project:{slug}", "PROJECT_CONTEXT.md invalid: " + "; ".join(errors), "fix the file, not the tooling")
        else:
            ok(f"project:{slug}", "PROJECT_CONTEXT.md VALID")
        art = f"{WS}/projects/{slug}/artifacts"
        missing = [d for d in ARTIFACT_DIRS if not os.path.isdir(f"{art}/{d}")]
        if missing:
            fix(f"project:{slug}", f"artifact dirs missing: {missing}", f"mkdir -p {art}/{{{','.join(missing)}}}")
        if not os.path.isfile(f"{art}/specs/_planned-data.md"):
            fix(f"project:{slug}", "specs/_planned-data.md missing", "copy from projects/_template/specs/ (onboarding step 3)")
        loose = [f for f in os.listdir(f"{WS}/projects/{slug}") if f not in ("PROJECT_CONTEXT.md", "artifacts")]
        if loose:
            fix(f"project:{slug}", f"stray files in the project dir: {loose}", "delete; only PROJECT_CONTEXT.md and artifacts/ live here")
    return ctxs


def check_code_roots(ctxs):
    if not os.path.isdir(CODE):
        fix("code", f"{CODE} missing", "mkdir -p ~/projects"); return
    slugs = set(ctxs)
    for entry in sorted(os.listdir(CODE)):
        p = f"{CODE}/{entry}"
        if entry == ".worktrees":
            for wslug in os.listdir(p):
                if wslug not in slugs:
                    fix("code", f".worktrees/{wslug} belongs to no onboarded project", "delete after checking nothing is unpushed")
            continue
        if entry not in slugs:
            fix("code", f"~/projects/{entry} is not an onboarded project's Code (CWD)", "delete (old agy worktrees, logs, prompts) or onboard it")
    for slug, f in ctxs.items():
        cwd = f.get("code_cwd", "")
        if not os.path.isdir(f"{cwd}/.git"):
            fix(f"code:{slug}", f"Code (CWD) {cwd} is not a git checkout", "clone it (onboarding step 3)"); continue
        rc, st = run(["git", "status", "--porcelain"], cwd=cwd)
        rc2, br = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd)
        want = f.get("default_branch")
        if st:
            fix(f"code:{slug}", f"primary checkout is dirty ({len(st.splitlines())} paths); agents must never edit it",
                "hand to VanDev: move the work to a worktree branch or discard it")
        elif want and br != want:
            fix(f"code:{slug}", f"primary checkout is on `{br}`, expected `{want}`", f"git -C {cwd} checkout {want} && git pull --ff-only")
        else:
            ok(f"code:{slug}", f"primary checkout clean on `{br}`")
    managed = f"{OC}/worktrees"
    if os.path.isdir(managed):
        n = sum(len(glob.glob(f"{d}/*")) for d in glob.glob(f"{managed}/*") if os.path.isdir(d))
        if n:
            fix("code", f"{n} OpenClaw managed worktree dir(s) under ~/.openclaw/worktrees (settings-repo copies, never code)",
                "openclaw worktrees list; openclaw worktrees remove <id> for each; then openclaw worktrees gc")
        else:
            ok("code", "no OpenClaw managed worktrees")


def check_config(ctxs):
    try:
        c = json.load(open(f"{OC}/openclaw.json"))
    except Exception as e:
        fix("config", f"cannot read openclaw.json: {e}"); return
    ent = c.get("agents", {}).get("entries", {})
    main = ent.get("main", {})
    deny = main.get("tools", {}).get("deny", [])
    (ok if deny == [] else fix)("config", f"main tools.deny = {deny}" + ("" if deny == [] else " (inherited by every spawned session)"),
                                "" if deny == [] else "patch: {agents:{entries:{main:{tools:{deny:[]}}}}}")
    want_allow = set(AGENTS)
    have = set(main.get("subagents", {}).get("allowAgents", []))
    (ok if have == want_allow else fix)("config", f"main.subagents.allowAgents = {sorted(have)}", "" if have == want_allow else f"set to {sorted(want_allow)}")
    for a in AGENTS:
        sub = ent.get(a, {}).get("subagents", {}).get("allowAgents", None)
        if sub not in ([], None):
            fix("config", f"{a} may spawn agents ({sub}); specialists spawn nothing", f"set agents.entries.{a}.subagents.allowAgents = []")
    ld = c.get("tools", {}).get("loopDetection", {}).get("enabled")
    (ok if ld is True else fix)("config", f"tools.loopDetection.enabled = {ld}", "" if ld else "patch: {tools:{loopDetection:{enabled:true}}}")
    hb = c.get("agents", {}).get("defaults", {}).get("heartbeat", {})
    (ok if hb.get("isolatedSession") else fix)("config", f"heartbeat.isolatedSession = {hb.get('isolatedSession')}", "" if hb.get("isolatedSession") else "patch: {agents:{defaults:{heartbeat:{isolatedSession:true}}}}")
    for b in c.get("bindings", []):
        if b.get("agentId") != "main":
            fix("config", f"binding routes a channel to `{b.get('agentId')}`: {b}", "remove; only main is bound to chat")
    for acc, v in c.get("channels", {}).get("discord", {}).get("accounts", {}).items():
        if acc != "main" and v.get("enabled", True):
            fix("config", f"discord account `{acc}` is enabled (specialist bot)", f"patch: {{channels:{{discord:{{accounts:{{{acc}:{{enabled:false}}}}}}}}}}")
    dev_deny = ent.get("developer", {}).get("tools", {}).get("deny", [])
    (ok if "tracker-*" in dev_deny else fix)("config", f"developer deny = {dev_deny}", "" if "tracker-*" in dev_deny else "add tracker-*")
    pm_deny = ent.get("project-manager", {}).get("tools", {}).get("deny", [])
    need = {"tracker-*__clickup_update_task", "tracker-*__clickup_create_task"}
    (ok if need <= set(pm_deny) else fix)("config", f"project-manager deny = {pm_deny}", "" if need <= set(pm_deny) else "add the two tracker write tools (writes go through scripts)")
    for a in ("qa-engineer", "code-reviewer"):
        d = set(ent.get(a, {}).get("tools", {}).get("deny", []))
        (ok if {"figma-*", "tracker-*"} <= d else fix)("config", f"{a} deny = {sorted(d)}", "" if {"figma-*", "tracker-*"} <= d else "add figma-* and tracker-*")
    servers = set(c.get("mcp", {}).get("servers", {}).keys())
    for slug, f in ctxs.items():
        want = {f"tracker-{slug}"} | ({f"figma-{slug}"} if f.get("figma_mcp_server") else set())
        missing = want - servers
        (ok if not missing else fix)("config", f"MCP servers for {slug}: {sorted(want & servers)}", "" if not missing else f"openclaw mcp set {sorted(missing)} (onboarding 4b/4c)")
    orphan = [s for s in servers if not any(s.endswith(f"-{slug}") for slug in ctxs)]
    if orphan:
        fix("config", f"MCP servers for no onboarded project: {orphan}", "openclaw mcp remove <name>")
    enabled = [k for k, v in c.get("skills", {}).get("entries", {}).items() if v.get("enabled")]
    extra = set(enabled) - {"coding-agent"}
    (ok if not extra else fix)("config", f"enabled bundled skills = {enabled}", "" if not extra else "disable everything but coding-agent")
    ws = c.get("skills", {}).get("workshop", {})
    if ws.get("approvalPolicy") != "pending" or ws.get("autonomous", {}).get("mode") != "propose":
        fix("config", f"skills.workshop = {ws}", "set autonomous.mode=propose, approvalPolicy=pending")
    fb = c.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
    (ok if len(fb) >= 2 else fix)("config", f"model fallbacks = {fb}", "" if len(fb) >= 2 else "need >= 2 fallbacks on a different provider")


def check_host():
    rc, out = run(["df", "-h", "/tmp"])
    line = out.splitlines()[-1] if out else ""
    if line.startswith("tmpfs"):
        size = line.split()[1]
        gb = float(size[:-1]) / (1024 if size.endswith("M") else 1) if size[-1] in "MG" else 99
        (ok if gb <= 1.0 else fix)("host", f"/tmp is tmpfs sized {size}", "" if gb <= 1.0 else "cap at 1G as root (OPENCLAW_ARCHITECTURE.md step 4)")
    else:
        ok("host", "/tmp is on disk")
    rc, pid = run(["systemctl", "--user", "show", "-p", "MainPID", "--value", "openclaw-gateway.service"])
    if pid.strip().isdigit() and pid.strip() != "0":
        try:
            env = open(f"/proc/{pid.strip()}/environ", "rb").read().decode(errors="replace").split("\0")
            kv = dict(e.split("=", 1) for e in env if "=" in e)
            tmp = kv.get("TMPDIR", "")
            (ok if tmp.startswith(f"{HOME}/.cache") else fix)("host", f"gateway TMPDIR = {tmp or '(unset -> /tmp)'}", "" if tmp.startswith(f"{HOME}/.cache") else "systemd drop-in tmpdir.conf (guide 4.2)")
            path = kv.get("PATH", "")
            (ok if f"{HOME}/.local/bin" in path else fix)("host", "gateway PATH contains ~/.local/bin", "" if f"{HOME}/.local/bin" in path else "gcloud/gh symlinks unreachable (guide 3.2)")
        except Exception as e:
            fix("host", f"cannot read gateway environ: {e}")
    else:
        fix("host", "gateway not running (MainPID 0)", "systemctl --user start openclaw-gateway.service")
    for b in ("gcloud", "gh"):
        (ok if os.path.exists(f"{HOME}/.local/bin/{b}") else fix)("host", f"~/.local/bin/{b} present", "" if os.path.exists(f"{HOME}/.local/bin/{b}") else f"symlink {b} into ~/.local/bin (guide 3.2)")
    baks = glob.glob(f"{OC}/openclaw.json.clobbered*") + glob.glob(f"{OC}/openclaw.tmp.json")   # .bak..bak.4 is OpenClaw's own ring: allowed
    if baks:
        fix("host", f"{len(baks)} leftover openclaw.json.clobbered*/openclaw.tmp.json file(s)", "move to ~/.openclaw/backups/config-history/ (the .bak ring is OpenClaw's own and stays)")
    cfg = [f for f in glob.glob(f"{OC}/backups/**/openclaw.json*", recursive=True) if os.path.isfile(f)]
    (ok if len(cfg) <= 5 else fix)("host", f"{len(cfg)} openclaw.json backup copies in ~/.openclaw/backups (Decision J: last 5)",
                                   "" if len(cfg) <= 5 else "delete all but the 5 newest openclaw.json.* copies")
    n = len(glob.glob(f"{OC}/backups/*"))
    (ok if n <= 10 else fix)("host", f"{n} entries in ~/.openclaw/backups", "" if n <= 10 else "keep the last 5 config backups + one dated dir per incident; delete the rest (they are 30 MB+)")
    props = glob.glob(f"{OC}/skill-workshop/proposals/*")
    if props:
        fix("host", f"{len(props)} pending skill-workshop proposal(s)", "review weekly: openclaw skills workshop list; delete the ones you will not adopt")


def main():
    as_json = "--json" in sys.argv
    check_framework_files()
    check_offbox()
    ctxs = check_projects()
    check_code_roots(ctxs)
    check_config(ctxs)
    check_host()
    fixes = [r for r in R if r[0] == "FIX"]
    if as_json:
        print(json.dumps([dict(status=s, area=a, message=m, fix=f) for s, a, m, f in R], indent=1))
    else:
        for s, a, m, f in R:
            print(f"{s:3} [{a}] {m}" + (f"\n      -> {f}" if f else ""))
        print(f"\n{len(R) - len(fixes)} OK, {len(fixes)} FIX")
    sys.exit(1 if fixes else 0)


if __name__ == "__main__":
    main()
