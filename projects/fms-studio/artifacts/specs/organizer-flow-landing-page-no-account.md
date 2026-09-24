# Spec: Organizer Flow: Landing Page No Account

Source: Figma node 9731-3297.

---ticket
title: [Feature] Organizer Flow: Landing Page No Account
id: z94kydab9b
lane: FEATURE
priority: normal
status: to do
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297 · Lane: FEATURE

**Restoration Note:** The landing page was previously built as one large ticket but was rejected for not being pixel-perfect. We are breaking it down into component-level tickets to ensure exact design fidelity.

## User story
As an unauthenticated organizer, I want to learn about the Studio product, its features, and its pricing, so that I can decide whether to sign up and buy credits.

## In scope
- Full marketing landing page broken into components: Navigation/Footer, Hero, How it works, Customization demo, and Pricing.
- Pixel-perfect implementation from Figma tokens and assets.
- Links to Sign In, Sign Up, and Contact Us.

## Out of scope (do NOT build)
- Actual checkout flow or payment processing (separate feature).
- Authentication logic or backend session management.
- Dynamic behavior in the customization mockup (it is just static marketing).
- Main FindMyShots marketplace pages.

## Acceptance criteria
- Given the user is not authenticated, when they visit `/`, then the Studio marketing landing page is displayed.
- Given the page is displayed, when a user scrolls, then they see the Hero, How it works, Features, Customization demo, Pricing, and Footer sections in order.
- Given any navigation or pricing button, when clicked, then the user is routed to the correct anchor or path (`/signup`, `/signin`, `mailto:`).

## Technical notes
- Endpoint / schema: Static page, no API required.

## Depends on / blocks
- Depends on: none
- Blocks: Authentication Flow, Checkout Flow

## Test notes (how QA verifies)
- Run the [QA] E2E scenario.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [BUG] Footer Text Font is not Actor
id: z94kydb188
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: normal
status: to do
estimate_hours: 1
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9773-3522
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account (z94kydab9b) · Lane: FE

## User story
As an unauthenticated organizer, I expect the footer to match the design spec exactly, including the typography.

## In scope
- Fixing the footer text font family.

## Out of scope (do NOT build)
- Any other layout or styling changes.

## Acceptance criteria
- Given the footer text, when rendered, then it uses the `Actor` font (e.g., via the `font-actor` Tailwind class).
- Given the footer text, when rendered, then it does not inherit the host font or default font.
- Given the layout, when the footer is rendered, then the `font-actor` class correctly sets the font-family.

## Design fidelity
- Tokens: Text `#313131` · Font `Actor` 400 at 20px.
- Assets: none

## Technical notes
- The Tailwind class `font-actor` is defined but not applied to the footer text elements.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Visually inspect the footer font and verify the computed CSS uses the `Actor` font family.

## Definition of done
- [ ] All acceptance criteria pass
---end

---ticket
title: [FE] Landing Page: Header and Footer
id: z94kydb12t
id: z94kydb12t
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: high
status: to do
estimate_hours: 4
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3216
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: Header is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3216 and Footer is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9773-3522 · Lane: FE

## User story
As an unauthenticated organizer, I want to navigate the landing page and find legal links in the footer.

## In scope
- Global navigation bar for the unauthenticated landing page.
- Footer section.

## Out of scope (do NOT build)
- Body content sections (Hero, Pricing, etc).
- Authentication logic.

## Acceptance criteria
- Given the header, when rendered, then it displays the logo and "Events", "Pricing", "Sign In", "Get Started" links pointing to their routes (`#events`, `#pricing`, `/signin`, `/signup`).
- Given the footer, when rendered, then it displays "findmyshots", "About", "Privacy", "Made by Symph" and the links point to `/about` and `/privacy`.
- Given a narrow viewport (<1024px), when the header and footer render, then they adjust spacing and wrap responsibly.

## Design fidelity
- Tokens: Primary `#FF6100` · Text `#313131` · Muted `#797979` · Font `Host Grotesk` 400/500/600/800. Footer text uses `Actor` 400 at 20px.
- Assets:
  - `assets/logo.svg` → `frontend/public/brand/logo.svg` — FindMyShots Studio wordmark, 154x26
