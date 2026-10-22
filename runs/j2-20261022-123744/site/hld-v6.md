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

## Components

The Brew Lab page is made of eight components. Each has one responsibility and names the PRD requirements it covers, so every requirement R1 to R12 traces to a component.

- **C1** Shop identity block: shows the name Brew Lab and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text, with no embedded map, so the address is the only location information. Covers R1, R2, R3.
- **C2** Menu list: shows exactly seven items with prices in rupees: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140 and Banana bread slice 120. Covers R4, R5.
- **C3** Pre-order form: collects the fields name, phone, items and pickup time, and no other fields. Covers R6.
- **C4** Order delivery: sends the submitted pre-order to hello@brewlab.example, where the Shop team receives it. Covers R7.
- **C5** Pickup and payment notice: tells the person ordering that the order is collected at the shop and that no online payment is taken, so the page has no payment fields. Covers R8, R9.
- **C6** Phone layout: arranges the page so it works on phones, with no horizontal overflow at 360px width. Covers R10.
- **C7** Content guard: keeps opening hours and a shop phone number off the page. The phone field in C3 belongs to the person ordering and is not a shop phone number. Covers R11.
- **C8** Single-file package: delivers the page as one file of plain HTML, CSS and JavaScript with no build step, with the same facts as the PRD, HLD and LLD. Covers R12.

### Requirement traceability

Each PRD requirement below is covered by the component named after it.

- **R1** Name Brew Lab shown as text: covered by the shop identity block.
- **R2** Address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 shown as text: covered by the shop identity block.
- **R3** No embedded map, address is the only location information: covered by the shop identity block.
- **R4** Exactly seven menu items with their prices: covered by the menu list.
- **R5** Every menu price in rupees and matching R4: covered by the menu list.
- **R6** Pre-order form with name, phone, items and pickup time only: covered by the pre-order form.
- **R7** Submitted order sent to hello@brewlab.example for the Shop team: covered by order delivery.
- **R8** Customers collect the order at the shop: covered by the pickup and payment notice.
- **R9** No online payment and no payment fields: covered by the pickup and payment notice.
- **R10** Works on phones with no horizontal overflow at 360px width: covered by the phone layout.
- **R11** No opening hours and no shop phone number: covered by the content guard.
- **R12** One file of plain HTML, CSS and JavaScript, no build step, same facts in every document: covered by the single-file package.

## Data flow

This section follows a pre-order from the customer to the Shop team. The page has one form and one destination for the order, hello@brewlab.example. It has no other integration, no map, no payment service and no database.

**Forms**
- The pre-order form (component C3, covers R6) is the only form on the page. Its fields are name, phone, items and pickup time, and no other fields.
- The phone field holds the phone number of the person ordering. It is not a shop phone number, and the page shows no shop phone number (R11).

**Integrations**
- Order delivery (component C4, covers R7) sends the submitted order to hello@brewlab.example, where the Shop team receives it.
- There are no other integrations. The page has no embedded map (R3) and takes no online payment (R9).

**Flow of a pre-order**
1. The customer reads the menu, where the seven items show their prices in rupees (R4, R5).
2. The customer fills in the form fields name, phone, items and pickup time.
3. The customer submits the form.
4. The order, with those four fields, is sent to hello@brewlab.example (R7).
5. The Shop team receives the order at hello@brewlab.example.
6. The customer collects the order at the shop (R8). The page takes no online payment and holds no payment fields, so no payment data moves anywhere (R9).

**Data carried**

| Data | Where it comes from | Where it goes |
| --- | --- | --- |
| name | Customer, in the form | hello@brewlab.example |
| phone | Customer, in the form | hello@brewlab.example |
| items | Customer, in the form | hello@brewlab.example |
| pickup time | Customer, in the form | hello@brewlab.example |

**Not in the flow**
- Payment details: none are collected, because no online payment is taken.
- Opening hours and a shop phone number: none are shown (R11).
- The menu and the address are fixed text on the page. They are not sent anywhere.

Assumption: the form is submitted from the customer's own device, and the page does not send the order anywhere other than hello@brewlab.example.

## Hosting and deployment

The Brew Lab page ships as one file of plain HTML, CSS and JavaScript with no build step (PRD R12, component C8). The file is the whole website, so there is nothing to compile, bundle or install before it goes live.

**What is deployed**
- One file holding the HTML, the CSS and the JavaScript of the Brew Lab page.
- The file holds the shop name Brew Lab, the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text, the menu of seven items with prices in rupees, and the pre-order form with the fields name, phone, items and pickup time.
- The file has no embedded map, no payment fields, no opening hours and no shop phone number.

**Where it lives**
- The brief and the PRD do not name a hosting provider, a domain or a cost, so this document names none and states no cost.
- The page is a fixed file, so any place that can serve one file to a browser can hold it. The page needs no server code of its own.

**How it ships**
1. The file is written as one file, with no build step.
2. The file is checked against the PRD: the same facts as the PRD, HLD and LLD, no contradictions (R12), the seven menu items and rupee prices (R4, R5), the form fields (R6) and no horizontal overflow at 360px width (R10).
3. The checked file is put in its place as it is. No other step changes it.
4. A change to the page is a change to this one file, which is checked again the same way before it replaces the earlier file.

**What the deployment depends on**
- The pre-order form sends the order to hello@brewlab.example, where the Shop team receives it (R7). This is the only destination for orders, and the deployment adds no database and no payment service.

Assumption: the file is served as a static file, so no server of Brew Lab's own is run.
Assumption: the LLD gives the detail of how the form delivers the order to hello@brewlab.example.

## Assumptions to confirm

- the parts appear on the page in the order shown above (name and address, menu, pre-order form).
- the form is submitted from the customer's own device, and the page does not send the order anywhere other than hello@brewlab.example.
- the file is served as a static file, so no server of Brew Lab's own is run.
- the LLD gives the detail of how the form delivers the order to hello@brewlab.example.
