# Spec: Editing Album

Source: Figma nodes 10009-4695, 10041-4424, 10009-5369. Written by VanPM.

---ticket
title: [Editing Album] [Feature] Organizer Dashboard: Editing Album
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-4695, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10041-4424, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-5369
screenshots: specs/_figma/editing-album/10009-4695.png, specs/_figma/editing-album/10041-4424.png, specs/_figma/editing-album/10009-5369.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-5369 · Lane: FEATURE

## User story
As an organizer, I want to edit my album's details and look & feel so that I can keep event information accurate and update its branding over time.

## In scope
- "Edit Album" action in the album card dropdown menu.
- A modal to edit basic info (Title, Description, Location, Category, Start/End Date).
- A section within the modal to edit Look & Feel (Cover image, Font, Theme color).
- Updating the `events` table with the edited values.

## Out of scope (do NOT build)
- "Share Album" functionality (covered in a separate feature).
- "Delete Album" functionality (covered in a separate feature).
- Bulk editing multiple albums.
- Changing the privacy/password settings (done via a different flow/ticket).

## Acceptance criteria
- Given the user is on the Organizer Dashboard, when they click the "⋮" menu on an album card, then a dropdown appears with "Edit Album", "Share Album", and "Delete Album" options.
- Given the album dropdown is open, when the user clicks "Edit Album", then the Edit Album modal opens populated with the album's current data.
- Given the Edit Album modal is open, when the user modifies the "Album Title" or "Location" and clears it, then the field shows a required validation error.
- Given the Edit Album modal is open, when the user clicks "Save Changes", then a PATCH request is sent to update the event and the modal closes upon success.
- Given the user is editing the album cover, when they click "Remove", then the cover image is removed from the form state and the UI shows the empty upload placeholder.

## Technical notes
- We are updating an existing `events` row. The endpoint should likely be `PATCH /api/events/:id`.
- The modal combines fields that were originally collected across Step 1 (Basic Info) and Step 2 (Look & Feel) of the Event Creation flow.
- The `events` table columns already exist (planned in `event-creation-step-1` and `event-creation-step-2`).

## Depends on / blocks
- Depends on: [FE] Dashboard: layout + static components (dashboard-dashboard), [FE] My Albums: grid layout header and search controls (dashboard-my-albums)
- Blocks: none

## Test notes (how QA verifies)
- Verify the modal can scroll if the viewport is short.
- Verify removing a cover image successfully nulls it in the database on save.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [Editing Album] [FE] Album Card Menu and Modal Layout
lane: FE
parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album
priority: normal
estimate_hours: 8
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10041-4424, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-5369
screenshots: specs/_figma/editing-album/10041-4424.png, specs/_figma/editing-album/10009-5369.png
assets: specs/_figma/editing-album/assets/manifest.json

## Context
Parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-5369 · Lane: FE

## User story
As an organizer, I want to open an edit form from my album card so I can update its details.

## In scope
- Adding the dropdown menu to the "⋮" button on the Album card component.
- Building the "Edit Album" modal layout containing two columns (Basic info fields, Look & feel fields).
- Wiring the form fields to local state (Title, Description, Location, Category, Start Date, End Date, Font, Theme Color, Cover Image).
- Firing a save callback when "Save Changes" is clicked.

## Out of scope (do NOT build)
- API integration (wiring to the backend is handled in a separate ticket).
- "Share Album" and "Delete Album" actions (stub them or leave them un-wired).

## Acceptance criteria
- Given the user is viewing an album card, when they click the "⋮" button, then a menu appears with "Edit Album", "Share Album", and "Delete Album".
- Given the album menu is open, when the user clicks "Edit Album", then the Edit Album modal opens.
- Given the Edit Album modal is open, when the user clicks the "X" button in the header, then the modal closes and changes are discarded.
- Given the Edit Album modal is open, when the user types in the "Album Title" or "Location" inputs, then the input values update.
- Given the Edit Album modal is open, when the user clicks a font card (e.g., "Honfleur"), then that card receives an orange 3px border to indicate selection.
- Given the Edit Album modal has a cover image uploaded, when the user clicks "Remove", then the cover image disappears and the empty upload state is shown.

