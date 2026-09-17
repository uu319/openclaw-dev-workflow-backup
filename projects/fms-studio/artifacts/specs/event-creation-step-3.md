# Spec: Event Creation Step 3

Source: Figma node 9836-5766. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 3 — Privacy and Access
lane: FEATURE
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
screenshots: specs/_figma/event-creation-step-3/9836-5766.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766 · Lane: FEATURE

## User story
As an organizer, I want to set the privacy and access level for my new event album, so that I can control who can find, view, and claim photos.

## In scope
- Privacy and Access selection step (Step 3) in the event creation wizard
- Persisting the selected privacy level to the event draft
- Navigation (Next Step, Close)
- Five privacy options: Public, Hidden, Link only, Restricted, Password protected

## Out of scope (do NOT build)
- The sub-flows for configuring "Password protected" or "Restricted" (those are handled in step 3.1, etc.)
- Enforcing the privacy rules on the guest side
- Editing privacy after creation (this is just the creation wizard)

## Acceptance criteria
- Given the organizer is on step 3 of event creation, when they select "Public (Default)" and click "Next Step →", then `PATCH /api/events/:id/draft` is called with `{ privacy: 'public' }` and the wizard navigates to step 4.
- Given the organizer is on step 3, when they select "Hidden" and click "Next Step →", then the draft is updated with `{ privacy: 'hidden' }` and the wizard navigates to step 4.
- Given the organizer is on step 3, when they select "Link only" and click "Next Step →", then the draft is updated with `{ privacy: 'link-only' }` and the wizard navigates to step 4.
- Given the organizer is on step 3, when they select "Restricted" and click "Next Step →", then the draft is updated with `{ privacy: 'restricted' }` and the wizard navigates to the Restricted configuration sub-step.
- Given the organizer is on step 3, when they select "Password protected" and click "Next Step →", then the draft is updated with `{ privacy: 'password' }` and the wizard navigates to the Password configuration sub-step (step 3.1).
- Given the organizer is on step 3, when they click the "X" close icon, then they are prompted to confirm discarding the draft.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft { privacy: 'public' | 'hidden' | 'link-only' | 'restricted' | 'password' }

## Depends on / blocks
- Depends on: Event Creation Step 2
- Blocks: Event Creation Step 4, Event Creation Step 3.1

## Test notes (how QA verifies)
- Run the [QA] E2E scenario for Step 3.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Step 3 Privacy: form layout and state selection
lane: FE
parent: [Feature] Event Creation: Step 3 — Privacy and Access
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
screenshots: specs/_figma/event-creation-step-3/9836-5766.png

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766 · Lane: FE

## User story
As an organizer, I want to clearly see and select the privacy options for my album, so that I can make an informed choice before continuing.

## In scope
- Page route `frontend/src/app/events/new/step-3/page.tsx`
- Wizard header with close icon ("X")
- Progress indicator showing step 3 ("Access") as current
- Title ("Privacy and Access") and helper text
- Grid of 5 selectable privacy option cards
- "Next Step →" button

## Out of scope (do NOT build)
- Calling the API to save the selection (wiring ticket handles this)
- Implementing the logic for the "X" close confirmation modal (just call the shared wizard context method)

## Acceptance criteria
- Given the page loads, when no prior selection exists, then the "Public (Default)" card is visually selected (filled orange radio button) and the others are unselected (empty grey circle).
- Given the page is loaded, when the user clicks the "Hidden" card, then the radio button on the "Hidden" card becomes filled orange, the "Public" radio becomes empty, and the internal state updates to 'hidden'.
- Given the page is loaded, when the user clicks the "Link only" card, then its radio button becomes filled orange and the internal state updates to 'link-only'.
- Given the page is loaded, when the user clicks the "Restricted" card, then its radio button becomes filled orange and the internal state updates to 'restricted'.
- Given the page is loaded, when the user clicks the "Password protected" card, then its radio button becomes filled orange and the internal state updates to 'password'.
- Given any valid selection, when the "Next Step →" button is clicked, then the provided `onContinue(privacyState)` mock function is called with the current selection.
- Given a viewport narrower than 640px, when the privacy options render, then they appear in a 1-column layout; given wider than 640px, they appear in a 2-column grid.

## Technical notes
- Files/paths: frontend/src/app/events/new/step-3/page.tsx, frontend/src/components/PrivacyCard.tsx
- Mock or fixture for parallel work: `onContinue(privacy: string): Promise<void>` prop; page calls it, parent wiring ticket supplies the real one.
- Breakpoints (FE only): mobile <640px: 1 column, tablet/desktop >640px: 2 columns.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Step 3 Privacy: wire Next Step to PATCH /api/events/:id/draft

