# Brew Lab

## Pages and sections

Brew Lab has one page. It shows the shop name, the address as text, the menu with prices in rupees, the opening hours, the pre-order form and the pickup note. Each part below has its own id, and each component is built by exactly one part.

### Page sections

- **S1** `#shop-name` (page index.html): shows the shop name Brew Lab as text at the top of the page. Implements C1.
- **S2** `#address` (page index.html): shows the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text only, with no embedded map and no phone number for the shop. Implements C2.
- **S3** `#menu` (page index.html): shows the seven menu items, each next to its price in rupees, so a customer can see the cost without ordering: Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140, Banana bread slice 120. Implements C3.
- **S4** `#opening-hours` (page index.html): shows the opening hours as 7 am to 10 pm, every day. Implements C4.
- **S5** `#pre-order` (page index.html): holds the pre-order form with the fields name, phone, items and pickup time, with no payment fields. The phone field is for the customer's own number only. When the customer submits the form, the order is sent to hello@brewlab.example. Implements C5, C6. Version 2: The LLD names the form and button #pre-order-form and #pre-order-submit, but this workflow's constraints and checks require #order-form and #order-submit, and one element cannot carry both ids. I built the workflow's ids and kept the specified behaviour and fields..
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

- **E1** in S5: `#order-submit` trigger click; behaviour submits the pre-order form `#order-form`, which starts the form submission. The button takes no payment and has no payment step. Implements C5.
- **E2** in S5: `#order-form` trigger submit; behaviour checks that the fields name, phone, items and pickup time are filled in, then sends the order to hello@brewlab.example with the values the customer typed. The phone value is the customer's own number only, and no shop phone number is shown or used. The order is collected at the shop, and no online payment is taken. Implements C5, C6.

Assumption: the form id `#order-form` and the button id `#order-submit` are design choices made here. They are not in the brief.

Assumption: if a required field is empty, the form is not sent and the empty field is pointed out to the customer.

Assumption: after the order is sent, the page tells the customer that the order was sent and will be collected at the shop.

Assumption: the order is sent from the page's own JavaScript, by opening the customer's email app with the order details addressed to hello@brewlab.example. The brief does not say how the order is sent.

## Form fields

The page has one form, the pre-order form `#order-form` in S5 `#pre-order`. It collects four fields: name, phone, items and pickup time. It has no payment fields, because no online payment is taken and customers collect the order at the shop. The phone field is for the customer's own number only. No phone number for the shop is shown or collected anywhere on the form.

- **F1** in S5, form `#order-form`: field `name`, type text, required yes, validation the field is not empty after leading and trailing spaces are removed.
- **F2** in S5, form `#order-form`: field `phone`, type tel, required yes, validation the field is not empty and holds the customer's own phone number. It is not a shop phone number.
- **F3** in S5, form `#order-form`: field `items`, type multi-line text, required yes, validation the field is not empty. The customer names what they want from the menu of seven items.
- **F4** in S5, form `#order-form`: field `pickup time`, type time, required yes, validation a time is chosen.

Assumption: all four fields are required. The brief lists the four fields but does not say whether each is required. This matches the Interactive elements section, where an empty field stops the form from being sent.

Assumption: the field `name` is written `name`, `phone`, `items` and `pickup-time` in the HTML `name` attributes, and the inputs have the ids `#order-name`, `#order-phone`, `#order-items` and `#order-pickup-time`. These are design choices made here and are not in the brief.

Assumption: the phone field accepts digits, spaces, `+` and `-`, and the page does not check the number against any country format. The brief gives no phone format rule.

Assumption: the items field is a free-text box, not a list of choices. The brief does not say how items are picked.

Assumption: the pickup time input is limited to the opening hours, 7 am to 10 pm, so the customer can only choose a time when the shop is open. The brief does not say how pickup time is checked.

Assumption: each field has a visible label with the same wording as the field name, and a missing or wrong value is pointed out next to that field. The brief does not describe the error messages.

