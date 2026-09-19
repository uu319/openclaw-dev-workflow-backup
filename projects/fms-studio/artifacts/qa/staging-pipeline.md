# QA: Staging deployment pipeline to GCP App Engine

## Criteria

- **FAIL**: Given a push or merge to the `Development` branch, when Cloud Build triggers, then it successfully builds the Next.js and NestJS apps using Nx. (Build failed after PR #4 merge)
- **FAIL**: Given a successful build, when the deployment step runs, then both apps are deployed to their respective App Engine services.
- **FAIL**: Given the apps are deployed, when visiting the App Engine staging URLs, then both apps respond with 200 OK.

## Defects

### Defect: Cloud Build pipeline failure
- **Steps to reproduce:**
  1. Trigger a push/merge to the `Development` branch (specifically, merging PR #4 `fix/deployment-404`).
  2. Wait for the Cloud Build pipeline to execute.
- **Expected result:** The Cloud Build pipeline successfully builds and deploys both the frontend and backend applications to App Engine.
- **Observed result:** The Cloud Build pipeline failed during execution. (Earlier deployments resulted in continuous HTTP 500 errors on both staging URLs).
- **Evidence:** Confirmed build failure after merge of PR #4 into `Development` branch. Troubleshooting is being handled outside of this QA run.
