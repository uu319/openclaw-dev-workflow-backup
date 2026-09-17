# Spec: Organizer Flow Landing Pages

Source: Figma nodes 9731-3297, 9782-3552.

---ticket
title: [Feature] Landing Page: Organizer Marketing & Pricing
lane: FEATURE
priority: high
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552
screenshots: specs/_figma/organizer-flow-landing-pages/9731-3297.png, specs/_figma/organizer-flow-landing-pages/9782-3552.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552 · Lane: FEATURE

## User story
As an event organizer, I can read about the features and pricing of FindMyShots Studio so that I can decide to sign up or purchase credits.

## In scope
- Public landing page layout (Hero, Value Props, Pricing).
- Header component with two states (authenticated vs unauthenticated).
- Footer component.
- Responsive layout for desktop and mobile.

## Out of scope (do NOT build)
- Actual user authentication (login/signup logic is separate).
- Actual checkout integration (Stripe, etc.).
- Contact form implementation.
- Dashboard implementation.

## Acceptance criteria
- Given an unauthenticated user on the landing page, when viewing the header, then they see "Events", "Pricing", "Sign In", and a "Get Started" button.
- Given an authenticated user on the landing page, when viewing the header, then they see a "Dashboard" link, "Buy Credits" button, and an Avatar profile menu.
- Given the user clicks "Pricing" in the unauth header or "Buy Credits" anywhere, when clicked, then the page scrolls smoothly to the Credit Packages section.
- Given the user views the Credit Packages section, when presented with the options, then they see exactly 4 tiers (3,000, 5,000, 10,000, 15,000) and a "Contact Us" prompt for custom volumes.

## Technical notes
- Use Next.js App Router static rendering where possible.
- The authentication state check should run client-side (or via middleware if already set up) to render the correct header without breaking static caching of the main content.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Landing Page: Header & Footer
lane: FE
parent: [Feature] Landing Page: Organizer Marketing & Pricing
priority: high
estimate_hours: 4
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552
screenshots: specs/_figma/organizer-flow-landing-pages/9731-3297.png, specs/_figma/organizer-flow-landing-pages/9782-3552.png

## Context
Parent: [Feature] Landing Page: Organizer Marketing & Pricing · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552 · Lane: FE

## User story
As an organizer, I can navigate the site via the header and footer regardless of whether I am logged in.

## In scope
- Header component (Desktop and Mobile responsive).
- Unauthenticated state navigation links.
- Authenticated state navigation links and placeholder Avatar.
- Footer component.

## Out of scope (do NOT build)
- Functional login or signup endpoints.
- Functional profile dropdown menu contents.
- Pages the header links point to (except anchor links).

## Acceptance criteria
- Given the user is unauthenticated, when the header renders, then it displays the logo, "Events", "Pricing", "Sign In", and a primary "Get Started" button.
- Given the user is authenticated, when the header renders, then it displays the logo, "Dashboard", a "Buy Credits" button, and a user Avatar icon.
- Given the user clicks the FindMyShots logo, when clicked, then they are routed to `/`.
- Given the user scrolls to the bottom of the page, when viewing the footer, then they see "About", "Privacy", and "Made by Symph".
- Given a mobile viewport (< 768px), when viewing the header, then the navigation links collapse into a standard mobile menu or are appropriately sized.

## Technical notes
- Create reusable `Header` and `Footer` layout components.
- Mock the auth state using a simple boolean prop or context for now until real auth is integrated.
- Breakpoints: mobile <768px standard mobile menu; >=768px inline links.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- `npx nx test frontend --testFile=Header` covers the auth and unauth states.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Landing Page: Content & Pricing Sections
lane: FE
parent: [Feature] Landing Page: Organizer Marketing & Pricing
priority: high
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552
screenshots: specs/_figma/organizer-flow-landing-pages/9731-3297.png, specs/_figma/organizer-flow-landing-pages/9782-3552.png

## Context
Parent: [Feature] Landing Page: Organizer Marketing & Pricing · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297, https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552 · Lane: FE

## User story
As a prospective user, I can read about the features and see pricing so I understand what I am paying for.

## In scope
- Hero section with image collage.
- "Built around one job" features section.
- "Every album looks like your event" customization section.
- Credit Packages pricing section.
- Smooth scroll navigation.

