# Spec: Dashboard Screens

Source: Figma nodes 9794-3220, 9794-6008, 9794-6547.

---ticket
title: [Feature] Dashboard: Organizer overview, albums, and drafts
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008,https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220,https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547
screenshots: specs/_figma/dashboard-screens/9794-6008.png,specs/_figma/dashboard-screens/9794-3220.png,specs/_figma/dashboard-screens/9794-6547.png

## Context
Parent: this is the parent · Figma: Dashboard, My Albums, My Drafts · Lane: FEATURE

## User story
As an event organizer, I want to see a summary of my credit usage and event performance, view all my active albums, and manage draft albums so that I can successfully deliver photos to attendees and monitor my account balance.

## In scope
- Shared navigation sidebar and top header (branding, credits badge, buy credits button, user profile).
- Dashboard Overview screen (credit balance widget, 4 KPI stat cards, most downloaded marathon highlight, 6-month upload chart).
- My Albums screen (album grid, search, filter, album context menu).
- My Drafts screen (draft grid, search).
- Create New Album entry point (static card leading to future creation flow).

## Out of scope
- The actual album creation wizard/flow (only the entry point card is in scope).
- The payment/checkout flow for "Buy Credits" or "Top Up" (these should route to a placeholder or future billing view).
- The detailed album management/editing screen (clicking an album card navigates to a placeholder or future route).
- Real-time websocket updates for stats (standard API polling/refresh is sufficient).
- User profile settings screen (only the dropdown UI is in scope).
- Search and filtering logic for millions of records (basic pagination/filtering is enough for MVP).

## Acceptance criteria
- Given I am logged in, when I visit the root path `/`, then I am redirected to the Dashboard overview (`/dashboard`).
- Given I am on any dashboard screen, when I view the sidebar, then I see navigation icons for Overview, Albums, Drafts, and Settings.
- Given I am on the Overview screen, when I check my credit balance, then I see my exact remaining credits, used credits, and a visual progress bar.
- Given I am on the Overview screen, when I look at the stats, then I see 4 KPI cards (Albums Total, Photos Uploaded, Attendee Downloads, Match Rate) and a 6-month upload chart.
- Given I am on the My Albums screen, when I view the grid, then I see published albums with their cover image, title, and a 3-dot context menu for Edit/Settings/Delete.
- Given I am on the My Drafts screen, when I view the grid, then I see unpublished albums with placeholder styling.

## Technical notes
- This is the entry feature, so it includes DB setup for Users and Albums.

## Depends on / blocks
- Depends on: none
- Blocks: Future Album Creation flows

## Test notes
- Run the [QA] E2E scenario.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Setup: Users Albums and Credits tables
lane: DB
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: high
estimate_hours: 6

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Lane: DB

## User story
As an engineer, I need the database schema to exist so the dashboard endpoints can read and calculate stats.

## In scope
- Setup ORM (Prisma or TypeORM) for the NestJS backend as this is the first feature to persist data.
- User/Organization table with `creditsBalance` and `creditsUsed` integer columns.
- Album table with `id`, `title`, `status` (enum: DRAFT, PUBLISHED), `coverImageUrl`, `downloadsCount`, `photosCount`, `matchRate` and `createdAt`.
- First migration.

## Out of scope
- Detailed photo asset tables (only aggregates on the Album table for now).
- Authentication provider setup (assume mock user for now).

## Acceptance criteria
- Given the database is empty, when migrations run, then the ORM is installed and configured in the NestJS backend.
- Given the migration, when it completes, then a User table exists with credit columns.
- Given the migration, when it completes, then an Album table exists with the specified columns and an enum for status.
- Given the schema, when I inspect it, then a relation exists linking Albums to the User/Organization.

## Technical notes
- Stack: NestJS, Vitest. Choose Prisma or TypeORM and document it in the PR.
- Add seed data for the dashboard to render properly during dev.

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Dashboard: Overview stats endpoint, [BE] Albums: List and filter endpoints

## Test notes
- Verify migrations run on a clean DB.

## Definition of done
- [ ] Schema created and migrations generate successfully.
- [ ] Seed script works.
---end

---ticket
title: [BE] Dashboard: Overview stats endpoint
lane: BE
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: high
estimate_hours: 4
depends_on: [DB] Setup: Users Albums and Credits tables

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Lane: BE

## User story
As an organizer, I want the backend to calculate my stats so the frontend can display them accurately.

## In scope
- Endpoint `GET /api/dashboard/overview`
- Calculate credits, KPI stats, most downloaded album, and 6-month upload history based on DB data.

## Out of scope
- Real-time updates.

## Acceptance criteria
- Given a valid session, when a GET request is made to `/api/dashboard/overview`, then it returns a JSON object.
- Given the overview response, when I inspect the payload, then it contains a `credits` object (total, used, remaining).
- Given the overview response, when I inspect the payload, then it contains `stats` (albumsTotal, photosUploaded, downloads, matchRate).
- Given the overview response, when I inspect the payload, then it contains `mostDownloaded` (event details) and `uploadHistory` (6 months of data points).

