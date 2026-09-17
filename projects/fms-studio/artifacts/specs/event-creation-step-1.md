# Spec: Event Creation Step 1 - Basic Info

Source: Figma node 9810-7244. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 1 — Basic Info
lane: FEATURE
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244
screenshots: specs/_figma/event-creation-step-1/9810-7244.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FEATURE

## User story
As an organizer, I want to provide the basic details for my event, so that I can create a new album draft and move to the next steps.

## In scope
- Event creation step 1 layout and form.
- Form fields: Album Title, Description, Location, Category, Start Date, End Date.
- Character count validation on Description.
- Required field validation.
- Creating the initial event draft in the database.
- Navigation to Step 2.

## Out of scope (do NOT build)
- Image uploads (later step).
- Access control/passwords (later step).
- Review/Publish logic (later step).
- The rest of the dashboard layout behind the modal.

## Acceptance criteria
- Given the organizer clicks Create Album, when Step 1 opens, then the modal renders with all form fields empty and the 'Next Step' button disabled.
- Given the organizer has filled in all required fields (Album Title, Location, Start Date), when 'Next Step' is clicked, then `POST /api/events/draft` is called with the form data and the wizard navigates to Step 2.
- Given the user types in the Description field, when the length exceeds 255 characters, then the field prevents further typing and the character count shows '255/255'.
- Given a required field is empty when blured, then an error message is shown and the 'Next Step' button remains disabled.

## Technical notes
- Endpoint / schema: `POST /api/events/draft` { title, description?, location, category?, startDate, endDate? } → 201 { id }

## Depends on / blocks
- Depends on: none
- Blocks: Event Creation: Step 2

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [DB] Basic Info: events table + migration
lane: DB
parent: [Feature] Event Creation: Step 1 — Basic Info
estimate_hours: 4

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: DB

## User story
As a developer, I want the events table created, so that the API can persist event drafts.

## In scope
- Set up ORM (e.g., Prisma or TypeORM) since this is the first feature persisting data.
- Create `events` table with columns: id, owner_id, title, description, location, category, start_date, end_date.

## Out of scope (do NOT build)
- Columns for images, passwords, or publish status (will be added in later DB tickets).

## Acceptance criteria
- Given the DB is empty, when the migration runs, then the `events` table is created with the required schema.
- Given the ORM is set up, when the backend starts, then it can connect to the database successfully.
- Given a valid insert command, when executed, then a row is saved in the `events` table.

## Technical notes
- Endpoint / schema: `events` table schema: id (UUID), owner_id (UUID), title (VARCHAR), description (VARCHAR 255), location (VARCHAR), category (VARCHAR), start_date (DATE), end_date (DATE).
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [BE] Basic Info: POST /api/events/draft creates initial draft

