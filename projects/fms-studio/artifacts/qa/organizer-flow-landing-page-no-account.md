# QA Report: organizer-flow-landing-page-no-account
**Commit SHA:** 5269e8b1fba82443b2f6134eb65c62f6c053151f

## Acceptance Criteria
- PASS: Header contains Logo ("findmyshots studio"), Links (Events, Pricing, Sign In), and Get Started button.
- FAIL: Footer contains "findmyshots" text and links, but it does not use the `Actor` font as required by the global fonts spec in the Figma extraction.
- PASS: Hero section contains collage of images and Buy Credits button.
- PASS: Value Proposition sections render correctly.
- PASS: Pricing section renders packages as expected.

## Design fidelity
### Manifest Assets
- PASS: `frontend/public/brand/logo.svg`
- PASS: `frontend/public/icons/shopping-bag.svg`
- PASS: `frontend/public/icons/calendar-heart.svg`
- PASS: `frontend/public/icons/ticket.svg`
- PASS: `frontend/public/icons/gift.svg`
- PASS: `frontend/public/icons/images.svg`
- PASS: `frontend/public/marketing/demo/swatch-gradient.svg`
- PASS: `frontend/public/marketing/demo/my-albums.png`
- PASS: `frontend/public/marketing/demo/swatch-overlay-01.png`
- PASS: `frontend/public/marketing/demo/swatch-overlay-02.png`
- PASS: `frontend/public/marketing/demo/approved.png`
- PASS: `frontend/public/marketing/hero/photo-01.png`
- PASS: `frontend/public/marketing/hero/photo-02.png`
- PASS: `frontend/public/marketing/hero/photo-03.png`
- PASS: `frontend/public/marketing/hero/photo-04.png`
- PASS: `frontend/public/marketing/hero/photo-05.png`
- PASS: `frontend/public/marketing/hero/photo-06.png`
- PASS: `frontend/public/marketing/hero/photo-07.png`
- PASS: `frontend/public/marketing/hero/photo-08.png`
- PASS: `frontend/public/marketing/hero/photo-09.png`
- PASS: `frontend/public/marketing/hero/photo-10.png`
- PASS: `frontend/public/marketing/hero/photo-11.png`
- PASS: `frontend/public/marketing/hero/photo-12.png`
- PASS: `frontend/public/marketing/hero/photo-13.png`
- PASS: `frontend/public/marketing/hero/scribble-01.png`
- PASS: `frontend/public/marketing/hero/scribble-02.png`
- PASS: `frontend/public/marketing/hero/scribble-03.png`
- PASS: `frontend/public/marketing/hero/scribble-04.png`
- PASS: `frontend/public/marketing/hero/scribble-05.png`
- PASS: `frontend/public/marketing/hero/scribble-06.png`
- PASS: `frontend/public/marketing/features/photo-01.png`
- PASS: `frontend/public/marketing/features/photo-02.png`
- PASS: `frontend/public/marketing/features/photo-03.png`
- PASS: `frontend/public/marketing/features/photo-04.png`
- PASS: `frontend/public/marketing/features/photo-05.png`
- PASS: `frontend/public/marketing/features/photo-06.png`

### Tokens & Fonts
- FAIL: The footer text ("findmyshots", "About", "Privacy", "Made by Symph") is not using the `Actor` font. The `font-actor` tailwind class is defined in `global.css` but never used in `page.tsx` for the footer elements. The footer links use `font-host`.

## Defects
### Defect 1: Footer not using Actor font
- **Steps:** Navigate to the landing page and inspect the footer elements.
- **Expected:** The footer text should use the `Actor` font, per the design specification global fonts list.
- **Observed:** The footer text ("findmyshots", "About", "Privacy", "Made by Symph") uses `font-host` or inherits the default font.
- **Evidence Path:** `frontend/src/app/page.tsx` lines 30-34, the tailwind classes applied lack `font-actor`.