## Technical notes
- Ensure the 6-month aggregation groups correctly by month.

## Depends on / blocks
- Depends on: [DB] Setup: Users, Albums, and Credits tables
- Blocks: [FE] Dashboard: Overview screen and widgets

## Test notes
- Unit tests for aggregation logic.

## Definition of done
- [ ] Endpoint implemented and tested.
---end

---ticket
title: [BE] Albums: List and filter endpoints
lane: BE
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: high
estimate_hours: 4
depends_on: [DB] Setup: Users Albums and Credits tables

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Lane: BE

## User story
As an organizer, I want to fetch my albums and drafts so I can manage them.

## In scope
- Endpoints `GET /api/albums` (published) and `GET /api/albums/drafts` (drafts).
- Query parameter filtering for title (`search`).

## Out of scope
- Advanced filtering beyond search.

## Acceptance criteria
- Given a valid session, when a GET request is made to `/api/albums`, then it returns a paginated list of published albums.
- Given a valid session, when a GET request is made to `/api/albums/drafts`, then it returns a paginated list of draft albums.
- Given the GET `/api/albums` request, when I pass a `search` query parameter, then the results are filtered by album title (case-insensitive).

## Technical notes
- Default pagination limit: 20.

## Depends on / blocks
- Depends on: [DB] Setup: Users, Albums, and Credits tables
- Blocks: [FE] Albums: My Albums grid and context menu, [FE] Albums: My Drafts grid

## Test notes
- Test filtering with partial string matches.

## Definition of done
- [ ] Endpoints implemented and tested.
---end

---ticket
title: [FE] Shared: Dashboard layout and navigation
lane: FE
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008
screenshots: specs/_figma/dashboard-screens/9794-6008.png

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Figma: Dashboard · Lane: FE

## User story
As an organizer, I want a consistent sidebar and header so I can navigate the application.

## In scope
- App layout (`frontend/src/app/(dashboard)/layout.tsx`).
- Left sidebar with navigation links (Overview, Albums, Drafts, Settings).
- Top header with dynamic credit badge, "Buy Credits" button, and user dropdown shell.

## Out of scope
- Clicking settings/buy credits opens actual flows (use dummy links/placeholders).

## Acceptance criteria
- Given the application loads, when I view the layout, then a persistent left sidebar is rendered containing the logo and 4 navigation icons (album, dashboard, pen, settings).
- Given the top header, when I view my credits, then an orange badge shows "420 Credits" (or current balance from API/mock) and a "Buy Credits" button.
- Given the top header, when I view the right side, then my avatar and a dropdown chevron are visible.
- Given the sidebar, when I click the dashboard icon, then the URL changes to `/dashboard` and the Overview screen renders.
- Given the sidebar, when I click the album icon, then the URL changes to `/albums` and the My Albums screen renders.
- Given the sidebar, when I click the pen icon, then the URL changes to `/drafts` and the My Drafts screen renders.

## Technical notes
- Use Next.js 15 App router layouts.
- Integrate with the provided Figma components.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes
- Component tests for active navigation states.

## Definition of done
- [ ] Layout implemented and tested.
---end

---ticket
title: [FE] Dashboard: Overview screen and widgets
lane: FE
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: high
estimate_hours: 8
depends_on: [BE] Dashboard: Overview stats endpoint, [FE] Shared: Dashboard layout and navigation
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008
screenshots: specs/_figma/dashboard-screens/9794-6008.png

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Figma: Dashboard · Lane: FE

## User story
As an organizer, I want to see a visual summary of my credits and performance.

## In scope
- Page route `/dashboard`.
- Credit balance widget with progress bar.
- 4 KPI stat cards.
- Most downloaded album highlight widget.
- 6-month bar chart for uploads.
- Wiring to `/api/dashboard/overview`.

## Out of scope
- Interactivity on the bar chart (static rendering is fine).

## Acceptance criteria
- Given I am on `/dashboard`, when the page loads, then the heading "My Overview" and "Good Morning, [Name]!" are visible.
- Given the Credit Balance widget, when it renders, then it displays "4,320" (credits left) and "2,680 used this month · out of 7,000 loaded" based on API data.
- Given the Credit Balance widget, when it renders, then a progress bar shows the ratio of used to total credits.
- Given the stats section, when it renders, then 4 cards appear: "Albums Total", "Photos Uploaded", "Attendee Downloads", and "Match Rate".
- Given the Most Downloaded widget, when it renders, then it shows the title, download count, and a preview image of the top event.
- Given the Photos Uploaded chart, when it renders, then a 6-month bar chart is displayed with the current month highlighted in orange.

## Technical notes
- You can use a lightweight charting library or CSS for the 6-month bar chart.

