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

Background worker that writes code: feature work, large refactors, test suites. It never runs git, gh,
builds, tests or deploys; those stay VanDev's own `exec` calls (commit, push and PR included).
Sibling of the bundled `coding-agent` skill, which covers Claude Code. Same
discipline applies; only the launch form differs.

## When to use

Use for: multi-file feature work, large refactors, test suites.

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

## Design work: assets before the prompt

`agy` cannot see the design. It has no Figma tools, it cannot open a PNG, and the
screenshots live in Internal Artifacts, outside the worktree it runs in. Given a
text ticket alone it invents stand-ins — a `<div>Logo</div>`, a grey box captioned
"[Photo Collage Image Placeholder]", `bg-orange-500` where the brand is `#FF6100`.
Every fms-studio screen built before 2026-09-21 shipped that way.

So when the ticket has a `## Design fidelity` section, do this **before** launching:

1. **Copy the assets into the worktree**, at the `repo_path` the section gives:

   ```bash
   A="<Internal Artifacts>/specs/_figma/<feature-slug>"
   install -D "$A/assets/logo.svg" "<worktree>/frontend/public/brand/logo.svg"
   ```

   `install -D` creates the parent directories. Copy only the assets this ticket
   claims. They are downloaded already — never call a Figma tool to re-fetch what
   is sitting in Internal Artifacts, and never have `agy` fetch them itself.
2. **Check each one arrived and is not empty** (`test -s <path>`). A 0-byte asset
   is a failed download upstream: stop and report it, do not build around it.
3. **Name them in the prompt**, with the tokens, and forbid the fallback:

   ```
   Implement <ticket title> in this worktree.
   <the ticket body, verbatim>

   Design assets are ALREADY in this worktree — use them, do not invent placeholders:
     frontend/public/brand/logo.svg   the wordmark; replaces any text logo, 154x26
     frontend/public/marketing/hero-collage.png   the hero image, 1472x1774
   Design tokens are exact. Primary #FF6100, text #313131, font Host Grotesk 400/500,
   radius 12px. Add them to the project's theme config rather than hardcoding per
   component. Do not substitute a near colour from the framework's default palette.
   Do NOT render a placeholder box, a text stand-in, or a solid colour anywhere an
   asset above belongs. If something you need is missing, stop and say so.
   ```

4. **Check the result before you commit**: `git -C <worktree> status` must show the
   assets as added files, and the diff must reference each one. An asset copied in
   but never referenced by the code means `agy` ignored it — that is a rework, not a
   pass. Grep the diff for `placeholder`, `Placeholder` and `TODO` before you push.

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
