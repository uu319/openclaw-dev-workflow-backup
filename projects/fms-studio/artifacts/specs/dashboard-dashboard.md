# Spec: Dashboard

Source: Figma node 9794-6008. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Dashboard: Organizer Dashboard
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008
screenshots: specs/_figma/dashboard-dashboard/9794-6008.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008 · Lane: FEATURE

## User story
As an organizer, I want a dashboard showing my credit usage and event performance metrics, so that I can monitor activity and know when to top up.

## In scope
- Top navigation with credit balance and Buy Credits CTA
- Left sidebar navigation structure
- Main overview area with greeting
- Credit balance card with usage bar and Top Up button
- Four stat cards (Albums, Photos, Downloads, Match Rate)
- Most downloaded event widget
- 6-month upload history chart

## Out of scope (do NOT build)
- User profile settings drop-down interactions
- Implementing the "Buy Credits" / "Top Up" flow (separate feature)
- Interactive tooltips on the chart
- Responsive mobile menu interactions (if complex, stick to basic hiding/stacking per standard breakpoints)
- Real time live-updating

## Acceptance criteria
- Given the organizer accesses `/dashboard`, when the page loads, then they see their organization name in the greeting ("Good Morning, [Org Name]!").
- Given the dashboard loads, when data is fetched, then the credit balance, usage text, and progress bar reflect the organizer's current credit usage and limits.
- Given the dashboard loads, when data is fetched, then the four stat cards display correct aggregated totals for Albums, Photos Uploaded, Downloads, and Match Rate.
- Given the dashboard loads, when data is fetched, then the Most Downloaded widget displays the details and cover of the organizer's top event.
- Given the dashboard loads, when data is fetched, then the bar chart displays the last 6 months of photo upload counts, with the current month highlighted.

## Technical notes
- Endpoint / schema: `GET /api/dashboard/overview` → `{ greetingName, credits: { left, used, total }, stats: { albums, photos, downloads, matchRate }, topEvent: { title, downloads, location, coverUrl }, chart: [{ month, count }] }`
- Mock or fixture for parallel work: Hardcode a JSON fixture matching the schema for initial FE work.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Dashboard: read models for metrics (if missing)
lane: DB
parent: [Feature] Dashboard: Organizer Dashboard
priority: normal
estimate_hours: 4

## Context
Parent: [Feature] Dashboard: Organizer Dashboard · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008 · Lane: DB

## User story
As a developer, I want queries or views to efficiently aggregate dashboard metrics, so that the dashboard loads quickly.

## In scope
- Ensure necessary DB indexes exist for counting albums, photos, and downloads per organizer.
- (If using an ORM/query builder) Write the aggregation queries needed by the dashboard endpoint.

## Out of scope (do NOT build)
- Creating the core tables (Albums, Photos, Events) - these should be handled by their respective feature tickets. This ticket is just for read-aggregation logic/indexes.

## Acceptance criteria
- Given the database schema, when aggregating metrics for an organizer, then a query can efficiently return total albums, total photos, and total downloads.
- Given the database schema, when finding the top event, then a query can efficiently order events by download count and return the highest.
- Given the database schema, when charting 6 months of uploads, then a query can group photo creation timestamps by month for a given organizer.

## Technical notes
- Endpoint / schema: N/A - DB level
- Mock or fixture for parallel work: N/A

## Depends on / blocks
- Depends on: [DB] Setup ORM + events table (from previous project init)
- Blocks: [BE] Dashboard: GET /api/dashboard/overview returns aggregated metrics

## Test notes (how QA verifies)
- N/A (tested via BE integration)

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/dashboard-db` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [BE] Dashboard: GET /api/dashboard/overview returns aggregated metrics
lane: BE
parent: [Feature] Dashboard: Organizer Dashboard
priority: high
estimate_hours: 5
depends_on: [DB] Dashboard: read models for metrics (if missing)

## Context
Parent: [Feature] Dashboard: Organizer Dashboard · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008 · Lane: BE

## User story
As the dashboard UI, I want an endpoint that returns all required metrics in one call, so that I don't have to make multiple requests.

## In scope
- Implement `GET /api/dashboard/overview` endpoint.
- Secure endpoint to only return data for the authenticated organizer.
- Aggregate and return data matching the dashboard UI requirements.

## Out of scope (do NOT build)
- Complex analytics pipelines. Use basic SQL aggregations for MVP.

## Acceptance criteria
- Given an authenticated organizer, when `GET /api/dashboard/overview` is called, then it returns HTTP 200 with JSON containing `credits`, `stats`, `topEvent`, and `chart` data.
- Given an unauthenticated request, when the endpoint is called, then it returns HTTP 401.
- Given an organizer with no data (new account), when the endpoint is called, then it returns HTTP 200 with 0s for stats, null for topEvent, and an empty array for the chart.

## Technical notes
- Endpoint / schema: `GET /api/dashboard/overview`
- Mock or fixture for parallel work: N/A

## Depends on / blocks
- Depends on: [DB] Dashboard: read models for metrics (if missing)
- Blocks: [FE] Dashboard: wire overview endpoint

## Test notes (how QA verifies)
- Call endpoint with valid token, verify JSON structure.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/dashboard-api` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Dashboard: layout + static components
lane: FE
parent: [Feature] Dashboard: Organizer Dashboard
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008
screenshots: specs/_figma/dashboard-dashboard/9794-6008.png

