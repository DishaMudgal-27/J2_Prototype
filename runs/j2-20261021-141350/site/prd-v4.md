# Brew Lab

## Problem

Brew Lab is a specialty coffee shop at 12, 100 Feet Road, Indiranagar, Bengaluru 560038. Today customers cannot see the menu or order ahead.

The people affected are coffee lovers and office staff near the shop in Indiranagar, Bengaluru. A customer who wants to know what the shop sells has no menu to look at. A customer who wants to collect an order at the shop has no way to place it before arriving.

This document describes a single-page website that solves this problem.

## Users

The page is for coffee lovers and office staff near the shop in Indiranagar, Bengaluru. Each group does the following on the page.

### Coffee lovers

- Look at the menu with prices.
- Check the opening hours.
- Find the address.
- Place a pre-order for pickup.

### Office staff nearby

- Place a quick pre-order on their phone.
- Pick the order up on the way to work.

## Goals

The page lets customers do four things. Each goal can be checked by reading the page.

- **G1**: Customers can see the menu with prices, all seven items shown with their rupee prices, so they know what the shop sells and what it costs before they come.
- **G2**: Customers can check the opening hours, 7 am to 10 pm, every day, so they know when the shop is open.
- **G3**: Customers can find the address, 12, 100 Feet Road, Indiranagar, Bengaluru 560038, shown as text.
- **G4**: Customers can pre-order for pickup at the shop by filling in the pre-order form, with no online payment.

## Requirements

The page is a single-page website for Brew Lab. Each requirement below can be checked by reading the page.

1. **R1**: The page shows the shop name Brew Lab as text.
2. **R2**: The page shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text, so coffee lovers can find the shop.
3. **R3**: The page does not contain an embedded map. The address is text only.
4. **R4**: The page shows a menu of seven items with prices in rupees, exactly as follows: Filter coffee 90 rupees, Cappuccino 160 rupees, Latte 180 rupees, Cold brew 200 rupees, Masala chai 80 rupees, Almond croissant 140 rupees, Banana bread slice 120 rupees.
5. **R5**: The menu shows each item next to its price, so a customer can see what each item costs without placing an order.
6. **R6**: The page shows the opening hours as 7 am to 10 pm, every day.
7. **R7**: The page has a pre-order form with these fields: name, phone, items and pickup time.
8. **R8**: When a customer submits the pre-order form, the order is sent to hello@brewlab.example.
9. **R9**: The page states that customers collect the order at the shop, so coffee lovers and office staff nearby know the order is picked up in person.
10. **R10**: The page takes no online payment. The pre-order form has no payment fields.
11. **R11**: The page works on phones. A customer, including office staff nearby, can read the menu, the opening hours and the address, and fill in and submit the pre-order form, on a phone screen.
12. **R12**: The page does not show a phone number for the shop. The form field called phone is for the customer's own number only.
13. **R13**: The website is plain HTML, CSS and JavaScript in one file.
