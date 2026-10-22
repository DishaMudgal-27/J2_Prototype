# Brew Lab

## Pages and sections

Brew Lab has one page. It shows the shop name and address as text, the menu, a pre-order form, and a pickup and payment notice. It shows no opening hours, no shop phone number, no embedded map and no payment fields.

Assumption: the page file is named `index.html`, and the section ids below (for example `#shop-identity`) are chosen by this LLD because the brief does not name them.

- **S1** `#shop-identity` (page index.html): shows the name Brew Lab and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as plain text. The address is the only location information, and there is no embedded map. Implements C1 (Shop identity block).
- **S2** `#menu` (page index.html): lists exactly seven items with prices in rupees: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140 and Banana bread slice 120. Implements C2 (Menu list).
- **S3** `#pre-order` (page index.html): holds the pre-order form `#pre-order-form` with the fields name, phone, items and pickup time, and no other fields. On submit the order is sent to hello@brewlab.example, where the shop team receives it. The phone field belongs to the person ordering and is not a shop phone number. Implements C3 (Pre-order form) and C4 (Order delivery).
- **S4** `#pickup-payment-notice` (page index.html): tells the person ordering that the order is collected at the shop and that no online payment is taken. It contains no payment fields. Implements C5 (Pickup and payment notice).
- **S5** `#page` (page index.html): the wrapper around S1 to S4 inside the single file of plain HTML, CSS and JavaScript with no build step. It sets the layout so the page works on phones with no horizontal overflow at 360px width. It also holds no element for opening hours or a shop phone number, so the page shows neither. Implements C6 (Phone layout), C7 (page content check) and C8 (single package file).

## Assumptions to confirm

- the page file is named index.html, and the section ids below (for example #shop-identity) are chosen by this LLD because the brief does not name them.
