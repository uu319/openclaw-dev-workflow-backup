# Screen Inventory: Event Creation Step 3

Link: https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-5766
Screenshot: `specs/_figma/event-creation-step-3/9836-5766.png`

## Visible Elements

1.  **Header (Modal/Wizard)**
    *   Title: "Create Album"
    *   Subtitle: "Privacy and Access"
    *   Close icon (X button at top right)

2.  **Wizard Progress Indicator**
    *   Step 1: "Basic Info" (completed, orange)
    *   Step 2: "Look & Feel" (completed, orange)
    *   Step 3: "Access" (current, orange)
    *   Step 4: "Review" (upcoming, grey)

3.  **Section Header**
    *   Title: "Privacy and Access"
    *   Helper text: "Choose who can find and view this album. You can change this any time after creating it."

4.  **Privacy Options (Radio Buttons/Cards)**
    *   **"Public (Default)"** (Currently selected, orange radio)
        *   Icon: Users (two people)
        *   Description text: "Listed and visible to everyone — attendees can find it without needing a link."
    *   **"Hidden"**
        *   Icon: Eye crossed out
        *   Description text: "Not visible to anyone yet — use this while you're still setting up or uploading. Nobody can view or claim photos."
    *   **"Link only"**
        *   Icon: Link (chain)
        *   Description text: "Not listed anywhere. Only people who have the direct link can view or claim photos."
    *   **"Restricted"**
        *   Icon: Circle crossed out
        *   Description text: "Only specific people you invite by username can view this album — everyone else is blocked, even with the link."
    *   **"Password protected"**
        *   Icon: Lock
        *   Description text: "Anyone with the link can find it, but needs a password before they can view or claim photos."

5.  **Actions**
    *   **"Next Step →"** Button (Orange, Primary)

## Layout & Visual States
*   **Layout:** A large modal window overlaying the dashboard. Top header with close button. Stepper below. Main content is a 2-column grid of selectable cards for privacy options. A "Next Step" button is anchored at the bottom right.
*   **Colors:** White modal background (`#FFFFFF`), Orange primary (`#FF6100`), Light gray card backgrounds (`#F3F3F5` or `rgba(0, 0, 0, 0.05)`), Text mostly dark gray (`#313131`).
*   **Fonts:** Host Grotesk throughout.
*   **Selected State:** The "Public (Default)" card has a filled orange radio button. Unselected cards have an empty grey outline circle.