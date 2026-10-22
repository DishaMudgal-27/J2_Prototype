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

## Pages

Brew Lab has one page. It is one file of plain HTML, CSS and JavaScript with no build step, so there are no other pages to link to. The page has three parts.

**Shop name and address**
- Shows the name Brew Lab as text.
- Shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text.
- Has no embedded map. The address is the only location information on the page.

**Menu**
- Lists exactly seven items with prices in rupees: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140 and Banana bread slice 120.
- Each price matches the number given for that item in the PRD.

**Pre-order form**
- Has the fields name, phone, items and pickup time, and no other fields.
- Sends the order to hello@brewlab.example, where the Shop team receives it.
- Customers collect the order at the shop. The page takes no online payment and has no payment fields.

**Phone layout**
- The page works on phones, with no horizontal overflow at 360px width.

**Left out of the page**
- No opening hours (not decided yet).
- No shop phone number (the shop has none). The phone field in the form belongs to the person ordering and is not a shop phone number.
- No embedded map.
- No online payment.

Assumption: the parts appear on the page in the order shown above (name and address, menu, pre-order form).

## Assumptions to confirm

- the parts appear on the page in the order shown above (name and address, menu, pre-order form).
