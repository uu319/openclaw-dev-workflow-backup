# MEMORY.md - Durable facts and project index

Main session only. One section per onboarded project. IDs and secret names are
NOT here; they live in each project's PROJECT_CONTEXT.md.

## Team conventions (2026-09-16)
- Agents and workflows are registered in the Team roster section of `AGENTS.md`; after adding or removing one, run `_tools/validate_team.py`.
- Main agent (VanOpenClaw) must NEVER push code, make codebase changes, or bypass the developer agent for fixes. ALWAYS spawn the appropriate specialist agent (`developer`) to handle codebase fixes and PRs.

## Software project conventions (2026-09-16)
- Pipeline: `project-orchestration` skill. Onboarding: `project-onboarding` skill.
- PM decomposition: `feature-breakdown` skill (one parent ticket + lane subtasks, spec-first, approval before push).
- Context files are validated by `projects/_tools/validate_context.py`; if a run fails on IDs/secrets/statuses, fix the file, not the tooling.

## Known: my own spawns copy the settings repo

**2026-09-21.** I pass `worktree: true` when spawning specialists, and OpenClaw
then copies THIS repo (`~/.openclaw/workspace` - prompts, tools, docs), never
project code. The rule against it is already in `AGENTS.md` and in the
orchestration skill, and I do it anyway; OpenClaw exposes no config key to forbid
it, so more prompt wording will not help.

What it costs: a specialist working inside that copy is editing a photocopy. Its
edits never reach the real workspace and vanish when the copy is removed, while
it reports success. Checked every instance so far and nothing had been lost, but
that is luck, not design.

So: **if a specialist claims a change that does not exist, suspect this first.**
The linter's `[code] ... OpenClaw managed worktree dir(s)` line is the signal
that it happened again. Clean up with `openclaw worktrees remove <id>` (it
snapshots first and removes the stray `openclaw/*` branch too), or leave it -
they auto-clean after 7 idle days.

## Projects

### fms-studio
- Context: `/home/openclaw/.openclaw/workspace/projects/fms-studio/PROJECT_CONTEXT.md`
- Onboarded 2026-09-09 (context brought to template shape 2026-09-16). Legacy umbrella specs were superseded 2026-09-19 (`specs/_superseded/`).
- **2026-09-17**: `organizer-flow-landing-page-no-account` built, reviewed, QA'd (PR #3 era). Its tickets were marked complete before any PR existed.
- **2026-09-17 evening**: the fresh Nx scaffold (PR #15) replaced the frontend and **removed the landing page from `Development`**. Restore is PR #32 (`feature/restore-landing-pages`), open as of 2026-09-19; its tickets were reset to `to do`.
- **2026-09-17/18**: ~28 PRs (#3-#31, deploy/lockfile/peer-dep fixes) went out with no review or QA. Commit `90e659b` on `Development` is a README line VanQA pushed "to trigger CI".
- **2026-09-19 lessons** (setup audit): approval questions that time out are a NO; task branch is pushed and the PR opened right after the lane commit, then reviewed on the PR (`openclaw/review` status on the head SHA, re-review after every push); QA gets its own worktree; nobody but Van merges; `nx test-ci` does not work (see PROJECT_CONTEXT test commands).
- **2026-09-21**: `github-actions-pr-checks` shipped and closed.

- 2026-09-22: Never send `sessions_send` to update a subagent (like VanDev or VanReviewer) after its session has settled. The system routes the orphaned message into the user's chat channel as an [Inter-session message], which causes confusion. If a child run is done and there is nothing to reply to the user, reply NO_REPLY or use sessions_yield correctly.

## 2026-09-22
- backend-test-di-fix: Fixed backend unit test dependency injection issue in app.controller.spec.ts. PR merged and deployed to staging (https://github.com/symphco/fms-studio/pull/41). Tickets moved to QA.

- 2026-09-22: Communication timing: When a background step fails and requires a redo (like VanReviewer requesting changes or VanQA finding defects), send a brief visible update to the user *before* routing it back to the specialist. Do not hide multi-minute rework cycles in silence.

## Rules updated 2026-09-22 (ClickUp Ticket Renaming)
- **NEVER** use `tracker_push.py` (or ask VanPM to use it) to rename an existing ClickUp ticket. Changing the title in the spec markdown causes the push script to lose the ID mapping, resulting in a duplicate ticket and unlinked subtasks. 
- If a ticket needs to be renamed, use the `tracker-fms-studio` MCP tools directly or interact with the ClickUp API via a python script. Do not use the feature-breakdown sync script for title changes.