- No placeholders: The logo must be rendered via `next/image` or inline SVG, not text.

## Technical notes
- Component: `<LandingHeader>` and `<LandingFooter>` in the `app/page.tsx` layout.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Unit test navigation links and visual fidelity of header/footer.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Design fidelity matched exactly
---end

---ticket
title: [FE] Landing Page: Hero Section
id: z94kydb12u
id: z94kydb12u
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: normal
status: to do
estimate_hours: 8
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9734-3593
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: Collage is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9734-3593 and Text is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9734-3601 · Lane: FE

## User story
As an unauthenticated organizer, I want to see an engaging hero section that explains the core value proposition.

## In scope
- Hero section containing the display heading, subtext, and CTAs.
- The complex hero photo collage with 13 images and 6 decorative scribbles.

## Out of scope (do NOT build)
- Other page sections.

## Acceptance criteria
- Given the Hero section, when rendered, then it displays the display heading "Upload event photos. Let your attendees claim them free." and the subtext "Built around one job: getting photos to the right person".
- Given the Hero CTAs, when rendered, then the "Buy Credits" button points to `/signup` and "See how it works" points to `#how-it-works`.
- Given the Hero section, when rendered, then the photo collage and scribbles exactly match the positioning, layering, and scales defined in Figma.

## Design fidelity
- Tokens: Primary `#FF6100` · Text `#313131` · Black `#000000`. Text at 50%: `rgba(49, 49, 49, 0.5)`. Shadows: `rgba(0, 0, 0, 0.1)`. Font `Heavitas` 400 at 50px (heading) and `Host Grotesk` 800 at 60px (subtext).
- Assets:
  - `assets/hero-photo-01.png` → `frontend/public/marketing/hero/photo-01.png`
  - `assets/hero-photo-02.png` → `frontend/public/marketing/hero/photo-02.png`
  - `assets/hero-photo-03.png` → `frontend/public/marketing/hero/photo-03.png`
  - `assets/hero-photo-04.png` → `frontend/public/marketing/hero/photo-04.png`
  - `assets/hero-photo-05.png` → `frontend/public/marketing/hero/photo-05.png`
  - `assets/hero-photo-06.png` → `frontend/public/marketing/hero/photo-06.png`
  - `assets/hero-photo-07-bcceaf.png` → `frontend/public/marketing/hero/photo-07.png`
  - `assets/hero-photo-08-41b289.png` → `frontend/public/marketing/hero/photo-08.png`
  - `assets/hero-photo-09-7583dc.png` → `frontend/public/marketing/hero/photo-09.png`
  - `assets/hero-photo-10-442cfc.png` → `frontend/public/marketing/hero/photo-10.png`
  - `assets/hero-photo-11-317644.png` → `frontend/public/marketing/hero/photo-11.png`
  - `assets/hero-photo-12.png` → `frontend/public/marketing/hero/photo-12.png`
  - `assets/hero-photo-13.png` → `frontend/public/marketing/hero/photo-13.png`
  - `assets/hero-scribble-01-2e7fd8.png` → `frontend/public/marketing/hero/scribble-01.png`
  - `assets/hero-scribble-02-5fb332.png` → `frontend/public/marketing/hero/scribble-02.png`
  - `assets/hero-scribble-03-3f7df0.png` → `frontend/public/marketing/hero/scribble-03.png`
  - `assets/hero-scribble-04-19fb02.png` → `frontend/public/marketing/hero/scribble-04.png`
  - `assets/hero-scribble-05-542cb2.png` → `frontend/public/marketing/hero/scribble-05.png`
  - `assets/hero-scribble-06-4491a3.png` → `frontend/public/marketing/hero/scribble-06.png`
- No placeholders: all images must render. Use `next/image` with appropriate priority for hero images.

## Technical notes
- Use absolute positioning within a relative container for the collage to match Figma's exact overlap.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Visual verification against Figma.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Pixel-perfect implementation of the collage
---end

