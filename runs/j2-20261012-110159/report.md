# J2 run report: 20261012-110159

Brief: make a website for my friend's south indian restaurant called Kaveri Kitchen in Pune. people should be able to see the menu with prices, filter it by veg and non-veg, see today's specials, book a table on whatsapp, find the address and opening hours, see photos of the dishes, and read a few customer reviews. it should feel warm and homely and work well on phones

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** A clean happy-path run: 7 workflows, all done, no conflicts, 0 failures, one audit pass, 120 of 200 spent, but it stressed almost none of J2's hard paths.

## Measured (counted by code)
- 21 AI calls, 1 cycles, 6.6 min, model sonnet
- Budget 120/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 7 site versions, final site 38 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 3 | 0 | 0 | 4 | Asked one bundled round of questions [2], got a full answer, recorded the charter, and closed with evidence [35]. The charter carries a garbled done-when item ('160... see menu price 180') and a rule the Requester never stated (editable data in one place). The low audit warning got no recorded disposition. |
| Adaptation | 1 | 0 | 0 | 4 | One proposal covers all 12 done-when items and gives menu and specials one shared data object [8]. Seven workflows for a 38 KB page is more than the smallest useful split. The full proposal fields are not in the chat, so completeness is unverified. |
| Priority | 8 | 0 | 0 | 3 | In role, no overreach. It granted all seven at once at the rate-card minimum [9] with no bargaining. The seven envelope checks are near-identical and 'Budget 120/200 used' never changes [12, 15, 18, 21, 24, 27, 30], so they show little judgment. |
| Coordination | 7 | 0 | 0 | 4 | Stated its scheduling rule each time, ran W-1 first for the shell dependency and kept one writer on the lock [11, 14, 17]. The rule text is duplicated in [26] and [29]. Nothing was on hold, so HOLD handling went untested. |
| Audit | 1 | 0 | 0 | 3 | Reported all 12 items passing [34], but its tally (18 PASS, 2 warnings) disagrees with the metrics (12 pass, 0 warnings). Filter results and the WhatsApp message content were judged 'on code', not in a browser. It did not flag the garbled charter item. |
| W-1 Builder | 1 | 0 | 0 | 4 | Shell and theme done [13]. The 'hide links to missing ids at load' rule can hide a missing section from the link check. |
| W-2 Builder | 1 | 0 | 0 | 4 | All contact facts match the charter [16]. Honest that it was not browser-run. |
| W-3 Builder | 1 | 0 | 0 | 5 | 11 dishes in one data object, filter counts by data 8 Veg and 3 Non-veg, matching the charter [19]. |
| W-4 Builder | 1 | 0 | 0 | 5 | Specials read from the menu data, so Mysore dosa shows 180 and nothing is hard-coded [22]. |
| W-5 Builder | 1 | 0 | 0 | 4 | Uses wa.me/910000033333 with the details in the message [25]. It added unrequested validation (past dates, time window), which is reasonable but beyond the declared scope. |
| W-6 Builder | 1 | 0 | 0 | 4 | Six labelled empty spots [28]. The 'real photos are coming' note is not a Requester-supplied fact. |
| W-7 Builder | 1 | 0 | 0 | 5 | Exactly the three supplied reviews and nothing extra [31]. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v7: 12 pass, 0 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Every agent stayed in role: 0 redirects, 0 invalid moves, 0 validator or role refusals.
- One question round to the Requester was enough [2, 4]; nothing is left to be confirmed.
- Menu and specials share one data object, so the filter and specials cannot drift apart [19, 22].
- The code-run render check (360px, 1280px, JS errors, links) was clean [33].
- No invented content: offers, prices and reviews match the Requester's facts.

## Problems (reviewer)
- The charter's specials item contains leftover text '160... see menu price 180', and the validator still called the charter valid [7].
- Audit's counts conflict: [34] says 18 PASS plus 2 warnings, metrics say 12 pass and 0 warnings. The Call us underline warning has no recorded outcome [34, 35].
- No browser test of filtering or of the WhatsApp message contents; the only form check is 'submit' [33]. Builders said 'not yet run in a browser' [13 to 31].
- Estimate equals charge for all 7 workflows, so cost is a rate-card figure, not a measurement.
- Priority and Coordination envelope checks are templated and repeat 7 times for one tiny site [11 to 30].

## Learnings (reviewer)
- This run tests only the happy path: 0 counters, refusals, conflicts, holds or retries, and 1 cycle. Next, set the budget below 120 or give a brief with a missing fact to exercise COUNTER/REFUSE and the Identity ruling.
- Lessons memory was off (lessons.memory false), so the 'save a lesson' step is untested. Run a second cycle with memory on.
- Add a charter check that rejects ellipses, unresolved text and figures that differ from the Requester's data. The 160/180 item got through.
- Add scripted checks: click Veg and expect 8 dishes, Non-veg expect 3, submit the form and read the wa.me URL. Also confirm all six section ids exist, since W-1 hides links to missing ids [13].
- Make Audit's tally match the metrics and require Identity to record what it did with each warning.
- Log real model calls per workflow against the envelope. Today 'charged' equals the estimate, so Priority's scrutiny cannot be judged. Also test a 2 or 3 workflow split to see if the 14 overhead turns shrink; the cost is less isolation per section.
- Keep: dependency-first scheduling with a stated rule, the single write lock, rate-card envelopes and the code-run render check. Evidence is thin on final page quality because I saw only messages and metrics, not the page.
