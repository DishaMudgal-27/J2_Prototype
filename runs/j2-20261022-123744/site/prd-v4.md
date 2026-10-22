# Brew Lab

## Problem

Brew Lab is a specialty coffee shop at 12, 100 Feet Road, Indiranagar, Bengaluru 560038. Customers of Brew Lab have no easy way to see the menu and prices. They also have no easy way to order ahead and collect the order at the shop.

The shop has no online page that shows its name and address. This document describes a one-page, mobile-friendly website that solves this by showing the name, address, menu and prices, and by taking pre-orders for pickup.

## Users

Brew Lab has two user groups. Customers use the page to see the shop and order ahead. The Shop team receives the orders by email.

### Customers

Customers are people who want to see the menu and pre-order for pickup. Customers can:

- View the shop name and address.
- Read the menu and prices.
- Fill in and submit the pre-order form.
- Collect the order at the shop.

### Shop team

The Shop team receives the pre-orders that customers submit. The Shop team can:

- Receive pre-orders at hello@brewlab.example.

## Goals

The goal of the Brew Lab page is to show the shop name, address and menu, and to take pre-orders for pickup. Each goal below can be checked by looking at the page.

- **G1**: Show the name Brew Lab and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text, with no embedded map.
- **G2**: Show the menu of seven items with their prices in rupees, exactly as given in the brief.
- **G3**: Take pre-orders for pickup through a form with the fields name, phone, items and pickup time, sent to hello@brewlab.example. Customers collect the order at the shop, and no online payment is taken.

All three goals apply on a phone as well as on a larger screen, because the page is mobile-friendly.

## Requirements

This section lists what the Brew Lab page must do. Each requirement can be checked by looking at the page.

1. **R1**: The page shows the name Brew Lab as text.
2. **R2**: The page shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text, so Customers can view the shop name and address.
3. **R3**: The page has no embedded map. The address is the only location information on the page.
4. **R4**: The menu lists exactly seven items: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140 and Banana bread slice 120.
5. **R5**: Every menu price is in rupees and matches the number given in R4, so Customers can read the menu and prices.
6. **R6**: The page has a pre-order form with the fields name, phone, items and pickup time, and no other fields.
7. **R7**: When a Customer submits the pre-order form, the order is sent to hello@brewlab.example, where the Shop team receives it.
8. **R8**: Customers collect the order at the shop.
9. **R9**: No online payment is taken. The page has no payment fields.
10. **R10**: The page works on phones. At 360px width there is no horizontal overflow, and the name, address, menu and form can all be read and used.
11. **R11**: The page does not show opening hours or a shop phone number.
12. **R12**: The page is one file of plain HTML, CSS and JavaScript with no build step, and it contains the same facts as the PRD, HLD and LLD with no contradictions.
