# OpenClaw Dev Factory — Architecture and Self-Fix Runbook

**Version:** 2.7 · **Date:** 2026-09-22 (2.7: **the design reaches the code** — VanPM downloads the screen's assets and exact tokens, not just a screenshot; `[FE]` tickets carry a `## Design fidelity` contract the push script enforces; VanDev copies assets into the worktree before agy runs, because agy cannot see the design; VanReviewer checks fidelity and gets Figma read access. Phase D. 2.6: **stress-tested** — the primary checkout is kept current and never trampled (5.3a), a cached test result is not a test run, the merge gate states what it actually verified, the daily lint is owned by the first project that VALIDATES, feedback ack ids cannot collide, and PR stages require a repo. 96 regression cases under `_tools/stress/` (75 at 2.6). 2.5: **development-only**, and the toolchain becomes pluggable — tracker and CI are adapter packages, `Tracker: none` and `github-actions` are real answers, §4.1b. 2.4: delivery watcher — success by ancestry, blame by authorship, act only on our PRs, no state waits forever. 2.3: review check moved to merge time — `openclaw/review` status; shared skill under git. 2.2: steps 6-9 done; step 10 open) · **For:** Van (van@symph.co)
**Companion:** `~/OPENCLAW_DEV_SETUP.md` ("the guide", v1.7) stays the fresh-install reference (host, config keys, every incident).
This document is shorter and answers a different question: **what is the architecture, why does the system
keep rotting, and how does it fix itself.** When the two disagree, this one wins and the guide gets edited.

---

## 0. The problem this solves

Van, 2026-09-19: *"the files eventually clutter, garbage files appear, different implementations appear, and the
system eventually breaks because it has no proper architecture."*

That is an accurate diagnosis. Evidence from this box, three weeks in:
- 11 Python tools in 3 locations, plus 4 dead scripts (`fetch_figma.py`, `test.sh`, `write_specs*.py`, `update_mcp_skills.py`), 3 diagram files and an explainer in the agent workspace, 30 unreviewed skill-workshop proposals, 47 backup entries (31 MB), 5 loose `openclaw.json.bak*` copies.
- Three tracker implementations existed at once (curl scripts, an MCP server, `tracker_push.py`), two Figma paths, two worktree mechanisms, two templates for `PROJECT_CONTEXT.md`, and a `TRACKER_`→`CLICKUP_` rename that only half happened.
- Rules lived in six `AGENTS.md` files, four skills and a 1250-line guide, so every fix was a prompt edit that the next session did not see, and config settings crept back (`main.tools.deny` twice).
- The framework directory is a git repo, but had 111 uncommitted paths: nobody could tell a deliberate file from garbage.

The root cause is not any one of these. It is that **nothing defined which files may exist, who owns them, and
when they die**, so every session added its own. The fix is an architecture with a manifest and a linter that
reads the manifest, so "is this garbage?" is a command, not an opinion.

**The goal**, in Van's words: a real developer-team assistant that acts on his behalf as a human developer, on
projects he shares with other humans (same repo, same tickets), across **many projects with different setups**,
without the system breaking. So: one framework, zero project knowledge in it; one file per project that
declares how that project works; a linter that keeps both true.

**And only that.** This is a development factory, not an assistant that also does development
(Decision P, 2026-09-20). The distinction is not decoration: an agent that may fall back to
"general assistant work" has no reason to say "nobody owns this", which is the sentence that keeps
work inside the pipeline. Scope is enforced in two places, because either alone leaks - the prompts
(main's `AGENTS.md`, `SOUL.md`, `USER.md`) and the config (`skills.allowBundled`, non-development
plugins removed). Before this, 28 skills were live for main including `weather`, `notion`,
`meme-maker` and `clawhub`, and an **active** USER.md directive read "act as Van's main agent,
**not a dev-only orchestrator**".

---

## 1. The architecture on one page

Five layers. Each has one owner, one location, one lifecycle, and a rule about who may write there.

| Layer | What it is | Location | Written by | Lifecycle | In git? |
|---|---|---|---|---|---|
| **1. Host** | OS, Node, gcloud, gh, tmpfs fix, systemd unit + drop-in | `/`, `~/.config/systemd`, `~/.local` | Van (root) | Set up once; verified by the linter | No (documented in guide §3–4) |
| **2. Platform** | `openclaw.json`, agent registrations, MCP registrations, secrets vault | `~/.openclaw/openclaw.json`, `~/.openclaw/state` | Van via `openclaw config patch` / `openclaw mcp set` / `openclaw secrets` | Desired state is encoded in the linter; drift = FIX | No (backed up by `openclaw backup`) |
| **3. Framework** | Prompts, skills, shared tools, template. **Project-agnostic; contains no project name, ID or secret.** | `~/.openclaw/workspace` (+ 4 agent workspaces inside it) | Claude Code sessions with Van, committed to git | Every change is a commit; `git status` must be empty in all six repos | **Yes**: main workspace repo + one repo per agent workspace (each has its own `.git`; the main `.gitignore` excludes them) + `~/.openclaw/skills/worktree-lifecycle` |
| **4. Project** | One context file + generated artifacts per project | `workspace/projects/<slug>/` and `~/projects/<slug>` (code) | Agents, through the framework tools only | Context file: onboarding + edits with validation. Artifacts: created by pipeline steps, archived by the watcher | Context yes; artifacts yes (history is useful); code has its own repo |
| **5. Runtime** | Sessions, transcripts, worktrees, run logs, watcher state, temp | `~/.openclaw/agents/*/agent`, `~/projects/.worktrees`, `artifacts/runs`, `$TMPDIR` | OpenClaw and the tools | Created by a task, removed by `finish`/`sweep`/TTL; never hand-edited | No (`.gitignore`) |

Three invariants make the layers hold:

1. **Manifest or garbage.** `_tools/lint_workspace.py` holds the list of every path pattern that may exist in the
   framework and project layers. A file outside it is a `FIX` line. No file is "temporary" without a lifecycle
   in the table in §3.
2. **One implementation per concern.** The registry in §2 names the single tool for each job. A second script
   that does the same job is a bug, even if it works. An agent that needs a tool the registry lacks reports
   it; it does not write one into the workspace.
3. **Desired state is checkable.** Config, layout, host settings all have an expected value in the linter.
   Changing the design = change the linter expectation and the guide in the same commit, then apply.

Run the linter any time; it is read-only and exits 1 when something needs fixing:
```bash
python3 /home/openclaw/.openclaw/workspace/_tools/lint_workspace.py
```
The heartbeat runs it once a day (§7 step 9) and posts FIX lines to the project channel. Nothing auto-deletes.

---

## 2. Registry: one tool per concern

| Concern | The one tool | Owner | Reads | Never |
|---|---|---|---|---|
| Project facts | `projects/<slug>/PROJECT_CONTEXT.md` + `projects/_tools/validate_context.py` | main (onboarding), VanPM (`## Stack`) | — | duplicated into USER.md, skills, scripts |
| Figma access | `projects/_tools/figma_mcp.py` → MCP `figma-<slug>` | VanPM (screenshots, **assets**, tokens), VanDev (missing detail only), VanReviewer (confirm a value only) | context + vault | REST calls, shared key, a second download of an asset VanPM already fetched |
| Tracker adapters | `projects/_tools/trackers/` (`for_project(fields, token)` → clickup · jira · linear · none) | shared by every tracker caller | context + vault | a provider name outside this package; a second client for the same tracker |
| Board discovery | `projects/_tools/tracker_probe.py` → the board's real name, statuses and a proposed Status map | main (onboarding step 3d) | the tracker + vault | typing a board's statuses from memory; assuming another project's mapping |
| Tracker read | `projects/_tools/tracker_mcp.py` → MCP `tracker-<slug>` (tools `tracker_get_task` / `tracker_create_task` / `tracker_update_task`; reads only for VanPM) | VanPM | context + vault | discovery of boards by API; a vendor in a tool name |
| Tracker write | `feature-breakdown/scripts/tracker_status.py` and `tracker_push.py` (**any tracker**: spec → tickets, via the adapters) | VanPM only | context + the env var OpenClaw provides for the env-kind secret + spec markers | curl, MCP update tool, any other agent |
| Human-made tickets | `feature-breakdown/scripts/tracker_scan.py` | VanPM | tracker | creating a duplicate; adopt with `existing_id` |
| Spec planning index | `projects/_tools/spec_index.py` → `specs/_index.md`, `specs/_planned-data.md` | VanPM | specs | hand edits of `_index.md` |
| GitHub API | `projects/_tools/git_env.py <slug> -- gh …` | VanDev (main read-only) | context + vault | `gh auth login`, merges, a PR base other than the Flow PR base, raw commit-status writes |
| Review result on GitHub | `git_env.py <slug> --review-status <pr>` → commit status `openclaw/review` on the PR head | VanReviewer | `reviews/*.md` (`Reviewed SHA` must equal the head) | any other status write; calling a PR ready while it is not green |
| Git push | plain `git` over the project's SSH deploy-key alias | VanDev | — | default branch, force, primary checkout |
| Cloud | `projects/_tools/gcloud_env.py <slug> -- …` | VanDev, VanQA | context + vault | bare `gcloud`, global config |
| CI adapters | `projects/_tools/ci/` (`for_project(fields, host)` → cloud-build · github-actions · none) | the delivery watcher | the host's `gh`/`gcloud` runners | holding a token itself; a provider name outside this package |
| Code checkouts | `projects/_tools/worktree.py <slug> create/finish/sweep/list` | every specialist | context | OpenClaw `worktree: true`, `git worktree add` by hand, editing Code (CWD) |
| Delivery (PR → CI → ticket) | `projects/_tools/delivery_watch.py <slug>` from the heartbeat | main (isolated heartbeat) | GitHub, the CI adapter, the tracker adapter (read) | writing anything itself; agents setting `complete` (sole exception: VanPM closes a `[SPIKE]` ticket once its findings note exists) |
| Team registry | `AGENTS.md` roster + `_tools/validate_team.py` | main | — | a second roster file |
| Architecture | `_tools/lint_workspace.py` | anyone (read-only) | everything above | deleting |
| Design docs | `docs/OPENCLAW_ARCHITECTURE.md`, `docs/OPENCLAW_DEV_SETUP.md` (`~/OPENCLAW_*.md` are symlinks) | Claude Code sessions with Van | — | a second copy; changing the design without them in the same commit |
| Off-box copy (Decision I) | `_tools/framework_offbox.py push <private repo url>` → one branch per framework repo, `refs/offbox/<name>` | Van, from a real terminal | the six repos (full-history token scan first) | git remotes on framework repos; force pushes; pushing `~/Backups/openclaw-git` |
| Code writing | coding agent (agy on Gemini, Decision B) in the worktree `create` printed | VanDev | — | git, gh, builds, tests, deploys (those are VanDev's own `exec`) |

If a job is not in this table, the answer to "which script?" is **none yet**: add a row, then the tool, in one commit.

---

## 3. File layout and lifecycle

Every path, who creates it, who removes it, when. Anything else the linter flags.

```
~/.openclaw/workspace/                        FRAMEWORK (git repo; project-agnostic)
├── AGENTS.md SOUL.md USER.md IDENTITY.md      auto-loaded for main (≤ 20k chars each)
├── MEMORY.md                                  main only: project index + lessons; never IDs/secrets
├── DREAMS.md, memory/                         OpenClaw-generated; gitignored; Decision G
├── _tools/validate_team.py, lint_workspace.py, framework_offbox.py
├── docs/OPENCLAW_ARCHITECTURE.md, OPENCLAW_DEV_SETUP.md   this doc and the guide; ~/OPENCLAW_*.md are symlinks
├── skills/project-onboarding/, project-orchestration/
├── credentials/gcp/<slug>.json                0600; restored from the vault by gcloud_env.py; gitignored
├── projects/_template/PROJECT_CONTEXT.md, specs/_planned-data.md      the ONLY templates
├── projects/_tools/<8 shared tools>           see §2 (tracker_mcp.py, not a vendor name)
├── projects/_tools/trackers/{__init__,clickup,jira,linear}.py   one module per tracker
├── projects/_tools/ci/{__init__,cloud_build,github_actions}.py  one module per CI
├── projects/<slug>/PROJECT_CONTEXT.md         PROJECT: created by onboarding, validated on every edit
├── projects/<slug>/artifacts/
│   ├── specs/<feature>.md + .tracker.json     VanPM; archived to specs/_done/ by FEATURE_COMPLETE, specs/_superseded/ when replaced
│   │                                          (`.clickup.json` from before the rename is still read everywhere)
│   ├── specs/_index.md, _planned-data.md      generated / VanPM-maintained
│   ├── specs/_figma/<feature>/*.png           VanPM screenshots; archived with the spec
│   ├── specs/_figma/<feature>/assets/        VanPM: the artwork the screen ships (image fills, icon SVGs).
│   │                                          manifest.json is COMMITTED (the contract: file → repo_path +
│   │                                          the download block); the binaries are GITIGNORED - one screen
│   │                                          is ~37 MB and rebuildable. VanDev copies them into its worktree
│   ├── patches/<feature>--<lane>.patch        VanDev; kept (history)
│   ├── reviews/<feature>--<lane>.md           VanReviewer; the saved review of a PR head (`--review-status` needs it)
│   ├── qa/<feature>.md                        VanQA
│   ├── runs/<feature>--<lane>--<utc>.log      RUNTIME: coding-agent logs; sweep deletes > 30 days
│   ├── worktrees.jsonl (+ .lock), prs.md      worktree.py ledger + generated PR table
│   └── delivery_state.json                    delivery_watch.py state
├── project-manager/ developer/ qa-engineer/ code-reviewer/
│   ├── AGENTS.md SOUL.md USER.md IDENTITY.md  auto-loaded for that agent
│   ├── skills/<one skill dir each>            feature-breakdown / agy-coding / code-review / qa-verification
│   └── DREAMS.md, memory/, media/             OpenClaw-generated; gitignored
~/.openclaw/skills/worktree-lifecycle/         shared skill, all agents; its own git repo. Anything else in ~/.openclaw/skills is a FIX
~/projects/<slug>/                             CODE primary checkout: read-only for agents, on the default branch,
                                               fast-forwarded by delivery_watch each heartbeat (see 5.3a)
~/projects/.worktrees/<slug>/<branch>/         one per task; created by worktree.py create, removed by finish/sweep
~/.openclaw/openclaw.json, .last-good          PLATFORM; every other openclaw.json.* copy → ~/.openclaw/backups/config-history/
~/.openclaw/backups/<incident-date>/           one dated dir per incident, pruned to the last 5 config backups
~/.openclaw/skill-workshop/proposals/          auto-generated; reviewed weekly, deleted if not adopted
~/.cache/openclaw-tmp/                         TMPDIR for the gateway and shells; TTL cleanup
```

Rules that follow from the table:
- Agents write **code** only inside a worktree and **files** only under `artifacts/`. A script an agent needs
  once goes to `$TMPDIR`, never into the workspace. (`developer/test.sh`, `fms-studio/fetch_figma.py` are what
  happens otherwise.)
- Backups are made by `openclaw backup` (daily, `--exclude-secrets`) plus **one** dated directory per incident.
  Ad-hoc `cp x x.bak` next to live files is forbidden; the linter counts them.
- `.gitignore` in the framework repo: `memory/`, `**/memory/`, `DREAMS.md`, `**/DREAMS.md`, `media/`, `**/media/`,
  `credentials/`, `__pycache__/`, `**/artifacts/runs/`, `**/artifacts/delivery_state.json`, `**/worktrees.jsonl.lock`.
  Everything else is either committed or a FIX, with one exception: agent artifacts under `projects/*/artifacts/`
  change on every run and agents never commit, so the linter counts them in an OK line and a Claude Code session
  commits them. (Before 2026-09-19 night they made the daily lint a permanent FIX.)
- No token-shaped string in any framework file, ignored files included (only `credentials/` holds key material).
  The linter greps for them; 2026-09-19 night it found none after an agent-written `specs/_figma/fetch.py` with
  the live Figma token (committed 2026-09-17) was removed. That token must be rotated.

---

## 4. Per-project model: data + flow profile

Multiple projects must not share one flow. The framework therefore knows **no** flow constants; every step the
orchestrator takes is switched by the project's `## Flow` section. Same tools, same agents, different pipeline.

### 4.1 The `## Flow` section of `PROJECT_CONTEXT.md` (live since 2026-09-19)
```markdown
## Flow
- **Profile:** `factory` | `teammate` | `maintenance` | `custom`
- **Stages:** `spec, tickets, review, internal-qa, merge-gate, delivery-watch`   (subset, in this order)
- **Ticket source:** `agent` | `human` | `both`
- **Assignee filter:** `<tracker user id or email of Van>` | `any`
- **Branch model:** `feature-branch` | `ticket-branch`
- **PR base:** `<branch>`   (defaults to Default branch)
- **Merge by:** `van` | `humans`   (agents never merge in either)
- **Deploy signal:** `cloud-build` | `github-actions` | `none`
- **Deploy checks:** `<check-a, check-b>`   (all must pass; Cloud Build triggers or Actions workflows)
- **Status map:** `todo=to do, doing=in progress, staged=qa, rejected=rejected, done=complete, cancelled=cancelled, hold=on hold`
- **Chat channel:** `discord:<channel id>`
- **PR conventions:** `<path to the repo's PR template / CONTRIBUTING, or none>`
```
### 4.1b The toolchain half: `## Tracker & Design`

The Flow section says how a project *works*; these say what it *talks to*. Both are
per project, and the framework knows neither.

```markdown
- **Tracker:** `clickup` | `jira` | `linear` | `none`
- **Tracker Board ID:** `<ClickUp list id | Jira project key | Linear team id or key>`
- **Tracker MCP server:** `tracker-<slug>`        (unless Tracker is `none`)
- **Tracker Base URL:** `https://<site>.atlassian.net`   (Jira only)
- **Figma file:** `<url>` | none
- **GCP Project ID:** `<id>`                      (only when the project has GCP)
- **GitHub Repo:** `<owner/repo>`                 (only when the project is on GitHub)
```

Every one of these is a **conditional vendor block**: name the capability and its
fields and credentials become required; omit it and the capability is skipped
cleanly. `Tracker: none` is a real answer - a repo with PRs and no ticket system
is a project like any other; it just cannot run the `tickets` stage.

Adapters, not branches in the callers: `projects/_tools/trackers/` and
`projects/_tools/ci/` each expose one interface with one module per provider, so
no tool above the adapter names a vendor. What a provider cannot do raises
`Unsupported` rather than silently doing nothing.

**Finished 2026-09-21:** `tracker_push.py` (spec -> tickets) runs on ClickUp,
Jira and Linear. It used to carry its own ClickUp REST client - the only reason
it refused the others - and now goes through the adapters, which gained
`attach`, `link_tasks`, `update_task` and `attachments` for the purpose. Each
was verified against the real service and read back from the server.

Porting it surfaced four bugs, every one of them an assumption about ClickUp's
shapes: the duplicate guard crashed on a plain status string; the verify step
counted `parent["subtasks"]`, which only ClickUp returns, and so printed VERIFY
MISMATCH for a Jira push that had in fact created both subtasks; the cross-spec
scan died if any marker-bearing spec in the folder was unparseable, blocking
every later push on that project; and Jira and Linear `create_task` ignored
`tags`, which would have dropped lane labels silently on exactly the trackers
being opened up. That last one is the shape to watch for - the tickets exist and
look right, and only the labels the spec index depends on are missing.

Jira needs one thing the others do not: its v3 API takes Atlassian Document
Format, not markdown, so `md_to_adf` converts headings, bullets, checkboxes,
fenced code and inline marks. A body posted as a plain string arrives as one
unreadable paragraph.

`validate_context.py` parses these. Every line is optional: Profile defaults to `factory`, Stages is required only
for `custom`, `teammate`/`maintenance` need an Assignee filter, and the Status map must resolve `todo doing done
cancelled` (plus `staged` when a Deploy signal is set), written out or inferred from **Statuses**. Scripts use the
**canonical** names (`todo doing staged rejected done cancelled hold`) and translate through the map, so a project whose board says
`Backlog / In Dev / Staging / QA Failed / Done` needs zero script changes.

### 4.2 Three archetypes (and what changes)

| | `factory` (fms-studio today) | `teammate` (Van is one dev on a human team) | `maintenance` (bug fixes only) |
|---|---|---|---|
| Stages | all six | `review, merge-gate, delivery-watch` (+ `spec` on request) | `review, merge-gate` |
| Ticket source | agent (VanPM creates from Figma) | human (tickets already exist) | human |
| Assignee filter | any | Van's tracker id: agents only pick up tickets assigned to Van | Van's id |
| Branch model | feature-branch, lanes one at a time | ticket-branch (`<prefix>/<ticket-id>-<slug>`) | ticket-branch |
| PR conventions | ours | the repo's template + CONTRIBUTING; PR body carries the ticket URL | the repo's |
| Merge by | van | humans (reviewers on the team) | humans |
| Deploy signal | cloud-build → `staged` | whatever the repo has, or `none` (on merge: `staged` if the board maps one, else `done`) | none |

The orchestration skill becomes: *read Flow → for each stage in Stages, run the step; skip the rest.* One
skill, no forks. The onboarding skill asks for the Flow answers as one checklist (defaults = `factory`).

### 4.3 Team mode (acting as Van among humans)
When Profile is `teammate` or `maintenance`:
- Only tickets whose assignee matches **Assignee filter**, or that Van hands over by name, are claimed. Every
  other ticket is read-only. `tracker_scan.py` lists human tickets; they are adopted with `existing_id`, never recreated.
- Human tickets are never rewritten. VanPM adds a comment or a linked sub-ticket; the description stays theirs.
- Branch from the project's PR base, rebase or merge it in before opening the PR when behind (`git fetch` +
  `git merge origin/<base>` in the worktree; never force-push a shared branch).
- Follow the repo's PR template, CODEOWNERS and commit conventions (from **PR conventions**). PR body carries
  the ticket URL. Every agent comment on GitHub starts with `🤖 VanDev:`; human review comments are answered
  within one heartbeat (`PR_FEEDBACK`): fix, push, then VanReviewer reviews the new head (`openclaw/review`).
- Nobody on the team merges, closes other people's PRs, edits other people's branches, or moves other
  people's tickets. Status moves happen only on Van's tickets, only through `tracker_status.py`, only per the map.
- Opening a PR from a task branch is routine (the review happens on it). Messages to other people wait for Van's
  yes; silence is a NO. **Decided 2026-09-20 (Decision O):** on `teammate`/`maintenance` projects a reply to a human
  reviewer is such a message: VanDev fixes and pushes the code without asking, writes the reply as a draft, and it is
  posted only after Van approves the text. On `factory` (only Van reads those PRs) VanDev posts it itself.

---

## 5. The eight management areas

Each: source of truth → the tool → rules → how it fails.

**5.1 Context management.** Source: `PROJECT_CONTEXT.md` (validated) for project facts; `MEMORY.md` for
lessons and the project index; daily `memory/` notes are OpenClaw's, not ours. Tools: `validate_context.py`,
`spec_index.py`. Rules: every spawn message names slug + context path (the file cannot auto-load; it is
outside every workspace on purpose); sessions are isolated per task and `/new` after long threads;
`midTurnPrecheck` compaction on. Fails as: a value copied into USER.md/skill/script (drift), or a 12k-event
session (degenerate loops).

**5.2 Ticket management.** Source: the tracker (whichever one - `trackers/`), mirrored by
`specs/<feature>.md` + `.tracker.json` markers.
Tools: `tracker_push.py` (create/update, matched by the `id:` stamped into the spec's ticket
header so a renamed title updates instead of duplicating; marker = idempotency), `tracker_status.py`
(`--get`, `--claim`, `--status`), `tracker_scan.py` (human tickets). Rules: VanPM is the only writer; canonical
statuses through the Status map; `staged` only from the delivery watcher (DEPLOYED, or MERGED when Deploy signal is
`none` and the board maps `staged`); `done` only by external QA, a MERGED action on a board without `staged`, or
VanPM closing a `[SPIKE]` whose findings note exists; tickets not created through VanPM are reported, not guessed. Fails as:
a second write path (curl, MCP update tool), or "ensure a ticket exists" sent to VanDev.

**5.3a The primary checkout must be current, and must not be trampled.**
`~/projects/<slug>` is what an agent reads when it needs to see project code: to diagnose a bug, answer a
question about the codebase, or write a spec. It was described as "kept on the default branch" for weeks
while nothing kept it there. `delivery_watch` fetches in it every heartbeat, but a plain fetch moves
remote-tracking refs and leaves the working tree untouched, so `origin/<base>` was current while the FILES
were whatever was checked out last.

Found 2026-09-21, 15 commits and two days behind. The damage is silent and total: reading it produced a bug
report for a test that had not failed in two days (the old file used a `TestingModule` and failed on
decorator metadata; the current one constructs the controller directly and passes). A spec, three tickets, a
branch and a PR were produced for a problem that did not exist. Every agent behaved correctly - the input
was two days old and nothing said so.

`delivery_watch.refresh_primary()` now fast-forwards it after the fetch. The refusals matter as much as the
refresh: **read-only for agents** means anything uncommitted, any other branch, or any divergence is a
person's work in progress, so each is reported in `errors` and left strictly alone - never reset, never
switched. `--dry` reports staleness without moving, because silence there would hide the problem it exists
to name. Regression: `_tools/stress/cases/t4_primary.py`, mutation-verified against the `git reset --hard`
version that eats uncommitted work. One known side effect: the fast-forward moves code, not
dependencies, so `node_modules` there can lag `package.json`. That is cosmetic - the primary exists to be
READ, and agents build and test in their own worktree after running the project's Install command - but a
tool run there can fail on a missing package until someone reinstalls.

**CI reads must cover the watch window, not a fixed count.** The Actions adapter made ONE request capped at
100 runs (default 60). On a repo with steady CI traffic - fms-studio has 19 runs from dependabot alone - a merge
commit's run falls off the end, the watcher sees a merge that apparently never built, and waits until
`NO_BUILD_AFTER_MIN`: the 12.5f stall reached by another route. It now pages until the runs are older than
`watch_since`, bounded by `MAX_RUNS = 500`, with the page size injectable so a test can force multi-page paging
without 60 real runs. Proven live 2026-09-21: page_size=2 over 6 runs issued 4 requests and returned the same
commits as one page. Cloud Build has the same shape (`--limit`) and no cursor; it is untested against an overflow.

**A cached test result is not a test run.** Related, same root: verification means the command actually
executed. Nx (and any caching build system) replays a previous result when the inputs match - including a
result computed in *another agent's worktree*. A verification run must defeat the cache
(`npx nx test <p> --skip-nx-cache`); an ordinary dev run should not. Found the same day, when a "green"
verification turned out to be a 100% cache hit from VanDev's worktree with nothing executed locally.

**5.3 Worktree management.** Source: `artifacts/worktrees.jsonl`. Tool: `worktree.py`. Rules: one task = one
branch = one worktree = one PR; primary checkout read-only, on the default branch and kept current (5.3a);
`create` refuses a
branch another agent holds; `finish` refuses to drop local-only work (exit 2); `sweep` daily; handoffs pass
slug + branch, never a path. Fails as: `sessions_spawn … worktree: true` (copies the settings repo), or a
worktree under `~/projects/<slug>-agy-*`.

**5.4 Orchestration.** Source: `AGENTS.md` roster + Flow section. Tool: `project-orchestration` skill,
`validate_team.py`. Rules: main has every tool (spawned sessions inherit its deny list) and a prompt-level
lock: shell for checking, never doing; spawn with `agentId`, `context: "isolated"`, `visible: true`, no cwd;
verify artifacts, `git log`, `gh pr view` before relaying; silence is a NO; approval gate before anything
outward. Fails as: a deny on main (workers lose tools), a specialist chat bot, main "just checking" a
build by running it.

**5.5 Git management.** Source: the project's remote. Tools: SSH deploy key per project for push,
`git_env.py` for the API with a repo-scoped PAT. Rules (enforced in `git_env.py`, not prompts): no merge,
PR base = the project's PR base, commit statuses only through `--review-status`; task branch pushed and PR
opened directly by VanDev; never the default branch, never force. Review happens on the PR; its result is the
commit status `openclaw/review` on the head SHA, set only when a saved review file names that SHA, so any push
after a review needs a new review. **The merge-time check**: `git_env.py <slug> --readiness <pr>` (not an agent eyeballing the PR). It reads
the review status AND every workflow run on this exact head, exiting 2 with each blocker named, 3 when
something could not be checked, 0 when ready. It exists because PR #39 was called ready while its CI was
failing: the old path looked only for `openclaw/review`, and `statusCheckRollup` needs a `Checks` token
permission this token does not have, so the gate could read nothing at all. Both facts are reachable
without it — `/commits/{sha}/status` and `/actions/runs?head_sha=`.

**It states what it actually verified.** With no PR CI configured, nothing runs on the head, so nothing can
fail and the gate passes — and it used to announce "every check on this head is green" when no check
existed. A gate built because of an unverified claim must not make one about itself; the verdict now says
the review was checked and the code was not. The policy is deliberately unchanged: a project with no PR CI
is still mergeable, because many legitimately have none. fms-studio is in exactly this state while its
Cloud Build PR trigger is uncreated — its merge gate is review-only, and says so. A GitHub ruleset on the PR base *requiring*
`openclaw/review` would have GitHub enforce it instead, and agents should not be able to change it (the token was minted without
Administration permission; branch-protection reads return 403 — writes were not tested). The ruleset
is per repo and Van's to set (team repos: the team's call, since it also gates human and bot PRs). Needs the
token permission "Commit statuses: Read and write". Fails as: `/pull/new/` links called "the PR", a PR
opened by main, or a "ready to merge" message on a head that is not green.

**5.6 Development and pipeline integration.** Source: `## Stack` (install/test/lint/E2E/deploy commands,
explicit, never inferred) and the Deploy signal, read through the CI adapter (`ci/`), so `cloud-build`,
`github-actions` and `none` are the same code path to the watcher. Tools: coding agent in the worktree; `gcloud_env.py`;
`delivery_watch.py` (PR feedback, deployed, build failed, rejected, feature complete, sweep due). Rules: the
coding agent writes code, VanDev runs everything else itself; `git status` clean after `git add`; 3-poll
rule; run log under `artifacts/runs/`. Fails as: watch-mode test targets (28 QA timeouts), `agy` used to
run `git push`, a deploy workaround instead of a source fix.

Three rules the watcher holds to, each one a 2026-09-19 incident (guide §12.5f):
**success is by ancestry, blame is by authorship** — a PR is on staging when *any* later green build contains
its merge commit (so stacked and superseded PRs deploy themselves), but a red build is only ever the fault of
the PR whose own merge commit is red, and consecutive reds are one outage reported once;
**act only on our own PRs** — ownership is the project token's account (`gh api user`), branch prefixes only
as fallback, so a teammate's PR is watched but never pushed to;
**no state waits forever** — "a trigger we expect has not reported yet" expires after `NO_BUILD_AFTER_MIN`,
because a permanent `running` silently stops every ticket move and still reads as a healthy report.

**5.7 Per-project tools and secrets.** Source: SecretRefs in the context file; values only in the vault
(`env` kind). Tools: the four launchers + two MCP registrations per project. Rules: names
`<KIND>_<SLUGUPPER>`; no ambient defaults (bare `gcloud`/`gh` fail); never list secrets (it prints values);
store from a real terminal. Adding project #2 touches: one context file, four secrets, two `openclaw mcp set`
lines, two `trustedWorkspaces` paths. Nothing in the framework. Fails as: a typo'd name repeated as fact,
or an env-var fallback in a launcher.

**5.8 File management.** Source: the manifest in `lint_workspace.py` + the table in §3. Rules: agents write
only to worktrees and `artifacts/`; scratch goes to `$TMPDIR`; backups are `openclaw backup` + one dated dir
per incident; the framework repo is committed after every change and its `git status` is empty; the
linter runs daily. Fails as: everything in §0.

---

## 5.9 The regression suite (`_tools/stress/`)

`python3 _tools/stress/run.py [--tier N] [--list]` — standard library only, no network, no credentials,
and it never touches `projects/` (tools resolve their workspace through `OPENCLAW_WORKSPACE`, which exists
so tests can point them at a sandbox; the heartbeat scans the real tree every 15 minutes).

`soak.py --minutes N` runs the suite on a loop while sampling memory, `/tmp` and the session DB. Its first
two minutes found the harness leaking 20 temp dirs per run — on a 1 GB RAM disk, where a full disk presents
as "out of memory", never "out of disk".

| Tier | What it covers |
|---|---|
| 1 | Validator parses that were wrong-but-accepted; adapter dispatch and link parsing; watcher build grouping |
| 2 | Fault injection: 401/403/429/500, truncated JSON, an HTTP 200 carrying an error envelope |
| 4 | State and concurrency: acks, ledger locking, marker agreement, the primary checkout |
| 5 | The merge gate's verdicts |

**Every case here is a bug that happened**, not a hypothetical. Three rules earned the hard way:

1. **A test that cannot fail proves nothing.** Every case is mutation-verified: reintroduce the bug and
   watch that exact case go red. Twice in one session a new case passed against the reintroduced bug —
   the B1 guard (an empty board reads every status as `"?"`, which is not in `QA_FROM`, so removing the
   guard changed nothing; the bug was the `or (not tasks and i)` clause) and the lint-owner case (it
   called the helper directly, so reverting the *call site* left it green). Both now pin the real thing.
2. **Assert the wiring, not just the helper.** A correct function nothing calls is worth nothing.
3. **Every guard needs a positive control.** "Produces no actions" must sit next to "produces the right
   actions", or a broken feature is indistinguishable from a working guard.

## 6. What to stop doing (the anti-patterns that produced the clutter)

1. Writing a helper script next to the problem (`write_specs2.py`, `check_new_build.sh` × 200). → Registry row or `$TMPDIR`.
2. Fixing behaviour with a new paragraph in an `AGENTS.md`. → Fix the tool or the linter; then the paragraph.
3. Editing `openclaw.json` by hand, or leaving `.bak` copies beside it. → `config patch --dry-run`; backups dir.
4. Copying a template into a skill "for convenience". → One template, referenced by path.
5. Letting agents "ensure a ticket exists" / "just push it". → Roles are hard; VanPM writes tickets, VanDev pushes after review.
6. Treating a `/pull/new/` link, a claim, or a timeout as done. → Verify; silence is a NO.
7. Keeping every generated proposal, dream, backup and worktree forever. → Lifecycles in §3; linter counts them.
8. Baking project names into the framework (`FMSSTUDIO` fallback in a launcher). → Zero project knowledge in layer 3.
9. **An agent editing the framework to satisfy a request.** 2026-09-19 13:04: Van asked for reviews to live in the
   GitHub PR; main (the orchestrator, whose rule is "shell is for checking, not doing") rewrote `git_env.py`, its own
   `AGENTS.md` and the orchestration skill within six minutes, deleting the review gate outright. The request was
   legitimate; the path was not. → Framework changes are design changes: they go through a Claude Code session with
   Van, update the registry and linter, and land as one commit. Agents that receive such a request reply
   "this is a framework change" and stop. The linter's `git status` check is what surfaced it. Follow-up (phase A,
   same night): the check was rebuilt at merge time (§5.5), where GitHub enforces it instead of a script agents can edit.

