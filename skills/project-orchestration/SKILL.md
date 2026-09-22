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
`visible: true`, and a time limit `runTimeoutSeconds`: **3600** for `developer`, **1800** for
`qa-engineer`, `project-manager` and `code-reviewer`. A run that hits the limit stops; its worktree
and commits stay, so ask the agent what it has (`sessions_send`) or re-spawn it; never lift the limit
to 0 to get past a hang (a hang is a watch-mode command or a loop: find it). **Never `worktree: true`, never `cwd`**: OpenClaw can only copy
agent workspaces, never the code repo. Each specialist makes its own code
checkout with the `worktree-lifecycle` skill. The message always starts with
`Project <slug>. Context: <CTX>.` and names branches, never folder paths.

## The project's Flow decides which steps run

Every project declares its own flow in CTX `## Flow` (`validate_context.py CTX --json` gives `flow` and
`status`). Read it at step 0 and run **only** the steps whose stage is in `flow.stages`:

| Step | Stage | When the stage is off |
|---|---|---|
| 1 Spec + tickets | `spec`, `tickets` | Tickets already exist (made by people): VanPM runs `tracker_scan.py`, adopts them, pushes nothing |
| 2 Build & PR | always | - |
| 3 Review on GitHub | `review` | Tell Van the PR has no internal review before saying it is ready |
| 4 Internal QA | `internal-qa` | Skip; go to step 5 after review |
| 5 Readiness gate | `merge-gate` | Skip the "ready to merge" message; merges are still never ours |
| 6 Delivery watch | `delivery-watch` | Watcher reports only sweep/lint; tell Van yourself when a PR merges |

Statuses in this skill are **canonical keys** (`todo doing staged rejected done cancelled hold`); the board's
real names come from `status` (example: a board may map `doing`=`In Dev`, `staged`=`Staging`, `done`=`Done`).
Pass the key to `tracker_status.py --status <key>`; never type a board's name from memory.

Branches follow `flow.branch_model`: `feature-branch` = `<prefix>/<feature-slug>` (the default below);
`ticket-branch` = `<prefix>/<ticket id>-<short-slug>`, one branch and one PR per ticket. PRs always
target `flow.pr_base` (`git_env.py` refuses any other base).

**GitHub reviews and one token:** VanDev and VanReviewer act through the same GitHub account (the project's
token), and GitHub does not let an account approve its own PR, so `gh pr review --approve` fails and reviews
land as COMMENTED. VanReviewer therefore submits `--comment` (or `--request-changes`) and states the verdict on
the first line of the review body (`APPROVED` / `CHANGES REQUESTED`) and in its reply to you. A real GitHub
approval needs a second GitHub account for VanReviewer.

## Design-led work: a Figma link binds every step

A Figma link anywhere in the request - Van's message, a ticket, a spec, a PR
comment - makes the work **design-led**. The design is then part of the contract,
not a reference picture, and every step below runs its Figma half. There is no
"build it from the screenshot" path and no eyeballing at any stage: every
fms-studio screen shipped before 2026-09-21 was built that way, and every one of
them went out with a text stand-in where the wordmark belongs and a grey box
where the hero image belongs.

Check this at step 0, before you spawn anything:

- CTX must name a **Figma file** and a **Figma MCP server** (`figma-<slug>`). If
  it does not, stop and tell Van the project has to be onboarded with its Figma
  key first. Never let an agent reach Figma through another project's server or
  through the REST API, and never call a `figma-*` tool yourself.
- The link goes to **VanPM first, always** - including a one-line "make this
  match the design" fix. A Figma link handed straight to VanDev is the failure
  this section exists to prevent: VanDev gets no screen inventory, no asset
  manifest and no tokens, and `agy` cannot see the design at all.

What each step owes, and what you check before moving on:

