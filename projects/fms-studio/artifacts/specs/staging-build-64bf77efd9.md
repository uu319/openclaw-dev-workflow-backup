# Spec: Fix staging build lint failure (64bf77efd9)

Source: GCP Cloud Build e188f26a-f9da-47c6-abac-bcd256994e2d, 299dd5e4-14f5-4730-9166-fefdc71d3043

---ticket
title: [Feature] DevOps: Staging builds pass
lane: FEATURE
priority: high

## Context
Parent: this is the parent · Figma: none · Lane: FEATURE

## User story
As a developer, I want the staging deployment to succeed so that merged changes are deployed to the testing environment.

## In scope
- Fixing the `lint` target inference in Nx so `nx lint frontend` and `nx lint backend` succeed in Cloud Build.

## Out of scope (do NOT build)
- E2E tests
- Removing lint steps from Cloud Build (we want linting)

## Acceptance criteria
- Given the cloudbuild staging pipelines run, when they reach the lint step, then they pass the lint check and do not report missing configuration.
- Given a push to the Development branch, when the staging builds run, then they complete successfully.
- Given a local development checkout, when `npx nx lint frontend` and `npx nx lint backend` are run, then they execute cleanly.

## Technical notes
- The error is `Cannot find configuration for task frontend:lint`. This happens because Nx 23 infers targets from tooling config files (like `eslint.config.mjs` or `.eslintrc.json`), and these are missing from the `frontend/` and `backend/` directories, so `@nx/eslint/plugin` does not create the `lint` targets.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Push a test commit to Development and verify that Cloud Build succeeds and deploys.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [INT] Staging builds: add ESLint config to frontend
lane: INT
parent: [Feature] DevOps: Staging builds pass
estimate_hours: 2
parallel: true

## Context
Parent: [Feature] DevOps: Staging builds pass · Figma: none · Lane: INT

## User story
As a developer, I want the frontend to have a valid ESLint configuration so that the Cloud Build lint step succeeds.

## In scope
- Adding `eslint.config.mjs` or `.eslintrc.json` for the `frontend` project.
- Fixing any immediate lint errors in `frontend` that prevent the build from passing.

## Out of scope (do NOT build)
- Backend ESLint configuration

## Acceptance criteria
- Given the `frontend` project, when `npx nx lint frontend` is run, then it executes successfully and exits with status 0.
- Given the frontend codebase, when lint rules are applied, then they adhere to the standard Next.js / Nx React linting defaults.
- Given the Cloud Build staging pipeline for frontend runs, when it executes the lint step, then it passes.

## Technical notes
- Missing `eslint.config.mjs` prevents `@nx/eslint/plugin` from inferring the `lint` target.
- Breakpoints: none
- Mock or fixture for parallel work: none

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run `npx nx lint frontend` locally and confirm it works.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/frontend-eslint` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [INT] Staging builds: add ESLint config to backend
lane: INT
parent: [Feature] DevOps: Staging builds pass
estimate_hours: 2
parallel: true

## Context
Parent: [Feature] DevOps: Staging builds pass · Figma: none · Lane: INT

## User story
As a developer, I want the backend to have a valid ESLint configuration so that the Cloud Build lint step succeeds.

## In scope
- Adding `eslint.config.mjs` or `.eslintrc.json` for the `backend` project.
- Fixing any immediate lint errors in `backend` that prevent the build from passing.

## Out of scope (do NOT build)
- Frontend ESLint configuration

## Acceptance criteria
- Given the `backend` project, when `npx nx lint backend` is run, then it executes successfully and exits with status 0.
- Given the backend codebase, when lint rules are applied, then they adhere to the standard NestJS / Nx linting defaults.
- Given the Cloud Build staging pipeline for backend runs, when it executes the lint step, then it passes.

## Technical notes
- Missing `eslint.config.mjs` prevents `@nx/eslint/plugin` from inferring the `lint` target.
- Breakpoints: none
- Mock or fixture for parallel work: none

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run `npx nx lint backend` locally and confirm it works.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test backend`)
- [ ] Lint and typecheck clean (`npx nx lint backend`, `npx tsc -p backend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/backend-eslint` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Staging builds: verify deployment
lane: QA
parent: [Feature] DevOps: Staging builds pass
estimate_hours: 1
depends_on: [INT] Staging builds: add ESLint config to frontend, [INT] Staging builds: add ESLint config to backend

## Context
Parent: [Feature] DevOps: Staging builds pass · Figma: none · Lane: QA

## User story
As a QA engineer, I want to verify that the staging builds complete successfully and deploy.

## In scope
- Verifying the Cloud Build pipelines for staging on the Development branch.

## Out of scope (do NOT build)
- Fixing the lint errors

## Acceptance criteria
- Given the `[INT]` frontend and `[INT]` backend fixes are merged to Development, when the staging pipelines are triggered, then they complete successfully without `nx lint` task missing errors.
- Given the deployed environment, when accessed, then the application is reachable.
- Given the Cloud Build logs, when inspected, then the `npx nx lint` step has exited with 0.

## Technical notes
- None

## Depends on / blocks
- Depends on: [INT] Staging builds: add ESLint config to frontend, [INT] Staging builds: add ESLint config to backend
- Blocks: none

## Test notes (how QA verifies)
- Review the Cloud Build logs for the latest run on the `Development` branch for both frontend and backend.
- Confirm they are marked green (Successful).

## Definition of done
- [ ] All acceptance criteria pass
---end