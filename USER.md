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
- Always run software feature work for onboarded projects through the 5-Layer WRARM framework (Workflow, Roles, Artifacts, Rules, Memory) in the `project-orchestration` skill: spawn isolated subagents, write completion markers to the project's `artifacts/`, gate every external side effect (ClickUp writes, pushes, sends) on Van's explicit yes, and persist durable state in `MEMORY.md`. When spawning VanDev (developer) via `sessions_spawn`, always explicitly set `cwd` to the project's root directory (e.g., `/home/openclaw/.openclaw/workspace/projects/<slug>`) so their terminal is focused on the code.
<!-- project: path:/home/openclaw/.openclaw/workspace -->

<!-- observed: 2026-09-16 | status: active -->
- Figma goes through the Figma MCP (`figma-developer-mcp`), one server per project: `mcp.servers["figma-<slug>"]` runs `projects/_tools/figma_mcp.py <slug>`, which loads only that project's Design key from its PROJECT_CONTEXT.md. Only VanPM and VanDev have the Figma tools; main, QA and reviewer do not. OpenClaw still starts each `figma-*` server (~120 MB) in any agent session with tools, because a tool deny only hides tools; idle servers shut down after 5 minutes (`mcp.sessionIdleTtlMs`). Never call the Figma REST API directly, and never use another project's `figma-*` server.

<!-- observed: 2026-09-16 | status: active -->
- Always onboard projects with the `project-onboarding` skill. Per-project secrets are named `<KIND>_<SLUGUPPER>` (slug uppercased, hyphens removed). The user stores them with `openclaw secrets store set <NAME> --value-file -`. The only source of truth for a project's IDs, secret names, and statuses is `/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md`, validated by `projects/_tools/validate_context.py`. Never derive these from memory, from scripts, or from this file: USER.md holds working preferences only, never project IDs or secret names.
<!-- project: path:/home/openclaw/.openclaw/workspace -->

## Related

- [Agent workspace](/concepts/agent-workspace)
