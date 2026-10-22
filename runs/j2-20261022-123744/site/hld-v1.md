# Brew Lab

## Purpose and scope

This high-level design describes how the Brew Lab page is built to meet the PRD requirements R1 to R12. Brew Lab is a small specialty coffee shop at 12, 100 Feet Road, Indiranagar, Bengaluru 560038. Customers of Brew Lab have no easy way to see the menu and prices or to order ahead and collect at the shop, and the shop has no online page that shows its name and address. The page solves this.

**Purpose**
- Show the name Brew Lab and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text.
- Show the menu of seven items with prices in rupees.
- Let customers send a pre-order through a form with the fields name, phone, items and pickup time. The form sends the order to hello@brewlab.example, where the Shop team receives it.
- Let customers collect the order at the shop.
- Work on phones, with no horizontal overflow at 360px width.

**In scope**
- One page, built as one file of plain HTML, CSS and JavaScript with no build step.
- The shop name and address as text.
- The menu with the seven items and their rupee prices.
- The pre-order form, with pickup at the shop.

**Out of scope**
- Opening hours (not decided yet), so none are shown.
- A shop phone number (the shop has none), so none is shown.
- An embedded map. The address is the only location information on the page.
- Online payment. The page has no payment fields.

**Users**
- Customers view the shop name and address, read the menu and prices, fill in and submit the pre-order form, and collect the order at the shop.
- The Shop team receives pre-orders at hello@brewlab.example.

The PRD, this HLD, the LLD and the website must contain the same facts with no contradictions.