## File structure

Plain HTML, CSS and JavaScript in one file. The whole Brew Lab page is delivered as that single file. There is no build step, and no second file is needed to show the page.

### The file

- **File** `index.html`: the only file of the website. It holds the HTML, the CSS and the JavaScript. Implements C9.
- The file has three parts, in this order: the HTML part, the CSS part and the JavaScript part.

### HTML part

- The HTML part holds the page text and the pre-order form.
- The wrapper `#page` (S7) comes first and contains S1 to S6 in this order:
  1. S1 `#shop-name`: the shop name Brew Lab. Implements C1.
  2. S2 `#address`: the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text only, with no embedded map and no shop phone number. Implements C2.
  3. S3 `#menu`: the seven menu items, each next to its price in rupees. Implements C3.
  4. S4 `#opening-hours`: 7 am to 10 pm, every day. Implements C4.
  5. S5 `#pre-order`: the form `#order-form` with the fields name, phone, items and pickup time, and the button `#order-submit`. Implements C5, C6.
  6. S6 `#pickup-note`: customers collect the order at the shop, and no online payment is taken. Implements C7.
- S7 `#page` carries the phone layout through the CSS part. Implements C8, C9.

### CSS part

- The CSS part sits in one style block inside `index.html`, before the page text.
- It holds all the styling for S1 to S7, including the rules that make the layout fit a phone screen. Implements C8.
- It does not load any separate CSS file.

### JavaScript part

- The JavaScript part sits in one script block inside `index.html`, after the page text.
- It holds the behaviour of E1 `#order-submit` and E2 `#order-form` in S5: checking the four fields and sending the order to hello@brewlab.example. Implements C5, C6.
- It does not load any separate JavaScript file.

### Rules for the file

- Everything the page needs is inside `index.html`: no build step, and no other file for the page.
- Every id in the file is unique, and the ids match the ones used in Pages and sections, Interactive elements and Form fields.
- The file contains no embedded map, no payment fields and no phone number for the shop.

Assumption: the file is named `index.html`, as in the Pages and sections section. The brief does not give a file name.

Assumption: the CSS part comes before the page text and the JavaScript part comes after it. The brief does not set the order of the parts.

Assumption: the page uses no outside libraries. The brief does not ask for any.

## Responsive and accessibility rules

Works on phones. The page is used by coffee lovers and office staff nearby, so a customer can read the menu, the opening hours and the address, and fill in and submit the pre-order form, on a phone screen. These rules are built in the CSS part of `index.html` through the wrapper `#page` (S7). They implement C8 and C9, and they apply to S1 to S6 and the form fields F1 to F4.

### Responsive rules

- **Width limits:** the page has no horizontal overflow at 360px and at 1280px. Nothing in `#page` is wider than the screen, and the customer never has to scroll sideways to read or fill in anything.
- **One column on phones:** on a phone screen, S1 `#shop-name`, S2 `#address`, S3 `#menu`, S4 `#opening-hours`, S5 `#pre-order` and S6 `#pickup-note` are stacked in one column, in the same order as in Pages and sections.
- **Fluid sizes:** widths of `#page` and its parts follow the screen width and are not fixed in pixels. Long text, such as the address in `#address`, wraps onto the next line instead of running past the screen edge.
- **Menu on a phone:** in `#menu`, each of the seven items stays on the same row as its price in rupees, so a customer can see what each item costs without ordering. If a name is long, such as Banana bread slice, the name wraps and the price stays beside it.
- **Opening hours and address on a phone:** `#opening-hours` (7 am to 10 pm, every day) and `#address` (12, 100 Feet Road, Indiranagar, Bengaluru 560038) are plain text in the normal flow of the page. They are not hidden behind a click and not shown in an image.
- **Form on a phone:** in `#order-form`, the fields `#order-name`, `#order-phone`, `#order-items` and `#order-pickup-time` and the button `#order-submit` each take the full width of `#page`, one under the other. Each label sits above its field.
- **No shop phone number and no map:** the phone layout adds no phone number for the shop and no embedded map. The address stays text only.
- **Plain HTML, CSS and JavaScript in one file:** the responsive rules are written in the style block of `index.html`. No separate CSS file is loaded.

