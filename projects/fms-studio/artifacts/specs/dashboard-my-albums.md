# Spec: Dashboard My Albums

Source: Figma node 9794-3220. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Dashboard: My Albums view
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220
screenshots: specs/_figma/dashboard-my-albums/9794-3220.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220 · Lane: FEATURE

## User story
As an organizer, I want to see a dashboard of my created albums so that I can manage them, search through them, and quickly create a new one.

## In scope
- Dashboard layout frame (header, sidebar stubs)
- "My Albums" grid layout showing album cards
- "Create New Album" empty card action
- Album card component with a 3-image fan layout, title, and action icons (dots, share, star)
- Search text input filter
- Context menu popover on a card (Edit, Settings, Delete)

## Out of scope (do NOT build)
- Pagination or infinite scrolling
- The actual Edit, Settings, Delete, or Share workflows (just the UI buttons are in scope)
- "Top Up" / Credit purchasing workflow
- Global top navigation and full sidebar functionality (stub the visuals only)
- Real image processing/fanning (just display the provided cover arrays using standard CSS transforms)

## Acceptance criteria
- Given the organizer visits the dashboard, when the page loads, then they see their albums arranged in a grid, newest first.
- Given a user has no albums, when the grid loads, then only the "Create New Album" card is displayed.
- Given the user types "Nike" in the Search input, when the input fires, then only albums with "Nike" in the title remain in the grid.
- Given a user clicks the three-dots menu on a card, when it opens, then a popover appears with "Edit Album", "Settings", and "Delete Album".

## Technical notes
- Endpoint / schema: GET /api/albums?owner=me → returns `Array<{ id, title, coverUrls: string[], isStarred: boolean, createdAt: string }>`

## Depends on / blocks
- Depends on: none
- Blocks: Album Creation feature, Edit/Delete flows

## Test notes (how QA verifies)
- Run the [QA] scenario below to verify grid display, searching, and menu interactions.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] My Albums: add is_starred and cover_urls columns to events
lane: DB
parent: [Feature] Dashboard: My Albums view
priority: high
estimate_hours: 2

## Context
Parent: [Feature] Dashboard: My Albums view · Figma: none · Lane: DB

## User story
As a developer, I want the album card fields stored on `events`, so that My Albums can list them. An album in the UI is an `events` row (see `[DB] Basic Info: events table + migration`).

## In scope
- One migration adding to `events`: `is_starred` (BOOLEAN, NOT NULL, default false) and `cover_urls` (TEXT[] / JSON array of URLs for the fanned card, NOT NULL, default empty).

## Out of scope (do NOT build)
- A separate `albums` table
- ORM setup (done by `[DB] Basic Info: events table + migration`, Event Creation Step 1)
- A photos table or relations

## Acceptance criteria
- Given the Step 1 `events` migration has run, when this migration runs, then `events` has `is_starred` (default false) and `cover_urls` (default empty array).
- Given existing `events` rows, when this migration runs, then each row has `is_starred = false` and `cover_urls = []`.
- Given this migration has run, when it is rolled back, then both columns are removed and no other column changes.

## Technical notes
- Endpoint / schema: `events.is_starred BOOLEAN NOT NULL DEFAULT false`, `events.cover_urls` array of text, NOT NULL, default empty

## Depends on / blocks
- Depends on (other feature): [DB] Basic Info: events table + migration (Event Creation Step 1)
- Blocks: [BE] Albums: GET /api/albums?owner=me returns the caller's albums

## Test notes (how QA verifies)
- Run the migration up and down on a fresh database and inspect the `events` columns.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Migration runs up and down cleanly on a fresh database
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Albums: GET /api/albums?owner=me returns the caller's albums
lane: BE
parent: [Feature] Dashboard: My Albums view
priority: high
estimate_hours: 4
depends_on: [DB] My Albums: add is_starred and cover_urls columns to events

## Context
Parent: [Feature] Dashboard: My Albums view · Figma: none · Lane: BE

## User story
As a frontend application, I want to fetch the current user's albums so that I can display them in the dashboard grid.

