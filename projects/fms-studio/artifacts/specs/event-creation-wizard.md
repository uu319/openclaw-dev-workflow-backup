# Spec: Event Creation Wizard (Steps 1 to 4)

Source: Figma Event Creation screens. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Wizard flow
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244,https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977,https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730,https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766,https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520,https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation/9810-7244.png,specs/_figma/event-creation/9836-3977.png,specs/_figma/event-creation/9873-3730.png,specs/_figma/event-creation/9836-5766.png,specs/_figma/event-creation/9836-6520.png,specs/_figma/event-creation/9836-6900.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FEATURE

## User story
As an organizer, I want a step-by-step wizard to create an album, so that I can configure its details, look, and privacy before publishing.

## In scope
- Step 1: Basic Info (Title, Location, Date)
- Step 2: Look & Feel (Cover, Font, Theme)
- Step 2.1: Preview of the guest view
- Step 3: Privacy and Access (Public, Link, Password, etc.)
- Step 3.1: Password setup modal
- Step 4: Review and Publish

## Out of scope (do NOT build)
- Guest-side album viewing
- Guest-side password prompt
- Actual photo upload endpoints (dummy/blob for now)

## Acceptance criteria
- Given the organizer is on Step 1, when valid data is entered and 'Next Step ->' is clicked, then a draft is created via `POST /api/albums/draft` and the UI navigates to Step 2.
- Given the organizer is on Step 2 or 3, when valid selections are made and 'Next Step ->' is clicked, then the draft is updated via `PATCH /api/albums/:id/draft` and the UI navigates to the next step.
- Given the organizer is on Step 4, when 'Create ->' is clicked, then `POST /api/albums/:id/publish` is called and the user is redirected to the dashboard.

## Technical notes
- Endpoint / schema: POST/PATCH/POST for drafts and publish
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] E2E scenario.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [INT] Event Creation: Set up Playwright E2E runner
lane: INT
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 3

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: none · Lane: INT

## User story
As a QA engineer, I want an E2E testing framework, so that automated tests can verify the wizard flow.

## In scope
- Install Playwright in the Nx workspace for the frontend.
- Add an e2e target.

## Out of scope (do NOT build)
- Full coverage (just framework setup)

## Acceptance criteria
- Given a fresh checkout, when `npx nx e2e frontend` is executed, then Playwright runs the tests.
- Given Playwright runs, when a dummy test is executed, then it reports success.
- Given CI/CD runs, when the e2e command is triggered, then tests execute headlessly without a UI.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Event Creation: E2E test for wizard flow

## Test notes (how QA verifies)
- Run `npx nx e2e frontend`.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [DB] Event Creation: albums table for drafts and publish
lane: DB
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 4

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: none · Lane: DB

## User story
As a developer, I want a database table, so that album data is persisted across wizard steps.

## In scope
- Prisma ORM initialization.
- Create `albums` table with columns for all steps: title, description, location, category, start_date, end_date, cover_url, font, theme_color, privacy, password_hash, status (default 'draft').

## Out of scope (do NOT build)
- Guest users table
- Photo storage table

## Acceptance criteria
- Given the database is empty, when Prisma migrations are applied, then the `albums` table is created with all defined columns.
- Given the `albums` table exists, when the application starts, then the ORM connects successfully to the database.
- Given the ORM is connected, when a dummy row is inserted, then the row can be read back with all fields.

## Technical notes
- Endpoint / schema: table `albums`
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Event Creation: POST /api/albums/draft

## Test notes (how QA verifies)
- Inspect DB schema.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [BE] Event Creation: POST /api/albums/draft
lane: BE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 3
depends_on: [DB] Event Creation: albums table for drafts and publish

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: none · Lane: BE

## User story
As an organizer, I want to create a draft when I finish Step 1.

## In scope
- Endpoint `POST /api/albums/draft`
- Validation for Step 1 fields (title, location, startDate).
- DB insert.

## Out of scope (do NOT build)
- Updating existing drafts.

## Acceptance criteria
- Given a valid payload with title, location, and startDate, when `POST /api/albums/draft` is called, then it creates a row in the DB and returns 201 with the ID.
- Given a payload missing the title, when `POST /api/albums/draft` is called, then it returns 400 Bad Request.
- Given a payload missing the location, when `POST /api/albums/draft` is called, then it returns 400 Bad Request.

## Technical notes
- Endpoint / schema: POST /api/albums/draft

## Depends on / blocks
- Depends on: [DB] Event Creation: albums table for drafts and publish
- Blocks: [FE] Event Creation: Step 1 UI and API wiring

## Test notes (how QA verifies)
- Postman request.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [BE] Event Creation: PATCH /api/albums/:id/draft
lane: BE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 4
depends_on: [DB] Event Creation: albums table for drafts and publish

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: none · Lane: BE

## User story
As an organizer, I want to save my design, privacy, and password choices to my draft.

## In scope
- Endpoint `PATCH /api/albums/:id/draft`
- Accepts partial updates for look & feel (coverUrl, font, themeColor), privacy, and password.
- If password is provided, hashes it using bcrypt before saving.

