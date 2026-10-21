# J2 run report: 20261013-165916

Brief: Write a PRD for a web app where students book lab slots. The users are students and lab staff. The problem: booking is done on paper and slots get double-booked. Must-have features: book a slot, cancel a slot, and see availability. Constraint: it must work on phones. Success measure: 80% of bookings are made without staff help.

**Outcome:** Done: the PRD is workable. Every done-when item, rubric item and necessary condition passes.
**Reviewer verdict:** The department delivered a workable LabSlot PRD in one cycle (9.1 min, 98 of 200 budget, 7 workflows, zero validator refusals), but it only exercised the happy path and left the staff-role gap as a warning.

## Measured (counted by code)
- 33 AI calls, 1 cycles, 9.1 min, model sonnet
- Budget 98/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 7 site versions, final site 4 KB
- Negotiation: 2 proposals, 1 GRANT / 1 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 1: 1 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 3 {'fact': 2, 'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 7 | 0 | 0 | 4 | Asked for the name [2], refused to invent a G2 number [42], and re-asked when 'option A' came with no value [45]. The first question [38] bundled a choice, an example and an optional staff question, which cost an extra round. 'to_agents' contained '@Requester' three times (events at msgs 38, 45, 62). Declared done [62] with the staff warning still open. |
| Adaptation | 3 | 0 | 0 | 4 | Six one-per-section workflows [8] and a clean revision for the G2 fix [51]. Accepted the counter with a reason [53]. Only 3 turns, so evidence is thin. It never saved a lesson after Audit confirmed the fix [61]. |
| Priority | 9 | 0 | 0 | 4 | GRANT at rate-card minimums [9] and a useful COUNTER cutting 40 to 8 [52]. The counter leaned on what Audit's re-check would clear, which edges into Audit's lane, but it was correct (P5 met [60]). Estimates equal charges on all 7 workflows, so there is no real cost measurement. |
| Coordination | 7 | 0 | 0 | 4 | State the rule every time, honoured dependencies and the write lock [11][15][19], no holds needed. Never tested under conflict. Message [27] repeats the rule text. |
| Audit | 3 | 0 | 0 | 4 | Found the G2 gap beyond the done-when list [37] and refused to invent a number [44]. Passed item 2 with a warning although no staff action is stated, which is generous. mechanical_ran is false on all 3 audits. |
| W-1 Builder | 1 | 0 | 0 | 5 | In scope, checks passed on attempt 1 [13][14]. |
| W-2 Builder | 1 | 0 | 0 | 3 | Staff wording ('run the labs', 'help with fewer bookings') goes beyond the brief [18][61], against the standard of using only brief facts. |
| W-3 Builder | 1 | 0 | 0 | 4 | G1 and G2 traced to the problem, no invented numbers [22]. |
| W-4 Builder | 1 | 0 | 0 | 4 | R1 to R5 all traced [26]. R5 is derived from the problem, not a must-have, but allowed by the rule. |
| W-5 Builder | 1 | 0 | 0 | 5 | One metric only, nothing added [30]. |
| W-6 Builder | 1 | 0 | 0 | 4 | Six exclusions with no source in the brief [34]. Audit passed item 7, but F-10 flags statements beyond the brief and does not say which. Attribution is unproven. |
| W-7 Builder | 1 | 0 | 0 | 5 | Kept G1, added G2 = zero, no period or extra number [58]. |

## Conflicts (full log in conflicts.json)
- C-1 (cycle 1, proposal): Adaptation vs Priority, 2 attempt(s), resolved by agents. Outcome: Adaptation accepted Priority's COUNTER: Add G2 zero double-booking metric to Success metrics (8) goes to the validator.

## Audit by cycle
- Cycle 1, v6: 7 pass, 1 warn, 0 fail; mechanical: not run
- Cycle 1, v6: 5 pass, 2 warn, 1 fail; mechanical: not run
- Cycle 1, v7: 7 pass, 1 warn, 0 fail; mechanical: not run

## What went well (reviewer)
- Every workflow passed its code checks on attempt 1; 0 redirects, 0 invalid moves, 0 role refusals.
- Nobody invented a G2 target; Identity and Audit both held the line [42][44].
- The Priority/Adaptation bargain settled in 2 attempts with no escalation [52][53].
- The fix was one small workflow (8) instead of five parts (40).

## Problems (reviewer)
- The G2 gap (goal 'prevents double-booking' with no metric) surfaced only at Audit [36][37]. It cost W-7, 3 pauses and 2 extra Requester rounds.
- Item 2 is still only a warning: no stated staff action. The optional staff question went unanswered and was dropped [45][62]. The system's 'every done-when item passes' [64] overstates this.
- Identity's question [38] asked for a choice, then a value. The Requester answered 'option A' with no number [40], forcing a repeat [45].
- Audit's mechanical checks never ran (mechanical_ran false x3), so the 'run mechanical checks first' step is unverified.
- Envelope shows 'model calls 0/2' for every run although builders ran [12][16], and charged equals estimate for all 7. The envelope and cost tracking may be fixed-price display, not measurement (unverified).

## Learnings (reviewer)
- Test next: a run that hits the untested paths. Refusals, parks, holds, validator rejections and Identity rulings were all 0. Use a tight budget or a conflicting brief. This run proves only the happy path.
- Change: run the necessary-conditions check (P6 style) right after the charter or the first proposal, so goal-without-metric gaps are asked about up front, not after six sections are built [36].
- Change: Identity should ask for the missing value directly with a stated fallback ('give a number or say no number'), not a choice first [38][40].
- Fix the test system: make sure Audit's mechanical checks run or are marked not applicable for markdown PRDs, and confirm envelope call counts are real.
- Decide whether a done-when item that passes only with a warning counts as done. Today 'Done: every item passes' [64] hides item 2's gap.
- Lessons memory was off (memory false, none saved or used). The 'save a lesson after a confirmed fix' step is untested. Enable it for the next run.
- Keep: the code-counted per-workflow checks and the stated scheduling rule. Both gave clean, verifiable evidence.