## Out of scope (do NOT build)
- Header and Footer (handled in separate ticket).
- Checkout functionality when clicking "Select Option".
- Interactivity of the customization mockup (it is just static/images for the landing page).

## Acceptance criteria
- Given a user on the landing page, when viewing the hero, then they see the headline "Upload event photos. Let your attendees claim them free." and a "Buy Credits" button.
- Given a user clicks a "Buy Credits" button, when clicked, then the window scrolls smoothly to the Credit Packages section.
- Given a user views the pricing section, when rendered, then it lists 4 cards: 3,000 ($150), 5,000 ($250), 10,000 ($500), and 15,000 ($750) credits.
- Given a user clicks "Select Option", when clicked, then it routes to a placeholder `/checkout` route.
- Given the user views the value props, when scrolling down, then they see the 01, 02, 03 orange feature cards and the Customization UI mockup exactly as designed.

## Technical notes
- Export required static assets (hero collage, UI mockups) from Figma and place them in the public folder.
- Ensure text scales correctly and the pricing grid stacks neatly (e.g., 1 column on mobile, 2 on tablet, 4 on desktop) using Tailwind.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- `npx nx test frontend --testFile=LandingPage` renders the sections properly.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests added and green
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [INT] Set up Playwright E2E runner
lane: INT
parent: [Feature] Landing Page: Organizer Marketing & Pricing
priority: high
estimate_hours: 4
parallel: true

## Context
Parent: [Feature] Landing Page: Organizer Marketing & Pricing · Lane: INT

## User story
As an engineer, I can run an E2E test suite so that I know the compiled application works in a real browser.

## In scope
- Playwright installation and Nx configuration.
- A basic GitHub Actions or local CI script for Playwright (if applicable).
- A smoke test verifying the app boots and loads the index page.

## Out of scope (do NOT build)
- Writing tests for every feature (those belong in `[QA]` tickets).

## Acceptance criteria
- Given a fresh clone, when a developer runs `npx nx e2e frontend-e2e`, then Playwright executes tests against the built Next.js application.
- Given the generated smoke test, when executed, then it passes by verifying the page title or basic element.
- Given a CI environment, when the pipeline runs, then it can execute the Playwright tests headlessly without failing on missing browser binaries.

## Technical notes
- Use the standard `@nx/playwright` plugin.

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Landing Page: Organizer Marketing & Pricing

## Test notes (how QA verifies)
- Verify `npx nx e2e frontend-e2e` completes successfully.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Playwright configured
- [ ] PR reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [QA] Landing Page: Organizer Marketing & Pricing
lane: QA
parent: [Feature] Landing Page: Organizer Marketing & Pricing
priority: high
estimate_hours: 4
depends_on: [FE] Landing Page: Header & Footer, [FE] Landing Page: Content & Pricing Sections, [INT] Set up Playwright E2E runner

## Context
Parent: [Feature] Landing Page: Organizer Marketing & Pricing · Lane: QA

## User story
As a QA engineer, I can verify the landing page functions as expected for all users.

## In scope
- E2E tests for the landing page layout and navigation.

## Out of scope (do NOT build)
- Testing actual checkout (since it's mocked).
- Testing actual auth flow (since it's mocked).

## Acceptance criteria
- Given the Playwright test suite, when executed, then a test verifies the unauthenticated header contains "Sign In" and "Get Started".
- Given the Playwright test suite, when executed, then a test verifies the authenticated header contains "Dashboard" and "Buy Credits".
- Given the Playwright test suite, when executed, then a test verifies clicking "Pricing" scrolls to or focuses the Credit Packages section.
- Given the Playwright test suite, when executed, then a test verifies the 4 pricing tiers are visible.

## Technical notes
- Write Playwright E2E tests in the `frontend-e2e` project.

## Depends on / blocks
- Depends on: [FE] Landing Page: Header & Footer, [FE] Landing Page: Content & Pricing Sections, [INT] Set up Playwright E2E runner
- Blocks: none

## Test notes (how QA verifies)
- CI automatically runs these tests.

## Definition of done
- [ ] All tests passing
- [ ] PR reviewed
- [ ] Status moved to COMPLETE
---end
