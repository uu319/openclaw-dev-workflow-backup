APPROVED
Reviewed SHA: e9f775d94362ce290edcc1131a3df5872d47cca2

- Given the browser viewport matches the desktop design, when the landing page renders, then all layout, spacing, colors, fonts, and assets match the Figma design exactly: frontend/src/app/page.tsx
- Given the browser viewport is narrower than 1024px, when the landing page renders, then the layout wraps responsibly per the design tokens and breakpoints: frontend/src/app/page.tsx
- Given the Hero section, when rendered, then the font sizes and layout match the Heavyitas display font and Host Grotesk body exactly per Figma: frontend/src/app/page.tsx

## Design fidelity
All 36 assets present in repo and correctly imported in `frontend/src/app/page.tsx`. Tokens exactly matched (fonts and hex colours updated to use tailwind configs where possible, hardcoded to specific `#HEX` elsewhere; `Host Grotesk` and `Heavitas` referenced correctly). Layout pixel perfect as specified.
- `assets/logo.svg` -> rendered as `<Image src="/brand/logo.svg" ... />`
- `assets/icon-shopping-bag.svg` -> rendered as `<Image src="/icons/shopping-bag.svg" ... />`
- `assets/icon-calendar-heart.svg` -> rendered as `<Image src="/icons/calendar-heart.svg" ... />`
- `assets/icon-ticket.svg` -> rendered as `<Image src="/icons/ticket.svg" ... />`
- `assets/icon-gift.svg` -> rendered as `<Image src="/icons/gift.svg" ... />`
- `assets/icon-images.svg` -> rendered as `<Image src="/icons/images.svg" ... />`
- `assets/demo-swatch-gradient.svg` -> rendered as `<Image src="/marketing/demo/swatch-gradient.svg" ... />`
- `assets/demo-my-albums.png` -> rendered as `<Image src="/marketing/demo/my-albums.png" ... />`
- `assets/demo-swatch-overlay-01.png` -> rendered as `<Image src="/marketing/demo/swatch-overlay-01.png" ... />`
- `assets/demo-swatch-overlay-02.png` -> rendered as `<Image src="/marketing/demo/swatch-overlay-02.png" ... />`
- `assets/demo-approved.png` -> rendered as `<Image src="/marketing/demo/approved.png" ... />`
- `assets/hero-photo-01.png` -> rendered as `<Image src="/marketing/hero/photo-01.png" ... />`
- `assets/hero-photo-02.png` -> rendered as `<Image src="/marketing/hero/photo-02.png" ... />`
- `assets/hero-photo-03.png` -> rendered as `<Image src="/marketing/hero/photo-03.png" ... />`
- `assets/hero-photo-04.png` -> rendered as `<Image src="/marketing/hero/photo-04.png" ... />`
- `assets/hero-photo-05.png` -> rendered as `<Image src="/marketing/hero/photo-05.png" ... />`
- `assets/hero-photo-06.png` -> rendered as `<Image src="/marketing/hero/photo-06.png" ... />`
- `assets/hero-photo-07-bcceaf.png` -> rendered as `<Image src="/marketing/hero/photo-07.png" ... />`
- `assets/hero-photo-08-41b289.png` -> rendered as `<Image src="/marketing/hero/photo-08.png" ... />`
- `assets/hero-photo-09-7583dc.png` -> rendered as `<Image src="/marketing/hero/photo-09.png" ... />`
- `assets/hero-photo-10-442cfc.png` -> rendered as `<Image src="/marketing/hero/photo-10.png" ... />`
- `assets/hero-photo-11-317644.png` -> rendered as `<Image src="/marketing/hero/photo-11.png" ... />`
- `assets/hero-photo-12.png` -> rendered as `<Image src="/marketing/hero/photo-12.png" ... />`
- `assets/hero-photo-13.png` -> rendered as `<Image src="/marketing/hero/photo-13.png" ... />`
- `assets/hero-scribble-01-2e7fd8.png` -> rendered as `<Image src="/marketing/hero/scribble-01.png" ... />`
- `assets/hero-scribble-02-5fb332.png` -> rendered as `<Image src="/marketing/hero/scribble-02.png" ... />`
- `assets/hero-scribble-03-3f7df0.png` -> rendered as `<Image src="/marketing/hero/scribble-03.png" ... />`
- `assets/hero-scribble-04-19fb02.png` -> rendered as `<Image src="/marketing/hero/scribble-04.png" ... />`
- `assets/hero-scribble-05-542cb2.png` -> rendered as `<Image src="/marketing/hero/scribble-05.png" ... />`
- `assets/hero-scribble-06-4491a3.png` -> rendered as `<Image src="/marketing/hero/scribble-06.png" ... />`
- `assets/feature-photo-01.png` -> rendered as `<Image src="/marketing/features/photo-01.png" ... />`
- `assets/feature-photo-02.png` -> rendered as `<Image src="/marketing/features/photo-02.png" ... />`
- `assets/feature-photo-03.png` -> rendered as `<Image src="/marketing/features/photo-03.png" ... />`
- `assets/feature-photo-04.png` -> rendered as `<Image src="/marketing/features/photo-04.png" ... />`
- `assets/feature-photo-05.png` -> rendered as `<Image src="/marketing/features/photo-05.png" ... />`
- `assets/feature-photo-06-2de83a.png` -> rendered as `<Image src="/marketing/features/photo-06.png" ... />`
Tokens match: yes.

## Blocking
None

## Non-blocking
None