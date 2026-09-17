# Project Context: fms-studio

<!-- Single source of truth for this project. Every agent reads this before acting.
     Keep the field labels exactly as written: tooling parses them by label.
     Validate after every edit: python3 /home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py <this file> -->

## Identity
- **Slug:** `fms-studio`
- **Display name:** FindMyShots Studio
- **Onboarded:** 2026-09-09 by Van (context file brought to template shape 2026-09-16)

## Repository
- **Git SSH Clone URL:** `git@fms-studio.github.com:symphco/fms-studio.git`
- **SSH Alias:** `fms-studio.github.com`
- **Default branch:** `Development`

## Stack
- **Layout:** Nx monorepo (`nx.json`, Nx 23). Run tasks with `npx nx <target> <project>`.
- **frontend/**: Next.js 15 + React 19 + Tailwind 4, tests with Vitest + Testing Library. App router under `frontend/src/app/`.
- **backend/**: NestJS 11 (webpack build), tests with Vitest. Modules under `backend/src/app/`.
- **Database:** none yet. The first feature that persists data must include a `[DB]` ticket that chooses and sets up the ORM and the first table.
- **Repo state:** scaffold only (2 commits). Assume nothing exists until you read the tree.

## Tracker & Design
- **Tracker Tool:** ClickUp
- **Tracker MCP Prefix:** clickup_
- **ClickUp List ID:** `1100770000001008`
- **Figma file:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding
- **Figma MCP server:** `figma-fms-studio` (tools `figma-fms-studio__get_figma_data`, `figma-fms-studio__download_figma_images`; uses only this project's Design key)
- **GCP Environment:** Staging only (`fms-studio-staging`), region: `asia-southeast1`. No production environment exists yet.
- **SecretRefs:**
  - Tracker: `CLICKUP_API_TOKEN_FMSSTUDIO` (exact name in the OpenClaw secret vault; no fallback)
  - Design: `FIGMA_API_KEY_FMSSTUDIO` (env-kind vault entry; loaded only by the `figma-fms-studio` MCP server via `projects/_tools/figma_mcp.py`)
  - GCP Staging Vault: `GCP_SA_KEY_FMSSTUDIO_STAGING` (exact name in the OpenClaw secret vault)
  - GCP Staging JSON: `/home/openclaw/.openclaw/workspace/credentials/gcp/fms-studio.json`

## Workflow Rules
- **Statuses:** `to do`, `in progress`, `qa`, `for development`, `on hold`, `complete`, `cancelled`
- **Create status:** `to do`
- **Branch Prefixes:** `feature/`, `bug/`
- **Dev/QA Test Commands:** AI will automatically infer test commands by inspecting the repository (e.g., `package.json` scripts, `project.json` targets) rather than requiring manual configuration.

## Ticket conventions (enforced by the PM's `feature-breakdown` skill)
- One parent ticket per user-visible feature: `[Feature] <Area>: <Outcome>`.
- Subtasks per engineering lane, only the lanes the feature touches: `[FE]`, `[BE]`, `[DB]`, `[INT]`, `[QA]`, `[SPIKE]`. Each ≤ 8h.
- Every ticket body follows the template: Context · User story · In scope · Out of scope · Acceptance criteria (Given/When/Then, falsifiable) · Technical notes · Depends on/blocks · Test notes · Definition of done.
- Tags: `agent-created` + lane tag. Priority: urgent=1, high=2, normal=3, low=4. Estimates in `time_estimate`.
- Dependencies pushed as ClickUp task links. `[DB]` → `[BE]` → `[FE] wiring`; `[QA]` last.
- Specs live in `artifacts/specs/<feature-slug>.md`; the push writes `<feature-slug>.clickup.json` next to it (completion marker; re-runs update instead of duplicate).
- The 11 legacy screen tickets (Sept 15) are adopted as parents via `existing_id` in their specs, not deleted.

## Artifact Routing
- **Code (CWD):** `/home/openclaw/projects/fms-studio`
- **Internal Artifacts:** `/home/openclaw/.openclaw/workspace/projects/fms-studio/artifacts/` (`specs/`, `patches/`, `reviews/`, `qa/`)
