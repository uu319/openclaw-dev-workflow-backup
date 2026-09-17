# Spec: Event Creation Step 2.1 Preview

Source: Figma node 9873-3730. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 2.1 — Preview event
lane: FEATURE
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730
screenshots: specs/_figma/event-creation-step-2-1-preview/9873-3730.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730 · Lane: FEATURE

## User story
As an organizer, I want to preview how my event will look to guests, so that I can ensure all details are correct before publishing.

## In scope
- Full-page preview of the guest view using event draft data
- "Preview Only" badge and floating "Close Preview" button
- Header section with cover, title, description, date, location, and category
- Photo grid toolbar (search, sort, face filters) and masonry photo grid

## Out of scope (do NOT build)
- Actual search, sort, or face filtering logic (UI only for preview)
- Photo downloading (UI only for preview)
- Global navigation bar (assume app shell provides it or it's out of scope for this specific step)

## Acceptance criteria
- Given the organizer is in the event creation flow, when they open the preview, then the guest view layout renders with the draft's cover image, title, description, date, location, and category.
- Given the preview is open, when the organizer clicks "Close Preview", then the preview closes and returns them to the event creation wizard.
- Given the preview is open, when the page loads, then a "Preview Only" badge is visible at the top right of the main content area.
- Given the preview is open, when the photo grid area renders, then the photo grid displays the uploaded draft photos (or empty state if none) and the toolbar shows "Search", "Sort by: Newest", and face filters.

## Technical notes
- None

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Event preview: overlay and header layout
lane: FE
parent: [Feature] Event Creation: Step 2.1 — Preview event
estimate_hours: 5
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730
screenshots: specs/_figma/event-creation-step-2-1-preview/9873-3730.png

## Context
Parent: [Feature] Event Creation: Step 2.1 — Preview event · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730 · Lane: FE

## User story
As an organizer, I want to see my event details exactly as guests will see them, so I can review my draft.

## In scope
- "Preview Only" badge and floating "Close Preview" button
- Header layout: Cover image, title, share icon, description, date, location, category

## Out of scope (do NOT build)
- Photo grid and toolbar (handled in separate ticket)
- Actual share functionality (UI only)
- Global navigation bar

## Acceptance criteria
- Given the preview renders, when the page loads, then a "Preview Only" badge is visible at the top right of the content area.
- Given the preview renders, when the page loads, then a floating "Close Preview" button with an 'x' icon is visible at the bottom right.
- Given the preview renders, when the "Close Preview" button is clicked, then the `onClose` callback is fired.
- Given draft data is provided, when the header renders, then the header renders the cover image, title, description, date (with `calendar` icon), location (with `map-pin` icon), and category (with `party-popper` icon).
- Given the header renders, when the page loads, then a share icon (`share-2`) is visible next to the title.

## Technical notes
- Mock or fixture for parallel work: `eventDraft: { title, description, date, location, category, coverUrl }`, `onClose: () => void`

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Event preview: wire to event draft

## Test notes (how QA verifies)
- Component tests for rendering the header with mock data and verifying the `onClose` callback on button click.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Event preview: toolbar and photo grid layout
lane: FE
parent: [Feature] Event Creation: Step 2.1 — Preview event
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730
screenshots: specs/_figma/event-creation-step-2-1-preview/9873-3730.png

## Context
Parent: [Feature] Event Creation: Step 2.1 — Preview event · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730 · Lane: FE

## User story
As an organizer, I want to preview how the photo grid and toolbar will look to guests.

## In scope
- Toolbar: Search input, Sort dropdown, photo count, face filters
- Masonry photo grid
- Photo hover state (download icon, maximize icon, photographer name, event tag)

## Out of scope (do NOT build)
- Actual search, sort, or filter functionality (UI only)
- Actual download or maximize functionality (UI only)

## Acceptance criteria
- Given the toolbar renders, when the page loads, then a search input with placeholder "Search" and a `search` icon is visible.
- Given the toolbar renders, when the page loads, then a sort dropdown showing "Sort by: Newest" and a `chevron-down` icon is visible.
- Given the toolbar renders, when the page loads, then the photo count (e.g., "1500 photos") and circular face filter avatars are visible.
- Given the photo grid component receives photos, when it renders, then the photos are displayed in a masonry layout.
- Given the photo grid is visible, when a user hovers over a photo, then the hover overlay appears showing the `download` icon, `maximize-2` icon, photographer name, and event tag.

## Technical notes
- Mock or fixture for parallel work: `photos: { id, url, photographer, eventTag }[]`

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Event preview: wire to event draft

## Test notes (how QA verifies)
- Component tests for rendering the toolbar and photo grid hover state.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Event preview: wire to event draft
lane: FE
parent: [Feature] Event Creation: Step 2.1 — Preview event
estimate_hours: 3
depends_on: [FE] Event preview: overlay and header layout, [FE] Event preview: toolbar and photo grid layout
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730
screenshots: specs/_figma/event-creation-step-2-1-preview/9873-3730.png

## Context
Parent: [Feature] Event Creation: Step 2.1 — Preview event · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730 · Lane: FE

## User story
As an organizer, I want the preview to show the actual data I have entered so far in the event creation wizard.

## In scope
- Fetching or accessing the current event draft state (from local state/context or API)
- Passing draft data to the preview header and photo grid
- Wiring the "Close Preview" button to return to the wizard

## Out of scope (do NOT build)
- Saving draft changes (handled in other steps)

## Acceptance criteria
- Given the preview page loads, when draft data is available, then the header and photo grid components render with the actual draft details and uploaded photos.
- Given the preview is open, when "Close Preview" is clicked, then the app navigates back to the active wizard step.
- Given the draft has no uploaded photos, when the preview renders, then the photo count shows "0 photos" and the grid displays an empty state.

## Technical notes
- Endpoint / schema: likely reads from FE state manager or `GET /api/events/:id/draft` if needed.

## Depends on / blocks
- Depends on: [FE] Event preview: overlay and header layout, [FE] Event preview: toolbar and photo grid layout
- Blocks: [QA] Event preview: E2E organizer previews event draft

## Test notes (how QA verifies)
- Manual check that the preview matches the entered wizard data.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [QA] Event preview: E2E organizer previews event draft
lane: QA
parent: [Feature] Event Creation: Step 2.1 — Preview event
estimate_hours: 2
depends_on: [FE] Event preview: wire to event draft

## Context
Parent: [Feature] Event Creation: Step 2.1 — Preview event · Figma: none · Lane: QA

## User story
As a QA engineer, I want to verify that the event preview correctly reflects the draft data and can be closed.

## In scope
- E2E test for the preview flow

## Out of scope (do NOT build)
- Testing full guest functionality (just the preview rendering)

## Acceptance criteria
- Given an event draft with a title, description, and photos, when the organizer clicks preview, then the preview shows the correct title, description, and photos.
- Given the preview is open, when "Close Preview" is clicked, then the wizard is visible again.
- Given the preview is open, when the page loads, then the "Preview Only" badge is visible at the top right.

## Technical notes
- None

## Depends on / blocks
- Depends on: [FE] Event preview: wire to event draft
- Blocks: none

## Test notes (how QA verifies)
- Playwright E2E test covering the scenario.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end
