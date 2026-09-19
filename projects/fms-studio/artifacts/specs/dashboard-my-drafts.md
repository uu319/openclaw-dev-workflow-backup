# Spec: Dashboard — My Drafts

Source: Figma node 9794-6547. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Dashboard: My Drafts
lane: FEATURE
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547
screenshots: specs/_figma/dashboard-my-drafts/9794-6547.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547 · Lane: FEATURE

## User story
As an organizer, I want to see a dashboard with my draft events and credits, so that I can easily create new albums or manage my drafts.

## In scope
- Dashboard layout including the top navigation bar and left sidebar
- Greeting using the organizer's name
- Display of available credits
- "My Drafts" grid with a "Create New Album" card and cards for existing drafts
- Cards for drafts displaying the title and a "Publish" button

## Out of scope (do NOT build)
- Searching functionality (mock the input for now)
- "Top Up +" flow
- "Buy Credits" flow
- Publish action (it just routes to the publish wizard for now)
- Settings, Album, or Square Pen left navigation routes
- Profile dropdown interactions

## Acceptance criteria
- Given the user is authenticated, when they navigate to `/dashboard`, then the dashboard renders with their name in "Good Morning, [Name]!" and their credit balance in the header.
- Given there are draft events, when the dashboard loads, then the "My Drafts" section renders a "Create New Album" card first, followed by a card for each draft event.
- Given a draft event card, when the user views it, then the event title, placeholder image, a three-dot menu, and a "Publish" button are visible.
- Given the "Create New Album" card, when clicked, then the application navigates to the event creation flow.

## Technical notes
- Endpoint / schema: `GET /api/dashboard` returning `{ user: { name }, credits: number, drafts: [{ id, title, image }] }`

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Login as an organizer with at least one draft. Navigate to dashboard. Verify layout, greeting, credits, and draft cards. Click "Create New Album" and verify routing.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Dashboard: My Drafts Section
lane: FE
parent: [Feature] Dashboard: My Drafts
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547
screenshots: specs/_figma/dashboard-my-drafts/9794-6547.png

## Context
Parent: [Feature] Dashboard: My Drafts · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547 · Lane: FE

## User story
As an organizer, I want to see my drafts and create new albums on the dashboard.

## In scope
- Page header with "Good Morning, [Name]!" and "Search" input
- "My Drafts" section header with "Top Up +" button
- Drafts grid
- "Create New Album" card
- Draft cards with title, placeholder image, "Publish" button, and three-dot menu

## Out of scope (do NOT build)
- Search filtering logic
- "Top Up +" action
- Real image fetching (use placeholder)

## Acceptance criteria
- Given the dashboard content area, when it renders, then the header text shows "Good Morning, Dream Marathon Org!" (using the mock user name) and a search input with placeholder "Search" is visible.
- Given the "My Drafts" section, when it renders, then a "Top Up +" button is visible.
- Given the drafts grid, when it renders, then the first card is a light grey square with a plus icon and the text "Create New Album".
- Given the user has drafts, when the grid renders, then cards for each draft show the title (e.g. "Nike Run 2026"), an image placeholder, a three-dot menu in the top left, and a "Publish" button.
- Given the "Create New Album" card, when clicked, then the app navigates to `/events/new`.
- Given the "Publish" button on a draft card, when clicked, then the app opens Step 4 (Review & Create) of the event creation wizard for that draft.

## Technical notes
- Mock or fixture for parallel work: `user = { name: "Dream Marathon Org" }`, `drafts = [{ id: '1', title: 'Nike Run 2026' }, { id: '2', title: 'Fun Run Marathon' }]`

## Depends on / blocks
- Depends on (other feature): [FE] Dashboard: layout + static components (Dashboard: Organizer Dashboard builds the shared top nav and sidebar)
- Blocks: [FE] Dashboard: API Wiring

