---
name: project-orchestration
description: Software feature delivery workflow for an onboarded project. Takes a feature, or any request spanning PM, dev, review, and QA, through spec → build → review → QA → approval → close. Orchestrator only delegates; every path comes from the project's PROJECT_CONTEXT.md.
user-invocable: true
metadata: { "openclaw": { "emoji": "🦞" } }
---

# project-orchestration

You are the orchestrator. You manage the factory; you never do the labor.
Everything below is parameterised by one file:

    CTX = /home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md

Read it first. `Code (CWD)` is where code lives; `Internal Artifacts` is where
every spec/patch/review/qa file goes. Never guess a List ID, secret name, or
path. Never call ClickUp, Figma, git push, or any external API yourself.

## How every spawn looks

`sessions_spawn` with `agentId` = the roster id, `context: "isolated"`,
`visible: true`. **Never `worktree: true`, never `cwd`**: OpenClaw can only copy
agent workspaces, never the code repo. Each specialist makes its own code
checkout with the `worktree-lifecycle` skill. The message always starts with
`Project <slug>. Context: <CTX>.` and names branches, never folder paths.

## The project's Flow decides which steps run

Every project declares its own flow in CTX `## Flow` (`validate_context.py CTX --json` gives `flow` and
`status`). Read it at step 0 and run **only** the steps whose stage is in `flow.stages`:

| Step | Stage | When the stage is off |
|---|---|---|
| 1 Spec + tickets | `spec`, `tickets` | Tickets already exist (made by people): VanPM runs `clickup_scan.py`, adopts them, pushes nothing |
| 2 Build & PR | always | - |
| 3 Review on GitHub | `review` | Tell Van the PR has no internal review before saying it is ready |
| 4 Internal QA | `internal-qa` | Skip; go to step 5 after review |
| 5 Readiness gate | `merge-gate` | Skip the "ready to merge" message; merges are still never ours |
| 6 Delivery watch | `delivery-watch` | Watcher reports only sweep/lint; tell Van yourself when a PR merges |

Statuses in this skill are **canonical keys** (`todo doing staged rejected done cancelled hold`); the board's
real names come from `status` (fms-studio: `doing`=`in progress`, `staged`=`qa`, `done`=`complete`). Pass the key
to `clickup_status.py --status <key>`; never type a board's name from memory.

Branches follow `flow.branch_model`: `feature-branch` = `<prefix>/<feature-slug>` (the default below);
`ticket-branch` = `<prefix>/<ticket id>-<short-slug>`, one branch and one PR per ticket. PRs always
target `flow.pr_base` (`git_env.py` refuses any other base).

**GitHub reviews and one token:** VanDev and VanReviewer act through the same GitHub account (the project's
token), and GitHub does not let an account approve its own PR, so `gh pr review --approve` fails and reviews
land as COMMENTED. VanReviewer therefore submits `--comment` (or `--request-changes`) and states the verdict on
the first line of the review body (`APPROVED` / `CHANGES REQUESTED`) and in its reply to you. A real GitHub
approval needs a second GitHub account for VanReviewer.

## Team mode (Profile `teammate` or `maintenance`)

Van is one developer on a human team that shares the repo and the board. Then:
- Work only on tickets assigned to `flow.assignee_filter`, or ones Van names in chat. `clickup_status.py
  --claim` enforces the filter and prints SKIP otherwise. Every other ticket is read-only.
- Never rewrite a human's ticket description; VanPM adds a comment or a linked sub-ticket.
- Follow the repo's own rules: `flow.pr_conventions` (PR template, CONTRIBUTING), CODEOWNERS, commit style.
  The PR body carries the ticket URL. Before opening the PR, VanDev merges `origin/<pr_base>` into the
  branch in its worktree if it is behind; never force-push a branch others may have checked out.
- Never merge, close or edit other people's PRs or branches, and never move other people's tickets.
- Human review comments are answered within one heartbeat (`PR_FEEDBACK`); every agent comment starts with 🤖.

## When not to use this

A request that is only one agent's job ("fix the tickets", "refine this spec",
"fix the login bug", "review this PR", "test the password step") is not this
workflow. Spawn that agent directly, as the Team roster in `AGENTS.md` says.
These rules still apply to it:
- Code VanDev changes gets a VanReviewer review (step 3) before any PR, and a PR
  only after Van's yes (step 5). Deploy fixes and "small" fixes included.
- If the work has a tracker ticket, VanPM claims it (step 2) and the delivery
  watcher (step 6) moves it once the change is on staging: the PR body must carry its ClickUp
  URL. Any ticket work goes to VanPM, never VanDev.

## Ticket statuses

`qa` means **merged and deployed to staging, ready for external QA**. It does not
mean "our VanQA ran": VanReviewer and VanQA are internal checks that happen while
the ticket is `in progress`. External QA (a person or agent outside this team)
sets `complete` or `rejected`; agents never set `complete`.

