# Screen Inventory: Event Creation: Step 3.1 — Set event password

- **Link:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9836-6520
- **Screenshot:** `specs/_figma/event-creation-step-3-1-set-password/9836-6520.png`

## Modal Layout

The modal is centered over a blurred dashboard background.

1.  **Header:**
    -   Icon: A grey circle with a lock icon.
    -   Title: "Set Album Password" (Host Grotesk, 20px, Medium, `#313131`)
    -   Subtitle: "Set a password to control access to the album." (Host Grotesk, 17px, Regular, `rgba(49, 49, 49, 0.5)`)
    -   Close button: An 'X' icon (component `2949:2312`) in the top right.

2.  **Form Fields:**
    -   **Set Password field:**
        -   Label: "Set Password*" (Host Grotesk, 18px, Regular, `#313131` with an orange asterisk `#FF6100`)
        -   Input: Grey background (`rgba(0, 0, 0, 0.05)`), rounded corners (7px).
        -   Placeholder/Value: "Hello123!" (`rgba(49, 49, 49, 0.6)`)
        -   Control: "eye" icon button inside the input on the right (component `5028:5794`).
    -   **Confirm Password field:**
        -   Label: "Confirm Password*" (Host Grotesk, 18px, Regular, `#313131` with an orange asterisk `#FF6100`)
        -   Input: Grey background (`rgba(0, 0, 0, 0.05)`), rounded corners (7px).
        -   Placeholder/Value: "*********" (`rgba(49, 49, 49, 0.6)`)
        -   Control: "eye-off" icon button inside the input on the right (component `5028:5801`).

3.  **Footer Actions:**
    -   **Secondary action:** "I’ll do this later." (Host Grotesk, 16px, Regular, underlined, `rgba(49, 49, 49, 0.5)`). Placed on the left.
    -   **Primary action:** "Save" button (Host Grotesk, 16px, Regular, White text `#FFFFFF` on Orange background `#FF6100`, rounded 7px). Placed on the right.

## Global Styles
- **Font Family:** Host Grotesk
- **Primary Text:** `#313131`
- **Secondary Text:** `rgba(49, 49, 49, 0.5)` or `rgba(49, 49, 49, 0.6)`
- **Brand Orange:** `#FF6100` (used for asterisks and primary button)
- **Input Background:** `rgba(0, 0, 0, 0.05)`
- **Modal Background:** `#FFFFFF`