| Step | Agent | Its Figma obligation | You verify before relaying |
|---|---|---|---|
| 1 | VanPM | Per node: `download_figma_images` -> `view_image` -> `get_figma_data`, then the artwork, the manifest and the exact tokens | `specs/_figma/<feature-slug>.md` exists; each `<nodeId>.png` is non-zero; `specs/_figma/<feature-slug>/assets/manifest.json` exists (`"assets": []` is a valid answer, silence is not) |
| 2 | VanDev | None of its own: it builds from the manifest files and the ticket's `## Design fidelity` values | the PR diff adds every `repo_path` that section lists, and references each one |
| 3 | VanReviewer | `get_figma_data` on the ticket's `fileKey` + `nodeId` to confirm any value it doubts | the review file carries a `## Design fidelity` block |
| 4 | VanQA | None live (Figma is denied to it): it tests against the captured inventory, screenshots and manifest | the QA report carries a `## Design fidelity` block |

A step that cannot produce its artifact **stops and reports**; it never
substitutes an approximation. Relaying "done" without the artifact is exactly
how the placeholder shipped.

## Team mode (Profile `teammate` or `maintenance`)

Van is one developer on a human team that shares the repo and the board. Then:
- Work only on tickets assigned to `flow.assignee_filter`, or ones Van names in chat. `tracker_status.py
  --claim` enforces the filter and prints SKIP otherwise. Every other ticket is read-only.
- Never rewrite a human's ticket description; VanPM adds a comment or a linked sub-ticket.
- Follow the repo's own rules: `flow.pr_conventions` (PR template, CONTRIBUTING), CODEOWNERS, commit style.
  The PR body carries the ticket URL. Before opening the PR, VanDev merges `origin/<pr_base>` into the
  branch in its worktree if it is behind; never force-push a branch others may have checked out.
- Never merge, close or edit other people's PRs or branches, and never move other people's tickets.
- Human review comments are answered within one heartbeat (`PR_FEEDBACK`), but **a reply to a person is a message to
  a person: Van approves its text first**. VanDev fixes and pushes the code without waiting; it writes the reply as a
  draft and posts it only after Van says yes. Every agent comment starts with 🤖.

## When not to use this

A request that is only one agent's job ("fix the tickets", "refine this spec",
"fix the login bug", "review this PR", "test the password step") is not this
workflow. Spawn that agent directly, as the Team roster in `AGENTS.md` says.
These rules still apply to it:
- Code VanDev changes goes on a task branch with a PR (step 2) and gets a VanReviewer
  review on that PR (step 3) before you tell Van it is ready; merging stays Van's
  (step 5). Deploy fixes and "small" fixes included.
- A request that carries a **Figma link** is never a single-agent VanDev job, however
  small it sounds ("just make this header match the design"). It goes to VanPM first for
  the Figma pass and the `## Design fidelity` section; then VanDev, then review. See
  "Design-led work" above.
- If the work has a tracker ticket, VanPM claims it (step 2) and the delivery
  watcher (step 6) moves it once the change is on staging: the PR body must carry its ClickUp
  URL. Any ticket work goes to VanPM, never VanDev.

## Ticket statuses

`qa` means **merged and deployed to staging, ready for external QA**. It does not
mean "our VanQA ran": VanReviewer and VanQA are internal checks that happen while
the ticket is `in progress`. External QA (a person or agent outside this team)
sets `complete` or `rejected`; agents never set `complete` (one exception: `[SPIKE]` tickets, below).

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
`skills/feature-breakdown/scripts/tracker_status.py --context <CTX> --spec <spec> ...`.
`[SPIKE]` tickets produce a findings note (`<Internal Artifacts>/specs/<feature-slug>--spike.md`)
instead of code; VanPM sets them `complete` when the note exists (nothing deploys).

A ticket with no `.tracker.json` marker was not created through VanPM: report
it to Van instead of guessing.

## 0. Resolve the project

- If the request names a project, set `<slug>`. If it doesn't and more than one
  directory exists under `/home/openclaw/.openclaw/workspace/projects/` (ignore
  `_template`, `_tools`), ask which one.
