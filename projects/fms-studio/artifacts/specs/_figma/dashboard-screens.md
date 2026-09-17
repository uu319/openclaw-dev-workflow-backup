# Dashboard Screens Inventory

## My Albums (9794:3220)
- Link: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-3220
- Screenshot: `specs/_figma/dashboard-screens/9794-3220.png`

### Layout & Elements
1. **Sidebar Navigation (Left)**
   - Logo mark (image 108) at top
   - Navigation icons (album, layout-dashboard, square-pen, settings)
   - User profile avatar at bottom
2. **Top Header**
   - Studio logo mark + "studio" text
   - "Dashboard" breadcrumb/title
   - "420 Credits" badge (orange pill with dot)
   - "Buy Credits" button
   - User profile dropdown with avatar and chevron-down
3. **Main Content Header**
   - Title: "My Albums"
   - Search input (pill shape, "Search" placeholder, search icon)
   - Filter dropdown ("Filter by: All Albums" with chevron-down)
   - Primary action: "Top Up" button (+ icon)
4. **Welcome Area**
   - "Good Morning, Dream Marathon Org!"
5. **Album Grid**
   - Each card has:
     - Cover image (rounded rectangle)
     - Album Title (e.g., "Nike Run 2026", "Liberty Run Marathon", "Great Lakes Run 2025")
     - Bottom actions: 3-dot menu (horizontal ellipses) and "share-2" icon
   - First card placeholder is a "Create New Album" action with a large plus icon
   - Some cards have a "star" or "star-filled" icon in top right

6. **Context Menu (Overlay/Popover for 3-dot menu)**
   - Displayed in the bottom right corner (node 9794:5566)
   - "Edit Album" (with edit icon)
   - "Settings" (with settings icon)
   - "Delete Album" (with trash-2 icon)

## Dashboard (9794:6008)
- Link: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6008
- Screenshot: `specs/_figma/dashboard-screens/9794-6008.png`

### Layout & Elements
1. **Navigation & Header** (Same as My Albums)
2. **Main Content Header**
   - Title: "My Overview"
   - Welcome message: "Good Morning, Dream Marathon Org!"
3. **Credit Balance Section**
   - "Credit Balance" header
   - Big number: "4,320" (credits left)
   - Subtext: "2,680 used this month · out of 7,000 loaded"
   - Progress bar (orange/grey pill)
   - Action: "Top Up" button (+ icon)
4. **Stats Row (4 cards)**
   - "Albums Total" (12)
   - "Photos Uploaded" (8,940)
   - "Attendee Downloads" (6,102)
   - "Match Rate" (91%)
5. **Bottom Row**
   - Left side: "Most Downloaded Marathon"
     - Title: "Liberty Run Marathon 2026"
     - Stats: "2,340 Downloads · Riverbend Summit"
     - Large image preview
   - Right side: "Photos Uploaded - Last 6 Months"
     - Bar chart showing April through September
     - September bar is highlighted (orange), others are grey

## My Drafts (9794:6547)
- Link: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9794-6547
- Screenshot: `specs/_figma/dashboard-screens/9794-6547.png`

### Layout & Elements
1. **Navigation & Header** (Same as My Albums)
2. **Main Content Header**
   - Title: "My Drafts"
   - Welcome message: "Good Morning, Dream Marathon Org!"
   - Search input (pill shape, "Search" placeholder)
   - Primary action: "Top Up" button (+ icon)
3. **Drafts Grid**
   - Same card structure as Albums, but cover images have a grey overlay/placeholder styling or show as empty states with image icons ("Publish" button shown on some)
   - Empty card placeholder with "Create New Album" action
   - Titles: "Nike Run 2026", "Fun Run Marathon"

### Visual Design (Common)
- Font: Host Grotesk
- Brand Color: Orange (`#FF6100`)
- Text Primary: Dark Grey (`#313131`)
- Backgrounds: Light Grey (`#F7F6F6`) for cards/sections
- Corners: Heavily rounded (pill shapes for buttons/inputs, 20px radius for cards)
