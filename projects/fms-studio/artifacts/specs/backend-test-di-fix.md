# Spec: Fix backend unit test DI failure

---ticket
title: [Feature] DevOps: Fix backend unit test DI failure
lane: FEATURE
priority: normal

## Context
The backend unit tests are failing on the Development branch (`npx nx test backend`).
The `app.controller.spec.ts` test fails with `TypeError: Cannot read properties of undefined (reading 'getData')`.
This indicates that `appService` is not being properly injected into the controller during the test.

## User story
As a developer, I want the backend unit tests to pass so that I can rely on CI and local test runs to verify changes.

## In scope
- Fix `app.controller.spec.ts` dependency injection setup so that `AppService` is provided to `AppController`.

## Out of scope (do NOT build)
- Changing production runtime behavior.
- Adding new tests.

## Acceptance criteria
- Given the backend unit tests are executed, when running `npx nx test backend`, then `app.controller.spec.ts` executes without a TypeError.
- Given the backend unit tests are executed, when running `npx nx test backend`, then `app.service.spec.ts` continues to pass.
- Given the test setup, when `app.controller.spec.ts` runs, then `appController.getData()` returns the value provided by `AppService`.

## Technical notes
- Ensure `AppService` is included in the `providers` array of the `TestingModule` in `app.controller.spec.ts`.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run `npx vitest run` inside the `backend` folder locally, or `npx nx test backend` (as mentioned in the request, though PROJECT_CONTEXT notes vitest test-ci is being fixed).

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [BE] Fix DI in app.controller.spec.ts
lane: BE
parent: [Feature] DevOps: Fix backend unit test DI failure
priority: normal
estimate_hours: 1

## Context
`app.controller.spec.ts` fails to inject `AppService`.

## User story
As a developer, I need the DI configured properly in the test so that it runs successfully.

## In scope
- Update `app.controller.spec.ts` testing module setup.

## Out of scope (do NOT build)
- Application runtime changes.
- Changes to other tests.

## Acceptance criteria
- Given the test setup in `app.controller.spec.ts`, when the module compiles, then `AppService` is injected into `AppController`.
- Given the test execution, when `getData()` is called on the controller, then it delegates to `AppService` without a TypeError.
- Given the test execution, when `getData()` returns, then it matches the expected mock or instance output of `AppService`.

## Technical notes
- Edit `backend/src/app/app.controller.spec.ts`.
- Add `AppService` to the `providers` array of `Test.createTestingModule`.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
Run tests with `npx vitest run` in the backend folder.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR reviewed
---end

---ticket
title: [QA] Verify backend unit tests pass
lane: QA
parent: [Feature] DevOps: Fix backend unit test DI failure
estimate_hours: 1
depends_on: [BE] Fix DI in app.controller.spec.ts

## Context
Ensure the backend tests pass.

## User story
As QA, I verify the unit tests run green.

## In scope
- Run unit tests for backend.

## Out of scope (do NOT build)
- Writing new tests.

## Acceptance criteria
- Given the fix is merged to the test branch, when running the backend test command, then 0 tests fail.
- Given the test output, when the run completes, then `app.controller.spec.ts` is reported as passing.
- Given the test output, when the run completes, then `app.service.spec.ts` is reported as passing.

## Technical notes
- None

## Depends on / blocks
- Depends on: [BE] Fix DI in app.controller.spec.ts
- Blocks: none

## Test notes (how QA verifies)
Run tests locally.

## Definition of done
- [ ] Tests verified passing.
---end
