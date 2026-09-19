# Spec: Event Creation Step 2 — Look & Feel

Source: Figma node 9836-3977. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 2 — Look & Feel
lane: FEATURE
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation-step-2/9836-3977.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FEATURE

## User story
As an organizer, I want to customize the look and feel of my event, so that the album matches my event's branding or theme.

## In scope
- Step 2 page/modal in the event creation wizard
- Album cover image upload (optional)
- Font selection from predefined list
- Theme color selection from predefined swatches and custom picker
- Saving selections to the event draft
- Navigation to Step 3 and previewing

## Out of scope (do NOT build)
- Full album viewer implementation
- Advanced CSS customization beyond font/color variables
- Image cropping tools

## Acceptance criteria
- Given the organizer is on Step 2, when they select a cover image, choose "Hi Melody" font, choose the Red theme color, and click "Next Step ->", then the selections are saved to the draft event and the wizard navigates to Step 3 (Access).
- Given the organizer is on Step 2, when they make selections and click "View Preview", then a preview modal or new tab opens showing a sample album with the selected font, color, and cover image.
- Given no album cover is uploaded, when the step is saved, then the event draft records no cover, and the helper text logic applies ("If no album cover is uploaded, the first three uploaded photos become the album thumbnails.").

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft { coverImageId?: string, font?: string, themeColor?: string }
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: Event Creation Step 1
- Blocks: Event Creation Step 3

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Look & Feel: layout font and color selection
lane: FE
parent: [Feature] Event Creation: Step 2 — Look & Feel
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation-step-2/9836-3977.png

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FE

## User story
As an organizer, I want to select my font and colors, so that I can personalize my album.

## In scope
- Progress tracker showing Step 2 active
- Font selection grid with 6 options (Host Grotesk, Honfleur, High Tower, Hubbali, Hi Melody, Helvetica)
- Theme color selection swatches (9 predefined + 1 custom plus button)
- "View Preview" and "Next Step ->" buttons

## Out of scope (do NOT build)
- Image upload component implementation (separate ticket)
- API integration (separate ticket)
- Actual preview generation

## Acceptance criteria
- Given the font grid, when "Aa Hi Melody" is clicked, then it becomes the active selection with a 3px solid `#FF6100` border, and any previously selected font loses its active state.
- Given the color swatches, when the orange swatch (`#FF6100`) is clicked, then it becomes the active selection.
- Given the color swatches, when the `+` button is clicked, then a native color picker or custom input opens to select a hex code.
- Given the footer, when the form is dirty and "Next Step ->" is clicked, then the selections are emitted to the parent wizard component.
- Given the footer, when "View Preview" is clicked, then a preview event is emitted.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: `onNext(data: { font: string, themeColor: string })` prop
- Breakpoints (FE only): Assume desktop layout as per Figma; mobile stacking not explicitly designed but standard responsive flex-wrap applies.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Look & Feel: wire to draft API

## Test notes (how QA verifies)
- `npx nx test frontend` - verify component renders and emits correct values on click.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Look & Feel: cover image upload component
lane: FE
parent: [Feature] Event Creation: Step 2 — Look & Feel
estimate_hours: 5
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation-step-2/9836-3977.png

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FE

## User story
As an organizer, I want to upload a cover image, so my album has a recognizable hero banner.

## In scope
- Drag-and-drop or click-to-upload area with dashed border
- Display of "Recommended: 400x400px."
- Image preview within the upload area once a file is selected
- Display of helper text: "If no album cover is uploaded, the first three uploaded photos become the album thumbnails."

## Out of scope (do NOT build)
- Image cropping or editing
- Direct to S3 upload (handled by backend or separate integration)

## Acceptance criteria
- Given the upload area, when a user drops a valid image file, then a preview of the image is rendered inside the dashed box replacing the placeholder.
- Given the upload area, when a user clicks the area, then the native file browser opens to select an image.
- Given an image is selected, when the component state updates, then the file or file ID is emitted to the parent component.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: `onFileSelected(file: File)` prop
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Look & Feel: wire to draft API

## Test notes (how QA verifies)
- `npx nx test frontend` - verify file selection triggers the emit.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [DB] Look & Feel: add branding columns to events
lane: DB
parent: [Feature] Event Creation: Step 2 — Look & Feel
estimate_hours: 2

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: none · Lane: DB

## User story
As a developer, I want columns for the branding choices, so that the draft API can save them.

## In scope
- One migration adding to `events`: `cover_image_id` (UUID, nullable), `font` (VARCHAR, nullable), `theme_color` (CHAR(7), nullable, hex such as `#FF6100`).

## Out of scope (do NOT build)
- Image upload or storage
- Any column not listed above
- ORM setup (done by `[DB] Basic Info: events table + migration`)

