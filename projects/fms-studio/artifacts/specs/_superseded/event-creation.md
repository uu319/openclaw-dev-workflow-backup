# Spec: Event Creation Step 1 — Basic Info

Source: Figma node 9810-7244. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 1 — Basic Info
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244
screenshots: specs/_figma/event-creation/9810-7244.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FEATURE

## User story
As an organizer, I want to enter the basic details of my event, so that I can begin creating my album.

## In scope
- Step 1 of the Create Album wizard
- Basic info form (title, description, location, category, start date, end date)
- Navigating to Step 2

## Out of scope (do NOT build)
- Step 2, 3, 4 of the wizard
- Look & Feel customization
- Publishing the album

## Acceptance criteria
- Given the organizer is on the Create Album wizard Step 1, when valid data is entered and 'Next Step ->' is clicked, then `POST /api/albums/draft` is called and the wizard navigates to Step 2.
- Given empty required fields (Title, Location, Start Date), when 'Next Step ->' is clicked, then validation errors appear under those fields and the form does not submit.
- Given the API returns an error, when 'Next Step ->' is clicked, then a generic error message is shown and the user stays on Step 1.

## Technical notes
- Endpoint / schema: POST /api/albums/draft { title, description, location, category, startDate, endDate } -> 200 { id }
- Mock or fixture for parallel work: Create album endpoint mock returning a dummy ID

## Depends on / blocks
- Depends on: none
- Blocks: Event Creation Step 2

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Basic Info: Set up ORM and albums table
lane: DB
parent: [Feature] Event Creation: Step 1 — Basic Info
priority: high
estimate_hours: 4

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: DB

## User story
As a developer, I want an ORM and a database table, so that album drafts can be persisted.

## In scope
- Choose and set up Prisma ORM (standard for NestJS)
- Create `albums` table with columns: id, title, description, location, category, start_date, end_date, created_at, updated_at
- Initial DB migration

## Out of scope (do NOT build)
- Look and Feel columns (added in Step 2)
- Privacy and access columns (added in Step 3)
- Real user authentication / owner_id (stub for now if needed)

## Acceptance criteria
- Given the backend starts, when the ORM is initialized, then it connects to the database successfully.
- Given a fresh database, when migrations run, then the `albums` table is created with all required columns.
- Given the `albums` table exists, when a row is inserted manually, then the ORM can read it.

## Technical notes
- Endpoint / schema: table `albums` (id uuid PK, title varchar not null, description text, location varchar not null, category varchar, start_date date not null, end_date date)
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Basic Info: POST /api/albums/draft

## Test notes (how QA verifies)
- Developer runs migrations and inserts a dummy row.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [INT] Basic Info: Set up Playwright E2E runner
lane: INT
parent: [Feature] Event Creation: Step 1 — Basic Info
priority: high
estimate_hours: 3

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: INT

## User story
As a QA engineer, I want an E2E testing framework, so that I can write automated UI tests for features.

## In scope
- Install and configure Playwright for the `frontend` Nx project.
- Add an Nx target to run E2E tests.

## Out of scope (do NOT build)
- Complex authentication helpers
- Full coverage of existing features (just the framework setup)

## Acceptance criteria
- Given the Nx workspace, when `npx nx e2e frontend` is run, then Playwright executes a basic dummy test and reports success.
- Given Playwright is configured, when a new test file is added, then the runner picks it up.
- Given CI/CD, when E2E tests run, then they execute headlessly.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Basic Info: E2E organizer creates album draft

## Test notes (how QA verifies)
- Run `npx nx e2e frontend` and see the dummy test pass.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Basic Info: POST /api/albums/draft creates draft
lane: BE
parent: [Feature] Event Creation: Step 1 — Basic Info
priority: high
estimate_hours: 4
depends_on: [DB] Basic Info: Set up ORM and albums table

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: BE

## User story
As an organizer, I want my basic info saved, so that I can proceed to customize the album.

## In scope
- Endpoint `POST /api/albums/draft`
- Validation for required fields (title, location, startDate)
- Saving the row via ORM and returning the ID

## Out of scope (do NOT build)
- Modifying existing drafts (`PATCH` will be used later)
- Access control / user scoping (assume anonymous or stub user for now)

## Acceptance criteria
- Given valid payload `{ title, description, location, category, startDate, endDate }`, when `POST /api/albums/draft` is called, then a row is created in `albums` and it returns 201 with `{ id }`.
- Given missing `title`, when called, then it returns 400 Bad Request with validation error messages.
- Given missing `location` or `startDate`, when called, then it returns 400 Bad Request.

## Technical notes
- Endpoint / schema: POST /api/albums/draft -> 201 { id }
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [DB] Basic Info: Set up ORM and albums table
- Blocks: [FE] Basic Info: wire Next Step to POST /api/albums/draft

