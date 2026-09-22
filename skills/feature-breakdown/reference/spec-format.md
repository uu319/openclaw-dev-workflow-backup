# Spec file format (parsed by scripts/clickup_push.py)

One spec file per feature at `projects/<project>/artifacts/specs/<feature-slug>.md`.

Rules:
- The file starts with a `# ` heading (free text, ignored by the script).
- Each ticket is a fenced block that begins with a line `---ticket` and ends
  with a line `---end`. Inside: a YAML-ish key/value header, a blank line, then
  the markdown body (the ticket template).
- The **first** ticket must be the parent (`lane: FEATURE`). Every other ticket
  must have `parent:` equal to the parent's `title`.
- `title` is the dedupe key. The script matches it exactly (case-sensitive)
  against existing task names in the list, so keep titles stable across runs.

Header keys:

| key | required | values |
|---|---|---|
| `title` | yes | full ticket title, e.g. `[FE] Set password: form layout + validation states` |
| `lane` | yes | `FEATURE`, `FE`, `BE`, `DB`, `INT`, `QA`, `SPIKE` |
| `parent` | subtasks | exact `title` of the parent ticket |
| `priority` | no | `urgent`, `high`, `normal` (default), `low` |
| `estimate_hours` | subtasks | number ≤ 8 (script refuses larger) |
| `tags` | no | comma-separated extra tags; lane tag and `agent-created` are added automatically |
| `depends_on` | no | comma-separated titles of tickets in this spec |
| `parallel` | no | `true` if it can start before its dependencies land (against a mock) |
| `status` | no | status for a ticket when it is first created (ignored on re-push; move statuses with clickup_status.py) |
| `figma` | `FEATURE`, `FE` (when the project has a Figma file) | comma-separated Figma frame URLs with `node-id`, the frames this ticket implements |
| `screenshots` | `FEATURE`, `FE` (when the project has a Figma file) | comma-separated PNG paths relative to Internal Artifacts, e.g. `specs/_figma/<feature-slug>/9884-4390.png` (from `download_figma_images`). Uploaded as ClickUp attachments and embedded in a generated `## Design` section |
| `assets` | `FE` (when the project has a Figma file) | one path, relative to Internal Artifacts, to the feature's asset manifest, e.g. `specs/_figma/<feature-slug>/assets/manifest.json` (written in Step 1.5). Every file it lists must exist and be non-empty. An empty `"assets": []` is valid and means "this screen is CSS only" |
| `existing_id` | no | tracker ticket id to update when the title differs from the existing ticket (used when adopting tickets people already made) |

## Complete example

