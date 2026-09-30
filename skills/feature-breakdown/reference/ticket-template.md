# Ticket body template (the default — a project may replace it)

This is the skeleton a project gets when its `## Ticket conventions` section
names no `Required sections` of its own. **Check the project first**
(`validate_context.py <CTX> --json` → `tickets.required_sections`,
`tickets.acceptance_heading`, `tickets.design_section`): when it named its own
headings, build the body from those instead and keep the sections below that it
did not name but that a developer still needs. The parts that never change are
the intent of each section, not its title.

Copy the skeleton into every ticket's body (parent and subtask). Keep every
heading, even if the content is "none" — a heading with "none" under it is a
statement, a missing heading is a question. Replace everything in angle
brackets. Do not add a `## Design` section: the push script generates it from
the ticket's `figma:`, `screenshots:` and `assets:` headers (links, embedded
screenshots, asset list). `## Design fidelity` below is different — you **do**
write that one, on every ticket in the project's `design_lanes` (default `[FE]`),
under whatever heading its `design_section` names.

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
<the project's `acceptance_heading`; e.g. fms-studio calls this `## Acceptance scenarios`>
- Given <state>, when <trigger>, then <exact observable result>.
- Given <state>, when <trigger>, then <exact observable result>.
- <at least `min_acceptance_criteria` (default three); all in Given/when/then form unless the project's `acceptance_format` is `free`; design lanes: one per button, input, link and state in the screen inventory, quoting exact Figma labels>

## Design fidelity
<the project's `design_section`, on its `design_lanes` only (default `[FE]`); omit the whole section on other lanes>
- Tokens: <every colour as hex, font family + weights + sizes, radii, shadows — exact values from get_figma_data, never names>
- Assets (from `specs/_figma/<feature-slug>/assets/manifest.json`, copy into the repo at these paths):
  - `<assets/file.svg>` → `<repo path>` — <what it is, WxH, what it replaces>
  - <or: "none (this screen is CSS only)">
- No placeholders: every asset above is rendered by the code. A grey box, a text
  stand-in, or a solid colour where artwork belongs is a defect.

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
- [ ] ([FE] only) Every asset in `## Design fidelity` is committed at its stated repo
      path, non-empty, and rendered by the code; no placeholder box or text stand-in
      remains, and the tokens listed there are the values in the code
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
