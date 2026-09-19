# Planned data: fms-studio

What the tickets plan to add to the database and are **not built yet**, with
the ticket that owns each change. This is not the schema: once a `[DB]` ticket
is merged, delete its rows here (the Schema file in PROJECT_CONTEXT holds them).
Nothing is built yet (Stack: Database none yet), so every row below is planned.
Created 2026-09-19 after an audit found two ORM setups and an `albums` table
competing with `events`.

## Decisions

- **An album is an `events` row.** The UI says "album" (My Albums, Album Title)
  and the wizard says "event"; both are the same record. Drafts have
  `status = 'draft'`, published albums `status = 'published'`. There is no
  `albums` table. (Assumed 2026-09-19; confirm with Van.)
- One ORM setup for the project: `[DB] Basic Info: events table + migration`.

## Planned changes

### `events` (new)

| Column | Type | Planned by (exact ticket title, spec file) |
|---|---|---|
| id | UUID PK | [DB] Basic Info: events table + migration (event-creation-step-1) |
| owner_id | UUID | same |
| title | VARCHAR | same |
| description | VARCHAR(255) | same |
| location | VARCHAR | same |
| category | VARCHAR | same |
| start_date, end_date | DATE | same |
| status | VARCHAR `'draft' \| 'published'`, default `'draft'` | same |
| created_at, updated_at | TIMESTAMP | same |
| cover_image_id | UUID NULL | [DB] Look & Feel: add branding columns to events (event-creation-step-2) |
| font | VARCHAR NULL | same |
| theme_color | CHAR(7) NULL | same |
| privacy | VARCHAR NULL, CHECK in `public, hidden, link-only, restricted, password` | [DB] Step 3 Privacy: add privacy column to events (event-creation-step-3) |
| password_hash | VARCHAR NULL | [DB] Set password: Add password_hash column (event-creation-step-3-1-set-password) |
| is_starred | BOOLEAN, default false | [DB] My Albums: add is_starred and cover_urls columns to events (dashboard-my-albums) |
| cover_urls | TEXT[], default empty | same |

## Not owned by any spec yet (open questions)

- **users**: `owner_id` points at a user, but no spec creates users or auth.
  Endpoints currently stub the current user.
- **photos, downloads**: the Dashboard metrics (photos uploaded, attendee
  downloads, match rate, 6-month chart) count data no feature creates yet.
- **credits**: the credit balance shown in the top nav and Buy Credits has no
  table; see `buying-credits.md` (not pushed).
