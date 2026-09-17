# Organizer Flow: Buying Credits steps 5, 5.1, 5.2

## Goal
I can buy credits to upload photos, see the pricing, and enter payment details.

## Screen 1: Dashboard with Buy Credits button
**Link:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-4376
**Screenshot:** `specs/_figma/buying-credits/9878:4376.png`

1. **Header**
   - "Good Morning, Dream Marathon Org!"
   - Search bar: "Search" input
   - Filter dropdown: "Filter by: All Albums"
2. **Albums Section**
   - Heading: "My Albums"
   - Button: "Top Up +" (orange pill)
3. **Top Navigation/Status**
   - "Dashboard" (text link)
   - Status pill: "420 Credits" (white with orange border)
   - Button: "Buy Credits" (solid orange pill)
   - User avatar with dropdown

## Screen 2: Buy Credits Modal (Package Selection)
**Link:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9878-3930
**Screenshot:** `specs/_figma/buying-credits/9878:3930.png`

1. **Modal Header**
   - Title: "Buy Credits"
   - Subtitle: "1 credit = 1 photo upload. Credits never expire."
   - Close button: "x" icon
2. **Current Status**
   - "Current Balance" / "420 credits" (in a light grey block)
3. **Package Grid (2x2)**
   - Option 1: "3,000 credits" / "$150.00 total"
   - Option 2: "5,000 credits" / "$250.00 total"
   - Option 3: "10,000 credits" / "$500.00 total"
   - Option 4: "15,000 credits" / "$750.00 total"
   - (Note: 5,000 credits option is shown with an orange number, perhaps indicating it's selected or highlighted)
4. **Rate Info**
   - "Rate: $0.05 per credit"
5. **Contact Banner**
   - "Need fewer than 3,000 or more than 15,000?"
   - Button: "Contact Us" (orange)
6. **Footer Actions**
   - Link: "Cancel"
   - Button: "Buy Now" (orange)

## Screen 3: Payment Details Modal
**Link:** https://www.figma.com/design/ve5qHWxtQeBIxDF9xehnbn/FindMyShots-Branding?node-id=9884-3853
**Screenshot:** `specs/_figma/buying-credits/9884:3853.png`

1. **Modal Header**
   - Icon: Wallet/Card
   - Title: "Payment Details"
   - "Secure Payment" (green with shield check icon)
   - Subtitle: "1 credit = 1 photo upload. Credits never expire."
   - Close button: "x" icon
2. **Payment Method Selector**
   - "Card" (selected, with icon)
   - "Paypal" (with icon)
   - "Apple" (with icon)
3. **Order Summary (grey block)**
   - "Package" / "5,000 credits"
   - "Current balance" / "420"
   - "New balance" / "5,420"
   - "Total due" / "$250.00"
4. **Card Form**
   - "Name on Card*" input (placeholder "e.g Juan dela Cruz")
   - "Card Number*" input (placeholder "e.g Juan dela Cruz" - Note: This placeholder is likely a design copy-paste error and should probably be a card number format, but we record it verbatim)
   - "Expiry*" input (placeholder "MM/YY")
   - "CVC*" input (placeholder "123")
5. **Footer Actions**
   - Link: "Cancel"
   - Button: "Complete Purchase" (orange gradient)

## Flows in/out
- User accesses this flow from the Dashboard by clicking "Buy Credits" or "Top Up +".
- Clicking "Buy Credits" or "Top Up +" opens the Package Selection Modal.
- In the Package Selection Modal, clicking "Cancel" or "x" closes the modal.
- In the Package Selection Modal, clicking "Buy Now" proceeds to the Payment Details Modal.
- In the Payment Details Modal, clicking "Cancel" returns to the Package Selection Modal or closes it entirely (needs clarification, assuming it goes back or closes).
- In the Payment Details Modal, clicking "Complete Purchase" submits the payment and transitions to the Credits Added success modal (Step 5.3, `artifacts/specs/credits-added-success.md`).
- "Contact Us" likely opens a mailto or contact form.

## Unknowns
- Does clicking "Cancel" on the Payment Details modal go back to the Package Selection modal, or does it close the modal entirely? (Spike or assumption: typical pattern is back or close. We'll assume close for simplicity or let FE handle standard modal behaviour).
- Are there validation errors needed for the card form beyond standard empty checks? (e.g. Stripe integration handles this).
- What payment gateway is used? (Assuming Stripe based on standard SaaS).
- What is the default selected package? (The design shows 5,000 highlighted).