- If CTX is missing → run the `project-onboarding` skill first.
- Run `python3 /home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py CTX`.
  Not VALID → fix via onboarding; do not continue.
- Keep `flow` and `status` from `validate_context.py CTX --json`: they decide which steps below run.
- If the request carries a Figma link, it is design-led: run the checks in
  "Design-led work" above (CTX has a Figma file + `figma-<slug>` server; the link
  goes to VanPM first) before step 1.
- Run the delivery watcher once (step 6) and handle what it prints.

## 1. Spec (VanPM) — stages `spec` + `tickets`

Spawn `project-manager`:

> Project `<slug>`. Context: `<CTX>`. Use `feature-breakdown` on: <feature list + Figma links>.
> Write the spec to `<Internal Artifacts>/specs/<feature-slug>.md` and stop
> for approval. Do not push tickets.

When the feature has Figma links, add to that message:

> These Figma links are the design contract, so the `feature-breakdown` Figma
> steps are mandatory for **every** link, through the `figma-<slug>` MCP server
> named in CTX: `download_figma_images` (screenshot), `view_image` (look at it),
> `get_figma_data` with the `nodeId` (exact text, sizes, hex colours, fonts,
> radii), then download the artwork itself (IMAGE fills, `[IMAGE-SVG]` nodes,
> `gifRef`s) into `specs/_figma/<feature-slug>/assets/` and write its
> `manifest.json`. Do not describe a screen from the PNG alone and do not
> approximate a value: every colour is a hex and every font is a real family in
> the spec. Every `[FE]` ticket carries `figma:`, `screenshots:`, `assets:` and a
> `## Design fidelity` section. If a Figma tool is missing or errors, stop and
> report it - do not fall back to the REST API or to eyeballing. Reply with the
> paths you wrote.

`sessions_yield` until done. On a design-led feature, **check the artifacts before
you relay anything**: `ls` `specs/_figma/<feature-slug>.md`, each screenshot PNG
(non-zero bytes - a 0-byte screenshot sat unnoticed in fms-studio for five days)
and `specs/_figma/<feature-slug>/assets/manifest.json`. Any of them missing or
empty → `sessions_send` VanPM to finish the Figma pass; do not relay the summary
and do not ask Van for a go on a spec that has no design data behind it.

Relay VanPM's summary (parent, subtasks per lane,
hours, open questions) to the user **verbatim**. Wait for Van's explicit "go".
No answer is not a go. On "go": `sessions_send` VanPM "approved, push". VanPM
replies with ticket links; relay them.

## 2. Build & PR (VanDev), one unit of work at a time, in dependency order

Branch, from the Flow **Branch model**:
- `feature-branch` (default): **one branch per feature**, `<branch prefix>/<feature-slug>`
  (`bug/<slug>` for a bug-only feature). Its lane tickets run **one at a time**
  (`[DB]` → `[BE]` → `[FE]` → `[INT]`), never in parallel: they share the branch,
  and two workers must never share a folder.
- `ticket-branch`: **one branch per ticket**, `<branch prefix>/<ticket id>-<short-slug>`.
  Each ticket gets its own branch, worktree and PR, so there is no shared-branch
  ordering constraint - but keep dependencies in order anyway.

"Lane tickets" only exist when VanPM created them. With Ticket source `human` the
units of work are whatever tickets the team already wrote, and with **no tracker**
it is the single piece of work Van named - one branch, one PR, no claim step.

For each unit of work:

1. Claim it - **only when the project has a tracker.** Spawn `project-manager`:

   > Project `<slug>`. Context: `<CTX>`. Claim ticket `<exact ticket title>` from
   > `<Internal Artifacts>/specs/<feature-slug>.md` with `tracker_status.py --claim --only`.
   > Reply with the script's GO or SKIP line. If this is the feature's first claim,
   > also set the `[Feature]` parent to the board's `doing` status.

   SKIP → skip this ticket. GO → continue.
   Tracker `none` → skip this step entirely; there is nothing to claim.

