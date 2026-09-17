# Organizer Flow: Buying Credits

---ticket
title: [Feature] Organizer Dashboard: Buying Credits
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-4376, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-3930, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-3853
screenshots: specs/_figma/buying-credits/9878-4376.png, specs/_figma/buying-credits/9878-3930.png, specs/_figma/buying-credits/9884-3853.png

## Context
Organizers need to purchase credits to upload photos. This flow allows them to view credit packages, select an amount, and enter payment details to complete the purchase directly from their dashboard.

## User story
As an organizer, I want to buy credits so that I can continue uploading photos to my albums.

## In scope
- Dashboard entry points ("Buy Credits" and "Top Up +").
- Package selection modal showing available credit tiers and pricing.
- Payment details modal to collect credit card information.
- Integrating with the backend to initiate and complete a purchase.
- Navigation handoff to the success screen (`artifacts/specs/credits-added-success.md`).

## Out of scope
- Processing PayPal or Apple Pay (UI placeholders only for this ticket, unless specified in INT).
- Subscription billing (this is a one-off purchase).
- The "Contact Us" actual messaging flow (assume it links out or opens a separate known modal not covered here).
- Building the Success Modal (this is covered by `artifacts/specs/credits-added-success.md`).

## Acceptance criteria
- Given the organizer is on the Dashboard, when they click "Buy Credits" or "Top Up +", then the "Buy Credits" modal opens.
- Given the "Buy Credits" modal is open, when the user views the current status, then they see "Current Balance" and their existing credit count (e.g., "420 credits").
- Given the "Buy Credits" modal, when viewing packages, then the options "3,000 credits" ($150.00), "5,000 credits" ($250.00), "10,000 credits" ($500.00), and "15,000 credits" ($750.00) are visible.
- Given a package is selected on the "Buy Credits" modal, when the user clicks "Buy Now", then the "Payment Details" modal opens.
- Given the "Payment Details" modal is open, when the user views the order summary, then they see the selected "Package", "Current balance", expected "New balance", and "Total due".
- Given the "Payment Details" modal is open, when the user enters details into "Name on Card*", "Card Number*", "Expiry*", and "CVC*" and clicks "Complete Purchase", then the payment is submitted.
- Given the payment is successful, when the process completes, then the system transitions to the Credits Added success modal.
- Given any modal is open, when the user clicks "Cancel" or the "x" icon, then the modal closes and the user remains on the Dashboard.

## Technical notes
- We need to integrate a payment provider (e.g., Stripe) to handle the actual card processing.
- The `[FE]` layer should use a generic modal component if available, or build one that can swap contents between package selection and payment details.
- `[FE]` Note: The Figma placeholder for "Card Number*" is "e.g Juan dela Cruz"; developers should use a standard card number placeholder instead.

## Depends on/blocks
- Blocks the actual uploading of photos if credits are zero.
- Hands off to the Success Modal (feature `credits-added-success`).

## Test notes
- Verify the modal opens from both dashboard entry points.
- Verify the math in the Payment Details summary ("Current balance" + "Package" = "New balance").
- Use test credit card numbers to verify successful and failed transactions.

## Definition of done
- Modals match the design (layout, typography, colors).
- End-to-end flow from dashboard to payment submission works with mocked or test gateway data.
- E2E tests pass.
---end

---ticket
title: [FE] Buying Credits: Modals and Dashboard Entry
lane: FE
parent: [Feature] Organizer Dashboard: Buying Credits
estimate_hours: 8
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-4376, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-3930, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-3853
screenshots: specs/_figma/buying-credits/9878-4376.png, specs/_figma/buying-credits/9878-3930.png, specs/_figma/buying-credits/9884-3853.png

## Context
Implement the UI for the package selection and payment details modals, and wire up the entry buttons on the dashboard.

figma:
- https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-4376
- https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-3930
- https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-3853

