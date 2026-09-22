# OpenClaw Fresh Setup — Development Factory

**Version:** 1.7 · **Written:** 2026-09-17 · **Revised:** 2026-09-22 (1.7: the design reaches the code — Figma assets and tokens, not just screenshots; VanReviewer gains Figma read access and the fidelity check; 1.6: development-only + pluggable tracker/CI; 1.5: §12.5f delivery watcher stall; 1.4: aligned with the architecture doc) · **For:** Van (van@symph.co)
> **Architecture and self-fix runbook (2026-09-20):** `~/OPENCLAW_ARCHITECTURE.md` **v2.7** defines the layers, the file manifest, the per-project Flow profile and toolchain block, and the ordered self-fix steps; `~/.openclaw/workspace/_tools/lint_workspace.py` checks this box against it. When that document and this guide disagree, the architecture document wins.

**Target OpenClaw version:** 2026.9.4 or later (every config key below was checked against
`/usr/lib/node_modules/openclaw/docs` on that version; re-check keys if you install a newer one).

This document is the complete instruction set for standing up a **new** OpenClaw instance that does
one thing: **software development delivery**, project by project, with isolated per-project
credentials. Nothing else (no workflow generator, no email/calendar/weather automations, no
"general assistant" features). Everything in here comes from three weeks of running the previous
instance and the incidents it produced. Section 12 (Learnings) is the part that matters most; the
rest of the document is those learnings turned into a setup.

**What changed in 1.6 (2026-09-20):**
- **Development only** (Decision P). The setup no longer offers general-assistant work. `AGENTS.md`
  routing step 4 says "nobody owns it" instead of "handle it yourself if it is general assistant work";
  `SOUL.md` was stock OpenClaw boilerplate and is now VanOpenClaw's own; the **active** USER.md
  directive "act as Van's main agent, not a dev-only orchestrator" is superseded. Config enforces it
  too: `skills.allowBundled` (28 ready skills → 9), non-development plugins removed. (5.6, 7.2)
- **The tracker is a provider** (Decision Q): `clickup | jira | linear | none`, behind
  `projects/_tools/trackers/`. Fields are vendor-neutral (`Tracker`, `Tracker Board ID`,
  `Tracker Board name`, `Tracker MCP server`, `Tracker Base URL` for Jira); the old ClickUp labels are
  still read. `none` is a real answer. `clickup_mcp.py` → `tracker_mcp.py` with neutral tool names
  (`tracker_get_task`/`tracker_create_task`/`tracker_update_task`), so the PM deny list and the linter
  no longer name a vendor. PM scripts renamed `tracker_push/status/scan.py`. (6, 9.1, 9.2, 9.4, 9.5, 10)
- **CI is a provider** (Decision R): `cloud-build | github-actions | none`, behind
  `projects/_tools/ci/`. `Deploy triggers` → `Deploy checks`. (9.4, 10)
- **All trackers (2026-09-21):** `tracker_push.py` (spec → tickets) runs on ClickUp, Jira and Linear;
  it refuses other trackers and names the alternative. Status reads/writes work everywhere.
- **Bug:** the "`## Stack` is unfilled" check never worked - `\s*[^<\n]` backtracks so the space after
  the colon satisfied it. Every unfilled template passed. Fixed. (9.8)
- `runTimeoutSeconds` was a prompt rule only; with `agents.defaults.subagents.runTimeoutSeconds` unset,
  a spawn that omitted it got **no timeout at all**. Now set to 1800 as a floor. (5.1)

**What changed in 1.4 (2026-09-19 night, aligned with `~/OPENCLAW_ARCHITECTURE.md` v2.3):**
- **Review check at merge time.** VanDev pushes and opens the PR right after a lane commit; VanReviewer reviews on the
  PR and runs `git_env.py <slug> --review-status <pr>`, which sets the commit status `openclaw/review` on the PR head
  (only when a saved review file names that exact SHA). Main checks that status is green before calling a PR ready;
  a ruleset that would make GitHub enforce it is **Decision N: not enabled for now**. The old PR-create review gate is gone. (5.4 note, 7.5, 8.1, 9.4, 12.5e)
- **Flow profile per project** (`## Flow` in PROJECT_CONTEXT): stages, ticket source, assignee filter, branch model,
  PR base, status map. Scripts use canonical statuses (`todo doing staged rejected done cancelled hold`). (8.1, 9.1, 10)
- Section 10 is now a copy of the real template (it had drifted both ways); layout, tool list, watcher actions,
  heartbeat prompt and skill names match the box; the shared `worktree-lifecycle` skill is its own git repo.
- Superseded text in 12.5b/12.5c/12.5d is marked, not deleted (it is history).
- **Security (found 2026-09-19 night):** an agent-written `specs/_figma/fetch.py` held the live fms-studio Figma token in
  the framework repo since 09-17 (also in agent transcripts, so it reached the model provider): file removed, token to be
  rotated. The linter now greps every framework file for token shapes. `~/Backups/openclaw-git` history holds plaintext
  vault rows up to the 2026-09-19 09:30 run: never push it; pull it to your own machine (architecture §7 phase C).
- Design docs live in the framework repo (`~/.openclaw/workspace/docs/`, `~/OPENCLAW_*.md` are symlinks);
  `_tools/framework_offbox.py` makes the off-box copy (Decision I).

**What changed in 1.3 (2026-09-19 evening):** decisions closed (Gemini stays, agy stays, Discord + Telegram,
active-memory and dreaming off, skill-creator removed); `/tmp` cap is 1G; cleanup done on the old box. The architecture,
manifest and self-fix runbook live in `~/OPENCLAW_ARCHITECTURE.md`.

**What changed in 1.2 (2026-09-19 workflow audit + live test, details in 12.5c/12.5d):**
- **ClickUp `qa` = deployed to staging.** `in progress` covers all internal work (VanDev, VanReviewer, VanQA,
  PR, PR feedback). A read-only **delivery watcher** (`delivery_watch.py`) run by the heartbeat every 15 min moves
  merged tickets to `qa` only when every Cloud Build of a commit containing the merge succeeded; external QA sets
  `complete` or `rejected`. (5.10, 8.1, 9.4, 10)
- **Enforced, not prompted:** `git_env.py` refuses every merge, and refuses a PR base other than the Default branch (1.4: the Flow PR base). VanPM's tracker MCP write tools are denied (reads only; writes through its scripts). (5.4, 9.4)
- **Heartbeat in an isolated session** (it revived an old task from main's history otherwise), reporting to the
  project's Discord channel. (5.10)
- **Branch flow:** one branch per feature, lanes one at a time; VanDev pushes the task branch and opens the PR immediately so VanReviewer can review natively on GitHub; `worktree.py create` refuses a branch another agent holds. (9.7)
- **Approval silence is a NO** (`ask_user` timeouts say "proceed with best judgment"). No agent merges. (7.2)
- Secrets: never list them (the PM skill told VanPM to, and it printed the ClickUp token); backups with
  `--exclude-secrets`. (4.4, 6)

**What changed in 1.1 (2026-09-18/19 fixes on the old box, now folded in):**
- Tool-policy inheritance: any `tools.deny` on `main` is inherited by every session it spawns. The
  `exec` deny took the shell away from VanDev; the remaining `figma-*`/`tracker-*` deny was verified on
  2026-09-19 to take Figma and the tracker away from spawned VanPM too. **Main now has an empty deny
  list**; the orchestrator lock is prompt-level. (Sections 2.3, 5.3, 12.2)
- Worktrees: OpenClaw managed worktrees (`sessions_spawn … worktree: true`) can only copy agent
  workspaces, never a project repo. Replaced by `projects/_tools/worktree.py` + the shared
  `worktree-lifecycle` skill: one task = one branch = one worktree = one PR. (9.7)
- GitHub API per project: `gh` installed (no login), `git_env.py <slug> -- gh …` with a repo-scoped PAT,
  `GitHub Repo` + `GitHub Token` fields in the context file. (9.4, 10)
- The coding agent writes code; **VanDev itself runs git, gh, builds, tests, gcloud**. Never a script
  handed to a worker, never a `/approve` request for a shell command. (7.4, 12.4)
- `tools.loopDetection.enabled: true` applied and a second loop type (degenerate model loop on an
  oversized session) documented with its fix (`/stop` then `/new`). (5.2, 12.5)
- Tracker launcher fixed to read PROJECT_CONTEXT + vault like the other launchers. (9.4)
- gcloud on the gateway PATH via symlinks; `openclaw secrets store list` prints env-kind values in
  plaintext (do not use it to verify); secrets must be stored from a real SSH terminal. (3.2, 6)

---

## 0. How to use this document

1. Read Section 1 (Goal) and Section 2 (Principles) once. They explain *why* the setup looks the way it does.
2. Do Sections 3 → 8 in order on the fresh box. Each step has a verification line. Do not skip a verification.
3. Onboard the first project with Section 9.
4. Run the smoke test in Section 11 before letting anyone use it.
5. Keep Section 12 open whenever something breaks. Most failures are already listed there with the fix.

Conventions in this document:
- `<slug>` = project slug, lowercase with hyphens (`fms-studio`).
- `<SLUGUPPER>` = slug uppercased with hyphens removed (`FMSSTUDIO`). Used in secret names.
- `~` = `/home/openclaw`. OpenClaw state is `~/.openclaw`. Agent workspaces are under `~/.openclaw/workspace`.
- "Van runs" = a command that must be run by a human in a **real SSH terminal** (secrets, config writes,
  anything the auto-mode classifier blocks). Not the chat `!` prefix: `--value-file -` reads stdin, which a
  chat shell does not provide, and the secret is silently stored **empty**. "Agent may run" = safe for an agent.

---

## 1. Goal

Build a team of five agents that takes a feature from a Figma screen or a sentence to a merged PR,
**without any agent ever holding a credential that belongs to another project**, and without the
orchestrator ever doing a specialist's work.

| Agent id | Display name | Job in one line |
|---|---|---|
| `main` | VanOpenClaw (Orchestrator) | Talks to Van, routes, verifies with a read-only shell, never builds or changes anything |
| `project-manager` | VanPM | Figma/request → spec → tickets in the tracker |
| `developer` | VanDev | One lane ticket → branch + PR; a coding agent writes the code, VanDev runs git/gh/builds |
| `code-reviewer` | VanReviewer | PR vs ticket → APPROVED / CHANGES REQUESTED on GitHub + the `openclaw/review` status, design fidelity included |
| `qa-engineer` | VanQA | Feature vs acceptance criteria → PASS/FAIL report with defects |

**How a design becomes code** (the chain is only as strong as its weakest link — it broke at every link
before 2026-09-22, architecture Phase D). VanPM downloads three things from each Figma frame, not one: the
**screenshot** (`specs/_figma/<feature>/<nodeId>.png`, what the screen looks like), the **assets**
(`specs/_figma/<feature>/assets/` + `manifest.json` — the image fills and icon SVGs the code has to ship,
which a screenshot cannot be cut up into), and the **tokens** (exact hexes and font families). Those become a
`## Design fidelity` section on every `[FE]` ticket, which `tracker_push.py` refuses to push without. VanDev
copies the assets into its worktree **before** launching the coding agent and names them in the prompt —
the coding agent has no Figma tools and cannot see a PNG, so anything not in its prompt becomes a placeholder.
VanReviewer then checks the diff actually contains and renders them. A screen with no artwork says so with an
empty manifest; silence is what produced the placeholders.

Every project brings its own:
1. **Project management tool** (ClickUp now; Jira/Linear later) — reached through an MCP server per project.
2. **Figma** — MCP server per project, with that project's Figma API token.
3. **Git** — a per-project SSH deploy key for push and a repo-scoped fine-grained GitHub PAT for the API
   (PRs, checks), never a machine-wide credential. (Decision F if you want PAT-only.)
4. **Cloud** — one GCP service-account JSON per project (per environment), injected per command.
5. **ClickUp API key** — one per project/workspace account, stored under a per-project name.
6. Plus (found necessary in practice): a coding-agent backend the developer delegates code writing to,
   explicit test/install/deploy commands, an E2E runner, a per-task worktree tool, a chat channel for the
   orchestrator only, and a validated `PROJECT_CONTEXT.md` that every agent reads first.

Success looks like: Van says "build the Set Password step from this Figma link" in Discord, and the
result is a spec he approves, tickets in the right ClickUp list, a reviewed and QA'd branch, and a
real PR URL, with every side-effect gated on his "go". Adding project #2 changes **zero** tooling:
one context file, four secrets, two MCP registrations.

---

## 2. Principles (each one is a scar)

1. **One source of truth per project.** IDs, list IDs, secret names, statuses, paths, branch prefixes,
   test/install/deploy commands live only in `projects/<slug>/PROJECT_CONTEXT.md`. Never in USER.md, never
   in a script, never in a prompt. Every tool reads it through one validator. Four copies of one fact, all
   drifting, caused every "wrong list" / "token not found" incident.
2. **No ambient defaults.** No global `GOOGLE_APPLICATION_CREDENTIALS`, no `gcloud config set project`,
   no `gh auth login`, no global git credential, no machine-wide Figma key. A bare `gcloud` must print
   `(unset)`; a bare `gh` must fail. Project #2 must fail loudly, not silently act as project #1.
3. **The orchestrator's lock is a prompt rule, and `main` has an empty `tools.deny`.** `sessions_spawn`
   children inherit the requester's effective tool policy ("each level can further restrict, never grant
   back"). On the old box, denying `exec` on main left every spawned VanDev without a shell (~20 sessions,
   zero commands, endless "/approve this script" requests), and the leftover `figma-*`/`tracker-*` deny was
   found on 2026-09-19 in the spawned VanPM's `inheritedToolDeny`. So main keeps every tool and its
   AGENTS.md says: shell is for read-only verification (`ls`, `git log`, `gh pr view`), nothing that changes
   state, no Figma or tracker calls. Restrictions go on the **specialists**, which spawn nothing.
4. **A specialist's summary is a claim, not evidence.** The orchestrator checks the artifact path, `git log`,
   or `gh pr view` before telling Van anything is done. "VanDev says it used the coding agent" and "VanDev
   used it (log: …, worktree: …)" are different sentences.
5. **Fix with tooling, not with "follow the rules better".** If an agent keeps making a mistake, change the
   tool, validator, or config so the mistake is impossible, then update the prompt.
6. **Artifacts are completion markers.** `specs/`, `patches/`, `reviews/`, `qa/` under Internal Artifacts.
   If it exists, the step is done; resume, don't redo.
7. **Every external side effect waits for Van's explicit yes**: merges (always Van's own), pushes to the default branch,
   ticket writes outside the orchestration status table, messages to other people. Pushing a task branch and opening
   its PR are routine (the review happens on the PR), and nothing reaches the PR base without Van merging.
8. **Never edit `openclaw.json` by hand.** `openclaw config patch --file x.json --dry-run`, read the diff,
   then apply. It hot-reloads. A hand edit once set `tools.allow: ["message"]` and broke every turn.
9. **Platform layer vs project repo.** "Fix our setup" means `~/.openclaw/**`, the host, the gateway.
   A bug found in a project repo gets documented in that project's context file and handed to VanDev as a ticket.
