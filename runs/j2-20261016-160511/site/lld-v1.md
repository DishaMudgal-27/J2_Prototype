# Brew Lab

## Pages and sections

Brew Lab is one page only. Assumption: the single page file is named `index.html`.

- **S1** `#menu` (page index.html): the menu with each item and its price, so visitors see what things cost before they visit. Implements C1. Serves R1, R5, R6.
- **S2** `#pre-order` (page index.html): the pre-order form for pickup, with no online payment asked for or taken. Implements C2. Serves R2, R5, R6, R7.
- **S3** `#shop-address` (page index.html): the shop's map or address, so visitors can find Brew Lab in Indiranagar, Bengaluru. Implements C3. Serves R3, R5, R6.
- **S4** `#opening-hours` (page index.html): the opening hours, so visitors can check when Brew Lab is open before they come. Implements C4. Serves R4, R5, R6.
- **S5** `#page-layout` (page index.html): the wrapper that holds the menu, pre-order form, shop address and opening hours on the one page, readable and usable on a phone. Implements C5. Serves R5, R6.

Coverage: C1 is built by the menu section, C2 by the pre-order section, C3 by the shop address section, C4 by the opening hours section and C5 by the layout section. Every section id is unique and every component C1 to C5 is built by exactly one section.

## Assumptions to confirm

- the single page file is named index.html.