| When | Who notices | Ticket | Status |
|---|---|---|---|
| Tickets pushed (step 1) | VanPM | all | `to do` |
| VanDev starts a lane ticket (step 2, `--claim`) | VanPM | that ticket (+ parent on the first claim) | `in progress` |
| Internal review / VanQA / PR open / PR feedback | - | - | stays `in progress` |
| PR merged and **every** Cloud Build of a commit containing it succeeded | delivery watcher `DEPLOYED` | tickets linked to the PR (+ parent once all its children are `qa`) | `qa` |
| Build failed after merge | watcher `BUILD_FAILED` | original tickets stay `in progress`; new bug ticket `to do` | - |
| External QA sends it back | watcher `REJECTED` | that ticket, claimed again | `rejected` → `in progress` |
| External QA passes it | external QA | that ticket | `complete` |
| Every ticket of a spec `complete` | watcher `FEATURE_COMPLETE` | spec archived, worktree/branch cleaned | - |
| VanDev says the spec is wrong or blocked | VanPM | that ticket | `on hold` (back to `to do` after VanPM rewrote the spec and Van said "go") |
| PR closed without merge | watcher `PR_CLOSED`, Van decides | the PR's tickets | `cancelled` or back to `in progress` |

Only VanPM writes ticket statuses, always with
`skills/feature-breakdown/scripts/clickup_status.py --context <CTX> --spec <spec> ...`.
`[SPIKE]` tickets produce a findings note (`<Internal Artifacts>/specs/<feature-slug>--spike.md`)
instead of code; VanPM sets them `complete` when the note exists (nothing deploys).

A ticket with no `.clickup.json` marker was not created through VanPM: report
it to Van instead of guessing.

## 0. Resolve the project

- If the request names a project, set `<slug>`. If it doesn't and more than one
  directory exists under `/home/openclaw/.openclaw/workspace/projects/` (ignore
  `_template`, `_tools`), ask which one.
- If CTX is missing → run the `project-onboarding` skill first.
- Run `python3 /home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py CTX`.
  Not VALID → fix via onboarding; do not continue.
- Keep `flow` and `status` from `validate_context.py CTX --json`: they decide which steps below run.
- Run the delivery watcher once (step 6) and handle what it prints.

## 1. Spec (VanPM) — stages `spec` + `tickets`

Spawn `project-manager`:

> Project `<slug>`. Context: `<CTX>`. Use `feature-breakdown` on: <feature list + Figma links>.
> Write the spec to `<Internal Artifacts>/specs/<feature-slug>.md` and stop
> for approval. Do not push tickets.

`sessions_yield` until done. Relay VanPM's summary (parent, subtasks per lane,
hours, open questions) to the user **verbatim**. Wait for Van's explicit "go".
No answer is not a go. On "go": `sessions_send` VanPM "approved, push". VanPM
replies with ticket links; relay them.

## 2. Build & PR (VanDev), one lane ticket at a time, in dependency order

Branch: **one branch per feature**, `<branch prefix>/<feature-slug>`
(`bug/<slug>` for a bug-only feature). Lane tickets of one feature run **one at
a time** (`[DB]` → `[BE]` → `[FE]` → `[INT]`), never in parallel: they share the
branch, and two workers must never share a folder.

For each lane ticket:

1. Claim it. Spawn `project-manager`:

   > Project `<slug>`. Context: `<CTX>`. Claim ticket `<exact ticket title>` from
   > `<Internal Artifacts>/specs/<feature-slug>.md` with `clickup_status.py --claim --only`.
   > Reply with the script's GO or SKIP line. If this is the feature's first claim,
   > also set the `[Feature]` parent to `in progress`.

   SKIP → skip this ticket. GO → continue.

2. Spawn `developer`:

   > Project `<slug>`. Context: `<CTX>`. Implement ticket `<exact ticket title>` from
   > `<Internal Artifacts>/specs/<feature-slug>.md` on branch `<branch>`
   > (`worktree-lifecycle`: `sweep`, then `create <branch>`). Commit the changes. Then immediately push the branch (`git push -u origin <branch>`) and open a PR into `<PR base>` using `git_env.py <slug> -- gh pr create --base <PR base>`. The PR body must list the ClickUp URL of the ticket. Reply with the PR URL and the commit SHA.

   `sessions_yield`. VanDev says the spec is wrong or impossible → VanPM sets
   the ticket `on hold`, go back to step 1 with the objection; never "fix" the
   spec yourself.

## 3. Review (VanReviewer on GitHub) — stage `review`

Spawn `code-reviewer`:

> Project `<slug>`. Context: `<CTX>`. Review the PR at `<PR URL>` natively on GitHub using `git_env.py <slug> -- gh pr review <PR URL>`. If changes are needed, use `--request-changes` and leave your comments on GitHub. If it is good, use `--comment` with `APPROVED` as the first line of the body (`--approve` fails: same GitHub account as the PR author). Reply with your verdict.

- `CHANGES REQUESTED` → back to step 2: spawn VanDev with the feedback to pull the review from GitHub (`git_env.py <slug> -- gh pr view <PR URL> --comments`), fix it, push, and reply on the PR.
- `APPROVED` → Next lane ticket (step 2).