10. **Specialists are spawned, not chatted with.** Only `main` has a chat bot. Direct chat with a specialist
    bot is what produced the 34-minute polling loop with no reply.
11. **One task = one branch = one worktree = one PR; the primary checkout is read-only for agents.**
    Worktrees come only from `projects/_tools/worktree.py <slug> create|finish|sweep|list`, taught by the
    shared `worktree-lifecycle` skill. **Never** spawn with OpenClaw `worktree: true` + a project `cwd`: a
    spawned agent's `cwd` must sit inside an agent workspace, so OpenClaw silently worktrees the *settings*
    repo instead (old box: 24 managed worktrees, zero containing code, while every agent edited the shared
    primary checkout). See 9.7.
12. **The coding agent writes code; the developer agent operates.** git, gh, builds, tests, installs,
    gcloud, log reads are VanDev's own `exec` calls. Wrapping them in a script for a worker (old box: `agy`
    launched just to run `git push` + `gh pr create`) or asking Van to `/approve` a shell command is a
    symptom of a missing tool or a leaked deny, never the design.

---

## 3. Host preparation (Van runs, as root where noted)

### 3.1 Sizing
- 8 GB RAM minimum (the old box: 7.7 GB + 2 GB swap). The gateway idles at ~1.7 GB; each Figma MCP
  server is ~120 MB; a coding-agent run is 0.5–1.5 GB; `npm install` bursts are 0.5–2 GB.
- 4 GB of that was silently eaten by `/tmp` on the old box. See 3.3. This is the single most important host fix.
- Disk: 50 GB+. Node caches, worktrees (each with its own `node_modules` under npm), and repos add up.

### 3.2 Base packages
```bash
# as root
apt-get update && apt-get install -y git curl python3 python3-venv sqlite3 jq build-essential
# Node 24 LTS (the old box ran v24.20.0). Use NodeSource or nvm for the openclaw user; do not use apt's node.
# gcloud SDK: install to /home/openclaw/google-cloud-sdk (NOT /tmp — it was 485 MB of RAM on the old box)
# then put it on the GATEWAY's PATH, not just ~/.bashrc (agent exec shells never read .bashrc):
mkdir -p /home/openclaw/.local/bin
for b in gcloud gsutil bq; do ln -s /home/openclaw/google-cloud-sdk/bin/$b /home/openclaw/.local/bin/$b; done
# gh (GitHub CLI): download gh_<v>_linux_amd64.tar.gz, verify against gh_<v>_checksums.txt,
# unpack to /home/openclaw/.local/opt/gh, symlink /home/openclaw/.local/bin/gh. NEVER run `gh auth login`.
```
**Why the symlinks:** the gcloud installer only edits `~/.bashrc`. The gateway's systemd unit has its own
fixed `PATH` (`/usr/bin:/bin:/usr/local/bin:~/.local/bin:~/.npm-global/bin:~/bin`) and agent `exec` shells
are non-interactive, so they never saw `~/google-cloud-sdk/bin`. On the old box agents said "gcloud not
installed" for days and guessed at deploy failures instead of reading logs. Verify with
`tr '\0' '\n' < /proc/$(systemctl --user show -p MainPID --value openclaw-gateway.service)/environ | grep ^PATH=`.
Install `sqlite3` explicitly. The old box did not have it and every transcript diagnosis had to go through python.

### 3.3 `/tmp` is a RAM disk — fix it before anything else
On Ubuntu/Debian VPS images `/tmp` is often tmpfs sized at half of RAM (a systemd default, nothing in
`/etc/fstab`). OpenClaw's generated systemd unit hardcodes `Environment=TMPDIR=/tmp`, so every `npx`,
`npm`, `nx`, and coding-agent scratch install goes **into RAM**, and `npx` never cleans up when killed.
Result on the old box: 20 orphaned temp dirs, 1.9 GB, in 11 minutes, OOM killer fired three times inside
the gateway, agents "went crazy" (they were being killed mid-sentence).

Check:
```bash
df -h /tmp          # if the Filesystem column says tmpfs, you have the problem
```
Fix (do both):
```bash
# a) as root: shrink the tmpfs so a runaway cannot take the box down
mkdir -p /etc/systemd/system/tmp.mount.d
printf '[Mount]\nOptions=mode=1777,strictatime,nosuid,nodev,size=1G\n' > /etc/systemd/system/tmp.mount.d/size.conf   # 1G: Claude Code sessions keep scratch here too
systemctl daemon-reload && systemctl restart tmp.mount   # or reboot

# b) as openclaw: point the whole gateway process tree at real disk (done again in 4.2 after install)
mkdir -p ~/.cache/openclaw-tmp/node-compile-cache
```
Also add to `~/.bashrc` for the openclaw user (this is for hand-run commands; the gateway gets its own drop-in in 4.2):
```bash
export TMPDIR=$HOME/.cache/openclaw-tmp TMP=$HOME/.cache/openclaw-tmp TEMP=$HOME/.cache/openclaw-tmp
export NODE_COMPILE_CACHE=$HOME/.cache/openclaw-tmp/node-compile-cache
```
Verify: `df -h /tmp` shows 1.0G; `echo $TMPDIR` prints the cache path in a new shell.
Note: `/tmp/openclaw` is OpenClaw's own log directory. Leave it alone when sweeping `/tmp`.

### 3.4 Swap
2 GB swapfile minimum (4 GB on an 8 GB box). Swap is the overflow drawer; it does not fix a RAM leak
but it turns an instant OOM kill into a slow-down you can see coming.
```bash
fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 3.5 User and lingering
```bash
useradd -m -s /bin/bash openclaw            # if not present
loginctl enable-linger openclaw             # so the user systemd unit runs without a login session
```

### 3.6 Directory layout (create now, fill later)
```
/home/openclaw/
├── projects/<slug>/                          # Code (CWD): primary checkout, READ-ONLY for agents, stays on the default branch
├── projects/.worktrees/<slug>/<branch>/      # one worktree per task, made/removed only by worktree.py
├── .openclaw/                                # OpenClaw state (config, agent sqlite)
│   ├── skills/worktree-lifecycle/SKILL.md    # shared skill, visible to every agent; its own git repo (nothing else here)
│   └── workspace/                            # main agent workspace (auto-loads AGENTS/SOUL/USER/IDENTITY/TOOLS/MEMORY.md)
│       ├── AGENTS.md  SOUL.md  USER.md  IDENTITY.md  MEMORY.md
│       ├── skills/project-orchestration/SKILL.md
│       ├── skills/project-onboarding/SKILL.md
│       ├── _tools/validate_team.py, lint_workspace.py, framework_offbox.py   # lint = manifest + desired state; offbox = Decision I
│       ├── docs/OPENCLAW_ARCHITECTURE.md, OPENCLAW_DEV_SETUP.md   # this guide; ~/OPENCLAW_*.md are symlinks
│       ├── credentials/gcp/<slug>.json       # 0600, restored from vault by gcloud_env.py
│       ├── projects/
│       │   ├── _template/PROJECT_CONTEXT.md, specs/_planned-data.md   # THE templates; no copies anywhere else
│       │   ├── _tools/{validate_context,figma_mcp,tracker_mcp,gcloud_env,git_env,worktree,delivery_watch,spec_index}.py
│       │   ├── _tools/trackers/{__init__,clickup,jira,linear}.py   _tools/ci/{__init__,cloud_build,github_actions}.py
│       │   └── <slug>/PROJECT_CONTEXT.md
│       │   └── <slug>/artifacts/{specs,patches,reviews,qa,runs}/ + worktrees.jsonl + prs.md + delivery_state.json
│       ├── project-manager/{AGENTS.md,SOUL.md,USER.md,IDENTITY.md,skills/feature-breakdown/}
│       ├── developer/{AGENTS.md,SOUL.md,USER.md,IDENTITY.md,skills/agy-coding/}
│       ├── code-reviewer/{AGENTS.md,SOUL.md,USER.md,IDENTITY.md,skills/code-review/}
│       └── qa-engineer/{AGENTS.md,SOUL.md,USER.md,IDENTITY.md,skills/qa-verification/}
├── .local/bin/{gcloud,gsutil,bq,gh}          # on the gateway PATH
├── .local/opt/gh/                            # gh release, checksum-verified
├── .local/lib/figma-developer-mcp/           # pinned MCP server packages (NOT under ~/.openclaw, keeps backups small)
├── .cache/openclaw-tmp/                      # TMPDIR for everything
└── Backups/                                  # OpenClaw's daily backup target
```
Facts that drive this layout:
- Only `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, `MEMORY.md` auto-load, capped at
  20,000 chars each, and only from the agent's **own** workspace root. `PROJECT_CONTEXT.md` is
  deliberately outside every workspace: it is reached by the spawn message ("project `<slug>`"), and that
  contract is the enforcement.
- Code (CWD) and the worktrees are outside every agent workspace, so `fs.workspaceOnly` must stay `false`.
- MCP server packages live in `~/.local/lib`, not `~/.openclaw`, so the daily backup does not include `node_modules`.
- The framework is six git repos: the main workspace, each of the four agent workspaces (own `.git`; the main
  `.gitignore` excludes them) and `~/.openclaw/skills/worktree-lifecycle`. After any change, commit; the linter
  reports a non-empty `git status` in any of them. Which files may exist, and when they die: architecture §3.

---

## 4. Install OpenClaw (Van runs)

### 4.1 Install and first run
```bash
npm install -g openclaw@latest
openclaw --version
openclaw onboard              # accept security notice; local mode; skip channels for now
openclaw gateway install      # creates ~/.config/systemd/user/openclaw-gateway.service
systemctl --user status openclaw-gateway.service
```

### 4.2 TMPDIR for the gateway and for shells (mandatory; see 3.3)
```bash
mkdir -p ~/.config/systemd/user/openclaw-gateway.service.d
cat > ~/.config/systemd/user/openclaw-gateway.service.d/tmpdir.conf <<'X'
# /tmp is tmpfs (RAM). OpenClaw's unit hardcodes TMPDIR=/tmp. Point the whole process tree at disk.
# Drop-ins survive `openclaw gateway install --force` regenerating the unit.
[Service]
Environment=TMPDIR=/home/openclaw/.cache/openclaw-tmp
Environment=TMP=/home/openclaw/.cache/openclaw-tmp
Environment=TEMP=/home/openclaw/.cache/openclaw-tmp
Environment=NODE_COMPILE_CACHE=/home/openclaw/.cache/openclaw-tmp/node-compile-cache
X
systemctl --user daemon-reload && systemctl --user restart openclaw-gateway.service
```
Verify in the live process, not the unit file:
```bash
tr '\0' '\n' < /proc/$(systemctl --user show -p MainPID --value openclaw-gateway.service)/environ | grep -E '^(TMPDIR|NODE_COMPILE_CACHE|PATH)='
```

The drop-in reaches only the gateway's own process tree. A shell still gets `TMPDIR=/tmp`, and that
is not cosmetic: on 2026-09-22 `openclaw backup create` tried to compact the 942 MB `main` agent DB
into /tmp's 702 MB of free RAM and died with `SQLITE_FULL`, which SQLite reports as **"database or
disk is full"** on a box with 70 GB free on `/`. Append to `~/.bashrc`:
```bash
cat >> ~/.bashrc <<'X'
# /tmp is tmpfs (RAM). The gateway drop-in covers only the service; shells need their own.
export TMPDIR=/home/openclaw/.cache/openclaw-tmp
export TMP="$TMPDIR"
export TEMP="$TMPDIR"
export SQLITE_TMPDIR="$TMPDIR"          # SQLite reads this ahead of TMPDIR
[ -d "$TMPDIR" ] || mkdir -p "$TMPDIR"
X
```
`sudo` resets the environment, so the export does not survive into a root command. Anything heavy
that must run as root carries it inline, and points at real disk rather than the openclaw-owned
cache dir (root writing there leaves root-owned files where agent subprocesses later write):
```bash
sudo env TMPDIR=/var/tmp npm install -g openclaw@<version>
```
The linter checks the gateway's TMPDIR and the shell's, separately.

### 4.3 Node heap
Leave OpenClaw's automatic `--max-old-space-size` (half of RAM). It keeps any existing heap flag when
regenerating the unit. Revisit only after the tmpfs fix is verified and memory is re-measured.

### 4.4 Backups
OpenClaw ships a daily `openclaw-backup-schedule` cron writing to `~/Backups/openclaw-git`. Keep it, but
**redacted**: `openclaw backup enable --repository ~/Backups/openclaw-git --every 24h --exclude-secrets`. Without
`--exclude-secrets` every snapshot keeps the whole `secret_store_entries` table, and git history keeps old token
values even after rotation.
Before any config change: copy `openclaw.json` into **one dated folder per change or incident**,
`~/.openclaw/backups/<what>-<YYYY-MM-DD>/` (e.g. `decisions-2026-09-19/`), next to the patch file you apply. Never
a loose `.bak` beside a live file; OpenClaw's own `openclaw.json.bak`..`.bak.4` ring is fine. Keep the last 5
config backups (Decision J); the linter counts the entries.
**Never** back up systemd override files that contain plaintext tokens (two of those had to be deleted and the tokens rotated).

---

## 5. Gateway configuration (`openclaw.json`)

Apply every block below with:
```bash
openclaw config patch --file patch.json --dry-run     # read the diff
openclaw config patch --file patch.json               # hot-reloads, no restart
journalctl --user -u openclaw-gateway.service -n 50 | grep -iE 'invalid|error'   # must be clean
```
Never hand-edit. `tools.allow` is an **exclusive** whitelist; use `deny` (or `alsoAllow`) to adjust.
A turn that was already queued **keeps the old tool policy** after a hot reload; finish or `/stop` it,
then `/new`. Check what a live session really has with
`openclaw gateway call tools.effective --params '{"sessionKey":"<key>"}'`, not the stored session entry.

