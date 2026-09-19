---
name: worktree-lifecycle
description: "How every agent gets, hands off and removes a code checkout for ANY onboarded project: one task = one branch = one git worktree, created and removed only through projects/_tools/worktree.py. Use before touching project code, before launching agy/Claude Code, before QA or code review of a branch, and after opening a PR."
---

# Worktree lifecycle (all projects, all agents)

**One task = one branch = one worktree = one PR.** Agents never edit a project's primary
checkout (its `Code (CWD)` in `PROJECT_CONTEXT.md`); that folder is read-only for agents.
Every checkout an agent works in comes from one tool:

```
python3 /home/openclaw/.openclaw/workspace/projects/_tools/worktree.py <slug> <command> ...
```

`<slug>` is the project slug from your task. The tool reads everything else (primary
checkout, default branch, artifacts folder) from that project's `PROJECT_CONTEXT.md`, so it
works unchanged for every project. Do not hand-roll `git worktree add`, `rm -rf` a worktree,
or ask OpenClaw for `worktree: true` on a spawn: OpenClaw's managed worktrees can only copy
agent workspaces, never a project's code repo.

## The routine

| When | Who | Command |
|---|---|---|
| Start of every coding task | VanDev | `worktree.py <slug> sweep` |
| Before any code is written | VanDev | `worktree.py <slug> create <branch> --agent developer --task "<one line>"` |
| Code gets written | agy / Claude Code | launched with `workdir:` = the printed worktree path |
| Review says CHANGES REQUESTED | VanDev | fix in the same worktree (it is still there), commit, new patch |
| Review APPROVED that SHA | VanDev | `git -C <worktree> push -u origin <branch>` (never the default branch), then `finish <branch>` |
| QA run / code review | VanQA, VanReviewer | `create <branch> --agent qa-engineer` (or `code-reviewer`) -> work -> `finish <branch>` |
| Next lane ticket / QA fixes | VanDev | `create <branch>` again: it checks out `origin/<branch>` |
| PR (after Van's yes) | VanDev | `create <branch>`, `git_env.py <slug> -- gh pr create --base <Default branch>`, then `finish <branch> --pr <url>` |

A branch lives in **one** worktree at a time. `create` refuses when another agent
still holds it: that agent must push and `finish` first. That is why a task branch
is pushed as soon as its review is APPROVED (pushing a task branch deploys nothing;
PRs and merges are what need Van).

`finish` is not optional: skipping it leaves the folder and, worse, can leave uncommitted files
out of the PR without anyone noticing. `create` prints the exact `finish` command to run.
Before `git push`, run `git -C <worktree> status`: anything listed is NOT in your PR.

Branch names (enforced by `create`): one of the project's **Branch Prefixes** from `PROJECT_CONTEXT.md` +
`<feature-slug>`, e.g. `feature/organizer-landing`, `bug/cloud-build-errors`. Never the
default branch.

## What each command guarantees

- **create** fetches first, then either starts a new branch from `origin/<Default branch>` or,
  if `origin/<branch>` exists, checks that branch out. It verifies HEAD equals the fetched
  start SHA and prints a *preparation receipt* (worktree path, branch, start ref + SHA). Paste
  that receipt into the agy/Claude Code worker prompt: it is the `coding-agent` skill's Git
  preparation block. Running `create` again for a branch that already has a worktree just
  prints the existing path.
- **finish** deletes the worktree only if nothing in it exists only locally: no modified or
  untracked files, an upstream is set, zero unpushed commits. If anything is local it keeps
  the folder, prints why and exits 2. Exit 2 is not an error to work around: push the work,
  or tell Van what is there. Never `--force`, never `rm -rf`.
- **sweep** runs `git fetch --prune` + `git worktree prune`. For a branch whose remote is gone
  (GitHub deletes head branches after merge) it asks GitHub for the PR: if it is MERGED/CLOSED
  and the PR head equals the local tip, the worktree and local branch are removed - even when
  `finish` was skipped. Uncommitted files are never deleted: sweep reports `KEPT ... tell Van`,
  because files that were never committed were never in the PR. It also reports worktrees it did not create
  (`UNMANAGED`) and a primary checkout that is dirty or off the default branch (`PRIMARY`) -
  relay both to Van, never "fix" them yourself.

## Where things live

- Worktrees: `<parent of Code (CWD)>/.worktrees/<slug>/<branch with / as __>`
- Ledger (source of truth): `<Internal Artifacts>/worktrees.jsonl`
- PR list for humans (generated, do not edit): `<Internal Artifacts>/prs.md`

## Dependencies (node_modules)

A worktree is a fresh checkout without `node_modules`. Install only when the task needs a
build or tests, inside the worktree, with the project's install command from
`PROJECT_CONTEXT.md`. Gitignored files the project needs (e.g. `.env`) are copied
automatically when the repo has a `.worktreeinclude` file (gitignore syntax) at its root.

## Handing a branch to another agent

Pass the **slug and branch name**, never a worktree path: the receiving agent runs its own
`create`, so two agents never share one folder.