2. Spawn `developer`:

   > Project `<slug>`. Context: `<CTX>`. Implement ticket `<exact ticket title>` from
   > `<Internal Artifacts>/specs/<feature-slug>.md` on branch `<branch>`
   > (`worktree-lifecycle`: `sweep`, then `create <branch>`). Commit the changes. Then immediately push the branch (`git push -u origin <branch>`) and open a PR into `<PR base>` using `git_env.py <slug> -- gh pr create --base <PR base>`. The PR body must list the ticket's URL (skip when the project has no tracker). Reply with the PR URL and the commit SHA.

   When the ticket has a `## Design fidelity` section, add to that message:

   > This is a design-led ticket. Before you launch the coding agent, copy every
   > asset from `<Internal Artifacts>/specs/_figma/<feature-slug>/assets/` into the
   > worktree at the `repo_path` that section names (`install -D`), check each one
   > is non-empty, and put the asset paths and the exact tokens (hex colours, font
   > families and weights, radii) in the prompt. `agy` cannot see the design:
   > unprompted it writes a grey box and a text logo. No placeholder, no text
   > stand-in, no near colour from the framework palette, no value you eyeballed
   > from the screenshot. If the assets folder holds only `manifest.json`, or an
   > asset is 0 bytes, or the ticket gives you no `## Design fidelity` section at
   > all, stop and report it instead of building around it. Before you commit,
   > confirm the diff adds each asset **and** references it.

   `sessions_yield`. A stop of that kind is VanPM's to fix (rebuild the asset cache
   from the manifest, or write the missing `## Design fidelity` section), not
   VanDev's and not yours. VanDev says the spec is wrong or impossible → VanPM sets
   the ticket `on hold`, go back to step 1 with the objection; never "fix" the
   spec yourself.

## 3. Review (VanReviewer on GitHub) — stage `review`

Spawn `code-reviewer`:

> Project `<slug>`. Context: `<CTX>`. Review the PR at `<PR URL>` natively on GitHub using `git_env.py <slug> -- gh pr review <PR URL>`. If changes are needed, use `--request-changes` and leave your comments on GitHub. If it is good, use `--comment` with `APPROVED` as the first line of the body (`--approve` fails: same GitHub account as the PR author). Save the same review as `<Internal Artifacts>/reviews/<feature-slug>--<lane-slug>.md` (line 1 verdict, line 2 `Reviewed SHA: <head sha>`), then run `git_env.py <slug> --review-status <PR URL>`. Reply with the verdict, the file path and that command's output line.

When the PR's ticket has a `## Design fidelity` section, add to that message:

> Check the design too, against the raw Figma data - not against the screenshot
> and not by eye. Every `repo_path` in the ticket's `## Design fidelity` section is
> an added, non-empty file in the diff **and** is referenced by code in the same
> diff; the diff contains no `placeholder`/`Placeholder`/`[Image`/`Logo</` and no
> plain coloured box where artwork belongs; the hexes and font families are the
> exact ones in the section, defined once in the theme rather than per component.
> Any value the ticket does not state, or one you think is wrong, you resolve with
> `get_figma_data` on the ticket's `fileKey` + `nodeId` through the `figma-<slug>`
> server - read only: never re-download assets, never another project's server.
> Your review file carries a `## Design fidelity` block: one line per asset (repo
> path → the file:line that renders it, or MISSING) and one line on the tokens. A
> missing or unreferenced asset, a stand-in, or a wrong token is **blocking**.

- `ls` the review file before relaying the verdict. On a design-led ticket, read it
  and confirm the `## Design fidelity` block is there: a verdict without it is not a
  review of this ticket, so send it back rather than relaying an approval.
- The review's result on GitHub is the commit status `openclaw/review` on the PR head (green = APPROVED,
  red = CHANGES REQUESTED). Any push after the review is a new commit without it, so every fix is reviewed
  again (this includes `PR_FEEDBACK` fixes). If VanReviewer's line says `403 … Commit statuses`, tell Van once:
  the project token needs the permission "Commit statuses: Read and write".
