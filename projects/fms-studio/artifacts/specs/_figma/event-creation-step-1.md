# Screen Inventory: Event Creation Step 1 - Basic Info

Source: Figma node 9810-7244
Screenshot: `specs/_figma/event-creation-step-1/9810-7244.png`

## Layout and General Properties
- Modal dialog over a blurred dashboard background.
- Width: 1408px, Height: 828px.
- Background: White (`#FFFFFF`).
- Close button (`x` icon) at top right.

## Headers
- H1: "Create Album" (Host Grotesk, 26px, Medium, `#313131`)
- Subhead: "Event Details" (Host Grotesk, 20px, Regular, `#313131`)

## Step Indicator (Stepper)
4 steps connected by lines:
1. Active: Orange circle (`#FF6100`), white text "1", label below "Basic Info" (`#313131`).
2. Inactive: Grey circle (`#F3F3F5`), grey text "2" (`#9C9FA4`), label below "Look & Feel" (Grey).
3. Inactive: Grey circle (`#F3F3F5`), grey text "3" (`#9C9FA4`), label below "Access" (Grey).
4. Inactive: Grey circle (`#F3F3F5`), grey text "4" (`#9C9FA4`), label below "Review" (Grey).

## Form Elements
All inputs have a light grey background (`rgba(0, 0, 0, 0.05)`). Mandatory fields have an orange asterisk (`*`).

1. **Album Title***
   - Type: Text input
   - Placeholder: "e.g. philippine-marathon-2025"

2. **Description (Optional)**
   - Type: Textarea
   - Helper text (bottom right inside textarea): "0/255"

3. **Location***
   - Type: Text input
   - Placeholder: "e.g. Manila, Philippines"

4. **Category (Optional)**
   - Type: Select/Dropdown
   - Placeholder: "Select"
   - Icon: Chevron down on the right.

5. **Start Date***
   - Type: Date picker input
   - Placeholder: "dd/mm/yyyy"
   - Icon: Calendar icon on the right.

6. **End Date (Optional)**
   - Type: Date picker input
   - Placeholder: "dd/mm/yyyy"
   - Icon: Calendar icon on the right.

## Actions
- **Next Step** button
  - Location: Bottom right
  - Style: Orange background (`rgba(255, 97, 0, 0.5)`), white text, right arrow icon.
  - Label: "Next Step"