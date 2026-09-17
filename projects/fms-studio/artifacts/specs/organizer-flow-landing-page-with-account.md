---ticket
title: [Feature] Organizer Flow: Landing Page With Account
lane: FEATURE
priority: normal
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552
screenshots: specs/_figma/organizer-flow-landing-page-with-account/9782-3552.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552 · Lane: FEATURE

## User story
As an organizer, I want a landing page that explains the FindMyShots Studio benefits and pricing, and allows me to purchase credit blocks, so that I can manage event photo sharing easily.

## In scope
- Full responsive landing page layout (Navbar, Hero, Value Props, App Preview, Benefits, Customization, Pricing, Footer).
- Pricing table with 4 credit packages (3k, 5k, 10k, 15k).
- Linking to dashboard and purchase flows.

## Out of scope (do NOT build)
- Actual Stripe checkout processing (will be a separate billing feature).
- Authentication flow (handled by existing system/other tickets).
- Attendee-facing marketplace.

## Acceptance criteria
- Given the user navigates to `/studio` (or the configured landing page route), when the page loads, then the navigation bar displays the text logo "findmyshots studio", a "Dashboard" link, a "Buy Credits" button, and a user avatar with a chevron.
- Given a user on the landing page, when they scroll, then they see the Hero, Value Proposition, App Preview, Benefits, Customization Showcase, and Pricing sections in that exact vertical order.
- Given the Pricing section, when rendered, then it displays 4 packages (3,000 for $150, 5,000 for $250, 10,000 for $500, 15,000 for $750) with "Select Option" buttons.
- Given the pricing section footer, when rendered, then it shows the text "Need fewer than 3,000 or more than 15,000 credits?" and a "Contact Us" button.

## Technical notes
- Endpoint / schema: Static content, mostly frontend layout.
- Mock or fixture for parallel work: None needed (static page layout).
- Breakpoints (FE only): Mobile <640px, tablet 640–1024px, desktop >1024px.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Run the [QA] E2E scenario in this feature to verify layout rendering and link/button destinations.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/organizer-flow-landing-page-with-account` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Landing Page: Navbar and Hero Section
lane: FE
parent: [Feature] Organizer Flow: Landing Page With Account
priority: normal
estimate_hours: 4
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552
screenshots: specs/_figma/organizer-flow-landing-page-with-account/9782-3552.png

## Context
Parent: [Feature] Organizer Flow: Landing Page With Account · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552 · Lane: FE

## User story
As an organizer, I want to see a navigation bar and hero section, so that I understand the value prop and can access my dashboard or buy credits.

## In scope
- Navbar component with logo, Dashboard link, Buy Credits button, User Avatar dropdown.
- Hero section with photo collage, "Buy Credits" button, and "See how it works" link.

## Out of scope (do NOT build)
- User session fetching logic (assume mock or existing context).
- Actual checkout flow when "Buy Credits" is clicked.
- Implementation of the dropdown menu content.

## Acceptance criteria
- Given the navigation bar is rendered, when the user views it, then the logo reads exactly "findmyshots studio".
- Given the navigation bar is rendered, when the user views it, then there is a link reading exactly "Dashboard".
- Given the navigation bar is rendered, when the user views it, then there is an orange button reading exactly "Buy Credits".
- Given the hero section is rendered, when the user views it, then there is a central orange button reading exactly "Buy Credits" and an underlined link reading exactly "See how it works".

## Technical notes
- Endpoint / schema: Static layout.
- Mock or fixture for parallel work: Mock user session for the avatar.
- Breakpoints (FE only): mobile <640px: hide "Dashboard" text and "Buy Credits" button in navbar, show hamburger menu; tablet 640–1024px: show full navbar.

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Organizer Flow: Landing Page With Account: E2E test

## Test notes (how QA verifies)
- Render the page and verify the presence of the navbar elements and hero buttons/links with exact text.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/organizer-flow-landing-page-with-account` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Landing Page: Content Sections
lane: FE
parent: [Feature] Organizer Flow: Landing Page With Account
priority: normal
estimate_hours: 6
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552
screenshots: specs/_figma/organizer-flow-landing-page-with-account/9782-3552.png

## Context
Parent: [Feature] Organizer Flow: Landing Page With Account · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552 · Lane: FE

## User story
As an organizer, I want to read about the features and see app screenshots, so that I know what Studio offers.

## In scope
- Value proposition section ("Upload event photos. Let your attendees claim them free.")
- App screenshot section ("Built around one job: getting photos to the right person") with orange floating badges.
- Orange benefits section ("Credits, not subscriptions", "One dashboard per event", "Attendees never pay").
- Customization showcase section ("Every album looks like your event, not ours").

