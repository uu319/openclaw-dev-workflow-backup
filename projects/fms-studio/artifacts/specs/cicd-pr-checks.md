# Spec: CI/CD Pipeline PR Checks

---ticket
title: [Feature] CI/CD: Cloud Build PR checks
lane: FEATURE
priority: normal
existing_id: z94kydawa8

## Context
Parent: this is the parent · Lane: FEATURE

## User story
As a developer, I want the CI/CD pipeline to catch broken assets and failed builds before code is merged into the default branch, so that staging and production remain stable.

## In scope
- Cloud Build configuration for PR checks
- E2E tests running in the pipeline against a production-like build
- Explicit pipeline failures on missing assets (404s)

## Out of scope (do NOT build)
- Full E2E test suites for all user features (only the baseline network check is needed now)
- Deployment steps in the PR pipeline (PRs only test, they don't deploy)

## Acceptance criteria
- Given a PR is opened against the `Development` branch, when the Cloud Build PR check runs, then it builds and tests the Next.js `standalone` artifact.
- Given a page requests a broken image or missing asset (404), when the E2E test runs, then the test fails explicitly and halts the pipeline.
- Given the CI pipeline, when it runs, then it executes `npm ci`, linting, unit tests, and the E2E tests.

## Technical notes
- Use Playwright for the baseline E2E network test.
- The pipeline must serve the Next.js `standalone` build for tests, rather than a dev server.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Introduce a broken image in a branch and verify the PR check fails.

## Definition of done
- [ ] All subtasks COMPLETE and the CI/CD pipeline triggers correctly on PRs
---end

---ticket
title: [INT] PR Checks: Create Cloud Build configuration
lane: INT
parent: [Feature] CI/CD: Cloud Build PR checks
priority: normal
estimate_hours: 4
existing_id: z94kydawaa

## Context
Parent: [Feature] CI/CD: Cloud Build PR checks · Lane: INT

## User story
As a developer, I want a Cloud Build PR trigger to run validation checks before merging to Development, so that we prevent regressions.

## In scope
- Cloud Build yaml for PRs
- Running tests, linting, and the new Playwright E2E test

## Out of scope (do NOT build)
- Deployment from this trigger

## Acceptance criteria
- Given a pull request is opened, when it updates, then Cloud Build runs the CI pipeline.
- Given the CI pipeline, when it runs, then it executes `npm ci`, linting, unit tests, and Playwright tests.
- Given the pipeline completes, when successful, then the GitHub PR check status is marked as green.

## Technical notes
- Expected file: `cloudbuild-pr.yaml`.

## Depends on / blocks
- Depends on: [INT] Test Production Artifact Locally, [QA] Configure Playwright E2E Tests
- Blocks: none

## Test notes (how QA verifies)
- Open a PR and ensure the Cloud Build check is triggered and visible in GitHub.

## Definition of done
- [ ] Trigger yaml committed
- [ ] PR checks successfully run on new PRs
---end

---ticket
title: [QA] Configure Playwright E2E Tests
lane: QA
parent: [Feature] CI/CD: Cloud Build PR checks
priority: normal
estimate_hours: 4

## Context
Parent: [Feature] CI/CD: Cloud Build PR checks · Lane: QA

## User story
As a developer, I want an E2E test that fails on any 404 network request, so that broken images and assets are caught before merging.

## In scope
- Playwright configuration and baseline test setup
- E2E test script to load the root application page
- Interception of network requests to assert no 404s (specifically for assets/images)

## Out of scope (do NOT build)
- Cypress setup (we use Playwright)
- Tests for business logic and workflows

## Acceptance criteria
- Given the application is running, when the Playwright test navigates to the root, then it listens to all network requests.
- Given a network request returns a 404 status code, when it occurs during the test, then the test fails immediately.
- Given all network requests return 200 or 3xx, when the test finishes, then the test passes.

## Technical notes
- Use Playwright's `page.on('response', ...)` to catch 404s and explicitly fail the test runner.

## Depends on / blocks
- Depends on: none
- Blocks: [INT] PR Checks: Create Cloud Build configuration

## Test notes (how QA verifies)
- Introduce a broken image `<img>` tag in a local branch and verify `npx playwright test` fails.

## Definition of done
- [ ] Playwright configured in the Nx workspace
- [ ] Network 404 test passing on clean `Development` branch
- [ ] Test fails locally when a 404 is intentionally introduced
---end

---ticket
title: [INT] Test Production Artifact Locally
lane: INT
parent: [Feature] CI/CD: Cloud Build PR checks
priority: normal
estimate_hours: 5

## Context
Parent: [Feature] CI/CD: Cloud Build PR checks · Lane: INT

## User story
As a developer, I want to build and test the actual Next.js `standalone` artifact in the pipeline, so that the tested app is identical to what runs in App Engine.

## In scope
- Updating Next.js config to `output: 'standalone'`
- Creating a script or Nx configuration to serve the standalone artifact locally for the E2E test

## Out of scope (do NOT build)
- App Engine deployment changes (this is for PR checks only)

## Acceptance criteria
- Given the CI/CD pipeline runs, when it prepares to test the application, then it builds the standalone Next.js artifact instead of running the dev server.
- Given the artifact is built, when the E2E tests start, then they run against the standalone production build.
- Given the E2E tests complete, when the process exits, then the standalone node server stops.

## Technical notes
- The App Engine environment uses the build output. This ensures PRs test the same compiled bundle.
- Ensure the Nx `e2e` target or testing script knows how to start the standalone node server.

## Depends on / blocks
- Depends on: none
- Blocks: [INT] PR Checks: Create Cloud Build configuration

## Test notes (how QA verifies)
- Verify Cloud Build or local CI logs show the standalone Node server starting, not the Next.js dev server, when Playwright runs.

## Definition of done
- [ ] Next.js configured for standalone output
- [ ] CI testing script updated to start the production artifact for E2E tests
---end