## Out of scope (do NOT build)
- Creating new drafts (handled by POST).

## Acceptance criteria
- Given a payload with `font` and `themeColor`, when the endpoint is called, then the database row is updated and 200 is returned.
- Given a payload with `privacy: 'public'`, when the endpoint is called, then the DB is updated to public.
- Given a payload with a plaintext password, when the endpoint is called, then the DB stores a bcrypt hash of the password and does not return the hash in the response.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft

## Depends on / blocks
- Depends on: [DB] Event Creation: albums table for drafts and publish
- Blocks: [FE] Event Creation: Step 2 UI and API wiring

## Test notes (how QA verifies)
- Postman requests.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [BE] Event Creation: POST /api/albums/:id/publish
lane: BE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 2
depends_on: [DB] Event Creation: albums table for drafts and publish

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: none · Lane: BE

## User story
As an organizer, I want to finalize my draft to make it live.

## In scope
- Endpoint `POST /api/albums/:id/publish`
- Sets `status` to 'published'.

## Out of scope (do NOT build)
- Validating if all fields are complete (assume draft is valid if they reach step 4).

## Acceptance criteria
- Given a valid draft ID, when the publish endpoint is called, then the DB status is updated to 'published'.
- Given a valid draft ID, when the publish endpoint is called, then it returns a 200 OK response.
- Given an invalid draft ID, when the publish endpoint is called, then it returns a 404 Not Found error.

## Technical notes
- Endpoint / schema: POST /api/albums/:id/publish

## Depends on / blocks
- Depends on: [DB] Event Creation: albums table for drafts and publish
- Blocks: [FE] Event Creation: Step 4 UI and publish wiring

## Test notes (how QA verifies)
- Postman request.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [FE] Event Creation: Step 1 UI and API wiring
lane: FE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244
screenshots: specs/_figma/event-creation/9810-7244.png

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FE

## User story
As an organizer, I want to enter basic info and proceed to the next step.

## In scope
- Wizard layout, stepper, inputs (Title, Description, Location, Category, Dates).
- Client validation and error states.
- Wire 'Next Step ->' to `POST /api/albums/draft` and navigate.

## Out of scope (do NOT build)
- Other steps.

## Acceptance criteria
- Given empty required fields, when 'Next Step ->' is clicked, then 'This field is required' shows under Title, Location, and Start Date.
- Given valid data, when 'Next Step ->' is clicked, then the POST endpoint is called and the UI navigates to Step 2.
- Given the POST endpoint returns 500, when 'Next Step ->' is clicked, then a generic error message is displayed and the UI stays on Step 1.

## Technical notes
- Endpoint / schema: POST /api/albums/draft
- Mock or fixture for parallel work: intercept POST request with mock ID.

## Depends on / blocks
- Depends on: [BE] Event Creation: POST /api/albums/draft
- Blocks: [FE] Event Creation: Step 2 UI and API wiring

## Test notes (how QA verifies)
- E2E flow.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [FE] Event Creation: Step 2 UI and API wiring
lane: FE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 6
depends_on: [FE] Event Creation: Step 1 UI and API wiring, [BE] Event Creation: PATCH /api/albums/:id/draft
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation/9836-3977.png

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FE

## User story
As an organizer, I want to pick my album's font and color and save it.

## In scope
- Font and Theme Color swatches with visual selection states.
- Mock image upload dropzone.
- Wire 'Next Step ->' to `PATCH /api/albums/:id/draft`.

## Out of scope (do NOT build)
- Preview modal.

## Acceptance criteria
- Given the font selector, when 'Hi Melody' is clicked, then it gets an orange border to indicate selection.
- Given the theme colors, when the orange swatch is clicked, then it is visually marked as selected.
- Given valid selections, when 'Next Step ->' is clicked, then the PATCH endpoint is called and the UI navigates to Step 3.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft

## Depends on / blocks
- Depends on: [FE] Event Creation: Step 1 UI and API wiring, [BE] Event Creation: PATCH /api/albums/:id/draft
- Blocks: [FE] Event Creation: Step 3 UI and API wiring

## Test notes (how QA verifies)
- Visual inspection of selection states.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [FE] Event Creation: Step 2.1 Preview modal
lane: FE
parent: [Feature] Event Creation: Wizard flow
priority: normal
estimate_hours: 5
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730
screenshots: specs/_figma/event-creation/9873-3730.png

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9873-3730 · Lane: FE

## User story
As an organizer, I want to preview my album design.

## In scope
- Preview modal with 'Preview Only' badge and 'Close Preview X' button.
- Applies selected font and theme color classes.
- Dummy grid of photos.

## Out of scope (do NOT build)
- API integration for the preview.

## Acceptance criteria
- Given the 'View Preview' button is clicked on Step 2 or 4, when the modal opens, then the album title uses the selected font class.
- Given the preview modal is open, when 'Close Preview X' is clicked, then the modal closes.
- Given the preview modal is open, when it renders, then a dummy grid of at least 3 photos is displayed.

