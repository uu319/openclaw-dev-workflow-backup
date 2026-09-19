# QA Results: Organizer Flow - Landing Page No Account

## Acceptance Criteria Verified

### From `[QA]` Ticket
- **Given an unauthenticated browser, when the user visits `/`, then the page title contains "FindMyShots Studio" and the "Credit Packages" section is visible.**
  - **FAIL**
- **Given the Pricing section, when the user clicks "Select Option" on the "$150 total" card, then the browser navigates to the `/signup` route.**
  - **FAIL**
- **Given the Hero section, when the user clicks "See how it works", then the page scrolls to the `#how-it-works` anchor section.**
  - **PASS**

### From `[Feature]` Parent Ticket
- **Given the user is not authenticated, when they visit `/`, then the Studio marketing landing page is displayed.**
  - **PASS**
- **Given the navigation bar, when the user clicks "Events", "Pricing", "Sign In", or "Get Started", then they are routed to the respective placeholder routes or anchors.**
  - **PASS**
- **Given the Hero section, when the user clicks "Buy Credits" or "See how it works", then they are routed appropriately.**
  - **FAIL**
- **Given the Pricing section, when the user clicks "Select Option" on any credit package card (3,000, 5,000, 10,000, 15,000), then they are routed to the sign-up/checkout flow.**
  - **FAIL**
- **Given the "Need fewer... or more" banner, when the user clicks "Contact Us", then a mailto link or contact form is opened.**
  - **FAIL**

## Defects

### Defect 1: Missing correct page title and "Credit Packages" text
- **Steps:** 
  1. Inspect the layout metadata in `src/app/layout.tsx`.
  2. Inspect the pricing section in `src/app/page.tsx` for the expected text.
- **Expected:** Page title contains "FindMyShots Studio" and the pricing section mentions "Credit Packages".
- **Observed:** Page title is "Welcome to frontend". The pricing section text says "Simple, transparent pricing" but does not contain "Credit Packages".
- **Evidence:** `layout.tsx` metadata title is `'Welcome to frontend'`. The text "Credit Packages" is absent from `page.tsx`.

### Defect 2: Pricing cards missing "Select Option" button and routing
- **Steps:**
  1. Go to the Pricing section on the landing page.
  2. Look for the "Select Option" button on any of the pricing cards (e.g., "$150" card).
  3. Attempt to click it to navigate to `/signup`.
- **Expected:** A button or link labeled "Select Option" exists and navigates the user to `/signup`.
- **Observed:** The button is labeled "Buy now" and is a standard `<button>` element with no click handler or `href` attribute. It does not route anywhere.
- **Evidence:** Code in `src/app/page.tsx` shows `<button className="...">Buy now</button>`.

### Defect 3: "Buy Credits" button in Hero section routes incorrectly
- **Steps:**
  1. Inspect the "Buy Credits" button in the Hero section.
- **Expected:** The button routes the user appropriately to the signup page (`/signup`).
- **Observed:** The button links to the `#pricing` anchor instead of `/signup`.
- **Evidence:** `<Link href="#pricing" className="...">Buy Credits</Link>` in `src/app/page.tsx`.

### Defect 4: "Contact Us" banner link is not a mailto link
- **Steps:**
  1. Inspect the "Contact Us" link in the banner below the pricing cards.
- **Expected:** A `mailto:` link is opened when clicked.
- **Observed:** The link routes to a placeholder page (`/contact`).
- **Evidence:** `<Link href="/contact" className="...">Contact Us</Link>` in `src/app/page.tsx`.

### Defect 5: Missing E2E Tests
- **Steps:**
  1. Attempt to run the E2E suite via `npx nx run-many -t e2e`.
- **Expected:** An E2E test runs for the landing page scenario as defined in the `[QA]` ticket.
- **Observed:** No e2e targets are found. The QA playwright scenario from the ticket was not implemented.
- **Evidence:** Running `npx nx run-many -t e2e` yields "NX No tasks were run" and there is no e2e project folder.