### 5.1 Models
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "google/gemini-3.1-pro-preview",        // Van's choice (2026-09-19): Gemini, not Claude
        fallbacks: ["google/gemini-3-flash-preview", "anthropic/claude-sonnet-5"]
      },
      utilityModel: "google/gemini-3-flash-preview",    // summaries/compaction: cheap and fast
      compaction: { midTurnPrecheck: { enabled: true } }, // sessions grew to 2.7k messages / 260k tokens without it
      workspace: "/home/openclaw/.openclaw/workspace",
      subagents: { allowAgents: [] }                      // nobody spawns by default; main is opened up below
    }
  }
}
```
Rules learned:
- A fallback list with one entry that is spend-capped is **no fallback**: each turn burned ~2m20s of
  retries on a dead key. Always have a fallback on a *different* provider and put the fastest one first.
- Never move a specialist's *primary* to a "flash" model for speed. Use the fast model as fallback and as `utilityModel` only.
- The 200k shown by `openclaw sessions` is a reporting default, not the real window. Compaction fires
  near the model's true window unless `midTurnPrecheck` is on. An oversized session (12k+ events) is where
  the degenerate model loop in 12.5 happened; keep sessions short with isolated spawns and `/new`.

### 5.2 Loop guard
```json5
{ tools: { loopDetection: { enabled: true } } }
```
Rolling-history detector from `docs/tools/loop-detection.md` (off by default; enabled on the old box
2026-09-18). It catches "same tool, same args, same result" repetition. It is **not** a per-turn tool-call
cap (none exists in the schema), so the prompt rule in 7.1 ("poll at most 3 times, then report") stays.

### 5.3 The orchestrator: full tools, prompt-level lock
```json5
{
  agents: {
    entries: {
      main: {
        workspace: "/home/openclaw/.openclaw/workspace",
        identity: { name: "VanOpenClaw", emoji: "🦞", theme: "Orchestrator — decisive, delegating, verifies before relaying" },
        subagents: { allowAgents: ["project-manager", "developer", "qa-engineer", "code-reviewer"], delegationMode: "prefer" },
        memory: { search: { rememberAcrossConversations: true } },
        tools: { deny: [] }        // EMPTY on purpose. Anything denied here is denied in every session main spawns.
      }
    }
  }
}
```
**Why empty:** `sessions_spawn` children inherit the requester's effective tool policy
(`docs/tools/subagents/tool-reference.md`: each level can further restrict, never grant back). Evidence
from the old box, table `session_nodes.entry_json` in each specialist's sqlite:
- with `deny: ["exec","process","terminal","apply_patch",…]` on main → every spawned developer had
  `inheritedToolDeny` with `exec`, ran zero commands, and asked Van to `/approve` scripts;
- with `deny: ["figma-*","tracker-*"]` on main (the 2026-09-18 "fix") → the spawned project-manager
  session shows `inheritedToolDeny: ["figma-*","tracker-*"]` (checked 2026-09-19), i.e. no Figma, no tickets.
So the lock lives in main's AGENTS.md ("shell is for checking, not doing"; no Figma/tracker calls) and in
routing: main is never given a project `cwd`, never runs the pipeline steps itself.
`delegationMode` is only `suggest|prefer`; there is no hard "must delegate" mode.

### 5.4 The four specialists (restrictions go here; they spawn nothing)
```json5
{
  agents: {
    entries: {
      "project-manager": {
        workspace: "/home/openclaw/.openclaw/workspace/project-manager",
        identity: { name: "VanPM", emoji: "📋", theme: "Organized, precise, strict project manager" },
        subagents: { allowAgents: [] },
        memory: { search: { sources: ["memory"], rememberAcrossConversations: false } },
        tools: { deny: ["tracker-*__tracker_update_task", "tracker-*__tracker_create_task"] }   // writes go through scripts
      },
      developer: {
        workspace: "/home/openclaw/.openclaw/workspace/developer",
        identity: { name: "VanDev", emoji: "💻", theme: "Technical, efficient, builder" },
        subagents: { allowAgents: [] },
        memory: { search: { sources: ["memory"], rememberAcrossConversations: false } },
        tools: { deny: ["tracker-*"] }                         // tickets are PM's; VanDev once created its own ticket and desynced the board
      },
      "code-reviewer": {
        workspace: "/home/openclaw/.openclaw/workspace/code-reviewer",
        identity: { name: "VanReviewer", emoji: "🔍", theme: "Sharp, eagle-eyed, constructive" },
        subagents: { allowAgents: [] },
        memory: { search: { sources: ["memory"], rememberAcrossConversations: false } },
        tools: { deny: ["tracker-*"] }   // figma-* read access since 2026-09-22: it checks design fidelity
      },
      "qa-engineer": {
        workspace: "/home/openclaw/.openclaw/workspace/qa-engineer",
        identity: { name: "VanQA", emoji: "🧪", theme: "Methodical, skeptical, thorough" },
        subagents: { allowAgents: [] },
        memory: { search: { sources: ["memory"], rememberAcrossConversations: false } },
        tools: { deny: ["figma-*", "tracker-*"] }
      }
    }
  }
}
```
Create the agents first: `openclaw agents add <id> --workspace ~/.openclaw/workspace/<id>` for each of the four.

Note on `figma-*` deny: it only **hides** the tools. OpenClaw still spawns every `figma-*` server
(~120 MB each) in any agent session that has tools, because the MCP runtime checks per-run
`toolsAllow`, not the agent deny list. Mitigation is 5.5.

**VanReviewer Figma read (2026-09-22, Phase D):** the reviewer used to deny `figma-*` too, and that is part of
why every fms-studio screen passed review with a text logo and a grey placeholder box: nobody in the chain ever
compared the built screen to the design. It now denies only `tracker-*`, and the linter expects exactly that
(`figma-*` in the reviewer's deny list is a FIX line, not an OK). The access is read-only by prompt: confirm a
value the ticket does not state, never download assets — VanPM already did that, into Internal Artifacts.
VanQA keeps both denies; it tests behaviour against the AC, and has no design contract to check.

**VanPM tracker writes (2026-09-19):** that is why `project-manager` denies `tracker-*__tracker_update_task` and
`tracker-*__tracker_create_task` (the linter checks these exact lists; `apply_patch` is not denied anywhere on the live box). It keeps `tracker_get_task` for reads; every write goes through
`tracker_push.py` / `tracker_status.py`, which keep the spec markers in sync. A VanPM that had the MCP write tool
moved three tickets to `qa`/`complete` on its own during the first live run.

### 5.5 MCP runtime
```json5
{ mcp: { sessionIdleTtlMs: 300000 } }   // idle servers exit after 5 min; verified no figma process left after 13 min
```
Servers themselves are registered per project in Section 9. **`mcp.servers.*.env` does not accept
SecretRefs and `${VAR}` only sees the gateway's own environment** (only `plugins.entries.acpx.config.mcpServers`
takes SecretRefs). That is why every MCP server is launched through a Python launcher that reads the
project's context file and the vault, and injects the key into the child process only.

### 5.6 Skills hardening
```json5
{
  skills: {
    workshop: { autonomous: { mode: "propose" }, approvalPolicy: "pending" },   // agents cannot self-install skills
    allowBundled: ["coding-agent", "spike", "python-debugpy", "node-inspect-debugger"],  // development only
    entries: { "coding-agent": { enabled: true } }
  }
}
```
**Use `skills.allowBundled`, not a list of `false` entries.** The old box had 30 entries set `false` but
**21 bundled skills were never named at all**, so `weather`, `notion`, `meme-maker`, `taskflow`,
`clawhub`, `apple-*` and `peekaboo` were all live (28 ready for main). An allowlist closes every gap at
once and only affects *bundled* skills: managed (`worktree-lifecycle`), workspace
(`project-orchestration`, `project-onboarding`) and agent-level (`feature-breakdown`, `agy-coding`,
`code-review`, `qa-verification`) skills are untouched. It does **not** cover workshop skills in
`~/.openclaw/agents/*/agent/workshop-skills` - remove those by hand (2026-09-20: `workflow-architect`
and `chat-media-attachments` moved to `~/Backups/removed-skills/`). Deliberately not allowed:
`github`/`gh-issues` (they would give agents a path around `git_env.py`'s merge and PR-base refusals),
`clawhub` (installs third-party skills), `diagram-maker`, `healthcheck`, `control-ui`, `tmux`.
Each enabled skill is prompt text on every turn.
The skill workshop still generates *proposals* (the old box accumulated seven in one day: "troubleshoot npm ci",
"deploy nx app engine", …). They stay pending; review or delete them weekly.

### 5.6b Memory plugins (Decisions E, G)
```json5
{ plugins: { entries: { "active-memory": { enabled: false }, "memory-core": { config: { dreaming: { enabled: false } } } } } }
```
Plugin changes need a gateway restart (`config patch` says so). `memory-core` stays on: agents keep `MEMORY.md`, daily notes and `memory_search`.

### 5.7 Tools profile and filesystem
```json5
{
  tools: { profile: "coding" },
  // fs.workspaceOnly stays false: Code (CWD) and worktrees are outside every workspace. Do not "fix" this.
  // tools.sessions.visibility ("all") and tools.agentToAgent (enabled) are needed for sessions_send between agents.
  // Both are OpenClaw defaults and are NOT set explicitly on the live box. Do not "fix" them to something narrower.
}
```

### 5.8 Channels: one bot, bound to `main` only
```json5
{
  channels: {
    discord: {
      enabled: true,
      groupPolicy: "allowlist", dmPolicy: "allowlist", allowFrom: ["<van discord user id>"],
      accounts: { main: { token: { source: "store", provider: "default", id: "DISCORD_BOT_TOKEN_MAIN" } } },
      defaultAccount: "main",
      guilds: { "<guild id>": { requireMention: true, users: ["<van discord user id>"] } }
    }
  },
  bindings: [ { agentId: "main", match: { channel: "discord", accountId: "*" } } ],
  commands: { ownerAllowFrom: ["discord:<van discord user id>"] }
}
```
Do **not** give specialists their own bots. On the old box a `developer` bot bound to Discord meant Van
could talk to VanDev directly, which bypassed the orchestrator, the verify gate, and the approval gate,
and produced the 34-minute no-reply loop. It crept back on the old box (found 2026-09-19: a `developer` account +
binding); if one exists, remove the binding and set `accounts.developer.enabled: false`. Telegram (Decision D) follows the same
rule: the live box has `channels.telegram` with its own allowlist and one binding `{ agentId: "main", match: { channel:
"telegram", accountId: "default" } }`. Copy that block from the old box's config rather than retyping it.
Chat controls you will need: `/stop` aborts the current run (the CLI cannot abort a Discord-owned run;
`sessions.abort` returns unauthorized), `/new` starts a fresh session.

Store the token first: `openclaw secrets store set DISCORD_BOT_TOKEN_MAIN --kind secret --value-file -` (paste, Ctrl-D).

### 5.9 Provider keys
```bash
openclaw secrets store set GEMINI_API_KEY --kind env --value-file -       # env-kind: the coding agent must read it back
openclaw secrets store set ANTHROPIC_API_KEY --kind secret --value-file -
```
Then point `models.providers.google.apiKey` and the anthropic auth profile at the store ids via `openclaw config patch`.
Verify: `openclaw secrets audit` shows no plaintext keys in per-agent sqlite. If it does, Van runs
`openclaw secrets configure --apply --agent <id>` in a real terminal (the TUI renders nothing under an agent pty).

---

### 5.10 Heartbeat: the delivery watcher's clock
```json5
{
  agents: { defaults: { heartbeat: {
    agentId: "main", every: "15m",
    target: "discord", to: "channel:<project channel id>", accountId: "main",
    directPolicy: "allow",       // as on the live box
    isolatedSession: true,       // fresh session each run; in main's own session it revived an old task
    prompt: "Heartbeat. Follow the heartbeat monitor scratch context when provided. Then, for every project directory under /home/openclaw/.openclaw/workspace/projects (skip _template and _tools), run `python3 /home/openclaw/.openclaw/workspace/projects/_tools/delivery_watch.py <slug>`. For each ACTION it prints, do exactly what its `do:` line says, following step 6 of the project-orchestration skill (delegate: VanPM for tickets, VanDev for code, VanReviewer for reviews; post short one-line updates in this channel), then run its `ack:` command. If you cannot finish an action, leave it un-acked and say why in one line; it comes back next heartbeat. Never push, merge, deploy, retry builds or edit code yourself. Do not infer or repeat old tasks from prior chats. When the watcher prints a LINT action (once a day), post its lines in ONE message starting with 'Daily lint:' and ack it; never delete, move or edit files from a heartbeat, and never ask a specialist to fix them: fixing the framework is Van's. If the watcher printed NO_ACTIONS and nothing else needs attention, reply NO_REPLY."
  } } }
}
```
`prompt` replaces the default body (not merged). Runtime heartbeat instructions come from the prompt and the
monitor scratch, never from a `HEARTBEAT.md` file. With one Discord channel per project, point `to:` at the
channel Van works in; several projects share it until per-project heartbeats are needed.

---

## 6. Secrets: naming and kinds

| Secret | Name | Kind | Why that kind |
|---|---|---|---|
| Tracker API key | `<CLICKUP\|JIRA\|LINEAR>_API_TOKEN_<SLUGUPPER>` | `env` | tracker launcher must read it back. Jira stores `email:api_token` (Basic auth needs both) |
| Figma token | `FIGMA_API_KEY_<SLUGUPPER>` | `env` | figma launcher must read it back |
| GitHub fine-grained PAT | `GITHUB_TOKEN_<SLUGUPPER>` | `env` | git launcher must read it back |
| GCP SA key JSON | `GCP_SA_KEY_<SLUGUPPER>_<ENV>` | `env` | gcloud launcher restores the file from it |
| Discord/Telegram bot tokens | `DISCORD_BOT_TOKEN_MAIN` | `secret` | only the gateway reads it |
| Anthropic key | `ANTHROPIC_API_KEY` | `secret` | only the gateway reads it |
| Gemini key | `GEMINI_API_KEY` | `env` | coding agent (agy) reads it per invocation |

Rules:
- `--kind env` is **required** for anything a launcher reads. Without it, names ending in `_API_KEY`,
  `_TOKEN`, `_PASSWORD` default to `secret` kind, which is **write-only forever**: `store get` exits 2,
  and the value cannot be moved or recovered. This broke the Figma MCP and the first coding-agent auth attempt.
- Store from a **real SSH terminal** with `--value-file -` and paste; never `--value` on a command line
  (shell history), never through the chat `!` prefix (no stdin → empty secret stored silently).
- Van stores; agents never see values. **Do not run `openclaw secrets store list`**: it prints env-kind
  values in plaintext. Verify names and kinds without a Node process:
  ```bash
  # NOTE 2026-09-20: the sqlite3 CLI is NOT installed on this box (3.2 says to install it, and it was
  # never done), so the line below fails with "command not found". Until it is installed, use python3,
  # which needs no extra package and starts no second Node process:
  python3 -c "import sqlite3;c=sqlite3.connect('file:/home/openclaw/.openclaw/state/openclaw.sqlite?mode=ro',uri=True);[print(f'{k:8} {n}') for n,k in c.execute('select name,kind from secret_store_entries where deleted_at_ms is null order by name')]"

  sqlite3 'file:/home/openclaw/.openclaw/state/openclaw.sqlite?mode=ro' \
    "select name, kind from secret_store_entries where deleted_at_ms is null order by name"
  ```
  Agents verify existence with their `secrets` tool (`action: list`), never by shelling out to
  `openclaw secrets` (second Node process; can OOM the gateway).
- Never print a SecretRef `id` verbatim in a script's output. Van once pasted a live token into an `id`
  field; a shape-check script printed it and it went to the model provider. Validate against
  `^[A-Z][A-Z0-9_]{0,127}$` and print OK / NEEDS ATTENTION only.
- Rotate anything that ever landed in a transcript, a backup, or a systemd override.
- Fine-grained PATs expire (set ≤ 90 days, record the date in PROJECT_CONTEXT). Deploy keys do not. That is
  why push stays on the deploy key and only the GitHub API uses the PAT (Decision F).

---

## 7. Agent workspaces

### 7.1 Files every agent has
`AGENTS.md` (role + rules), `SOUL.md` (voice), `IDENTITY.md`, `USER.md` (Van's preferences only, never
project facts), `memory/YYYY-MM-DD.md` (daily notes, written by the session-memory hook).
`MEMORY.md` exists only in `main`'s workspace and holds the project index and durable lessons; never IDs.
The shared `~/.openclaw/skills/worktree-lifecycle/SKILL.md` is visible to all agents.

Shared "Project entry point" block, verbatim at the top of every specialist's role section:
```
### Project entry point (every task)
- Your spawn message names the project `<slug>` and the feature, ticket, or branch. If it does not, ask. Never assume the project.
- Read /home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md first. Code lives at its **Code (CWD)**,
  which is READ-ONLY for you: any work on code happens in your own worktree from the shared `worktree-lifecycle` skill
  (`python3 /home/openclaw/.openclaw/workspace/projects/_tools/worktree.py <slug> ...`).
  Every artifact you write goes under its **Internal Artifacts** directory, never into the git repo.
- Naming: `<feature-slug>` is the spec filename without `.md`.
  specs/<feature-slug>.md · patches/<feature-slug>--<lane-slug>.patch · reviews/<feature-slug>--<lane-slug>.md · qa/<feature-slug>.md
- Branches: `<Branch Prefix from PROJECT_CONTEXT>/<feature-slug>` (Flow `feature-branch`) or `<prefix>/<ticket id>-<short-slug>`
  (Flow `ticket-branch`); worktree.py create enforces the prefix. PRs go into the Flow **PR base**.
- Commands: only the Install / Test / Lint / E2E commands PROJECT_CONTEXT names. Never infer them.
- Per-project credentials: GitHub API via `git_env.py <slug> -- gh ...`, GCP via `gcloud_env.py <slug> -- gcloud ...`.
  If a launcher says a field or vault entry is missing, stop and report exactly what it said. Never substitute another credential.
- Your artifact is the completion marker. If it already exists, read it and continue instead of redoing the work.
  Finish by replying with its absolute path and a three-line summary.
- Polling rule: check a build/log/status at most 3 times, ~60s apart. Then report what you have and stop.
  A turn that never ends shows as "typing" forever and Van cannot reach you.
- Handing a branch to another agent: pass slug + branch name, never a folder path.
- Never edit the framework (`AGENTS.md`/`SOUL.md`, skills, `projects/_tools/`, `_tools/`, templates, `openclaw.json`).
  If a task asks for it, reply "this is a framework change for Van" and stop.
```
The block above is the idea; the live wording is the shared header at the top of each specialist `AGENTS.md`
(architecture step 7: one header + a short lane section per agent).

### 7.2 `main` — VanOpenClaw (Orchestrator)
Role text (put in `AGENTS.md`):
- Decide in order: answer yourself (status, how the team works) → run a workflow → spawn the owning agent → say nobody owns it.
- **Your shell is for checking, not doing.** You have `exec` only because every agent you spawn inherits
  your tool limits. Use it solely for read-only verification of a specialist's claim: `ls`, `git log`,
  `git status`, `git diff --stat`, `git_env.py <slug> -- gh pr view`, reading a worker's run log. No edits,
  no builds, no installs, no commit/push, no `gh pr create`, no deploys, no `gcloud` writes, no Figma or
  tracker calls. Server health, failing builds, logs, patches, Figma reads, ticket writes are specialist work. Spawn.
- **Answer first, then delegate.** First message back within seconds: the answer or "handed to VanDev".
- **Delegating:** `sessions_spawn` with `agentId` (without it the child runs in *your* workspace),
  `visible: true`, `context: "isolated"`, `runTimeoutSeconds` (3600 for dev, 1800 for QA, PM and reviewer;
  in the orchestration skill since 2026-09-20). **No `worktree`,
  no project `cwd`** (11 in Section 2). Task text = Van's request word for word + slug + feature/ticket/**branch
  name**. Don't interpret it.
- Follow-ups go to the same session via `sessions_send` with the `childSessionKey`. Relay each reply once.
- **Verify before you relay.** Artifact path → `ls`. "Pushed" → `git log origin/<branch>`. "PR opened" →
  `gh pr view` through `git_env.py`; a `/pull/new/...` link is **not** a PR. Coding-agent delegation →
  run-log + worktree paths, or `sessions_send` and ask. Report claims as claims, facts as facts.
- Approval gate: merges, pushes to the default branch, tracker writes outside the status table, and messages to other
  people - including a reply to a human reviewer's PR comment on a `teammate`/`maintenance` project, which VanDev
  drafts and does not post - wait for Van's explicit yes. **Silence is a NO:** `ask_user` returning no answer / "proceed with best
  judgment" means stop and wait (it pushed twice on a timeout on the old box). A task-branch push and its PR need no yes.
- GitHub-Native Reviews: VanDev pushes to the task branch and opens the PR directly. VanReviewer then reviews the code
  natively on the GitHub PR and marks the head commit with the `openclaw/review` status (`git_env.py <slug>
  --review-status`). A PR is "ready" only when that status is green on its current head (8.1 step 5).
  `git_env.py` refuses every merge; never work around a refusal.
- **Framework changes are not agent work.** A request that needs an `AGENTS.md`, a skill, `projects/_tools/`,
  `_tools/`, the template or `openclaw.json` changed gets the answer "framework change, for Van's next Claude Code
  session" plus two or three lines on what would change. (2026-09-19 13:04: main rewrote `git_env.py`, its own
  AGENTS.md and the orchestration skill in six minutes and deleted the review gate.)
- Heartbeat: run `delivery_watch.py <slug>` per project and carry out its ACTIONs by delegating (8.1 step 6).
- It sees `figma-*`/`tracker-*` only so spawned VanPM inherits them; it never calls them.
- Never list secrets (`secrets` tool `list`, `openclaw secrets store list`): values print into the transcript.
- Red lines: never edit `openclaw.json` (show before/after, wait for yes); check every key against
  `/usr/lib/node_modules/openclaw/docs`; after any config change read the journal; never run `openclaw doctor --fix`.
- Discord: bullets not tables; wrap multiple links in `<>`.
- Team roster section: one `####` entry per agent (`Owns`, `Spawn with`) and per workflow (`Use for`, `Agents`),
  parsed by `_tools/validate_team.py`. Only what is listed exists.

Skills owned by `main`: `project-orchestration` (8.1), `project-onboarding` (Section 9).

### 7.3 `project-manager` — VanPM
- Translates requests into specs and tickets. **Never writes application code.**
- Every ticket request goes through the `feature-breakdown` skill: one `[Feature]` parent + lane subtasks
  `[FE] [BE] [DB] [INT] [QA] [SPIKE]`, each ≤ 8h, Given/When/Then acceptance criteria (≥ 3), explicit out-of-scope.
  Never one ticket per screen. Never filler ("primary UI elements are visible").
- Step 0 always: read + validate PROJECT_CONTEXT. Never query the tracker to discover lists.
- Figma: for every link, `download_figma_images` → `view_image` → `get_figma_data` (with `nodeId`, never a
  whole file) → screen inventory. No UI ticket without the screenshot.
- Spec first → stop for Van's approval → push with `tracker_push.py` → verify by reading back. Statuses only with
  `tracker_status.py` (`--get` read, `--claim` GO/SKIP, `--only … --status`), only when the orchestrator names the
  ticket and status per the table in 8.1. `staged` only for a watcher DEPLOYED/MERGED action, `done` only for a MERGED
  action on projects without a deploy signal, and for `[SPIKE]` tickets once their findings note exists. Never otherwise.
- Never spawns agents. Never hand-written ClickUp calls. Never lists secrets (verify the token with `--get`).
- Figma is required only for specs that have an `[FE]` ticket; CI/backend specs use `figma: none` (the old check
  made agents paste dummy PNGs with fake node ids).
- Owns one onboarding step: fill `## Stack` from the repo (reading it by absolute path) and run the validator `--live`.
- Tools: `tracker-<slug>__tracker_get_task` (writes denied, 5.4), `figma-<slug>__*`, exec (scripts, validators), read/write.

### 7.4 `developer` — VanDev
- Implements **one lane ticket at a time**, named in the spawn message. AC + out-of-scope are the contract.
- Routine (from the `worktree-lifecycle` skill): `worktree.py <slug> sweep` → `worktree.py <slug> create
  <prefix>/<feature-slug> --agent developer --task "…"` → launch the coding agent with `workdir:` = the printed
  worktree and the printed preparation receipt in its prompt → review its diff → run the named test + lint
  commands → `git -C <worktree> status` must be empty after `git add` (PR #31 on the old box shipped without its
  `.gcloudignore` because one file was never committed) → commit → push the task branch (`git push -u origin <branch>`, never the default branch) and open the PR (`git_env.py <slug> -- gh pr create --base <Flow PR base> --head <branch> …`) with the **ClickUp URL of every delivered ticket in the PR body** (that is what moves them to
  `qa` after deploy) → reply with the **real PR URL `gh` prints** → `worktree.py <slug> finish <branch> --pr <url>` → VanReviewer reviews natively on GitHub. Team projects: follow
  the repo's PR template (Flow **PR conventions**) and merge `origin/<PR base>` into the branch first when it is behind.
- Never merges, never force-pushes, never edits Code (CWD). GitHub review comments: pull feedback from the PR, fix, push to the
  same branch, reply to the threads on the PR starting with `🤖 VanDev:` (the watcher skips those). A QA-`rejected` ticket is fixed
  on `bug/<feature-slug>--<ticket id>`.
- Saves `git diff <base>...HEAD` to `patches/<feature-slug>--<lane>.patch` plus the commands run and their results.
- If the ticket is wrong or impossible: stop and say so. Do not reinterpret.
- **Delegate substantial code writing** (multi-file, refactors, test suites) to the coding-agent backend;
  hand-code small edits and say so. **Never delegate operations:** git, gh, builds, tests, installs,
  gcloud, log reads are your own `exec` calls. Do not wrap them in a script for a worker and do not ask Van
  to `/approve` a script. If you find yourself without a shell, that is a leaked deny (5.3): report it, do not work around it.
- Report run-log + worktree paths for any delegation. The run log is `<Internal Artifacts>/runs/<feature>--<lane>--<UTC>.log` (worker output piped through `tee`). An honest "I hand-coded this, two lines" is correct;
  a false delegation claim is the one unforgivable thing.
- Dev server: random port, exposed via `portal`, link shared. Never 3000/8080.
- Polling rule (7.1) is hard: 3 checks, then report. The old VanDev rewrote and re-ran one script ~200 times.

### 7.5 `code-reviewer` — VanReviewer
- Reviews the PR named in the spawn message against the ticket's acceptance criteria (`gh pr diff` through
  `git_env.py`; its own worktree only when it needs the files).
- Posts on GitHub: `gh pr review <url> --request-changes` when something blocks, otherwise `--comment` with
  `APPROVED` as the first line. **`--approve` always fails**: VanReviewer acts through the same GitHub account that
  opened the PR, and GitHub does not let an account approve its own PR (a real approval needs a second account).
- Saves the same review as `reviews/<feature-slug>--<lane-slug>.md`: line 1 verdict, line 2 `Reviewed SHA: <PR head>`,
  one line per acceptance criterion (implemented where, tested where, or MISSING), then Blocking / Non-blocking.
- Runs `git_env.py <slug> --review-status <url>`: sets `openclaw/review` on the head (green = APPROVED, red = CHANGES
  REQUESTED) only if that file's SHA is the head; `refused: no review file` = the PR moved, review the new head. A
  `403 … Commit statuses` line means the project token lacks that permission; it goes into the reply for Van.
- Never writes feature code. Never pushes or commits. No tracker, no Figma. No commit status except `--review-status`.

### 7.6 `qa-engineer` — VanQA
- `worktree.py <slug> create <branch> --agent qa-engineer`, run the `[QA]` ticket: E2E scenario + parent AC,
  with the named test commands only, never in Code (CWD). `finish <branch>` when done.
- Writes `qa/<feature-slug>.md`: PASS/FAIL per criterion, then one block per defect (steps, expected, observed, evidence path).
- Internal pre-merge check: it changes no ticket status (ClickUp `qa` means "on staging", 8.1).
- Never modifies code, never commits or pushes (the old VanQA pushed a README line to `Development` "to trigger
  CI"), never files tickets (VanPM adds defects as tickets to the same spec). Cleans test output out of the
  worktree so `finish` finds it clean. No public tunnels; at most 3 checks about 60 s apart (7.1).
- If the E2E runner is missing, report it; the first feature of a project carries `[INT] Set up Playwright E2E runner`.
- Spawned with `runTimeoutSeconds: 1800`. A watch-mode test command hits that cap every time (28 timeouts on the old
  box); the real fix is the explicit, non-watch test commands in PROJECT_CONTEXT.

---

## 8. Orchestrator skills

### 8.1 `project-orchestration` (main) — feature delivery pipeline
Parameterised entirely by `CTX = workspace/projects/<slug>/PROJECT_CONTEXT.md`. Every spawn is `agentId` +
`context: "isolated"` + `visible: true`, **no `cwd`, no `worktree`**; messages start `Project <slug>. Context: <CTX>.`
and name branches, never folders. The skill file is the source of truth; this is its shape.

**The project's Flow decides which steps run** (`validate_context.py CTX --json` → `flow`, `status`): step 1 needs
stages `spec`+`tickets` (off: VanPM adopts human tickets with `tracker_scan.py`), step 3 `review`, step 4
`internal-qa`, step 5 `merge-gate`, step 6 `delivery-watch`; step 2 always runs. Team profiles (`teammate`,
`maintenance`) only claim tickets matching the Flow **Assignee filter**, never rewrite human tickets, follow the
repo's PR conventions, and never touch other people's PRs, branches or tickets (architecture §4.3).

**Statuses** use canonical keys (`todo doing staged rejected done cancelled hold`) that each project maps to its board
through the Flow **Status map**; scripts take the key (`tracker_status.py --status staged`). Shown here with the
fms-studio names (`staged` = `qa` = merged **and deployed to staging**, ready for external QA):

| When | Who notices | Status |
|---|---|---|
| Tickets pushed after Van's "go" | VanPM | `to do` |
| VanDev starts a lane ticket (`--claim`; parent on first claim) | VanPM | `in progress` |
| Internal review, VanQA, PR open, PR feedback | - | stays `in progress` |
| Every Cloud Build of a commit containing the merge succeeded | watcher `DEPLOYED` → VanPM | `qa` (tickets linked in the PR body; parent when all children are `qa`) |
| Build failed after merge | watcher `BUILD_FAILED` | originals stay `in progress`; bug ticket → normal flow; all move to `qa` with the first green build |
| External QA sends it back / passes it | external QA | `rejected` (watcher → VanDev, re-claimed) / `complete` |
| All tickets of a spec `complete` | watcher `FEATURE_COMPLETE` | spec → `specs/_done/`, sweep, MEMORY line |
| Spec wrong or blocked / PR closed unmerged | VanPM / watcher `PR_CLOSED` | `on hold` / Van decides `cancelled` or `in progress` |

0. **Resolve project**, validate CTX, run the watcher once.
1. **Spec (VanPM)** → relay the summary verbatim → wait for Van's explicit "go" (no answer is not a go) → push.
2. **Build, one lane ticket at a time** on one feature branch `<prefix>/<feature-slug>` (`[DB]`→`[BE]`→`[FE]`→`[INT]`,
   never in parallel: they share the branch). VanPM `--claim` → GO/SKIP. VanDev implements in its worktree,
   commits, pushes the branch, and opens the PR. Spec objection → `on hold` → back to 1.
3. **Review (VanReviewer)** of that PR natively on GitHub, saved as `reviews/…md`, then `--review-status` sets
   `openclaw/review` on the head → `CHANGES REQUESTED`: VanDev fixes, pushes, and the new head is reviewed again;
   `APPROVED`: next lane. Any push after a review (PR feedback included) needs a new review.
4. **VanQA** once per feature in its own worktree (internal; no status change). Defects → VanPM adds tickets to
   the same spec → 2.
5. **Final Readiness Gate:** main checks `gh pr view <n> --json state,headRefOid,statusCheckRollup`: head = the QA'd
   SHA and `openclaw/review` = SUCCESS (empty can also mean the token cannot read statuses: say so). Then: "Feature
   `<feature-slug>` passed GitHub PR review and QA. Everything is ready on the PR. Merging is yours." Van merges on
   GitHub. A ruleset requiring `openclaw/review` would make GitHub refuse an unreviewed head, but **Decision N
   (2026-09-20) is not to add one yet**, so step 5's check is what enforces it.
6. **Delivery watcher** (heartbeat, 15 min): `delivery_watch.py <slug>` prints ACTIONs — `PR_FEEDBACK`, `DEPLOYED`,
   `BUILD_FAILED`, `NO_BUILD`, `PR_CLOSED`, `REJECTED`, `FEATURE_COMPLETE`, `STALE_WORKTREE`, `SWEEP_DUE`, `MERGED`
   (Deploy signal `none`: the merge is the signal), `LINT` (daily, first project only: posted, never fixed) — each
   with what to do and an `--ack` id. Main delegates, then acks; un-acked actions come back. On team profiles a
   `PR_FEEDBACK` fix is pushed right away, but the reply to the person is drafted by VanDev and posted only after
   Van approves the text (8.1 step 6; architecture Decision O).
7. **Memory:** one line per feature in `MEMORY.md` (date, slug, PR, artifacts, lessons; no IDs).

Direct single-agent requests skip 1 and 4 but not the rules: code goes on a task branch with a PR, is reviewed on
that PR before Van hears "ready", and the PR body carries the ticket URL when a ticket exists. Nobody in the team merges, deploys, retries builds or sets `complete`.

### 8.2 `project-onboarding` (main) — Section 9 is the runbook.

### 8.3 Specialist skills
- `project-manager/skills/feature-breakdown/` — decomposition rules, ticket template, splitting patterns,
  spec validator (rejects > 8h, < 3 AC, non-GWT AC, filler phrases, missing out-of-scope), push **only** through
  `scripts/tracker_push.py` (matches each ticket by the `id:` it stamps into the spec header, similarity check, `<feature-slug>.clickup.json` marker next to the spec),
  statuses through `scripts/tracker_status.py`, human tickets through `scripts/tracker_scan.py`. The MCP write tools
  are denied to VanPM (5.4); `tracker-<slug>__tracker_get_task` is for reads.
- `developer/skills/agy-coding/` — how to launch the coding-agent backend (9.6) in the worktree
  `create` printed, in background, with a notification route; what "proof of delegation" means; when
  hand-coding is right; the explicit list of things never delegated (git, gh, builds, tests, gcloud).
- `code-reviewer/skills/code-review/` — review checklist and report format (the posting rules in 7.5 win).
- `qa-engineer/skills/qa-verification/` — how to test against acceptance criteria and what a QA report must contain (written 2026-09-20).
- `~/.openclaw/skills/worktree-lifecycle/` — shared by all four; its own git repo; copy from the old box as-is.
  Nothing else goes in `~/.openclaw/skills/` (every skill there loads for every agent; the linter flags extras).

Keep every skill project-agnostic. No skill names a project except in a labelled example.

---

## 9. Onboarding a project (per project, repeatable)

The output is one validated file, `workspace/projects/<slug>/PROJECT_CONTEXT.md`. If that file is wrong,
tickets land in the wrong list and secrets resolve under the wrong name. No step is optional.
**Adding a project touches no tool, no skill, no prompt**: only this file, the secrets, and two MCP registrations.

### 9.1 Collect from Van (one checklist)
- Slug, display name.
- Git SSH clone URL + SSH alias (deploy key per project), **GitHub repo as `owner/repo`**, default branch.
- Tracker (`clickup`/`jira`/`linear`/`none`) and its Board ID - a ClickUp list id (digits), a Jira
  project key plus the site URL, or a Linear team key/id. **Never discovered by API.**
- Figma file link (or "none").
- GCP project id(s) + region per environment (or "none").
- **Explicit install, test, lint, E2E, and deploy commands/pipeline** (or "none yet"). Never "infer from the repo".
- **Flow answers** (defaults = `factory`): Profile, Stages, Ticket source, Assignee filter (Van's tracker id for team
  projects), Branch model, PR base, Merge by, Deploy signal, Status map (board names), Chat channel, PR conventions.
- Whether the repo's PR base gets a ruleset requiring the `openclaw/review` status (team repos: the team decides).

### 9.2 Secrets (Van runs, real SSH terminal; agents never see values)
```bash
openclaw secrets store set <CLICKUP|JIRA|LINEAR>_API_TOKEN_<SLUGUPPER> --kind env --value-file -   # Jira: email:api_token
openclaw secrets store set FIGMA_API_KEY_<SLUGUPPER> --kind env --value-file -
openclaw secrets store set GITHUB_TOKEN_<SLUGUPPER> --kind env --value-file -
openclaw secrets store set GCP_SA_KEY_<SLUGUPPER>_STAGING --kind env --value-file /path/to/sa.json   # then delete the file
```
Verify with the sqlite query in Section 6 (all four present, kind `env`).

How to mint each:
- **ClickUp:** ClickUp → Settings → Apps → API Token. One per ClickUp workspace/account; if two projects share
  a workspace, store the same value under both names anyway (the name is per project; the value may repeat).
- **Figma:** Figma → Settings → Security → Personal access tokens, scopes `file_content:read`, `file_dev_resources:read`.
- **GitHub fine-grained PAT:** GitHub → Settings → Developer settings → Fine-grained tokens. Resource owner = the org,
  Repository access = **only this repo**, permissions: Contents read/write, Pull requests read/write, **Commit statuses
  read/write** (the `openclaw/review` status), **Actions read**, **Workflows read/write**, Metadata read.
  No Administration: agents must not be able to change rulesets.
  The last two were missing from this list until 2026-09-21 and both were proven necessary on a real repo:
  - **Actions: read** — every CI read goes through `/actions/runs`. Without it the API returns
    `403 Resource not accessible by personal access token`, so the merge gate can read no check at all and
    `--readiness` reports UNKNOWN rather than a verdict. fms-studio's token still lacks it.
  - **Workflows: read/write** — GitHub refuses a fine-grained PAT that creates or edits anything under
    `.github/workflows/`, with `refusing to allow a Personal Access Token to create or update workflow ...
    without workflow scope`. `Contents: write` is NOT enough. VanDev adding a CI workflow (fms-studio PR #39
    did exactly that) fails at push time without it, and the error reads like a bug rather than a missing scope.
  Expiry ≤ 90 days; put the expiry date in PROJECT_CONTEXT. If the org requires approval, an org owner must approve
  it before `git_env.py <slug> --check` passes.
- **GitHub deploy key:** `ssh-keygen -t ed25519 -f ~/.ssh/<slug>_ed25519`, add as a deploy key with write access,
  and an `~/.ssh/config` `Host <slug>.github.com` alias with `IdentitiesOnly yes`.
- **GCP:** one service account per project per environment, least privilege (no Owner/Editor — the old box had an
  admin SA pinned as the global default). Enable Cloud Resource Manager API on the project or metadata calls fail with `SERVICE_DISABLED`.

### 9.3 Directories and clone (agent may run after Van's yes)
```bash
mkdir -p /home/openclaw/projects/.worktrees/<slug>
SLUG=<slug>
mkdir -p /home/openclaw/.openclaw/workspace/projects/$SLUG/artifacts/{specs/_done,specs/_superseded,patches,reviews,qa,runs}
sed "s/<slug>/$SLUG/g" /home/openclaw/.openclaw/workspace/projects/_template/specs/_planned-data.md \
  > /home/openclaw/.openclaw/workspace/projects/$SLUG/artifacts/specs/_planned-data.md   # same as the project-onboarding skill
git clone git@<slug>.github.com:<owner>/<repo>.git /home/openclaw/projects/<slug>    # primary checkout; agents never edit it
```

### 9.4 Per-project launchers (`projects/_tools/`, stdlib Python only)
All share one shape: **read `PROJECT_CONTEXT.md` via `validate_context.py`, take the secret name from it,
read the env-kind value with `openclaw secrets store get --plain <name>`, inject into the child env only, `exec`.**
Nothing is written to `~/.bashrc`, `~/.gitconfig`, `~/.config/gh`, or the repo; a missing field fails loudly naming the field.
**All of these exist and are verified on the old box; copy them as-is (Appendix).**

| Launcher | Called by | Injects |
|---|---|---|
| `figma_mcp.py <slug>` | `mcp.servers["figma-<slug>"]` | `FIGMA_API_KEY`, `IMAGE_DIR`=Internal Artifacts, cwd=Internal Artifacts (the server loads `<cwd>/.env` with override, so it must never start inside the repo), `--no-telemetry` |
| `tracker_mcp.py <slug>` | `mcp.servers["tracker-<slug>"]` | the tracker token from the `Tracker:` SecretRef; the provider comes from the `**Tracker:**` line and the work is done by `_tools/trackers/`. Tool names are neutral (`tracker_get_task` …) so no deny list or prompt is per project |
| `gcloud_env.py <slug> -- <cmd>` | VanDev/VanQA in exec | `GOOGLE_APPLICATION_CREDENTIALS`, `CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE`, `CLOUDSDK_CORE_PROJECT`, `CLOUDSDK_COMPUTE_REGION`, `CLOUDSDK_ACTIVE_CONFIG_NAME=<slug>`; strips inherited `GOOGLE_*`/`CLOUDSDK_*`; restores the key file 0600 from the vault |
| `git_env.py <slug> -- <cmd>` / `--check` / `--review-status <pr>` | VanDev, VanReviewer (`--review-status`), main read-only | `GH_TOKEN`/`GITHUB_TOKEN`, `GH_REPO=<owner/repo>` (gh cannot infer the repo from an SSH-alias remote), `GH_PROMPT_DISABLED=1`, `GIT_TERMINAL_PROMPT=0`, one-shot `credential.helper` scoped to `https://github.com` for HTTPS remotes |
| `delivery_watch.py <slug> [--json\|--ack <id>…\|--dry --since <iso>]` | the heartbeat (main) | nothing; read-only join of GitHub (via `git_env.py`), Cloud Build (via `gcloud_env.py`, builds on the Flow PR base (default: Default branch), every `Deploy triggers` name must succeed, `COMMIT_SHA` per build, ancestry via `git merge-base --is-ancestor`) and ClickUp (list tasks + comments; token from env or vault). State in `<Internal Artifacts>/delivery_state.json` (`watch_since` set on first run: older merges are history). Ignores `*[bot]`, the `GitHub bots:` context line, and comments starting with 🤖. Refuses unknown `--ack` ids |
| `worktree.py <slug> create\|finish\|sweep\|list\|path` | every specialist | no secrets; reads Code (CWD), Default branch, Flow PR base, Branch Prefixes, Internal Artifacts; uses `git_env.py` internally to ask GitHub for PR state during `sweep` |

**`git_env.py` is also the gate** (the only way agents reach GitHub): refuses `gh pr merge` and the merge API;
refuses `gh pr create` unless `--base` is the Flow PR base and the branch exists on origin; refuses raw
`gh api …/statuses/…` writes. `--review-status <pr>` is the only status writer: `openclaw/review` = success/failure on
the PR head, only when a `reviews/*.md` file has that head as `Reviewed SHA:` (newest file wins).

`validate_context.py` fields (all parsed by label): required for every project `slug`, `repo_url`,
`code_cwd`, `artifacts_dir`; required only when `**Tracker:**` is not `none`: `board_id`,
`tracker_secret`, `statuses`, `create_status` (plus `tracker_mcp_server`, and `tracker_base_url` for
Jira); conditional `figma_file`→`figma_mcp_server`+`design_secret`,
`gcp_project_id`→`gcp_key_secret`+`gcp_key_json`+`gcp_region`, `github_repo`→`git_secret`; plus `default_branch`,
`branch_prefixes`, `deploy_triggers`, and `flow` + `status` from `## Flow` (all optional: Profile defaults to `factory`; Stages is required only for `custom`; `teammate`/`maintenance` need an
Assignee filter; the Status map must resolve `todo doing done cancelled`, plus `staged` when a Deploy signal is set,
explicitly or inferred from **Statuses**; refused: stage `tickets` with Ticket source `human`, Deploy signal
`cloud-build` without a GCP Project ID, stage `delivery-watch` without a GitHub Repo). `--json` prints the fields. `--live` calls ClickUp GET /list and checks the
statuses. Exit 0 ok · 1 field errors · 3 live failed.

### 9.5 Register the project's MCP servers (Van runs)
```bash
# Figma (figma-developer-mcp pinned under ~/.local/lib/figma-developer-mcp, not npx: npx re-downloads into TMPDIR every start)
openclaw mcp set figma-<slug> '{"command":"/usr/bin/python3","args":["/home/openclaw/.openclaw/workspace/projects/_tools/figma_mcp.py","<slug>"],"connectionTimeoutMs":30000,"requestTimeoutMs":120000}'
openclaw mcp probe figma-<slug>        # must list figma-<slug>__get_figma_data and figma-<slug>__download_figma_images

# Tracker
openclaw mcp set tracker-<slug> '{"command":"/usr/bin/python3","args":["/home/openclaw/.openclaw/workspace/projects/_tools/tracker_mcp.py","<slug>"],"connectionTimeoutMs":30000,"requestTimeoutMs":120000}'
openclaw mcp probe tracker-<slug>
```
A failed probe almost always means: context file invalid, secret missing, or secret stored as kind `secret`.
Check those before touching any prompt. Jira and Linear are supported: set `**Tracker:**` and the launcher does the rest; VanPM talks to
`tracker-<slug>__*` tools regardless (Decision Q). Skip this step when the Tracker is `none`.

### 9.6 Coding-agent backend for VanDev (Decision B: agy on Gemini)
- *(not used; Van chose agy)* **Claude Code via ACP** (`docs/tools/acp-agents/`): install the `@openclaw/acpx` runtime plugin; VanDev spawns
  `sessions_spawn({ runtime: "acp", … })` with the worktree as working directory. Tracked as a background task with a run log.
- **agy (Antigravity CLI)**: `GEMINI_API_KEY="$(openclaw secrets store get GEMINI_API_KEY --plain)" agy --mode accept-edits --print "<prompt>"`
  (`--print` must be last before the prompt; it swallows the next token). Add **both** the project's Code (CWD)
  **and** its worktree root `/home/openclaw/projects/.worktrees/<slug>` to `trustedWorkspaces` in
  `~/.gemini/antigravity-cli/settings.json` during onboarding, or agy refuses the directory.
Either way: launched in background with `workdir:` = the worktree `worktree.py create` printed, never the
primary checkout, never inside `~/.openclaw`, with a notification route; run-log path + worktree path go in
VanDev's reply. The worker **writes code only**. Commit, push, PR are VanDev's own commands.

### 9.7 Worktrees: one task = one branch = one worktree = one PR
Standard pattern (Claude Code, GitKraken, pnpm docs agree): each agent task gets its own `git worktree`; nobody
edits the primary checkout; remove with `git worktree remove`, never `rm -rf`. Implemented once for all projects:

| Piece | Where |
|---|---|
| Tool (stdlib) | `~/.openclaw/workspace/projects/_tools/worktree.py <slug> create\|finish\|sweep\|list\|path` |
| Shared skill (all agents) | `~/.openclaw/skills/worktree-lifecycle/SKILL.md` |
| Worktrees | `<parent of Code (CWD)>/.worktrees/<slug>/<branch with / as __>` |
| Ledger (source of truth, flock-protected) | `<Internal Artifacts>/worktrees.jsonl` |
| PR list for humans | `<Internal Artifacts>/prs.md` (generated, never hand-edited) |

Inputs come only from PROJECT_CONTEXT (`Code (CWD)`, `Default branch`, Flow `PR base`, `Branch Prefixes`, `Internal Artifacts`),
so a new project needs **zero** tool changes.

Lifecycle:
1. **sweep** at the start of every VanDev task: `git fetch --prune` + `git worktree prune`. For a branch whose
   remote is gone (GitHub auto-deleted it after merge) it asks GitHub for the PR through `git_env.py`; if MERGED/CLOSED
   and the PR head equals the local tip, the worktree and local branch are removed even when `finish` was skipped.
   Uncommitted files are never deleted (`KEPT … tell Van`). Reports `UNMANAGED` worktrees and a dirty/off-branch
   `PRIMARY` checkout; never fixes them.
2. **create** fetches, branches from `origin/<Flow PR base>` (or checks out `origin/<branch>` if it exists, for
   review fixes / QA / review), enforces the Branch Prefixes, verifies HEAD == start SHA, copies `.worktreeinclude`
   files, prints the preparation receipt the `coding-agent` skill requires. Idempotent.
   **Refuses** a branch that another agent's worktree still holds (agents never share a folder); that agent must
   push and `finish` first.
3. **finish** after VanDev pushes and opens the PR (`finish <branch> --pr <url>`): removes the worktree only if
   nothing is local-only (clean, upstream set, 0 unpushed commits); otherwise exit 2 and the folder is kept with
   the reason. Never `--force`. A no-op checkout of a branch already on origin (QA, review) keeps the branch's
   `pushed`/`pr_open` ledger row (it used to mark a live PR `abandoned`).
4. The task branch is pushed and its PR opened right after the lane commit (a task-branch push deploys nothing),
   so the review happens on the PR and QA/Reviewer `create` their **own** worktree from origin when they need the
   files; handoffs pass slug + branch, never a path.
5. The heartbeat runs `sweep` once a day (watcher `SWEEP_DUE`) and reports worktrees older than 3 days.

Never use OpenClaw managed worktrees (`sessions_spawn … worktree: true`, `cwd`) for project code: a spawned
agent's `cwd` must be inside an agent workspace, so OpenClaw worktrees the settings repo instead (24 of them,
297 MB, zero code, on the old box). If any exist: `openclaw worktrees gc`.

GitHub repo setting (repo admin, once per project): **Settings → General → Automatically delete head branches = on**.
That is the merge signal `sweep` reads, and it works for squash merges.

Repo hygiene (VanDev ticket per project, optional): `.worktreeinclude` (gitignore syntax) at the repo root lists
ignored files `create` copies into each worktree (e.g. `.env.local`). Prefer **pnpm** over npm for monorepos: with
npm each worktree needs its own full `node_modules` (881 MB for fms-studio); pnpm's shared store makes it near zero.

### 9.8 Write and validate PROJECT_CONTEXT.md
Copy **the one template** `projects/_template/PROJECT_CONTEXT.md` (Section 10; no copies inside skills), fill every
placeholder except `## Stack`, then:
```bash
python3 ~/.openclaw/workspace/projects/_tools/validate_context.py ~/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md
```
Then spawn VanPM (isolated; **no cwd, no worktree**; it reads the repo by absolute path): fill `## Stack` from the
repo ("unknown" is allowed, an invented framework is not; check the lockfile before naming a library), run the
validator `--live` (GET the ClickUp list, paste real list name + statuses), report the list name so Van confirms
it is the right list. Wrong list → fix the ID → repeat.

### 9.9 Final checks, register, persist
```bash
python3 ~/.openclaw/workspace/projects/_tools/worktree.py <slug> list      # must run clean
python3 ~/.openclaw/workspace/projects/_tools/git_env.py <slug> --check    # token reaches the repo
python3 ~/.openclaw/workspace/projects/_tools/gcloud_env.py <slug> -- gcloud auth list
```
- Add both paths to agy `trustedWorkspaces` if agy is the backend (9.6).
- Append the project section to `MEMORY.md` (date, context path, list *name*, secret *names*, MCP server names, worktree root). No IDs.
- Reply to Van with: context path, list name, the four secret names, the two MCP server names, worktree root, PAT expiry date.

---

## 10. `PROJECT_CONTEXT.md` template

Copy of `~/.openclaw/workspace/projects/_template/PROJECT_CONTEXT.md` as of 2026-09-19 (1.4). **The file wins**: when
they differ, re-copy it here. Labels are parsed by `validate_context.py`, `delivery_watch.py` and `spec_index.py`; keep them exact.
```markdown
# Project Context: <slug>

<!-- Single source of truth for this project. Every agent reads this before acting.
     Keep the field labels exactly as written: tooling parses them by label.
     Validate after every edit: python3 /home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py <this file> -->

## Identity
- **Slug:** `<slug>` (lowercase, hyphens; used for directory names)
- **Display name:** <Human name>
- **Onboarded:** <YYYY-MM-DD> by <who>

## Repository
- **Git SSH Clone URL:** `<git@host:org/repo.git>`
- **SSH Alias:** `<alias or none>`
- **GitHub Repo:** `<owner/repo>` (delete this line when the project is not on GitHub; when it is
  set, the GitHub Token SecretRef below becomes required)
- **Default branch:** `main`
- **PAT expiry:** <YYYY-MM-DD> (the GitHub Token below; renew before this date or `gh` calls start failing)

## Stack
<!-- Filled by VanPM by inspecting the repo. No guesses: "unknown" is acceptable, an invented framework is not. -->
- **Layout:** <monorepo tool / single app>
- **frontend/**: <framework + version, test runner, where routes live>
- **backend/**: <framework + version, test runner, where modules live>
- **Database:** <ORM + engine, or "none yet">
- **Schema file:** <path to the ORM schema in the repo (e.g. `backend/prisma/schema.prisma`), or "none yet">
- **Deploy:** <pipeline: trigger, config files, targets, how to check builds, e.g. `gcloud_env.py <slug> -- gcloud builds list`; or "none">
- **Deploy triggers:** `<trigger-a, trigger-b>` (Cloud Build trigger names that must ALL succeed before the watcher says DEPLOYED; delete this line when there is one trigger or no Cloud Build)
- **Repo state:** <scaffold / active / legacy; commit count>

## Tracker & Design
- **Tracker Tool:** ClickUp
- **ClickUp List ID:** <digits only, copied from the list URL or list settings; never discovered by API>
- **ClickUp List name:** <as shown in ClickUp, confirmed by validate_context.py --live>
- **Figma file:** <https://www.figma.com/design/... or none>
- **Figma MCP server:** `figma-<slug>` (required when Figma file is set; delete this line when it is none)
- **GCP Environment:** <prose: which environments exist, or "none">
- **GCP Project ID:** `<gcp-project-id>` (delete this line when the project has no GCP; when it is
  set, the two GCP SecretRefs below become required)
- **GCP Region:** `<region>`
- **SecretRefs:**
  - Tracker: `CLICKUP_API_TOKEN_<SLUGUPPER>`
  - Design: `FIGMA_API_KEY_<SLUGUPPER>` (delete this line when Figma file is none)
  - GCP Key Vault: `GCP_SA_KEY_<SLUGUPPER>_<ENV>`
  - GCP Key JSON: `/home/openclaw/.openclaw/workspace/credentials/gcp/<slug>.json`
  - Reach GCP only through `projects/_tools/gcloud_env.py <slug> -- <command>`; there is no
    ambient gcloud default and `gcloud` run bare will not be pointed at this project.
  - GitHub Token: `GITHUB_TOKEN_<SLUGUPPER>` (env-kind vault entry; fine-grained PAT scoped to this
    repo only: Contents + Pull requests + Commit statuses read/write, no Administration)
  - Reach the GitHub API only through `projects/_tools/git_env.py <slug> -- gh <args>`; bare `gh`
    has no login on this box.

## Workflow Rules
<!-- Statuses: exactly as on the board, confirmed by validate_context.py --live. -->
- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`
- **Create status:** `to do`
- **Branch Prefixes:** `feature/`, `bug/`
- **GitHub bots:** `<bot login>` (accounts whose PR comments are not review feedback, e.g. a PR-description bot; `*[bot]` accounts are always ignored; delete this line when none)
- **Install command:** `<exact command run inside a fresh worktree, e.g. npm ci>`
- **Dev/QA Test Commands:** explicit, never inferred (inferring them hung QA 28 times on the old box). VanPM fills these during onboarding after running each one once in a worktree.
  - Tests: `<exact command that runs once and exits>`
  - Lint: `<exact command>`
  - E2E: `<exact command, or "none yet: first feature carries [INT] Set up Playwright E2E runner">`
  - Forbidden: `<any watch-mode target>`
- **Known repo issues:** <what an agent will hit in this repo, date found, "report and stop" or the workaround; mark Resolved with a date; or "none">

## Flow
<!-- How THIS project works. Parsed by validate_context.py; see ~/OPENCLAW_ARCHITECTURE.md §4.
     Profiles: `factory` (we plan, build, review, QA, watch deploys) · `teammate` (Van is one dev on a human
     team: tickets exist, agents only take Van's) · `maintenance` (bug fixes only) · `custom` (set Stages).
     Every line except Profile is optional; the profile supplies defaults. -->
- **Profile:** `factory`
- **Stages:** `spec`, `tickets`, `review`, `internal-qa`, `merge-gate`, `delivery-watch`
- **Ticket source:** `agent` (`agent` = VanPM creates tickets · `human` = the team does · `both`)
- **Assignee filter:** `any` (teammate/maintenance: Van's tracker user id or email; only those tickets are claimed)
- **Branch model:** `feature-branch` (`feature-branch` = one branch per feature · `ticket-branch` = one per ticket)
- **PR base:** `<branch PRs go into; defaults to Default branch>`
- **Merge by:** `van` (`van` or `humans`; agents never merge)
- **Deploy signal:** `cloud-build` (`cloud-build` = watcher waits for Cloud Build before `staged` · `none` = merge is the signal)
- **Status map:** `todo=to do`, `doing=in progress`, `staged=qa`, `rejected=rejected`, `done=complete`, `cancelled=cancelled`, `hold=on hold`
- **Chat channel:** `<discord:channel id>`
- **PR conventions:** `none` (or the repo path of its PR template / CONTRIBUTING.md; agents follow it)

## Ticket conventions (enforced by the PM's `feature-breakdown` skill)
- One parent ticket per user-visible feature: `[Feature] <Area>: <Outcome>`.
- Subtasks per engineering lane, only the lanes the feature touches: `[FE]`, `[BE]`, `[DB]`, `[INT]`, `[QA]`, `[SPIKE]`. Each ≤ 8h.
- Every ticket body follows the template: Context · User story · In scope · Out of scope · Acceptance criteria (Given/When/Then, falsifiable) · Technical notes · Depends on/blocks · Test notes · Definition of done.
- Tags: `agent-created` + lane tag. Priority: urgent=1, high=2, normal=3, low=4. Estimates in `time_estimate`.
- Dependencies pushed as ClickUp task links. `[DB]` → `[BE]` → `[FE] wiring`; `[QA]` last.
- Specs live in `artifacts/specs/<feature-slug>.md`; the push writes `<feature-slug>.clickup.json` next to it.

## Artifact Routing
- **Code (CWD):** `/home/openclaw/projects/<slug>`
  Primary checkout, **read-only for agents** and kept on the Default branch. All code work
  happens in per-task worktrees under `/home/openclaw/projects/.worktrees/<slug>/`, created and
  removed only by `projects/_tools/worktree.py <slug> ...` (shared `worktree-lifecycle` skill).
  PR history: `prs.md` in Internal Artifacts (generated from `worktrees.jsonl`).
- **Internal Artifacts:** `/home/openclaw/.openclaw/workspace/projects/<slug>/artifacts/` (`specs/`, `patches/`, `reviews/`, `qa/`)
```

---

## 11. Smoke test (run before the first real feature)

1. `free -h`, `df -h /tmp`, and the `/proc/<pid>/environ` TMPDIR + PATH check from 4.2 (PATH contains `~/.local/bin`; `gcloud`, `gh` resolve).
2. `openclaw gateway status --deep` — healthy. (**Not** `openclaw doctor`: see 12.6.)
3. `openclaw mcp probe figma-<slug>` and `openclaw mcp probe tracker-<slug>` list tools.
4. `python3 validate_context.py <ctx>` → VALID; VanPM `--live` → LIVE OK with the right list name.
5. `git_env.py <slug> --check`, `gcloud_env.py <slug> -- gcloud auth list` succeed; bare `gcloud config get project` prints `(unset)`; bare `gh pr list` fails.
6. `worktree.py <slug> list` runs clean; `create feature/smoke --agent developer --task smoke` then `finish feature/smoke` removes it as `abandoned`.
7. `python3 _tools/validate_team.py` passes.
8. In Discord: "@VanOpenClaw what projects are onboarded?" → answers from MEMORY.md within seconds, no spawn.
9. "@VanOpenClaw write the spec for <tiny feature> in <slug>" → VanPM spawned, spec file appears, summary relayed, waits for go.
   Then check the spawned session's policy: `openclaw gateway call tools.effective --params '{"sessionKey":"<childSessionKey>"}'`
   must list `tracker-<slug>__*`, `figma-<slug>__*`, and `exec`. If any is missing, main has a deny list (5.3).
10. Headless check of each specialist: `openclaw agent --agent developer -m "Project <slug>. List the test commands from PROJECT_CONTEXT and stop."` (`-m` is required).
11. `openclaw tasks audit` shows nothing `stale_running`; `openclaw sessions --all-agents --active 60` is quiet.
12. `delivery_watch.py <slug> --dry --since <a week ago>` lists past merges as DEPLOYED/BUILD_FAILED with the right
    build ids, and reads the ClickUp list without errors. Then run it once without `--dry` to set `watch_since`.
13. Gate check (no network write): `git_env.py <slug> -- gh pr merge 999999` → "refused"; `gh pr create -B <not the PR base> …`
    → "refused"; `gh api -X POST repos/<owner>/<repo>/statuses/abc -f state=success` → "refused".
14. Review status (after the token has Commit statuses): on the first reviewed PR, `git_env.py <slug> --review-status <pr> --dry`
    prints `DRY openclaw/review=success …`; after VanReviewer runs it for real, `gh pr view <pr> --json statusCheckRollup`
    shows `openclaw/review` SUCCESS. Only then add the ruleset rule (a required status that never arrives blocks every merge).
15. `python3 ~/.openclaw/workspace/_tools/lint_workspace.py` → 0 FIX.

---

## 12. Learnings (what actually went wrong, and the fix that stuck)

### 12.1 Host and memory
- **`/tmp` tmpfs + `TMPDIR=/tmp` in the unit = the OOM root cause.** 1.9 GB of dead npx dirs in 11 minutes,
  three OOM kills, gateway "using 6 GB" while its Node process was 2.65 GB (the rest was tmpfs charged to its cgroup).
  A full RAM disk presents as "out of memory", never "out of disk". Fix: 3.3 + 4.2. Gateway went 6.0 G → 1.7 G.
- **"Agents went crazy" = they were being killed mid-tool-call.** An amputated tool process produces confused
  continuation, not a clean error. Before suspecting a model or prompt: `free -h`, `df -h /tmp`,
  `journalctl --user -u openclaw-gateway.service | grep "OOM killer"`.
- Anything run **by hand** still writes to `/tmp` unless the shell exports TMPDIR (3.3). The gcloud SDK tarball,
  a stray repo clone, and `node-compile-cache` were 800 MB of RAM on the old box. `/tmp/openclaw` is the log dir; keep it.
- `openclaw secrets …`, `openclaw config schema`, `openclaw doctor` each start a second Node process. On a tight box
  that alone can tip the OOM killer. Read sqlite directly for checks (Section 6).
- **"gcloud not installed" was PATH, not install.** The SDK sat in `~/google-cloud-sdk`; only `~/.bashrc` knew.
  Agents diagnosed deploy failures from pasted logs for a day instead of reading them. Fix: symlinks in `~/.local/bin` (3.2).

### 12.2 Config and tool policy
- **Spawned sessions inherit the spawner's `tools.deny`.** `exec` denied on main → ~20 developer sessions with
  `inheritedToolDeny` containing `exec`, zero commands run, VanDev writing `create_pr.sh` and asking Van to `/approve`
  it, then launching `agy` "as a glorified script-runner" to run `git push` and `gh pr create`. Dropping `exec` from
  the deny but keeping `figma-*`/`tracker-*` moved the problem: the spawned VanPM inherits those (2026-09-19).
  **Main's deny list is empty. Period.** Restrictions live on the specialists (5.4).
- **A queued turn keeps the old tool policy after a hot reload.** The 09:34 message that resumed after `/stop`
  still spawned no-shell workers. `/stop`, then `/new`, then re-send. Verify with `tools.effective`, not the stored entry.
- **`tools.allow` is exclusive.** `allow: ["message"]` removed every other tool: "No callable tools remain" on every turn.
  Use `deny` / `alsoAllow`. Always `--dry-run` first. Never let an agent hand-edit `openclaw.json`.
- **No usable fallback = no fallback.** One capped provider in `fallbacks` burned 2m20s of retries per turn.
- `openclaw doctor` (even `--lint --all`, documented read-only) **stops the gateway** on systemd installs and leaves
  it stopped (upstream bug: post-stop ownership check never sets `managerUid`). Use `openclaw doctor --json` or
  `openclaw gateway status --deep`. If doctor ran, `systemctl --user start openclaw-gateway.service`.
- `agents.entries.*.tools.deny` hides MCP tools but does not stop the server spawning (5.4/5.5).
- `sessions_spawn` without `agentId` runs the child in the caller's workspace. Always set it and `visible: true`.
  `worktree: true` + project `cwd` worktrees the **settings repo** (11 in Section 2). Never set them.
- `agents.defaults.subagents.allowAgents: []` + explicit list on `main` = only main can spawn. Keep it.
- `tools.loopDetection.enabled: true` exists and was off until 2026-09-18. Keep it on (5.2).
- Invalid config blocks `openclaw config set`; fix the one bad field surgically (python, 0600), backup **before**
  reading (a backup taken after the bad edit captured the broken state).

### 12.3 Secrets and per-project isolation
- Secret kind `secret` is write-only forever; launchers need `env`. Names ending `_API_KEY`/`_TOKEN` default to `secret`. Always pass `--kind env` for those.
- `openclaw secrets store list` prints **env-kind values in plaintext**. Verify with the sqlite query instead (Section 6).
- A secret stored through the chat `!` prefix with `--value-file -` is stored **empty** (no stdin). Real SSH terminal only.
- A typo'd secret name (`FIGMA_API_KEY_FMS_STUDIO` vs `FIGMA_API_KEY_FMSSTUDIO`) lived in two USER.md files and a script
  for days and was repeated as fact. Names live in PROJECT_CONTEXT only; verify in the vault table before stating one.
- The tracker MCP launcher read `TRACKER_API_TOKEN_*` from the environment (a stray rename script had changed
  CLICKUP→TRACKER in skills), which nothing set, so every ClickUp call failed silently for a day. Every launcher now
  resolves name from PROJECT_CONTEXT and value from the vault; **no environment fallbacks, no hardcoded project**.
- Global `GOOGLE_APPLICATION_CREDENTIALS` + `gcloud config set project` pinned an **admin** SA of project #1 as the
  machine default; project #2 would have silently used it. Fix: `gcloud_env.py` + `gcloud config unset project/account`.
- `gh` was never installed and no GitHub token existed, so agents could push but only ever produced `/pull/new/` links
  and called them "the PR". Fix: `gh` binary + `git_env.py` + `GH_REPO` (gh cannot parse an SSH-alias remote) + a
  "real PR URL only" rule.
- Two systemd override backups contained plaintext ClickUp/Figma tokens. Rotate; never back up overrides.
- A live token printed by a "shape check" script went into a transcript and to the model provider. Never print SecretRef ids.

### 12.4 Orchestrator behaviour
- **Blind relay.** Main reported "the developer used the coding agent" when VanDev had hand-run 110 CLI commands
  in two hours and the agent ran 3 times (only when Van forced it). Main was not lying: it had no shell then and its
  prompt said "relay verbatim". Fix: "Verify before you relay" (7.2) + VanDev must give run-log and worktree paths.
- **Doing the specialist's work.** Main once ran the repo scaffold itself with raw shell. The tool deny that
  followed broke the workers (12.2). The lock is now the prompt rule "shell is for checking, not doing" plus
  routing (main never gets a project cwd), and Van reviews main's `exec` use in transcripts if it drifts.
- **Rationalising a broken design.** With the shell gone, main explained to Van at length why "using a full AI
  coding assistant as a glorified script-runner" was a deliberate security architecture. It was a leaked deny.
  When an agent invents a justification for an obviously wasteful step, check the tool policy first.
- **Silence.** Main went quiet for minutes while spawning/waiting. Fix: "answer first, then delegate"; first message
  within seconds; say "still waiting on VanDev" rather than nothing.
- **Sycophancy after breaking things.** Long apologies, then guessed config keys, then broke more. The rule: check
  every key against the bundled docs, show before/after, wait for yes.
- Main hand-wrote curl scripts to create 11 tickets, bypassing VanPM, producing one screen-sized ticket each.
  Root cause: no decomposition rule existed anywhere. Fix: `feature-breakdown` skill + main never calls tracker tools.

### 12.5 Specialist behaviour
- **"Stuck at typing" = a no-progress tool loop, not a hang.** VanDev rewrote and re-ran one check script ~200
  times over 34 minutes with byte-identical output. Discord shows typing until the turn ends; messages sent
  during it queue behind it and get no reply. `model-fetch … status=200` every 7 s the whole time. Not OOM, not network.
  A **gateway restart does not fix it**: the lane is aborted and the pending input is re-dispatched, so the same
  loop resumes 40 s later. Fix: `/stop` in Discord, then `/new`; `tools.loopDetection`; the 3-poll rule; no specialist chat bots.
- **Second loop type: degenerate model loop on an oversized session.** Main (12k+ events, ~150k tokens per call)
  answered "give me the PR link" with `get_goal {}` → `{"status":"missing"}`, empty text, identical thought signature,
  every 5–10 s (311+ calls in 33 min, ~$0.037 each). Not a rule problem. Fix: `/stop` then `/new`; keep sessions
  small (isolated spawns, compaction precheck, `/new` after long threads).
- **QA timed out 28 of 38 runs** because the project's Nx config set vitest to watch mode, so the inferred `test`
  target never exited and hit the 1800 s cap. PROJECT_CONTEXT said "AI will infer test commands". Fix: explicit,
  non-watch commands in the context file; a "Forbidden" line; `runTimeoutSeconds` on spawn.
- **Uncommitted file, shipped PR.** PR #31 went out without its `.gcloudignore` because the file was written but never
  added. Rule: `git -C <worktree> status` must be empty after `git add`, before push. `worktree.py finish` refuses to
  remove a worktree with local-only files for the same reason.
- **Everyone edited the primary checkout.** With OpenClaw managed worktrees silently pointing at the settings repo,
  dev, QA, and reviewer all worked in `/home/openclaw/projects/<slug>` at once. Fix: `worktree.py` + read-only primary.
- VanDev created its own ClickUp ticket for a CI fix, desyncing the board. Fix: `tracker-*` denied for developer.
- VanDev missed the SA key file because `gcloud` was not on PATH and assumed the host had no credentials. Fix: PATH
  symlinks; launcher restores the key from the vault and names the missing field; "do not hunt for credentials".
- Developer over-reported ("used agy") to look compliant. The AGENTS.md now says an honest "I hand-coded it" is correct
  and a false delegation claim is the one thing that is not.
- VanDev patched a deploy symptom (`npm install --package-lock-only` inside `dist/`) instead of syncing the lockfile at
  the root. Van: "we should fix the root cause then perfectly sync them." Rule for the dev prompt: a workaround in the
  deploy step is a finding, not a fix; sync sources, not artifacts.
- Specialist sessions ballooned (461 exec calls, 1761 events, 113 % of context, 150 MB sqlite). Isolated spawns per
  task + `midTurnPrecheck` compaction + no long-lived chat sessions.

### 12.5b Planning and ticket hygiene (2026-09-19)
- **Only VanPM touches the tracker.** VanDev created two duplicate tickets via MCP, then `openclaw secrets store
  list` (printed the token: rotate), then curl, because main said "ensure a ClickUp ticket exists". Fix: developer
  `tools.deny: ["tracker-*"]`, AGENTS.md "tracker writes → VanPM only". The secret store is team-scoped, so
  any agent with exec can still read env-kind tokens: this lock is policy, not a wall.
- **Status flow** *(superseded the same day by 12.5d: `qa` = deployed to staging; the table in 8.1 is current)*:
  `to do` → `in progress` (VanPM claims) → `qa` (review APPROVED) → `complete` per ticket after the PR is **merged**,
  parent last; `on hold` if the spec is blocked.
  `tracker_status.py` needs `--only "<title>"` or `--all`. Re-push never changes status.
- **Planning in isolation caused duplicates and gaps** (two ORM setups, `albums` vs `events`, columns "added
  later" by no ticket, three umbrella specs over the same screens). Fixes, all project-agnostic:
  - `projects/_tools/spec_index.py <slug>` writes `specs/_index.md` (one line per feature; ~5 KB for 18). VanPM
    reads it instead of every spec. Finished specs move to `specs/_done/`, replaced ones to `specs/_superseded/`.
  - `specs/_planned-data.md` (template in `projects/_template/specs/`) = planned-not-built columns and their
    owning ticket; rows are deleted when the `[DB]` ticket merges. Built schema = **Schema file** in `## Stack`.
  - `tracker_push.py` rejects: Figma-node overlap with an active spec, 2nd ORM setup / same `CREATE` table,
    unknown `Depends on (other feature)` titles, hedge words ("(or", "(if", "if missing", "assuming").
    Exit 3 on titles ≥ 82 % similar to any live ticket (`existing_id:` adopts, `--allow-similar` overrides).
    Skips tickets whose description changed in ClickUp since the last push (`desc_hash` in the marker;
    `--overwrite-edits` overrides). Regenerates the index after a push.
  - `tracker_scan.py --context <CTX>` lists live tickets no spec knows about (made by people).
- **Scale path:** markdown index to ~100 open features; then the same generator can emit SQLite; long term
  the tracker (custom fields: Figma node, tables) + real schema are the sources and specs are drafts.

### 12.5c Workflow audit (2026-09-19): the design had almost never run

A read-only audit of every stage (code, config, all agent transcripts, git, GitHub) found that
only one feature (09-17 morning) went through spec → build → review → QA → approval; ~28 PRs
after it had no review or QA, and PR #15 (a fresh scaffold) wiped merged work from `Development`.
What changed, and why:
- **Silence is not a yes.** `ask_user` returns "No answer arrived; proceed with best judgment" on
  timeout, and main pushed twice on it. Main AGENTS.md + the skill now treat it as NO.
- **main's deny must stay `[]`** (5.3). `["figma-*","tracker-*"]` had crept back, so every VanPM
  main spawned lost ClickUp reads (the claim/SKIP check was impossible) and Figma.
- **No specialist bots.** A `developer` Discord account was bound straight to VanDev (5.8), which
  bypassed every gate. Binding removed, account disabled.
- **Branch model** *(push timing superseded at 13:04: push + PR right after the lane commit, review on the PR;
  see 12.5e)*. One branch per feature, lane tickets strictly one at a time; VanDev pushes the
  task branch right after an APPROVED review (pushing a task branch deploys nothing) and runs
  `finish`, so VanQA/VanReviewer `create` their own worktree. `worktree.py create` now refuses a
  branch another agent's worktree still holds; `finish` of a no-op checkout keeps the branch's
  `pushed`/`pr_open` row (it used to mark a live PR `abandoned`).
- **Review file carries the SHA**, one line per acceptance criterion; the PR head SHA must equal it (still true: it is
  what `--review-status` checks, 12.5e).
- **Statuses:** `tracker_status.py --get` (read) and `--claim` (GO/SKIP) exist; parent and `[QA]`
  move too; `on hold`/closed-PR exits defined; re-push never changes status (the `status:` header
  is create-only). Table in the project-orchestration skill.
- **Nobody merges but Van.** Close-on-merge and failed Cloud Builds are checked by the heartbeat,
  which reports to the project's Discord channel, not Telegram.
- **Secrets:** the PM skill told VanPM to `secrets list`, which printed the ClickUp token 4 times.
  Every AGENTS.md now forbids listing; backups should run with `--exclude-secrets`.
- **fms-studio test command:** `nx test-ci` needs Nx Cloud (ciTargetName atomizer); interim is
  `npx vitest run` inside the project folder.

### 12.5d Delivery flow: ClickUp `qa` = on staging (2026-09-19, Van's design)

- `in progress` covers all internal work (VanDev, VanReviewer, VanQA, PR, PR feedback).
  `qa` = merged **and** every Cloud Build of a commit containing the merge succeeded;
  external QA sets `complete` or `rejected` (renamed from `for development`).
- `projects/_tools/delivery_watch.py <slug>` (stdlib, read-only) joins GitHub PRs, Cloud Build
  (`COMMIT_SHA` per build, ancestry via `git merge-base --is-ancestor`) and ClickUp, and prints
  ACTIONs (PR_FEEDBACK, DEPLOYED, BUILD_FAILED, NO_BUILD, PR_CLOSED, REJECTED, FEATURE_COMPLETE,
  STALE_WORKTREE, SWEEP_DUE) with `--ack`. The heartbeat (every 15 min) carries them out.
  PRs link tickets through ClickUp URLs in the PR body; bots listed under `GitHub bots:` in
  PROJECT_CONTEXT are ignored; agent replies start with 🤖.
- **Enforced, not prompted:** `git_env.py` refuses `gh pr merge`/the merge API, and refused
  `gh pr create` unless `reviews/*.md` had `APPROVED` + `Reviewed SHA:` equal to the branch head on
  origin. Added after main opened PRs #33/#34 unreviewed minutes after the prompt-only rule was written.
  *(Removed at 13:04 the same day by main itself; replaced by the merge-time check in 12.5e.)*

### 12.5e The review gate an agent deleted, rebuilt at merge time (2026-09-19)
- 13:04: Van asked for reviews to happen on the GitHub PR. Main, whose rule is "shell is for checking", rewrote
  `git_env.py`, its own AGENTS.md and the orchestration skill in six minutes and deleted the PR-create review gate
  (the function stayed in the file, never called, and its header comment kept describing the gate). The linter's
  `git status` check surfaced it hours later. Lesson: a request can be legitimate while the path is not; framework
  changes go through a Claude Code session with Van (7.2, architecture §6.9).
- The gate moved to where it cannot be edited by an agent: **merge time, enforced by GitHub**. VanReviewer runs
  `git_env.py <slug> --review-status <pr>`, which sets the commit status `openclaw/review` on the PR head only when a
  saved review file names that head; any later push is a new SHA without it. A repo ruleset on the PR base requiring
  `openclaw/review` makes GitHub refuse the merge. `git_env.py` refuses every other status write.
- Needs the token permission **Commit statuses: Read and write** (fms-studio's token returned 403 for status reads and
  writes on 2026-09-19). Without it, `gh pr view --json statusCheckRollup` returns an **empty list, not an error**:
  empty never means "reviewed".
- A required status applies to every PR into that branch, **including dependabot and human PRs**: either VanReviewer
  reviews those too or Van keeps a bypass for himself in the ruleset. On team repos it is the team's decision.
- The shared skill `~/.openclaw/skills/worktree-lifecycle` was in no git repo and still taught push-after-APPROVED and
  "PR after Van's yes". It is now its own repo and the linter checks it, plus flags any other shared skill.

### 12.5f The delivery watcher's silent stall: backticks, and blame by ancestry (2026-09-19)

Van: *"it is claiming that it is currently running cloud build for older or outdated commits, which actually
[is] not true"*. It was reporting `staging build running for <commit>` for five merged PRs at once while
Cloud Build had been idle for six hours, and no ticket had ever moved to `qa` on its own.

- **A field parsed with its backticks still attached stopped the whole pipeline.** `deploy_triggers` was the
  one `OPTIONAL` pattern that captured the raw line, so the expected trigger names came out as
  `` ['`deploy-frontend-staging', 'deploy-backend-staging`'] ``. Those match no real trigger, so
  `expected.issubset(...)` was never true and **every commit was classified `running` forever** — including
  commits whose builds had all succeeded. `DEPLOYED` could never fire (no ticket moves), and `BUILD_FAILED`
  sits behind `if failed and not running`, so failures could never fire either. The watcher printed
  confident, wrong notes instead of erroring: it had exactly one poisoned value and no way to notice.
  Introduced 17:20–18:00 the same day with the per-project Flow profile; it had worked that morning.
  Fix: normalise the field like `branch_prefixes` (accept `` `a, b` ``, `` `a`, `b` `` and bare `a, b`,
  drop an unfilled `<placeholder>`), and never let "a trigger we expect has not reported" mean *running*
  for longer than `NO_BUILD_AFTER_MIN` — after that, judge the commit on the builds that did run and name
  the trigger that never fired.
- **"Which commits contain my merge?" is the right question for success and the wrong one for failure.**
  Candidates are every built commit descended from the PR's merge commit, which is correct for `DEPLOYED`
  (a later green build genuinely puts an earlier PR on staging, so stacked PRs and "a newer PR that includes
  mine" already worked). Reused for failure it made every earlier PR guilty of a later commit's breakage:
  one red build resolved to a single `BUILD_FAILED` carrying five unrelated tasks' tickets. Blame now lands
  only on the PR whose own merge commit is red; the rest wait and deploy themselves on the next green.
  A red commit that belongs to no PR on the base (a direct push, another team) is reported on its own
  instead of being lost. Staging is one environment, so consecutive reds are one outage: act on the newest,
  note the rest — otherwise a streak of failed fix attempts files a bug ticket and spawns a VanDev for each.
- **The watcher acted on every human's PR on the base branch.** Only `*[bot]` and `dependabot/` were skipped,
  so any teammate's open PR produced `PR_FEEDBACK` — which spawns VanDev to push commits to their branch.
  Ownership is now the project token's own account (`gh api user`), with branch prefixes as the fallback when
  that lookup fails. Identity, not branch naming: `fix-chokidar-deps` and `fix-frontend-deploy` are ours and
  match no prefix, and a teammate can name a branch `feature/…` at any time. Someone else's PR is still
  watched for a red build, and still moves our tickets when its body links them; it is just never acted on.
- **Reading the tool's own output is not verification.** Everything above was invisible until the builds were
  listed straight from Cloud Build and compared with what the watcher said about the same commits. Do that
  before trusting a watcher's summary — `gcloud_env.py <slug> -- gcloud builds list --limit=20 --format=...`
  against `delivery_watch.py <slug> --dry`, and `--dry --since <older>` to replay a path that never fires.

### 12.7b Development-only and the toolchain seam (2026-09-20)

- **A capability you did not name is a capability you have.** `skills.entries` had 30 skills set
  `false`, which read like a lockdown - but 21 bundled skills were never named at all, so `weather`,
  `notion`, `meme-maker`, `taskflow`, `clawhub`, the Apple skills and `peekaboo` were all live
  (28 ready for main). Denylists rot as the upstream package adds skills; `skills.allowBundled` is an
  allowlist and cannot. It does not cover workshop skills under
  `~/.openclaw/agents/*/agent/workshop-skills`, which had to be moved by hand.
- **An active USER.md directive beats any AGENTS.md edit.** "Always act as Van's main agent, **not a
  dev-only orchestrator**" was `status: active` while the guide's own mission statement said
  "software development delivery … nothing else". Change the directive first, or the prompt edit is
  decoration.
- **A vendor name in a tool name becomes a config dependency.** `clickup_update_task` was load-bearing
  in `project-manager.tools.deny` *and* in the linter's check of that list, so the tracker could not
  change without editing an agent's tool policy. Neutral names (`tracker_update_task`) removed that
  coupling. Re-pointing the MCP server and renaming the deny entries had to be **one** config patch:
  either order alone leaves VanPM briefly holding live write tools.
- **Validation failure is fatal to every consumer.** `delivery_watch`, `worktree`, `git_env`,
  `gcloud_env`, `figma_mcp`, `spec_index` and the PM scripts all `die()` on an invalid context file.
  So "the tracker field is wrong" also meant "no worktree and no PR". Anything a project may not have
  must be *conditional*, never required - the pattern Figma and GCP already used and the tracker did not.
- **A regex that backtracks can make a guard inert.** The "`## Stack` is unfilled" check used
  `\*\*[A-Za-z/]+:\*\*\s*[^<\n]`: `\s*` matches empty and `[^<\n]` then matches the *space*, so
  `- **Layout:** <placeholder>` passed. Every unfilled template has always passed a check written to
  catch exactly that. Anchor on the first non-space character.
