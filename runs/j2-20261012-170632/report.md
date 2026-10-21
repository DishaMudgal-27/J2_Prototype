# J2 run report: 20261012-170632

Brief: make a website for our college tech fest called Spark 2026 at Northfield College of Engineering in Pune. students should be able to see the schedule day by day, browse events by category, register for an event with a form, see the sponsors, find the venue, and contact the organisers on whatsapp. it should feel energetic and modern and work well on phones

**Outcome:** Done with open items: shipped as is as the only option left (Out of budget: 2 of 80 units left, less than the cheapest rate-card part, and the site isn't workable yet.). Still not workable: design rubric R-6 (NEEDS_REVISION): Tap targets are big enough on phones (at least 44x44px).
**Reviewer verdict:** The process ran cleanly (0 redirects, 0 invalid moves, 8 of 8 workflows done) but the site shipped without sponsors, a named brief item, and with a failing 44px tap target, because the 40-credit start and 80 cap ran out.

## Measured (counted by code)
- 37 AI calls, 2 cycles, 11.2 min, model sonnet
- Budget 78/80 (started 40, 1 raise(s) approved by the Requester, cap 80; rate card on), 8 site versions, final site 37 KB
- Negotiation: 3 proposals, 1 GRANT / 2 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 2: 2 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 3 {'limit': 2, 'info': 1}
- Validator refusals 1 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 8 | 0 | 0 | 3 | Charter kept every supplied fact and invented none, and the limit questions gave the Requester concrete options [32][58]. But [67] tells Adaptation how to reshape the fees proposal and tells Priority what to fund first, which the role forbids. [63] misstates what the Requester dropped (says items 4 and 6, actual 6 and 10) and says item 10 stays, against [61]. |
| Adaptation | 5 | 0 | 0 | 3 | Accepted both counters, stated its trade-off each time, and settled in 2 attempts [10][70]. But in [38] it trimmed its own proposal to exactly 40, dropping sponsors and the R-6 fix Identity had asked for in [37], so Priority had nothing to weigh. Fees was first planned as a separate workflow after the schedule [8] and mistyped as a page_section [40]. |
| Priority | 11 | 0 | 0 | 3 | Envelope checks were correct and the arithmetic held (shortfall 6 credits [69]). It repeatedly dictated workflow steps ([9] nav links, [39] and [69] 'do not touch the nav'), which is a named failure pattern. It also claimed nothing was bundled in [39] when fees rewrites W-2. |
| Coordination | 8 | 0 | 0 | 4 | Stated its scheduling rule every time [13][17][43], kept one writer under the lock, caused no collisions. Evidence is thin: runs were strictly sequential and held_ever is 0, so HOLD and collision handling were never tested. |
| Audit | 4 | 0 | 0 | 4 | Findings match the code tally and the mechanical checks, and it did not rewrite work. It re-audited an unchanged v7 with identical results [66]. It lists extra issues (F-11, F-9) without saying what they are [57][78], so F-9 NEEDS_REVISION on the shipped v8 was never explained to the Requester. |
| W-1 Builder | 1 | 0 | 0 | 4 | Hero with name, college, dates and placeholder; passed code checks on attempt 1 [15][16]. |
| W-2 Builder | 1 | 0 | 0 | 4 | Schedule correct, no room or hall invented [20]. |
| W-3 Builder | 1 | 0 | 0 | 4 | Form has all fields and an 8-option dropdown, and it said honestly that submit opens an email [24]. Whether the warning on item 5 relates to the mailto is unknown, its text is not in the evidence. |
| W-4 Builder | 1 | 0 | 0 | 3 | Nav brand link was 101x28px at 360px from v4 on [30] and never fixed. Its report only says 'checks are run by code' [28] and does not say whether its completion check holds. |
| W-5 Builder | 1 | 0 | 0 | 4 | Four categories, 8 event cards, scope held [46]. No fees on the cards, as scoped. |
| W-6 Builder | 1 | 0 | 0 | 4 | Address and map link as supplied, nav untouched [50]. |
| W-7 Builder | 1 | 0 | 0 | 4 | wa.me link matches +91 00000 33333 and the email is shown [54]. |
| W-8 Builder | 1 | 0 | 0 | 4 | Added all 8 fee tags inside #schedule only, times and nav unchanged [75]. |

## Conflicts (full log in conflicts.json)
- C-1 (cycle 1, proposal): Adaptation vs Priority, 2 attempt(s), resolved by agents. Outcome: Adaptation accepted Priority's COUNTER: Hero and event identity (10), Day by day schedule (10), Registration form (15), Base styling and page health (5) goes to the validator.
- C-2 (cycle 2, proposal): Adaptation vs Priority, 2 attempt(s), resolved by agents. Outcome: Adaptation accepted Priority's COUNTER: Event fees on schedule (8) goes to the validator.

## Audit by cycle
- Cycle 1, v4: 3 pass, 1 warn, 6 fail; mechanical: clean
- Cycle 1, v7: 6 pass, 1 warn, 3 fail; mechanical: clean
- Cycle 1, v7: 6 pass, 1 warn, 1 fail; mechanical: clean
- Cycle 2, v8: 6 pass, 2 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- No facts were invented: no room or hall, no extra prices or contacts [20][46].
- Every workflow passed its code checks on attempt 1, with no failures or retries.
- Mechanical gates were clean from v4 on: no overflow at 360 or 1280px, no JS errors, no broken links [30][56][77].
- Both Adaptation/Priority bargains settled in 2 attempts with no escalation.
- The validator caught the mistyped fees workflow and forced it to be priced as a fix [40].

## Problems (reviewer)
- Sponsors, one of the six visitor needs in the brief, was dropped, and the unbuilt item 10 (colour scheme and placeholders) went with it. Neither was the Requester's real choice: Adaptation left sponsors out in [38] before Priority saw it.
- R-6 failed at v4 [30] and shipped. W-4's own checks passed, so the rubric never reached the builder. The fix was priced at 8, the same as a page section [69].
- Fees were split from the schedule although the data was in the brief [8]. That cost an 8-credit rewrite [75], and fees appear on the schedule only, not on the category cards.
- Identity told the Requester item 10 was 'not built yet' [32] while Audit said it passes [31]. [63] then named the wrong dropped items. Item numbers shift after drops, which invites this.
- The Requester's option text [58] does not name which items stay. The code chose.
- The form opens the visitor's mail app; Identity wrote that it 'emails' the organisers [32]. Registration is the main action, so a lost send is a real risk (unverified, not tested).
- The cap (80 = 2x start) was below the need: 78 spent, plus at least 18 unfunded (sponsors 10, R-6 8). The run ended on budget, not on design.

## Learnings (reviewer)
- Put the design rubric (R-1 to R-6) into each builder's brief and into W-4's completion check. Test: rerun this brief and see if R-6 passes at v4, avoiding the 8-credit fix.
- Have Adaptation fold facts already in the brief (fees) into the first build of the section. Test: compare credits against this run's 10 + 8 for fees. A saving of about 8 is my estimate, not measured.
- Have Adaptation send the full list and let Priority cut it. Test whether a named brief item like sponsors survives when polish competes with it.
- Hold Identity and Priority to their roles: no step instructions ([9][39][67][69]). Test with a prompt reminder, then count such messages.
- Test setup: rerun with a start of 60 or a cap of 3x. This run cannot show whether the loop reaches J2.h, because it died on budget.
- Test setup: Requester questions should name each dropped item with Audit's current status, and keep original item numbers. Audit should print what every extra issue is.
- Test setup: lessons memory was off (saved: []), charged equals estimate on all 8 workflows (rate card), and runs were sequential. So lesson saving, Priority's cost judgement and HOLD handling are untested. Recompute workable by code instead of re-auditing an unchanged version [66].