---

## 7. Self-fix runbook for the current box

Ordered. Each step ends with a check. **Agent may run** = safe for the orchestrator or a Claude Code session;
**Van runs** = real SSH terminal (secrets, deletes the classifier blocks, root). Baseline first, then clutter,
then structure, then the flow profile, then automation.

**Status 2026-09-20: development-only + the toolchain seam are DONE** (Decisions P, Q, R, S).
Prompts and config both enforce scope; tracker and CI are adapter packages; the validator no longer
requires a ClickUp list of every project. Proven offline on three fixtures - Django+Jira+GitHub
Actions on a fully custom board, Linear with no CI, and a repo with no tracker - none of which could
be onboarded before. fms-studio re-verified live end to end after every step. What is still open:
Step 10's *live* half still
needs a real second project.

**Status 2026-09-19 night: Steps 1-9 are DONE** (linter went from 18 OK / 10 FIX to 22 OK / 0 FIX after Step 5). Step 10 is open; phase A below is done on the box and waits for two GitHub settings.

### Steps 1-5 — DONE 2026-09-19 (record)
- **1. Framework baseline:** `~/.openclaw/workspace` committed (`e929997`), `.gitignore` carries the lifecycle rules
  (memory, dreams, media, credentials, `__pycache__`, runs, watcher state). Agent-made edits recorded in `965c153`.
