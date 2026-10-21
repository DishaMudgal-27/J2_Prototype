# Brew Lab

## Pages and sections

Brew Lab is one page only. Assumption: the single page file is named `index.html`.

- **S1** `#menu` (page index.html): the menu with each item and its price, so visitors see what things cost before they visit. Implements C1. Serves R1, R5, R6.
- **S2** `#pre-order` (page index.html): the pre-order form for pickup, with no online payment asked for or taken. Implements C2. Serves R2, R5, R6, R7.
- **S3** `#shop-address` (page index.html): the shop's map or address, so visitors can find Brew Lab in Indiranagar, Bengaluru. Implements C3. Serves R3, R5, R6.
- **S4** `#opening-hours` (page index.html): the opening hours, so visitors can check when Brew Lab is open before they come. Implements C4. Serves R4, R5, R6.
- **S5** `#page-layout` (page index.html): the wrapper that holds the menu, pre-order form, shop address and opening hours on the one page, readable and usable on a phone. Implements C5. Serves R5, R6.

Coverage: C1 is built by the menu section, C2 by the pre-order section, C3 by the shop address section, C4 by the opening hours section and C5 by the layout section. Every section id is unique and every component C1 to C5 is built by exactly one section.

## Interactive elements

The Brew Lab page is one page only and works on phones. Every element below sits on `index.html` and belongs to a section from Pages and sections. No element asks for or takes payment.

Assumption: the selector names below are design choices, not facts from the brief.

- **E1** in S2: `#pre-order-form` trigger submit; behaviour: the Pre-order form for pickup is sent when every required field is filled in. If a required field is empty or invalid, the form is not sent and the problem is shown next to that field. No payment is asked for or taken (R7).
- **E2** in S2: `#pre-order-form` fields, trigger change; behaviour: each field is checked as the visitor leaves it and shows its message beside the field. The fields and their rules are listed under Form fields.
- **E3** in S2: `#pre-order-status` trigger form sent; behaviour: shows a message that the pre-order for pickup was received, so the visitor knows it went through. Assumption: the message appears in the same section and the form stays on the page.
- **E4** in S5: `#page-nav` links trigger click; behaviour: each link moves the visitor to `#menu` (S1), `#pre-order` (S2), `#shop-address` (S3) or `#opening-hours` (S4) on the same page. Assumption: this in-page navigation exists to keep the one page easy to move around on a phone.

## Form fields

Brew Lab has one form, the pre-order form for pickup (`#pre-order-form` in S2, page index.html). No payment: the form has no card or other payment field and takes no online payment (R7). Every field below serves R2 and R6, so a visitor on a phone can fill in and send it.

Assumption: the field names, types, required flags and validation rules below are design choices, not facts from the brief. The brief gives no field list.

- **F1** in S2, form `#pre-order-form`: field `customer-name`, type text, required yes, validation: must not be empty. Assumption: the shop needs a name to hand over the order at pickup.
- **F2** in S2, form `#pre-order-form`: field `customer-phone`, type tel, required yes, validation: must not be empty and must contain digits only. Assumption: the shop needs a way to reach the visitor about the order.
- **F3** in S2, form `#pre-order-form`: field `coffee-item`, type select, required yes, validation: one option must be chosen, and the options match the items listed in `#menu` (S1).
- **F4** in S2, form `#pre-order-form`: field `quantity`, type number, required yes, validation: a whole number of one or more.
- **F5** in S2, form `#pre-order-form`: field `pickup-time`, type time, required yes, validation: must not be empty and must fall within the opening hours shown in `#opening-hours` (S4). Assumption: the visitor picks the time they will collect the order.

Rules for all fields:
- Each field has a visible label, and its validation message appears beside the field, as set out under Interactive elements.
- A form with any required field empty or invalid is not sent.
- Assumption: no other fields are added, so the form asks only for what a pickup pre-order needs.

## Assumptions to confirm

- the single page file is named index.html.
- the selector names below are design choices, not facts from the brief.
- the message appears in the same section and the form stays on the page.
- this in-page navigation exists to keep the one page easy to move around on a phone.
- the field names, types, required flags and validation rules below are design choices, not facts from the brief. The brief gives no field list.
- the shop needs a name to hand over the order at pickup.
- the shop needs a way to reach the visitor about the order.
- the visitor picks the time they will collect the order.
- no other fields are added, so the form asks only for what a pickup pre-order needs.