## Design fidelity
- Tokens: Primary `#FF6100` · Gradient Orange (Save Button) `linear-gradient(180deg, rgba(255, 100, 4, 1) 0%, rgba(255, 135, 57, 1) 100%)` · Text Dark `#313131` · Input Background `rgba(0, 0, 0, 0.05)` · Modal Background `#FFFFFF` · Selected Font Border `#FF6100` 3px
- Fonts: Base/Headings `Host Grotesk` (400, 500, 600) · Display Options: `Host Grotesk`, `Honfleur`, `High Tower Text`, `Hubballi`, `Hi Melody`, `Helvetica LT Std`
- Assets (from `specs/_figma/editing-album/assets/manifest.json`, copy into the repo at these paths):
  - `assets/theme-swatch-green.png` → `frontend/public/images/theme-swatch-green.png` — Green Theme Color Swatch, 101x126
  - `assets/theme-swatch-pink.png` → `frontend/public/images/theme-swatch-pink.png` — Pink Theme Color Swatch, 100x56
- No placeholders: every asset above is rendered by the code. A grey box, a text stand-in, or a solid colour where artwork belongs is a defect.

## Technical notes
- Interface / schema: Modal accepts `isOpen`, `onClose`, `initialData`, `onSave(data)`.
- Mock or fixture for parallel work: `onSave(data: object): Promise<void>` prop; page calls it, parent wiring ticket supplies the real one.
- Breakpoints (UI lanes only): mobile <640px: full width modal taking up entire screen, tablet 640–1024px: centered modal with vertical scrolling, desktop >1024px: centered modal up to ~1400px max-width.

## Depends on / blocks
- Depends on: none
- Blocks: [Editing Album] [FE] API Wiring and Validation

## Test notes (how QA verifies)
- Open modal, ensure fonts render correctly and selections update visual state.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] ([FE] only) Every asset in `## Design fidelity` is committed at its stated repo path, non-empty, and rendered by the code; no placeholder box or text stand-in remains, and the tokens listed there are the values in the code
- [ ] Unit tests for this lane added and green
- [ ] Lint clean
- [ ] PR opened from the branch this project's Flow **Branch model** gives, and reviewed
- [ ] Status moved to the board's `staged` status once the change is on staging
---end

---ticket
title: [Editing Album] [BE] Update event endpoint
lane: BE
parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album
priority: normal
estimate_hours: 6

## Context
Parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album · Figma: none · Lane: BE

## User story
As a backend system, I must provide a secure endpoint to update event details.

## In scope
- Creating a `PATCH /api/events/:id` endpoint.
- Validating the incoming payload (allowing partial updates of title, description, location, category, start_date, end_date, font, theme_color, cover_image_id).
- Verifying the user has permission to edit the event (they are the owner).
- Updating the `events` row in the database.

## Out of scope (do NOT build)
- Updating privacy or password settings (this is a separate endpoint/flow).
- Changing the `status` from 'published' to 'draft' or vice-versa.

## Acceptance criteria
- Given a valid authenticated request with a partial payload (e.g., just `title` and `font`), when `PATCH /api/events/:id` is called, then the `events` table is updated with only the provided fields and a 200 OK is returned.
- Given a request missing required fields if they are explicitly set to null (e.g., `title: null`), when `PATCH /api/events/:id` is called, then a 400 Bad Request validation error is returned.
- Given a request for an event ID that the authenticated user does not own, when `PATCH /api/events/:id` is called, then a 403 Forbidden is returned.
- Given a request for an event ID that does not exist, when `PATCH /api/events/:id` is called, then a 404 Not Found is returned.

## Technical notes
- Interface / schema: `PATCH /api/events/:id` accepting `Partial<Event>` body.

## Depends on / blocks
- Depends on: none
- Blocks: [Editing Album] [FE] API Wiring and Validation

## Test notes (how QA verifies)
- Call endpoint with various payloads using curl or Postman to confirm validation and permissions.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green
- [ ] Lint clean
- [ ] PR opened from the branch this project's Flow **Branch model** gives, and reviewed
- [ ] Status moved to the board's `staged` status once the change is on staging
---end

