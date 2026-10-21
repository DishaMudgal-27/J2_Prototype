# Brew Lab

## Pages and sections

Brew Lab is one page only. Assumption: the single page file is named `index.html`.

- **S1** `#menu` (page index.html): the menu with each item and its price, so visitors see what things cost before they visit. Implements C1. Serves R1, R5, R6.
- **S2** `#pre-order` (page index.html): the pre-order form for pickup, with no online payment asked for or taken. Implements C2. Serves R2, R5, R6, R7. Version 2: The LLD slice lists a quantity field, select, number and time field types and ids such as #pre-order-submit, #pre-order-fields and #pre-order-status. The charter and the Requester's answer say four fields (name, phone, items, pickup time) with no quantity, and the atom allows only the #po-* ids. I followed the charter. Mailto cannot confirm receipt, so there is no separate status element..
- **S3** `#shop-address` (page index.html): the shop's map or address, so visitors can find Brew Lab in Indiranagar, Bengaluru. Implements C3. Serves R3, R5, R6.
- **S4** `#opening-hours` (page index.html): the opening hours, so visitors can check when Brew Lab is open before they come. Implements C4. Serves R4, R5, R6.
- **S5** `#page-layout` (page index.html): the wrapper that holds the menu, pre-order form, shop address and opening hours on the one page, readable and usable on a phone. Implements C5. Serves R5, R6.

Coverage: C1 is built by the menu section, C2 by the pre-order section, C3 by the shop address section, C4 by the opening hours section and C5 by the layout section. Every section id is unique and every component C1 to C5 is built by exactly one section.

## Interactive elements

The Brew Lab page is one page only and works on phones. Every element below sits on `index.html` and belongs to a section from Pages and sections. No payment: no element asks for or takes any payment (R7).

Assumption: the selector names below are design choices, not facts from the brief.

- **E1** in S2: selector `#po-submit`; trigger submit; behaviour the Pre-order form for pickup is sent when every required field is filled in. If a required field is empty or invalid, the form is not sent and the problem is shown beside that field. No payment is asked for or taken.
- **E2** in S2: selector `#pre-order-form`; trigger change; behaviour that field is checked when the visitor leaves it, and its message is shown beside it. The fields and their rules are listed under Form fields.
- **E3** in S2: selector `#po-error`; trigger submit; behaviour a message shows that the pre-order for pickup was received, so the visitor knows it went through.
- **E4** in S5: selector `#page-nav`; trigger click; behaviour each link moves the visitor to `#menu` (S1), `#pre-order` (S2), `#shop-address` (S3) or `#opening-hours` (S4) on the same page.

Assumption: the message in E3 appears in the same section and the pre-order form stays on the page.

Assumption: the in-page links in E4 exist to keep the one page easy to move around on a phone.

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

## File structure

One page only. Brew Lab is a single page: the menu, pre-order form, shop address and opening hours all sit on it, with no second page (R5). Every section id below comes from Pages and sections, and every element id comes from Interactive elements and Form fields.

Assumption: the page is one file named `index.html`, written in plain HTML, CSS and JavaScript, with the styles and scripts kept inside that file and no build step.

Where each section sits in the page, top to bottom:
- `#page-layout` (S5, C5): the wrapper that holds every other section. It also holds the in-page links `#page-nav` (E4).
- `#menu` (S1, C1): the menu with each item and its price.
- `#pre-order` (S2, C2): the pre-order form for pickup. It holds `#pre-order-form` (fields F1 to F5, elements E1 and E2) and `#po-error` (E3). No payment field is placed here (R7).
- `#shop-address` (S3, C3): the map or address.
- `#opening-hours` (S4, C4): the opening hours.

Rules for the file:
- Each section id appears once, and each section sits inside `#page-layout`.
- The coffee choices in the form field `coffee-item` (F3) are taken from the items in `#menu`, so the menu is written once.
- The pre-order form points to no other page and asks for no payment.
- Assumption: the sections appear in the order listed above, so the in-page links in `#page-nav` follow the same order.
- Assumption: the styles sit in one block and the scripts in one block in the same file, so the page stays one file.

