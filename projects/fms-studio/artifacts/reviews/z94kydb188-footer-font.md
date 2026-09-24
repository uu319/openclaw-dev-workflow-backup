APPROVED
Reviewed SHA: 64b3fcfb398d747a2a1ea2a04d2a55b1633156a5
- Given the footer text, when rendered, then it uses the `Actor` font (e.g., via the `font-actor` Tailwind class). - frontend/src/app/page.tsx:350
- Given the footer text, when rendered, then it does not inherit the host font or default font. - frontend/src/app/page.tsx:350
- Given the layout, when the footer is rendered, then the `font-actor` class correctly sets the font-family. - frontend/src/app/global.css:17

## Design fidelity
- Assets: none
- Tokens exactly match Figma (`#313131`, `Actor` 400 at 20px).

## Blocking
- None.

## Non-blocking
- None.
