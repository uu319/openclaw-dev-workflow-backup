# USER.md - User Model

Store stable user preferences and profile facts as directives that can guide future sessions.

Use one directive per entry:

```md
<!-- observed: YYYY-MM-DD | status: active -->

- Prefer concise progress updates during implementation work.
```

- Begin each directive with an imperative such as `Always`, `Never`, or `Prefer`.
- Record the observation date and either `active` or `superseded` on the metadata line.
- When a preference changes, mark the old entry `superseded` and rewrite the active directive in place. Never append a contradictory active directive.
- Keep stable communication style, relationships, and active-project context here. Put durable non-profile facts and decisions in `MEMORY.md`.

## Directives

<!-- observed: 2026-09-10 | status: active -->
- Always remember the environment is a Hostinger VPS. Take remote/headless access constraints into account (e.g., SSH port forwarding, Tailscale) when suggesting commands or UI access.

<!-- observed: 2026-09-16 | status: superseded -->
- Always run multi-step project work through the 5-Layer WRARM framework (Workflow, Roles, Artifacts, Rules, Memory) as defined in the `project-orchestration` skill: VanOpenClaw orchestrates only; `project-manager` (VanPM) plans and owns tickets via its `feature-breakdown` skill; `developer` (VanDev) builds; `code-reviewer` reviews; `qa-engineer` verifies. Each project's workbench and artifact paths come from its `PROJECT_CONTEXT.md`. Spawn isolated subagents, write completion markers to `projects/<project>/artifacts/`, gate every external side-effect (ClickUp writes, pushes, sends) on explicit user approval, persist durable state in `MEMORY.md`.
<!-- project: path:/home/openclaw/.openclaw/workspace -->

<!-- observed: 2026-09-15 | status: superseded -->
- As the Orchestrator (VanOpenClaw), strictly NEVER execute task work directly (e.g., writing code, making API calls, managing tickets). Always delegate by using `sessions_spawn` to invoke the correct subagent (`project-manager` for planning/tickets, `developer` for code, etc.). Do not bypass the WRARM routing.
<!-- project: path:/home/openclaw/.openclaw/workspace -->

<!-- observed: 2026-09-16 | status: active -->
- Always act as Van's main agent, not a dev-only orchestrator: answer simple questions directly, run a workflow when one fits, and spawn the owning agent from the Team roster in `AGENTS.md` for anything that is that agent's job. Never do a specialist's work (code, specs, tickets, reviews, tests) yourself; pass the request to the specialist word for word and let it ask the clarifying questions.
<!-- project: path:/home/openclaw/.openclaw/workspace -->

<!-- observed: 2026-09-16 | status: active -->
- Always run software feature work for onboarded projects through the 5-Layer WRARM framework (Workflow, Roles, Artifacts, Rules, Memory) in the `project-orchestration` skill: spawn isolated subagents, write completion markers to the project's `artifacts/`, gate every external side effect (ClickUp writes, pushes, sends) on Van's explicit yes, and persist durable state in `MEMORY.md`. Never set `cwd` or `worktree: true` on a spawn: put the project slug, its PROJECT_CONTEXT.md path and the branch name in the message; each specialist makes its own code worktree with the `worktree-lifecycle` skill.
<!-- project: path:/home/openclaw/.openclaw/workspace -->

<!-- observed: 2026-09-16 | status: active -->
- Figma goes through the Figma MCP (`figma-developer-mcp`), one server per project: `mcp.servers["figma-<slug>"]` runs `projects/_tools/figma_mcp.py <slug>`, which loads only that project's Design key from its PROJECT_CONTEXT.md. Only VanPM and VanDev use the Figma tools; QA and reviewer have them denied, and main has them only so the VanPM it spawns inherits them (main never calls them). OpenClaw still starts each `figma-*` server (~120 MB) in any agent session with tools, because a tool deny only hides tools; idle servers shut down after 5 minutes (`mcp.sessionIdleTtlMs`). Never call the Figma REST API directly, and never use another project's `figma-*` server.

<!-- observed: 2026-09-16 | status: active -->
- Always onboard projects with the `project-onboarding` skill. Per-project secrets are named `<KIND>_<SLUGUPPER>` (slug uppercased, hyphens removed). The user stores them with `openclaw secrets store set <NAME> --kind env --value-file -` (without `--kind env` the launchers cannot read them). The only source of truth for a project's IDs, secret names, and statuses is `/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md`, validated by `projects/_tools/validate_context.py`. Never derive these from memory, from scripts, or from this file: USER.md holds working preferences only, never project IDs or secret names.
<!-- project: path:/home/openclaw/.openclaw/workspace -->

## Related

- [Agent workspace](/concepts/agent-workspace)

<!-- observed: 2026-09-17 | status: active -->
Always ensure the dev server is started with a dynamic port and exposed via `portal` for frontend/backend tasks, and share the portal link with the user so they can view progress.

<!-- observed: 2026-09-17 | status: active -->
- Always use the MCP (Model Context Protocol) architecture for project management trackers (e.g., Jira, Linear, ClickUp) instead of building custom bespoke skills or using brittle file-based syncing. Add the official or custom MCP server to OpenClaw's config, declare the tracker and its tool prefix (e.g., `linear_*`, `jira_*`) in the project's `PROJECT_CONTEXT.md`, VanPM reads tickets with those MCP tools, but writes (create, update, status) go only through its `feature-breakdown` scripts (`clickup_push.py`, `clickup_status.py`), which keep the spec markers in sync.
