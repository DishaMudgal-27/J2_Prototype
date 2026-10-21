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
- **C3** Shop address: shows the shop's map or address so visitors can find Brew Lab in Indiranagar, Bengaluru. Covers R3, R5, R6.
- **C4** Opening hours: shows when Brew Lab is open so visitors can check before they come. Covers R4, R5, R6.
- **C5** One-page layout: holds the menu, pre-order form, map or address and opening hours on one page and keeps them readable and usable on a phone. Covers R5, R6.

No payment is taken anywhere on the site (R7). There is no payment component, and the pre-order form does not ask for or take any online payment.

**Requirement coverage**
- R1: menu display
- R2: pre-order form
- R3: shop address
- R4: opening hours
- R5: one-page layout, with every other component placed on that one page
- R6: one-page layout, with the menu, hours, address and form each usable on a phone
- R7: pre-order form, with no payment component

## Data flow

No payment is asked for or taken anywhere on the Brew Lab page (R7). The pre-order form (C2) is the only form on the page.

**Viewing the page (information goes to the visitor)**
- The menu with prices (C1), the map or address (C3) and the opening hours (C4) are part of the single page (C5). They reach coffee lovers and office staff nearby when the page opens.
- The visitor sends nothing back while reading these parts (R1, R3, R4).

**Pre-ordering for pickup (information goes from the visitor to the shop)**
1. The visitor reads the menu (C1) and fills in the pre-order form (C2) for the coffee they want to collect at the shop (R2).
2. The visitor sends the form from their phone or computer (R6).
3. The pre-order reaches the shop, and the visitor collects the coffee at the shop.
4. The form carries no payment details, because it does not ask for or take any online payment (R7).

**Forms and integrations**
- Forms: one, the pre-order form (C2).
- Payment integration: none (R7).

Assumption: The pre-order form collects only what the shop needs to prepare a pickup order, such as the coffee chosen and a name for collection. The brief does not list the form fields.

Assumption: The way a sent pre-order reaches the shop (for example email or a form-handling service) is not set in the brief and is still to be chosen. The design only requires that the order reaches the shop.

Assumption: The address (C3) is shown as text on the page. If a map is embedded, it would be an external integration that loads the map for the visitor.

## Hosting and deployment

The Brew Lab site is one page only (R5). It is built as a single file of plain HTML, CSS and JavaScript, with no build step, so the file you write is the file that goes live. Works on phones: the same file serves phones and computers, so a visitor on a phone can read the menu with prices, the opening hours and the address, and can fill in and send the pre-order form (R6).

**Hosting**
- The site is a static page served as that one file. It has no server code of its own.
- All five components (C1 to C5) ship inside that file.
- No payment service is connected anywhere (R7).

**Deployment**
- To publish or update the site, replace the single file at its host. There are no build or release stages.

Assumption: The file is published on a static hosting service. The brief names no host, domain or price, so none is chosen here.

Assumption: A static file cannot receive a sent pre-order by itself, so the pre-order form (C2) needs a route to the shop, such as email or a form-handling service. This is the same open choice named in Data flow, and the hosting choice should be made together with it.

## Risks

The measure at risk is the target of 30 pre-orders per week. Each risk below is tied to a component and to the PRD requirement it threatens.

- **Pre-orders do not reach the shop.** If a sent pre-order is lost or unseen, a visitor arrives to find no order and the target of 30 pre-orders per week is missed. Affects C2 (R2). The route from form to shop is not yet set in the Data flow section, so it must be chosen together with hosting and checked end to end before launch.
- **Menu prices go out of date.** A visitor could order at a price the shop no longer charges. Affects C1 (R1). The site is one file, so the fix is to replace that file whenever prices change.
- **Opening hours go out of date.** A visitor could pre-order for a time the shop is closed. Affects C4 (R4). The same single-file update applies.
- **The page is hard to use on a phone.** If the menu is hard to read or the form is hard to fill in and send, phone visitors drop out and fewer orders arrive. Affects C2 and C5 (R2, R6). The page should be tested on a phone before it goes live.
- **Visitors cannot find the shop.** An address that is unclear, or a map that fails to load, leaves visitors unable to find the shop. Affects C3 (R3). The address should always appear as text, with any map as an addition.
- **Visitors expect to pay online.** Because no payment is taken, some visitors may be unsure whether an order is complete. Affects C2 (R7). The form should state clearly that it takes no online payment.

## Assumptions to confirm

- The pre-order form collects only what the shop needs to prepare a pickup order, such as the coffee chosen and a name for collection. The brief does not list the form fields.
- The way a sent pre-order reaches the shop (for example email or a form-handling service) is not set in the brief and is still to be chosen. The design only requires that the order reaches the shop.
- The address (C3) is shown as text on the page. If a map is embedded, it would be an external integration that loads the map for the visitor.
- The file is published on a static hosting service. The brief names no host, domain or price, so none is chosen here.
- A static file cannot receive a sent pre-order by itself, so the pre-order form (C2) needs a route to the shop, such as email or a form-handling service. This is the same open choice named in Data flow, and the hosting choice should be made together with it.
