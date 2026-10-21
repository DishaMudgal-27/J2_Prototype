# Brew Lab

## Purpose and scope

This document is the high-level design for the Brew Lab website. Brew Lab is a small specialty coffee shop in Indiranagar, Bengaluru. The site solves one problem: people cannot see the menu or order ahead. It serves coffee lovers and office staff nearby, who can see the menu with prices, check the opening hours, find the shop and pre-order a coffee for pickup. The success measure is 30 pre-orders per week.

**In scope**
- Menu with prices (R1)
- Pre-order form for pickup (R2)
- Map or address (R3)
- Opening hours (R4)
- One page only, holding all of the above (R5)
- Works on phones (R6)

**Out of scope**
- Online payment: No payment is asked for or taken (R7)
- Any page beyond the single page (R5)

## Pages

One page only. The Brew Lab site is a single page, so there are no other pages to move between (R5).

All four parts sit on that single page:
- **Menu with prices:** shows each item and what it costs, so visitors can see it before they visit (R1).
- **Pre-order form for pickup:** lets a visitor pre-order a coffee and collect it at the shop. The form does not ask for or take any online payment (R2, R7).
- **Map or address:** shows where Brew Lab is in Indiranagar, Bengaluru (R3).
- **Opening hours:** shows when Brew Lab is open (R4).

The page works on phones. A visitor on a phone can read the menu with prices, the opening hours and the address, and can fill in and send the pre-order form (R6).

## Components

The Brew Lab page is built from five components. Each has one responsibility and names the PRD requirements it covers.

- **C1** Menu display: shows each menu item with its price so visitors can see what things cost before they visit. Covers R1, R5, R6.
- **C2** Pre-order form: lets a visitor pre-order a coffee for pickup and collect it at the shop, and asks for no online payment. Covers R2, R5, R6, R7.
- **C3** Location and address: shows the shop's map or address so visitors can find Brew Lab in Indiranagar, Bengaluru. Covers R3, R5, R6.
- **C4** Opening hours: shows when Brew Lab is open so visitors can check before they come. Covers R4, R5, R6.
- **C5** Single-page layout: holds the menu, pre-order form, map or address and opening hours on one page and keeps them readable and usable on a phone. Covers R5, R6.

No payment is taken anywhere on the site (R7). There is no payment component, and the pre-order form does not ask for or take any online payment.

**Requirement coverage**
- R1: menu display
- R2: pre-order form
- R3: location and address
- R4: opening hours
- R5: single-page layout, with every other component placed on that one page
- R6: single-page layout, with the menu, hours, address and form each usable on a phone
- R7: pre-order form, with no payment component