## Test notes (how QA verifies)
- Load dashboard. Verify text, search input, "Top Up +" button. Verify "Create New Album" card routes correctly. Verify draft cards display correct information and "Publish" button routes correctly.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR opened and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Dashboard: GET /api/dashboard returns user and drafts
lane: BE
parent: [Feature] Dashboard: My Drafts
estimate_hours: 5

## Context
Parent: [Feature] Dashboard: My Drafts · Figma: none · Lane: BE

## User story
As an organizer, I want the dashboard to load my specific drafts and credits so that I see my own data.

## In scope
- Endpoint `GET /api/dashboard`
- Fetching user details (name, credits)
- Fetching draft events for the user: `events` rows where `owner_id` is the caller and `status = 'draft'`

## Out of scope (do NOT build)
- Pagination for drafts (assume all fit or return top N for now)
- Published events

## Acceptance criteria
- Given an authenticated user with drafts, when `GET /api/dashboard` is called, then it returns 200 with `{ user: { name, credits }, drafts: [{ id, title, ... }] }`.
- Given an authenticated user with no drafts, when `GET /api/dashboard` is called, then it returns 200 with `{ user: { name, credits }, drafts: [] }`.
- Given an unauthenticated request, when `GET /api/dashboard` is called, then it returns 401.

## Technical notes
- Endpoint / schema: `GET /api/dashboard` -> 200 `{ user: { name: string, credits: number }, drafts: { id: string, title: string }[] }`

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Dashboard: API Wiring

## Test notes (how QA verifies)
- Call endpoint with and without drafts.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR opened and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Dashboard: API Wiring
lane: FE
parent: [Feature] Dashboard: My Drafts
estimate_hours: 3
depends_on: [FE] Dashboard: My Drafts Section, [BE] Dashboard: GET /api/dashboard returns user and drafts
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547
screenshots: specs/_figma/dashboard-my-drafts/9794-6547.png

## Context
Parent: [Feature] Dashboard: My Drafts · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547 · Lane: FE

## User story
As an organizer, I want to see my actual data on the dashboard.

## In scope
- Connect dashboard page to `GET /api/dashboard`
- Loading and error states

## Out of scope (do NOT build)
- Retries or complex caching

## Acceptance criteria
- Given the dashboard is loading, when data is fetched, then a loading skeleton or spinner is visible.
- Given a successful fetch, when the data returns, then the layout and drafts section populate with the real user name, credits, and draft events.
- Given the API returns a 5xx error, when the page loads, then a generic error message "Could not load dashboard" is shown.

## Technical notes
- Integrate with data fetching library (e.g. SWR, React Query, or Next.js server components).

## Depends on / blocks
- Depends on: [FE] Dashboard: My Drafts Section, [BE] Dashboard: GET /api/dashboard returns user and drafts
- Blocks: [QA] Dashboard: E2E View My Drafts

## Test notes (how QA verifies)
- Load dashboard, verify real data appears. Mock a 500 error, verify error state.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR opened and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Dashboard: E2E View My Drafts
lane: QA
parent: [Feature] Dashboard: My Drafts
estimate_hours: 3
depends_on: [FE] Dashboard: API Wiring

## Context
Parent: [Feature] Dashboard: My Drafts · Figma: none · Lane: QA

## User story
As an organizer, I want the dashboard to work flawlessly end-to-end.

## In scope
- E2E test for the dashboard

## Out of scope (do NOT build)
- Visual regression testing

## Acceptance criteria
- Given the E2E suite runs, when the dashboard test executes, then it logs in and navigates to `/dashboard`.
- Given the test is on the dashboard, when checking the header, then the greeting, credits, and "Dashboard" link are verified.
- Given the test is on the dashboard, when checking the "My Drafts" grid, then the "Create New Album" card and at least one existing draft card (with a "Publish" button) are verified.

## Technical notes
- Playwright test in the project's E2E suite (runner set up by `[INT] Setup Playwright E2E runner`, Event Creation Step 1).

## Depends on / blocks
- Depends on: [FE] Dashboard: API Wiring
- Blocks: none

## Test notes (how QA verifies)
- Run `npx playwright test`.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR opened and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end