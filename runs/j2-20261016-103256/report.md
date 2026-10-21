# J2 run report: 20261016-103256

Brief: A one-page website for Brew Lab, a small specialty coffee shop in Indiranagar, Bengaluru. Visitors see the menu with prices, the opening hours and where to find the shop, and they can pre-order a coffee for pickup. Users: coffee lovers and office staff nearby. Problem: people cannot see the menu or order ahead. Must-have: menu with prices, pre-order form, map or address, opening hours. Constraints: one page only, works on phones, no payment. Success: 30 pre-orders per week.
Items and prices (rupees): Filter coffee 90, Cappuccino 160, Latte 180, Cold brew 200, Masala chai 80, Almond croissant 140, Banana bread slice 120.
Open: Monday to Saturday 7:30 am to 9:00 pm, Sunday 8:30 am to 6:00 pm.
Address: 12, 100 Feet Road, Indiranagar, Bengaluru 560038.
Contact: show phone +91 98450 12345 and email hello@brewlab.example.
Pre-orders: the customer enters name, phone, items and pickup time, and the order is emailed to hello@brewlab.example. No online payment, they pay at pickup.
Write the design docs first.

**Outcome:** Done with open items: shipped as is on the Requester's decision (The same failure came back twice in a row, so another cycle would likely repeat it.). Still not workable: document rubric D-5 (NEEDS_REVISION): No invented facts: every fact comes from the brief or the Requester's answers, or is labelled "Assumption:"; the evidence quotes each unlabelled claim not in the brief; necessary condition P4 not met: No invented facts: every number, email and proper name comes from the charter or the Requester's answers, or sits in an Assumption: line (not in the charter or the Requester's answers, and not marked Assumption: This).
**Reviewer verdict:** The PRD passed all 10 done-when items in one cycle for 133 of 300 budget, but the one remaining defect (an extra unlabelled 'Assumptions to confirm' section) was fixed by guesswork, never cleared, and the HLD, LLD and website were never built.

## Measured (counted by code)
- 25 AI calls, 2 cycles, 8.5 min, model sonnet
- Budget 133/300 (started 300, 0 raise(s) approved by the Requester, cap 600; rate card on), 7 site versions, final site 5 KB
- Negotiation: 2 proposals, 2 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'limit': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 3 | Correctly used the repeat-failure limit and asked the Requester one question [47]. But [36] spelled out the exact rework, which its role forbids. The option text in [47] says 'missing parts' when none were listed missing. [50] says 'all the parts you asked for' are in, yet the brief asked for design docs and a site, and only the PRD exists. |
| Adaptation | 2 | 0 | 0 | 3 | Clean one-workflow-per-section plan [6] and a small fix proposal [37]. But it named W-5 as the source without checking, and said so itself. That guess cost 8 and changed nothing. |
| Priority | 9 | 0 | 0 | 4 | Priced each part, reserved 175 for later work [7], and added a stop-loss in [38] that made the failed fix cheap. Stayed out of scheduling and quality. Envelope checks were correct every time. |
| Coordination | 7 | 0 | 0 | 5 | Stated its scheduling rule, held the write lock, handed off in order, and passed the stop condition to W-7 [40]. No collisions, no holds needed, no scope changes. |
| Audit | 2 | 0 | 0 | 4 | Evidence-based, cited codes F-11, D-5, P4, and in [46] reported where the extra section does not appear without fixing it. Small bleed in [35] ('the fix is to remove or relabel'). Never located the source of the section. |
| W-1 Builder | 1 | 0 | 0 | 5 | Problem section written first try, checks passed [11], report matches its completion check [12]. |
| W-2 Builder | 1 | 0 | 0 | 5 | Users section first try, checks passed [15], both groups and their actions covered [16]. |
| W-3 Builder | 1 | 0 | 0 | 5 | Goals section first try, checks passed [19]. |
| W-4 Builder | 1 | 0 | 0 | 5 | Largest section (menu, form, hours, address, constraints), 8 checks passed first try [23]. |
| W-5 Builder | 1 | 0 | 0 | 3 | Checks passed, but [28] added a 'visible-on-the-page check' not in the brief. Its labelled Assumption line is the likely trigger for the extra section (inferred from [43], not verified). |
| W-6 Builder | 1 | 0 | 0 | 5 | Out of scope section matched the brief [32]. Checks passed. |
| W-7 Builder | 1 | 0 | 0 | 4 | Followed the stop-loss, did not edit blindly, and reported honestly [43]. Its diagnosis (section assembled by code) is the most useful finding in the run, but it is a guess ('looks like'). |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v6: 10 pass, 0 warn, 0 fail; mechanical: not run
- Cycle 2, v7: 10 pass, 0 warn, 0 fail; mechanical: not run

## What went well (reviewer)
- All 10 done-when items passed on v6 and v7, no invalid moves, no redirects, no conflicts [35][46].
- Hand-offs were clean: 7 workflows run one at a time under one writer [9][13][17].
- Priority's [38] fix-to-finding mapping and stop-loss limited the cost of a wrong guess to 8.
- Audit and W-7 reported what they saw instead of claiming a fix.

## Problems (reviewer)
- The extra section was never traced to its source. Nobody looked at where it came from before spending on W-7 [37][43].
- Cycle 2 made no edit, yet it counted as 'the same failure twice' and triggered the limit [43][46]. The Requester was asked to give up before a real second attempt.
- Identity's wording to the Requester was misleading: 'missing parts' [47] and 'all the parts you asked for' [50], while HLD, LLD and the site were absent. [4] and [36] narrowed the charter to the PRD.
- Identity told Adaptation what to propose [36], against its role file.
- Mechanical checks did not run in either audit (mechanical_ran false), so the no-JS-error and 360px/1280px rules went untested.
- Estimated and charged cost match on all 7 workflows, so the rate card hides whether Adaptation estimates well.

## Learnings (reviewer)
- Test system: when a flagged defect may come from code assembly, have the check output name the producing part. Tie to [37][43]: without it, fixes get aimed at the wrong workflow.
- Test system: count a failure repeat only when a fix was actually applied. W-7 changed nothing [43], so the limit fired on a no-op.
- J2 design: finished messages should list what was not built (HLD, LLD, site) and say the charter covered the PRD only. Test with a prompt rule or code-added line.
- J2 design: add a code reminder or check that Identity does not dictate proposal content ([36]).
- Keep: dependency-ordered single writer, per-finding fix pricing, stop-loss on guessed fixes.
- Next test: a website brief with variable costs, so mechanical checks and estimate accuracy get exercised.
- Evidence is thin on the root cause. I did not see the PRD text or the check output, so the 'assembled by code' explanation rests on [43] and [46] only.