- `CHANGES REQUESTED` → back to step 2: spawn VanDev with the feedback to pull the review from GitHub (`git_env.py <slug> -- gh pr view <PR URL> --comments`), fix it, push, and reply on the PR.
- `APPROVED` → Next lane ticket (step 2).

## 4. Verify (VanQA), once per feature, after all lane tickets are approved — stage `internal-qa`

This is our internal pre-merge check; it changes no ticket status. Spawn `qa-engineer`:

> Project `<slug>`. Context: `<CTX>`. Verify `<feature-slug>` on branch `<branch>` against its
> acceptance criteria (your own worktree: `create <branch> --agent qa-engineer`, then
> `finish <branch>`). Use only the test commands in PROJECT_CONTEXT. Write
> `<Internal Artifacts>/qa/<feature-slug>.md` with the tested SHA. Do not modify code,
> commit or push.

When the feature is design-led, add to that message:

> Verify the screens against the captured Figma data, which is the same raw
> extraction the spec was written from: the screen inventory
> `<Internal Artifacts>/specs/_figma/<feature-slug>.md` (every element, its exact
> copy and its tokens), the screenshots `specs/_figma/<feature-slug>/<nodeId>.png`
> (open them with `view_image` and compare against the running screen), and
> `specs/_figma/<feature-slug>/assets/manifest.json` (every asset, and the
> `repo_path` it must live at). Figma itself is denied to you - that inventory is
> your source, and it is what the tickets were written from, so a disagreement
> between the two is a finding. Confirm each manifest asset exists in the branch at
> its `repo_path`, is non-empty, and is what actually renders on the screen; check
> the tokens as rendered (computed colour, font family, radius), not as declared in
> a config file. Report it in a `## Design fidelity` block in your report, one line
> per asset and one on the tokens. A placeholder box, a text stand-in or a near
> colour is a defect with the same weight as a broken button.

What VanQA tests against depends on what exists: the `[QA]` ticket's scenario plus the
parent's criteria when VanPM wrote the spec; otherwise the human ticket's own acceptance
criteria, or - with no tracker - the change Van described. Name the source in the spawn
message. `internal-qa` without `tickets` is legitimate; do not invent a `[QA]` ticket.

- Passed → step 5.
- Defects, **with a tracker** → spawn VanPM: "add a bug ticket per defect **to the same
  spec** `<feature-slug>.md`, under the same parent, and push it". Then step 2 for each new
  ticket on the **same branch**, step 3, then step 4 again.
- Defects, **no tracker** (or Ticket source `human`, where we do not write tickets) → relay
  the QA report to Van with the defect list and let him decide; the fix then goes through
  step 2 as its own unit of work.

## 5. Final Readiness Gate (User checks off on merge) — stage `merge-gate`

First verify, then send the message the Flow **Merge by** calls for.

- Verify with **`git_env.py <slug> --readiness <n>`**. It prints the review stamp and every check on
  the PR's current head, and exits non-zero unless all of them are green. Do not eyeball this yourself:
  the old instruction was to read `statusCheckRollup`, which only ever surfaced `openclaw/review`, so a
  RED CI check was invisible to the one gate meant to catch it (fms-studio PR #39: the PR Checks
  workflow failed and nothing in the pipeline noticed). It also needs a token permission we do not have.
- Exit 0 → reviewed and green. Exit 2 → it prints `NOT READY:` and the blockers; relay them and stop.
  Exit 3 → something could not be READ (a missing token permission); say exactly that rather than
  calling it ready. Also confirm the head SHA is the one VanQA tested.
- A red check is VanDev's to fix on the same branch, then the new head needs a new review (step 3).
- On a design-led feature, also read the review file and the QA report and confirm both carry
  their `## Design fidelity` block, each asset accounted for. `git_env.py` cannot see the design;
  this is the last place a placeholder can still be caught before Van merges it.

- **Merge by `van`** (default): "Feature `<feature-slug>` passed review and QA. Everything is ready on
  the PR. Merging is yours; tickets move when the merge is detected." Relay the PR link.
