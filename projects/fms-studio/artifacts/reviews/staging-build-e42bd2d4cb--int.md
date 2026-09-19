CHANGES REQUESTED
Reviewed SHA: 7c5709cf7d91e48358459f0f97af81313e63ee9f

- Given the repository root, when `npm ci` is run, then it executes successfully and exits with status 0. (Not implemented - the provided fix does not include the needed changes to `package-lock.json` for `content-type@1.0.5`).
- Given the lockfile, when inspected, then it contains the resolution for `content-type@1.0.5` in sync with `package.json`. (Not implemented - missing from the diff entirely).
- Given the Cloud Build staging pipeline runs, when it executes the deployment step, then it passes without lockfile errors. (Not tested).

### Blocking
- `package-lock.json`: The diff introduces `tailwindcss` dependencies (`@tailwindcss/oxide-wasm32-wasi` etc.) instead of syncing `content-type@1.0.5`. Without `content-type` in the lockfile, the build will still fail during the `npm ci` step in staging. Please run `npm install --package-lock-only content-type@1.0.5` (or just `npm install`) and push the correct changes to the `package-lock.json`.