## Test notes (how QA verifies)
- Use curl or Postman to trigger the endpoint.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Basic Info: form layout + validation states
lane: FE
parent: [Feature] Event Creation: Step 1 — Basic Info
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244
screenshots: specs/_figma/event-creation/9810-7244.png

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FE

## User story
As an organizer, I want to see a clear form for my event details, so that I provide all required info.

## In scope
- Wizard layout with stepper (1 Basic Info active)
- Form fields: Album Title*, Description (with 0/255 counter), Location*, Category (Optional), Start Date*, End Date (Optional)
- Client-side validation for required fields
- 'Next Step ->' button

## Out of scope (do NOT build)
- Calling the real API (that is the wiring ticket)
- Other wizard steps

## Acceptance criteria
- Given the Step 1 form, when 'Next Step ->' is clicked and 'Album Title' is empty, then an error 'Title is required' shows under the field.
- Given the Step 1 form, when 'Next Step ->' is clicked and 'Location' or 'Start Date' is empty, then respective errors show under those fields.
- Given description text is typed, when it exceeds 255 characters, then the counter turns red and form submission is disabled.
- Given all required fields are filled, when 'Next Step ->' is clicked, then the mock submit handler is called with the form data.
- Given a viewport narrower than 640px, when the form renders, then it is full-width; given wider, it is centered in the modal wrapper.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: `onSubmit(data: BasicInfo): Promise<void>` prop
- Breakpoints (FE only): mobile <640px full width, >=640px modal dialog size

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Basic Info: wire Next Step to POST /api/albums/draft

## Test notes (how QA verifies)
- Render the component and click 'Next Step' without filling fields to see validations.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Basic Info: wire Next Step to POST /api/albums/draft
lane: FE
parent: [Feature] Event Creation: Step 1 — Basic Info
priority: high
estimate_hours: 3
depends_on: [FE] Basic Info: form layout + validation states, [BE] Basic Info: POST /api/albums/draft creates draft
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244
screenshots: specs/_figma/event-creation/9810-7244.png

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FE

## User story
As an organizer, I want my form to save to the server, so that my draft is created.

## In scope
- Wire the 'Next Step ->' button to `POST /api/albums/draft`
- Handle loading state and server errors
- Navigation to Step 2 URL on success (passing the new album ID)

## Out of scope (do NOT build)
- Form layout
- Step 2 UI

## Acceptance criteria
- Given the Step 1 form is valid, when 'Next Step ->' is clicked, then the button shows a loading state.
- Given the API returns 201 with `{ id }`, when the request finishes, then the user is navigated to `/albums/new/step-2?id=<id>` (or similar route).
- Given the API returns an error, when the request finishes, then a generic error toast/message is shown.

## Technical notes
- Endpoint / schema: POST /api/albums/draft -> 201 { id }
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Basic Info: form layout + validation states, [BE] Basic Info: POST /api/albums/draft creates draft
- Blocks: [QA] Basic Info: E2E organizer creates album draft

## Test notes (how QA verifies)
- See E2E scenario.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Basic Info: E2E organizer creates album draft
lane: QA
parent: [Feature] Event Creation: Step 1 — Basic Info
priority: high
estimate_hours: 3
depends_on: [FE] Basic Info: wire Next Step to POST /api/albums/draft, [INT] Basic Info: Set up Playwright E2E runner

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: QA

## User story
As a QA engineer, I want an end-to-end test for Step 1, so that I can ensure drafts are created successfully.

## In scope
- Playwright E2E test covering the happy path of Step 1 and the validation errors.

## Out of scope (do NOT build)
- Tests for other steps.

## Acceptance criteria
- Given Playwright runs, when the test fills in 'Album Title', 'Location', and 'Start Date' and clicks 'Next Step', then the app navigates to Step 2 and the network tab shows a successful POST.
- Given Playwright runs, when the test clicks 'Next Step' on an empty form, then the validation messages are asserted.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Basic Info: wire Next Step to POST /api/albums/draft, [INT] Basic Info: Set up Playwright E2E runner
- Blocks: none

## Test notes (how QA verifies)
- Run `npx nx e2e frontend`.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end
# Spec: Event Creation Step 2 — Look & Feel

Source: Figma node 9836-3977. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 2 — Look & Feel
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation/9836-3977.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FEATURE

## User story
As an organizer, I want to customize the look and feel of my album, so that it matches my event's branding.

## In scope
- Step 2 of the Create Album wizard
- Uploading an album cover
- Selecting a font (Host Grotesk, Honfleur, High Tower, Hubbali, Hi Melody, Helvetica)
- Selecting a theme color (swatches)
- Preview button functionality (saving state and opening preview)
- Navigating to Step 3

