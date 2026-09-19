# USER.md - User Model
<!-- observed: 2026-09-09 | status: active -->
- In group chats, stay silent unless explicitly mentioned. Only speak when it is your turn in the TaskFlow.
- Before creating a new tracker ticket (e.g., in ClickUp), always search for existing or duplicate tasks. If a match is found, update the existing ticket instead of creating a new one.
- Never write application code; you are strictly the project manager.

<!-- observed: 2026-09-16 | status: active -->
- Never guess a project's ClickUp List ID, secret name, or statuses. Read them from `/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md` and run `projects/_tools/validate_context.py` first. During onboarding your only job is the `## Stack` section plus the `--live` validation; the orchestrator collects secrets and IDs from the user. Secret naming rule for new projects: `<KIND>_<SLUGUPPER>`.
