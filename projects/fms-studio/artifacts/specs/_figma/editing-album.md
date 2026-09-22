# Editing Album Screen Inventory

## Screen 1: Album (Dashboard View)
**Link:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-4695
**Screenshot:** `specs/_figma/editing-album/10009-4695.png`

**Visible Elements:**
1. Album Grid Item (e.g., "Nike Run 2026")
2. Action Menu Trigger (three vertical dots "⋮") on the top left of the album cover.
3. Share Trigger (share icon) on the top right of the album cover.

## Screen 2: Edit Album Menu
**Link:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10041-4424
**Screenshot:** `specs/_figma/editing-album/10041-4424.png`

**Visible Elements:**
1. Popover menu positioned below/relative to the "⋮" trigger.
2. Menu Item 1: "Edit Album" (with pencil/edit icon).
3. Menu Item 2: "Share Album" (with user-plus icon).
4. Menu Item 3: "Delete Album" (with trash icon).

## Screen 3: Edit Album Modal
**Link:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=10009-5369
**Screenshot:** `specs/_figma/editing-album/10009-5369.png`

**Visible Elements:**
1. Modal Header: "Edit Album" with an "X" (close) button on the top right.
2. Form Fields (Left Column):
   - "Album Title*" (input, value "Nike Run 2026")
   - "Description (Optional)" (textarea, value empty, character count "0/255")
3. Form Fields (Right Column):
   - "Location*" (input, value "Spokane, Washington")
   - "Category (Optional)" (dropdown, value "Marathon")
   - "Start Date*" (date input, value "06/11/2003")
   - "End Date (Optional)" (date input, value "06/11/2003")
4. Album Cover Upload Area (Left below Description):
   - "Upload Album Cover (Optional)" label with sub-label "Recommended: 400x400px."
   - Current cover image shown ("Nike Run 2026" text overlaid)
   - "Remove" button (with "x" icon) overlaid on the bottom left.
   - "Reupload" button (with upload icon) overlaid on the bottom right.
   - Helper text below: "If no album cover is uploaded, the first three uploaded photos become the album thumbnails."
5. Album Font Selection (Right below End Date):
   - "Album Font" label and helper text.
   - Six selectable font cards: Host Grotesk (Selected, highlighted with orange border), Honfleur, High Tower, Hubbali, Hi Melody, Helvetica.
6. Theme Color Selection (Right below Album Font):
   - "Theme Color" label and helper text.
   - Ten color swatches and one "plus" (custom/add) button.
7. Modal Footer:
   - "Save Changes →" button (primary orange button).

## Design tokens
- Primary Orange: `#FF6100` (Stroke/Button background)
- Gradient Orange (Save Button): `linear-gradient(180deg, rgba(255, 100, 4, 1) 0%, rgba(255, 135, 57, 1) 100%)`
- Text Dark: `#313131` (Headings, primary text)
- Text Light: `rgba(49, 49, 49, 0.5)` (Helper text, placeholder)
- Input Background: `rgba(0, 0, 0, 0.05)`
- Modal Background: `#FFFFFF`
- Selected Font Border: `#FF6100` (Stroke weight: 3px)
- Fonts:
  - Base/Headings: `Host Grotesk` (Weights: 400, 500, 600)
  - Display Options: `Host Grotesk`, `Honfleur`, `High Tower Text`, `Hubballi`, `Hi Melody`, `Helvetica LT Std`

## Assets
- `assets/theme-swatch-green.png` — Green Theme Color Swatch (10009:5416) → `frontend/public/images/theme-swatch-green.png`
- `assets/theme-swatch-pink.png` — Pink Theme Color Swatch (10009:5418) → `frontend/public/images/theme-swatch-pink.png`