## Out of scope (do NOT build)
- The Preview modal itself (separate feature)
- Actual image processing/resizing backend (store raw for now or use simple storage)

## Acceptance criteria
- Given the organizer is on Step 2, when they select an image, select 'Hi Melody' and the Orange theme, then click 'Next Step ->', then `PATCH /api/albums/:id/draft` is called and the wizard navigates to Step 3.
- Given the organizer clicks 'View Preview', when the state is valid, then the draft is saved and the Preview feature opens.
- Given no album cover is uploaded, when 'Next Step ->' is clicked, the form still submits successfully (cover is optional).

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft { coverUrl, font, themeColor } -> 200
- Mock or fixture for parallel work: none

## Depends on / blocks
- Depends on: Event Creation Step 1
- Blocks: Event Creation Step 3

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Look & Feel: add design columns to albums table
lane: DB
parent: [Feature] Event Creation: Step 2 — Look & Feel
priority: high
estimate_hours: 2

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: none · Lane: DB

## User story
As a developer, I want database columns for design choices, so that the album theme is saved.

## In scope
- Add `cover_url`, `font`, and `theme_color` columns to the `albums` table.
- DB migration script.

## Out of scope (do NOT build)
- Other tables.

## Acceptance criteria
- Given the database migrations run, when completed, then the `albums` table has `cover_url` (varchar, nullable), `font` (varchar, nullable), `theme_color` (varchar, nullable).

## Technical notes
- Endpoint / schema: table `albums` additions
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Look & Feel: PATCH /api/albums/:id/draft

## Test notes (how QA verifies)
- Run migrations and inspect schema.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Look & Feel: PATCH /api/albums/:id/draft
lane: BE
parent: [Feature] Event Creation: Step 2 — Look & Feel
priority: high
estimate_hours: 4
depends_on: [DB] Look & Feel: add design columns to albums table

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: none · Lane: BE

## User story
As an organizer, I want my design choices saved to my draft.

## In scope
- `PATCH /api/albums/:id/draft` endpoint
- Updating the album row with `coverUrl`, `font`, `themeColor`

## Out of scope (do NOT build)
- S3 image upload endpoint (will mock or use base64 in FE for now, or just save the URL string passed by FE). Note: In a real app, an [INT] ticket for S3 would be here. For simplicity in this spec, we assume the FE provides a URL or base64.

## Acceptance criteria
- Given a valid draft ID and payload `{ coverUrl: '...', font: 'Hi Melody', themeColor: '#FFA500' }`, when `PATCH` is called, then the database row is updated and 200 OK is returned.
- Given an invalid draft ID, when called, then it returns 404 Not Found.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft -> 200 { id }
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [DB] Look & Feel: add design columns to albums table
- Blocks: [FE] Look & Feel: wire to PATCH API

## Test notes (how QA verifies)
- Send a PATCH request via Postman and verify DB update.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Look & Feel: layout + state selection
lane: FE
parent: [Feature] Event Creation: Step 2 — Look & Feel
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation/9836-3977.png

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FE

## User story
As an organizer, I want to pick my album's font and color, so that it matches my style.

## In scope
- Wizard Step 2 UI (stepper active on 2)
- Image upload dashed dropzone with 'Upload Album Cover' (simulated upload state showing image)
- Font selection grid (6 options)
- Theme color selection swatches (10 swatches + Add button)
- 'View Preview' and 'Next Step ->' buttons

## Out of scope (do NOT build)
- Real S3 upload (mock with a local blob URL or base64 data URL)
- Actual Preview modal

## Acceptance criteria
- Given the font selector, when 'Hi Melody' is clicked, then it gets an orange border indicating selection.
- Given the theme color swatches, when a color is clicked, then it is selected.
- Given the cover upload, when a file is selected, then the preview image replaces the dashed box text.
- Given the Next Step button, when clicked, then the mock submit handler receives the state.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: `onSubmit(data: LookAndFeelData): Promise<void>`
- Breakpoints (FE only): mobile <640px full width, >=640px modal dialog size

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Look & Feel: wire to PATCH API

## Test notes (how QA verifies)
- Click through fonts and colors and verify visual selection states.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Look & Feel: wire to PATCH API
lane: FE
parent: [Feature] Event Creation: Step 2 — Look & Feel
priority: high
estimate_hours: 3
depends_on: [FE] Look & Feel: layout + state selection, [BE] Look & Feel: PATCH /api/albums/:id/draft
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation/9836-3977.png

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FE

## User story
As an organizer, my design settings must be saved when moving to the next step.

