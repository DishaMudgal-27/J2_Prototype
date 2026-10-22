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

Assumption: the id `#order-status` is chosen by this LLD because the brief does not name it. The pre-order form in S3 is defined once in S3, and this section refers to it by that name.

Assumption: with no server and no build step, submit hands the order to the visitor's email application as a message addressed to hello@brewlab.example, for example through a `mailto:` link built by the page's JavaScript. The brief says only that the form sends the order to hello@brewlab.example.

- **E1** in S3: the form in S3, trigger submit, when every field is valid; behaviour the page builds one order message from the four fields (name, phone, items and pickup time) and sends it to hello@brewlab.example, where the shop team receives it (implements C3, C4). The message states that the order is collected at the shop. No payment is requested. After sending, `#order-status` shows a short confirmation that the order was sent for pickup at the shop.
- **E2** in S3: the form in S3, trigger submit, when any field is empty or invalid under the rules in the Form fields section; behaviour the page does not send the order, shows a short message in `#order-status` naming each field to fix, and moves focus to the first invalid field (implements C3).

Assumption: `#order-status` is a text area that announces its message to screen readers. It is the only element that shows the result of E1 and E2.

## Form fields

The page has one form, the pre-order form in S3. It has exactly four fields: name, phone, items and pickup time. It has no other fields and no payment fields. The form sends the order to hello@brewlab.example, where the shop team receives it. The customer collects the order at the shop. This implements C3 and C4.

Assumption: the field ids `#order-name`, `#order-phone`, `#order-items` and `#order-pickup-time` are chosen by this LLD because the brief does not name them.

Assumption: the types, the required flags and the validation rules below are chosen by this LLD because the brief names only the four fields.

Assumption: the phone field needs at least 10 digits, chosen by this LLD.

- **F1** in S3, the pre-order form: field `name` (`#order-name`), type text, required yes, validation: not empty after trimming spaces. Label shown: "Name".
- **F2** in S3, the pre-order form: field `phone` (`#order-phone`), type tel, required yes, validation: not empty, only digits, spaces, `+` and `-`, and at least 10 digits. This is the phone number of the person ordering. It is not a shop phone number. Label shown: "Phone".
- **F3** in S3, the pre-order form: field `items` (`#order-items`), type multi-line text, required yes, validation: not empty after trimming spaces. The customer writes which menu items they want. Label shown: "Items".
- **F4** in S3, the pre-order form: field `pickup time` (`#order-pickup-time`), type time, required yes, validation: a time must be chosen. Label shown: "Pickup time".

### Form rules

- A field that fails its validation rule stops the send. The page shows a message naming the field in `#order-status` and moves focus to the first invalid field, as described in the Interactive elements section.
- When every field is valid, the order is sent to hello@brewlab.example.
- The form has no field for payment, card, or any other data, because no online payment is taken.
- The form has no field, label or hint that shows opening hours or a shop phone number.

## File structure

The Brew Lab page is delivered as one file of plain HTML, CSS and JavaScript. There is no build step, no second file and no separate stylesheet or script file. This implements C8 and matches R12 in the PRD.

Assumption: the file is named `index.html`, the same name used for the page in the Pages and sections section. The brief does not name the file.

### Parts of the file, in order

- **Part 1, document head.** It holds the page title (Brew Lab), the setting that lets the page scale to the width of a phone screen (supports C6), and the whole of the CSS in one style block.
- **Part 2, CSS.** It sits in the style block inside the head. It holds all the layout and text rules for S1 to S5. It includes the rules that keep the page free of horizontal overflow at 360px width (C6). It holds no rule that depends on a second file.
- **Part 3, HTML body.** The wrapper `#page` (S5) comes first and holds the other four sections in this order:
  1. `#shop-identity` (S1): the name Brew Lab and the address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 as text, with no embedded map.
  2. `#menu` (S2): the seven items with prices in rupees.
  3. `#pre-order` (S3): the form `#pre-order-form` with the four fields in F1 to F4, and the result text area `#order-status`.
  4. `#pickup-payment-notice` (S4): collect at the shop, no online payment.
- **Part 4, JavaScript.** It sits in one script block at the end of the body, after all the HTML above, so every element it uses already exists when it runs. It holds only the behaviour of E1 and E2 on `#pre-order-form`: checking the four fields, building the order message for hello@brewlab.example, and writing the result into `#order-status`.

### Rules for the file

- The file holds the same facts as the PRD, HLD and the other LLD sections, with no contradictions.
- The file has no opening hours and no shop phone number. The phone field in F2 is for the person ordering.
- The file has no embedded map and no payment field.
- The file needs no build tool and no install step. It opens as it is.
- Assumption: the file needs no outside library, so it makes no request to any CDN. The brief does not ask for one.
- Every id in the file is unique, and each id matches the one named in the other LLD sections.

## Responsive and accessibility rules

These rules apply to the single page `index.html` and to every section S1 to S5. They implement C6 (phone layout) and support C3 and C5. They trace to R10 in the PRD: the page works on phones, with no horizontal overflow at 360px width. They add no opening hours, no shop phone number, no embedded map and no payment field.

### Responsive rules