## Test notes (how QA verifies)
- `npx nx test frontend --testFile=step-3` covering default selection and changing selections.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/step-3-layout` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [BE] Step 3 Privacy: PATCH /api/events/:id/draft stores privacy setting
lane: BE
parent: [Feature] Event Creation: Step 3 — Privacy and Access
estimate_hours: 4

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: none · Lane: BE

## User story
As an organizer, I want my selected privacy setting saved to my event draft, so that it applies when I publish the album.

## In scope
- Updating the `PATCH /api/events/:id/draft` endpoint to accept and validate the `privacy` field.
- Saving the field to the database draft record.

## Out of scope (do NOT build)
- Enforcing the privacy settings on album read endpoints (handled in a separate feature).

## Acceptance criteria
- Given an authenticated organizer and a valid draft ID, when `PATCH /api/events/:id/draft` is called with `{ "privacy": "hidden" }`, then the database draft record is updated and the endpoint returns 200 OK with the updated draft object.
- Given the payload contains `{ "privacy": "invalid-option" }`, when the endpoint is called, then it returns 400 Bad Request with a validation error message.
- Given the payload contains `{ "privacy": "password" }`, when the endpoint is called, then the database draft record is updated to 'password' and returns 200 OK.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft { privacy: 'public' | 'hidden' | 'link-only' | 'restricted' | 'password' }
- Requires adding `privacy` column/field to the Event/Draft schema if not present.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Step 3 Privacy: wire Next Step to PATCH /api/events/:id/draft

## Test notes (how QA verifies)
- Send valid and invalid PATCH requests via API client and verify database state and response codes.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test backend`)
- [ ] Lint and typecheck clean (`npx nx lint backend`, `npx tsc -p backend/tsconfig.json --noEmit`)
- [ ] PR opened and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Step 3 Privacy: wire Next Step to PATCH /api/events/:id/draft
lane: FE
parent: [Feature] Event Creation: Step 3 — Privacy and Access
estimate_hours: 3
depends_on: [FE] Step 3 Privacy: form layout and state selection, [BE] Step 3 Privacy: PATCH /api/events/:id/draft stores privacy setting
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
screenshots: specs/_figma/event-creation-step-3/9836-5766.png

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766 · Lane: FE

## User story
As an organizer, I want my privacy selection actually saved when I proceed, so that I can finish creating my event.

## In scope
- Connecting the "Next Step →" button in step 3 to the `PATCH /api/events/:id/draft` endpoint.
- Handling success navigation (routing to step 4, or sub-steps 3.1/restricted based on selection).
- Handling API errors.

## Out of scope (do NOT build)
- UI layout and state management (handled in layout ticket).

## Acceptance criteria
- Given the user has selected "Public (Default)", when they click "Next Step →", then a PATCH request is sent to `/api/events/:id/draft` with `{ privacy: 'public' }` and upon 200 OK, the app router navigates to `/events/new/step-4`.
- Given the user has selected "Password protected", when they click "Next Step →", then a PATCH request is sent with `{ privacy: 'password' }` and upon 200 OK, the app router navigates to the password configuration step (`/events/new/step-3-password` or equivalent).
- Given the API returns a 5xx or network error, when "Next Step →" is clicked, then a toast or inline error message "Failed to save privacy settings. Please try again." is displayed and navigation does not occur.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft

## Depends on / blocks
- Depends on: [FE] Step 3 Privacy: form layout and state selection, [BE] Step 3 Privacy: PATCH /api/events/:id/draft stores privacy setting
- Blocks: [QA] Step 3 Privacy: E2E organizer sets privacy level

## Test notes (how QA verifies)
- Run the app, select a privacy level, click Next, and verify the network request and correct navigation in the browser.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [QA] Step 3 Privacy: E2E organizer sets privacy level
lane: QA
parent: [Feature] Event Creation: Step 3 — Privacy and Access
estimate_hours: 3
depends_on: [FE] Step 3 Privacy: wire Next Step to PATCH /api/events/:id/draft

## Context
Parent: [Feature] Event Creation: Step 3 — Privacy and Access · Figma: none · Lane: QA

## User story
As a QA engineer, I want an automated end-to-end test for Step 3, so that regressions in privacy selection are caught.

## In scope
- Playwright E2E scenario covering Step 3 of the event creation wizard.

## Out of scope (do NOT build)
- E2E tests for other steps.

## Acceptance criteria
- Given the E2E runner starts at step 3, when the script selects "Public (Default)" and clicks "Next Step →", then it verifies the network request payload and asserts that the URL changes to step 4.
- Given the E2E runner starts at step 3, when the script selects "Hidden" and clicks "Next Step →", then it verifies the network request payload and asserts that the URL changes to step 4.
- Given the E2E runner starts at step 3, when the script selects "Password protected" and clicks "Next Step →", then it verifies the network payload and asserts that the URL changes to the password config sub-step.

## Technical notes
- Endpoint / schema: none
- Mock or fixture for parallel work: none

## Depends on / blocks
- Depends on: [FE] Step 3 Privacy: wire Next Step to PATCH /api/events/:id/draft
- Blocks: none

## Test notes (how QA verifies)
- `npx nx e2e frontend-e2e` runs the new scenarios successfully.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR opened and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end