## In scope
- Wire 'Next Step ->' to `PATCH /api/albums/:id/draft`
- On success, navigate to Step 3.

## Out of scope (do NOT build)
- Preview feature

## Acceptance criteria
- Given valid selections, when 'Next Step ->' is clicked, then `PATCH` is called with the current draft ID and the UI navigates to Step 3.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Look & Feel: layout + state selection, [BE] Look & Feel: PATCH /api/albums/:id/draft
- Blocks: [QA] Look & Feel: E2E test

## Test notes (how QA verifies)
- QA scenario below.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Look & Feel: E2E test
lane: QA
parent: [Feature] Event Creation: Step 2 — Look & Feel
priority: high
estimate_hours: 2
depends_on: [FE] Look & Feel: wire to PATCH API

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: none · Lane: QA

## User story
As a QA engineer, I want an E2E test to ensure Step 2 saves correctly.

## In scope
- E2E test continuing from Step 1, selecting a font and color, and saving.

## Out of scope (do NOT build)
- Preview test.

## Acceptance criteria
- Given Playwright, when the test selects 'Hi Melody', a color, and clicks Next Step, then the request succeeds and the app navigates to Step 3.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Look & Feel: wire to PATCH API
- Blocks: none

## Test notes (how QA verifies)
- `npx nx e2e frontend`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end
# Spec: Event Creation Step 2.1 — Preview

Source: Figma node 9873-3730. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 2.1 — Preview
lane: FEATURE
priority: normal
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730
screenshots: specs/_figma/event-creation/9873-3730.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730 · Lane: FEATURE

## User story
As an organizer, I want to preview my album design, so that I can see exactly what guests will see before I finish creating it.

## In scope
- Full-screen preview modal showing the event cover, title, description, date, location, category
- Application of selected font and theme color to the preview UI
- Dummy photo grid and face filters to simulate the guest view
- 'Close Preview X' floating button

## Out of scope (do NOT build)
- Actual photo upload or face filtering logic (these are dummy/static for the preview)
- Saving data (preview is read-only)

## Acceptance criteria
- Given the organizer is on Step 2 or 4, when 'View Preview' is clicked, then the Preview modal opens over the wizard, rendering the draft details (title, cover, font, theme).
- Given the Preview is open, when 'Close Preview X' is clicked, then the modal closes and the user returns to the wizard step they were on.

## Technical notes
- Endpoint / schema: none (uses local draft state)
- Breakpoints: Responsive desktop and mobile layout

## Depends on / blocks
- Depends on: Event Creation Step 2
- Blocks: none

## Test notes (how QA verifies)
- See QA ticket.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Preview: Modal layout and dummy guest view
lane: FE
parent: [Feature] Event Creation: Step 2.1 — Preview
priority: normal
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730
screenshots: specs/_figma/event-creation/9873-3730.png

## Context
Parent: [Feature] Event Creation: Step 2.1 — Preview · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730 · Lane: FE

## User story
As an organizer, I want a realistic mock-up of the guest view in the preview.

## In scope
- AlbumPreviewModal component
- Renders `draft` prop (title, description, coverUrl, font, themeColor, date, location, category)
- Applies the selected `font` class to the text and `themeColor` to accent elements
- Renders dummy Search, Sort select, Face filters, and a static grid of mock photos
- 'Preview Only' top badge
- 'Close Preview X' button

## Out of scope (do NOT build)
- API calls

## Acceptance criteria
- Given the `draft` prop has `font: 'Hi Melody'`, when the modal renders, then the title uses the Hi Melody font.
- Given the `draft` prop has a cover URL, when the modal renders, then the cover image is displayed.
- Given the 'Close Preview X' button, when clicked, then the `onClose` callback is fired.
- Given a viewport < 640px, when the preview renders, then the photo grid is 1-2 columns; given >= 640px, it is 3+ columns.

## Technical notes
- Mock or fixture for parallel work: static photo URLs and face avatars for the dummy grid.

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Preview: E2E check

## Test notes (how QA verifies)
- Render in storybook or test file and check font/color application.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Preview: E2E check
lane: QA
parent: [Feature] Event Creation: Step 2.1 — Preview
priority: normal
estimate_hours: 2
depends_on: [FE] Preview: Modal layout and dummy guest view

## Context
Parent: [Feature] Event Creation: Step 2.1 — Preview · Figma: none · Lane: QA

## User story
As a QA engineer, I want to ensure the preview modal opens and closes.

## In scope
- E2E test clicking 'View Preview' on Step 2 and closing it.

## Out of scope (do NOT build)
- Testing dummy photo interactions.

## Acceptance criteria
- Given Step 2, when 'View Preview' is clicked, then the preview modal becomes visible.
- Given the preview modal is visible, when 'Close Preview X' is clicked, then it is removed from the DOM.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none

