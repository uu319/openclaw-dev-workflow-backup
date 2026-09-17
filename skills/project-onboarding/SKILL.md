---
name: project-onboarding
description: Onboard a new project end to end — collect IDs and secrets from the user, create the workbench and artifact directories, write PROJECT_CONTEXT.md from the template, validate it, and delegate the Stack section to VanPM. Use for "onboard", "start a new project", "set up <project>".
user-invocable: true
metadata: { "openclaw": { "emoji": "🧭" } }
---

# project-onboarding

The orchestrator owns onboarding. The output is one validated file,
`/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md`, that
every agent reads before touching the project. If that file is wrong, tickets
land in the wrong list and secrets are looked up under the wrong name, so no
step below is optional.

## 1. Collect from the user (ask once, as one checklist)

- **Slug**: lowercase, hyphens (`my-app`). Derive `SLUGUPPER` = slug uppercased with hyphens removed (`MYAPP`).
- **Display name**
- **Git SSH clone URL** and SSH alias if the host uses one
- **ClickUp List ID**: digits from the list URL (`https://app.clickup.com/<team>/v/l/li/<LIST_ID>`) or List settings → "Copy ID". Never query the ClickUp API to find it.
- **Figma file link** (or "none"). If "none", skip every Figma step below.

Do not proceed with placeholders. Missing List ID = stop and ask.

## 2. Secrets (user runs these; you never see the values)

Names are fixed by the rule `<KIND>_<SLUGUPPER>`:

```
openclaw secrets store set CLICKUP_API_TOKEN_<SLUGUPPER> --kind env --value-file -
openclaw secrets store set FIGMA_API_KEY_<SLUGUPPER> --kind env --value-file -
```

`--kind env` is required: without it names ending in `_API_KEY`/`_TOKEN` are
stored write-only and neither the scripts nor the Figma MCP launcher can read
them. Give both commands, wait for the user to confirm, then verify with your
`secrets` tool (`action: list`): both must show kind `env`. Never shell out to `openclaw secrets` from a
subprocess (second Node process; can OOM the gateway).

## 3. Create directories (approval gate: this touches the filesystem)

```
mkdir -p /home/openclaw/projects/<slug>
mkdir -p /home/openclaw/.openclaw/workspace/projects/<slug>/artifacts/{specs,patches,reviews,qa}
```

If a clone URL was given and the workbench directory is empty, clone into it
after the user confirms (`git clone <url> /home/openclaw/projects/<slug>`).

## 3b. Trust the workbench in the coding tool (approval gate: edits a tool config)

VanDev delegates builds to `agy`, which refuses untrusted directories. After the
user approves, add `/home/openclaw/projects/<slug>` to `trustedWorkspaces` in
`/home/openclaw/.gemini/antigravity-cli/settings.json` (read the JSON, append if
absent, write back; python3, not node). Say what you changed.

## 4. Write PROJECT_CONTEXT.md from the template

Copy `{baseDir}/reference/PROJECT_CONTEXT.template.md` to
`/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md` and fill
every `<placeholder>` **except the `## Stack` section**. Keep field labels
exactly as in the template; tooling parses them by label.

## 4b. Register the project's Figma MCP server (user runs these)

Skip if the Figma file is "none". The server name is always `figma-<slug>`; it
must match the **Figma MCP server** line in PROJECT_CONTEXT.md.

```
openclaw mcp set figma-<slug> '{"command":"/usr/bin/python3","args":["/home/openclaw/.openclaw/workspace/projects/_tools/figma_mcp.py","<slug>"],"connectionTimeoutMs":30000,"requestTimeoutMs":120000}'
openclaw mcp probe figma-<slug>
```

The probe must list `figma-<slug>__get_figma_data`. The launcher reads the
Design key named in PROJECT_CONTEXT.md, so a failed probe usually means that
file is invalid or the key is missing or stored as kind `secret`. The main, QA
and reviewer agents already deny `figma-*__*`, so nothing else changes per project.

## 5. Validate (must pass before delegating)

```
python3 /home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py /home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md
```

It will report the Stack section as unfilled; that is expected at this point.
Any other error: fix the file, do not continue.

## 6. Delegate the Stack section + live check to VanPM

`sessions_spawn` `project-manager` (context: isolated, cwd: `/home/openclaw/projects/<slug>`) with:

> Onboarding `<slug>`. Fill the `## Stack` section of
> `/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md` by
> inspecting the repo (package.json, nx.json, project.json, lockfiles; say
> "none yet" or "unknown" rather than guessing). Then run
> `validate_context.py <file> --live`, paste the LIVE list name/space/statuses
> into the file's "ClickUp List name" and "Statuses" fields, re-run until VALID
> and LIVE OK. Do not create tickets. Report the list name so the user can
> confirm it is the right list.

Relay VanPM's report to the user, especially the ClickUp list name. If the
user says it is the wrong list, fix the ID in the file and re-run step 6.

## 7. Persist and report

- Append to `MEMORY.md`: `<date> onboarded <slug>: context at <path>, ClickUp list '<name>' (<id>), secrets CLICKUP_API_TOKEN_<SLUGUPPER> / FIGMA_API_KEY_<SLUGUPPER>`.
- Reply with the context path, the validated list name, the two secret names, and the Figma MCP server name.

## Re-validating an existing project

Any time an agent hits "list not found", "token not found", or a status
mismatch, run step 5 (and `--live` via VanPM) before changing any prompt or
script. Fix the file, not the tooling.
