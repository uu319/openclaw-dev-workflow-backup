CHANGES REQUESTED
Reviewed SHA: 3d06ebe9b2d8b8bff1a187edf8a55dbda642d350
- Given the footer text, when rendered, then it uses the `Actor` font (e.g., via the `font-actor` Tailwind class).: MISSING
- Given the footer text, when rendered, then it does not inherit the host font or default font.: MISSING
- Given the layout, when the footer is rendered, then the `font-actor` class correctly sets the font-family.: MISSING
## Design fidelity
- Tokens: MISSING (text uses Host Grotesk via font-host class rather than Actor)
## Blocking
- frontend/src/app/page.tsx:30: The inner div explicitly applies `font-host`, replacing `font-actor` and failing the AC to use the Actor font.
- frontend/src/app/page.tsx:28: The `font-actor` class added to the footer element does not apply because its children override it with `font-host`.
## Non-blocking
- none
