# Brew Lab

## Purpose and scope

This high-level design describes the one-page website for Brew Lab, a small specialty coffee shop at 12, 100 Feet Road, Indiranagar, Bengaluru 560038. The page is for coffee lovers and office staff near the shop in Indiranagar, Bengaluru. Today these customers cannot see the menu or order ahead. The page fixes this by showing the menu with prices and letting customers pre-order for pickup at the shop.

**In scope** (each item is traced to the PRD):
- The shop name Brew Lab and the address shown as text (R1, R2).
- A menu of seven items with prices in rupees, each item shown next to its price (R4, R5).
- Opening hours of 7 am to 10 pm, every day (R6).
- A pre-order form with the fields name, phone, items and pickup time, which sends the order to hello@brewlab.example (R7, R8).
- A statement that customers collect the order at the shop (R9).
- A layout that works on phones (R11).
- A website built as plain HTML, CSS and JavaScript in one file (R13).

**Out of scope:**
- An embedded map. The address is text only (R3).
- Online payment. The pre-order form has no payment fields (R10).
- A phone number for the shop. The form field called phone is for the customer's own number only (R12).

**Success measure:** the page is working if it gets 20 pre-orders a week within the first month.

## Pages

Brew Lab has one page, built as a single file of plain HTML, CSS and JavaScript (R13). It is laid out so that coffee lovers and office staff nearby can read everything and place a pre-order on a phone screen (R11). A visitor sees these parts, from top to bottom:

- **Shop name and address:** the name Brew Lab and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038, both as plain text (R1, R2). There is no embedded map (R3).
- **Menu:** seven items, each shown next to its price in rupees, so a customer can see the cost without ordering (R4, R5):
  - Filter coffee 90
  - Cappuccino 160
  - Latte 180
  - Cold brew 200
  - Masala chai 80
  - Almond croissant 140
  - Banana bread slice 120
- **Opening hours:** 7 am to 10 pm, every day (R6).
- **Pre-order form:** the fields name, phone, items and pickup time (R7). Submitting it sends the order to hello@brewlab.example (R8). The phone field is for the customer's own number only, and the form has no payment fields (R10, R12).
- **Pickup note:** a statement that customers collect the order at the shop, and that no online payment is taken (R9, R10).

The page does not show a phone number for the shop (R12).