- **A prompt-level limit needs a config-level floor.** `runTimeoutSeconds` was passed per spawn by the
  orchestration skill. With `agents.defaults.subagents.runTimeoutSeconds` unset, a spawn that *omitted*
  it fell back to `0` - no timeout at all. The rule was right; nothing caught the one time it was forgotten.
- **Verify a refactor against the live system, not its own output** (12.5f again). Every tracker/CI
  change here was checked with `validate_context.py --live`, `delivery_watch.py --dry` (byte-identical
  notes before and after), a 7- and 30-day `--dry --since` replay, and a real `tracker_get_task` through
  the MCP server - not by reading the new code.
- **A third-party skill is prompt text you did not write.** `code-review` was an unedited ClawHub
  import: it carried `npx clawhub@latest install` *inside* the skill and prescribed a review format
  that contradicted the one VanReviewer's AGENTS.md requires. Two formats, no precedence marker.

### 12.6 Operations cheat sheet
```bash
# health
free -h; df -h /tmp; openclaw gateway status --deep
journalctl --user -u openclaw-gateway.service -n 200 | grep -iE 'OOM|lane task error|invalid|no callable'
# who is busy / stuck
openclaw sessions --all-agents --active 60
openclaw tasks audit                 # stale_running → openclaw tasks cancel <id>  (maintenance will NOT prune them)
openclaw worktrees gc                # OpenClaw managed worktrees only; project worktrees: worktree.py <slug> sweep
# what tools a live session really has (after a hot reload the stored entry can be stale)
openclaw gateway call tools.effective --params '{"sessionKey":"agent:developer:subagent:<uuid>"}'
# read a transcript (CLI redacts tool args; sessions are sqlite, not jsonl)
sqlite3 'file:/home/openclaw/.openclaw/agents/<id>/agent/openclaw-agent.sqlite?mode=ro' \
  "select seq, substr(event_json,1,300) from transcript_events where session_id='<sid>' order by seq desc limit 40"
# inherited deny on spawned sessions
sqlite3 'file:/home/openclaw/.openclaw/agents/<id>/agent/openclaw-agent.sqlite?mode=ro' \
  "select substr(entry_json,1,400) from session_nodes where entry_json like '%inheritedToolDeny%' order by rowid desc limit 5"
# secrets present? (no Node process, no values printed). sqlite3 is not installed on this box: use python3.
python3 -c "import sqlite3;c=sqlite3.connect('file:/home/openclaw/.openclaw/state/openclaw.sqlite?mode=ro',uri=True);[print(f'{k:8} {n}') for n,k in c.execute('select name,kind from secret_store_entries where deleted_at_ms is null order by name')]"
# delivery watcher (what the heartbeat sees); --dry writes nothing
python3 ~/.openclaw/workspace/projects/_tools/delivery_watch.py <slug> --dry
cat <Internal Artifacts>/delivery_state.json      # pending / acked actions, watch_since
# headless turn
openclaw agent --agent <id> -m "<text>"
# memory index broken (SECRET_SURFACE_UNAVAILABLE from CLI is by design)
openclaw memory reset --agent <id> --yes   # then one headless turn that calls memory_search
```
- Restart hangs 5 min in `deactivating (stop-sigterm)` when stale tasks are `running`. Cancel them first.
- `discord: skipping guild message reason=no-mention` is normal. "Bot stopped replying" is usually **busy**, not dead:
  `lane wait exceeded … activeAhead=1` in the journal. The CLI cannot abort a Discord-owned run; send `/stop` in Discord.