### Accessibility rules

- **Labels:** every form field F1 to F4 has a visible label with the same wording as the field name. Each label is tied to its field, so a screen reader reads the label when the field is reached.
- **Field help:** `#order-phone` says that it is for the customer's own number. A missing or wrong value is pointed out in text next to that field, not by colour alone.
- **Keyboard access:** every interactive element, that is `#order-form` and `#order-submit`, can be reached and used with the keyboard alone. The order of the keyboard focus follows the order of the fields on the page, and the focused field or button is clearly visible.
- **Headings and structure:** each of S1 to S6 has a clear heading or text label, in the page order, so assistive tools can move from one part to the next. The menu items are written as a list, with the price next to each item.
- **Readable text and contrast:** text and its background have strong contrast, and the menu, prices, opening hours, address and pickup note are in text a customer can read on a small screen without zooming.
- **Messages:** the message that the order was sent and will be collected at the shop is shown as text on the page, so it can be read by assistive tools.
- **No payment fields:** the form has no payment fields, so there is nothing to enter other than name, phone, items and pickup time.

Assumption: on a phone screen, the touch targets of `#order-submit` and the form fields are large enough to tap with a thumb. The brief gives no size.

Assumption: the layout changes from one column to a wider layout only when the screen is wider than a phone, and the exact width where it changes is chosen when the page is built. The brief gives no breakpoint.

Assumption: the field help and error text next to a field is linked to that field so assistive tools read it. The brief does not describe error messages.

Assumption: the page language is set to English for assistive tools. The brief does not state a language.

## Assumptions to confirm

- the page file name index.html and the section ids in this list are design choices made here. They are not in the brief.
- the order of S1 to S6 on the page follows the order of this list.
- the form id #order-form and the button id #order-submit are design choices made here. They are not in the brief.
- if a required field is empty, the form is not sent and the empty field is pointed out to the customer.
- after the order is sent, the page tells the customer that the order was sent and will be collected at the shop.
- the order is sent from the page's own JavaScript, by opening the customer's email app with the order details addressed to hello@brewlab.example. The brief does not say how the order is sent.
- all four fields are required. The brief lists the four fields but does not say whether each is required. This matches the Interactive elements section, where an empty field stops the form from being sent.
- the field name is written name, phone, items and pickup-time in the HTML name attributes, and the inputs have the ids #order-name, #order-phone, #order-items and #order-pickup-time. These are design choices made here and are not in the brief.
- the phone field accepts digits, spaces, + and -, and the page does not check the number against any country format. The brief gives no phone format rule.
- the items field is a free-text box, not a list of choices. The brief does not say how items are picked.
- the pickup time input is limited to the opening hours, 7 am to 10 pm, so the customer can only choose a time when the shop is open. The brief does not say how pickup time is checked.
- each field has a visible label with the same wording as the field name, and a missing or wrong value is pointed out next to that field. The brief does not describe the error messages.
- the file is named index.html, as in the Pages and sections section. The brief does not give a file name.
- the CSS part comes before the page text and the JavaScript part comes after it. The brief does not set the order of the parts.
- the page uses no outside libraries. The brief does not ask for any.
- on a phone screen, the touch targets of #order-submit and the form fields are large enough to tap with a thumb. The brief gives no size.
- the layout changes from one column to a wider layout only when the screen is wider than a phone, and the exact width where it changes is chosen when the page is built. The brief gives no breakpoint.
- the field help and error text next to a field is linked to that field so assistive tools read it. The brief does not describe error messages.
- the page language is set to English for assistive tools. The brief does not state a language.
