# Brew Lab

## Problem

Brew Lab is a small specialty coffee shop in Indiranagar, Bengaluru. People cannot see the menu or order ahead.

Coffee lovers and office staff near the shop are the people affected. The one-page Brew Lab website described in the rest of the document shows the menu with prices, the opening hours and the shop location, and lets people pre-order a coffee for pickup.

## Users

The site is for two groups of people near Brew Lab in Indiranagar, Bengaluru: coffee lovers and office staff nearby.

### Coffee lovers

On the site, coffee lovers can:

- See the menu with prices.
- See opening hours and where the shop is.
- Pre-order a coffee for pickup.

### Office staff nearby

On the site, office staff nearby can:

- See the menu with prices.
- See opening hours and where the shop is.
- Pre-order a coffee for pickup.

Both groups use the same one-page site. Neither group pays online: there is no online payment, and customers pay at pickup.

## Goals

The one-page Brew Lab website has three goals. Together they solve the problem that people cannot see the menu or order ahead, for both coffee lovers and office staff nearby.

- **G1**: Show the menu with prices. The page lists all seven menu items, each with its price in rupees.
- **G2**: Show the opening hours and where the shop is. The page shows the opening hours for Monday to Saturday and for Sunday, and the shop address in Indiranagar, Bengaluru.
- **G3**: Let people pre-order a coffee for pickup. A visitor can send a pre-order from the page with their name, phone, items and pickup time, and pays at pickup because there is no online payment.

## Requirements

The Brew Lab page must meet the requirements below. Coffee lovers and Office staff nearby use the same requirements.

1. **R1**: The page shows a menu with all seven items and their prices in rupees: Filter coffee 90 rupees, Cappuccino 160 rupees, Latte 180 rupees, Cold brew 200 rupees, Masala chai 80 rupees, Almond croissant 140 rupees, Banana bread slice 120 rupees.
2. **R2**: Each menu item is shown with its own price next to its name, and the page shows no menu item or price other than the seven in R1.
3. **R3**: The page shows the opening hours for Monday to Saturday 7:30 am to 9:00 pm.
4. **R4**: The page shows the opening hours for Sunday 8:30 am to 6:00 pm.
5. **R5**: The page shows the shop address as 12, 100 Feet Road, Indiranagar, Bengaluru 560038.
6. **R6**: The page shows the shop phone number +91 98450 12345 so customers can call.
7. **R7**: The page shows the shop email address hello@brewlab.example.
8. **R8**: The page has a pre-order form where the customer enters name, phone, items and pickup time, and the form has a field for each of these four.
9. **R9**: When a customer submits the pre-order form, the order is emailed to hello@brewlab.example.
10. **R10**: The page states "No online payment, they pay at pickup" next to the pre-order form, and the form has no payment fields.
11. **R11**: The website is one page only: the menu, hours, address, contacts and pre-order form are all on that single page, with no second page.
12. **R12**: The page works on phones: the page has no sideways scrolling and every pre-order form field can be used at a 360 px wide screen.

Assumption: a phone screen is 360 px wide.

13. **R13**: The website takes no online payment: customers pay at pickup.
14. **R14**: Coffee lovers and Office staff nearby can both use the menu (R1, R2), the opening hours (R3, R4), the location (R5) and the pre-order form (R8, R9, R10) without any difference between the two groups.

## Success metrics

Each metric below names the goal it measures. The one number in this section, 30 pre-orders per week, is the target given by the Requester. The other two metrics are checked by reading the page.

| Goal | Metric |
|------|--------|
| G1 | The page lists all seven menu items, each with its price in rupees, as given in the Requirements section. |
| G2 | The page shows the opening hours (Monday to Saturday 7:30 am to 9:00 pm, Sunday 8:30 am to 6:00 pm) and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038. |
| G3 | Brew Lab receives 30 pre-orders per week through the pre-order form. |

- **G3**: The measurement window for the pre-order target is each week.

Assumption: Pre-orders are counted from the order emails received at hello@brewlab.example, because each submitted pre-order is emailed there.

## Out of scope

This version of the Brew Lab website does not include the following.

- **Online payment**: No online payment, they pay at pickup. The pre-order form has no payment fields, and the site takes no payment of any kind.
- **Additional pages**: The site is one page only. It has no second page, and the menu, opening hours, address, contacts and pre-order form all stay on that single page.

Anything not described in the Requirements section is not part of this version.

## Assumptions to confirm

- a phone screen is 360 px wide.
- Pre-orders are counted from the order emails received at hello@brewlab.example, because each submitted pre-order is emailed there.
