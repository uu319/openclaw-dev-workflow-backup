# Spec: Organizer Flow: Landing Page No Account

Source: Figma node 9731-3297.

---ticket
title: [Feature] Organizer Flow: Landing Page No Account
lane: FEATURE
priority: normal
status: to do
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png

## Context
Parent: this is the parent · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297 · Lane: FEATURE

**Restoration Note:** The landing page was previously built but overwritten. This ticket has been reopened to restore the landing page layout, header, footer, and pricing sections.

## User story
As an unauthenticated organizer, I want to learn about the Studio product, its features, and its pricing, so that I can decide whether to sign up and buy credits.

## In scope
- Full marketing landing page layout (Hero, How it works, Features, Customization demo, Pricing)
- Navigation bar for unauthenticated users
- Static pricing cards displaying credit packages
- Links to Sign In, Sign Up ("Get Started", "Buy Credits", "Select Option"), and Contact Us

## Out of scope (do NOT build)
- Actual checkout flow or payment processing (separate feature)
- Authentication logic or backend session management
- Dynamic behavior in the customization mockup (it's just a static marketing image/layout)
- Main FindMyShots marketplace pages (this is strictly the Studio landing page)

## Acceptance criteria
- Given the user is not authenticated, when they visit `/`, then the Studio marketing landing page is displayed.
- Given the navigation bar, when the user clicks "Events", "Pricing", "Sign In", or "Get Started", then they are routed to the respective placeholder routes or anchors.
- Given the Hero section, when the user clicks "Buy Credits" or "See how it works", then they are routed appropriately.
- Given the Pricing section, when the user clicks "Select Option" on any credit package card (3,000, 5,000, 10,000, 15,000), then they are routed to the sign-up/checkout flow.
- Given the "Need fewer... or more" banner, when the user clicks "Contact Us", then a mailto link or contact form is opened.

## Technical notes
- Endpoint / schema: Static page, no API required.

## Depends on / blocks
- Depends on: none
- Blocks: Authentication Flow, Checkout Flow

## Test notes (how QA verifies)
- Run the [QA] E2E scenario below.

## Definition of done
- [ ] All subtasks COMPLETE and the [QA] scenario passes
---end

---ticket
title: [FE] Landing Page: layout - navigation - and static content
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: normal
status: to do
estimate_hours: 8
parallel: true
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297 · Lane: FE

**Restoration Note:** The previous content, navigation & pricing sections were overwritten by an Nx scaffold and need to be restored.

## User story
As an unauthenticated organizer, I want to see the marketing landing page so I can learn about the product and view pricing.

## In scope
- Page route `frontend/src/app/page.tsx`
- Navigation bar (Logo, "Events", "Pricing", "Sign In", "Get Started")
- Hero section with photo collage and "Buy Credits" / "See how it works" buttons
- Three-card "How it works" section
- Large dashboard mockup section with floating orange labels
- Orange features block ("Credits, not subscriptions", "One dashboard per event", "Attendees never pay")
- Customization section with static font/theme pickers and album mockup
- Pricing section with 4 tier cards and "Contact Us" banner
- Footer (Logo, "About", "Privacy", "Made by Symph")

## Out of scope (do NOT build)
- Authentication logic
- Stripe/payment integration for the "Select Option" buttons
- Interactive font/color changing on the album mockup (it should render statically as designed)

## Acceptance criteria
- Given the navigation bar, when rendered, then the "Events", "Pricing", "Sign In", and "Get Started" links are visible and point to their respective routes (`#events`, `#pricing`, `/signin`, `/signup`).
- Given the Hero section, when rendered, then the "Buy Credits" button points to `/signup` and "See how it works" points to `#how-it-works`.
- Given the Pricing section, when rendered, then 4 cards display exactly: "3,000", "5,000", "10,000", and "15,000" credits with prices "$150", "$250", "$500", and "$750" respectively.
- Given a pricing card, when the user clicks "Select Option", then they are navigated to `/signup`.
- Given the custom pricing banner, when the user clicks "Contact Us", then it opens a `mailto:` link (e.g., `mailto:support@findmyshots.com`).
- Given the footer, when rendered, then the "About" and "Privacy" links point to `/about` and `/privacy`.
- Given a viewport narrower than 1024px, when the pricing section renders, then the 4 cards wrap into a grid or column layout instead of overflowing horizontally.

## Design fidelity
- Tokens (exact, from `get_figma_data` on node 9731-3297 — define these once in the Tailwind theme, not per component):
  - Primary `#FF6100` · Text `#313131` · Muted `#797979` · White `#FFFFFF` · Black `#000000`
  - Text at 50%: `rgba(49, 49, 49, 0.5)` · on-dark text at 60%: `rgba(255, 255, 255, 0.6)`
  - Shadows use `rgba(0, 0, 0, 0.1)`, `rgba(0, 0, 0, 0.2)`, `rgba(0, 0, 0, 0.25)`, `rgba(0, 0, 0, 0.6)`
  - Font `Host Grotesk` — 400 at 18/20px (body), 500 at 18/20px (labels), 800 at 30/40/60px (headings)
  - Font `Heavitas` 400 at 50px — the display heading only
  - Radii: 10px, 16px, 25px, 40px, 50px, 100px (pill)
- Assets (36 files, already downloaded to `specs/_figma/organizer-flow-landing-page-no-account/assets/`;
  copy each into the repo at the path given, then reference it — do not re-download):
  - **Brand**
    - `assets/logo.svg` → `frontend/public/brand/logo.svg` — FindMyShots Studio wordmark (header + footer), 154x26
  - **Icons**
    - `assets/icon-shopping-bag.svg` → `frontend/public/icons/shopping-bag.svg` — 'shopping-bag' section icon, 54x54
    - `assets/icon-calendar-heart.svg` → `frontend/public/icons/calendar-heart.svg` — 'calendar-heart' section icon, 54x54
    - `assets/icon-ticket.svg` → `frontend/public/icons/ticket.svg` — 'ticket' section icon, 54x54
    - `assets/icon-gift.svg` → `frontend/public/icons/gift.svg` — 'gift' section icon, 54x54
    - `assets/icon-images.svg` → `frontend/public/icons/images.svg` — 'images' section icon, 54x54
  - **Customization demo**
    - `assets/demo-swatch-gradient.svg` → `frontend/public/marketing/demo/swatch-gradient.svg` — theme-colour gradient swatch, 84x84
    - `assets/demo-my-albums.png` → `frontend/public/marketing/demo/my-albums.png` — customization demo: My Albums screen, 4096x2290
    - `assets/demo-swatch-overlay-01.png` → `frontend/public/marketing/demo/swatch-overlay-01.png` — theme-colour swatch overlay, 736x920
    - `assets/demo-swatch-overlay-02.png` → `frontend/public/marketing/demo/swatch-overlay-02.png` — theme-colour swatch overlay, 1200x675
    - `assets/demo-approved.png` → `frontend/public/marketing/demo/approved.png` — customization demo: approved album screen, 3456x1966
  - **Hero collage**
    - `assets/hero-photo-01.png` → `frontend/public/marketing/hero/photo-01.png` — hero collage photo (image 97), 1472x1774
    - `assets/hero-photo-02.png` → `frontend/public/marketing/hero/photo-02.png` — hero collage photo (image 98), 1200x1500
    - `assets/hero-photo-03.png` → `frontend/public/marketing/hero/photo-03.png` — hero collage photo (image 99), 2400x2918
    - `assets/hero-photo-04.png` → `frontend/public/marketing/hero/photo-04.png` — hero collage photo (image 107), 736x1308
    - `assets/hero-photo-05.png` → `frontend/public/marketing/hero/photo-05.png` — hero collage photo (image 100), 1472x1852
    - `assets/hero-photo-06.png` → `frontend/public/marketing/hero/photo-06.png` — hero collage photo (image 101), 800x1104
    - `assets/hero-photo-07-bcceaf.png` → `frontend/public/marketing/hero/photo-07.png` — hero collage photo (image 104), 735x908
    - `assets/hero-photo-08-41b289.png` → `frontend/public/marketing/hero/photo-08.png` — hero collage photo (image 102), 800x537
    - `assets/hero-photo-09-7583dc.png` → `frontend/public/marketing/hero/photo-09.png` — hero collage photo (Untitled design (7) 2), 668x536
    - `assets/hero-photo-10-442cfc.png` → `frontend/public/marketing/hero/photo-10.png` — hero collage photo (Untitled design (7) 4), 488x566
    - `assets/hero-photo-11-317644.png` → `frontend/public/marketing/hero/photo-11.png` — hero collage photo (Untitled design (7) 4), 484x490
    - `assets/hero-photo-12.png` → `frontend/public/marketing/hero/photo-12.png` — hero collage photo (image 106), 1200x1500
    - `assets/hero-photo-13.png` → `frontend/public/marketing/hero/photo-13.png` — hero collage photo (image 105), 735x572
    - `assets/hero-scribble-01-2e7fd8.png` → `frontend/public/marketing/hero/scribble-01.png` — decorative scribble (row scribble 1), 656x182
    - `assets/hero-scribble-02-5fb332.png` → `frontend/public/marketing/hero/scribble-02.png` — decorative scribble (row scribble 2), 364x424
    - `assets/hero-scribble-03-3f7df0.png` → `frontend/public/marketing/hero/scribble-03.png` — decorative scribble (row scribble (1) 2), 174x536
    - `assets/hero-scribble-04-19fb02.png` → `frontend/public/marketing/hero/scribble-04.png` — decorative scribble (row scribble (1) 1), 483x536
    - `assets/hero-scribble-05-542cb2.png` → `frontend/public/marketing/hero/scribble-05.png` — decorative scribble (row scribble (4) 1), 649x165
    - `assets/hero-scribble-06-4491a3.png` → `frontend/public/marketing/hero/scribble-06.png` — decorative scribble (row scribble (5) 2), 514x432
  - **Feature cards**
    - `assets/feature-photo-01.png` → `frontend/public/marketing/features/photo-01.png` — feature card photo (image 113), 1200x1600
    - `assets/feature-photo-02.png` → `frontend/public/marketing/features/photo-02.png` — feature card photo (image 114), 1200x1599
    - `assets/feature-photo-03.png` → `frontend/public/marketing/features/photo-03.png` — feature card photo (image 115), 700x1050
    - `assets/feature-photo-04.png` → `frontend/public/marketing/features/photo-04.png` — feature card photo (image 109), 735x551
    - `assets/feature-photo-05.png` → `frontend/public/marketing/features/photo-05.png` — feature card photo (image 110), 1200x1499
    - `assets/feature-photo-06-2de83a.png` → `frontend/public/marketing/features/photo-06.png` — feature card photo (image 111), 1200x1499
- Large photos are the original uploads (14 are over 1 MB). Serve them through `next/image` so Next.js emits
  sized/modern formats; if a source is more than twice the largest size it is ever displayed at, downscale it
  to 2x that size before committing. Do not swap in a different photo.
- No placeholders: every asset above is rendered by the code. A grey box, a text stand-in such as
  "FindMyShots Studio Logo", or a solid colour where artwork belongs is a defect, not a first pass.
## Technical notes
- Breakpoints: Desktop >1024px (full layout), Tablet 640-1024px (grid wrapping), Mobile <640px (single column stack). Use Tailwind grid/flex wrapping.

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- `npx nx test frontend --testFile=page.test.tsx` checking for the presence of key marketing headings and pricing cards.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] Every asset in `## Design fidelity` is committed at its stated repo path, non-empty, and rendered by the
      code; no placeholder box or text stand-in remains, and the tokens listed there are the values in the code
