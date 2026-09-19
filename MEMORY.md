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

## Projects

### fms-studio
- Context: `/home/openclaw/.openclaw/workspace/projects/fms-studio/PROJECT_CONTEXT.md`
- Onboarded 2026-09-09 (context brought to template shape 2026-09-16). Legacy umbrella specs were superseded 2026-09-19 (`specs/_superseded/`).
- **2026-09-17**: `organizer-flow-landing-page-no-account` built, reviewed, QA'd (PR #3 era). Its tickets were marked complete before any PR existed.
- **2026-09-17 evening**: the fresh Nx scaffold (PR #15) replaced the frontend and **removed the landing page from `Development`**. Restore is PR #32 (`feature/restore-landing-pages`), open as of 2026-09-19; its tickets were reset to `to do`.
- **2026-09-17/18**: ~28 PRs (#3-#31, deploy/lockfile/peer-dep fixes) went out with no review or QA. Commit `90e659b` on `Development` is a README line VanQA pushed "to trigger CI".
- **2026-09-19 lessons** (setup audit): approval questions that time out are a NO; task branch is pushed and the PR opened right after the lane commit, then reviewed on the PR (`openclaw/review` status on the head SHA, re-review after every push); QA gets its own worktree; nobody but Van merges; `nx test-ci` does not work (see PROJECT_CONTEXT test commands).