---ticket
title: [Editing Album] [FE] API Wiring and Validation
lane: FE
parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album
priority: normal
estimate_hours: 4
depends_on: [Editing Album] [FE] Album Card Menu and Modal Layout, [Editing Album] [BE] Update event endpoint
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10041-4424
screenshots: specs/_figma/editing-album/10041-4424.png
assets: specs/_figma/editing-album/assets/manifest-empty.json

## Context
Parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-5369 · Lane: FE

## User story
As an organizer, I want my edits to actually save to the server and update the dashboard.

## In scope
- Populating the Edit Album modal with the selected album's data from the API.
- Implementing form validation (Title and Location are required, Start Date is required).
- Calling the `PATCH /api/events/:id` endpoint on "Save Changes".
- Handling loading states (disabling the save button) and error states (showing a toast or message on failure).
- Refreshing the dashboard album list on successful save.

## Out of scope (do NOT build)
- UI layout (done in the layout ticket).

## Acceptance criteria
- Given the user clicks "Edit Album", when the modal opens, then the form fields are pre-populated with the album's existing data (Title, Location, Font, Theme Color, etc.).
- Given the user clears the "Album Title" field, when they click "Save Changes", then the submission is blocked and a required validation error is shown.
- Given the form is valid, when the user clicks "Save Changes", then the button shows a loading state and a PATCH request is made to the server.
- Given the PATCH request succeeds, when the response returns, then the modal closes and the dashboard's album list reflects the updated data.

## Design fidelity
- Tokens: Primary `#FF6100`
- Assets (from `specs/_figma/editing-album/assets/manifest-empty.json`, copy into the repo at these paths):
  - none (this screen is CSS only)
- No placeholders: every asset above is rendered by the code. A grey box, a text stand-in, or a solid colour where artwork belongs is a defect.

## Technical notes
- Interface / schema: fetch existing data (likely passed down from dashboard or fetched by id), call `PATCH /api/events/:id`.

## Depends on / blocks
- Depends on: [Editing Album] [FE] Album Card Menu and Modal Layout, [Editing Album] [BE] Update event endpoint
- Blocks: [Editing Album] [QA] Edit album details and verify on dashboard

## Test notes (how QA verifies)
- Verify form validates empty required fields before submission.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] ([FE] only) Every asset in `## Design fidelity` is committed at its stated repo path, non-empty, and rendered by the code; no placeholder box or text stand-in remains, and the tokens listed there are the values in the code
- [ ] Unit tests for this lane added and green
- [ ] Lint clean
- [ ] PR opened from the branch this project's Flow **Branch model** gives, and reviewed
- [ ] Status moved to the board's `staged` status once the change is on staging
---end

---ticket
title: [Editing Album] [QA] Edit album details and verify on dashboard
lane: QA
parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album
priority: normal
estimate_hours: 2
depends_on: [Editing Album] [FE] API Wiring and Validation

## Context
Parent: [Editing Album] [Feature] Organizer Dashboard: Editing Album · Figma: none · Lane: QA

## User story
As QA, I want to verify the Edit Album flow works end-to-end.

## In scope
- E2E scenario covering opening the modal, editing fields, and saving.

## Out of scope (do NOT build)
- Performance testing.

## Acceptance criteria
- Given a test album exists, when the E2E runner clicks "Edit Album", changes the title and location, and clicks "Save Changes", then the modal closes and the new title appears in the album list.
- Given the modal is open, when a required field like title is cleared, then the runner verifies the Save button is blocked or a validation error appears.
- Given the cover upload area, when the remove button is clicked, then the runner verifies the cover image is cleared from the preview.

## Technical notes
- Interface / schema: Playwright or Cypress (once set up) test script.

## Depends on / blocks
- Depends on: [Editing Album] [FE] API Wiring and Validation
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] scenario locally or in CI once available.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green
- [ ] Lint clean
- [ ] PR opened from the branch this project's Flow **Branch model** gives, and reviewed
- [ ] Status moved to the board's `staged` status once the change is on staging
---end