## Test notes (how QA verifies)
- Review migration file and verify table schema against AC.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test backend`)
- [ ] Lint and typecheck clean (`npx nx lint backend`, `npx tsc -p backend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/step-1-db` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [BE] Basic Info: POST /api/events/draft creates initial draft
lane: BE
parent: [Feature] Event Creation: Step 1 — Basic Info
estimate_hours: 4
depends_on: [DB] Basic Info: events table + migration

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: BE

## User story
As a frontend application, I want an endpoint to submit the basic info form, so that the initial event draft is saved to the database.

## In scope
- `POST /api/events/draft` endpoint.
- Validation of required fields (title, location, start date) and description length limit (255).
- Persisting to the `events` table.

## Out of scope (do NOT build)
- Authentication/Authorization (will be handled by INT auth later or mocked for now).
- Updates to existing drafts (PATCH endpoint).

## Acceptance criteria
- Given valid payload `{title, location, startDate}`, when `POST /api/events/draft` is called, then the server returns 201 with the new event `{id}`.
- Given a missing required field (e.g., title), when called, then the server returns 400 Bad Request with a validation error.
- Given a description longer than 255 characters, when called, then the server returns 400 Bad Request with a validation error.

## Technical notes
- Endpoint / schema: `POST /api/events/draft` { title: string, description?: string, location: string, category?: string, startDate: ISO8601, endDate?: ISO8601 } → 201 { id: string }
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [DB] Basic Info: events table + migration
- Blocks: [FE] Basic Info: wire Next Step to POST /api/events/draft

## Test notes (how QA verifies)
- Call the endpoint via curl or Postman and verify the responses match the AC.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test backend`)
- [ ] Lint and typecheck clean (`npx nx lint backend`, `npx tsc -p backend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/step-1-be` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Basic Info: form layout + validation states
lane: FE
parent: [Feature] Event Creation: Step 1 — Basic Info
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244
screenshots: specs/_figma/event-creation-step-1/9810-7244.png

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FE

## User story
As an organizer, I want a clear form to enter event details, so that I know what is required.

## In scope
- Modal layout with "Create Album", "Event Details", and the 'x' close button.
- Stepper component showing Step 1 ("Basic Info") active.
- Form inputs: Album Title, Description, Location, Category, Start Date, End Date.
- Client-side validation: required fields, description max length.

## Out of scope (do NOT build)
- API integration (wiring ticket).
- Closing the modal logic.
- Responsive breakpoints beyond standard desktop modal size (Figma is 1408x828).

## Acceptance criteria
- Given the modal opens, when no input is provided, then the 'Next Step' button is disabled.
- Given the 'Album Title*' input is empty, when the user types, then the placeholder 'e.g. philippine-marathon-2025' disappears.
- Given the 'Description (Optional)' textarea, when the user types, then the character count updates up to '255/255' and prevents typing further.
- Given the 'Location*' input, when the user blurs it while empty, then an error state is shown.
- Given the 'Category (Optional)' select, when clicked, then the dropdown options appear.
- Given the 'Start Date*' input, when clicked, then a date picker opens.
- Given the 'End Date (Optional)' input, when clicked, then a date picker opens.
- Given all required fields ('Album Title*', 'Location*', 'Start Date*') are filled, when validated, then the 'Next Step' button is enabled.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: `onNextStep(data: BasicInfoFormData): Promise<void>` prop; page calls it.
- Breakpoints (FE only): Desktop modal.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Basic Info: wire Next Step to POST /api/events/draft

## Test notes (how QA verifies)
- Run component tests for the form validation and layout.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/step-1-fe-layout` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Basic Info: wire Next Step to POST /api/events/draft
lane: FE
parent: [Feature] Event Creation: Step 1 — Basic Info
estimate_hours: 3
depends_on: [FE] Basic Info: form layout + validation states, [BE] Basic Info: POST /api/events/draft creates initial draft
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244
screenshots: specs/_figma/event-creation-step-1/9810-7244.png

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9810-7244 · Lane: FE

## User story
As an organizer, I want my form submission saved, so that I can proceed to Step 2.

## In scope
- Connecting the form submission to `POST /api/events/draft`.
- Handling success by routing to Step 2.
- Handling API errors (e.g., 500 or validation).

## Out of scope (do NOT build)
- Form layout and visual validation states.

## Acceptance criteria
- Given all required fields are filled, when 'Next Step' is clicked, then `POST /api/events/draft` is called with the payload.
- Given the API returns 201, when the request completes, then the application navigates to the Step 2 route.
- Given the API returns an error (e.g., 500), when the request fails, then a generic error message is displayed and the 'Next Step' button is re-enabled.

## Technical notes
- Endpoint / schema: `POST /api/events/draft`
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Basic Info: form layout + validation states, [BE] Basic Info: POST /api/events/draft creates initial draft
- Blocks: [QA] Basic Info: E2E organizer fills basic info and navigates to step 2

## Test notes (how QA verifies)
- Manual QA or E2E tests for the happy path and error path.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/step-1-fe-wiring` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [INT] Setup Playwright E2E runner
lane: INT
parent: [Feature] Event Creation: Step 1 — Basic Info
estimate_hours: 4
parallel: true

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: INT

## User story
As an engineer, I want the E2E testing framework set up, so that QA can verify features end-to-end.

## In scope
- Install and configure Playwright.
- Set up a basic smoke test to ensure Playwright runs against the frontend application.
- Add npm scripts to run tests locally and in CI.

## Out of scope (do NOT build)
- Writing all E2E scenarios for every feature.

## Acceptance criteria
- Given the repository is cloned, when `npx playwright test` is run, then Playwright executes tests against the frontend and passes.
- Given a CI environment, when the pipeline runs, then Playwright tests are executed.
- Given a failing test, when the pipeline runs, then the CI step fails.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Basic Info: E2E organizer fills basic info and navigates to step 2

## Test notes (how QA verifies)
- Run `npx playwright test` locally.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Playwright configured
- [ ] PR opened from `feature/setup-playwright` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [QA] Basic Info: E2E organizer fills basic info and navigates to step 2
lane: QA
parent: [Feature] Event Creation: Step 1 — Basic Info
estimate_hours: 3
depends_on: [FE] Basic Info: wire Next Step to POST /api/events/draft, [INT] Setup Playwright E2E runner

## Context
Parent: [Feature] Event Creation: Step 1 — Basic Info · Figma: none · Lane: QA

## User story
As QA, I want an automated test for Step 1, so that regressions are caught early.

## In scope
- Playwright E2E scenario covering the happy path of filling out Step 1 and proceeding to Step 2.

## Out of scope (do NOT build)
- Edge cases and exhaustive validation tests (handled by FE component tests).

## Acceptance criteria
- Given the application is running, when the E2E test executes, then it opens the modal, fills Album Title, Location, and Start Date, clicks Next Step, and verifies navigation to Step 2.
- Given the application is running, when the required fields are missing, then the 'Next Step' button remains disabled in the test.
- Given the application is running, when a description of length > 255 is typed, then the test verifies the input is truncated and the character limit is enforced.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Basic Info: wire Next Step to POST /api/events/draft, [INT] Setup Playwright E2E runner
- Blocks: none

## Test notes (how QA verifies)
- Run `npx playwright test` and observe the test passes.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR opened from `feature/step-1-qa` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end
