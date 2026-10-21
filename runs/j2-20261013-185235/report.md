# J2 run report: 20261013-185235

Brief: Write a PRD for a web app where students book lab slots. The users are students and lab staff. The problem: booking is done on paper and slots get double-booked. Must-have features: book a slot, cancel a slot, and see availability. Constraint: it must work on phones. Success measure: 80% of bookings are made without staff help.

**Outcome:** Done with open items: shipped as is on the Requester's decision (The same failure came back twice in a row, so another cycle would likely repeat it.). Still not workable: done-when item 2 (F-2 NEEDS_REVISION): Users section names both students and lab staff and lists what each group does in LabSlot; done-when item 3 (F-3 NEEDS_REVISION): Goals section states the goal of replacing paper booking and avoiding double-booked slots; done-when item 4 (F-4 NEEDS_REVISION): Requirements section lists book a slot, cancel a slot and see availability for students, and view all bookings and cancel a booking for a student for lab staff; done-when item 5 (F-5 NEEDS_REVISION): Requirements section states that LabSlot must work on phones; done-when item 6 (F-6 NEEDS_REVISION): Success metrics section states that 80% of bookings are made without staff help, counted per term; done-when item 7 (F-7 NEEDS_REVISION): Out of scope section lists what LabSlot does not cover, without adding features beyond the must-have list; document rubric D-1 (NEEDS_REVISION): Every requirement is specific and testable; document rubric D-2 (NEEDS_REVISION): Goals and success metrics are measurable; document rubric D-3 (NEEDS_REVISION): Users and problem are consistent with the requirements; document rubric D-4 (NEEDS_REVISION): Out of scope is explicit; necessary condition P1 not met: All six sections are present and not empty (missing or empty: Users (missing), Goals (missing), Requirements (missing), Success metrics (missing), Out of scope (missing)); necessary condition P2 not met: Requirement ids are unique and sequential (R1, R2, ...) (no Requirements section); necessary condition P3 not met: Every brief fact appears exactly (missing: ['80% of bookings are made without staff help', 'per term', 'book a slot', 'cancel a slot', 'see availability', 'view all bookings', 'cancel a booking for a student', 'it must work on phones']); necessary condition P6 not met: Every goal has a matching success metric (no G1, G2, ... ids in Goals); necessary condition P7 not met: Every user group named in the charter appears in Requirements or in a "no actions in this version" statement (no requirement and no "have no actions in this version" statement for: Students, Lab staff).
**Reviewer verdict:** The department failed: only 1 of 6 sections was written, because Adaptation never got a proposal to Priority in 4 tries and the W-1 check disagreed with the document, so the Requester shipped a 357-byte, one-section PRD.

## Measured (counted by code)
- 25 AI calls, 4 cycles, 10.6 min, model sonnet
- Budget 20/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 3 site versions, final site 0 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 3 {'info': 1, 'limit': 2}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 8 | 0 | 0 | 3 | Right calls on the early questions [2], the charter [6] and the escalations [35][51], and it spotted F-9 [29]. But it dictated the proposal's contents and output method [29][39], which is Adaptation's job, and sent three near-identical nudges [29][39][45] that changed nothing. |
| Adaptation | 6 | 4 | 0 | 1 | Four turns with no valid next speaker [24][30][40][46], despite three explicit corrections from Identity. It started its replies with a JSON wrapper rather than @Priority. It also called W-1 'BUILD_WRONG' [20] when the heading was in v3 (F-9), and sent a fund request to Coordination instead of Priority [20]. No proposal ever reached Priority. |
| Priority | 2 | 0 | 0 | 4 | Granted all six at rate-card price (90 of 200, 20+10+10+30+10+10 adds up) and held 110 in reserve [9]. Its envelope check on W-1 was correct [12]. It was never given another proposal to judge. |
| Coordination | 2 | 0 | 0 | 3 | Correctly put everything on HOLD and routed to Adaptation [22]. But the hold reasons for W-3 to W-6 say 'W-2 done and verified', which is false because W-2 never ran. It should state the missing condition. It also called W-1 'done' while it was escalated. |
| Audit | 4 | 0 | 0 | 4 | Findings are specific, tied to criteria, and caught the record/document mismatch (F-9), the unlabelled claim (D-5) and Adaptation's missing next speaker (F-10) [44]. Four near-identical audits of an unchanged v3 added no new information. Mechanical checks did not run in any of the four audits. |
| W-1 Builder | 1 | 0 | 0 | 2 | Resent unchanged wording on 3 attempts [15][17]. Its report [18] does not say whether its completion check held, and 'first line of the markdown block' hints at the same wrapper problem. Its output is not in the log, so the real cause is unverified. |
| W-2 Builder | 0 | 0 | 0 |  |  |
| W-3 Builder | 0 | 0 | 0 |  |  |
| W-4 Builder | 0 | 0 | 0 |  |  |
| W-5 Builder | 0 | 0 | 0 |  |  |
| W-6 Builder | 0 | 0 | 0 |  |  |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v3: 1 pass, 1 warn, 6 fail; mechanical: not run
- Cycle 2, v3: 1 pass, 1 warn, 6 fail; mechanical: not run
- Cycle 3, v3: 1 pass, 1 warn, 6 fail; mechanical: not run
- Cycle 4, v3: 1 pass, 1 warn, 6 fail; mechanical: not run

## What went well (reviewer)
- Identity asked for the missing name and period before starting [2][4], and the charter had 8 checkable items [7].
- Priority's pricing was correct and left a reserve [9]. Budget use was low (20 of 200).
- Audit's code-counted findings were stable and clear, and the exit report lists open items honestly [56].

## Problems (reviewer)
- 5 of 6 sections never ran. The cause was a 3-attempt W-1 failure followed by 4 Adaptation turns with no valid next speaker.
- The W-1 check said '## Problem' was not found on all 3 attempts [13][15][17], yet Audit found it in v3 (F-9 [29]). Either the check ran against the wrong document or the builder output was wrapped. This is unresolved.
- The Requester's 'option 1' [37] bought nothing: the same failure repeated and the same question came back [51]. Four cycles ended with identical audits.
- W-2 to W-6 were chained behind W-1 [11][22], so one bad section blocked the whole document, although their facts come from the charter.

## Learnings (reviewer)
- Fix first: run the W-1 heading check by hand against v3. If it passes, the check reads the wrong document (F-9) and caused most of this failure. Evidence: [13] vs [29].
- Test system: when a reply has no valid next speaker, re-prompt with the format error as the W-1 retries do, rather than silently routing to Priority [25][31][41][47]. Evidence: 4 redirects, 0 proposals.
- Test system: only offer 'keep going' if something different will happen. The retry [37] repeated the same failure and spent a Requester decision.
- Design: let sections be independent and use document order only when assembling. Coordination's own rule says to schedule another ready workflow rather than block [22]. Test this against the same brief.
- Design: let 'fix' pricing apply to an escalated W-1 without a prior finding id. Adaptation could not use the 110 reserve for that reason [24].
- Design: fix the bookkeeping in the metrics: 'done: 1' and 'spent 20' count W-1 although it was escalated, which overstates progress.
- Evidence is thin. Only one workflow ran, the W-1 output is not in the log, and no audit ran mechanical checks, so builder quality and Priority's counter behaviour are untested.
