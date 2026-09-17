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
- **Default branch:** `main`

## Stack
<!-- Filled by VanPM by inspecting the repo. No guesses: "unknown" is acceptable, an invented framework is not. -->
- **Layout:** <monorepo tool / single app>
- **frontend/**: <framework + version, test runner, where routes live>
- **backend/**: <framework + version, test runner, where modules live>
- **Database:** <ORM + engine, or "none yet">
- **Repo state:** <scaffold / active / legacy; commit count>

## Tracker & Design
- **Tracker Tool:** ClickUp
- **ClickUp List ID:** <digits only, copied from the list URL or list settings; never discovered by API>
- **ClickUp List name:** <as shown in ClickUp, confirmed by validate_context.py --live>
- **Figma file:** <https://www.figma.com/design/... or none>
- **Figma MCP server:** `figma-<slug>` (required when Figma file is set; delete this line when it is none)
- **SecretRefs:**
  - Tracker: `CLICKUP_API_TOKEN_<SLUGUPPER>`
  - Design: `FIGMA_API_KEY_<SLUGUPPER>`

## Workflow Rules
- **Statuses:** `to do`, `in progress`, `qa for development`, `on hold`, `complete`, `cancelled`
- **Create status:** `to do`
- **Branch Prefixes:** `feature/`, `bug/`
- **Dev/QA Test Commands:** inferred from the repo (`package.json` scripts, `project.json` targets); never hand-maintained here.

## Ticket conventions (enforced by the PM's `feature-breakdown` skill)
- One parent ticket per user-visible feature: `[Feature] <Area>: <Outcome>`.
- Subtasks per engineering lane, only the lanes the feature touches: `[FE]`, `[BE]`, `[DB]`, `[INT]`, `[QA]`, `[SPIKE]`. Each ≤ 8h.
- Every ticket body follows the template: Context · User story · In scope · Out of scope · Acceptance criteria (Given/When/Then, falsifiable) · Technical notes · Depends on/blocks · Test notes · Definition of done.
- Tags: `agent-created` + lane tag. Priority: urgent=1, high=2, normal=3, low=4. Estimates in `time_estimate`.
- Dependencies pushed as ClickUp task links. `[DB]` → `[BE]` → `[FE] wiring`; `[QA]` last.
- Specs live in `artifacts/specs/<feature-slug>.md`; the push writes `<feature-slug>.clickup.json` next to it.

## Artifact Routing
- **Code (CWD):** `/home/openclaw/projects/<slug>`
- **Internal Artifacts:** `/home/openclaw/.openclaw/workspace/projects/<slug>/artifacts/` (`specs/`, `patches/`, `reviews/`, `qa/`)
