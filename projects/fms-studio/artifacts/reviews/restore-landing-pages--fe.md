APPROVED
Reviewed SHA: e411d064af0346c2fe7ec0e62e1f77d9b6517719

Page route `frontend/src/app/page.tsx`: frontend/src/app/page.tsx:1
Navigation bar (Logo, "Events", "Pricing", "Sign In", "Get Started"): frontend/src/app/page.tsx:12
Hero section with photo collage and "Buy Credits" / "See how it works" buttons: frontend/src/app/page.tsx:24
Three-card "How it works" section: frontend/src/app/page.tsx:43
Large dashboard mockup section with floating orange labels: frontend/src/app/page.tsx:61
Orange features block ("Credits, not subscriptions", "One dashboard per event", "Attendees never pay"): frontend/src/app/page.tsx:73
Customization section with static font/theme pickers and album mockup: frontend/src/app/page.tsx:90
Pricing section with 4 tier cards and "Contact Us" banner: frontend/src/app/page.tsx:112
Footer (Logo, "About", "Privacy", "Made by Symph"): frontend/src/app/page.tsx:180
Correct the page title: frontend/src/app/page.tsx:4
Add the missing "Credit Packages" text to the Pricing section: frontend/src/app/page.tsx:116
Change Pricing buttons label from "Buy now" to "Select Option" and add `href` to `/signup`: frontend/src/app/page.tsx:127
Change Hero "Buy Credits" button anchor from `#pricing` to `/signup`: frontend/src/app/page.tsx:30
Add `mailto:` to the Contact link: frontend/src/app/page.tsx:173
Unit tests added and green: frontend/src/app/page.test.tsx:1 (Tests pass, tested via vitest run in frontend/)

Blocking:
- None. The PR correctly implements the acceptance criteria for both the frontend layout and the bug fixes. The static layout is complete and the routing links have the correct destinations.

Non-blocking:
- In `frontend/src/app/page.tsx:95` (Customization section text), there's a lint warning for unescaped apostrophe in `"brand's"`. Consider changing to `brand&apos;s` or escaping it properly to avoid React/Next.js hydration mismatch or build-time lint warnings down the line (though the build itself passes right now).
- The failed backend test is unrelated to this PR (caused by `AppController.getData` being undefined in the NestJS scaffold setup which was untouched by this branch).