---ticket
title: [FE] Landing Page: How it works & Features Block
id: z94kydb12w
id: z94kydb12w
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: normal
status: to do
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9749-3731
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: Features Block is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9749-3731 and How it works cards is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9749-3726 · Lane: FE

## User story
As an unauthenticated organizer, I want to understand how the platform works and its key features.

## In scope
- The three "How it works" cards ("You buy credits", "You upload the photos", "Attendees download free").
- The orange Features block containing 01 "Credits, not subscriptions", 02 "One dashboard per event", 03 "Attendees never pay".
- Floating pill badges ("Personalize", "Upload", "Organize", "Share Link", "Download Free").

## Out of scope (do NOT build)
- Hero or Customization sections.

## Acceptance criteria
- Given the How it works section, when rendered, then it displays the three cards with exact text and photos.
- Given the Features section, when rendered, then the orange block displays three feature pillars with exact text, typography, and photos.
- Given the floating pill badges, when rendered, then they match the Figma styling (rounded pills, orange background, white text).

## Design fidelity
- Tokens: Primary `#FF6100` · Text `#313131` · White `#FFFFFF` · Muted `#797979`. Card backgrounds: `#FFFFFF` with shadow `rgba(0, 0, 0, 0.1)`. Font `Host Grotesk` 400/500/800. Radii: 16px, 40px, 50px, 100px.
- Assets:
  - `assets/feature-photo-01.png` → `frontend/public/marketing/features/photo-01.png`
  - `assets/feature-photo-02.png` → `frontend/public/marketing/features/photo-02.png`
  - `assets/feature-photo-03.png` → `frontend/public/marketing/features/photo-03.png`
  - `assets/feature-photo-04.png` → `frontend/public/marketing/features/photo-04.png`
  - `assets/feature-photo-05.png` → `frontend/public/marketing/features/photo-05.png`
  - `assets/feature-photo-06-2de83a.png` → `frontend/public/marketing/features/photo-06.png`
- No placeholders allowed.

## Technical notes
- Utilize CSS flex/grid to ensure cards wrap properly on smaller viewports.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Verify texts, images, and card border radii match Figma.

## Definition of done
- [ ] All acceptance criteria pass
---end

---ticket
title: [FE] Landing Page: Customization Section
id: z94kydb12x
id: z94kydb12x
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: normal
status: to do
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-4728
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: Customization Section is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-4728 · Lane: FE

## User story
As an unauthenticated organizer, I want to see how I can customize my albums.

## In scope
- The static customization demo section.
- Text: "Every album looks like your event, not ours".
- The Album Font and Theme Color mock selectors.
- The two large UI mockups ("My Albums" and "APPROVED").

## Out of scope (do NOT build)
- Interactive font/color changing behavior (this is a static marketing image/layout).

## Acceptance criteria
- Given the customization section, when rendered, then it displays the exact headings and descriptions about album identity.
- Given the Album Font selector, when rendered, then it displays the static font choices (Host Grotesk, Honfleur, High Tower, Hubbali, Hi Melody, Helvetica).
- Given the Theme Color selector, when rendered, then it displays the static color swatches and gradients.
- Given the large mockups, when rendered, then the "My Albums" and "APPROVED" mockups display alongside the swatches.

## Design fidelity
- Tokens: Primary `#FF6100` · Text `#313131` · Font `Host Grotesk` 400/500/800.
- Theme Swatches (exact hexes): `#E53935`, `#FF6100`, `#FED448`, `#31B85C`, `#EE08E7`, `#357992`, `#535862`, `#7C57FF`, `#000000`.
- Assets:
  - `assets/demo-swatch-gradient.svg` → `frontend/public/marketing/demo/swatch-gradient.svg`
  - `assets/demo-my-albums.png` → `frontend/public/marketing/demo/my-albums.png`
  - `assets/demo-swatch-overlay-01.png` → `frontend/public/marketing/demo/swatch-overlay-01.png`
  - `assets/demo-swatch-overlay-02.png` → `frontend/public/marketing/demo/swatch-overlay-02.png`
  - `assets/demo-approved.png` → `frontend/public/marketing/demo/approved.png`
