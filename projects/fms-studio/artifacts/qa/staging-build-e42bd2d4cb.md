I have updated the `package-lock.json` to include the correct resolution for `content-type@1.0.5`. 

I ran `npm install content-type@1.0.5 --package-lock-only`, which synced the lockfile. The previous commit only added `Tailwind CSS WASM` binaries without actually syncing the `content-type` dependency. After running the sync, `content-type@1.0.5` is now correctly present in the lockfile resolutions. I verified the change by making sure `npm ci` succeeds.

1. Switched back to the correct commit that amends the lockfile.
2. Synced the package lock using `npm install --package-lock-only content-type@1.0.5`
3. Tested `npm ci` to ensure the lockfile works and there are no ERESOLVE issues.
4. Pushed the branch and created PR #37.
5. Saved patch to `/home/openclaw/.openclaw/workspace/projects/fms-studio/artifacts/patches/staging-build-e42bd2d4cb--int.patch`.

Commit SHA: `42b2e09000874bb0a3a29a9ee0212296e582ba93`
PR URL: https://github.com/symphco/fms-studio/pull/37