- **2. Garbage removed** (`978ae5e`): `developer/test.sh`, `projects/fms-studio/fetch_figma.py`, `openclaw-sessions-explained.md`,
  `diagrams/`, `skills/skill-creator/` (Decision H), `code-reviewer/pr37.diff`, and `developer/package*.json` (an agent ran
  `npm install` in its own settings folder at 12:14). `projects/fms-studio/artifacts/runs/` created.
- **3. Backups:** everything archived first to `~/Backups/openclaw-backups-2026-09-19.tgz` (84 entries, verified), then
  `~/.openclaw/backups` pruned 48 → 8 (3 dated dirs + 5 newest files). 36 skill-workshop proposals deleted. The
  `openclaw.json.bak`..`.bak.4` files are OpenClaw's own rotation ring and stay. No OpenClaw managed worktrees existed.
- **4. `/tmp` capped at 1G** (Van, `sudo`, drop-in `/etc/systemd/system/tmp.mount.d/size.conf`; 353M used after cleanup).
  1G rather than 512M because Claude Code sessions keep scratch files there.
- **5. Platform:** active-memory plugin and dreaming turned off (`decisions-2026-09-19/02-memory.patch.json5`, gateway
  restarted 17:03; restart hung in server close and systemd force-stopped it at 5m30s, no work lost). Models unchanged:
  Gemini 3.1 Pro primary. Discord channel `/new` sent (context 272k tokens → 0). OpenClaw 2026.9.5 upgrade not done
  (optional; no config-key changes found in its notes).

