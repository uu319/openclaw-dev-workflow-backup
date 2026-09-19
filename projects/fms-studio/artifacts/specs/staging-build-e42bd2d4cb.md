# Spec: Fix staging build failure (e42bd2d4cb)

Source: GCP Cloud Build a152f336-53cd-4c64-8e77-c87805730e10. Written 2026-09-19 by VanPM.

---ticket
title: [Feature] DevOps: Fix staging build failure (lockfile sync)
lane: FEATURE
priority: urgent

## Context
Parent: this is the parent · Figma: none · Lane: FEATURE

## User story
As a developer, I want the staging deployment to succeed so that merged changes are deployed to the testing environment.

## In scope
- Fixing the `npm ci` step failure during App Engine deployment in the Cloud Build pipeline.
- Updating `package-lock.json` so it is in sync with `package.json`.

## Out of scope (do NOT build)
- E2E tests
- Upgrading unrelated dependencies

## Acceptance criteria
- Given the cloudbuild staging pipelines run, when they reach the App Engine deployment step, then they pass the `npm ci` check and deploy successfully.
- Given a push to the Development branch, when the staging builds run, then they complete successfully.
- Given a local checkout, when `npm ci` is run, then it executes cleanly without lockfile mismatch errors.

## Technical notes
- The error is: `` `npm ci` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Please update your lock file with `npm install` before continuing. Missing: content-type@1.0.5 from lock file ``
- Fix by running `npm install` locally to update the lock file and committing the change.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Push the updated `package-lock.json` to the Development branch and verify that Cloud Build succeeds and the app deploys successfully.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [INT] Staging builds: update package-lock.json
lane: INT
parent: [Feature] DevOps: Fix staging build failure (lockfile sync)
priority: urgent
estimate_hours: 1
parallel: true

## Context
Parent: [Feature] DevOps: Fix staging build failure (lockfile sync) · Figma: none · Lane: INT

## User story
As a developer, I want the lockfile to be updated so that the Cloud Build deploy step succeeds.

## In scope
- Running `npm install` to update `package-lock.json` with the missing `content-type@1.0.5` dependency.

## Out of scope (do NOT build)
- Updating unrelated dependencies

## Acceptance criteria
- Given the repository root, when `npm ci` is run, then it executes successfully and exits with status 0.
- Given the lockfile, when inspected, then it contains the resolution for `content-type@1.0.5` in sync with `package.json`.
- Given the Cloud Build staging pipeline runs, when it executes the deployment step, then it passes without lockfile errors.

## Technical notes
- Missing `content-type@1.0.5` from `package-lock.json`.
- Run `npm install` to sync `package-lock.json` with `package.json`.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run `npm ci` locally and confirm it works without lockfile sync errors.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR opened from `bug/update-lockfile` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Staging builds: verify deployment after lockfile sync
lane: QA
parent: [Feature] DevOps: Fix staging build failure (lockfile sync)
priority: urgent
estimate_hours: 1
depends_on: [INT] Staging builds: update package-lock.json

## Context
Parent: [Feature] DevOps: Fix staging build failure (lockfile sync) · Figma: none · Lane: QA

## User story
As a QA engineer, I want to verify that the staging builds complete successfully and deploy.

## In scope
- Verifying the Cloud Build pipelines for staging on the Development branch.

## Out of scope (do NOT build)
- Fixing the lockfile errors

## Acceptance criteria
- Given the `[INT]` lockfile fix is merged to Development, when the staging pipelines are triggered, then they complete successfully without `npm ci` errors.
- Given the deployed environment, when accessed, then the application is reachable.
- Given the Cloud Build logs, when inspected, then the deployment step has exited with 0.

## Technical notes
- None

## Depends on / blocks
- Depends on: [INT] Staging builds: update package-lock.json
- Blocks: none

## Test notes (how QA verifies)
- Review the Cloud Build logs for the latest run on the `Development` branch for backend.
- Confirm they are marked green (Successful).

## Definition of done
- [ ] All acceptance criteria pass
---end