# Spec: Event Creation Step 4 — Review & Create

Source: Figma node 9836-6900. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 4 — Review & Create
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation-step-4/9836-6900.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900 · Lane: FEATURE

## User story
As an organizer, I want to review all my event details in one place before finalizing, so that I can catch mistakes before the album goes live.

## In scope
- Step 4 of the event creation wizard (Review & Create)
- Displaying the finalized album cover preview
- Displaying a summary of Basic Info, Look & Feel, and Access settings
- Editing navigation (going back to change settings)
- Final creation submission to the backend

## Out of scope (do NOT build)
- The actual live album view (that is a separate feature)
- PDF/Export of the summary
- Modifying values directly on this screen (must use the Edit/Back buttons)

## Acceptance criteria
- Given the organizer is on step 4, when the screen loads, then the summary shows the draft values for Title, Description, Date, Location, Category, Font, Theme, and Privacy.
- Given the album cover preview, when the user clicks 'View Preview', then the Event preview modal from Step 2.1 opens for this draft.
- Given the summary section, when the user clicks the 'Edit' button, then the wizard navigates back to Step 1 with the draft values filled in.
- Given the modal header, when the user clicks the 'x' close icon, then the wizard closes, the draft stays saved (every step already saved it), and the user lands on `/dashboard`.
- Given all details are correct, when the user clicks 'Create ->', then `POST /api/events/:id/publish` is called, the event's `status` becomes `'published'`, and the user is redirected to `/dashboard`.

## Technical notes
- Files/paths: frontend/src/app/events/new/step-4/ · backend/src/app/events/
- Endpoint: `POST /api/events/:id/publish` (built by `[BE] Review & Create: POST /api/events/:id/publish`).

## Depends on / blocks
- Depends on: Event Creation Steps 1, 2, 3
- Blocks: Live Album Viewing

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Review & Create: layout and data mapping
lane: FE
parent: [Feature] Event Creation: Step 4 — Review & Create
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation-step-4/9836-6900.png

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900 · Lane: FE

## User story
As an organizer, I want to see a clear summary of my album settings so I can verify them before creating.

## In scope
- Page route for Step 4
- Progress indicator showing step 4 active
- Album cover preview with dashed border, gradient, title overlay, and 'View Preview' button
- Right column data summary for Basic Info, Look & Feel, and Access
- 'Edit' button and 'Create ->' button
- 'x' close icon in header

## Out of scope (do NOT build)
- Calling the finalize API (wiring ticket)
- Live album implementation

## Acceptance criteria
- Given the screen renders, when the progress indicator is shown, then steps 1, 2, 3, and 4 are rendered as active (orange).
- Given the header, when clicked, then the 'x' close icon triggers the modal close action.
- Given the left column, when rendered, then the album cover preview shows the uploaded image, a bottom gradient, the album title in the chosen font ("Aethan and Kianna’s Wedding 2026"), and a 'View Preview' button.
- Given the right column summary, when rendered, then 'Album Title', 'Description', 'Event Date', 'Location', and 'Category' map to their respective draft values.
- Given the right column summary, when rendered, then 'Album Font' and 'Album Theme' map to the draft values.
- Given the right column summary, when rendered, then 'Privacy and Access' maps to the draft value (e.g., 'Password Protected').
- Given the summary section, when the 'Edit' button is clicked, then the user is navigated to the appropriate previous step.
- Given the empty state for optional fields (like Description), when the value is missing, then a '-' is displayed.

## Technical notes
- Component mapping: Build the summary list as a reusable definition list or grid.
- Mock: Pass a complete draft object to the page component for parallel development.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Review & Create: wire Create to API

## Test notes (how QA verifies)
- Component tests verifying all fields render the provided mock data correctly, including the '-' fallback for empty description.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Review & Create: POST /api/events/:id/publish
lane: BE
parent: [Feature] Event Creation: Step 4 — Review & Create
priority: high
estimate_hours: 3

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: none · Lane: BE

