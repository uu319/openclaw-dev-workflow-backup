CHANGES REQUESTED
Reviewed SHA: 42b2e09000874bb0a3a29a9ee0212296e582ba93

- Given the repository root, when `npm ci` is run, then it executes successfully and exits with status 0: Untested
- Given the lockfile, when inspected, then it contains the resolution for `content-type@1.0.5` in sync with `package.json`: Missing
- Given the Cloud Build staging pipeline runs, when it executes the deployment step, then it passes without lockfile errors: Untested

## Blocking
- `package-lock.json`: The diff does not add `content-type@1.0.5` to the lockfile as requested. It only contains unrelated `@tailwindcss/oxide-wasm32-wasi` dependencies. Please run `npm install content-type@1.0.5` or `npm install` to actually sync the lockfile for `content-type`.

## Non-blocking
- None