- No placeholders allowed.

## Technical notes
- This section overlaps large background assets. Use relative containers and precise z-indexing.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Visually verify the alignment of the swatches and mockups.

## Definition of done
- [ ] All acceptance criteria pass
---end

---ticket
title: [FE] Landing Page: Pricing & Contact
id: z94kydb12z
id: z94kydb12y
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: normal
status: to do
estimate_hours: 6
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9764-3322
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: Pricing Section is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9764-3322 and Contact banner is https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9773-3494 · Lane: FE

## User story
As an unauthenticated organizer, I want to see clear pricing options so I can purchase credits.

## In scope
- "Credit Packages" heading and subtext ("Rate: $0.05 per credit").
- Four pricing tier cards ($150, $250, $500, $750).
- The "Need fewer... or more" contact banner.

## Out of scope (do NOT build)
- Stripe integration or payment processing logic.

## Acceptance criteria
- Given the Pricing section, when rendered, then it displays the "Credit Packages" heading and the "$0.05 per credit" pill.
- Given the pricing cards, when rendered, then the 4 cards display exactly: "3,000", "5,000", "10,000", and "15,000" credits with prices "$150", "$250", "$500", and "$750" respectively.
- Given a pricing card, when the user clicks "Select Option", then they are navigated to `/signup`.
- Given the contact banner, when the user clicks "Contact Us", then it opens a `mailto:` link (e.g. `mailto:support@findmyshots.com`).
- Given a viewport narrower than 1024px, when the pricing section renders, then the 4 cards wrap into a grid or column layout instead of overflowing horizontally.

## Design fidelity
- Tokens: Primary `#FF6100` · Text `#313131` · Card `#FFFFFF` with shadow `rgba(0, 0, 0, 0.2)` · Font `Host Grotesk` 400/500/800.
- Fonts: "3,000", "5,000" etc use `Heavitas` 400 at 50px.
- Assets (Icons inside pricing cards and banner):
  - `assets/icon-shopping-bag.svg` → `frontend/public/icons/shopping-bag.svg`
  - `assets/icon-calendar-heart.svg` → `frontend/public/icons/calendar-heart.svg`
  - `assets/icon-ticket.svg` → `frontend/public/icons/ticket.svg`
  - `assets/icon-gift.svg` → `frontend/public/icons/gift.svg`
  - `assets/icon-images.svg` → `frontend/public/icons/images.svg`

## Technical notes
- Use a CSS grid for the 4 pricing cards.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- Verify cards render the correct icons and numbers, and links function correctly.

## Definition of done
- [ ] All acceptance criteria pass
---end

---ticket
title: [QA] Landing Page: E2E unauthenticated visitor views pricing and clicks signup
id: z94kydab9d
lane: QA
parent: [Feature] Organizer Flow: Landing Page No Account
status: to do
estimate_hours: 2
depends_on: [FE] Landing Page: Pricing & Contact

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: none · Lane: QA

## User story
As QA, I want to verify the unauthenticated landing page renders correctly and routes to signup.

## In scope
- E2E test verifying static content and routing on the landing page

## Out of scope (do NOT build)
- Testing actual checkout

## Acceptance criteria
- Given an unauthenticated browser, when the user visits `/`, then the page title contains "FindMyShots Studio" and the "Credit Packages" section is visible.
- Given the Pricing section, when the user clicks "Select Option" on the "$150 total" card, then the browser navigates to the `/signup` route.
- Given the Hero section, when the user clicks "See how it works", then the page scrolls to the `#how-it-works` anchor section.

## Technical notes
- Playwright scenario in the e2e project.

## Depends on / blocks
- Depends on: [FE] Landing Page: Pricing & Contact, [FE] Landing Page: Hero Section
- Blocks: none

## Test notes (how QA verifies)
- E2E script runs successfully.

## Definition of done
- [ ] All acceptance criteria pass
---end
