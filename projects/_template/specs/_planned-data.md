# Planned data: <slug>

What the **tickets plan to add** to the database and are **not built yet**,
with the ticket that owns each change. This is not the schema.

- **What already exists** lives in the real schema file named under
  `## Stack` → **Schema file** in PROJECT_CONTEXT.md. Read that for built tables.
- **When a `[DB]` ticket is merged**, delete its rows here: the schema now holds them.
- VanPM updates this file in the same change as the spec that plans a column.
  `projects/_tools/spec_index.py` lists it in `specs/_index.md`.

## Decisions
<!-- One line per modelling decision, with date. e.g. "An album is an `events` row (2026-09-19)". -->

## Planned changes
<!-- One table per table touched. Remove rows once merged. -->

### `<table>` (new | existing)
| Column | Type | Planned by (exact ticket title, spec file) |
|---|---|---|

## Not owned by any spec yet
<!-- Data the designs show that no ticket creates. Each is an open question for the user. -->
