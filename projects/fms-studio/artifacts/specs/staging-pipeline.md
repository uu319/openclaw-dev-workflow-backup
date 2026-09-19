# Spec: Staging deployment pipeline to GCP App Engine

---ticket
title: [Feature] CI/CD: Staging deployment pipeline to GCP App Engine
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=0-1
screenshots: specs/_figma/staging-pipeline/dummy.png

## Context
Parent: this is the parent · Figma: none · Lane: FEATURE

## User story
As an engineer, I want the `Development` branch to deploy automatically to a staging environment on GCP App Engine, so that QA and stakeholders can test changes before production.

## In scope
- GCP App Engine setup for staging (Next.js frontend, NestJS backend)
- Cloud Build triggers connected to GitHub
- Build scripts and `app.yaml` configuration for both apps in the Nx monorepo
- `dispatch.yaml` to route `/api/*` traffic to the backend service

## Out of scope (do NOT build)
- Production environment setup
- Database provisioning (no DB yet)
- Complex scaling rules (default scaling is fine)
- Custom domain setup

## Acceptance criteria
- Given a push or merge to the `Development` branch, when Cloud Build triggers, then it successfully builds the Next.js and NestJS apps using Nx.
- Given a successful build, when the deployment step runs, then both apps are deployed to their respective App Engine services (e.g., `default` for frontend, `api` for backend).
- Given the apps are deployed, when visiting the App Engine staging URLs, then both apps respond with 200 OK.

## Technical notes
- Endpoint / schema: N/A
- Mock or fixture for parallel work: N/A
- Breakpoints (FE only): N/A

## Depends on / blocks
- Depends on: none
- Blocks: QA testing of actual features

## Test notes (how QA verifies)
- Push a harmless change to the `Development` branch and observe the build in GCP Cloud Build. Verify the changes are reflected on the staging URLs.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [INT] CI/CD: Add app.yaml and build configs for Nx apps
lane: INT
parent: [Feature] CI/CD: Staging deployment pipeline to GCP App Engine
priority: high
estimate_hours: 4

## Context
Parent: [Feature] CI/CD: Staging deployment pipeline to GCP App Engine · Figma: none · Lane: INT

## User story
As a developer, I want the correct `app.yaml` and Nx build targets defined, so that App Engine knows how to serve the frontend and backend.

## In scope
- `app.yaml` for Next.js frontend (e.g., service `default`)
- `app.yaml` for NestJS backend (e.g., service `api`)
- `dispatch.yaml` to route requests appropriately
- Updating `project.json` or `package.json` with scripts that prepare the dist folders for App Engine

## Out of scope (do NOT build)
- Actual Cloud Build trigger creation (handled in another ticket)
- Database configurations

## Acceptance criteria
- Given the Nx monorepo, when running the prepare script for the frontend, then a deployable directory is created with `app.yaml` and Next.js standalone output.
- Given the Nx monorepo, when running the prepare script for the backend, then a deployable directory is created with `app.yaml` and the NestJS compiled output.
- Given the `app.yaml` files, when inspected, then they specify a valid Node.js runtime (e.g., `nodejs20`) for App Engine Standard.
- Given `dispatch.yaml`, when deployed, then it routes `/api/*` to the `api` service and `/*` to the `default` service.

## Technical notes
- Endpoint / schema: N/A
- Mock or fixture for parallel work: N/A
- Breakpoints (FE only): N/A
- Next.js needs `output: 'standalone'` in `next.config.js`.

## Depends on / blocks
- Depends on: none
- Blocks: [INT] CI/CD: Configure Cloud Build pipeline for GitHub

## Test notes (how QA verifies)
- Review the generated `app.yaml` and build artifacts locally.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test fms-studio`)
- [ ] Lint and typecheck clean (`npx nx lint fms-studio`, `npx tsc -p fms-studio/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/staging-deployment` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [INT] CI/CD: Configure Cloud Build pipeline for GitHub
lane: INT
parent: [Feature] CI/CD: Staging deployment pipeline to GCP App Engine
priority: high
estimate_hours: 4
depends_on: [INT] CI/CD: Add app.yaml and build configs for Nx apps

## Context
Parent: [Feature] CI/CD: Staging deployment pipeline to GCP App Engine · Figma: none · Lane: INT

## User story
As an engineer, I want a `cloudbuild.yaml` and GCP trigger setup, so that pushing to `Development` automatically builds and deploys the apps.

## In scope
- `cloudbuild.yaml` file in the repository root
- Steps for installing dependencies, running Nx build, and deploying via `gcloud app deploy` (including `dispatch.yaml`)
- Documentation for setting up the Cloud Build trigger in GCP connected to the GitHub repo

## Out of scope (do NOT build)
- E2E test execution inside the CI pipeline (for now, just build and deploy)

## Acceptance criteria
- Given a `cloudbuild.yaml`, when executed, then it runs `npm ci`, builds both apps, and runs `gcloud app deploy` for both services and `dispatch.yaml`.
- Given the GCP project, when a commit is pushed to `Development`, then the Cloud Build trigger automatically starts the build defined in `cloudbuild.yaml`.
- Given the deployment step, when it runs, then it uses the correct service account with App Engine Admin permissions.

## Technical notes
- Endpoint / schema: N/A
- Mock or fixture for parallel work: N/A
- Breakpoints (FE only): N/A

## Depends on / blocks
- Depends on: [INT] CI/CD: Add app.yaml and build configs for Nx apps
- Blocks: [QA] CI/CD: E2E staging deployment verification

## Test notes (how QA verifies)
- Push a test commit to `Development` and check the Cloud Build logs in GCP.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test fms-studio`)
- [ ] Lint and typecheck clean (`npx nx lint fms-studio`, `npx tsc -p fms-studio/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/staging-deployment` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] CI/CD: E2E staging deployment verification
lane: QA
parent: [Feature] CI/CD: Staging deployment pipeline to GCP App Engine
priority: high
estimate_hours: 2
depends_on: [INT] CI/CD: Configure Cloud Build pipeline for GitHub

## Context
Parent: [Feature] CI/CD: Staging deployment pipeline to GCP App Engine · Figma: none · Lane: QA

## User story
As a QA engineer, I want to verify that the staging deployment works end-to-end, so that we can rely on it for testing future features.

## In scope
- End-to-end testing of the CI/CD pipeline
- Verification of live staging URLs

## Out of scope (do NOT build)
- Writing automated E2E tests (just manual verification for this infrastructure task)

## Acceptance criteria
- Given a new commit pushed to the `Development` branch, when the Cloud Build pipeline finishes, then the frontend is accessible on the `default` service staging URL.
- Given the same deployment, when the pipeline finishes, then the backend is accessible on the `api` service staging URL (e.g., returning 200 on a healthcheck or root endpoint).
- Given both apps are live, when tested, then the frontend can communicate with the backend staging URL.

## Technical notes
- Endpoint / schema: N/A
- Mock or fixture for parallel work: N/A
- Breakpoints (FE only): N/A

## Depends on / blocks
- Depends on: [INT] CI/CD: Configure Cloud Build pipeline for GitHub
- Blocks: none

## Test notes (how QA verifies)
- Trigger the pipeline, monitor logs, and manually verify the deployed URLs.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test fms-studio`)
- [ ] Lint and typecheck clean (`npx nx lint fms-studio`, `npx tsc -p fms-studio/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/staging-deployment` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end
