# Brew Lab

## Problem

Brew Lab is a small specialty coffee shop in Indiranagar, Bengaluru. At present, people cannot see the menu or order ahead. Coffee lovers and office staff nearby, the two groups this PRD serves, have no way to see the menu with prices or to pre-order a coffee for pickup. This PRD describes a one-page website that addresses this problem.

## Users

Brew Lab serves two user groups in Indiranagar, Bengaluru. Both groups are affected by the problem described above: they cannot see the menu or order ahead. Each group has the same three actions on the website.

- **Coffee lovers**: see the menu with prices; see opening hours and where to find the shop; pre-order a coffee for pickup. They pay at pickup, as there is no online payment.
- **Office staff nearby**: see the menu with prices; see opening hours and where to find the shop; pre-order a coffee for pickup. They pay at pickup, as there is no online payment.

## Goals

Brew Lab wants coffee lovers and office staff nearby to get what they need from one page. Each goal below is one outcome that a visitor can complete and that can be checked on the page.

- **G1**: Visitors can see the menu with prices in rupees.
- **G2**: Visitors can see the opening hours and where to find the shop in Indiranagar, Bengaluru.
- **G3**: Visitors can pre-order a coffee for pickup and pay at pickup.

## Requirements

Coffee lovers and Office staff nearby both use every requirement below. Each requirement serves at least one of the goals G1, G2 and G3 in the Goals section.

1. **R1**: The page shows the menu with all seven items and their prices in rupees, exactly as given: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140, Banana bread slice 120. This serves G1.
2. **R2**: Each menu item is displayed next to its own price, and all seven items are visible on the page without leaving it. This serves G1.
3. **R3**: The page has a pre-order form with the fields name, phone, items and pickup time, so that a visitor can pre-order a coffee for pickup. This serves G3.
4. **R4**: When a visitor submits the pre-order form, the order is emailed to hello@brewlab.example and contains the values entered in name, phone, items and pickup time. This serves G3.
5. **R5**: No online payment, they pay at pickup. The pre-order form has no payment fields, and the page tells visitors they pay at pickup. This serves G3.
6. **R6**: The page shows the opening hours exactly as given: Monday to Saturday 7:30 am to 9:00 pm, and Sunday 8:30 am to 6:00 pm. This serves G2.
7. **R7**: The page shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as the map or address, so that visitors can find the shop. This serves G2.
8. **R8**: The page shows the contact details: phone +91 98450 12345 and email hello@brewlab.example. This serves G2.
9. **R9**: The website is one page only. The menu, pre-order form, opening hours, address and contact details are all on that single page.
10. **R10**: The page works on phones: a visitor on a phone can view the menu, opening hours, address and contact details, and can fill in and submit the pre-order form.
11. **R11**: Coffee lovers and Office staff nearby can each see the menu with prices, see the opening hours and where to find the shop, and pre-order a coffee for pickup, with no difference in what either group sees or can do. This serves G1, G2 and G3.

## Success metrics

Each metric below names the goal it measures in the Goals section. The only numeric target is the one in the brief.

| Goal | Metric |
|------|--------|
| G1 | The menu with all seven items and their prices in rupees is visible on the page. |
| G2 | The opening hours (Monday to Saturday 7:30 am to 9:00 pm, Sunday 8:30 am to 6:00 pm) and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 are visible on the page. |
| G3 | 30 pre-orders per week, measured per week. |

- Assumption: a pre-order is counted each time the pre-order form sends an order to hello@brewlab.example.

## Assumptions to confirm

- a pre-order is counted each time the pre-order form sends an order to hello@brewlab.example.
