# Ticket body template

Copy this skeleton into every ticket's body (parent and subtask). Keep every
heading, even if the content is "none". Replace everything in angle brackets.
Do not add a `## Design` section: the push script generates it from the
ticket's `figma:` and `screenshots:` headers (links + embedded screenshots).

```markdown
## Context
Parent: <feature title, or "this is the parent"> · Figma: <link or none> · Lane: <FE|BE|DB|INT|QA|SPIKE|FEATURE>

## User story
As a <role>, I want <goal>, so that <benefit>.

## In scope
- <one bullet per thing that will be built>

## Out of scope (do NOT build)
- <one bullet per thing the coding agent might otherwise add: pagination, auth, analytics, animations, other card types…>

## Acceptance criteria
- Given <state>, when <trigger>, then <exact observable result>.
- Given <state>, when <trigger>, then <exact observable result>.
- <at least three, all in Given/when/then form; [FE]: one per button, input, link and state in the screen inventory, quoting exact Figma labels>

## Technical notes
- Interface / schema: <the contract this lane adds or changes: HTTP endpoint, CLI command, queue
  message, exported function | table.column types>
- Mock or fixture for parallel work: <shape the FE can code against before the BE exists>
- Breakpoints (UI lanes only): <mobile <640px: …, tablet 640–1024px: …, desktop >1024px: …>

## Depends on / blocks
- Depends on: <ticket titles or none>
- Blocks: <ticket titles or none>

## Test notes (how QA verifies)
- <steps or command; for [QA] tickets this is the full E2E scenario>

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (the project's **Tests** command, run with the
      project's no-cache flag - a cached pass is not a run)
- [ ] Lint clean (the project's **Lint** command)
- [ ] PR opened from the branch this project's Flow **Branch model** gives, and reviewed
- [ ] Status moved to the board's `staged` status once the change is on staging (the delivery
      watcher tells VanPM; nobody sets it by hand)
```

## Acceptance-criteria examples

Bad → Good:

- "Users can sign in" → "Given a registered email and correct password, when
  the user submits the form, then `POST /api/auth/login` returns 200 with
  `{ token, user: { id, email } }` and the app navigates to `/dashboard`."
- "Show an error on failure" → "Given the API returns 401, when the form is
  submitted, then the `<FormError>` component renders the text 'Email or
  password is incorrect' under the password field and the submit button is
  re-enabled."
- "Responsive layout" → "Given a viewport narrower than 640px, when the
  dashboard renders, then the album cards render in 1 column; given 640–1024px,
  2 columns; given wider than 1024px, 3 columns (Tailwind `grid-cols-1
  sm:grid-cols-2 lg:grid-cols-3`)."
- "Password must be secure" → "Given a password shorter than 8 characters, when
  the user blurs the field, then the text 'Use at least 8 characters' appears
  below it and the Continue button stays disabled."