## In scope
- A new endpoint `GET /api/albums` in the backend NestJS app
- Filtering by `owner=me` (mocking the user ID as "org-1" for now if auth isn't fully integrated)
- Sorting results descending by `created_at`

## Out of scope (do NOT build)
- Pagination
- Search logic on the backend (we will handle search client-side for this slice as per UI rules)
- Full Authentication middleware (use a stubbed current-user interceptor for now)

## Acceptance criteria
- Given the API is running, when a GET request is made to `/api/albums?owner=me`, then it returns a 200 OK with a JSON array of album objects.
- Given albums exist in the database for the user, when fetched, then the items are ordered with the newest `created_at` first.
- Given the album data, when returned, then each object matches the shape `{ id, title, coverUrls, isStarred, createdAt }`.

## Technical notes
- Data source: `events` rows where `owner_id` is the caller and `status = 'published'` (drafts belong to My Drafts). `coverUrls` = `cover_urls`, `isStarred` = `is_starred`.
- Endpoint / schema: GET /api/albums?owner=me → response `Array<{ id, title, coverUrls: string[], isStarred: boolean, createdAt: string }>`

## Depends on / blocks
- Depends on: [DB] My Albums: add is_starred and cover_urls columns to events
- Blocks: [FE] My Albums: wire grid and search to GET /api/albums

## Test notes (how QA verifies)
- Call the endpoint directly or via tests to verify the JSON structure and sorting.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test backend`)
- [ ] Lint and typecheck clean
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] My Albums: grid layout header and search controls
lane: FE
parent: [Feature] Dashboard: My Albums view
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220
screenshots: specs/_figma/dashboard-my-albums/9794-3220.png

## Context
Parent: [Feature] Dashboard: My Albums view · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220 · Lane: FE

## User story
As an organizer, I want to see the main layout of my dashboard so that I can orient myself, see the welcome message, and locate the search controls.

## In scope
- Page route `frontend/src/app/dashboard/page.tsx`
- Welcome header ("Good Morning, Dream Marathon Org!")
- Subheader ("My Albums", "Top Up +" orange pill button)
- Search input pill and "Filter by: All Albums" dropdown stub
- Grid container for album cards

## Out of scope (do NOT build)
- The actual Album Card implementation (handled in a separate ticket)
- Global layout wrappers (top nav / sidebar) - assume a basic container if global layout is missing, or stub them visually if needed, but focus on the page content.
- Connecting the search input to data (just build the UI state)

## Acceptance criteria
- Given the dashboard page renders, when viewed, then the text "Good Morning, Dream Marathon Org!" is visible.
- Given the subheader, when rendered, then a button labeled "Top Up" with a `+` icon is present and styled with the primary orange (#FF6100).
- Given the controls area, when rendered, then an input with placeholder "Search" and a search icon is visible.
- Given the controls area, when rendered, then a "Filter by:" text and a button showing "All Albums" with a `chevron-down` icon is visible.
- Given a viewport < 640px, when the grid container renders, then it is a 1-column grid; given 640-1024px, 2 columns; given > 1024px, 4 columns.

## Technical notes
- Mock or fixture for parallel work: static layout components.
- Breakpoints: mobile <640px 1 col; tablet 640-1024px 2 cols; desktop >1024px 4 cols.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] My Albums: album card component + context menu

## Test notes (how QA verifies)
- Verify the responsive grid breakpoints and presence of the exact text labels.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] My Albums: album card component + context menu
lane: FE
parent: [Feature] Dashboard: My Albums view
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220
screenshots: specs/_figma/dashboard-my-albums/9794-3220.png

## Context
Parent: [Feature] Dashboard: My Albums view · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220 · Lane: FE

## User story
As an organizer, I want to see my individual albums as cards and access their actions so that I can manage my events.

## In scope
- "Create New Album" empty-action card (`plus` icon, light grey background)
- Standard Album Card component
- Fanned 3-image layout using CSS transforms
- Card action buttons: 3-dots menu, share-2 icon, star icon (toggleable UI state)
- Popover context menu triggered by the 3-dots icon (Edit Album, Settings, Delete Album)

## Out of scope (do NOT build)
- Connecting the card actions to actual backend mutations
- Fetching real data (use a mock)

## Acceptance criteria
- Given the album grid, when an album is rendered, then it displays the album title (e.g., "Nike Run 2026") centered.
- Given the "Create New Album" card, when rendered, then it shows a large `plus` icon and the exact text "Create New\nAlbum".
- Given a standard album card, when the user clicks the 3-dots icon, then a popover opens showing "Edit Album", "Settings", and "Delete Album" with their respective icons (`edit`, `settings`, `trash-2`).
- Given the standard album card, when the user clicks the `star` icon, then it toggles visually to a filled state (`star-filled`).

## Technical notes
- Mock or fixture for parallel work: `mockAlbum = { id: '1', title: 'Nike Run 2026', coverUrls: ['url1', 'url2', 'url3'], isStarred: true }`

## Depends on / blocks
- Depends on: none
- Blocks: [FE] My Albums: wire grid and search to GET /api/albums

## Test notes (how QA verifies)
- Test the visual states of the card, the opening of the popover, and the toggling of the star icon.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] My Albums: wire grid and search to GET /api/albums
lane: FE
parent: [Feature] Dashboard: My Albums view
priority: high
estimate_hours: 3
depends_on: [FE] My Albums: grid layout header and search controls, [FE] My Albums: album card component + context menu, [BE] Albums: GET /api/albums?owner=me returns the caller's albums
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220
screenshots: specs/_figma/dashboard-my-albums/9794-3220.png

## Context
Parent: [Feature] Dashboard: My Albums view · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220 · Lane: FE

## User story
As an organizer, I want to see my actual album data and use the search bar to filter them.

## In scope
- Fetching data from `GET /api/albums?owner=me` on dashboard load
- Handling loading and error states for the grid
- Wiring the client-side search input to filter the fetched array by album `title`

## Out of scope (do NOT build)
- Server-side search or sorting
- Wiring the popover actions (Edit, Delete, Settings)

## Acceptance criteria
- Given the dashboard is loading data, when mounted, then a loading skeleton or indicator is shown in place of the grid.
- Given the API returns a 500 error, when fetching albums, then an error message is displayed and a retry button is available.
- Given the dashboard has loaded 3 albums, when the user types a term into the "Search" input, then the grid immediately updates to show only albums where the title contains the search term (case-insensitive).
- Given the dashboard has loaded data, when rendered, then the "Create New Album" card is always shown as the first item in the grid, regardless of search filters.

## Technical notes
- Endpoint / schema: GET /api/albums?owner=me

## Depends on / blocks
- Depends on: [FE] My Albums: grid layout header and search controls, [FE] My Albums: album card component + context menu, [BE] Albums: GET /api/albums?owner=me returns the caller's albums
- Blocks: [QA] My Albums: E2E organizer views dashboard and searches albums

## Test notes (how QA verifies)
- Verify search functionality works entirely client-side based on the fetched data.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] My Albums: E2E organizer views dashboard and searches albums
lane: QA
parent: [Feature] Dashboard: My Albums view
priority: high
estimate_hours: 3
depends_on: [FE] My Albums: wire grid and search to GET /api/albums

## Context
Parent: [Feature] Dashboard: My Albums view · Figma: none · Lane: QA

## User story
As a QA engineer, I want an end-to-end test that verifies the dashboard displays albums and filters them correctly.

## In scope
- Playwright E2E scenario covering the dashboard loading, grid display, and search interactions.

## Out of scope (do NOT build)
- Testing the actual creation or deletion flows (covered in other features).

## Acceptance criteria
- Given the application has a seeded user with 2 albums named "Nike Run 2026" and "Liberty Run Marathon", when the E2E test runs, then it logs in, navigates to the dashboard, and asserts that exactly 3 cards are visible ("Create New Album" + the 2 data cards).
- Given the seeded data, when the E2E test enters "Nike" into the "Search" field, then it asserts that only the "Create New Album" card and the "Nike Run 2026" card remain visible in the grid.
- Given an empty state (seeded user with 0 albums), when the E2E test runs, then it asserts that only the "Create New Album" card is visible in the grid.

## Technical notes
- Endpoint / schema: E2E setup

## Depends on / blocks
- Depends on: [FE] My Albums: wire grid and search to GET /api/albums
- Blocks: none

## Test notes (how QA verifies)
- Run `npx playwright test` to execute this specific scenario.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end
