# Screen Inventory: Event Creation Step 4

Source: Figma node 9836:6900
Screenshot: `specs/_figma/event-creation-step-4/9836-6900.png`

## Layout & Visuals
Modal overlay on top of the dashboard.
- Background overlay: `rgba(49, 49, 49, 0.3)` with background blur `blur(10px)`
- Modal background: `#FFFFFF`
- Corner radius: 20px (top only on the modal root, though usually implies all corners in CSS)

## Header
- Title: "Create Album" (26px, Medium, `#313131`)
- Subtitle: "Privacy and Access" (20px, Regular, `#313131`)
- Close icon: `x` (top right, `9810:7631`)

## Progress Indicator
Four steps, all shown as active/completed (orange circles, `#FF6100`):
1. Basic Info
2. Look & Feel
3. Access
4. Review (Current step, text under it says "Review")

## Main Content
- Title: "Review & Create" (20px, Regular, `#313131`)
- Subtitle: "Double-check everything before your album goes live." (17px, Regular, `rgba(49, 49, 49, 0.5)`)

### Left Column: Album Cover Preview
- Title: "Album Cover" (20px, Regular, `#313131`)
- Image Preview Area (404x404)
  - Dashed border: 1px `#313131` with 5,5 dashes, 16px radius
  - Background image (uploaded cover)
  - Gradient overlay at bottom: `linear-gradient(180deg, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.3) 62%)`
  - Text overlay: "Aethan and Kianna’s Wedding 2026" (30px, Hi Melody, `#FFFFFF`)
  - Button: "View Preview" inside the image area (bottom left, `#7C57FF` background, white text)

### Right Column: Details Summary
Three sections separated by 1px solid lines (`rgba(0, 0, 0, 0.5)`).
Header on left (gray `rgba(49, 49, 49, 0.5)`), Value on right (dark `#313131`).

**Section 1: Basic Info**
- Album Title: Aethan and Kianna’s Wedding
- Description: -
- Event Date: June 14, 2036
- Location: Indian Ocean, Sri Lanka
- Category: Celebration

**Section 2: Look & Feel**
- Album Font: Hi Melody
- Album Theme: Grassy

**Section 3: Access**
- Privacy and Access: Password Protected

**Action Button**
- Top right of the summary area: "Edit" button (`#FF6100` background, white text)

## Footer
- "Create ->" button (Bottom right, `#FF6100` to `#FF8739` gradient, white text)