Lessons from doing it: long pasted commands wrap in Van's terminal and break at the wrap, so anything longer than one
line goes to Van as a small self-deleting script (`bash ~/<name>.sh`). Deletes Van approved by running them may be
finished by the agent that wrote them.

### Steps 6-8 — DONE 2026-09-19 (record)
- **6. Flow profile** (`55be54f`): `## Flow` in the template and fms-studio; `validate_context.py` parses and
  validates it and infers `factory` + a status map when it is missing. Stage names: `spec tickets review
  internal-qa merge-gate delivery-watch` (`merge-gate` = step 5 "ready to merge" message, since Van's 13:04 flow
  opens PRs right away). Tools use canonical statuses (`tracker_status.py --status staged`), the Flow PR base
  (`worktree.py`, `git_env.py`, watcher), and the assignee filter (`--claim` SKIPs other people's tickets). The
  watcher gained MERGED (no deploy pipeline) and stage gating. Orchestration skill: stage table, team mode,
  branch models. Onboarding asks the Flow questions. Tested with a teammate fixture (custom board names) and a
  deliberately broken one (7 precise errors).
- Found and fixed on the way: the four agent workspaces are separate git repos whose files had **never been
  committed** (the main repo ignored three of them and double-tracked `code-reviewer`). All five repos now have a
  baseline and the linter checks all five.
- **7. Prompts** (agent repos + `2fb2d5f`..): each specialist `AGENTS.md` is one shared header (entry routine, file
  rules, red lines incl. "framework changes are Van's") plus a short lane: job, tool table, never-list. Sizes
  61-91 lines; developer 10.9k → 6.1k chars. Removed two contradictions with the live pipeline (reviewer still
  reviewed patch files; developer still waited for approval before pushing). Reviewer now posts on GitHub with
  `--comment`/`--request-changes` (one GitHub account cannot approve its own PR) and saves
  `reviews/<feature>--<lane>.md`. Main: "Existing Solutions Preflight" replaced by "Framework changes are not
  agent work". Verified: each agent restated its tools, never-list and file rules correctly in a tool-free turn.
- **8. Retention** (`850e68f`): `worktree.py sweep` deletes run logs > 30 days and `specs/_figma/<feature>/` of
  features archived > 30 days (loose screenshot files are left alone); the watcher emits a daily `LINT` action
  from the first project. Tested on a throwaway tree.

### Step 9 — DONE 2026-09-19 17:29 UTC: heartbeat posts the daily lint (Van approved)
`~/.openclaw/backups/decisions-2026-09-19/03-heartbeat-lint.patch.json5` adds one sentence to the heartbeat prompt
(post LINT lines in one message, never fix files from a heartbeat). Applied as a hot reload; the gateway
defers it until in-flight agent turns finish. Backup: `openclaw.json.pre-heartbeat-lint` in the same folder.

### Phase A — DONE 2026-09-19 night: review check at merge time (Van approved)
- `git_env.py --review-status <pr>`: `openclaw/review` = success/failure on the PR head, only when a review file's
  `Reviewed SHA` equals it; raw `statuses` API writes refused; the unused PR-create review code removed.
- Reviewer AGENTS.md step 5, orchestration steps 3 + 5 (ready message only on a green head), main AGENTS.md,
  and the shared `worktree-lifecycle` skill (was untracked and still described push-after-APPROVED; now its own repo,
  checked by the linter, which also flags any other shared skill).
- Waiting on Van: token permission "Commit statuses: Read and write" (today reads and writes both return 403), then
  "Require status checks: `openclaw/review`" in the repo ruleset. Until then the reviewer reports the 403 line and
  step 5 cannot see a green status, so the ready message says the status is missing.

### Phase B — Step 10 offline half DONE 2026-09-19 night (live half open)
Run in an isolated copy of the framework (scratchpad), not in `projects/`: the heartbeat runs the watcher for every
`projects/<slug>` every 15 min and hands the daily LINT to the first project whose context VALIDATES (2026-09-21;
it was the alphabetically first, which meant a half-onboarded project captured the lint and then died in `Ctx()`
before running it, silently stopping the lint for everyone), so a half-onboarded test project would still have
posted errors to Discord all night. `demo-teammate`: teammate, human tickets, ticket-branch,
Deploy signal none, a custom board (Backlog/In Dev/Staging/QA Failed/Blocked/Done/Won't do), no Figma/GCP/GitHub.
- Fixed: the validator demanded a Figma secret for a project without Figma (now only when a Figma file is set);
  onboarding did not create `artifacts/runs`; stale worktree.py text.
- Passed: validator rules, worktree create/refuse/finish/sweep, every launcher refusing with the missing field
  named, watcher Flow gating, assignee filter, canonical → board status names, claim without a token failing loudly.
- Open (needs accounts): GitHub PRs, ClickUp, MCP registration, agents following the stage table. Create
  `projects/<slug>/` LAST when doing it live (after secrets and MCP), because the heartbeat picks it up at once.

### Phase C — off-box copy, 2026-09-19 night (tooling done; the push is Van's)
- Framework: `_tools/framework_offbox.py` (registry row). Tested against a scratch repo; it refuses today because
  the main repo's history holds the fms-studio Figma token (commit 7715e27): rotate it, then `--allow-rotated`.
- Design docs now live in the framework repo (`docs/`), so invariant 3 (design, linter and guide change in one
  commit) can finally hold and the docs travel with the off-box copy.
- `~/Backups/openclaw-git` (2.7 GB, OpenClaw's database backup) is NOT pushable: its history, including the
  2026-09-19 09:30 run (`excludedTables: []`), holds plaintext secrets (18 vault rows, one GCP key JSON).
  `--exclude-secrets` was added to the schedule after that run; the first redacted run is 2026-09-20 09:30 UTC
  (check `global/manifest.json` → `excludedTables` lists `secret_store_entries`). Copy it off the box by PULLING
  from Van's own encrypted machine (rsync over ssh), never by a push from this box.

### Phase D — DONE 2026-09-22: the design reaches the code (Van approved "do full fix")

**The defect.** The Figma MCP worked perfectly and the pipeline used one tenth of it. Every one of the 36 files
it had ever downloaded for fms-studio was a whole-screen PNG named `<nodeId>.png`. Zero assets: `git ls-files`
found **no** image or SVG tracked in the repo, and `frontend/public/` held only a favicon. The landing page
shipped `<div>FindMyShots Studio Logo</div>` where the wordmark belongs and a grey box captioned
`[Photo Collage Image Placeholder]` where the hero belongs, in stock Tailwind colours, while the Figma
inventory sitting in `specs/_figma/` had recorded `#FF6100` and `Host Grotesk` correctly. One screen group
alone (event creation) contains 36 image fills across 239 nodes and 222 vector nodes, none of them fetched.

Four gaps in series, each of which alone would have produced it:
1. `feature-breakdown` Step 1 said "screenshot the frame". It never said "download the artwork in it".
2. The spec carried no visual contract: AC must be falsifiable Given/When/Then, which pushes everything to
   behaviour, and the DoD said "subtasks COMPLETE and QA passes". Nothing required matching the design.
3. **`agy` cannot see the design** — no Figma tools, and the screenshots live outside the worktree it runs in.
   The agent that actually writes the components got text only, and filled the gaps with placeholders.
4. Nobody checked. QA and VanReviewer both had `figma-*` denied.

**The fix**, one change per gap:
- **VanPM** (`feature-breakdown` SKILL.md Step 1.4–1.6): download every `type: IMAGE` fill, `[IMAGE-SVG]` node
  and `gifRef` into `specs/_figma/<feature-slug>/assets/`, passing each node's `imageDownloadArguments`
  (they come in two shapes — inline JSON in the node's `fills`, and YAML under `GLOBAL_VARS`; reading only the
  YAML form found 3 of the landing page's 12 crops and missed 4 assets outright, because two crops of one source
  image look like one asset until you see their `filenameSuffix`), write `assets/manifest.json`
  (`file` → `repo_path`), and record tokens as exact values.
- **The spec** (`ticket-template.md`, `spec-format.md`): a new `assets:` header key and a `## Design fidelity`
  body section on every `[FE]` ticket — hex tokens, the asset list with repo paths, "no placeholders" — plus a
  DoD checkbox. `tracker_push.py` enforces all of it and renders the asset list into the ClickUp `## Design`
  section. An empty `"assets": []` is valid and means "this screen is CSS only": the point is a positive
  statement instead of silence.
- **VanDev** (`AGENTS.md` step 2, `agy-coding` "Design work"): copy the assets into the worktree at their
  `repo_path` **before** launching agy, verify non-empty, and name them and the tokens in the prompt with an
  explicit "do not render a placeholder". Assets are never re-downloaded; they are already on disk.
- **VanReviewer** (`AGENTS.md` step 2, `figma-*` un-denied, linter expectation inverted): four checks against
  the diff — assets present, assets actually referenced, no stand-ins, tokens exact. Figma access is read-only
  and only to confirm a value it thinks is wrong.

**Also fixed:** a failed download used to leave a 0-byte file that every later check passed
(`9794-6547.png` sat empty for five days). `tracker_push.py` now rejects a 0-byte screenshot or asset, and
Step 1.1 tells VanPM to read the tool's per-file reply instead of assuming.

**Repo size.** The downloaded binaries are gitignored (`.gitignore`): the landing page alone is 37 MB, and 13
screens would push this repo past 500 MB permanently, on a box whose framework repos are pushed off-box
(Decision I). `manifest.json` is committed and carries `file_key`, `png_scale` and a per-asset `download` block,
so the folder is a pure function of it; `tracker_push.py` tells you how to rebuild an empty cache instead of
reporting 36 missing files. Note the 36 screenshot PNGs already committed before this (35 MB) were left alone.

**Asset ownership.** A feature's `[FE]` tickets share one manifest. Each ships the subset its `## Design
fidelity` lists; across the spec every asset must be shipped by **exactly one** ticket. Nobody owning it means
the file never reaches the repo; two owning it means two developers writing the same path. A copy-fix or wiring
ticket that ships nothing is fine and does not repeat the list.

**Regression suite:** `_tools/stress/cases/t1_design_assets.py`, 17 cases (96 offline cases total, 0 failing) —
including the two that must keep passing: a `[BE]` ticket is never asked for a manifest, and a project with no
Figma file is untouched.

### Step 10 — Second project dry-run (proves multi-project)
Onboard a throwaway repo as `demo-teammate` with Profile `teammate`, Ticket source `human`, Deploy signal
`none`, no Figma, no GCP. Expected: onboarding needs only the context file, three secrets, one MCP server;
`worktree.py demo-teammate list`, `git_env.py demo-teammate --check`, and the linter all pass; the
orchestration skill skips `spec`, `tickets`, `internal-qa`. Then delete it (context dir, `~/projects/demo-teammate`, MCP server, secrets) and confirm the linter is clean again. Two projects with different flows and no framework edit = the goal is met.

---

## 8. Decisions (closed 2026-09-19 by Van)

| | Decision | State |
|---|---|---|
| A | Model: **stay on Gemini 3.1 Pro** (Flash + Sonnet fallbacks). No switch to Claude. | unchanged |
| B | Coding backend: **agy on Gemini**. No Claude Code. | unchanged |
| C | Tracker: keep `clickup_mcp.py` (reads) + VanPM scripts (writes) | unchanged |
| D | Chat: **Discord and Telegram**, both bound to main only | unchanged |
| E | active-memory plugin **off** (it never ran: 848/848 recalls skipped) | applied 17:03 |
| F | Git: per-project SSH deploy key for push + repo-scoped PAT for the GitHub API | unchanged |
| G | Dreaming **off** | applied 17:03 |
| H | `skills/skill-creator` **removed** | done |
| I | Private GitHub repo for the framework repos, pushed from Van's terminal only (`framework_offbox.py`); database backups pulled to Van's machine | tooling done; waits for Figma token rotation + SSH key |
| J | Retention: runs 30 d, figma 30 d after archive, last 5 config backups, proposals weekly | first prune done; automation is Step 8 |
| L | Spawn time limits: `runTimeoutSeconds` 3600 dev, 1800 others (orchestration skill) | applied 2026-09-20 |
| M | Shared skills: only `worktree-lifecycle`; `beautiful-mermaid` moved to `~/Backups/removed-skills/`; skill-workshop proposals rejected (36 registry entries whose files were already deleted cannot be rejected without `openclaw doctor --fix`, which is forbidden; they are inert) | applied 2026-09-20 |
| O | Team projects: replies to human PR comments are drafted by VanDev, posted only after Van's yes (code fixes still go out at once) | applied 2026-09-20 |
| N | Ruleset requiring `openclaw/review`: **not now** (the stamp shows; main checks it before "ready") | Van, 2026-09-20 |
| P | **Development only.** No general-assistant mode and no fallback to one. Enforced in prompts (main's AGENTS/SOUL/USER) *and* config (`skills.allowBundled`, non-dev plugins removed), not prompts alone | Van, 2026-09-20; applied |
| Q | Trackers: **ClickUp, Jira, Linear, or none**, behind `projects/_tools/trackers/`. Spec→ticket creation was ClickUp-only; opened to Jira and Linear 2026-09-21, each verified live | Van, 2026-09-20; applied |
| R | CI: **Cloud Build, GitHub Actions, or none**, behind `projects/_tools/ci/`. GitHub stays the only git host | Van, 2026-09-20; applied |
| S | Evolve the toolchain seam rather than rebuild the pipeline: the process layer (5 agents, Flow, worktrees, gates, watcher) is kept as-is | Van, 2026-09-20 |
| K | Review check at merge time: `openclaw/review` status + a ruleset that requires it (replaces the PR-create gate) | tooling done; token permission + ruleset are Van's |

Any future choice that changes a model, provider or cost is confirmed with Van item by item, never as part of "go with the recommendations".

## Appendix — linter output on 2026-09-19 (before Step 1; after Steps 1-5 it reports 22 OK / 0 FIX)
```
FIX [framework] 16 file(s) outside the manifest (test.sh, diagrams/*, openclaw-sessions-explained.md, fetch_figma.py, skills/skill-creator/*)
FIX [framework] 7 __pycache__ file(s)
FIX [framework] skill not in the manifest: skills/skill-creator
FIX [framework] framework repo has 111 uncommitted/untracked path(s)
OK  [project:fms-studio] PROJECT_CONTEXT.md VALID
FIX [project:fms-studio] artifact dirs missing: ['runs']
FIX [project:fms-studio] stray files in the project dir: ['fetch_figma.py']
OK  [code:fms-studio] primary checkout clean on `Development`
OK  [code] no OpenClaw managed worktrees          (9 "restorable" snapshots remain in the registry: Step 3)
OK  [config] main tools.deny = [] · allowAgents · loopDetection · heartbeat.isolatedSession · specialist denies · MCP servers · skills · fallbacks
FIX [host] /tmp is tmpfs sized 3.9G
OK  [host] gateway TMPDIR, PATH, gcloud, gh
FIX [host] 5 loose openclaw.json.bak*/clobbered/tmp copies
FIX [host] 47 entries in ~/.openclaw/backups
FIX [host] 30 pending skill-workshop proposal(s)
18 OK, 10 FIX
```
