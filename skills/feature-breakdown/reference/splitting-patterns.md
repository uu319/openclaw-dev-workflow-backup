# Splitting patterns, INVEST, and worked examples

## The "too big" test
A subtask is too big if it will take more than one developer-day (8h), or if
you cannot write its acceptance criteria without the word "and" joining two
different behaviours. Split it.

## INVEST (check every ticket)
- **I**ndependent — can be built without waiting, or its dependency is named
- **N**egotiable — describes the outcome, not the exact implementation, except where a path/endpoint must be fixed for other lanes
- **V**aluable — the parent has user value; a subtask's value is "unblocks the parent"
- **E**stimable — the coding agent can estimate it from the ticket alone
- **S**mall — ≤ 8h
- **T**estable — every AC is falsifiable

## Nine splitting patterns (Humanizing Work / Lawrence & Green)

| # | Pattern | Use when | Example |
|---|---|---|---|
| 1 | Workflow steps | Multi-step flow | Event creation → one feature per wizard step, then "preview" and "publish" as later features |
| 2 | Operations (CRUD) | "Manage X" | Manage albums → create album, rename album, delete album, list albums |
| 3 | Business-rule variations | Several rules for one goal | Event access → public, password, invite-only as three features |
| 4 | Data variations | Several data types | Upload photos → JPEG first, RAW/HEIC later |
| 5 | Data-entry methods | Fancy input | Date picker → plain input first, calendar widget later |
| 6 | Major effort | One story carries the infrastructure | First `[DB]` ticket sets up the ORM and the `events` table; later tickets add columns |
| 7 | Simple / complex | Core vs edge cases | Search albums by name first; filters and sorting as separate tickets |
| 8 | Defer performance | Works vs fast | List albums (any speed) first; pagination/virtualisation as its own ticket |
| 9 | Break out a spike | Unknown blocks estimation | `[SPIKE] Evaluate S3 vs Cloudflare R2 for photo storage` (≤ 4h, output is a written decision) |

Meta-rule: find the core complexity, list the variations, ship one thin
slice through the complexity first, then add variations as separate tickets.

## Lane decision table (read the project's `## Stack` section first; the rows assume a web frontend + API backend)

| Screen shows… | Lanes |
|---|---|
| Static content only (landing page, marketing) | FE, QA |
| A form that submits | FE (layout+states), FE (wiring), BE (endpoint), QA, DB if new fields persist |
| A list of the user's data | DB (if new), BE (list endpoint), FE (static + states), FE (wiring), QA |
| Login / signup / password | FE, BE, INT (auth), QA |
| File upload | FE, BE, INT (storage), QA |
| Anything the design doesn't answer | SPIKE, or a question to the user |

## Worked examples

### 1. `Organizer Flow: Landing Page No Account` (static marketing screen)
- `[Feature] Organizer landing: visitor without account sees value prop and CTA`
- `[FE] Landing (no account): hero, sections, footer per Figma 9731-3297` — 6h
- `[FE] Landing (no account): CTA routes to /signup, nav links, mobile menu` — 3h
- `[QA] Landing (no account): E2E visit /, see hero, click CTA, land on /signup` — 2h
- No BE/DB: nothing is submitted or read.

### 2. `Event Creation: Step 3.1 Set Password` (form + persistence + auth concern)
- `[Feature] Event Creation: Step 3.1 — Set event password`
- `[FE] Set password: form layout + validation states` — 6h, parallel
- `[BE] Set password: PATCH /api/events/:id/draft stores password hash` — 5h
- `[INT] Set password: hashing with bcrypt, never return the hash` — 2h (depends on BE ticket, or fold into BE if trivial)
- `[FE] Set password: wire Continue to PATCH /api/events/:id/draft` — 3h, depends on both FE-layout and BE
- `[QA] Set password: E2E organizer sets password and reaches step 4` — 3h, depends on all
- `[DB]` only if an `events.password_hash` column does not exist yet. In fms-studio nothing exists yet, so the **first** feature that persists anything gets a `[DB] Set up ORM + events table` ticket (pattern 6, major effort) and later features reference it as a dependency.

### 3. `Dashboard: My Albums` (list of user data)
- `[Feature] Dashboard: organizer sees their albums`
- `[DB] Albums: albums table (id, owner_id, title, cover_url, created_at) + migration` — 3h
- `[BE] Albums: GET /api/albums?owner=me returns the caller's albums newest first` — 4h, depends on DB
- `[FE] My Albums: grid layout + card component per Figma` — 5h, parallel (mock: array of `{ id, title, coverUrl, createdAt }`)
- `[FE] My Albums: loading skeleton, empty state ('No albums yet' + Create button), error state` — 3h, parallel
- `[FE] My Albums: wire grid to GET /api/albums` — 2h, depends on BE + both FE tickets
- `[QA] My Albums: E2E organizer with 0 and 3 albums sees empty state / 3 cards` — 3h
- Out of scope for all: pagination, search, sorting UI (pattern 7/8 → later tickets).