## Technical notes
- Mock or fixture for parallel work: use local draft state.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Click View Preview on Step 2.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [FE] Event Creation: Step 3 UI and API wiring
lane: FE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 5
depends_on: [FE] Event Creation: Step 2 UI and API wiring, [BE] Event Creation: PATCH /api/albums/:id/draft
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
screenshots: specs/_figma/event-creation/9836-5766.png

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766 · Lane: FE

## User story
As an organizer, I want to set privacy settings.

## In scope
- 5 privacy radio button cards.
- Wire 'Next Step' to PATCH if not password protected.
- If password protected, open Step 3.1 modal.

## Out of scope (do NOT build)
- The password modal UI.

## Acceptance criteria
- Given the radio options, when 'Hidden' is clicked, then its radio button becomes checked (orange dot) and others uncheck.
- Given 'Public' is selected, when 'Next Step ->' is clicked, then the PATCH API is called and the UI navigates to Step 4.
- Given 'Password protected' is selected, when 'Next Step ->' is clicked, then the Set Password modal opens instead of navigating to Step 4.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft

## Depends on / blocks
- Depends on: [FE] Event Creation: Step 2 UI and API wiring, [BE] Event Creation: PATCH /api/albums/:id/draft
- Blocks: [FE] Event Creation: Step 3.1 Password modal

## Test notes (how QA verifies)
- Test radio selection and routing logic.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [FE] Event Creation: Step 3.1 Password modal
lane: FE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 5
depends_on: [FE] Event Creation: Step 3 UI and API wiring, [BE] Event Creation: PATCH /api/albums/:id/draft
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520
screenshots: specs/_figma/event-creation/9836-6520.png

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520 · Lane: FE

## User story
As an organizer, I want to set a password for my album.

## In scope
- Password modal with inputs, show/hide toggle, Save button, 'I'll do this later' link.
- Validation for length and match.
- Wire to PATCH API.

## Out of scope (do NOT build)
- Backend hashing.

## Acceptance criteria
- Given the password inputs, when the values do not match and 'Save' is clicked, then a 'Passwords do not match' error is shown.
- Given a valid matching password >= 8 characters, when 'Save' is clicked, then the PATCH API is called and the UI navigates to Step 4.
- Given the modal is open, when 'I'll do this later.' is clicked, then the UI navigates to Step 4 without calling the PATCH API.

## Technical notes
- Endpoint / schema: PATCH /api/albums/:id/draft

## Depends on / blocks
- Depends on: [FE] Event Creation: Step 3 UI and API wiring, [BE] Event Creation: PATCH /api/albums/:id/draft
- Blocks: [FE] Event Creation: Step 4 UI and publish wiring

## Test notes (how QA verifies)
- Test validation and API request.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [FE] Event Creation: Step 4 UI and publish wiring
lane: FE
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 5
depends_on: [FE] Event Creation: Step 3.1 Password modal, [BE] Event Creation: POST /api/albums/:id/publish
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900
screenshots: specs/_figma/event-creation/9836-6900.png

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6900 · Lane: FE

## User story
As an organizer, I want to review my settings and publish the album.

## In scope
- Summary layout with cover image and details list.
- Edit button returns to Step 1.
- Wire 'Create ->' to `POST /api/albums/:id/publish`.

## Out of scope (do NOT build)
- Dashboard UI.

## Acceptance criteria
- Given the Step 4 screen, when it loads, then it displays the aggregated data matching the draft state (e.g., Title, Date, Privacy).
- Given the screen, when 'Edit' is clicked, then the router navigates back to Step 1.
- Given the screen, when 'Create ->' is clicked, then the POST publish API is called and the user navigates to `/dashboard`.

## Technical notes
- Endpoint / schema: POST /api/albums/:id/publish

## Depends on / blocks
- Depends on: [FE] Event Creation: Step 3.1 Password modal, [BE] Event Creation: POST /api/albums/:id/publish
- Blocks: [QA] Event Creation: E2E test for wizard flow

## Test notes (how QA verifies)
- E2E flow.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end

---ticket
title: [QA] Event Creation: E2E test for wizard flow
lane: QA
parent: [Feature] Event Creation: Wizard flow
priority: high
estimate_hours: 4
depends_on: [FE] Event Creation: Step 4 UI and publish wiring, [INT] Event Creation: Set up Playwright E2E runner

## Context
Parent: [Feature] Event Creation: Wizard flow · Figma: none · Lane: QA

## User story
As a QA engineer, I want to test the entire wizard flow.

## In scope
- E2E test walking through Steps 1, 2, 3, and 4, creating and publishing a draft.

## Out of scope (do NOT build)
- Exhaustive negative tests (done in unit tests).

## Acceptance criteria
- Given Playwright runs, when the test fills Step 1 and clicks Next, then it reaches Step 2.
- Given Playwright runs, when the test fills Step 2 and 3, then it reaches Step 4.
- Given Playwright runs, when the test clicks Create on Step 4, then the album is published and the dashboard loads.

## Technical notes
- Endpoint / schema: none

## Depends on / blocks
- Depends on: [FE] Event Creation: Step 4 UI and publish wiring, [INT] Event Creation: Set up Playwright E2E runner
- Blocks: none

## Test notes (how QA verifies)
- `npx nx e2e frontend`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR merged
---end