- **Rule 1, no overflow at 360px.** At a viewport width of 360px, the page must not scroll sideways. No element in `#page`, `#shop-identity`, `#menu`, `#pre-order`, the pre-order form in S3 or `#pickup-payment-notice` may be wider than the viewport.
- **Rule 2, viewport setting.** The document head sets the viewport so the page scales to the width of the phone screen, as described in the File structure section.
- **Rule 3, one column.** On a phone, sections S1 to S4 stack in one column inside `#page`, in the order: `#shop-identity`, `#menu`, `#pre-order`, `#pickup-payment-notice`.
- **Rule 4, flexible widths.** Widths use percentages or `max-width`, not fixed pixel widths wider than the screen. Images are not needed, and none may cause overflow.
- **Rule 5, long text wraps.** The address 12, 100 Feet Road, Indiranagar, Bengaluru 560038 and every menu item name wrap onto the next line when they are too long. They are never cut off and never push the page wider.
- **Rule 6, menu rows.** In `#menu`, each of the seven items shows its name and its price in rupees on the same row or stacked, and the price stays visible at 360px.
- **Rule 7, form fit.** The four fields in the pre-order form in S3 (`#order-name`, `#order-phone`, `#order-items`, `#order-pickup-time`) and the submit button fill the width of their container and stack one under another. The labels sit above their fields.
- **Rule 8, wider screens.** On a screen wider than a phone the layout may widen, but the content stays readable and inside the screen. The page still has no horizontal overflow.
- Assumption: the layout needs only one breakpoint, because the brief names only phones and gives no other screen size.
- Assumption: the page container has a maximum width of 720px on wide screens, chosen by this LLD for readability.

### Accessibility rules

- **Labels.** Every field in the pre-order form in S3 has a visible label linked to its field with the `for` and `id` pair. The labels are "Name", "Phone", "Items" and "Pickup time", matching F1 to F4 in the Form fields section. A placeholder never replaces a label.
- **Required fields.** Each field is marked required, in text and in the field itself, because all four fields are required in the Form fields section.
- **Field types.** The phone field uses the telephone type and the pickup time field uses the time type, so phones show a suitable keyboard or picker. The phone field is for the person ordering and is not a shop phone number.
- **Keyboard use.** Every interactive element, which is the four fields and the submit button in the pre-order form in S3, can be reached and used with the keyboard alone. The tab order follows the visual order: Name, Phone, Items, Pickup time, then submit. The submit button triggers E1 or E2 from the keyboard.
- **Visible focus.** The element that has keyboard focus always shows a clear focus outline. The CSS never removes the outline without a replacement.
- **Messages for screen readers.** `#order-status` announces its message to screen readers when E1 shows the confirmation or E2 shows the fields to fix. Each error message names the field it is about, in words, not by colour alone.
- **Focus after an error.** When E2 stops a send, focus moves to the first invalid field, as the Interactive elements section describes.
- **Page structure.** Each of S1 to S4 has a heading, and the shop name Brew Lab is the main page heading. Headings go in order and none is skipped. The menu items are marked up as a list.
- **Readable text.** Text is real text, never an image. The page text and its background have strong contrast. The page does not use colour alone to give meaning, including for prices and errors.
- **Text size.** Text sizes use relative units so the visitor can enlarge the text, and the page stays free of horizontal overflow at 360px when the text is enlarged.
- **Tap targets.** The submit button and the form fields are large enough to tap with a thumb, with space between them.
- **Notice text.** The pickup and payment notice is plain text in the page flow: order collected at the shop, no online payment taken. It is not hidden and not shown only on hover.
- **Page language.** The document sets its language so screen readers pronounce it correctly.
- Assumption: the page language is English, because the brief is written in English.
- Assumption: the body text is at least 16px and tap targets are at least 44px high, chosen by this LLD because the brief gives no sizes.
- Assumption: text contrast follows the WCAG AA level, chosen by this LLD because the brief names no accessibility standard.

### Checks for this section

- At 360px width the page has no horizontal overflow (R10, C6).
- All four form fields have a visible label and can be reached by keyboard.
- The status text area announces the result of E1 and E2.
- The page shows no opening hours, no shop phone number, no embedded map and no payment field (R3, R9, R11, C7).

## Assumptions to confirm

- the page file is named index.html, and the section ids below (for example #shop-identity) are chosen by this LLD because the brief does not name them.
- the id #order-status is chosen by this LLD because the brief does not name it. The pre-order form in S3 is defined once in S3, and this section refers to it by that name.
- with no server and no build step, submit hands the order to the visitor's email application as a message addressed to hello@brewlab.example, for example through a mailto: link built by the page's JavaScript. The brief says only that the form sends the order to hello@brewlab.example.
- #order-status is a text area that announces its message to screen readers. It is the only element that shows the result of E1 and E2.
- the field ids #order-name, #order-phone, #order-items and #order-pickup-time are chosen by this LLD because the brief does not name them.
- the types, the required flags and the validation rules below are chosen by this LLD because the brief names only the four fields.
- the phone field needs at least 10 digits, chosen by this LLD.
- the file is named index.html, the same name used for the page in the Pages and sections section. The brief does not name the file.
- the file needs no outside library, so it makes no request to any CDN. The brief does not ask for one.
- the layout needs only one breakpoint, because the brief names only phones and gives no other screen size.
- the page container has a maximum width of 720px on wide screens, chosen by this LLD for readability.
- the page language is English, because the brief is written in English.
- the body text is at least 16px and tap targets are at least 44px high, chosen by this LLD because the brief gives no sizes.
- text contrast follows the WCAG AA level, chosen by this LLD because the brief names no accessibility standard.
