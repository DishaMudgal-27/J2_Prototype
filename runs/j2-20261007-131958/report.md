# J2 run report: 20261007-131958

Brief: Brew Lab, Indiranagar, Bengaluru. One-page site. Must-haves, each one will be checked: today's opening hours are highlighted automatically; the pre-order form shows a running total in rupees; the loyalty section shows 10 stamp circles with the 10th marked FREE; every menu item shows a price; the location section has a "Get directions" link; the page works at 360px wide.

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** Clean one-cycle pass: all 5 workflows built and all 7 done-when items passed in 4.7 minutes for 75 of 80 budget, but the brief was easy and most of the department's hard paths were never exercised.

## Measured (counted by code)
- 17 AI calls, 1 cycles, 4.7 min, model sonnet
- Budget 75/80 (started 80, 0 raise(s) approved by the Requester, cap 160; rate card on), 5 site versions, final site 20 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 3 | 0 | 0 | 5 | Asked four bounded questions in one round with options for delivery [2], recorded a charter with rules and nothing left to confirm [5], and closed with an honest caveat that the highlight was not seen in a browser [28]. No design or audit work. |
| Adaptation | 1 | 0 | 0 | 4 | One proposal covering all 7 items with costs and a stated 5-unit margin [7]. It flagged that a fix (8) would need approval. It spent 94% of budget up front and the chat shows no proposal fields, so the completion checks cannot be judged. |
| Priority | 6 | 0 | 0 | 4 | GRANT tied each workflow to a done-when item [8] and correctly said a fix needs Identity's approval. It granted every ask in full with no counter, and its 5 later turns repeated 'within limits' with no new decision. |
| Coordination | 5 | 0 | 0 | 4 | Stated the scheduling rule each time and kept one writer at a time [10][13][16][19][22]. Minor flaws: the dependency is called the page shell in [10] but the menu in [13]; the rule text is duplicated in [22]. |
| Audit | 1 | 0 | 0 | 4 | Ran mechanical checks, passed 7 of 7, and found the duplicate title and meta charset [27]. It judged items 'on the code', and the chat gives no per-item evidence. It sent the correctable defect to Identity per team.md rather than Adaptation. |
| W-1 Builder | 1 | 0 | 0 | 4 | Built the shell and menu with all six prices [12]. The duplicate head tags most likely come from the shell, but the evidence does not attribute them. |
| W-2 Builder | 1 | 0 | 0 | 5 | Hours and a bl-today class set by script [15]. In scope, honest that it was not browser-tested. |
| W-3 Builder | 1 | 0 | 0 | 5 | Six items, live total, wa.me/919845000000 link, pay-at-pickup and 15-minute text [18]. Matches the charter rules. The mechanical check confirms the form submits. |
| W-4 Builder | 1 | 0 | 0 | 5 | 10 circles, 10th shows FREE, 5-column grid [21]. In scope, reported honestly. |
| W-5 Builder | 1 | 0 | 0 | 5 | Address and Get directions link match the supplied URL [24]. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v5: 7 pass, 0 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Zero redirects, invalid moves, validator refusals and retries; every workflow finished inside its envelope.
- Identity got all missing facts in one question round [2][4], so nothing was left to be confirmed.
- Builders and Identity labelled what was unverified ('not browser-tested' [12][15][18][21][24], [28]).
- Hand-offs followed team.md, and the write lock gave no collisions.

## Problems (reviewer)
- Today's highlight and the WhatsApp message content were checked by reading code. The mechanical check [26] covers overflow, JS errors, links and form submit only.
- Duplicate title and meta charset tags shipped [27][28]. Section assembly lets several agents add head tags.
- The 5-unit margin was below the cost of a fix (8) [7][8], so even a low-severity rework needed Identity approval.
- Priority and Coordination took 11 of 21 turns, mostly repeated envelope checks with no decision.
- Coordination's dependency wording differs between [10] and [13].

## Learnings (reviewer)
- Test system: this run never exercised COUNTER, REFUSE, HOLD, retries, conflicts or lessons (counters 0, refuses 0, held_ever 0, saved []). Next run: a brief that costs more than the budget, plus one with contradictory details.
- Test system: estimate_vs_charged is identical for all five workflows (10, 20, 25, 10, 10), so it cannot measure estimating accuracy. Record real call cost beside the rate card.
- Test system: add a render check with a fixed clock (a Monday and a Saturday) that asserts the highlighted row, and a check of the WhatsApp URL text. Evidence: [15], [26], [28].
- Design: give one agent ownership of the head, or have code dedupe head tags. Duplicates came from five writers sharing one file [27].
- Design: leave margin of at least one fix when granting. Test 70 of 80 against 75 of 80 and see whether rework then runs without an approval round trip.
- Untested, so no conclusion: whether one workflow for the whole 19 KB page would be cheaper than five serial ones. Run both on the same brief and compare calls and minutes.