- The auto-mode classifier blocks agents from: `rm`/`mv` of user files, `git worktree remove`, `openclaw tasks cancel`,
  `sessions.reset`, appending to `~/.bashrc`. Hand Van a one-liner instead (multi-line pastes break at the newline).
- Gemini's "sessions_spawn patternProperties" schema warning is harmless.

### 12.7 Scope discipline
- "Fix all" means the problems under discussion, not every problem found. A genuine repo bug (missing
  `@vitejs/plugin-react` breaking the whole Nx graph) was started as an `npm install` on a platform-fix task and
  had to be reverted. Document it in PROJECT_CONTEXT under Known repo issues; VanDev fixes it as a ticket (it was, 2026-09-18; the entry is now marked Resolved).
- Van's preferences: plain-text lettered options with a marked recommendation and one-line rationale (not
  interactive pickers); simple-terms explanations first (the desk/drawer analogy for RAM vs swap worked).

---

## 13. Decisions (closed 2026-09-19 by Van)

A Gemini 3.1 Pro stays primary (no Claude switch) · B agy on Gemini · C tracker MCP + VanPM scripts (superseded by Q) · D Discord + Telegram, both
bound to main · E active-memory off · F deploy key + repo PAT · G dreaming off · H skill-creator removed · I framework
backup remote (open) · J retention 30 d / 30 d / last 5 / weekly · K review check at merge time (`openclaw/review` +
ruleset) · **P development-only** · **Q tracker = clickup|jira|linear|none** · **R CI = cloud-build|github-actions|none** ·
**S evolve the toolchain seam, keep the pipeline**. Details and state: `~/OPENCLAW_ARCHITECTURE.md` §8.