## Depends on / blocks
- Depends on: [FE] Preview: Modal layout and dummy guest view
- Blocks: none

## Test notes (how QA verifies)
- `npx nx e2e frontend`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end
# Spec: Event Creation Step 3 — Privacy and Access

Source: Figma node 9836-5766. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 3 — Privacy and Access
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
screenshots: specs/_figma/event-creation/9836-5766.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766 · Lane: FEATURE

## User story
As an organizer, I want to choose how people access my album (Public, Link, Password, etc.), so that I can control privacy.

## In scope
- Wizard Step 3
- Radio selection for: Public (Default), Hidden, Link only, Restricted, Password protected
- Navigating to Step 4 (or triggering Password modal if selected)

## Out of scope (do NOT build)
- The Password modal itself (Step 3.1 - separate feature)
- Actual access enforcement middleware (this just sets the flag on the draft)

## Acceptance criteria
- Given the Step 3 form, when 'Public' is selected and 'Next Step ->' is clicked, then `PATCH /api/albums/:id/draft` is called with `privacy: 'public'` and it navigates to Step 4.
- Given the Step 3 form, when 'Password protected' is selected and 'Next Step ->' is clicked, then it opens the Set Password modal (Step 3.1) instead of immediately navigating to Step 4.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft { privacy: string } -> 200

## Depends on / blocks
- Depends on: Event Creation Step 2
- Blocks: Event Creation Step 3.1, Event Creation Step 4

## Test notes (how QA verifies)
- See [QA] ticket.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Privacy: Add privacy column to albums
lane: DB
parent: [Feature] Event Creation: Step 3 — Privacy and Access
priority: high
estimate_hours: 2

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: none · Lane: DB

## User story
As a developer, I want a column to store the privacy mode.

## In scope
- Add `privacy` column (enum/varchar) to `albums` table. Options: public, hidden, link, restricted, password.
- Migration script.

## Out of scope (do NOT build)
- Password hash column (done in Step 3.1)

## Acceptance criteria
- Given the migration runs, when completed, then `albums` has a `privacy` column.

## Technical notes
- Endpoint / schema: table `albums` (privacy varchar)

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Privacy: update PATCH draft

## Test notes (how QA verifies)
- Inspect DB schema.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Privacy: update PATCH draft
lane: BE
parent: [Feature] Event Creation: Step 3 — Privacy and Access
priority: high
estimate_hours: 2
depends_on: [DB] Privacy: Add privacy column to albums

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: none · Lane: BE

## User story
As an organizer, I want to save my privacy setting.

## In scope
- Update `PATCH /api/albums/:id/draft` to accept `privacy` field.

## Out of scope (do NOT build)
- Password saving logic

## Acceptance criteria
- Given valid payload `{ privacy: 'link' }`, when PATCH is called, then the DB is updated and returns 200.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft { privacy: string }

## Depends on / blocks
- Depends on: [DB] Privacy: Add privacy column to albums
- Blocks: [FE] Privacy: wire form to API

## Test notes (how QA verifies)
- Postman check.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Privacy: form layout
lane: FE
parent: [Feature] Event Creation: Step 3 — Privacy and Access
priority: high
estimate_hours: 5
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
screenshots: specs/_figma/event-creation/9836-5766.png

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766 · Lane: FE

## User story
As an organizer, I want to select a privacy option from a list.

## In scope
- Wizard Step 3 active state
- 5 custom radio button cards with icons, titles, and descriptions.
- Selection state management.

## Out of scope (do NOT build)
- API call

## Acceptance criteria
- Given the options, when 'Hidden' is clicked, then its radio button becomes checked (orange dot) and others uncheck.
- Given 'Next Step' is clicked with 'Public' selected, then mock submit is called with `{ privacy: 'public' }`.

## Technical notes
- Mock or fixture for parallel work: `onSubmit(data: { privacy: string }): void`

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Privacy: wire form to API

## Test notes (how QA verifies)
- Click through radio options.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Privacy: wire form to API
lane: FE
parent: [Feature] Event Creation: Step 3 — Privacy and Access
priority: high
estimate_hours: 3
depends_on: [FE] Privacy: form layout, [BE] Privacy: update PATCH draft
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
screenshots: specs/_figma/event-creation/9836-5766.png

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766 · Lane: FE

## User story
As an organizer, I want my choice saved when I proceed.

## In scope
- Wire 'Next Step' to `PATCH /api/albums/:id/draft`.
- Navigate to Step 4 (if not password protected).
- If 'Password protected' is selected, open the Set Password modal (or navigate to Step 3.1 route) instead of going to Step 4.

## Out of scope (do NOT build)
- The password modal content.

