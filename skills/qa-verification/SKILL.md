---
name: qa-verification
description: How to verify a feature against its acceptance criteria and write the QA report. Use when running the [QA] ticket of a feature. The worktree routine and the never-list are in your AGENTS.md - this file is how to test and what to write.
metadata: { "openclaw": { "emoji": "🧪" } }
---

# QA verification

**Your AGENTS.md owns the routine** - which branch, the worktree, which commands
you may run, the report path, and what you must never do. This file is the other
half: how to test well, and what a report has to contain to be worth anything.

## The contract

You test **the acceptance criteria**, not the code. A criterion is written
Given/When/Then and is falsifiable: either you performed it and observed the
Then, or you did not. "The code looks like it does that" is not a result.

This is the team's internal check. It changes no ticket status - VanPM moves
tickets, and `staged` comes from the delivery watcher, never from you.

## Before you test

1. Read the spec's parent ticket for the acceptance criteria, and the `[QA]`
   ticket for the end-to-end scenario. They are the whole scope.
2. Note the commit SHA you are testing (`git -C <worktree> rev-parse HEAD`). It
   goes at the top of the report. A report without it cannot be trusted later,
   because the branch moves.
3. Install with the project's **Install** command, then run only the **Tests**,
   **Lint** and **E2E** commands PROJECT_CONTEXT lists. Never infer one, never
   run a **Forbidden** one.

If a listed command fails for a reason outside this feature - a broken lockfile,
a missing service, an unrelated failing suite - that is a **finding you report**,
not something to fix, work around, or silently skip.

4. **Defeat the build cache, or you have verified nothing.** Nx, Turbo, Gradle,
   Bazel and friends replay a previous result when the inputs match - including
   a result computed in *another agent's worktree*. A green line that says
   `Cache: 1/1 hit (100%)`, or names a path that is not your worktree, means the
   command did not run. VanDev has usually just run the same command on the same
   inputs, so this is the normal case, not a rare one.

   Add the project's no-cache flag to every verification run: for Nx,
   `npx nx test <project> --skip-nx-cache`. Check the output names YOUR worktree
   path and does not report a cache hit. Put the command you actually ran in the
   report - not the one PROJECT_CONTEXT lists, the one you ran.

## How to test

- Follow the Given/When/Then literally. Set up the Given, do exactly the When,
  check the Then.
- Then try to break it. A criterion you only confirmed on the happy path is
  half-tested. Go at: empty, missing, very long, zero, negative, duplicate,
  out of order, wrong type, no permission, already-exists, and the boundary
  values on either side of a limit.
- Check what should *not* have changed: the out-of-scope list in the ticket is
  a set of things to confirm are untouched.
- Re-run anything that fails once before reporting it, so you do not file a
  flake as a defect - and if it passes on retry, say so and call it flaky.
- Poll a build, log or server at most 3 times, about 60s apart, then report what
  you have. A turn that never ends reads as "typing" forever and Van cannot
  reach you.

## The report

`<Internal Artifacts>/qa/<feature-slug>.md`:

```
Tested SHA: <commit>
Commands: <the exact commands you ran, and their result>

## Criteria
- [PASS] <criterion, quoted> - how you confirmed it
- [FAIL] <criterion, quoted> - see defect 2
- [BLOCKED] <criterion> - why it could not be tested

## Defects
### 1. <one-line summary>
- Steps: <numbered, reproducible from a clean state>
- Expected: <what the criterion says>
- Observed: <what actually happened, verbatim error text if any>
- Evidence: <path under qa/>
- Scope: <blocks the feature | pre-existing | out of scope>
```

Rules that make it useful:

- **Every criterion appears**, with a verdict. A criterion you did not test is
  `BLOCKED` with a reason, never omitted.
- **Steps reproduce from a clean state.** "Click the button again" is not a step.
- **Observed is what you saw**, quoted, not your interpretation of it.
- Evidence (screenshots, reports, logs) goes under `qa/`. Clean the worktree so
  `finish` does not refuse it.
- Finding nothing is a real result - but say what you tried, so the verdict can
  be judged.

## Never

- Never conclude PASS because the tests are green. The suite is not the criteria.
- Never report "looks fine". Either it passed, or you name the defect.
- Never file tickets or fix code: defects go to VanPM, fixes go to VanDev.