```markdown
# Spec: Event Creation Step 3.1 — Set event password

Source: Figma node 9836-6520. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Event Creation: Step 3.1 — Set event password
lane: FEATURE
priority: high
existing_id: <existing ticket id>
figma: https://www.figma.com/design/<file-key>/<File-Name>?node-id=<node-id>
screenshots: specs/_figma/event-creation-step-3-1-set-password/9836-6520.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/<file-key>/<File-Name>?node-id=<node-id> · Lane: FEATURE

## User story
As an organizer, I want to set a password on my event, so that only invited guests can open the album.

## In scope
- Password entry step in the event-creation wizard
- Persisting the password hash on the event draft
- Continue / Back navigation to steps 3 and 4

## Out of scope (do NOT build)
- Guest-side password prompt (separate feature)
- Password reset or "forgot password"
- Password strength meter beyond the length rule

## Acceptance criteria
- Given the organizer is on step 3.1, when the password field has ≥ 8 characters and Continue is clicked, then `PATCH /api/events/:id/draft` is called with `{ passwordSet: true }` and the wizard navigates to step 4.
- Given fewer than 8 characters, when the field is blurred, then 'Use at least 8 characters' shows under the field and Continue is disabled.
- Given the API returns 5xx, when Continue is clicked, then the `<FormError>` text 'Could not save. Try again.' shows and the entered value is kept.

## Technical notes
- Files/paths: frontend/src/app/events/new/step-3-1/ · backend/src/app/events/
- Endpoint / schema: PATCH /api/events/:id/draft { password: string } → 200 { id, passwordSet: true }

## Depends on / blocks
- Depends on: none
- Blocks: Event Creation Step 4

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Set password: form layout + validation states
lane: FE
parent: [Feature] Event Creation: Step 3.1 — Set event password
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/<file-key>/<File-Name>?node-id=<node-id>
screenshots: specs/_figma/event-creation-step-3-1-set-password/9836-6520.png
assets: specs/_figma/event-creation-step-3-1-set-password/assets/manifest.json

## Context
Parent: [Feature] Event Creation: Step 3.1 — Set event password · Figma: https://www.figma.com/design/<file-key>/<File-Name>?node-id=<node-id> · Lane: FE

## User story
As an organizer, I want a clear password step, so that I know what is required before I continue.

## In scope
- Page route `frontend/src/app/events/new/step-3-1/page.tsx`
- Password input with show/hide toggle, helper text, error text, Back and Continue buttons
- Client-side length validation (≥ 8)

## Out of scope (do NOT build)
- Calling the API (that is the wiring ticket)
- Strength meter, confirm-password field

## Acceptance criteria
- Given the page loads, when no input is given, then Continue is disabled and helper text 'At least 8 characters' is visible.
- Given 7 characters, when the field blurs, then 'Use at least 8 characters' renders in `text-red-600` under the field.
- Given ≥ 8 characters, when typed, then the error clears and Continue is enabled.
- Given a viewport narrower than 640px, when the Set Password step renders, then the form is full-width with 16px side padding; given 640px or wider, it is centered at max-width 480px.

## Design fidelity
- Tokens: Primary `#FF6100` · Text `#313131` · Error `#DC2626` · Font `Host Grotesk` 400/500, 16px body / 26px heading · Radius 8px
- Assets (from `specs/_figma/event-creation-step-3-1-set-password/assets/manifest.json`, copy into the repo at these paths):
  - `assets/icon-eye.svg` → `frontend/public/icons/eye.svg` — show/hide toggle, 24x24
  - `assets/icon-eye-off.svg` → `frontend/public/icons/eye-off.svg` — show/hide toggle, 24x24
- No placeholders: every asset above is rendered by the code.

## Technical notes
- Files/paths: frontend/src/app/events/new/step-3-1/page.tsx, frontend/src/components/PasswordField.tsx
- Mock or fixture for parallel work: `onContinue(password: string): Promise<void>` prop; page calls it, parent wiring ticket supplies the real one.
- Breakpoints: mobile <640px full width; ≥640px centered 480px.

## Depends on / blocks
- Depends on: none
- Blocks: [FE] Set password: wire Continue to PATCH /api/events/:id/draft

## Test notes (how QA verifies)
- `npx nx test frontend --testFile=step-3-1` covers the three validation states.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Every asset in `## Design fidelity` is committed at its stated repo path and rendered; no placeholders
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR from `feature/set-password-form` reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [BE] Set password: PATCH /api/events/:id/draft stores password hash
lane: BE
parent: [Feature] Event Creation: Step 3.1 — Set event password
priority: high
estimate_hours: 5

...body per template...
---end

---ticket
title: [FE] Set password: wire Continue to PATCH /api/events/:id/draft
lane: FE
parent: [Feature] Event Creation: Step 3.1 — Set event password
estimate_hours: 3
depends_on: [FE] Set password: form layout + validation states, [BE] Set password: PATCH /api/events/:id/draft stores password hash
figma: https://www.figma.com/design/<file-key>/<File-Name>?node-id=<node-id>
screenshots: specs/_figma/event-creation-step-3-1-set-password/9836-6520.png

...body per template...
---end

---ticket
title: [QA] Set password: E2E organizer sets password and reaches step 4
lane: QA
parent: [Feature] Event Creation: Step 3.1 — Set event password
estimate_hours: 3
depends_on: [FE] Set password: wire Continue to PATCH /api/events/:id/draft

...body per template...
---end
```
