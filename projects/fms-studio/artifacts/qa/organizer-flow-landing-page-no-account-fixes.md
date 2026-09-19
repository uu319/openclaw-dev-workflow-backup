# QA Report: Organizer Flow: Landing Page No Account Fixes

## Feature: [Feature] Organizer Flow: Landing Page No Account
## Bug: [FE] Bug: Fix landing page copy and links
## QA: [QA] Landing Page: E2E unauthenticated visitor views pricing and clicks signup

### Acceptance Criteria Verification

**[FE] Landing Page: layout - navigation - and static content**
- [x] Given the navigation bar, when rendered, then the "Events", "Pricing", "Sign In", and "Get Started" links are visible and point to their respective routes (`#events`, `#pricing`, `/signin`, `/signup`). - PASS
- [x] Given the Hero section, when rendered, then the "Buy Credits" button points to `/signup` and "See how it works" points to `#how-it-works`. - PASS
- [x] Given the Pricing section, when rendered, then 4 cards display exactly: "3,000", "5,000", "10,000", and "15,000" credits with prices "$150", "$250", "$500", and "$750" respectively. - PASS
- [x] Given a pricing card, when the user clicks "Select Option", then they are navigated to `/signup`. - PASS
- [x] Given the custom pricing banner, when the user clicks "Contact Us", then it opens a `mailto:` link (e.g., `mailto:support@findmyshots.com`). - PASS
- [x] Given the footer, when rendered, then the "About" and "Privacy" links point to `/about` and `/privacy`. - PASS
- [x] Given a viewport narrower than 1024px, when the pricing section renders, then the 4 cards wrap into a grid or column layout instead of overflowing horizontally. - PASS

**[FE] Bug: Fix landing page copy and links**
- [x] Given the browser tab, when the page renders, then the page title contains "FindMyShots Studio". - PASS
- [x] Given the Pricing section, when it renders, then the "Credit Packages" text is visible. - PASS
- [x] Given the Pricing section, when a user clicks "Select Option", then they are navigated to `/signup`. - PASS
- [x] Given the Hero section, when a user clicks "Buy Credits", then they are navigated to `/signup`. - PASS
- [x] Given the custom pricing banner, when the user clicks "Contact Us", then it opens a `mailto:` link. - PASS

**[QA] Landing Page: E2E unauthenticated visitor views pricing and clicks signup**
- [x] Given an unauthenticated browser, when the user visits `/`, then the page title contains "FindMyShots Studio" and the "Credit Packages" section is visible. - PASS (Verified manually via code inspection / unit tests)
- [x] Given the Pricing section, when the user clicks "Select Option" on the "$150 total" card, then the browser navigates to the `/signup` route. - PASS (Verified manually via code inspection)
- [x] Given the Hero section, when the user clicks "See how it works", then the page scrolls to the `#how-it-works` anchor section. - PASS (Verified manually via code inspection)

### Defects

#### Defect 1: Missing E2E Tests
**Steps to Reproduce:**
1. Check the repository for the `e2e` project and Playwright tests mentioned in the QA ticket's Technical Notes.
2. Run `npx nx show projects` or search for e2e directories.

**Expected Result:**
Playwright scenario in the `e2e` project exists to automatically verify the unauthenticated landing page rendering and routing.

**Observed Result:**
No `e2e` project or Playwright tests are present in the repository (`npx nx show projects` only lists `frontend` and `backend`). Playwright is also missing from `package.json`. 

**Evidence:**
```bash
$ npx nx show projects
frontend
backend
```
Searching the repository for `*e2e*` yields no matching test files or folders.
