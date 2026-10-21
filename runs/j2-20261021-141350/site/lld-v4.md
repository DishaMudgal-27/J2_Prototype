# Brew Lab

## Pages and sections

Brew Lab has one page. It shows the shop name, the address as text, the menu with prices in rupees, the opening hours, the pre-order form and the pickup note. Each part below has its own id, and each component is built by exactly one part.

### Page sections

- **S1** `#shop-name` (page index.html): shows the shop name Brew Lab as text at the top of the page. Implements C1.
- **S2** `#address` (page index.html): shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text only, with no embedded map and no phone number for the shop. Implements C2.
- **S3** `#menu` (page index.html): shows the seven menu items, each next to its price in rupees, so a customer can see the cost without ordering: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140, Banana bread slice 120. Implements C3.
- **S4** `#opening-hours` (page index.html): shows the opening hours as 7 am to 10 pm, every day. Implements C4.
- **S5** `#pre-order` (page index.html): holds the pre-order form with the fields name, phone, items and pickup time, with no payment fields. The phone field is for the customer's own number only. When the customer submits the form, the order is sent to hello@brewlab.example. Implements C5, C6.
- **S6** `#pickup-note` (page index.html): states that customers collect the order at the shop and that no online payment is taken. Implements C7.
- **S7** `#page` (page index.html): the wrapper around S1 to S6. It is delivered as plain HTML, CSS and JavaScript in one file, and its layout fits a phone screen, so a customer, including office staff nearby, can read the menu, the opening hours and the address, and fill in and submit the pre-order form. Implements C8, C9.

### Components and the section that builds each

- **C1** Shop name: built by S1 `#shop-name`.
- **C2** Address block: built by S2 `#address`.
- **C3** Menu list: built by S3 `#menu`.
- **C4** Opening hours: built by S4 `#opening-hours`.
- **C5** Pre-order form: built by S5 `#pre-order`.
- **C6** Order sender: built by S5 `#pre-order`, which sends the order to hello@brewlab.example when the form is submitted.
- **C7** Pickup note: built by S6 `#pickup-note`.
- **C8** Phone layout: built by S7 `#page`.
- **C9** Plain HTML, CSS and JavaScript in one file: built by S7 `#page`.

Assumption: the page file name `index.html` and the section ids in this list are design choices made here. They are not in the brief.

Assumption: the order of S1 to S6 on the page follows the order of this list.

## Interactive elements

The page has two interactive elements, and both are in section S5 `#pre-order`. The shop name, address, menu, opening hours and pickup note are plain text and have nothing to click or submit.

- **E1** in S5: `#pre-order-submit` trigger click; behaviour submits the pre-order form `#pre-order-form`, which starts the form submission. The button takes no payment and has no payment step. Implements C5.
- **E2** in S5: `#pre-order-form` trigger submit; behaviour checks that the fields name, phone, items and pickup time are filled in, then sends the order to hello@brewlab.example with the values the customer typed. The phone value is the customer's own number only, and no shop phone number is shown or used. The order is collected at the shop, and no online payment is taken. Implements C5, C6.

Assumption: the form id `#pre-order-form` and the button id `#pre-order-submit` are design choices made here. They are not in the brief.

Assumption: if a required field is empty, the form is not sent and the empty field is pointed out to the customer.

Assumption: after the order is sent, the page tells the customer that the order was sent and will be collected at the shop.

Assumption: the order is sent from the page's own JavaScript, by opening the customer's email app with the order details addressed to hello@brewlab.example. The brief does not say how the order is sent.

## Form fields

The page has one form, the pre-order form `#pre-order-form` in S5 `#pre-order`. It collects four fields: name, phone, items and pickup time. It has no payment fields, because no online payment is taken and customers collect the order at the shop. The phone field is for the customer's own number only. No phone number for the shop is shown or collected anywhere on the form.

- **F1** in S5, form `#pre-order-form`: field `name`, type text, required yes, validation the field is not empty after leading and trailing spaces are removed.
- **F2** in S5, form `#pre-order-form`: field `phone`, type tel, required yes, validation the field is not empty and holds the customer's own phone number. It is not a shop phone number.
- **F3** in S5, form `#pre-order-form`: field `items`, type multi-line text, required yes, validation the field is not empty. The customer names what they want from the menu of seven items.
- **F4** in S5, form `#pre-order-form`: field `pickup time`, type time, required yes, validation a time is chosen.

Assumption: all four fields are required. The brief lists the four fields but does not say whether each is required. This matches the Interactive elements section, where an empty field stops the form from being sent.

Assumption: the field `name` is written `name`, `phone`, `items` and `pickup-time` in the HTML `name` attributes, and the inputs have the ids `#order-name`, `#order-phone`, `#order-items` and `#order-pickup-time`. These are design choices made here and are not in the brief.

Assumption: the phone field accepts digits, spaces, `+` and `-`, and the page does not check the number against any country format. The brief gives no phone format rule.

Assumption: the items field is a free-text box, not a list of choices. The brief does not say how items are picked.

Assumption: the pickup time input is limited to the opening hours, 7 am to 10 pm, so the customer can only choose a time when the shop is open. The brief does not say how pickup time is checked.

Assumption: each field has a visible label with the same wording as the field name, and a missing or wrong value is pointed out next to that field. The brief does not describe the error messages.

## Assumptions to confirm

- the page file name index.html and the section ids in this list are design choices made here. They are not in the brief.
- the order of S1 to S6 on the page follows the order of this list.
- the form id #pre-order-form and the button id #pre-order-submit are design choices made here. They are not in the brief.
- if a required field is empty, the form is not sent and the empty field is pointed out to the customer.
- after the order is sent, the page tells the customer that the order was sent and will be collected at the shop.
- the order is sent from the page's own JavaScript, by opening the customer's email app with the order details addressed to hello@brewlab.example. The brief does not say how the order is sent.
- all four fields are required. The brief lists the four fields but does not say whether each is required. This matches the Interactive elements section, where an empty field stops the form from being sent.
- the field name is written name, phone, items and pickup-time in the HTML name attributes, and the inputs have the ids #order-name, #order-phone, #order-items and #order-pickup-time. These are design choices made here and are not in the brief.
- the phone field accepts digits, spaces, + and -, and the page does not check the number against any country format. The brief gives no phone format rule.
- the items field is a free-text box, not a list of choices. The brief does not say how items are picked.
- the pickup time input is limited to the opening hours, 7 am to 10 pm, so the customer can only choose a time when the shop is open. The brief does not say how pickup time is checked.
- each field has a visible label with the same wording as the field name, and a missing or wrong value is pointed out next to that field. The brief does not describe the error messages.
