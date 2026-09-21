# Spec: Cloud Build PR checks

---ticket
title: [Feature] CI/CD: Cloud Build PR checks
lane: FEATURE
priority: high

## Context
Parent: this is the parent · Lane: FEATURE

## User story
As a developer, I want pull requests to run lint typecheck and build checks automatically, so that errors are caught before merging instead of breaking Cloud Build later.

## In scope
- Cloud Build trigger config for pull requests to the `Development` branch using the `node:24` image.
- Commands: `npm ci`, `npx nx run-many -t lint`, `npx tsc -p frontend/tsconfig.json --noEmit`, `npx tsc -p backend/tsconfig.json --noEmit`, `npx nx run-many -t build`.
- Adding a clear note that creating the Cloud Build TRIGGER is a manual step for Van in the GCP console (a pull-request trigger on symphco/fms-studio pointing at the new yaml).

## Out of scope (do NOT build)
- Touching existing `.cloudbuild/` configs.
- Adding any test jobs.

## Acceptance criteria
- Given a pull request targeting `Development`, when it is opened or updated, then the Cloud Build trigger runs automatically.
- Given the workflow runs, when it reaches the check steps, then it executes `npm ci`, `npx nx run-many -t lint`, `npx tsc -p frontend/tsconfig.json --noEmit`, `npx tsc -p backend/tsconfig.json --noEmit` and `npx nx run-many -t build`.
- Given a failing check (e.g. lint or build fails), when the workflow finishes, then the PR is blocked from merging.

## Technical notes
- Files/paths: `.cloudbuild/cloudbuild-pr-checks.yaml`
- Use the `node:24` image for the steps.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [INT] PR Checks: Create Cloud Build configuration
lane: INT
parent: [Feature] CI/CD: Cloud Build PR checks
priority: high
estimate_hours: 4

## Context
Parent: [Feature] CI/CD: Cloud Build PR checks · Lane: INT

## User story
As a developer, I want a Cloud Build YAML file that runs all required checks, so that the PR process enforces quality automatically.

## In scope
- Creating `.cloudbuild/cloudbuild-pr-checks.yaml`.
- Adding run steps for install, lint, typecheck and build using the `node:24` image.

## Out of scope (do NOT build)
- Test steps.
- Modifying existing Cloud Build pipelines.

## Acceptance criteria
- Given the Cloud Build file, when committed, then it defines steps that use the `node:24` image.
- Given the workflow steps, when it executes, then it runs `npx nx run-many -t lint` successfully across the workspace.
- Given the workflow steps, when it executes, then it runs `npx tsc -p frontend/tsconfig.json --noEmit` and `npx tsc -p backend/tsconfig.json --noEmit`.
- Given the workflow steps, when it executes, then it runs `npx nx run-many -t build` successfully.

## Technical notes
- The step image must be `node:24`. This matches the Cloud Build builder (see `.cloudbuild/cloudbuild-frontend-staging.yaml` and `-backend-staging.yaml`).
- Creating the Cloud Build TRIGGER is a manual step for Van in the GCP console (a pull-request trigger on symphco/fms-studio pointing at the new yaml).

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
parent: [Feature] CI/CD: Cloud Build PR checks
estimate_hours: 2
depends_on: [INT] PR Checks: Create Cloud Build configuration

## Context
Parent: [Feature] CI/CD: Cloud Build PR checks · Lane: QA

## User story
As an orchestrator, I want to ensure the PR checks actually run and block or pass PRs correctly, so that broken code does not get merged.

## In scope
- Verifying the Cloud Build workflow in a live PR.

## Out of scope (do NOT build)
- Writing code or fixing the pipeline.

## Acceptance criteria
- Given a test PR opened against `Development`, when viewed in GitHub, then the PR checks workflow is triggered and visible in the Checks tab.
- Given the running workflow, when it completes without code errors, then it reports a green success status for lint, typecheck, and build steps.
- Given a test PR with a deliberate lint or build failure, when the workflow runs, then the check fails and blocks the PR.

## Technical notes
- Needs an active PR to test. A draft PR is sufficient for QA.

## Depends on / blocks
- Depends on: [INT] PR Checks: Create Cloud Build configuration
- Blocks: none

## Test notes (how QA verifies)
- Follow ACs manually in GitHub.

## Definition of done
- [ ] All acceptance criteria pass
---end