screenshots:
- specs/_figma/buying-credits/9878:4376.png
- specs/_figma/buying-credits/9878:3930.png
- specs/_figma/buying-credits/9884:3853.png

## User story
As an organizer, I need to see the credit packages, select one, and enter my card details in a clean interface.

## In scope
- "Buy Credits" button in the top nav and "Top Up +" pill on the dashboard.
- "Buy Credits" modal (Package Selection).
- "Payment Details" modal (Card Form).
- Form validation states (empty, invalid card number/expiry).
- Calling the backend API to initiate/complete the transaction.

## Out of scope
- Implementing the "Paypal" or "Apple" pay flows (UI tabs can be present but disabled/mocked).
- The actual success modal UI (use a router push or callback to trigger the existing success modal).

## Acceptance criteria
- Given the Dashboard, when the user clicks the "Top Up +" pill or "Buy Credits" button, then the "Buy Credits" modal is displayed.
- Given the "Buy Credits" modal, when it renders, then it shows "Current Balance" and the current credit amount.
- Given the package options ("3,000 credits", "5,000 credits", "10,000 credits", "15,000 credits"), when the user selects one and clicks "Buy Now", then the "Payment Details" modal replaces it.
- Given the "Buy Credits" modal, when the user clicks the "Contact Us" button, then the expected contact action occurs (e.g., mailto link).
- Given the "Payment Details" modal, when it renders, then the summary block accurately reflects the selected package and calculates the "New balance".
- Given the "Payment Details" modal, when the user clicks "Cancel", then the modal closes.
- Given the "Payment Details" modal, when the user attempts to click "Complete Purchase" with empty fields ("Name on Card*", "Card Number*", "Expiry*", "CVC*"), then validation errors are shown.
- Given valid card details, when the user clicks "Complete Purchase", then a loading state is shown while the transaction processes, followed by a handoff to the success flow.

## Technical notes
- Use a state machine or simple React state to toggle between the `PACKAGE_SELECTION` and `PAYMENT_DETAILS` modal views.
- If using Stripe, integrate `@stripe/react-stripe-js` Elements for the card inputs to handle PCI compliance and validation automatically.

## Depends on/blocks
- Depends on `[BE] Buying Credits: Checkout endpoints`.

## Test notes
- Verify all buttons and inputs have the exact labels from Figma.
- Verify validation messages appear on blur or submit.

## Definition of done
- UI matches the provided screenshots.
- User can navigate from dashboard to payment submission.
---end

---ticket
title: [BE] Buying Credits: Checkout endpoints
lane: BE
parent: [Feature] Organizer Dashboard: Buying Credits
estimate_hours: 6

## Context
The backend needs to provide available packages, handle checkout intent creation, and confirm payments to add credits to the user's account.

## User story
As an application, I need secure endpoints to process payments and update user credit balances.

## In scope
- Endpoint to fetch current balance (if not already existing on a user/me endpoint).
- Endpoint to create a checkout session or payment intent.
- Endpoint (or webhook) to confirm payment success and increment the user's credit balance.

## Out of scope
- Refund logic.
- Subscription logic.

## Acceptance criteria
- Given an authenticated user, when they request available packages, then the API returns the configured packages (3000, 5000, 10000, 15000) and their prices.
- Given an authenticated user, when they submit a request to purchase a specific package, then the API communicates with the payment provider to create a payment intent.
- Given a successful payment confirmation (via direct API call or webhook), when the payload is validated, then the user's credit balance is incremented by the purchased package amount.
- Given a failed payment, when the provider reports the failure, then the user's balance remains unchanged and an error is logged.

## Technical notes
- Integrate with the chosen payment provider's SDK (e.g., Stripe SDK for Node.js/NestJS).
- Ensure idempotency on the payment confirmation endpoint to prevent double-crediting if a webhook fires multiple times.

## Depends on/blocks
- Depends on `[INT] Set up Payment Provider (Stripe)`.
- Blocks `[FE] Buying Credits: Modals and Dashboard Entry`.

