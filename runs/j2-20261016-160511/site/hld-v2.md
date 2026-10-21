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
