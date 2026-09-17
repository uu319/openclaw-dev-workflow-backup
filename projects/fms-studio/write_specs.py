import os

specs_dir = "/home/openclaw/.openclaw/workspace/projects/fms-studio/artifacts/specs"
os.makedirs(specs_dir, exist_ok=True)

# Step 1
with open(f"{specs_dir}/event-creation-step-1.md", "w") as f:
    f.write("""# Spec: Event Creation Step 1 — Basic Info

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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
---end
""")

# Step 2
with open(f"{specs_dir}/event-creation-step-2.md", "w") as f:
    f.write("""# Spec: Event Creation Step 2 — Look & Feel

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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
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
- [ ] Status moved to QA FOR DEVELOPMENT
---end
""")

# ... Continue for Steps 2.1, 3, 3.1, 4 ...