- [ ] Unit tests added and green
- [ ] Lint and typecheck clean
- [ ] PR from `feature/landing-page-no-account` reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end

---ticket
title: [QA] Landing Page: E2E unauthenticated visitor views pricing and clicks signup
lane: QA
parent: [Feature] Organizer Flow: Landing Page No Account
status: to do
estimate_hours: 2
depends_on: [FE] Landing Page: layout - navigation - and static content

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: none · Lane: QA

**Restoration Note:** Re-run QA to verify the landing page restoration.

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
- Depends on: [FE] Landing Page: layout - navigation - and static content
- Blocks: none

## Test notes (how QA verifies)
- E2E script runs successfully.

## Definition of done
- [ ] All acceptance criteria pass
---end

---ticket
title: [FE] Bug: Fix landing page copy and links
lane: FE
parent: [Feature] Organizer Flow: Landing Page No Account
priority: high
status: to do
estimate_hours: 2
figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297
screenshots: specs/_figma/organizer-flow-landing-page-no-account/9731-3297.png
assets: specs/_figma/organizer-flow-landing-page-no-account/assets/manifest.json

## Context
Parent: [Feature] Organizer Flow: Landing Page No Account · Figma: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9731-3297 · Lane: FE

**Restoration Note:** These fixes were lost when the landing page was overwritten by the Nx scaffold.

