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
- Given the organizer is on the Set Password modal, when 'Save' is clicked with matching passwords ≥ 8 characters, then `PATCH /api/events/:id/draft` is called with the password and the wizard navigates to Step 4.
- Given passwords do not match, when 'Save' is clicked, then 'Passwords do not match' shows and submission is blocked.
- Given the modal renders, when 'I'll do this later.' is clicked, then the wizard navigates to Step 4 without calling the PATCH password endpoint.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft { password: string } -> 200

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
- Add `password_hash` column to `events` (an album is an `events` row; see `_planned-data.md`).
- Migration script.

## Out of scope (do NOT build)
- Plaintext password column.

## Acceptance criteria
- Given the migration runs, when complete, then `password_hash` exists on the `events` table.
- Given the migration rollback runs, when complete, then `password_hash` is removed from the `events` table.
- Given the application starts, when the ORM synchronizes, then it successfully maps the `password_hash` column.

## Technical notes
- Endpoint / schema: table `events` (`password_hash` varchar nullable)

## Depends on / blocks
- Depends on (other feature): [DB] Basic Info: events table + migration (Event Creation Step 1)
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
- Update `PATCH /api/events/:id/draft` to accept `password`.
- Hash the password using bcrypt before saving to `password_hash`.

## Out of scope (do NOT build)
- Returning the hash in responses.

## Acceptance criteria
- Given a payload with `password`, when PATCH is called, then the DB `password_hash` is updated with a bcrypt hash, and 200 is returned without the hash in the body.
- Given a payload with an empty `password`, when PATCH is called, then the endpoint returns a 400 Bad Request.
- Given a valid request, when the database update fails, then the endpoint returns a 500 Internal Server Error.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft
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
- Given the modal renders, when 'I'll do this later.' is clicked, then `onSkip()` is called.
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
- Wire modal `onSave` to `PATCH /api/events/:id/draft`.
- Navigate to Step 4 on success.
- Wire `onSkip` to navigate to Step 4 without calling the API.

## Out of scope (do NOT build)
- Modal UI

## Acceptance criteria
- Given a valid password, when 'Save' is clicked, then PATCH is called. Upon 200 OK, the modal closes and the URL changes to Step 4.
- Given the modal renders, when 'I'll do this later.' is clicked, then the URL changes to Step 4.
- Given an invalid password, when 'Save' is clicked, then PATCH is not called and the user remains on the modal.

## Technical notes
- Endpoint / schema: PATCH /api/events/:id/draft

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
- Given the user provides an invalid password, when 'Save' is clicked, then an error state is visible to the user.

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
