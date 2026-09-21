APPROVED
Reviewed SHA: 51339776db2dfc07a180295bff691b89e66fc9d5
- Given the test setup in `app.controller.spec.ts`, when the module compiles, then `AppService` is injected into `AppController`: backend/src/app/app.controller.spec.ts:8
- Given the test execution, when `getData()` is called on the controller, then it delegates to `AppService` without a TypeError: backend/src/app/app.controller.spec.ts:15
- Given the test execution, when `getData()` returns, then it matches the expected mock or instance output of `AppService`: backend/src/app/app.controller.spec.ts:16

## Blocking
- None

## Non-blocking
- None