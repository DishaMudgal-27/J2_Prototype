# Brew Lab

## Pages and sections

Brew Lab has one page. It shows the shop name, the address as text, the menu with prices in rupees, the opening hours, the pre-order form and the pickup note. Each part below has its own id, and each component is built by exactly one part.

- **S1** `#shop-name` (page index.html): shows the shop name Brew Lab as text at the top of the page. Implements C1.
- **S2** `#address` (page index.html): shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text only, with no embedded map and no phone number for the shop. Implements C2.
- **S3** `#menu` (page index.html): shows the seven menu items, each next to its price in rupees, so a customer can see the cost without ordering: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140, Banana bread slice 120. Implements C3.
- **S4** `#opening-hours` (page index.html): shows the opening hours as 7 am to 10 pm, every day. Implements C4.
- **S5** `#pre-order` (page index.html): holds the pre-order form with the fields name, phone, items and pickup time, with no payment fields. The phone field is for the customer's own number only. When the customer submits the form, the order is sent to hello@brewlab.example. Implements C5, C6.
- **S6** `#pickup-note` (page index.html): states that customers collect the order at the shop and that no online payment is taken. Implements C7.
- **S7** `#page` (page index.html): the wrapper around S1 to S6. It is delivered as plain HTML, CSS and JavaScript in one file, and its layout fits a phone screen, so a customer, including office staff nearby, can read the menu, the opening hours and the address, and fill in and submit the pre-order form. Implements C8, C9.

Assumption: the page file name `index.html` and the section ids in this list are design choices made here. They are not in the brief.

Assumption: the order of S1 to S6 on the page follows the order of this list.

## Assumptions to confirm

- the page file name index.html and the section ids in this list are design choices made here. They are not in the brief.
- the order of S1 to S6 on the page follows the order of this list.
