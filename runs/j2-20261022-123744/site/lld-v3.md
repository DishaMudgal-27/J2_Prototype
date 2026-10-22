# Brew Lab

## Pages and sections

Brew Lab has one page. It shows the shop name and address as text, the menu, a pre-order form, and a pickup and payment notice. It shows no opening hours, no shop phone number, no embedded map and no payment fields.

Assumption: the page file is named `index.html`, and the section ids below (for example `#shop-identity`) are chosen by this LLD because the brief does not name them.

### Page sections

- **S1** `#shop-identity` (page index.html): shows the name Brew Lab and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as plain text. The address is the only location information, and there is no embedded map. Implements C1.
- **S2** `#menu` (page index.html): lists exactly seven items with prices in rupees: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140 and Banana bread slice 120. Implements C2.
- **S3** `#pre-order` (page index.html): holds the pre-order form `#pre-order-form` with the fields name, phone, items and pickup time, and no other fields. On submit the order is sent to hello@brewlab.example, where the shop team receives it. The phone field belongs to the person ordering and is not a shop phone number. Implements C3, C4.
- **S4** `#pickup-payment-notice` (page index.html): tells the person ordering that the order is collected at the shop and that no online payment is taken. It contains no payment fields. Implements C5.
- **S5** `#page` (page index.html): the wrapper around S1 to S4 inside the single file of plain HTML, CSS and JavaScript with no build step. It sets the layout so the page works on phones with no horizontal overflow at 360px width. It holds no element for opening hours or a shop phone number, so the page shows neither. Implements C6, C7, C8.

### Components built by the sections

- **C1** Shop identity block: built by S1 (name Brew Lab and the address as text, no embedded map).
- **C2** Menu list: built by S2 (seven items with prices in rupees).
- **C3** Pre-order form: built by S3 (fields name, phone, items and pickup time, and no other fields).
- **C4** Order delivery: built by S3 (the submitted order goes to hello@brewlab.example).
- **C5** Pickup and payment notice: built by S4 (collect at the shop, no online payment, no payment fields).
- **C6** Phone layout: built by S5 (works on phones, no horizontal overflow at 360px width).
- **C7** page content check: built by S5 (no opening hours and no shop phone number on the page).
- **C8** single package file: built by S5 (one file of plain HTML, CSS and JavaScript, no build step).

## Interactive elements

The page has one interactive part, the pre-order form in S3. The menu (S2), the shop identity block (S1) and the pickup and payment notice (S4) are plain text and have no interactive elements. There is no payment control, no map, and nothing for opening hours or a shop phone number.

Assumption: the ids `#order-status` and `#pre-order-form` are chosen by this LLD because the brief does not name them. `#pre-order-form` is the form id already used in S3.

Assumption: with no server and no build step, submit hands the order to the visitor's email application as a message addressed to hello@brewlab.example, for example through a `mailto:` link built by the page's JavaScript. The brief says only that the form sends the order to hello@brewlab.example.

- **E1** in S3: `#pre-order-form` trigger submit, when every field is valid; behaviour the page builds one order message from the four fields (name, phone, items and pickup time) and sends it to hello@brewlab.example, where the shop team receives it (implements C3, C4). The message states that the order is collected at the shop. No payment is requested. After sending, `#order-status` shows a short confirmation that the order was sent for pickup at the shop.
- **E2** in S3: `#pre-order-form` trigger submit, when any field is empty or invalid under the rules in the Form fields section; behaviour the page does not send the order, shows a short message in `#order-status` naming each field to fix, and moves focus to the first invalid field (implements C3).

Assumption: `#order-status` is a text area that announces its message to screen readers. It is the only element that shows the result of E1 and E2.

## Assumptions to confirm

- the page file is named index.html, and the section ids below (for example #shop-identity) are chosen by this LLD because the brief does not name them.
- the ids #order-status and #pre-order-form are chosen by this LLD because the brief does not name them. #pre-order-form is the form id already used in S3.
- with no server and no build step, submit hands the order to the visitor's email application as a message addressed to hello@brewlab.example, for example through a mailto: link built by the page's JavaScript. The brief says only that the form sends the order to hello@brewlab.example.
- #order-status is a text area that announces its message to screen readers. It is the only element that shows the result of E1 and E2.