## Acceptance criteria
- Given 'Public' selected, when 'Next Step' is clicked, then PATCH is called and the user goes to Step 4.
- Given 'Password protected' selected, when 'Next Step' is clicked, then the Password Modal is triggered and it does NOT navigate to Step 4 yet.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft

## Depends on / blocks
- Depends on: [FE] Privacy: form layout, [BE] Privacy: update PATCH draft
- Blocks: [QA] Privacy: E2E check

## Test notes (how QA verifies)
- See E2E scenario.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Privacy: E2E check
lane: QA
parent: [Feature] Event Creation: Step 3 — Privacy and Access
priority: high
estimate_hours: 2
depends_on: [FE] Privacy: wire form to API

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: none · Lane: QA

## User story
As a QA engineer, I want to verify privacy selection routing.

## In scope
- Test selecting Public and going to Step 4.
- Test selecting Password Protected and seeing the modal.

## Out of scope (do NOT build)
- Filling the password modal.

## Acceptance criteria
- Given Step 3, when 'Link only' is selected and Next Step clicked, then the URL changes to Step 4.
- Given Step 3, when 'Password protected' is selected and Next Step clicked, then the Set Album Password modal appears.

## Technical notes
- Mock or fixture for parallel work: none

## Depends on / blocks
- Depends on: [FE] Privacy: wire form to API
- Blocks: none

## Test notes (how QA verifies)
- `npx nx e2e frontend`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end
# Spec: Event Creation Step 3.1 — Set event password

Source: Figma node 9836-6520. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 3.1 — Set event password
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520
screenshots: specs/_figma/event-creation/9836-6520.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520 · Lane: FEATURE

## User story
As an organizer, I want to set a password on my event, so that only invited guests can open the album.

## In scope
- Password entry modal triggered from Step 3
- 'Set Password' and 'Confirm Password' fields with show/hide toggle
- Validation (match, length)
- Persisting the password hash on the event draft
- 'Save' button navigates to Step 4
- 'I'll do this later.' navigates to Step 4 without saving a password

## Out of scope (do NOT build)
- Guest-side password prompt (separate feature)
- Password reset or "forgot password"
- Password strength meter beyond the length rule

## Acceptance criteria
- Given the organizer is on the Set Password modal, when 'Save' is clicked with matching passwords ≥ 8 characters, then `PATCH /api/albums/:id/draft` is called with the password and the wizard navigates to Step 4.
- Given passwords do not match, when 'Save' is clicked, then 'Passwords do not match' shows and submission is blocked.
- Given 'I'll do this later.' is clicked, then the wizard navigates to Step 4 without calling the PATCH password endpoint.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft { password: string } -> 200

## Depends on / blocks
- Depends on: Event Creation Step 3
- Blocks: Event Creation Step 4

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Set password: Add password_hash column
lane: DB
parent: [Feature] Event Creation: Step 3.1 — Set event password
priority: high
estimate_hours: 2

## Context
Parent: [Feature] Event Creation: Step 3.1 — Set event password · Figma: none · Lane: DB

## User story
As a developer, I need to store the hashed password.

## In scope
- Add `password_hash` column to `albums`.
- Migration script.

## Out of scope (do NOT build)
- Plaintext password column.

## Acceptance criteria
- Given the migration runs, when complete, then `password_hash` exists.

## Technical notes
- Endpoint / schema: table `albums` (`password_hash` varchar nullable)

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Set password: store hash

## Test notes (how QA verifies)
- Inspect DB schema.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Set password: store hash
lane: BE
parent: [Feature] Event Creation: Step 3.1 — Set event password
priority: high
estimate_hours: 4
depends_on: [DB] Set password: Add password_hash column

## Context
Parent: [Feature] Event Creation: Step 3.1 — Set event password · Figma: none · Lane: BE

## User story
As an organizer, I want my password hashed and stored securely.

## In scope
- Update `PATCH /api/albums/:id/draft` to accept `password`.
- Hash the password using bcrypt before saving to `password_hash`.

## Out of scope (do NOT build)
- Returning the hash in responses.

## Acceptance criteria
- Given a payload with `password`, when PATCH is called, then the DB `password_hash` is updated with a bcrypt hash, and 200 is returned without the hash in the body.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft
- INT note: bcrypt is a standard library addition, no separate INT ticket needed here.

## Depends on / blocks
- Depends on: [DB] Set password: Add password_hash column
- Blocks: [FE] Set password: wire Save to API

## Test notes (how QA verifies)
- Postman request and DB inspection to verify hashing.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Set password: modal layout + validation
lane: FE
parent: [Feature] Event Creation: Step 3.1 — Set event password
priority: high
estimate_hours: 5
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520
screenshots: specs/_figma/event-creation/9836-6520.png