## Test notes
- Unit test the balance increment logic.
- Mock the payment provider to test success and failure paths.

## Definition of done
- Endpoints are documented (Swagger/OpenAPI).
- Tests pass.
---end

---ticket
title: [DB] Buying Credits: Transactions table
lane: DB
parent: [Feature] Organizer Dashboard: Buying Credits
estimate_hours: 2

## Context
We need to record every credit purchase for auditing and history purposes.

## User story
As a system administrator, I need a record of all credit purchases so that I can audit revenue and user balances.

## In scope
- Creating a `transactions` (or `credit_purchases`) table.
- Updating the user table if a `credits_balance` column doesn't exist yet.

## Out of scope
- Invoicing generation.

## Acceptance criteria
- Given a new database migration, when it runs, then a `transactions` table is created with columns for `id`, `user_id`, `amount_cents`, `credits_added`, `provider_reference`, `status`, and `created_at`.
- Given the user model, when the migration runs, then ensuring a `credits_balance` integer column exists.
- Given a rollback command, when the down migration runs, then the `transactions` table is dropped and `credits_balance` column is removed.

## Technical notes
- Ensure `user_id` has a foreign key constraint referencing the users table.

## Depends on/blocks
- Blocks `[BE] Buying Credits: Checkout endpoints`.

## Test notes
- Verify the migration runs cleanly up and down.

## Definition of done
- Migration is committed.
- Schema reflects the new table and columns.
---end

---ticket
title: [INT] Set up Payment Provider (Stripe)
lane: INT
parent: [Feature] Organizer Dashboard: Buying Credits
estimate_hours: 4

## Context
The application needs a payment provider to process credit card transactions. We are assuming Stripe.

## User story
As a developer, I need Stripe configured in the environment so that I can process payments.

## In scope
- Setting up the Stripe SDK in the NestJS backend.
- Adding Stripe publishable and secret keys to the environment configuration.

## Out of scope
- Building the UI components (handled in FE).

## Acceptance criteria
- Given the backend application, when it boots, then the Stripe service is initialized with the secret key from the environment.
- Given the frontend application, when it boots, then the Stripe provider is initialized with the publishable key.
- Given the Stripe service, when it fails to initialize (e.g. missing environment variables), then the application logs an error and shuts down gracefully.

## Technical notes
- Do not commit real keys; use placeholder/test keys in the repo and rely on environment variables.

## Depends on/blocks
- Blocks `[BE] Buying Credits: Checkout endpoints`.

## Test notes
- Verify the backend can make a basic ping/test call to the Stripe API.

## Definition of done
- SDKs installed.
- Config wired up.
---end

---ticket
title: [QA] Buying Credits: E2E scenario
lane: QA
parent: [Feature] Organizer Dashboard: Buying Credits
estimate_hours: 4

## Context
End-to-end verification of the credit purchasing flow.

## User story
As a QA engineer, I need to ensure a user can successfully buy credits and see their balance update.

## In scope
- E2E test script using Playwright covering the happy path.

## Out of scope
- Testing actual real-money credit cards (use provider test cards).

## Acceptance criteria
- Given a logged-in user with a known balance, when they navigate to the dashboard, open the Buy Credits modal, select a package, enter test card details, and complete the purchase, then the success modal is shown and their dashboard balance reflects the addition.
- Given the Buy Credits modal, when a user clicks Cancel, then the modal closes and the user remains on the dashboard without being charged.
- Given the Payment Details modal, when a user enters invalid card data and submits, then the transaction is prevented and the UI shows validation errors.

## Technical notes
- Mock the payment provider or use Stripe's official test card numbers if making real requests to a test environment.

## Depends on/blocks
- Depends on all other tickets in this feature.

## Test notes
- N/A - This is the test ticket.

## Definition of done
- Playwright test is committed and passes in CI.
---end
