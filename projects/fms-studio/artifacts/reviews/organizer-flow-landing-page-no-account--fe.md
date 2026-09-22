APPROVED
Reviewed SHA: f1d3d783a039620b3049b3ed9338f9565e351136

[FE] Landing Page: layout - navigation - and static content
- Given the navigation bar, when rendered, then the "Events", "Pricing", "Sign In", and "Get Started" links are visible and point to their respective routes: `frontend/src/app/page.tsx`
- Given the Hero section, when rendered, then the "Buy Credits" button points to `/signup` and "See how it works" points to `#how-it-works`: `frontend/src/app/page.tsx`
- Given the Pricing section, when rendered, then 4 cards display exactly: "3,000", "5,000", "10,000", and "15,000" credits with prices "$150", "$250", "$500", and "$750" respectively: `frontend/src/app/page.tsx`
- Given a pricing card, when the user clicks "Select Option", then they are navigated to `/signup`: `frontend/src/app/page.tsx`
- Given the custom pricing banner, when the user clicks "Contact Us", then it opens a `mailto:` link: `frontend/src/app/page.tsx`
- Given the footer, when rendered, then the "About" and "Privacy" links point to `/about` and `/privacy`: `frontend/src/app/page.tsx`
- Given a viewport narrower than 1024px, when the pricing section renders, then the 4 cards wrap into a grid or column layout instead of overflowing horizontally: `frontend/src/app/page.tsx`

[FE] Bug: Fix landing page copy and links
- Given the browser tab, when the page renders, then the page title contains "FindMyShots Studio": `frontend/src/app/page.tsx`
- Given the Pricing section, when it renders, then the "Credit Packages" text is visible: `frontend/src/app/page.tsx`
- Given the Pricing section, when a user clicks "Select Option", then they are navigated to `/signup`: `frontend/src/app/page.tsx`
- Given the Hero section, when a user clicks "Buy Credits", then they are navigated to `/signup`: `frontend/src/app/page.tsx`
- Given the custom pricing banner, when the user clicks "Contact Us", then it opens a `mailto:` link: `frontend/src/app/page.tsx`

## Design fidelity
- Tokens exactly match specs in `frontend/src/app/global.css` and are used correctly in `frontend/src/app/page.tsx`
- assets/logo.svg: `frontend/public/brand/logo.svg` rendered in `frontend/src/app/page.tsx`
- assets/icon-shopping-bag.svg: `frontend/public/icons/shopping-bag.svg` rendered in `frontend/src/app/page.tsx`
- assets/icon-calendar-heart.svg: `frontend/public/icons/calendar-heart.svg` rendered in `frontend/src/app/page.tsx`
- assets/icon-ticket.svg: `frontend/public/icons/ticket.svg` rendered in `frontend/src/app/page.tsx`
- assets/icon-gift.svg: `frontend/public/icons/gift.svg` rendered in `frontend/src/app/page.tsx`
- assets/icon-images.svg: `frontend/public/icons/images.svg` rendered in `frontend/src/app/page.tsx`
- assets/demo-swatch-gradient.svg: `frontend/public/marketing/demo/swatch-gradient.svg` rendered in `frontend/src/app/page.tsx`
- assets/demo-my-albums.png: `frontend/public/marketing/demo/my-albums.png` rendered in `frontend/src/app/page.tsx`
- assets/demo-swatch-overlay-01.png: `frontend/public/marketing/demo/swatch-overlay-01.png` rendered in `frontend/src/app/page.tsx`
- assets/demo-swatch-overlay-02.png: `frontend/public/marketing/demo/swatch-overlay-02.png` rendered in `frontend/src/app/page.tsx`
- assets/demo-approved.png: `frontend/public/marketing/demo/approved.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-01.png: `frontend/public/marketing/hero/photo-01.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-02.png: `frontend/public/marketing/hero/photo-02.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-03.png: `frontend/public/marketing/hero/photo-03.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-04.png: `frontend/public/marketing/hero/photo-04.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-05.png: `frontend/public/marketing/hero/photo-05.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-06.png: `frontend/public/marketing/hero/photo-06.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-07-bcceaf.png: `frontend/public/marketing/hero/photo-07.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-08-41b289.png: `frontend/public/marketing/hero/photo-08.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-09-7583dc.png: `frontend/public/marketing/hero/photo-09.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-10-442cfc.png: `frontend/public/marketing/hero/photo-10.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-11-317644.png: `frontend/public/marketing/hero/photo-11.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-12.png: `frontend/public/marketing/hero/photo-12.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-photo-13.png: `frontend/public/marketing/hero/photo-13.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-scribble-01-2e7fd8.png: `frontend/public/marketing/hero/scribble-01.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-scribble-02-5fb332.png: `frontend/public/marketing/hero/scribble-02.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-scribble-03-3f7df0.png: `frontend/public/marketing/hero/scribble-03.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-scribble-04-19fb02.png: `frontend/public/marketing/hero/scribble-04.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-scribble-05-542cb2.png: `frontend/public/marketing/hero/scribble-05.png` rendered in `frontend/src/app/page.tsx`
- assets/hero-scribble-06-4491a3.png: `frontend/public/marketing/hero/scribble-06.png` rendered in `frontend/src/app/page.tsx`
- assets/feature-photo-01.png: `frontend/public/marketing/features/photo-01.png` rendered in `frontend/src/app/page.tsx`
- assets/feature-photo-02.png: `frontend/public/marketing/features/photo-02.png` rendered in `frontend/src/app/page.tsx`
- assets/feature-photo-03.png: `frontend/public/marketing/features/photo-03.png` rendered in `frontend/src/app/page.tsx`
- assets/feature-photo-04.png: `frontend/public/marketing/features/photo-04.png` rendered in `frontend/src/app/page.tsx`
- assets/feature-photo-05.png: `frontend/public/marketing/features/photo-05.png` rendered in `frontend/src/app/page.tsx`
- assets/feature-photo-06-2de83a.png: `frontend/public/marketing/features/photo-06.png` rendered in `frontend/src/app/page.tsx`

## Blocking
None

## Non-blocking
None