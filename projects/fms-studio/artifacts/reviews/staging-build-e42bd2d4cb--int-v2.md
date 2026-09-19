APPROVED
Reviewed SHA: 42b2e09000874bb0a3a29a9ee0212296e582ba93

- Given the repository root, when `npm ci` is run, then it executes successfully and exits with status 0. (verified via local execution of `npm ci`)
- Given the lockfile, when inspected, then it contains the resolution for `content-type@1.0.5` in sync with `package.json`. (package-lock.json:13138)
- Given the Cloud Build staging pipeline runs, when it executes the deployment step, then it passes without lockfile errors. (verified by `npm ci` fix, staging deploy relies on this passing)

Blocking
None

Non-blocking
None