# Spec: Event Creation Step 2 — Look & Feel

Source: Figma node 9836-3977. Written 2026-09-16 by VanPM.

## Screen Inventory

- Link: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-3977
- Screenshot: `specs/_figma/event-creation-step-2/9836-3977.png`

### Layout & Sections
- Modal header: "Create Album", "Look & Feel" with close (`x`) button.
- Progress tracker: Steps 1 (Basic Info, completed), 2 (Look & Feel, active), 3 (Access, upcoming), 4 (Review, upcoming).
- Main content split into two columns:
  - Left column: Upload Album Cover.
  - Right column: Album Font, Theme Color.
- Footer actions: "View Preview", "Next Step ->".

### Left Column: Upload Album Cover
1. Heading: "Upload Album Cover (Optional)"
2. Sub-heading: "Recommended: 400x400px."
3. Upload area: Dashed border (`rgba(0, 0, 0, 0.05)`, stroke `#313131`), showing a placeholder/preview image (Aethan and Kianna's Wedding 2026).
4. Helper text: "If no album cover is uploaded, the first three uploaded photos become the album thumbnails."

### Right Column: Album Font
1. Heading: "Album Font"
2. Description: "Select a font style for the album. This will be applied to album text and headings."
3. Font grid (3x2):
   - "Aa Host Grotesk"
   - "Aa Honfleur"
   - "Aa High Tower"
   - "Aa Hubbali"
   - "Aa Hi Melody" (Active state: `border: 3px solid #FF6100`)
   - "Aa Helvetica"

### Right Column: Theme Color
1. Heading: "Theme Color"
2. Description: "Select a theme color for the album. This color will be used for buttons and other accent elements."
3. Color swatches (10 colors + 1 add button):
   - Red (`#E53935`)
   - Orange (`#FF6100`)
   - Yellow (`#FED448`)
   - Green (`#31B85C` gradient)
   - Pink (`#EE08E7` gradient)
   - Teal (`#357992`)
   - Dark Gray (`#535862`)
   - Purple (`#7C57FF`)
   - Black (`#000000`)
   - Plus button (`+`) for custom color.

### Footer Buttons
1. "View Preview" (`#FF6100` fill, white text).
2. "Next Step ->" (Orange gradient fill, white text).
