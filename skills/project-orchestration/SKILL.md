---
name: project-orchestration
description: Software feature delivery workflow for an onboarded project. Takes a feature, or any request spanning PM, dev, review, and QA, through spec → build → review → QA → approval → close. Orchestrator only delegates; every path comes from the project's PROJECT_CONTEXT.md.
user-invocable: true
metadata: { "openclaw": { "emoji": "🦞" } }
---

# project-orchestration

You are the orchestrator. You manage the factory; you never do the labor.
Everything below is parameterised by one file:

    CTX = /home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md

Read it first. `Code (CWD)` is where code lives; `Internal Artifacts` is where
every spec/patch/review/qa file goes. Never guess a List ID, secret name, or
path. Never call ClickUp, Figma, git push, or any external API yourself.

## When not to use this

A request that is only one agent's job ("fix the tickets", "refine this spec",
"fix the login bug", "review this PR", "test the password step") is not this
workflow. Spawn that agent directly, as the Team roster in `AGENTS.md` says.

## 0. Resolve the project

- If the request names a project, set `<slug>`. If it doesn't and more than one
  directory exists under `/home/openclaw/.openclaw/workspace/projects/` (ignore
  `_template`, `_tools`), ask which one.
- If CTX is missing → run the `project-onboarding` skill first.
- Run `python3 /home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py CTX`.
  Not VALID → fix via onboarding; do not continue.

## 1. Spec (VanPM)

`sessions_spawn` `project-manager`, context `isolated`, `cwd` = Code (CWD), message:

> Project `<slug>`. Use `feature-breakdown` on: <feature list + Figma links>.
> Write the spec to `<Internal Artifacts>/specs/<feature-slug>.md` and stop
> for approval. Do not push tickets.

`sessions_yield` until done. Relay VanPM's summary (parent, subtasks per lane,
hours, open questions) to the user **verbatim**. Wait for "go".
On "go": message VanPM "approved, push". VanPM replies with ticket links;
relay them.

## 2. Build (VanDev) — one lane ticket at a time, in dependency order

For each subtask in the spec (`[DB]` → `[BE]` → `[FE]` → `[INT]`; parallel ones may run together):

First, verify the ticket is available to be worked on by spawning `project-manager`, context `isolated`, `cwd` = Code (CWD), message:

> Project `<slug>`. Check the status of ticket `<exact ticket title>` in the project's configured tracker. If someone else is working on it, or if it is already in progress/complete, report "SKIP". Otherwise, report "GO".

`sessions_yield`. If VanPM reports "SKIP", skip this ticket and move to the next one. If "GO", proceed to spawn the developer:

`sessions_spawn` `developer`, context `isolated`, `cwd` = Code (CWD), message:

> Project `<slug>`. Implement ticket `<exact ticket title>` from
> `<Internal Artifacts>/specs/<feature-slug>.md`. Branch
> `<branch prefix>/<feature-slug>`. Save the patch to
> `<Internal Artifacts>/patches/<feature-slug>--<lane-slug>.patch`. Do not push
> or open a PR.

`sessions_yield`. If VanDev reports the spec is wrong or impossible, go back to
step 1 with its objection; do not "fix" the spec yourself.

## 3. Review (VanReviewer)

`sessions_spawn` `code-reviewer`, `cwd` = Code (CWD):

> Project `<slug>`. Review `<Internal Artifacts>/patches/<feature-slug>--<lane-slug>.patch`
> against ticket `<title>` in `<Internal Artifacts>/specs/<feature-slug>.md`.
> Write `<Internal Artifacts>/reviews/<feature-slug>--<lane-slug>.md`.

Verdict `CHANGES REQUESTED` → back to step 2 with the review path. `APPROVED` → continue.

## 4. Verify (VanQA) — once per feature, after all lane tickets are approved

`sessions_spawn` `qa-engineer`, `cwd` = Code (CWD):

> Project `<slug>`. Run the `[QA]` ticket for `<feature-slug>` from the spec.
> Write `<Internal Artifacts>/qa/<feature-slug>.md`. Do not modify code.

Defects → step 1: VanPM turns each defect into a `bug/` ticket via
`feature-breakdown`, then step 2 for each.

## 5. Approval gate (external side-effects start here)

Ask the user, with the review and QA paths:
"Feature `<feature-slug>` passed review and QA. Approve push + PR?"
Only on yes: VanDev pushes the branch and opens the PR (spawn with that exact
instruction). Then `sessions_spawn` `project-manager` with the message: "Project `<slug>`. Mark the tickets for `<feature-slug>` as COMPLETE in the project's configured tracker."

## 6. Memory

Append to `/home/openclaw/.openclaw/workspace/MEMORY.md` under the project:
date, feature-slug, PR link, artifact paths, anything learned. Never store
secrets or IDs here; they live in CTX.

## Rules that apply to every step

- Artifacts are completion markers. Before spawning a step, check whether its
  artifact already exists; if so, read it and skip or resume.
- Subagents get the `<slug>` and absolute paths in the message. They must not
  discover them.
- If `sessions_spawn` fails with `agentId is not allowed`, check
  `agents.defaults.subagents.allowAgents` in `~/.openclaw/openclaw.json` and ask
  before editing config.
- Discord: bullets not tables; wrap multiple links in `<>`.