## Responsive and accessibility rules

Works on phones. Every section of the one page (S1 to S5 on `index.html`) must be readable and usable on a phone, so a visitor can read the menu with prices, the opening hours and the address, and can fill in and send the pre-order form (R6). No payment field appears anywhere on the page (R7).

Assumption: the page is checked at a phone width of 360px and a desktop width of 1280px, with no horizontal scrolling at either. These two widths come from the department's workable rules, not from the brief. No other breakpoint or size is set here.

Phone layout:
- `#page-layout` (S5) shows `#menu` (S1), `#pre-order` (S2), `#shop-address` (S3) and `#opening-hours` (S4) in one column on a phone, in the order set under File structure.
- No section is wider than the screen. Text wraps and nothing forces the visitor to scroll sideways.
- The page keeps one page only. No section moves to a second page on a phone.

Readable menu (S1, C1):
- Each menu item and its price are shown together, so a visitor sees what each item costs without searching.
- Menu text stays readable on a phone without zooming.

Address and opening hours (S3, S4):
- The address in `#shop-address` is plain text, so it can be read and copied on a phone. If a map is shown, it fits inside the screen width.
- The opening hours in `#opening-hours` are plain text and sit where a visitor can find them without extra taps.

Pre-order form (S2, E1, E2, E3, F1 to F5):
- Each field in the pre-order form sits on its own line and fills the width available on a phone.
- Every field F1 to F5 has a visible label placed with the field. A placeholder never replaces a label.
- Field types from Form fields are kept, so a phone offers a suitable input for each one: text for `customer-name`, tel for `customer-phone`, select for `coffee-item`, number for `quantity` and time for `pickup-time`.
- The submit control for E1 is easy to reach and tap on a phone, and sits after the last field.
- Validation messages from E2 appear next to the field they belong to, and are written in words. A problem is never shown by colour alone.
- The confirmation in `#po-error` (E3) is shown in the same section, so the visitor sees it without scrolling away from the form.
- Assumption: `#po-error` is marked so that screen readers announce the message when it appears.

In-page links (S5, E4):
- The links in `#page-nav` are big enough to tap on a phone and have clear text naming `#menu`, `#pre-order`, `#shop-address` and `#opening-hours`.

Keyboard use:
- Every control (the links in E4, every field F1 to F5 and the submit control in E1) can be reached and used from the keyboard alone.
- The order of controls follows the order on screen, from `#page-nav` down through S1, S2, S3 and S4.
- The control that has focus always shows a visible outline.
- The form can be sent from the keyboard, and a failed send moves the visitor to the first field with a problem.

Reading and structure:
- Each section S1 to S4 has a visible heading that names it, so the page can be understood by headings alone.
- Text and prices have enough contrast against the background to be read in daylight on a phone.
- Assumption: images, if any are added, carry a short text description. The brief lists no images.

## Assumptions to confirm

- the single page file is named index.html.
- the selector names below are design choices, not facts from the brief.
- the message in E3 appears in the same section and the pre-order form stays on the page.
- the in-page links in E4 exist to keep the one page easy to move around on a phone.
- the field names, types, required flags and validation rules below are design choices, not facts from the brief. The brief gives no field list.
- the shop needs a name to hand over the order at pickup.
- the shop needs a way to reach the visitor about the order.
- the visitor picks the time they will collect the order.
- no other fields are added, so the form asks only for what a pickup pre-order needs.
- the page is one file named index.html, written in plain HTML, CSS and JavaScript, with the styles and scripts kept inside that file and no build step.
- the sections appear in the order listed above, so the in-page links in #page-nav follow the same order.
- the styles sit in one block and the scripts in one block in the same file, so the page stays one file.
- the page is checked at a phone width of 360px and a desktop width of 1280px, with no horizontal scrolling at either. These two widths come from the department's workable rules, not from the brief. No other breakpoint or size is set here.
- #po-error is marked so that screen readers announce the message when it appears.
- images, if any are added, carry a short text description. The brief lists no images.
