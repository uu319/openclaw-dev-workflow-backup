# Spec: GitHub Actions PR checks

---ticket
title: [Feature] CI/CD: GitHub Actions PR checks
lane: FEATURE
priority: high

## Context
Parent: this is the parent · Lane: FEATURE

## User story
As a developer, I want pull requests to run lint typecheck and build checks automatically, so that errors are caught before merging instead of breaking Cloud Build later.

## In scope
- GitHub Actions workflow triggering on pull requests to the `Development` branch.
- Caching for `node_modules`.
- Commands: `npm ci`, `npx nx run-many -t lint`, `npx tsc -p frontend/tsconfig.json --noEmit`, `npx tsc -p backend/tsconfig.json --noEmit`, `npx nx run-many -t build`.

## Out of scope (do NOT build)
- Touching the Cloud Build pipeline or `.cloudbuild/` configs.
- Adding any test jobs.

## Acceptance criteria
- Given a pull request targeting `Development`, when it is opened or updated, then the GitHub Actions workflow triggers automatically.
- Given the workflow runs, when it reaches the check steps, then it executes `npm ci`, `npx nx run-many -t lint`, `npx tsc -p frontend/tsconfig.json --noEmit`, `npx tsc -p backend/tsconfig.json --noEmit` and `npx nx run-many -t build`.
- Given the workflow runs on subsequent commits, when the cache is hit, then `node_modules` is restored from the cache to speed up the run.

## Technical notes
- Files/paths: `.github/workflows/pr-checks.yml`

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [INT] PR Checks: Create GitHub Actions workflow
lane: INT
parent: [Feature] CI/CD: GitHub Actions PR checks
priority: high
estimate_hours: 4

## Context
Parent: [Feature] CI/CD: GitHub Actions PR checks · Lane: INT

## User story
As a developer, I want a GitHub Actions YAML file that runs all required checks, so that the PR process enforces quality automatically.

## In scope
- Creating `.github/workflows/pr-checks.yml`.
- Configuring triggers for PRs against `Development`.
- Adding actions/checkout, actions/setup-node, and cache setup.
- Adding run steps for install, lint, typecheck and build.

## Out of scope (do NOT build)
- Test steps.
- Modifying Cloud Build pipelines.

## Acceptance criteria
- Given the PR workflow file, when committed, then it defines an `on: pull_request` trigger for the `Development` branch.
- Given the workflow steps, when it executes, then it runs `npx nx run-many -t lint` successfully across the workspace.
- Given the workflow steps, when it executes, then it runs `npx tsc -p frontend/tsconfig.json --noEmit` and `npx tsc -p backend/tsconfig.json --noEmit`.
- Given the workflow steps, when it executes, then it runs `npx nx run-many -t build` successfully.

## Technical notes
- Setup Node action must use Node 24. This matches the Cloud Build builder (see `.cloudbuild/cloudbuild-frontend-staging.yaml` and `-backend-staging.yaml`). CI must build on Node 24 to match the builder; otherwise, on Node 22 a PR could pass while Cloud Build fails.

## Depends on / blocks
- Depends on: none
- Blocks: [QA] PR Checks: Verify workflow triggers and passes

## Test notes (how QA verifies)
- N/A

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR from `feature/pr-checks` reviewed
- [ ] Status moved to the board's `staged` status once the change is on staging (the delivery
      watcher tells VanPM; nobody sets it by hand)
---end

---ticket
title: [QA] PR Checks: Verify workflow triggers and passes
lane: QA
parent: [Feature] CI/CD: GitHub Actions PR checks
estimate_hours: 2
depends_on: [INT] PR Checks: Create GitHub Actions workflow

## Context
Parent: [Feature] CI/CD: GitHub Actions PR checks · Lane: QA

## User story
As an orchestrator, I want to ensure the PR checks actually run and block or pass PRs correctly, so that broken code does not get merged.

## In scope
- Verifying the GitHub Actions workflow in a live PR.

## Out of scope (do NOT build)
- Writing code or fixing the pipeline.

## Acceptance criteria
- Given a test PR opened against `Development`, when viewed in GitHub, then the PR checks workflow is triggered and visible in the Checks tab.
- Given the running workflow, when it completes without code errors, then it reports a green success status for lint, typecheck, and build steps.
- Given a second commit pushed to the same PR, when the workflow runs again, then the setup step shows that `node_modules` was restored from cache.

## Technical notes
- Needs an active PR to test. A draft PR is sufficient for QA.

## Depends on / blocks
- Depends on: [INT] PR Checks: Create GitHub Actions workflow
- Blocks: none

## Test notes (how QA verifies)
- Follow ACs manually in GitHub.

## Definition of done
- [ ] All acceptance criteria pass
---end
