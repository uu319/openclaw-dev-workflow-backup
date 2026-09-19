---
name: agy-coding
description: "Delegate substantial coding work to Antigravity CLI (agy) as a background worker; not simple edits or read-only lookup."
metadata:
  {
    "openclaw":
      {
        "emoji": "🛰️",
        "requires": { "anyBins": ["agy"] },
      },
  }
---

# agy (Antigravity CLI)

Background worker for feature builds, large refactors, and issue-to-PR loops.
Sibling of the bundled `coding-agent` skill, which covers Claude Code. Same
discipline applies; only the launch form differs.

## When to use

Use for: multi-file feature work, large refactors, test suites, issue-to-PR loops.

Do **not** use for: simple edits, read-only code lookup, or any run inside
`~/.openclaw`, `$OPENCLAW_STATE_DIR`, or active OpenClaw state dirs.

## Auth and models

`agy` runs on Van's own Gemini API key so usage bills to that key, not the
Antigravity subscription. `~/.gemini/antigravity-cli/settings.json` has
`"modelProvider": "gemini"` set, which makes `agy` require `GEMINI_API_KEY` in
its process environment instead of the OAuth/subscription flow.

The key lives in the OpenClaw team store as an **env-kind** entry named
`GEMINI_API_KEY` (env-kind, not secret-kind — secret-kind entries are
write-only and can never be read back out, which is why an earlier attempt at
this failed). It is never injected automatically; fetch it and export it for
each `agy` invocation only, never into a standing/global env var:

```bash
mkdir -p <Internal Artifacts>/runs
GEMINI_API_KEY="$(openclaw secrets store get GEMINI_API_KEY --plain)" \
  agy --mode accept-edits --print "<prompt>" 2>&1 \
  | tee <Internal Artifacts>/runs/<feature-slug>--<lane-slug>--$(date -u +%Y%m%dT%H%M).log
```

The `tee` log is the run log VanOpenClaw checks before it believes a delegation
claim. Never skip it. Fetch only `GEMINI_API_KEY` from the store: never `list`
the store and never `get` any other secret (ClickUp, GitHub, GCP keys reach you
through their launchers).

`--print` must immediately precede the prompt string — `agy --print --mode X "<prompt>"` fails
because `--print` swallows the next token (`--mode`) as its own argument. Put `--mode` first.

Never `echo`, log, or otherwise print the fetched value. Backend models are
Gemini 3.x; pick with `--model`, reasoning depth with `--effort low|medium|high`.

The workspace must be listed in `trustedWorkspaces` in that settings file.
The `project-onboarding` skill adds each project's Code (CWD) and its
`.worktrees/<slug>` folder there; if `agy`
refuses a directory, report it to the orchestrator rather than editing the file.

## Hard rules

- Always launch with `background:true`.
- Run from inside the target worktree; `agy` has no PTY requirement.
- Standard form: the `GEMINI_API_KEY="$(openclaw secrets store get GEMINI_API_KEY --plain)" agy --mode accept-edits --print "<prompt>"` form above — never launch `agy` without it now that auth is API-key based.
- `--dangerously-skip-permissions` is for fully unattended runs **only** in an
  isolated worktree built from a trusted ref. Never in the primary checkout.
- Capture a real notification route before spawning. The worker must report
  completion or failure via `openclaw message send`.
- Monitor with `process`. Do not kill slow workers without cause.
- If the worker fails or hangs, respawn or ask — never silently hand-code the
  task instead.
- `-c` / `--continue` resumes the most recent conversation; `--conversation <id>`
  resumes a specific one. Prefer resuming over restarting a long build.

## Git preparation

Create the worktree with `worktree.py <slug> create <branch>` (shared
`worktree-lifecycle` skill) and launch `agy` with `workdir:` set to the printed
path; its preparation receipt satisfies the rules below. Never create worktrees
by hand. Follow the mandatory Git preparation in the bundled `coding-agent` skill
(`/usr/lib/node_modules/openclaw/skills/coding-agent/SKILL.md`) before any run
that modifies a Git-backed project: prove the canonical remote and target base,
classify the source ref as trusted or untrusted, fetch immediately before
creating an isolated worktree, verify the starting SHA, and launch only in that
worktree. Never materialize a contributor-controlled ref outside the approved
untrusted-PR sandbox.