## User story
As an unauthenticated organizer, I want the landing page to have correct text and links so I can sign up and contact support.

## In scope
- Correct the page title.
- Add the missing "Credit Packages" text to the Pricing section.
- Change Pricing buttons label from "Buy now" to "Select Option" and add `href` to `/signup`.
- Change Hero "Buy Credits" button anchor from `#pricing` to `/signup`.
- Add `mailto:` to the Contact link.

## Out of scope (do NOT build)
- Any layout changes or new sections.

## Acceptance criteria
- Given the browser tab, when the page renders, then the page title contains "FindMyShots Studio".
- Given the Pricing section, when it renders, then the "Credit Packages" text is visible.
- Given the Pricing section, when a user clicks "Select Option", then they are navigated to `/signup`.
- Given the Hero section, when a user clicks "Buy Credits", then they are navigated to `/signup`.
- Given the custom pricing banner, when the user clicks "Contact Us", then it opens a `mailto:` link.

## Design fidelity
- Tokens (unchanged by this ticket, but the copy it touches must keep them): Primary `#FF6100` · Text `#313131`
  · Muted `#797979` · Font `Host Grotesk` 400/500/800. Do not introduce a framework default such as
  `bg-orange-500` or `font-sans` while editing these strings.
- Assets: none — this is a copy and link fix. All 36 files are shipped by
  `[FE] Landing Page: layout - navigation - and static content`.

## Technical notes
- Branch prefix: `bug/landing-page-fixes`

## Depends on / blocks
- Depends on: none
- Blocks: none

## Test notes (how QA verifies)
- E2E test `organizer-flow-landing-page-no-account` passes.

## Definition of done
- [ ] All acceptance criteria pass
- [ ] PR from `bug/landing-page-fixes` reviewed
- [ ] Status moved to `qa` (VanPM sets it after review approves)
---end
