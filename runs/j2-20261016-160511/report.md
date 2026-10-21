# J2 run report: 20261016-160511

Brief: A one-page website for Brew Lab, a small specialty coffee shop in Indiranagar, Bengaluru. Visitors see the menu with prices, the opening hours and where to find the shop, and they can pre-order a coffee for pickup. Write the design docs first. Users: coffee lovers and office staff nearby. Problem: people cannot see the menu or order ahead. Must-have: menu with prices, pre-order form, map or address, opening hours. Constraints: one page only, works on phones, no payment. Success: 30 pre-orders per week.

**Outcome:** Done with open items: shipped as is after the Requester accepted a document as it is. Still not workable: the product requirements: document rubric D-5 (NEEDS_REVISION): No invented facts: every fact comes from the brief or the Requester's answers, or is labelled "Assumption:"; the evidence quotes each unlabelled claim not in the brief; necessary condition P4 not met: No invented facts: every number, email and proper name comes from the charter or the Requester's answers, or sits in an Assumption: line (not in the charter or the Requester's answers, and not marked Assumption: Give).
**Reviewer verdict:** The site (v8) met all eight done-when items, but the department spent exactly 500 of 500, hit the 6-cycle limit, shipped the PRD with the no-invented-facts check (P4) still failing, and sent the Requester a garbled closing message.

## Measured (counted by code)
- 115 AI calls, 9 cycles, 30.1 min, model sonnet
- Budget 500/500 (started 500, 0 raise(s) approved by the Requester, cap 1000; rate card on), 8 site versions, final site 16 KB
- Negotiation: 9 proposals, 9 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 3 {'limit': 2, 'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 1

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 15 | 0 | 0 | 3 | [221] was a sound, budget-aware ruling that named the blocker (F-9) and kept the fix to one part. But it wrote the exact sentence for Adaptation, which is rewriting a proposal. The Requester-facing close [234] is a pasted rubric fragment ('the evidence quotes each unlabelled claim not in the brief;'). It also said 'finished' while [235] reports open items. The audience_mix flags at [111] and [173] show the same slip before. |
| Adaptation | 11 | 0 | 1 | 3 | Correctly judged the S2 check and the '.j2-btn' check were wrong, not the builds ([198], [215]), which saved retries and budget. But it replaced the S2 check with four element counts instead of getting the spec fixed, so coverage is weaker. Two PRD reworks (W-7, W-8) never cleared P4. One invalid move at [142] (no next speaker). |
| Priority | 40 | 0 | 0 | 3 | Stayed in role: envelope checks at [201], [205], [209], [226] and a sensible stop-loss at [223]. But 9 of 9 proposals were granted with no counter, and estimate equals charge on all 31 workflows, so real bargaining never happened. It also let the budget land on exactly 500/500 with no reserve. |
| Coordination | 31 | 0 | 0 | 4 | Stated its scheduling rule every time and gave the write lock to one workflow at a time. It flagged the LLD S2 vs charter gap ([200], [208]) without trying to fix it. Hold messages repeat every downstream workflow each time, which is noisy (21 of 31 workflows were held at some point). |
| Audit | 9 | 0 | 0 | 4 | Ran mechanical checks first and filed F-9 as a policy concern rather than a defect, saying no done-when item requires it ([220]). It also logged the S2 mismatch honestly as a warning (F-10) and confirmed the F-9 fix at [232]. Evidence is thin on why P4 failed twice. The PRD cause stayed 'suspected, unconfirmed'. |
| W-1 Builder | 1 | 0 | 0 |  |  |
| W-2 Builder | 1 | 0 | 0 |  |  |
| W-3 Builder | 1 | 0 | 2 | 2 | Two invalid moves at [21]: an empty 'done.' output was rejected twice. |
| W-4 Builder | 1 | 0 | 0 |  |  |
| W-5 Builder | 1 | 0 | 0 |  |  |
| W-6 Builder | 1 | 0 | 0 |  |  |
| W-7 Builder | 1 | 0 | 0 |  |  |
| W-8 Builder | 1 | 0 | 0 |  |  |
| W-9 Builder | 1 | 0 | 0 |  |  |
| W-10 Builder | 1 | 0 | 0 |  |  |
| W-11 Builder | 1 | 0 | 0 |  |  |
| W-12 Builder | 1 | 0 | 0 |  |  |
| W-13 Builder | 1 | 0 | 0 |  |  |
| W-14 Builder | 1 | 0 | 0 |  |  |
| W-15 Builder | 1 | 0 | 0 |  |  |
| W-16 Builder | 1 | 0 | 0 |  |  |
| W-17 Builder | 1 | 0 | 0 |  |  |
| W-18 Builder | 1 | 0 | 0 |  |  |
| W-19 Builder | 1 | 0 | 0 |  |  |
| W-20 Builder | 1 | 0 | 0 |  |  |
| W-21 Builder | 1 | 0 | 0 |  |  |
| W-22 Builder | 1 | 0 | 0 |  |  |
| W-23 Builder | 1 | 0 | 0 |  |  |
| W-24 Builder | 1 | 0 | 0 |  |  |
| W-25 Builder | 1 | 0 | 0 |  |  |
| W-26 Builder | 1 | 0 | 0 |  |  |
| W-27 Builder | 1 | 0 | 0 | 3 | Raised the spec conflict clearly and followed the charter ([192], [195]). But its report [196] does not say that its check had failed, which builder.md requires. |
| W-28 Builder | 1 | 0 | 0 |  |  |
| W-29 Builder | 1 | 0 | 0 |  |  |
| W-30 Builder | 1 | 0 | 0 | 3 | Correctly refused to edit other agents' sections ([213]). But it did not say whether its completion check held. |
| W-31 Builder | 1 | 0 | 0 | 5 | Added the one required sentence, changed nothing else, and passed 9 of 9 checks on attempt 1 ([227], [228]). |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 8, v7: 8 pass, 0 warn, 0 fail; mechanical: clean
- Cycle 9, v8: 8 pass, 0 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Site v8: no overflow at 360px or 1280px, no JS errors, no broken links, 16 KB, all eight done-when items pass [230], [232].
- The charter had exact facts and testable done-when items. The code-run necessary conditions (N1 to N8) caught the missing 30-per-week figure that Audit's item review alone passed [219].
- The site took five workflows plus one fix. No validator refusals, no role refusals, no open conflicts, only 3 Requester questions.
- Audit kept policy (N5) separate from defects, and Identity kept the last fix to the one part the budget allowed [220], [221].

## Problems (reviewer)
- The design docs took 422 of 500 budget (84%, my sum from the workflow charges). The site took 78. The last fix was funded with exactly 8 left, so one more failure could not have been paid for.
- P4 (no invented facts) failed on PRD v6 and v8 and was shipped unmet when the Requester accepted it as is [235].
- LLD S2 invented a quantity field and an item select that the charter does not have. LLD audit passed it anyway (L1 to L6 met). The conflict surfaced only in the site phase [192] and the LLD still disagrees with the built form [232].
- Two auto-generated slice checks were wrong (S2 field spec, '.j2-btn' counted page-wide). They cost failed attempts [193] to [197], [210] to [215].
- N5 forced an internal KPI ('Our goal: 30 pre-orders per week.') onto a public page. Audit said it does not help visitors [220]. It cost one cycle and the last 8 of budget.
- Identity's close [234] is garbled, and the audience_mix flags at [111] and [173] show repeated confusion between agent-facing and Requester-facing text.
- No lessons were saved (memory off) although the same failure types recurred.

## Learnings (reviewer)
- Add an LLD rubric item 'consistent with the charter field list'. The S2 mismatch [192] to [198] is the evidence. Test whether it catches the quantity field at LLD time.
- Scope slice checks to the owning section, not the whole page ('.j2-btn' found 4 times, expected 1 [210]). This is a fix to the test system.
- Mark charter facts as public or internal so N5 does not force targets onto the page. Test this on the same brief.
- Cap or phase the doc budget and keep a reserve (for example 15%). Docs took 84% here. The brief asked for docs first, so test a lower per-doc price rather than dropping them.
- Priority never countered in 9 grants and estimates matched charges everywhere. Test with underpriced proposals or a tighter budget to see whether it bargains. This run is thin evidence on that.
- Add a code check that Requester-facing Identity text is a full sentence and not a pasted rubric line [234].
- Rerun with lessons memory on. The P4 rework failing twice needs Audit to quote the exact unlabelled claim and the builder to target it. The audit text was not visible here, so the cause is unconfirmed.