## Context
Parent: [Feature] Dashboard: Organizer Dashboard · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008 · Lane: FE

## User story
As an organizer, I want to see the dashboard layout with all visual elements, so that I have a clear overview of my data.

## In scope
- Global layout shell (Top nav, Left sidebar).
- Overview page content area (`/dashboard`).
- Credit Balance widget.
- 4 Stat widgets.
- Most Downloaded widget.
- Chart widget (static CSS/HTML representation of the bars is fine for now, or a simple library).

## Out of scope (do NOT build)
- API wiring (fetching real data).
- Interactive charting features (tooltips, zooming).
- Routing for sidebar links (just make them look correct).

## Acceptance criteria
- Given the dashboard page, when rendered, then the top nav shows "Dashboard", a "420 Credits" pill, and a solid orange "Buy Credits" button.
- Given the dashboard page, when rendered, then the "Credit Balance" card displays a large number "4,320", text "credits left", and a "Top Up +" button.
- Given the dashboard page, when rendered, then four stat cards are visible with labels "Albums Total", "Photos Uploaded", "Attendee Downloads", and "Match Rate".
- Given the dashboard page, when rendered, then the "Most Downloaded Marathon" widget displays an image and text "Liberty Run Marathon 2026".
- Given the dashboard page, when rendered, then the "Photos Uploaded - Last 6 Months" chart shows 6 bars with the last bar ("Sepember") highlighted in orange.

## Technical notes
- Endpoint / schema: `GET /api/dashboard/overview` → `{ greetingName, credits: { left, used, total }, stats: { albums, photos, downloads, matchRate }, topEvent: { title, downloads, location, coverUrl }, chart: [{ month, count }] }`
- Mock or fixture for parallel work: Hardcode a JSON fixture matching the schema for initial FE work.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Dashboard: wire overview endpoint

## Test notes (how QA verifies)
- View the page and visually compare against Figma.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/dashboard-layout` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Dashboard: wire overview endpoint
lane: FE
parent: [Feature] Dashboard: Organizer Dashboard
priority: normal
estimate_hours: 3
depends_on: [FE] Dashboard: layout + static components, [BE] Dashboard: GET /api/dashboard/overview returns aggregated metrics
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008
screenshots: specs/_figma/dashboard-dashboard/9794-6008.png

## Context
Parent: [Feature] Dashboard: Organizer Dashboard · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008 · Lane: FE

## User story
As an organizer, I want my dashboard to show my actual data, so I can see my real metrics.

## In scope
- Fetch data from `GET /api/dashboard/overview`.
- Handle loading and error states for the dashboard.
- Populate all dashboard widgets with the fetched data.

## Out of scope (do NOT build)
- Real-time polling or websockets.

## Acceptance criteria
- Given the dashboard is loading, when the API request is in flight, then a loading skeleton or spinner is displayed.
- Given the API call fails, when the dashboard renders, then an error message is shown indicating data could not be loaded.
- Given the API call succeeds, when the dashboard renders, then the Top Nav credit pill, Credit Balance card, Stat cards, Most Downloaded event, and Chart all display the real data returned from the API.

## Technical notes
- Endpoint / schema: `GET /api/dashboard/overview`

## Depends on / blocks
- Depends on: [FE] Dashboard: layout + static components, [BE] Dashboard: GET /api/dashboard/overview returns aggregated metrics
- Blocks: [QA] Dashboard: E2E organizer views dashboard metrics

## Test notes (how QA verifies)
- Verify data shown matches DB state.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/dashboard-wiring` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [QA] Dashboard: E2E organizer views dashboard metrics
lane: QA
parent: [Feature] Dashboard: Organizer Dashboard
priority: normal
estimate_hours: 2
depends_on: [FE] Dashboard: wire overview endpoint

## Context
Parent: [Feature] Dashboard: Organizer Dashboard · Figma: N/A · Lane: QA

## User story
As a QA engineer, I want an automated test for the dashboard, so that we prevent regressions.

## In scope
- Playwright E2E test covering dashboard loading and data display.

## Out of scope (do NOT build)
- Testing the actual "Buy Credits" flow (that's a separate feature).

## Acceptance criteria
- Given a test organizer with known data, when the E2E test runs, then it logs in, navigates to `/dashboard`, and verifies that the displayed stats and credit balance match the seeded test data.
- Given a test organizer with no data, when the test runs, then it verifies the dashboard loads with 0s and empty states where appropriate.
- Given an unauthenticated session, when the E2E test attempts to visit `/dashboard`, then it verifies the user is redirected to the login page.

## Technical notes
- Endpoint / schema: N/A

## Depends on / blocks
- Depends on: [FE] Dashboard: wire overview endpoint
- Blocks: none

## Test notes (how QA verifies)
- Run `npx playwright test dashboard.spec.ts`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/dashboard-qa` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end
