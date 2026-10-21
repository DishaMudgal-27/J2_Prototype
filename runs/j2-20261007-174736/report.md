# J2 run report: 20261007-174736

Brief: make a website for my aunt's flower shop called Petal & Stem in Jaipur. people should see the bouquets with prices, order one for delivery, and know the shop timings and where it is

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department built a workable site in 2 cycles for 68 of 100 budget with no conflicts or refusals, but the run was easy and tested few of J2's hard paths.

## Measured (counted by code)
- 19 AI calls, 2 cycles, 4.8 min, model sonnet
- Budget 68/100 (started 100, 0 raise(s) approved by the Requester, cap 200; rate card on), 4 site versions, final site 12 KB
- Negotiation: 2 proposals, 2 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 1 | 4 | Asked all missing facts in one round [2], closed with an honest 'test one order yourself' [33]. Sending back F-11 [22] was a sound call, though code logged it as an invalid move [23]. |
| Adaptation | 2 | 0 | 0 | 4 | Three small workflows covered all 10 items [7], then a one-fix rework at 8 [24]. No lesson was saved after the fix was confirmed (lessons.saved is empty). |
| Priority | 6 | 0 | 0 | 4 | Granted with a reserve and a reason [8], kept the rework to the viewport tag only [25]. It never had to counter or refuse, so its judgment is untested. |
| Coordination | 4 | 0 | 0 | 4 | Stated its rule every turn and kept one writer under the lock [10][13][16][27]. It repeated W-3's dependency on 'bouquets', which looks unneeded (thin evidence). |
| Audit | 2 | 0 | 0 | 5 | Found a real defect outside the done-when list, the missing viewport tag [21], and confirmed the fix [32]. Per-item evidence is not visible in the chat. |
| W-1 Builder | 1 | 0 | 0 | 4 | Header and cards done to spec [12], but it owned the page head and left out the viewport tag, which cost a cycle. |
| W-2 Builder | 1 | 0 | 0 | 5 | Form with the four fields, empty-field block and wa.me link in one pass, with 'not run in a browser' disclosed [15]. |
| W-3 Builder | 1 | 0 | 0 | 5 | Hours, address, tap-to-call and map link as given, scoped to #w3 [18]. |
| W-4 Builder | 1 | 0 | 0 | 5 | Did only the scoped viewport change [29]. 'Section W-1 is unchanged' is unclear, since it rewrote that section. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v3: 10 pass, 0 warn, 0 fail; mechanical: clean
- Cycle 2, v4: 10 pass, 0 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- One question round gave a charter with 10 checkable items and nothing left to confirm [2][4][6].
- Zero conflicts, validator refusals, role refusals or stuck runs; 18 calls, 4.8 minutes.
- Audit caught a defect that the code check and the done-when list both missed [21]. The fix was a cheap 8-unit workflow [24][25][29].
- Builders and Identity said what was not tested (browser run, real WhatsApp) [12][15][29][33].

## Problems (reviewer)
- The viewport tag was missed on the first pass and cost one cycle and 8 budget.
- The 360px mechanical check passed without the tag [20], so it gave false comfort.
- Code said 'Workable: yes' while F-11 was NEEDS_REVISION [21], then flagged Identity's correct rework as an invalid move [23].
- No counters, refusals, holds or Identity rulings happened, so most of the bargaining and conflict design went untested.
- Estimate equals charged on all four workflows (rate card), so there is no cost-accuracy signal.
- No lesson was saved after Audit confirmed the fix; the hand-off table has no path from Audit or Identity back to Adaptation.
- Nothing, including the WhatsApp link, ran in a real browser; the check was pushed to the Requester [33].

## Learnings (reviewer)
- Change: add a head baseline (viewport tag) to the head owner's role file or the validator. Evidence: F-11 [21][24]. This beats relying on Audit to catch it each time.
- Change: make the mechanical check fail when the viewport tag is missing, or emulate a real mobile viewport. Evidence: [20] passed without it.
- Change: treat an Audit NEEDS_REVISION as not workable in code, and don't log Identity's rework as an invalid move. Evidence: [21][23].
- Change: add a trigger for Adaptation to save a lesson after a confirmed fix. Evidence: lessons.saved is empty.
- Add: a mechanical form test that submits and checks the wa.me URL contents.
- Test next: a harder brief (tight budget, missing facts, conflicting asks) to exercise COUNTER, REFUSE, HOLD and Identity rulings. One easy run is thin evidence for the rest of the design.
- Test next: a cost model where actual differs from estimate, so Priority's estimate check can be judged.