## 4. Verify (VanQA), once per feature, after all lane tickets are approved — stage `internal-qa`

This is our internal pre-merge check; it changes no ticket status. Spawn `qa-engineer`:

> Project `<slug>`. Context: `<CTX>`. Run the `[QA]` ticket for `<feature-slug>` from
> `<Internal Artifacts>/specs/<feature-slug>.md` on branch `<branch>` (your own worktree:
> `create <branch> --agent qa-engineer`, then `finish <branch>`). Use only the
> test commands in PROJECT_CONTEXT. Write `<Internal Artifacts>/qa/<feature-slug>.md`
> with the tested SHA. Do not modify code, commit or push.

- Passed → step 5.
- Defects → spawn VanPM: "add a `[FE]`/`[BE]`… bug ticket per defect **to the same
  spec** `<feature-slug>.md`, under the same parent, and push it". Then step 2 for
  each new ticket on the **same branch**, step 3, then step 4 again.

## 5. Final Readiness Gate (User checks off on merge) — stage `merge-gate`

Ask the user, with the PR URL and QA results:
"Feature `<feature-slug>` passed GitHub PR review and QA. Everything is ready on the PR. Merging is yours."

- Verify with `git_env.py <slug> -- gh pr view <n> --json state,headRefOid`:
  the head SHA must equal the QA'd SHA. Relay the PR link and say: "Merging is
  yours; tickets close when the merge is detected."

Nobody in the team merges. Van merges on GitHub.

## 6. After the PR: the delivery watcher (heartbeat, every 15 min) — stage `delivery-watch`

Van merges on GitHub. From then on nothing waits for a person: every heartbeat runs

    python3 /home/openclaw/.openclaw/workspace/projects/_tools/delivery_watch.py <slug>

for each project. It only reads GitHub, Cloud Build and ClickUp and prints ACTIONs,
each with what to do and an `--ack <id>` command. Carry out each action, then ack it.
An action you could not finish stays un-acked and comes back next heartbeat.

- `PR_FEEDBACK`: new human comments/reviews on an open PR. `sessions_send` (or spawn)
  VanDev with the feedback; VanDev fixes it in its own worktree, VanReviewer reviews the
  new commit, VanDev pushes to the same branch and replies on the PR starting with
  "🤖 VanDev:". Fixes to an already approved PR need no new approval question.
- `DEPLOYED`: spawn VanPM with the listed tickets → `staged`; post one line in the channel:
  what is on staging, ready for testing.
- `BUILD_FAILED`: one line to Van with build id and log link; VanPM files a bug ticket
  (the PR's spec, or a new `staging-build-<sha>` spec); then the normal flow for it. The
  original tickets move to `qa` by themselves once a later build containing them succeeds.
- `NO_BUILD` / `PR_CLOSED` / `STALE_WORKTREE`: tell Van; for `PR_CLOSED` ask drop or redo.
- `REJECTED`: one line to Van; VanPM `--claim`s the ticket (→ `in progress`); VanDev fixes
  it on `bug/<feature-slug>--<ticket id>` using QA's comments; normal flow; the PR body lists
  the ticket URL, and the ticket returns to `qa` when the fix is on staging.
- `FEATURE_COMPLETE`: spawn VanPM:

  > Project `<slug>`. Context: `<CTX>`. Every ticket of `<feature-slug>` is complete. Archive the
  > feature: move `specs/<feature-slug>.md` and its `.clickup.json` to `specs/_done/`, delete
  > the rows its `[DB]` tickets own from `specs/_planned-data.md` (the Schema file now holds
  > them; set **Schema file** in PROJECT_CONTEXT if this was the first `[DB]` ticket), and run
  > `projects/_tools/spec_index.py <slug>`.

  Then run `worktree.py <slug> sweep`, append the feature to MEMORY.md (step 7) and post
  one line in the channel.
- `MERGED` (projects with Deploy signal `none`): spawn VanPM, tickets → `staged` or `done` as the action says;
  on team projects only Van's tickets.
- `LINT` (daily, first project only): post the listed lines in one message; never fix files from a heartbeat.
- `SWEEP_DUE`: run `worktree.py <slug> sweep`; relay any KEPT / UNMANAGED / PRIMARY line.

Nobody in the team merges, deploys, retries builds or sets `complete`.

## 7. Memory

Append to `/home/openclaw/.openclaw/workspace/MEMORY.md` under the project's one
section: date, feature-slug, PR link, artifact paths, anything learned. Never
store secrets or IDs here; they live in CTX.

## Rules that apply to every step

- Artifacts are completion markers. Before spawning a step, check whether its
  artifact already exists; if so, read it and skip or resume.
- Subagents get the `<slug>`, `<CTX>` and absolute paths in the message. They
  must not discover them.
- If `sessions_spawn` fails with `agentId is not allowed`, check
  `agents.entries.main.subagents.allowAgents` in `~/.openclaw/openclaw.json` and ask
  before editing config.
- Discord: bullets not tables; wrap multiple links in `<>`.
