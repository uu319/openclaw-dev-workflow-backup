# Screen Inventory: Credits Added Success

Source: Figma node 9884-4390.
Screenshot: `specs/_figma/credits-added-success/9884-4390.png`

## Background

The background shows the "My Albums" dashboard blurred out by a backdrop filter (`blur(10px)`).

## Buy Credits Modal

A central, rounded white modal (`682x414`) that confirms credits were added successfully.

### Layout & Elements (Top to Bottom)
1. **Close button:** Top right `x` icon (SVG `heroicons-outline/x`, component `9810:7631`).
2. **Success Icon:** Orange checkmark circle icon (`heroicons-outline/check-circle`, component `2328:2338`).
3. **Heading:** "Credits Added!" (`36px` Host Grotesk, color `#313131`).
4. **Message Text:** "5,000 credits have been added to your account." (`16px` Host Grotesk, color `rgba(49, 49, 49, 0.7)`).
5. **Balance Box:** A light gray (`#FAFAFA`) rectangular box with rounded corners containing the updated balance.
   - **Total Credits:** "5,420" (`40px` Host Grotesk Bold, color `#FF6100` / orange).
   - **Label:** "credits available" (`18px` Host Grotesk, color `rgba(49, 49, 49, 0.6)`).
6. **Done Button:**
   - Label: "Done" (`18px` Host Grotesk, color `#FFFFFF`).
   - Background: Orange linear gradient button with rounded corners.
   - Size: `233x42`.

## Unknowns
- Does closing the modal via the 'x' or 'Done' button redirect the user anywhere, or just dismiss the modal and un-blur the dashboard underneath? Assuming it simply dismisses the modal for now.