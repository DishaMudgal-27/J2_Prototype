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

## Components

The Brew Lab page is made of the components below. Each has one responsibility, and together they cover every requirement in the PRD, R1 to R13.

- **C1** Shop name: shows the shop name Brew Lab as text at the top of the page. Covers R1.
- **C2** Address block: shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text only, with no embedded map and no phone number for the shop. Covers R2, R3, R12.
- **C3** Menu list: shows the seven items, each next to its price in rupees, so a customer can see the cost without ordering: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140, Banana bread slice 120. Covers R4, R5.
- **C4** Opening hours: shows the hours as 7 am to 10 pm, every day. Covers R6.
- **C5** Pre-order form: collects the fields name, phone, items and pickup time. It has no payment fields, and the phone field is for the customer's own number only. Covers R7, R10, R12.
- **C6** Order sender: when the customer submits the pre-order form, sends the order to hello@brewlab.example. Covers R8.
- **C7** Pickup note: states that customers collect the order at the shop and that no online payment is taken. Covers R9, R10.
- **C8** Phone layout: makes the layout fit a phone screen, so a customer, including office staff nearby, can read the menu, the opening hours and the address, and fill in and submit the pre-order form. Covers R11.
- **C9** Plain HTML, CSS and JavaScript in one file: delivers the whole page as plain HTML, CSS and JavaScript in one file. Covers R13.

### Requirement traceability

Each PRD requirement and the component that covers it:

- **R1** The page shows the shop name Brew Lab as text: covered by the Shop name component.
- **R2** The page shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text: covered by the Address block.
- **R3** The page has no embedded map: covered by the Address block.
- **R4** The menu has seven items with prices in rupees (Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140, Banana bread slice 120): covered by the Menu list.
- **R5** Each menu item is shown next to its price: covered by the Menu list.
- **R6** The opening hours are 7 am to 10 pm, every day: covered by the Opening hours component.
- **R7** The pre-order form has the fields name, phone, items and pickup time: covered by the Pre-order form.
- **R8** A submitted order is sent to hello@brewlab.example: covered by the Order sender.
- **R9** The page states that customers collect the order at the shop: covered by the Pickup note.
- **R10** The page takes no online payment and the form has no payment fields: covered by the Pre-order form and the Pickup note.
- **R11** The page works on phones: covered by the Phone layout.
- **R12** The page shows no phone number for the shop, and the phone field is for the customer's own number only: covered by the Address block and the Pre-order form.
- **R13** The website is plain HTML, CSS and JavaScript in one file: covered by the Plain HTML, CSS and JavaScript in one file component (C9).

## Data flow

The page has one form and one integration. The form is the pre-order form (R7). The integration is the delivery of a submitted order to the email address hello@brewlab.example (R8). The page uses no map and no payment service (R3, R10).

**How an order moves:**
- The customer reads the menu and opens the pre-order form on a phone or any other screen (R11).
- The customer fills in four fields: name, phone, items and pickup time (R7). The phone field holds the customer's own number only (R12).
- The customer submits the form.
- The page sends the order, made up of those four fields, to hello@brewlab.example (R8).
- The customer collects the order at the shop at the pickup time given (R9).

**What is not sent or stored:**
- No payment data. The form has no payment fields and no online payment is taken (R10).
- No phone number for the shop. The page does not show one (R12).

Assumption: the page's JavaScript hands the order to a way of sending email to hello@brewlab.example. The brief names the destination but not the sending method, so the method is left to the build.

Assumption: the page keeps no copy of the order. The order exists only in the email that reaches hello@brewlab.example.

## Hosting and deployment

The Brew Lab website is one file of plain HTML, CSS and JavaScript (R13). It has no build step, so the file that is written is the file that ships. It is served as a static page: the visitor's phone or browser receives the file and runs it directly (R11).

**Where the site lives:** on a web host that serves static files. The page needs no server code of its own. Orders leave the page as an email to hello@brewlab.example (R8), and the page takes no online payment and embeds no map, so it depends on no payment service and no map service (R3, R10).

**How it ships:**
- The single file is placed on the host as the page that visitors open.
- Nothing else has to be installed, compiled or bundled before it goes live.
- To change the menu, the prices or the opening hours, the file is edited and put on the host again.

Assumption: the brief does not name a hosting provider or a web address, so the choice of a static host and the address of the site are left to the Requester.

Assumption: the page is published by copying the single file to the chosen host, and a change goes live when the new copy replaces the old one.

## Risks

Each risk below is tied to the PRD requirement it threatens and has a mitigation. The page is judged successful if it gets 20 pre-orders a week within the first month.

- **Orders do not reach hello@brewlab.example (R8).** If the order email is not delivered, the customer expects a drink that the shop never heard about, and the goal of ordering ahead fails. Mitigation: before the page goes live, submit a test order with all four fields (name, phone, items and pickup time) and confirm it arrives at hello@brewlab.example.
  - Assumption: someone at the shop reads the hello@brewlab.example inbox during opening hours (7 am to 10 pm, every day), so orders are seen before pickup time.

- **The form is hard to use on a phone (R7, R11).** Coffee lovers and office staff nearby place orders on a phone screen, so a form that is cramped or hard to fill in loses orders. Mitigation: keep the form to the four required fields, and check the menu, the opening hours, the address and the form on a phone-sized screen before the page goes live.

- **Too few pre-orders against the target.** The target is 20 pre-orders a week within the first month, and the page cannot meet it if customers do not find it or do not use the form. Mitigation: put the menu with prices, the opening hours, the address and the pre-order form on one page, so a visitor sees everything needed to order without leaving it.
  - Assumption: the number of pre-orders is counted from the order emails received at hello@brewlab.example, because the brief names no other way to count.

- **Customers expect online payment or a shop phone number (R10, R12).** Some customers may look for a way to pay on the page or a number to call, and the page offers neither. Mitigation: the page states that customers collect the order at the shop and that no online payment is taken (R9, R10), and the phone field is for the customer's own number only (R12).

- **The menu or prices become out of date (R4, R5).** The seven items and their prices are written into the single file, so a change in the shop is not shown until the file is edited. Mitigation: the menu, prices and opening hours are changed by editing the file and putting it on the host again, as described in Hosting and deployment.

- **The hosting provider and web address are not yet chosen.** Customers cannot use the page until it is live on a host. Mitigation: the single plain file (R13) can be placed on any host that serves static files, as described in Hosting and deployment.
  - Assumption: the host and the web address are to be chosen by the shop owner.

## Assumptions to confirm

- the page's JavaScript hands the order to a way of sending email to hello@brewlab.example. The brief names the destination but not the sending method, so the method is left to the build.
- the page keeps no copy of the order. The order exists only in the email that reaches hello@brewlab.example.
- the brief does not name a hosting provider or a web address, so the choice of a static host and the address of the site are left to the Requester.
- the page is published by copying the single file to the chosen host, and a change goes live when the new copy replaces the old one.
- someone at the shop reads the hello@brewlab.example inbox during opening hours (7 am to 10 pm, every day), so orders are seen before pickup time.
- the number of pre-orders is counted from the order emails received at hello@brewlab.example, because the brief names no other way to count.
- the host and the web address are to be chosen by the shop owner.