---

## Appendix: what to copy from the old box before it is retired
```
~/.openclaw/workspace/projects/_tools/{validate_context.py,figma_mcp.py,tracker_mcp.py,gcloud_env.py,git_env.py,worktree.py,delivery_watch.py,spec_index.py}   # current 2026-09-20; copy as-is
~/.openclaw/workspace/projects/_tools/trackers/  ~/.openclaw/workspace/projects/_tools/ci/         # the provider adapters
~/.openclaw/workspace/projects/_template/PROJECT_CONTEXT.md        # current (Section 10 is a copy of it)
~/.openclaw/skills/worktree-lifecycle/                             # shared skill incl. .git; goes to the same path
~/.openclaw/workspace/_tools/{validate_team.py,lint_workspace.py,framework_offbox.py} + docs/  # or clone all six repos from the off-box copy
~/.openclaw/workspace/projects/_template/specs/_planned-data.md
~/.openclaw/workspace/skills/{project-orchestration,project-onboarding}/SKILL.md          # both current 2026-09-19
~/.openclaw/workspace/project-manager/skills/feature-breakdown/                            # keep as-is: scripts are the only tracker write path
~/.openclaw/workspace/{developer,qa-engineer,code-reviewer,project-manager}/               # whole agent repos incl. .git and skills (not memory/, DREAMS.md, media/)
~/.openclaw/workspace/AGENTS.md                                                            # main; current 2026-09-19 (silence = NO, heartbeat watcher, git_env gate)
~/.config/systemd/user/openclaw-gateway.service.d/tmpdir.conf
~/.local/opt/gh + ~/.local/bin/{gh,gcloud,gsutil,bq} symlinks (recreate, don't copy)
~/.openclaw/workspace/projects/fms-studio/PROJECT_CONTEXT.md                               # reference example of a filled file (Stack + Deploy sections)
```
Do **not** copy: `openclaw.json` (rebuild from Section 5; the old box's was fixed 2026-09-19 but carries history),
any `*.bak`, per-agent sqlite, `memory/` daily notes, `DREAMS.md`, skill-workshop proposals, the `credentials/`
directory (re-store from the vault), OpenClaw managed worktrees, `developer/test.sh` and other strays, and any shared skill
other than `worktree-lifecycle` (e.g. `beautiful-mermaid`) unless Van decided to keep it. Easiest: clone the framework repos
(git history included) instead of copying files, then run the linter.