## User story
As an organizer, I want 'Create' to publish my draft, so that my album goes live.

## In scope
- Endpoint `POST /api/events/:id/publish` for the caller's own draft
- Sets `events.status` from `'draft'` to `'published'` and updates `updated_at`
- Returns the updated event

## Out of scope (do NOT build)
- Checking fields other than `title` (Steps 1-3 validate their own fields)
- Unpublishing or deleting
- Enforcing privacy or password on album reads (separate feature)

## Acceptance criteria
- Given the caller owns a draft with a title, when `POST /api/events/:id/publish` is called, then it returns 200 with the event and `status: "published"`, and the row's `status` is `'published'`.
- Given the id does not exist or belongs to another user, when the endpoint is called, then it returns 404 and no row changes.
- Given the event is already published, when the endpoint is called, then it returns 409 and the row is unchanged.
- Given the draft has no title, when the endpoint is called, then it returns 400 with a validation message and `status` stays `'draft'`.

## Technical notes
- Endpoint / schema: POST /api/events/:id/publish → 200 `{ id, title, status, updatedAt }` · 400 · 404 · 409
- Uses the `status` column from `[DB] Basic Info: events table + migration` (Event Creation Step 1); no migration needed here.

## Depends on / blocks
- Depends on (other feature): [DB] Basic Info: events table + migration (Event Creation Step 1)
- Blocks: [FE] Review & Create: wire Create to API

## Test notes (how QA verifies)
- Backend integration tests for the 200, 400, 404 and 409 cases.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit/integration tests added and green (`npx nx test backend`)
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Review & Create: wire Create to API
lane: FE
parent: [Feature] Event Creation: Step 4 — Review & Create
estimate_hours: 3
depends_on: [FE] Review & Create: layout and data mapping, [BE] Review & Create: POST /api/events/:id/publish
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation-step-4/9836-6900.png

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900 · Lane: FE

## User story
As an organizer, I want the 'Create ->' button to actually save my event and make it ready.

## In scope
- Wiring the 'Create ->' button to `POST /api/events/:id/publish`
- Loading state on the Create button while the request is pending
- Error handling if the creation fails
- Redirect to `/dashboard` on success

## Out of scope (do NOT build)
- Backend implementation

## Acceptance criteria
- Given the step 4 screen, when the user clicks 'Create ->', then the button shows a loading state and `POST /api/events/:id/publish` is called.
- Given a successful API response, when the call completes, then the user is redirected to `/dashboard`.
- Given an API error (5xx/4xx), when the call fails, then an error message is displayed and the user remains on step 4.

## Technical notes
- Ensure the API client is used correctly to finalize the draft.

## Depends on / blocks
- Depends on: [FE] Review & Create: layout and data mapping, [BE] Review & Create: POST /api/events/:id/publish

## Test notes (how QA verifies)
- Verify network calls and loading states.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] PR reviewed
---end

---ticket
title: [QA] Review & Create: E2E organizer reviews and finalizes event
lane: QA
parent: [Feature] Event Creation: Step 4 — Review & Create
estimate_hours: 3
depends_on: [FE] Review & Create: wire Create to API

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Lane: QA

## User story
As a QA engineer, I want to ensure the entire review and create flow works end-to-end.

## In scope
- Playwright E2E test covering the step 4 screen rendering, data validation, and successful creation.

## Out of scope (do NOT build)
- Unit tests

## Acceptance criteria
- Given the E2E runner, when the step 4 test executes, then it navigates to the review screen with a mocked draft.
- Given the review screen is loaded, when the test inspects the summary, then it asserts the displayed data matches the mocked draft values.
- Given the summary is verified, when the test clicks Create, then it asserts the API call is made and the success redirect occurs.

## Technical notes
- Add to the existing Playwright suite.

## Depends on / blocks
- Depends on: [FE] Review & Create: wire Create to API

## Test notes (how QA verifies)
- Test runs green in CI.

## Definition of done
- [ ] Test written and passes locally and in CI
---end
