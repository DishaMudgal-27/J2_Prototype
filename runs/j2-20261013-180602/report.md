# J2 run report: 20261013-180602

Brief: make a website for our college tech fest called Spark 2026 at Northfield College of Engineering in Pune. students should be able to see the schedule day by day, browse events by category, register for an event with a form, see the sponsors, find the venue, and contact the organisers on whatsapp. it should feel energetic and modern and work well on phones

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department finished a workable site (all 10 done-when items pass on v7, 108 of 120 spent), but cycle 1 built nothing because of validator refusals, and a Requester budget top-up was needed.

## Measured (counted by code)
- 32 AI calls, 2 cycles, 20.5 min, model sonnet
- Budget 108/120 (started 60, 1 raise(s) approved by the Requester, cap 120; rate card on), 7 site versions, final site 33 KB
- Negotiation: 3 proposals, 2 GRANT / 1 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 1: 1 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 2 {'info': 1, 'limit': 1}
- Validator refusals 11 (role 0), limit failures 0, warnings 1

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 5 | 0 | 0 | 4 | Asked the right questions up front [2] and closed on evidence [74-75]. Stretched its role by listing the sections for Adaptation to cover [6]. The budget question to the Requester [46] was cluttered with truncated item text. |
| Adaptation | 4 | 0 | 0 | 3 | Cycle 2 proposal registered cleanly [54]. But it accepted a counter it had already priced above [23, 25], which led to two rate-card refusals [26-27]. It also re-added tap-targets checks [52-53] after saying they were dropped [23]. |
| Priority | 10 | 0 | 0 | 3 | Warned correctly that 30 would not cover the rest [17]. Its claimed tap-targets swap did not land [18-20]. It cut scope below the rate-card minimum and accepted that [24], which left 7 items unfunded [29]. It also edited checks [17, 53], which is design work. Cycle 2 pricing was right [53]. |
| Coordination | 7 | 0 | 0 | 5 | Stated its scheduling rule every time, ordered W-6 after the venue and contact work it depends on [59], and ran the W-7 rewrite alone under the lock [63]. No HOLDs. Hard cases were not tested. |
| Audit | 2 | 0 | 0 | 4 | Filed findings to Identity only. Caught the missing h1, nav and invented day dates at v3 [45], and gave measured evidence at v7 [74]. Its '5 of 10 not met' wording does not match the 7 failures in the tally. |
| W-1 Builder | 1 | 0 | 0 | 3 | Passed its checks first time [32]. It added per-day dates not in the charter, which the fact check flagged [44], and it wrote the global palette [33] beyond its own section. |
| W-2 Builder | 1 | 0 | 0 | 5 | Eight cards with fees and placeholders, plus a category filter. Checks passed first time [36-37]. |
| W-3 Builder | 1 | 0 | 0 | 5 | Form has all fields and an 8-event dropdown, and it sends by mailto to the required address [41]. |
| W-4 Builder | 1 | 0 | 0 | 5 | Text-only sponsors, no logos [58]. |
| W-5 Builder | 1 | 0 | 0 | 5 | Address, map link, WhatsApp and email, with no invented hall [62]. |
| W-6 Builder | 1 | 0 | 0 | 5 | One h1, a nav and a single Register action, 10 checks passed first time [69-70]. Cleared N8 and the h1 and nav findings. |
| W-7 Builder | 1 | 0 | 0 | 5 | Removed the invented dates in one pass and kept to its envelope [66]. |

## Conflicts (full log in conflicts.json)
- C-1 (cycle 2, proposal): Adaptation vs Priority, 2 attempt(s), resolved by agents. Outcome: Adaptation accepted Priority's COUNTER: Day-by-day schedule (10), Events by category with fees (10), Registration form (15), Venue, map and contact (10), Base style, nav and hero (15) goes to the validator.

## Audit by cycle
- Cycle 2, v3: 3 pass, 0 warn, 7 fail; mechanical: clean
- Cycle 2, v7: 10 pass, 0 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- All 7 workflows registered and passed their checks on attempt 1. There were 0 failures, 0 holds, 0 role refusals and 0 redirects.
- Final render check is clean: no overflow at 360px or 1280px, no JS errors, no broken links, 1 h1 [72-74].
- No invented content: no hall name, no logos, no prizes [58, 62].
- The Adaptation and Priority conflict (C-1) settled in 2 attempts with no escalation. Both Requester pauses worked [3, 47-49].

## Problems (reviewer)
- Cycle 1 registered nothing [22]. 9 of the 11 validator refusals came here: digits in check text [8, 9, 11], generic selectors [12-14], and the disallowed tap-targets test [18-20].
- A Priority edit said to be applied was still rejected by the validator [17 vs 18-20]. The cause is unverified.
- The underpriced counter [24] and its acceptance [25] meant only 3 of 5 workflows registered. 7 items went unfunded and the Requester was asked for more money [46].
- Adaptation knowingly sent a plan with the N8 gap [15]. v3 then failed N8 and R-3 [43-44].
- The invented dates cost an extra workflow (W-7, 8 credits).

## Learnings (reviewer)
- Give Adaptation and Priority the validator rules before cycle 1: allowed check types, no digits in check text, selectors limited to section ids or classes, and the rate-card minimums. All 11 refusals were mechanical rules. Test next: rerun the same brief and aim for 0 refusals in cycle 1.
- Run a code pre-check of every Priority counter against rate-card minimums before it reaches Adaptation [24-27].
- Reword the validator's digit error [8]. 'Says X but expects 1' misled Adaptation three times.
- Either tell Adaptation that the mechanical check covers tap targets (Audit reported 0 small targets [74]) or allow that test.
- Start budget 60 against about 108 needed forced a Requester pause. Keep it if testing the limit path. Use roughly 110 for a normal-path test.
- Keep the mechanical fact check (N6). Decide whether a derivable date such as '15 Feb' counts as invented, since it cost 8 credits.
- Not tested: lessons memory was off (nothing saved or used), the lock was never contested, and estimates equal charged for all 7 workflows. This is one run on one brief, judged without screenshots.