- **Merge by `humans`** (team projects): the PR is not Van's to merge, so do not tell him it is. Say the
  PR is ready for the team's reviewers, relay the link, and name anything they will look for that is not
  done yet (the repo's PR template, CODEOWNERS approvals, required checks). Then stop: a reviewer's
  comment comes back as `PR_FEEDBACK` in step 6.

**Nobody on this team merges, in either case.** `git_env.py` refuses every merge; never work around it.

## 6. After the PR: the delivery watcher (heartbeat, every 15 min) — stage `delivery-watch`

Van merges on GitHub. From then on nothing waits for a person: every heartbeat runs

    python3 /home/openclaw/.openclaw/workspace/projects/_tools/delivery_watch.py <slug>

for each project. It only reads GitHub, the project's tracker and its CI provider, and
prints ACTIONs, each with what to do and an `--ack <id>` command. Carry out each action,
then ack it. An action you could not finish stays un-acked and comes back next heartbeat.

Where an action says to post in the project's Flow **Chat channel**, use that channel; a
project that sets none gets the line in the channel the heartbeat is already running in.

- `PR_FEEDBACK`: new comments/reviews on an open PR. `sessions_send` (or spawn) VanDev with the feedback;
  VanDev fixes it in its own worktree and pushes to the same branch; then VanReviewer reviews the new head
  (step 3, `--review-status`). The code fix needs no approval question.
  The **reply on the PR** depends on the project's Flow profile:
  - `factory` (only Van reads these PRs): VanDev posts it itself, starting with "🤖 VanDev:".
  - `teammate` / `maintenance` (other people read it): VanDev returns the draft text instead. Relay it to Van
    verbatim and ask for a yes; silence is a NO. On yes, `sessions_send` VanDev "approved, post this reply".
    Ack the action only once the reply is posted or Van says not to send one.
- `DEPLOYED`: spawn VanPM with the listed tickets → `staged`; post one line in the project's
  Flow **Chat channel**: what is on staging, ready for testing.
- `BUILD_FAILED`: one line to Van with build id and log link; VanPM files a bug ticket
  (the PR's spec, or a new `staging-build-<sha>` spec); then the normal flow for it. The
  original tickets move to `qa` by themselves once a later build containing them succeeds.
- `NO_BUILD` / `PR_CLOSED` / `STALE_WORKTREE`: tell Van; for `PR_CLOSED` ask drop or redo.
- `REJECTED`: one line to Van; VanPM `--claim`s the ticket (→ `in progress`); VanDev fixes
  it on `bug/<feature-slug>--<ticket id>` using QA's comments; normal flow; the PR body lists
  the ticket URL, and the ticket returns to `qa` when the fix is on staging.
- `FEATURE_COMPLETE`: spawn VanPM:

  > Project `<slug>`. Context: `<CTX>`. Every ticket of `<feature-slug>` is complete. Archive the
  > feature: move `specs/<feature-slug>.md` and its `.tracker.json` marker to `specs/_done/`, delete
  > the rows its `[DB]` tickets own from `specs/_planned-data.md` (the Schema file now holds
  > them; set **Schema file** in PROJECT_CONTEXT if this was the first `[DB]` ticket), and run
  > `projects/_tools/spec_index.py <slug>`.

  Then run `worktree.py <slug> sweep`, append the feature to MEMORY.md (step 7) and post
  one line in the project's Flow **Chat channel**.
- `MERGED` (projects with Deploy signal `none`): spawn VanPM, tickets → `staged` or `done` as the action says;
  on team projects only Van's tickets.
- `LINT` (daily, first project only): post the listed lines in one message; never fix files from a heartbeat.
- `SWEEP_DUE`: run `worktree.py <slug> sweep`; relay any KEPT / UNMANAGED / PRIMARY line.

Nobody in the team merges, deploys, retries builds or sets `complete` (except `[SPIKE]`, see Ticket statuses).

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