## Acceptance criteria
- Given the Step 1 `events` migration has run, when this migration runs, then `events` has `cover_image_id`, `font` and `theme_color`, all nullable.
- Given existing `events` rows, when this migration runs, then those rows keep their data and the new columns are NULL.
- Given this migration has run, when it is rolled back, then the three columns are removed and no other column changes.

## Technical notes
- Endpoint / schema: `events.cover_image_id UUID NULL`, `events.font VARCHAR NULL`, `events.theme_color CHAR(7) NULL`

## Depends on / blocks
- Depends on (other feature): [DB] Basic Info: events table + migration (Event Creation Step 1)
- Blocks: [BE] Look & Feel: PATCH /api/events/:id/draft saves branding

## Test notes (how QA verifies)
- Run the migration up and down on a fresh database and inspect the `events` columns.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Migration runs up and down cleanly on a fresh database
- [ ] Lint and typecheck clean (`npx nx lint backend`, `npx tsc -p backend/tsconfig.json --noEmit`)
- [ ] PR reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Look & Feel: PATCH /api/events/:id/draft saves branding
lane: BE
parent: [Feature] Event Creation: Step 2 — Look & Feel
estimate_hours: 4
depends_on: [DB] Look & Feel: add branding columns to events

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: none · Lane: BE

## User story
As an organizer, I want my branding choices saved, so they apply to my event.

## In scope
- Update `PATCH /api/events/:id/draft` to accept `coverImageId`, `font`, and `themeColor`
- Validate font enum/string and themeColor hex code

## Out of scope (do NOT build)
- File upload handling endpoint (the FE cover upload ticket supplies `coverImageId`; storage is a separate feature)

## Acceptance criteria
- Given a valid draft ID, when `PATCH /api/events/:id/draft` is called with `{ font: "Hi Melody", themeColor: "#FF6100" }`, then the database updates the draft row and returns 200 OK with the updated object.
- Given an invalid hex code, when `PATCH` is called, then it returns 400 Bad Request.
- Given a request missing `coverImageId`, when `PATCH` is called, then it is accepted and the existing field is updated to null or preserved based on the payload.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft → accept coverImageId (uuid/string), font (string), themeColor (string, hex regex)
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [DB] Look & Feel: add branding columns to events
- Blocks: [FE] Look & Feel: wire to draft API

## Test notes (how QA verifies)
- Run backend unit/integration tests for the PATCH endpoint.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [FE] Look & Feel: wire to draft API
lane: FE
parent: [Feature] Event Creation: Step 2 — Look & Feel
estimate_hours: 3
depends_on: [FE] Look & Feel: layout font and color selection, [FE] Look & Feel: cover image upload component, [BE] Look & Feel: PATCH /api/events/:id/draft saves branding
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
screenshots: specs/_figma/event-creation-step-2/9836-3977.png

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977 · Lane: FE

## User story
As an organizer, I want my selections saved to the server when I proceed.

## In scope
- Combine image upload, font, and color state
- Call `PATCH /api/events/:id/draft` on "Next Step ->"
- Handle API loading and error states

## Out of scope (do NOT build)
- UI layout (already built)

## Acceptance criteria
- Given the form is filled, when "Next Step ->" is clicked, then a loading state shows and `PATCH /api/events/:id/draft` is called.
- Given a successful 200 response, when the call completes, then the wizard router navigates to Step 3.
- Given a 5xx response, when the call fails, then a toast or inline error shows "Could not save. Try again." and the user remains on Step 2.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Look & Feel: layout font and color selection, [FE] Look & Feel: cover image upload component, [BE] Look & Feel: PATCH /api/events/:id/draft saves branding
- Blocks: [QA] Look & Feel: E2E organizer sets branding

## Test notes (how QA verifies)
- Manual QA or E2E test.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Look & Feel: E2E organizer sets branding
lane: QA
parent: [Feature] Event Creation: Step 2 — Look & Feel
estimate_hours: 2
depends_on: [FE] Look & Feel: wire to draft API

## Context
Parent: [Feature] Event Creation: Step 2 — Look & Feel · Figma: none · Lane: QA

## User story
As a QA engineer, I want to ensure the branding step works end-to-end.

## In scope
- Playwright E2E scenario covering Step 2

## Out of scope (do NOT build)
- none

## Acceptance criteria
- Given the E2E runner, when it executes the Step 2 test with full selections, then it successfully uploads an image fixture, selects a font and color, clicks Next, and verifies navigation to Step 3.
- Given the E2E runner, when it skips image upload, then it still successfully navigates to Step 3 and the draft reflects a null cover image.
- Given the API responds with an error, when the runner intercepts and forces a 500, then the error toast is visible and the form does not advance.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none
- Breakpoints (FE only): none

## Depends on / blocks
- Depends on: [FE] Look & Feel: wire to draft API
- Blocks: none

## Test notes (how QA verifies)
- `npx playwright test`

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test <project>`)
- [ ] Lint and typecheck clean (`npx nx lint <project>`, `npx tsc -p <project>/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/<slug>` and reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end
