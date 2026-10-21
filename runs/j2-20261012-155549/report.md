# J2 run report: 20261012-155549

Brief: make a website for our college tech fest called Spark 2026 at Northfield College of Engineering in Pune. students should be able to see the schedule day by day, browse events by category, register for an event with a form, see the sponsors, find the venue, and contact the organisers on whatsapp. it should feel energetic and modern and work well on phones

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department delivered a workable site in 2 cycles for 131 of 200 budget with no illegal moves, but the run tested only the easy path: no counters, refusals or conflicts, and one real gap (email send) was disclosed late rather than decided.

## Measured (counted by code)
- 29 AI calls, 2 cycles, 8.4 min, model sonnet
- Budget 131/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 9 site versions, final site 48 KB
- Negotiation: 2 proposals, 2 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 4 | Asked one round then paused [2][3], and fenced Adaptation against invented facts [6]. Correct not-workable ruling [39] and honest closing note about mailto [49]. Weak spots: [39] dictated the proposal's owner and limits, and it never asked the Requester about real email sending, which Adaptation had flagged [8]. |
| Adaptation | 2 | 0 | 0 | 4 | Eight section-sized workflows covering all items [8], and a one-change fix proposal [40]. Flagged the mailto limit up front but sent it only to Priority, not Identity. Split one defect into two priced parts to match findings [40]. No lesson saved after the fix was confirmed. |
| Priority | 11 | 0 | 0 | 3 | Granted everything at rate-card price [9][41] with no counters, so the bargain role was barely used. Accepted paying 16 for R-6 and F-12, which Adaptation itself called the same defect [40][41]. Also told others which checks to rerun [41], which is outside its role. |
| Coordination | 9 | 0 | 0 | 4 | Right order (W-8 last on dependencies), stated the rule, one writer at a time, and correctly left test judgments to Audit [21][24]. Issues: six near-identical HOLD messages [14,18,21,24,27,30], the rule sentence duplicated in [18][24], and telling others which checks to rerun [43]. |
| Audit | 2 | 0 | 0 | 4 | Cited items and findings, caught the tap-target defect and confirmed the fix [38][48], and routed to Identity. Lenient on item 5: 'sends the details' passed with a warning though mailto does not send. Double-counted R-6 and F-12 in the tally. No evidence it tested the category filter. |
| W-1 Builder | 1 | 0 | 0 | 4 | Hero shows name, college, city and dates; stated checks honestly as read-only [13]. |
| W-2 Builder | 1 | 0 | 0 | 4 | 3 day blocks, 8 rows with exact times, no extra events [17]. No browser run. |
| W-3 Builder | 1 | 0 | 0 | 4 | 5 filter buttons, 8 cards with all fields [20]. Said the filter test is unconfirmed, which is honest but leaves a core item unverified. |
| W-4 Builder | 1 | 0 | 0 | 4 | Required fields, 8-event dropdown, confirmation that tells students to press send [23]. Honest about mailto. Form test unconfirmed. |
| W-5 Builder | 1 | 0 | 0 | 5 | Named concrete checks: one wa.me/910000033333 link, email twice, no invented building or pre-filled text [26]. Stayed inside the rules. |
| W-6 Builder | 1 | 0 | 0 | 4 | Three name-only sponsor cards, no images, no extras [29]. |
| W-7 Builder | 1 | 0 | 0 | 4 | Three dashed tiles labelled 'Photo placeholder', no img tags [32]. |
| W-8 Builder | 1 | 0 | 0 | 3 | Nav works, but the brand link shipped at 110x26 at 360px, which caused cycle 2 [37]. Its guard that hides nav links with missing targets [35] can mask a broken-link defect from the check. |
| W-9 Builder | 1 | 0 | 0 | 4 | One-property fix to the brand link, confirmed by the code check [45][47]. It rewrote the whole W-8 section for a one-line change, which adds regression risk. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v8: 9 pass, 2 warn, 0 fail; mechanical: clean
- Cycle 2, v9: 10 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Zero redirects, invalid moves, validator refusals and role refusals across 28 calls; every hand-off was legal.
- Facts stayed clean: no invented building name or pre-filled WhatsApp text [26], sponsors by name only [29], times and prices matched the list.
- The code mechanical check did the real verification: it found the tap-target defect [37] and confirmed the fix [47] with 10 PASS, 0 fail in cycle 2.
- Cycle 2 stayed small: one workflow, 16 spend, no regression on the other items [40][41][47].
- The mailto limit was disclosed at every stage [8][23][38][49] instead of being hidden.

## Problems (reviewer)
- Seven builders reported 'no browser run' [13,17,20,23,26,29,32]; only W-8 onward had code checks, so one defect surfaced after everything was built.
- Done-when item 5 says the form 'sends' details; mailto does not. Adaptation called it a Requester decision [8], but nobody asked and the Requester heard only at the end [49]. Under team.md this should be 'to be confirmed', yet to_be_confirmed is empty.
- R-6 and F-12 were one defect but were priced as two parts [40][41] and tallied as two failures [38].
- Role drift, minor: Identity specified the fix proposal's owner and limits [39]; Priority [41] and Coordination [43] prescribed which checks to rerun.
- Noise: six repeated HOLD messages and duplicated rule text [14 to 30].
- No lesson saved or used (lessons.memory false), though team.md says Adaptation saves one after a confirmed fix.
- Unverified: the name 'Spark 2026' sits with dates in February 2027, and no function checked whether that is intended.

## Learnings (reviewer)
- Test next with conflict built into the brief (tight budget, a request that cannot be met in one file, sponsor logos). This run had 0 counters, 0 refusals, 0 conflicts and 0 validator rejections, so Priority's bargain, Identity's ruling and Adaptation's reshape are untested.
- Decide how the department handles an unmeetable done-when item. Option: Identity asks one decision-ready question at J2.a when the charter item says 'sends'. Test whether Identity does this unprompted, using the same brief.
- Keep the code mechanical check, and add a check that clicks each category button and counts visible cards. 'Browse by category' is a core item and W-3 left it unconfirmed [20]; the audit of it has no visible evidence.
- Test running the mechanical check after the first builder and again at the end, versus only at the end. Evidence: one defect found at the end cost a full extra cycle and 16 budget [37][41]. Cost of earlier checks is unmeasured.
- Fix the test system: dedupe findings that name the same defect in the tally and in pricing (R-6/F-12), collapse repeated HOLD notices for an unchanged dependency, and stop repeating the rule sentence.
- Charged equals estimated for all 9 workflows, so spend is a price list, not a meter. Priority's 'treating estimates as known cost' failure cannot be assessed until actual use per run is reported.
- Run once with lesson memory on. A saved 'brand link needs a 44px tap target' lesson would plausibly have avoided cycle 2; this run cannot show it.
- Evidence is thin: one brief, one run, an easy path. Scores reflect role discipline observed, not resilience.
