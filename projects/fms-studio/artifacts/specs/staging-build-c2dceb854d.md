---ticket
lane: FEATURE
title: "[Feature] DevOps: Fix backend staging deploy failure (content-type missing)"
tags: ["agent-created"]
priority: high
---
# [Feature] DevOps: Fix backend staging deploy failure (content-type missing)

## Context
The `deploy-backend-staging` Cloud Build failed on App Engine deployment for commit c2dceb854d. The buildpack fails with `npm error \`npm ci\` can only install packages when your package.json and package-lock.json or npm-shrinkwrap.json are in sync. Missing: content-type@1.0.5 from lock file`.

## User story
As a developer, I want the backend App Engine deployment to succeed so that the latest features are available on staging.

## In scope
- Fixing the `backend` deployment configuration to ensure App Engine correctly resolves and installs dependencies without lockfile errors.

## Out of scope
- Modifying frontend deployment or other non-deployment CI steps.

## Acceptance criteria
- Given a trigger of the `deploy-backend-staging` workflow, When the App Engine deployment step executes, Then the `npm ci` or `npm install` process completes successfully.
- Given the deployment succeeds, When the staging endpoint is queried, Then the backend is responsive and functioning properly.
- Given a successful deployment, When reviewing the GCP Cloud Build logs, Then no lockfile synchronisation errors (`npm ci` can only install packages when your package.json and package-lock.json...) are present.

## Technical notes
- The App Engine deployment is initiated by `gcloud app deploy` inside the `dist/backend/` directory.
- `deploy-prepare` for `backend` currently runs `mkdir -p dist/backend && cp backend/app.yaml dist/backend/app.yaml && cp backend/package.json dist/backend/package.json`.
- A missing or out-of-sync lockfile causes `npm ci` in App Engine to fail. We may need to use Nx's `generatePackageJson` feature correctly or explicitly generate/copy a lockfile.

## Depends on/blocks
- Blocks all staging verification for backend changes.

## Test notes
- Push to a PR to trigger the CI or check the deployment logs once merged to `Development`.

## Definition of done
- The `deploy-backend-staging` Cloud Build finishes successfully.
---end

---ticket
lane: BE
parent: "[Feature] DevOps: Fix backend staging deploy failure (content-type missing)"
title: "[BE] Fix package-lock.json for App Engine deployment"
tags: ["agent-created", "BE"]
estimate_hours: 4
---
# [BE] Fix package-lock.json for App Engine deployment

## Context
The backend deployment fails because App Engine encounters a lockfile synchronization error when running `npm ci` on the `package.json` copied to `dist/backend`.

## User story
As a developer, I need the build output to contain a valid lockfile or configuration so App Engine deploys successfully.

## In scope
- Update the `backend` build or `deploy-prepare` configuration to provide a synchronized lockfile or configure the buildpack to run `npm install`.

## Out of scope
- Changes to the frontend deployment.

## Acceptance criteria
- Given the `backend:deploy-prepare` task is executed, When the `dist/backend` output is inspected, Then it either contains a valid `package-lock.json` that matches the `package.json`, or the deployment is configured to not fail on lockfile sync.
- Given a test deployment workflow, When triggered, Then the App Engine build succeeds.
- Given the fix is in place, When merging subsequent backend updates, Then deployments will continue without lockfile errors.

## Technical notes
- Consider leveraging Nx's capabilities for deploying Node.js applications, which can generate a pruned `package.json` and `package-lock.json` for the build output.
- `content-type@1.0.5` was noted as missing from the lock file.

## Depends on/blocks
- None

## Test notes
- Can be tested locally by running the build and `deploy-prepare`, then attempting `npm ci` in `dist/backend`.

## Definition of done
- The fix is merged and staging deploys successfully.
---end