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
- **GitHub repo** as `owner/repo` (or "not on GitHub"), and its **default branch**
- **Tracker**: `clickup`, `jira`, `linear`, or `none` (no ticket system - then skip every tracker step below).
- **Tracker Board ID**: never query the tracker API to find it.
  - ClickUp: digits from the list URL (`https://app.clickup.com/<team>/v/l/li/<LIST_ID>`) or List settings -> "Copy ID".
  - Jira: the project key (`BILL`), plus the site URL `https://<site>.atlassian.net`.
  - Linear: the team key (`ENG`) or team id, from Settings -> Teams.
- **Figma file link** (or "none"). If "none", skip every Figma step below.
- **GCP** (or "none"): GCP Project ID and region of the environment the project deploys
  to. If set, the user also stores the service-account key JSON (step 2) and you fill
  the template's GCP fields; `gcloud_env.py <slug>` then works for that project only.

- **How this project works (Flow)**, asked as one question with the default shown. Projects do not have
  to share a workflow; the answers go into `## Flow` of PROJECT_CONTEXT.md:
  - **Profile**: `factory` (default: we write specs, create tickets, build, review, QA, watch deploys) ·
    `teammate` (Van is one developer on a human team; tickets already exist; agents only take Van's) ·
    `maintenance` (bug fixes only) · `custom` (pick stages).
  - `teammate`/`maintenance` only: **Van's tracker user id or email** (the Assignee filter), and the repo's
    **PR template / CONTRIBUTING path** if it has one.
  - **PR base** if PRs do not go into the default branch (e.g. `develop`).
  - **Deploy signal**: `cloud-build` (needs GCP) · `github-actions` (needs a GitHub repo; the watcher
    reads check runs) · `none` (the merge is the signal).
  - **Deploy checks**: the trigger or workflow names that must ALL pass before a ticket moves to
    `staged`. Omit when there is one, or no CI.
  - **Board statuses: do not ask.** The tracker knows them; step 3d reads them and proposes the
    mapping. (This question used to present one project's board as the default, so every other
    project was framed as the exception, and it asked the user to do the mapping in their head.)
  - **Chat channel** where this project's updates go.

Do not proceed with placeholders. A missing Tracker Board ID (when the Tracker is not `none`) =
stop and ask.

## 2. Secrets (user runs these; you never see the values)

Names are fixed by the rule `<KIND>_<SLUGUPPER>`:

```
openclaw secrets store set <CLICKUP|JIRA|LINEAR>_API_TOKEN_<SLUGUPPER> --kind env --value-file -
#   ClickUp: the raw API token.   Linear: the API key.
#   Jira:    `email:api_token` on one line - Basic auth needs both halves.
openclaw secrets store set FIGMA_API_KEY_<SLUGUPPER> --kind env --value-file -
openclaw secrets store set GITHUB_TOKEN_<SLUGUPPER> --kind env --value-file -
# only if GCP is set: the name you put in PROJECT_CONTEXT's GCP Key Vault field
openclaw secrets store set GCP_SA_KEY_<SLUGUPPER>_<ENV> --kind env --value-file - < key.json
```

The user runs these in **their own SSH terminal**, not through a chat `!` prefix:
`--value-file -` reads a pasted value from stdin, which a chat shell does not
provide (it silently stores an empty value). The GitHub token is a fine-grained
PAT: resource owner = the org, only this repo, Contents + Pull requests
read/write, Commit statuses read/write (VanReviewer's `openclaw/review` status),
no Administration. If the org requires approval, an org owner must approve it before
`git_env.py <slug> --check` passes.

`--kind env` is required: without it names ending in `_API_KEY`/`_TOKEN` are
stored write-only and neither the scripts nor the Figma MCP launcher can read
them. Give the commands, wait for the user to confirm. Verify them through the
launchers in steps 4b, 4c, 6 and 7 (a probe or `--check` that passes proves the value is
readable). **Never** use `secrets` `action: list` or `openclaw secrets store list`: both
print env-kind values in plain text into the transcript. Never shell out to
`openclaw secrets` from a subprocess (second Node process; can OOM the gateway).

## 3. Create directories (approval gate: this touches the filesystem)

```
mkdir -p /home/openclaw/projects/<slug>
mkdir -p /home/openclaw/.openclaw/workspace/projects/<slug>/artifacts/{specs/_done,specs/_superseded,patches,reviews,qa,runs}
SLUG=<slug>
sed "s/<slug>/$SLUG/g" /home/openclaw/.openclaw/workspace/projects/_template/specs/_planned-data.md \
  > "/home/openclaw/.openclaw/workspace/projects/$SLUG/artifacts/specs/_planned-data.md"
```

`specs/_planned-data.md` is VanPM's list of planned-but-not-built database
changes; `specs/_done/` and `specs/_superseded/` hold archived specs. After
step 4, run `python3 /home/openclaw/.openclaw/workspace/projects/_tools/spec_index.py <slug>`
once to create `specs/_index.md` (it lists no features yet).

If a clone URL was given and the workbench directory is empty, clone into it
after the user confirms (`git clone <url> /home/openclaw/projects/<slug>`).

## 3b. Trust the workbench in the coding tool (approval gate: edits a tool config)

VanDev delegates code writing to `agy`, which refuses untrusted directories. After the
user approves, add **both** `/home/openclaw/projects/<slug>` and its worktree root
`/home/openclaw/projects/.worktrees/<slug>` to `trustedWorkspaces` in
`/home/openclaw/.gemini/antigravity-cli/settings.json` (read the JSON, append if
absent, write back; python3, not node). Say what you changed.

## 3c. GitHub repo setting (user, repo admin, once)

Ask the user to turn on **Settings → General → Automatically delete head branches**
for the repo. That is how `worktree.py <slug> sweep` learns a PR was merged.

## 3d. Ask the tracker for its board and statuses (skip when Tracker is `none`)

Never type a board's statuses from memory, and never assume the canonical keys map
onto them the way they do for another project.

```
python3 /home/openclaw/.openclaw/workspace/projects/_tools/tracker_probe.py \
  --tracker <clickup|jira|linear> --board <board id> --secret <VAULT NAME> \
  [--base-url https://<site>.atlassian.net]    # jira only
```

It prints the board's real name, its statuses, and the exact `**Statuses:**`,
`**Create status:**` and `**Status map:**` lines to paste into step 4.

Two things to do with the output:

1. **Confirm the board name with the user before continuing.** A valid id for the
   wrong board validates perfectly and then puts every ticket in the wrong place.
2. **Read the "not matched automatically" list aloud.** Each line says what that
   absent status costs (no `rejected` = QA rejections are not detected). Anything
   marked `!!` is required and must be mapped by hand; the rest are genuinely
   optional and the project works without them. If the board has an equivalent
   under a different name, add it to the Status map.

## 4. Write PROJECT_CONTEXT.md from the template

The one template is `/home/openclaw/.openclaw/workspace/projects/_template/PROJECT_CONTEXT.md`
(single source of truth; there is no copy inside this skill). Copy it to
`/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md` and fill
every `<placeholder>` **except the `## Stack` section**. Keep field labels
exactly as in the template; tooling parses them by label.

Fill `## Flow` from the Flow answers. Unfilled optional Flow lines may keep their `<placeholder>`: the
validator treats them as "use the profile default". The validator refuses combinations that cannot work
(e.g. `teammate` without an Assignee filter, `tickets` stage with human-owned tickets, `cloud-build` without
GCP, a Status map name that is not on the board), so fix the answer, not the tooling.

## 4b. Register the project's Figma MCP server (user runs these)

Skip if the Figma file is "none". The server name is always `figma-<slug>`; it
must match the **Figma MCP server** line in PROJECT_CONTEXT.md.

```
openclaw mcp set figma-<slug> '{"command":"/usr/bin/python3","args":["/home/openclaw/.openclaw/workspace/projects/_tools/figma_mcp.py","<slug>"],"connectionTimeoutMs":30000,"requestTimeoutMs":120000}'
openclaw mcp probe figma-<slug>
```

The probe must list `figma-<slug>__get_figma_data`. The launcher reads the
Design key named in PROJECT_CONTEXT.md, so a failed probe usually means that
file is invalid or the key is missing or stored as kind `secret`. QA and reviewer
already deny `figma-*` and `tracker-*`; **main's deny list stays empty** (anything denied
on main is denied to every agent it spawns), so nothing else changes per project.

## 4c. Register the project's tracker MCP server (user runs these)

**Skip this step entirely when the project's Tracker is `none`.**

The server name is always `tracker-<slug>` and the launcher is the same for every
tracker: it reads the project's `**Tracker:**` line and talks to ClickUp, Jira or
Linear accordingly. VanPM reads tickets through it (writes go through its scripts).
QA, reviewer and VanDev deny `tracker-*`.

```
openclaw mcp set tracker-<slug> '{"command":"/usr/bin/python3","args":["/home/openclaw/.openclaw/workspace/projects/_tools/tracker_mcp.py","<slug>"],"connectionTimeoutMs":30000,"requestTimeoutMs":120000}'
openclaw mcp probe tracker-<slug>
```

The probe must list `tracker-<slug>__tracker_get_task`. The tool names are the same
whatever the tracker is, which is why no deny list or prompt changes per project.

## 5. Validate (must pass before delegating)

```
python3 /home/openclaw/.openclaw/workspace/projects/_tools/validate_context.py /home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md
```

It will report the Stack section as unfilled; that is expected at this point.
Any other error: fix the file, do not continue.

## 6. Delegate the Stack section + live check to VanPM

`sessions_spawn` `project-manager` (context: isolated; no `cwd`, no `worktree`: a
spawned agent cannot use a project path as cwd, it reads the repo by absolute path) with:

> Onboarding `<slug>`. Fill the `## Stack` section of
> `/home/openclaw/.openclaw/workspace/projects/<slug>/PROJECT_CONTEXT.md` by
> inspecting the repo (whichever manifest it has: package.json/nx.json/lockfiles, pyproject.toml,
> requirements.txt, go.mod, Cargo.toml, pom.xml, Gemfile, composer.json; say
> "none yet" or "unknown" rather than guessing). Fill **Install command** and the
> **Dev/QA Test Commands** by running each candidate once in your own worktree
> (`worktree.py <slug> create <prefix>/onboarding-check --agent project-manager`, then
> `finish`): keep only commands that run once and exit; list watch-mode ones under
> Forbidden. Then run
> `validate_context.py <file> --live`, paste the LIVE list name/space/statuses
> into the file's "Tracker Board name" and "Statuses" fields, re-run until VALID
> and LIVE OK. Do not create tickets. Report the list name so the user can
> confirm it is the right list.

Relay VanPM's report to the user, especially the Tracker list name. If the
user says it is the wrong list, fix the ID in the file and re-run step 6.

## 7. Persist and report

- Check the code tooling for the new slug: `python3 /home/openclaw/.openclaw/workspace/projects/_tools/worktree.py <slug> list`
  (must run without error) and, if GitHub is set, `python3 .../_tools/git_env.py <slug> --check`.
- Append to `MEMORY.md`: `<date> onboarded <slug>: context at <path>, <tracker> board '<name>', secret *names* only (never ids or values).`
- Reply with the context path, the validated list name, the secret names, the Figma MCP server name, the worktree root,
  and the Flow in one line (profile, stages, PR base, deploy signal).

## Re-validating an existing project

Any time an agent hits "list not found", "token not found", or a status
mismatch, run step 5 (and `--live` via VanPM) before changing any prompt or
script. Fix the file, not the tooling.
