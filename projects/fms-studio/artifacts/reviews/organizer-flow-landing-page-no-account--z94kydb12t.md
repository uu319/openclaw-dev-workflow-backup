APPROVED
Reviewed SHA: 5269e8b1fba82443b2f6134eb65c62f6c053151f
- Header links pointing to routes (#events, #pricing, /signin, /signup): frontend/src/app/page.tsx:18, frontend/src/app/page.test.tsx:19
- Footer links pointing to /about, /privacy: frontend/src/app/page.tsx:33, frontend/src/app/page.test.tsx:28
- Header and footer wrap spacing for narrow viewport (<1024px): frontend/src/app/page.tsx:17, frontend/src/app/page.test.tsx:36
## Design fidelity
- frontend/public/brand/logo.svg: frontend/src/app/page.tsx:14
- Tokens match
## Blocking
- None
## Non-blocking
- frontend/src/app/global.css:4: The `Actor` font was added to global CSS as stated in the spec, but since the raw Figma node `9773:3520` actually specified `Host Grotesk` for the footer text via text overrides, the code correctly used `font-host` instead of `font-actor`. The unused `--font-actor` import could be removed, but this is non-blocking.
