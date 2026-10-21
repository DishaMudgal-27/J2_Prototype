# J2 run report: 20261006-124308

Brief: A website for my cafe.

**Outcome:** Done: Identity confirmed every done-when item holds, with Audit's evidence. Open inputs for the Requester (not blocking): Menu items and their prices; Street address and map pin for the Indiranagar location; Phone number or contact for the cafe; Where pre-orders should be delivered (email, WhatsApp, phone or other); Brand colours, logo and photos, if any.
**Reviewer verdict:** A clean happy-path run: three small workflows built, Audit passed 8 of 8 in one cycle at 70 of 100 budget, but nothing was contested, so the harder behaviours were not tested.

## Measured (counted by code)
- 14 AI calls, 1 cycles, 6.0 min, model sonnet
- Budget 70/100 (started 100, 0 raise(s) approved by the Requester, cap 200; rate card on), 3 site versions, final site 26 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 2 {'info': 2}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 4 | Stayed in role. Paused and asked the Requester [2], re-asked when the answer was off-topic [5], recorded the charter [8], and closed with honest caveats [26]. Lost a point because [5] repeated all four questions and [26] is far longer than the 1-3 sentence rule. |
| Adaptation | 1 | 0 | 0 | 4 | One proposal [10] with three small workflows in build order, 70 of 100, 30 held for rework. It surfaced the missing order destination and the no-payment limit instead of hiding them. The chat shows only a summary, so the proposal fields cannot be checked. |
| Priority | 4 | 0 | 0 | 4 | Granted all three with retry limits, a stated reserve and a named trade-off [11]. Envelope checks [15][18][21] went to Builder as required. Nothing needed bargaining, so its counter and refuse judgement is untested. |
| Coordination | 3 | 0 | 0 | 5 | Stated its scheduling rule each time and gave exact HOLD conditions with a single file lock [13][17][20]. Never touched budget or scope. Scheduling was a straight line, so the evidence is thin. |
| Builder | 3 | 0 | 0 | 5 | Three runs, each matching its workflow [16][19][22]. Final file 25.5 KB, no JS errors, no overflow [24]. No scope creep. |
| Audit | 1 | 0 | 0 | 4 | Used the code check [24], checked all 8 items and sent the result to Identity [25]. The F-9 warning is not described in [25]. Identity's caveat in [26] suggests it is about the submit check, but that is inferred. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v3: 8 pass, 0 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Placeholders were used instead of invented menu, address or phone, as the charter rule requires [19][22][26].
- Budget handling worked: holds released money and it was charged again on run [14]; spend ended at 70 of 100.
- No redirects, invalid moves, validator refusals or stuck runs across 16 agent turns.

## Problems (reviewer)
- The pre-order form sends nothing to the cafe [22][26]. Done-when passed, but the business function does not work yet.
- Nobody ran the form submit. Identity admits Audit read the code [26], and the mechanical check lists no interaction test [24].
- Identity's re-ask [5] repeated the same four questions instead of narrowing them.
- Agent turns sum to 16 but ai_calls is 13. Unverified, but likely some turns are code-written, so call counts may not match what agents did.

## Learnings (reviewer)
- Test next with a brief and budget that force friction: a tight budget so Priority must counter, a validator rejection, an Audit NEEDS_REVISION. Metrics show 0 conflicts, counters, refusals and rework, so only the happy path is proven.
- Add a scripted submit to the mechanical check (fill the form, submit, assert the summary). It would close the one caveat Identity had to state [26].
- The rate card made estimate equal charge for all three workflows (35/10/25), so estimation accuracy and bargaining were not exercised. Vary costs in the next test.
- Decide whether done-when should require an order destination or an explicit 'demo only' label. Today a template full of placeholders counts as done. Keep the no-invention rule.
- Show the full text of warning findings like F-9 in the chat so reviewers do not have to infer them.
- Keep the pause-on-missing-info step, but have Identity re-ask only the unanswered items.