## Context
Parent: [Feature] Event Creation: Step 3.1 — Set event password · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520 · Lane: FE

## User story
As an organizer, I want to enter and confirm my password in a modal.

## In scope
- Modal component 'Set Album Password'
- 'Set Password' and 'Confirm Password' inputs
- Eye icons to toggle text visibility (type="password" <-> type="text")
- 'I'll do this later.' link
- 'Save' button
- Client-side validation for length (>= 8) and match.

## Out of scope (do NOT build)
- API integration

## Acceptance criteria
- Given the modal, when the eye icon is clicked on an input, then its type changes to text and the icon changes to eye-off.
- Given the inputs, when the values do not match and 'Save' is clicked, then a 'Passwords do not match' error is shown.
- Given 'I'll do this later.' is clicked, then `onSkip()` is called.
- Given valid matching passwords, when 'Save' is clicked, then `onSave(password)` is called.

## Technical notes
- Mock or fixture for parallel work: `onSave`, `onSkip` callbacks.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Set password: wire Save to API

## Test notes (how QA verifies)
- Test show/hide toggle and validation.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Set password: wire Save to API
lane: FE
parent: [Feature] Event Creation: Step 3.1 — Set event password
priority: high
estimate_hours: 3
depends_on: [FE] Set password: modal layout + validation, [BE] Set password: store hash
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520
screenshots: specs/_figma/event-creation/9836-6520.png

## Context
Parent: [Feature] Event Creation: Step 3.1 — Set event password · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520 · Lane: FE

## User story
As an organizer, my password needs to be sent to the server.

## In scope
- Wire modal `onSave` to `PATCH /api/albums/:id/draft`.
- Navigate to Step 4 on success.
- Wire `onSkip` to navigate to Step 4 without calling the API.

## Out of scope (do NOT build)
- Modal UI

## Acceptance criteria
- Given a valid password, when 'Save' is clicked, then PATCH is called. Upon 200 OK, the modal closes and the URL changes to Step 4.
- Given 'I'll do this later.' is clicked, then the URL changes to Step 4.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft

## Depends on / blocks
- Depends on: [FE] Set password: modal layout + validation, [BE] Set password: store hash
- Blocks: [QA] Set password: E2E check

## Test notes (how QA verifies)
- See QA scenario.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Set password: E2E check
lane: QA
parent: [Feature] Event Creation: Step 3.1 — Set event password
priority: high
estimate_hours: 2
depends_on: [FE] Set password: wire Save to API

## Context
Parent: [Feature] Event Creation: Step 3.1 — Set event password · Figma: none · Lane: QA

## User story
As a QA engineer, I want to verify password setting.

## In scope
- E2E test for the modal: save flow and skip flow.

## Out of scope (do NOT build)
- Other steps.

## Acceptance criteria
- Given the modal, when a valid password is saved, then the API is called and the user reaches Step 4.
- Given the modal, when 'I'll do this later.' is clicked, then the user reaches Step 4 without a password PATCH request.

## Technical notes
- Endpoint / schema: none

## Depends on / blocks
- Depends on: [FE] Set password: wire Save to API
- Blocks: none

## Test notes (how QA verifies)
- `npx nx e2e frontend`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end
# Spec: Event Creation Step 4 — Review & Create

Source: Figma node 9836-6900. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 4 — Review & Create
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation/9836-6900.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900 · Lane: FEATURE

## User story
As an organizer, I want to review all my settings before finalizing the album, so that I catch any mistakes.

## In scope
- Wizard Step 4 (active)
- Review summary table (Album Title, Description, Event Date, Location, Category, Album Font, Album Theme, Privacy and Access)
- Album Cover image with 'View Preview' button overlay
- 'Edit' button returning to Step 1
- 'Create ->' button to finalize the album and navigate to the dashboard

## Out of scope (do NOT build)
- Modifying data on this screen (except via the Edit button which navigates back)

## Acceptance criteria
- Given the Step 4 screen, when it loads, then it displays the aggregated data from the draft.
- Given the screen, when 'Edit' is clicked, then the wizard navigates back to Step 1.
- Given the screen, when 'View Preview' is clicked on the cover, then the Preview modal opens.
- Given the screen, when 'Create ->' is clicked, then `POST /api/albums/:id/publish` is called and the user navigates to their dashboard.

## Technical notes
- Endpoint / schema: POST /api/albums/:id/publish -> 200

## Depends on / blocks
- Depends on: Event Creation Step 1, 2, 3
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Review & Create: Add status to albums
lane: DB
parent: [Feature] Event Creation: Step 4 — Review & Create
priority: high
estimate_hours: 1

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: none · Lane: DB

