# Spec: Credits Added Success Modal

Source: Figma node 9884-4390. Written 2026-09-16 by VanPM.

---ticket
title: [Feature] Top Up: Credits Added Success Modal
lane: FEATURE
priority: normal
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-4390
screenshots: specs/_figma/credits-added-success/9884-4390.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-4390 · Lane: FEATURE

## User story
As an organizer who just purchased credits, I want to see a confirmation screen with my new total balance, so that I know the transaction succeeded.

## In scope
- Showing a success modal immediately after a successful credit purchase.
- Displaying the amount of credits purchased in the message.
- Displaying the new total available balance.
- Dismissing the modal to return to the dashboard.

## Out of scope (do NOT build)
- The actual Stripe/payment processing flow (handled in the checkout feature).
- Viewing billing history or invoices.

## Acceptance criteria
- Given a successful credit purchase completes, when the modal opens, then the heading 'Credits Added!' and text '<amount> credits have been added to your account.' are visible.
- Given a successful purchase, when the modal opens, then the light gray box shows the new total credits available in orange bold text.
- Given the modal is open, when the 'Done' button or the 'x' close icon is clicked, then the modal dismisses and the user is on the dashboard.

## Technical notes
- Expects to receive `purchasedAmount` and `newTotalBalance` as props or from a global state/context following a successful purchase redirect/callback.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Credits Added Success: modal layout and dismissal
lane: FE
parent: [Feature] Top Up: Credits Added Success Modal
priority: normal
estimate_hours: 4
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-4390
screenshots: specs/_figma/credits-added-success/9884-4390.png

## Context
Parent: [Feature] Top Up: Credits Added Success Modal · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-4390 · Lane: FE

## User story
As an organizer who just purchased credits, I want a clear confirmation modal showing what was added and my new total.

## In scope
- Modal component `CreditsAddedModal.tsx`.
- Orange checkmark success icon.
- Dynamic message text: "[X] credits have been added to your account."
- Gray summary box showing the new total balance in large orange text.
- 'Done' button and 'x' icon to close the modal.

## Out of scope (do NOT build)
- API integration for fetching the balance (use props for now).
- The payment flow itself.

## Acceptance criteria
- Given `purchasedAmount=5000` and `newTotalBalance=5420`, when the modal renders, then the text '5,000 credits have been added to your account.' is visible.
- Given `newTotalBalance=5420`, when the modal renders, then '5,420' is visible in the gray box above 'credits available'.
- Given the modal is open, when the 'Done' button is clicked, then the `onClose` callback is triggered.
- Given the modal is open, when the 'x' icon is clicked, then the `onClose` callback is triggered.

## Technical notes
- Props: `isOpen: boolean`, `onClose: () => void`, `purchasedAmount: number`, `newTotalBalance: number`.
- The orange gradient for the button is `linear-gradient(180deg, rgba(255, 100, 4, 1) 0%, rgba(255, 135, 57, 1) 100%)`.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Component tests covering the rendering of dynamic numbers and the `onClose` triggers for both buttons.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [QA] Credits Added Success: E2E user sees success modal and dismisses it
lane: QA
parent: [Feature] Top Up: Credits Added Success Modal
estimate_hours: 2
depends_on: [FE] Credits Added Success: modal layout and dismissal

## Context
Parent: [Feature] Top Up: Credits Added Success Modal · Lane: QA

## User story
As QA, I want to verify the success modal renders correctly after a simulated purchase and can be dismissed.

## In scope
- Playwright test triggering the modal (can be mocked/triggered via a test route or state manipulation for now if the checkout flow isn't complete).
- Verifying the displayed numbers match the expected state.
- Verifying the modal closes.

## Out of scope (do NOT build)
- E2E testing a real Stripe transaction.

## Acceptance criteria
- Given the test environment, when the success modal is triggered with a 5000 purchase and 5420 total, then the modal appears with the exact text '5,000 credits have been added to your account.' and '5,420'.
- Given the test environment, when the modal is triggered with a 100 purchase and 520 total, then the modal appears with the exact text '100 credits have been added to your account.' and '520'.
- Given the modal is visible, when the user clicks 'Done', then the modal is no longer visible in the DOM.

## Technical notes

## Depends on / blocks
- Depends on: [FE] Credits Added Success: modal layout and dismissal
- Blocks: none

## Test notes (how QA verifies)
- Playwright runner executes successfully.

## Definition of done
- [ ] Test written and passing in CI
- [ ] Ticket closed
---end