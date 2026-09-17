# MEMORY.md - Durable facts and project index

Main session only. One section per onboarded project. IDs and secret names are
NOT here; they live in each project's PROJECT_CONTEXT.md.

## Team conventions (2026-09-16)
- Agents and workflows are registered in the Team roster section of `AGENTS.md`; after adding or removing one, run `_tools/validate_team.py`.

## Software project conventions (2026-09-16)
- Pipeline: `project-orchestration` skill. Onboarding: `project-onboarding` skill.
- PM decomposition: `feature-breakdown` skill (one parent ticket + lane subtasks, spec-first, approval before push).
- Context files are validated by `projects/_tools/validate_context.py`; if a run fails on IDs/secrets/statuses, fix the file, not the tooling.

## Projects

### fms-studio
- Context: `/home/openclaw/.openclaw/workspace/projects/fms-studio/PROJECT_CONTEXT.md`
- Onboarded 2026-09-09 (context brought to template shape 2026-09-16). 11 legacy screen tickets in ClickUp are adopted as `[Feature]` parents via `existing_id`.
- First spec written 2026-09-16: `artifacts/specs/event-creation-step-3-1-set-password.md` (not pushed yet).