## Out of scope (do NOT build)
- Interactive font or color changes in the customization mockups (they are static visuals for the landing page).

## Acceptance criteria
- Given the value prop section, when rendered, then it contains three cards with exact text: "You buy credits", "You upload the photos", and "Attendees download free".
- Given the app preview section, when rendered, then floating orange badges exist with exact text: "Personalize", "Buy Credits", "Upload", "Organize", "Share Link", "Download Free".
- Given the benefits section, when rendered, then three cards display exactly: "01 Credits, not subscriptions", "02 One dashboard per event", and "03 Attendees never pay".
- Given the customization section, when rendered, then the text reads exactly "Set a font and a theme per album before you publish it. Attendees see your event's identity — not a generic template."

## Technical notes
- Endpoint / schema: Static layout.
- Breakpoints (FE only): mobile <640px: stack value prop and benefit cards vertically; tablet 640–1024px: wrap cards; desktop >1024px: side-by-side cards.

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Organizer Flow: Landing Page With Account: E2E test

## Test notes (how QA verifies)
- Verify that all static sections render with the exact typography and cards as defined in the acceptance criteria.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/organizer-flow-landing-page-with-account` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [FE] Landing Page: Pricing and Footer
lane: FE
parent: [Feature] Organizer Flow: Landing Page With Account
priority: normal
estimate_hours: 5
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552
screenshots: specs/_figma/organizer-flow-landing-page-with-account/9782-3552.png

## Context
Parent: [Feature] Organizer Flow: Landing Page With Account · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9782-3552 · Lane: FE

## User story
As an organizer, I want to see the pricing tiers and contact information, so that I can choose a plan or ask for help.

## In scope
- "Credit Packages" section with 4 pricing tiers.
- "Contact Us" banner.
- Footer with logo and links.

## Out of scope (do NOT build)
- Backend pricing API integration (hardcode pricing values per design for now).

## Acceptance criteria
- Given the pricing section, when rendered, then 4 cards exist displaying exact prices: "$150 total", "$250 total", "$500 total", and "$750 total".
- Given any pricing card, when rendered, then it contains an orange button with the exact text "Select Option".
- Given any pricing card, when rendered, then beneath the button it displays the exact subtext "No Expiration • One time pay".
- Given the contact banner, when rendered, then it contains an orange button with the exact text "Contact Us".
- Given the footer, when rendered, then it contains exact links "About" and "Privacy" and text "Made by Symph".

## Technical notes
- Endpoint / schema: Static layout.
- Breakpoints (FE only): mobile <640px: stack pricing cards vertically (1 column); tablet 640–1024px: 2 columns; desktop >1024px: 4 columns.

## Depends on / blocks
- Depends on: none
- Blocks: [QA] Organizer Flow: Landing Page With Account: E2E test

## Test notes (how QA verifies)
- Verify pricing values and button text. Resize window to ensure cards wrap from 4 columns down to 1.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Unit tests for this lane added and green (`npx nx test frontend`)
- [ ] Lint and typecheck clean (`npx nx lint frontend`, `npx tsc -p frontend/tsconfig.json --noEmit`)
- [ ] PR opened from `feature/organizer-flow-landing-page-with-account` and reviewed
- [ ] Status moved to QA FOR DEVELOPMENT
---end

---ticket
title: [QA] Organizer Flow: Landing Page With Account: E2E test
lane: QA
parent: [Feature] Organizer Flow: Landing Page With Account
estimate_hours: 2
depends_on: [FE] Landing Page: Navbar and Hero Section, [FE] Landing Page: Content Sections, [FE] Landing Page: Pricing and Footer

## Context
Parent: [Feature] Organizer Flow: Landing Page With Account · Lane: QA

## User story
As QA, I want to verify the Landing Page renders completely and responsively.

## In scope
- Playwright E2E visual and structural test for the Landing page.

## Out of scope (do NOT build)
- Checkout flow E2E tests (tested in separate feature).

## Acceptance criteria
- Given the landing page route, when accessed via Playwright, then it renders without console errors.
- Given the landing page route, when accessed, then all buttons (Buy Credits, Select Option, Contact Us) are present and clickable.
- Given the landing page route, when viewport is resized to mobile width, then the layout responds and cards stack vertically.

## Technical notes
- Add to `apps/frontend-e2e` or the Playwright suite.

## Depends on / blocks
- Depends on: all lane tickets in this feature
- Blocks: none

## Test notes (how QA verifies)
- Execute `npx nx e2e frontend-e2e`.

## Definition of done
- [ ] Scenario executed and passes
- [ ] Status moved to QA FOR DEVELOPMENT
---end