# Figma Inventory: Dashboard My Albums

Source: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220
Screenshot: `specs/_figma/dashboard-my-albums/9794-3220.png`

## Global layout
- Top Navigation bar: Logo ("findmyshots studio"), Nav links ("Dashboard"), Credit count ("420 Credits" pill), "Buy Credits" button (orange), Profile avatar dropdown.
- Left Sidebar (thin): 4 icons (album, layout-dashboard, square-pen, settings) and a bottom avatar circle.
- Main content area:
  - Header: Welcome greeting ("Good Morning,\nDream Marathon Org!")
  - Subheader row: "My Albums" title, "Top Up +" orange button.
  - Right controls (above grid): "Search" input with search icon, "Filter by: All Albums" dropdown.
  - Content grid: Album cards.

## Elements

1.  **Welcome Text**: "Good Morning, Dream Marathon Org!" (Host Grotesk Medium, 26px)
2.  **Section Title**: "My Albums" (Host Grotesk Medium, 20px)
3.  **"Top Up" Button**: Label "Top Up" with a `+` icon, solid orange (#FF6100) pill.
4.  **Search Input**: Placeholder "Search" with a search icon right-aligned. Outline #313131 at 50% opacity, pill shape.
5.  **Filter Dropdown**: Label "Filter by:", button shows "All Albums" with `chevron-down` icon. Outline #313131 at 50% opacity.
6.  **"Create New Album" Card**: Empty state card. Label "Create New Album" with a large `plus` icon. Light grey background (#F7F6F6), rounded corners.
7.  **Album Card Component**:
    -   Container: Light grey with a subtle gradient/shadow at the bottom.
    -   Title text: Centered, e.g., "Nike Run 2026", "Liberty Run Marathon" (Host Grotesk, 16px).
    -   Cover imagery: A fanned arrangement of 3 images (center main, left/right angled behind).
    -   Top-left action: `more-vertical` (three dots) icon for a context menu.
    -   Top-right action: `share-2` icon.
    -   Bottom-right action: `star` icon (unfilled usually, "Nike Run 2026" shows `star-filled` black).
8.  **Card Context Menu (Popover)**: Shown floating over a card.
    -   White background, slight shadow.
    -   Item 1: `edit` icon + "Edit Album"
    -   Item 2: `settings` icon + "Settings"
    -   Item 3: `trash-2` icon + "Delete Album"

## Design Tokens & Typography
-   Font: Host Grotesk throughout.
-   Primary Orange: #FF6100
-   Dark Text: #313131 or #09090B
-   Card Background / Gradients: Linear gradient on cards fading to a darker grey at the bottom (`rgba(247, 246, 246, 1) 65%`, `rgba(153, 153, 153, 1) 100%`).

## Unknowns
- Search filtering: Server-side or client-side?
- Sorting: Does the user expect newest first?
- Navigation: Where do the "Top Up", "Buy Credits", or specific card actions actually go? (Assumed out of scope / stubbed for this feature slice).
- Pagination: Are all albums loaded at once, or is it paginated/infinite scroll? (Assumed out of scope as per splitting patterns example).