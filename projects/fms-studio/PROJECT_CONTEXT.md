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
- **GitHub Repo:** `symphco/fms-studio`
- **Default branch:** `Development`

## Stack
- **Layout:** Nx monorepo (`nx.json`, Nx 23). Run tasks with `npx nx <target> <project>`.
- **frontend/**: Next.js 15.1 + React 19, tests with Vitest + Testing Library. App router under `frontend/src/app/`.
  (No Tailwind in the lockfile as of 2026-09-18; do not assume it.)
- **backend/**: NestJS 11 (webpack build), tests with Vitest. Modules under `backend/src/app/`.
- **Database:** none yet. The first feature that persists data must include a `[DB]` ticket that chooses and sets up the ORM and the first table.
- **Schema file:** none yet. The `[DB]` ticket that sets up the ORM sets this path. Planned
  columns live in `artifacts/specs/_planned-data.md`.
- **E2E:** `cypress` 13 and `@playwright/test` are dependencies and `@nx/playwright` infers an `e2e`
  target, but there is no Cypress or Playwright config in the repo yet.
- **Deploy (staging):** Cloud Build configs in `.cloudbuild/` (`cloudbuild-frontend-staging.yaml`,
  `cloudbuild-backend-staging.yaml`): `npm ci` -> `nx run <app>:build` -> `nx run <app>:deploy-prepare` ->
  App Engine (`nodejs22`; frontend = service `default`, backend = service `backend`, per each `app.yaml`).
  Check builds via `gcloud_env.py fms-studio -- gcloud builds list`.
- **Deploy triggers:** `deploy-frontend-staging, deploy-backend-staging`
- **Repo state:** early product build (64 commits on `Development` as of 2026-09-18). Read the tree
  before assuming anything exists.

## Tracker & Design
- **Tracker:** `clickup`
- **Tracker Board ID:** `1100770000001008`
- **Tracker Board name:** List
- **Tracker MCP server:** `tracker-fms-studio` (tool `tracker-fms-studio__tracker_get_task`; writes go
  through VanPM's feature-breakdown scripts, never the MCP write tools)
- **Figma file:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding
- **Figma MCP server:** `figma-fms-studio` (tools `figma-fms-studio__get_figma_data`, `figma-fms-studio__download_figma_images`; uses only this project's Design key). **VanDev MUST use these tools to extract exact CSS, flexbox layouts, spacing, and download actual image assets during UI implementation. Do not approximate designs.**
- **GCP Environment:** Staging only. No production environment exists yet.
- **GCP Project ID:** `fms-studio-staging`
- **GCP Region:** `asia-southeast1`
- **SecretRefs:**
  - Tracker: `CLICKUP_API_TOKEN_FMSSTUDIO` (exact name in the OpenClaw secret vault; no fallback)
  - Design: `FIGMA_API_KEY_FMSSTUDIO` (env-kind vault entry; loaded only by the `figma-fms-studio` MCP server via `projects/_tools/figma_mcp.py`)
  - GCP Key Vault: `GCP_SA_KEY_FMSSTUDIO_STAGING` (exact name in the OpenClaw secret vault)
  - GCP Key JSON: `/home/openclaw/.openclaw/workspace/credentials/gcp/fms-studio.json`
  - Reach GCP only through `projects/_tools/gcloud_env.py fms-studio -- <command>`; there is no
    ambient gcloud default and `gcloud` run bare will not be pointed at this project.
  - GitHub Token: `GITHUB_TOKEN_FMSSTUDIO` (env-kind vault entry; fine-grained PAT scoped to
    `symphco/fms-studio` only: Contents + Pull requests read/write)
  - `git push` uses the SSH alias above. Everything that talks to the GitHub API (`gh pr create`,
    `gh pr view`, `gh run list`) goes through `projects/_tools/git_env.py fms-studio -- gh <args>`;
    bare `gh` has no login on this box and will fail.

## Workflow Rules
- **Statuses:** `to do`, `in progress`, `qa`, `rejected`, `on hold`, `complete`, `cancelled`
  - Meaning (2026-09-19): `in progress` = VanDev working (internal review + VanQA happen here) · `qa` = **merged and
    deployed to staging** (set by the delivery watcher after Cloud Build succeeds) · `rejected` = external QA sent it
    back (with a comment) · `complete` = external QA passed it. Agents never set `complete`.
- **GitHub bots:** `symphdevtools` (PR-description bot; its comments are not review feedback)
- **Create status:** `to do`
- **Branch Prefixes:** `feature/`, `bug/`
- **Install command:** `npm ci` (repo root, inside your own worktree; needed before any build or test).
- **Dev/QA Test Commands:** do **not** infer these - inferring them is what hung VanQA 28 times.
  Every line below was re-verified by running it on `Development` @ f5e20b5 on 2026-09-21.
  - Tests: `npx nx test <project>` (`frontend` or `backend`). Runs once and exits: `nx.json` now sets
    `testMode: "run"` and both vitest configs set `watch: false`.
  - **Verifying a fix (VanQA, and VanDev before saying done): `npx nx test <project> --skip-nx-cache`.**
    Without it Nx replays a previous result - including one computed in *another agent's worktree* - so a
    green line can mean nothing ran. If the output says `Cache: ... hit` or names a path that is not your
    worktree, you have verified nothing. Report the command you actually ran.
  - Test files DO exist (this said "none" until 2026-09-21 and was wrong): `backend/src/app/*.spec.ts`
    and `frontend/{specs/index.spec.tsx,src/app/page.test.tsx}`. Both suites: 2 passed, 2 passed.
  - Lint: `npx nx lint <project>` (from the `@nx/eslint` plugin).
  - E2E: none yet (Playwright/Cypress packages are installed, no config in the repo).
  - Forbidden: `npx nx test-ci <project>` - the target no longer exists ("Cannot find configuration for
    task <project>:test-ci"); it was the Nx Cloud atomized target and the `nx.json` fix removed it.
    Also any `vitest` without `run`.
  - `package.json` has no `scripts`, so there is nothing to infer from there.

## Flow
<!-- See projects/_template/PROJECT_CONTEXT.md for what each line means. -->
- **Profile:** `factory`
- **Stages:** `spec`, `tickets`, `review`, `internal-qa`, `merge-gate`, `delivery-watch`
- **Ticket source:** `agent`
- **Assignee filter:** `any`
- **Branch model:** `feature-branch`
- **PR base:** `Development`
- **Merge by:** `van`
- **Deploy signal:** `cloud-build`
- **Status map:** `todo=to do`, `doing=in progress`, `staged=qa`, `rejected=rejected`, `done=complete`, `cancelled=cancelled`, `hold=on hold`
- **Chat channel:** `discord:1547365802280362044`
- **PR conventions:** `none`

## Ticket conventions (enforced by the PM's `feature-breakdown` skill)
- One parent ticket per user-visible feature: `[Feature] <Area>: <Outcome>`.
- Subtasks per engineering lane, only the lanes the feature touches: `[FE]`, `[BE]`, `[DB]`, `[INT]`, `[QA]`, `[SPIKE]`. Each ≤ 8h.
- Every ticket body follows the template: Context · User story · In scope · Out of scope · Acceptance criteria (Given/When/Then, falsifiable) · Technical notes · Depends on/blocks · Test notes · Definition of done.
- Tags: `agent-created` + lane tag. Priority: urgent=1, high=2, normal=3, low=4. Estimates in `time_estimate`.
- Dependencies pushed as ClickUp task links. `[DB]` → `[BE]` → `[FE] wiring`; `[QA]` last.
- **Figma Designs:** If the Figma page is large or complex, VanPM must extract the component breakdown and include direct `?node-id=` links in the `[FE]` ticket and spec. For small/simple screens, the main design link is sufficient.
- Specs live in `artifacts/specs/<feature-slug>.md`; the push writes `<feature-slug>.clickup.json` next to it (completion marker; re-runs update instead of duplicate).

## Artifact Routing
- **Code (CWD):** `/home/openclaw/projects/fms-studio`
  Primary checkout, **read-only for agents** and kept on the Default branch. All code work
  happens in per-task worktrees under `/home/openclaw/projects/.worktrees/fms-studio/`, created and
  removed only by `projects/_tools/worktree.py fms-studio ...` (shared `worktree-lifecycle` skill).
  PR history: `prs.md` in Internal Artifacts (generated from `worktrees.jsonl`).
- **Internal Artifacts:** `/home/openclaw/.openclaw/workspace/projects/fms-studio/artifacts/` (`specs/`, `patches/`, `reviews/`, `qa/`)