## User story
As a developer, I need to distinguish drafts from published albums.

## In scope
- Add `status` column (enum/varchar) to `albums`. Default: 'draft'.
- Migration script.

## Out of scope (do NOT build)
- Other tables.

## Acceptance criteria
- Given the migration runs, when complete, then `status` exists and defaults to 'draft'.

## Technical notes
- Endpoint / schema: table `albums` (status varchar default 'draft')

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Review & Create: POST /api/albums/:id/publish

## Test notes (how QA verifies)
- DB inspection.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Review & Create: POST /api/albums/:id/publish
lane: BE
parent: [Feature] Event Creation: Step 4 — Review & Create
priority: high
estimate_hours: 3
depends_on: [DB] Review & Create: Add status to albums

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: none · Lane: BE

## User story
As an organizer, I want to finalize my draft into an active album.

## In scope
- `POST /api/albums/:id/publish`
- Sets the `status` of the album to 'published'.

## Out of scope (do NOT build)
- Sending emails, generating QR codes (separate features).

## Acceptance criteria
- Given a valid draft ID, when `POST /api/albums/:id/publish` is called, then the `status` is set to 'published' and 200 is returned.

## Technical notes
- Endpoint / schema: POST /api/albums/:id/publish

## Depends on / blocks
- Depends on: [DB] Review & Create: Add status to albums
- Blocks: [FE] Review & Create: wire Create button

## Test notes (how QA verifies)
- Postman request and DB verification.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Review & Create: UI layout
lane: FE
parent: [Feature] Event Creation: Step 4 — Review & Create
priority: high
estimate_hours: 5
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation/9836-6900.png

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900 · Lane: FE

## User story
As an organizer, I want to see a summary of my album details.

## In scope
- Wizard Step 4 active
- Two column layout: Left is Album Cover with 'View Preview' button overlay, Right is the details table and 'Edit' button.
- Details list showing formatted data from the draft context.

## Out of scope (do NOT build)
- Wiring the Create button to the API.

## Acceptance criteria
- Given the draft data, when the component renders, then all fields (Title, Date, Privacy, etc.) match the draft state.
- Given the 'Edit' button, when clicked, then the router navigates back to `/albums/new/step-1` (or equivalent).
- Given a viewport < 640px, when rendered, then the cover and details stack vertically; given >= 640px, they are side-by-side.

## Technical notes
- Mock or fixture for parallel work: static draft object.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Review & Create: wire Create button

## Test notes (how QA verifies)
- Verify data mapping from mock object to UI.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Review & Create: wire Create button
lane: FE
parent: [Feature] Event Creation: Step 4 — Review & Create
priority: high
estimate_hours: 3
depends_on: [FE] Review & Create: UI layout, [BE] Review & Create: POST /api/albums/:id/publish
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation/9836-6900.png

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900 · Lane: FE

## User story
As an organizer, I want to publish my album.

## In scope
- Wire 'Create ->' button to `POST /api/albums/:id/publish`.
- Navigate to the dashboard on success.

## Out of scope (do NOT build)
- Dashboard UI

## Acceptance criteria
- Given the Step 4 screen, when 'Create ->' is clicked, then POST is called. Upon 200, the user navigates to `/dashboard`.
- Given the API returns an error, when 'Create ->' is clicked, then a toast error shows and the user remains on Step 4.

## Technical notes
- Endpoint / schema: POST /api/albums/:id/publish

## Depends on / blocks
- Depends on: [FE] Review & Create: UI layout, [BE] Review & Create: POST /api/albums/:id/publish
- Blocks: [QA] Review & Create: Full wizard E2E

## Test notes (how QA verifies)
- See E2E.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Review & Create: Full wizard E2E
lane: QA
parent: [Feature] Event Creation: Step 4 — Review & Create
priority: high
estimate_hours: 4
depends_on: [FE] Review & Create: wire Create button

## Context
Parent: [Feature] Event Creation: Step 4 — Review & Create · Figma: none · Lane: QA

## User story
As a QA engineer, I want to ensure the entire wizard flows correctly and publishes an album.

## In scope
- Playwright E2E test starting at Step 1 and finishing at Step 4 publishing.

## Out of scope (do NOT build)
- Edge cases inside each step (those are in the step-specific QA tickets).

## Acceptance criteria
- Given the wizard, when the test fills Step 1, skips cover in Step 2, selects Public in Step 3, and clicks Create in Step 4, then the album is published and it reaches the dashboard.

## Technical notes
- Endpoint / schema: none

## Depends on / blocks
- Depends on: [FE] Review & Create: wire Create button
- Blocks: none

## Test notes (how QA verifies)
- `npx nx e2e frontend`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end
