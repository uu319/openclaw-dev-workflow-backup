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
- **GitHub Repo:** `<owner/repo>` (delete this line when the project is not on GitHub; when it is
  set, the GitHub Token SecretRef below becomes required)
- **Default branch:** `main`

## Stack
<!-- Filled by VanPM by inspecting the repo. No guesses: "unknown" is acceptable, an invented framework is not. -->
- **Layout:** <monorepo tool / single app>
- **frontend/**: <framework + version, test runner, where routes live>
- **backend/**: <framework + version, test runner, where modules live>
- **Database:** <ORM + engine, or "none yet">
- **Schema file:** <path to the ORM schema in the repo (e.g. `backend/prisma/schema.prisma`), or "none yet">
- **Repo state:** <scaffold / active / legacy; commit count>

## Tracker & Design
- **Tracker Tool:** ClickUp
- **ClickUp List ID:** <digits only, copied from the list URL or list settings; never discovered by API>
- **ClickUp List name:** <as shown in ClickUp, confirmed by validate_context.py --live>
- **Figma file:** <https://www.figma.com/design/... or none>
- **Figma MCP server:** `figma-<slug>` (required when Figma file is set; delete this line when it is none)
- **GCP Environment:** <prose: which environments exist, or "none">
- **GCP Project ID:** `<gcp-project-id>` (delete this line when the project has no GCP; when it is
  set, the two GCP SecretRefs below become required)
- **GCP Region:** `<region>`
- **SecretRefs:**
  - Tracker: `CLICKUP_API_TOKEN_<SLUGUPPER>`
  - Design: `FIGMA_API_KEY_<SLUGUPPER>`
  - GCP Key Vault: `GCP_SA_KEY_<SLUGUPPER>_<ENV>`
  - GCP Key JSON: `/home/openclaw/.openclaw/workspace/credentials/gcp/<slug>.json`
  - Reach GCP only through `projects/_tools/gcloud_env.py <slug> -- <command>`; there is no
    ambient gcloud default and `gcloud` run bare will not be pointed at this project.
  - GitHub Token: `GITHUB_TOKEN_<SLUGUPPER>` (env-kind vault entry; fine-grained PAT scoped to this
    repo only: Contents + Pull requests read/write)
  - Reach the GitHub API only through `projects/_tools/git_env.py <slug> -- gh <args>`; bare `gh`
    has no login on this box.

## Workflow Rules
- **Statuses:** `to do`, `in progress`, `qa for development`, `on hold`, `complete`, `cancelled`
- **Create status:** `to do`
- **Branch Prefixes:** `feature/`, `bug/`
- **Install command:** `<exact command run inside a fresh worktree, e.g. npm ci>`
- **Dev/QA Test Commands:** explicit, never inferred (inferring them hung QA 28 times on the old box). VanPM fills these during onboarding after running each one once in a worktree.
  - Tests: `<exact command that runs once and exits>`
  - Lint: `<exact command>`
  - E2E: `<exact command, or "none yet: first feature carries [INT] Set up Playwright E2E runner">`
  - Forbidden: `<any watch-mode target>`

## Ticket conventions (enforced by the PM's `feature-breakdown` skill)
- One parent ticket per user-visible feature: `[Feature] <Area>: <Outcome>`.
- Subtasks per engineering lane, only the lanes the feature touches: `[FE]`, `[BE]`, `[DB]`, `[INT]`, `[QA]`, `[SPIKE]`. Each ≤ 8h.
- Every ticket body follows the template: Context · User story · In scope · Out of scope · Acceptance criteria (Given/When/Then, falsifiable) · Technical notes · Depends on/blocks · Test notes · Definition of done.
- Tags: `agent-created` + lane tag. Priority: urgent=1, high=2, normal=3, low=4. Estimates in `time_estimate`.
- Dependencies pushed as ClickUp task links. `[DB]` → `[BE]` → `[FE] wiring`; `[QA]` last.
- Specs live in `artifacts/specs/<feature-slug>.md`; the push writes `<feature-slug>.clickup.json` next to it.

## Artifact Routing
- **Code (CWD):** `/home/openclaw/projects/<slug>`
  Primary checkout, **read-only for agents** and kept on the Default branch. All code work
  happens in per-task worktrees under `/home/openclaw/projects/.worktrees/<slug>/`, created and
  removed only by `projects/_tools/worktree.py <slug> ...` (shared `worktree-lifecycle` skill).
  PR history: `prs.md` in Internal Artifacts (generated from `worktrees.jsonl`).
- **Internal Artifacts:** `/home/openclaw/.openclaw/workspace/projects/<slug>/artifacts/` (`specs/`, `patches/`, `reviews/`, `qa/`)
