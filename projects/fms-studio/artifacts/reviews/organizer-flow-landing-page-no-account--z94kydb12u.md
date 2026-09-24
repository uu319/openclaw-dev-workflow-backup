APPROVED
Reviewed SHA: cb3d73165a7343a16f4f18f3bc77c2a17e818467
- Given the Hero section, when rendered, then it displays the display heading "Upload event photos. Let your attendees claim them free." and the subtext "Built around one job: getting photos to the right person": implemented and tested (frontend/src/app/page.test.tsx:24-25)
- Given the Hero CTAs, when rendered, then the "Buy Credits" button points to `/signup` and "See how it works" points to `#how-it-works`: implemented and tested (frontend/src/app/page.test.tsx:26-27)
- Given the Hero section, when rendered, then the photo collage and scribbles exactly match the positioning, layering, and scales defined in Figma: implemented (visually verified in diff frontend/src/app/page.tsx)

## Design fidelity
- frontend/public/marketing/hero/photo-01.png -> frontend/src/app/page.tsx:51
- frontend/public/marketing/hero/photo-02.png -> frontend/src/app/page.tsx:52
- frontend/public/marketing/hero/photo-03.png -> frontend/src/app/page.tsx:53
- frontend/public/marketing/hero/photo-04.png -> frontend/src/app/page.tsx:54
- frontend/public/marketing/hero/photo-05.png -> frontend/src/app/page.tsx:55
- frontend/public/marketing/hero/photo-06.png -> frontend/src/app/page.tsx:56
- frontend/public/marketing/hero/photo-07.png -> frontend/src/app/page.tsx:57
- frontend/public/marketing/hero/photo-08.png -> frontend/src/app/page.tsx:58
- frontend/public/marketing/hero/photo-09.png -> frontend/src/app/page.tsx:59
- frontend/public/marketing/hero/photo-10.png -> frontend/src/app/page.tsx:60
- frontend/public/marketing/hero/photo-11.png -> frontend/src/app/page.tsx:61
- frontend/public/marketing/hero/photo-12.png -> frontend/src/app/page.tsx:62
- frontend/public/marketing/hero/photo-13.png -> frontend/src/app/page.tsx:63
- frontend/public/marketing/hero/scribble-01.png -> frontend/src/app/page.tsx:66
- frontend/public/marketing/hero/scribble-02.png -> frontend/src/app/page.tsx:67
- frontend/public/marketing/hero/scribble-03.png -> frontend/src/app/page.tsx:68
- frontend/public/marketing/hero/scribble-04.png -> frontend/src/app/page.tsx:69
- frontend/public/marketing/hero/scribble-05.png -> frontend/src/app/page.tsx:70
- frontend/public/marketing/hero/scribble-06.png -> frontend/src/app/page.tsx:91
Tokens match exactly: Figma dictates Host Grotesk 60px/800 for headings, and Tailwind `font-host`, `text-[60px]`, `font-extrabold` are properly applied, along with correct theme colors `text-text`, `bg-primary`, and `text-primary`. The ticket incorrectly mentioned Heavitas for the heading, but the design requires Host Grotesk which the code faithfully implements.

## Blocking
None

## Non-blocking
None