## Depends on / blocks
- Depends on: [BE] Dashboard: Overview stats endpoint, [FE] Shared: Dashboard layout and navigation
- Blocks: none

## Test notes
- Ensure the progress bar calculation handles 0 credits without dividing by zero.

## Definition of done
- [ ] Page implemented and wired to API.
---end

---ticket
title: [FE] Albums: My Albums grid and context menu
lane: FE
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: high
estimate_hours: 7
depends_on: [BE] Albums: List and filter endpoints, [FE] Shared: Dashboard layout and navigation
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220
screenshots: specs/_figma/dashboard-screens/9794-3220.png

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Figma: My Albums · Lane: FE

## User story
As an organizer, I want to see my published albums and manage them via a menu.

## In scope
- Page route `/albums`.
- Albums grid layout.
- Search and filter UI elements.
- "Create New Album" static card.
- Album card component with a 3-dot context menu overlay.
- Wiring to `GET /api/albums`.

## Out of scope
- Filter dropdown logic beyond the UI shell (API only supports search for now).

## Acceptance criteria
- Given I am on `/albums`, when the page loads, then the heading "My Albums" and a "Top Up" button are visible.
- Given the Albums screen, when it renders, then a search input with placeholder "Search" and a "Filter by: All Albums" dropdown are visible.
- Given the Albums grid, when it renders, then the first card is a "Create New Album" action card with a plus icon.
- Given the Albums grid, when it renders, then a list of album cards is displayed showing cover images and titles.
- Given an album card, when I click the 3-dot menu, then a popover opens showing "Edit Album", "Settings", and "Delete Album" with respective icons.
- Given an album card, when I view the top right, then a star icon indicates favorite status.
- Given the search input, when I type a term, then it debounces and fetches filtered results.

## Technical notes
- Context menu popover should handle click-outside to close.

## Depends on / blocks
- Depends on: [BE] Albums: List and filter endpoints, [FE] Shared: Dashboard layout and navigation
- Blocks: none

## Test notes
- Component test for context menu popover behavior.

## Definition of done
- [ ] Grid and menu implemented and wired.
---end

---ticket
title: [FE] Albums: My Drafts grid
lane: FE
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: normal
estimate_hours: 5
depends_on: [BE] Albums: List and filter endpoints, [FE] Shared: Dashboard layout and navigation
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547
screenshots: specs/_figma/dashboard-screens/9794-6547.png

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Figma: My Drafts · Lane: FE

## User story
As an organizer, I want to view my draft albums separated from published ones.

## In scope
- Page route `/drafts`.
- Drafts grid reusing the album card layout but with draft styling (placeholder images/grey overlays).
- "Create New Album" static card.
- Wiring to `GET /api/albums/drafts`.

## Out of scope
- Clicking Publish does anything (placeholder for now).

## Acceptance criteria
- Given I am on `/drafts`, when the page loads, then the heading "My Drafts" and a search input are visible.
- Given the Drafts grid, when it renders, then the first card is a "Create New Album" action card.
- Given the Drafts grid, when it renders, then draft cards display with placeholder/grey overlay styling.
- Given a draft card, when I hover or view it, then a "Publish" action is visible (based on design).

## Technical notes
- Reuse components from My Albums where possible.

## Depends on / blocks
- Depends on: [BE] Albums: List and filter endpoints, [FE] Shared: Dashboard layout and navigation
- Blocks: none

## Test notes
- Visual differentiation test for draft vs published states.

## Definition of done
- [ ] Drafts grid implemented and wired.
---end

---ticket
title: [QA] Dashboard E2E flows
lane: QA
parent: [Feature] Dashboard: Organizer overview, albums, and drafts
priority: high
estimate_hours: 4
depends_on: [FE] Dashboard: Overview screen and widgets, [FE] Albums: My Albums grid and context menu, [FE] Albums: My Drafts grid

## Context
Parent: [Feature] Dashboard: Organizer overview, albums, and drafts · Lane: QA

## User story
As a QA engineer, I want to ensure the critical paths of the dashboard work end-to-end.

## In scope
- Playwright E2E tests for dashboard navigation, widgets, and album grid features.
- If Playwright is not yet set up, this ticket includes adding the `playwright` package and initial config.

## Out of scope
- Testing external Figma integration.

## Acceptance criteria
- Given the application, when playwright tests run, then they verify navigation between Overview, Albums, and Drafts via the sidebar.
- Given the application, when playwright tests run, then they verify the Overview credit balance widget displays calculated data correctly.
- Given the application, when playwright tests run, then they verify the album context menu opens and displays the 3 required actions.
- Given the application, when playwright tests run, then they verify typing in the search bar triggers a filtered request for albums.

## Technical notes
- Tests go in `frontend/e2e/`.

## Depends on / blocks
- Depends on: all FE tickets
- Blocks: none

## Test notes
- Tests must pass in CI.

## Definition of done
- [ ] E2E tests written and passing.
---end
