# J2 run report: 20261006-123218

Brief: A one-page website for Brew Lab, a small specialty coffee shop in Indiranagar, Bengaluru. Visitors should see the menu with prices, the opening hours, and where to find us, and be able to pre-order a coffee for pickup. It should feel warm and modern and work well on a phone. Include a section about our beans and the farms they come from, and a simple loyalty-card explainer (buy 9, get the 10th free).

**Outcome:** Stopped: every done-when item passes with Audit's evidence, but Identity did not declare done. Done means the done-when list only, so this needs a look at Identity's reason above.
**Reviewer verdict:** The department built all ten done-when items in one cycle for 90 of 200 budget, but shipped a 10px overflow at 360px, and the run stopped before the rework Identity ordered could happen.

## Measured (counted by code)
- 14 AI calls, 1 cycles, 5.8 min, model sonnet
- Budget 90/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 4 site versions, final site 30 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 0 {}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 2 | 0 | 0 | 4 | The charter [2] was sound, with no invented facts. The ruling at [24] cites the 360px no-scroll standard, which is a defensible reading of 'material finding'. But it blocked 'done' on a clause that is not in done-when, so it effectively widened done-when (openly, not silently). It also mentioned the 8-cost fix, which drifts toward Priority's territory. |
| Adaptation | 1 | 0 | 0 | 4 | One turn, one proposal [4]: four small workflows, 90 of 200, unknowns marked as placeholders. Efficient and in role. It never got to act on the rework, and I can't see its completion checks, so evidence is thin. |
| Priority | 5 | 0 | 0 | 4 | It granted all four with envelopes tied to done-when items and left 110 in reserve for fixes [5]. It named an 8 price for a fix, and Identity used that figure. It did not push back on the four-way split. 'None is padded' is asserted, not shown. |
| Coordination | 4 | 0 | 0 | 4 | It stated its scheduling rule every time, gave exact HOLD conditions [10][14], and kept one writer on index.html. One claim was wrong: [7] promised each handoff would be 'Audit-clean', but Audit ran only once, at the end. |
| Builder | 4 | 0 | 0 | 4 | It stayed in scope on each of four runs and reported untouched stubs [13][19]. Result: 30 KB, no JS errors, no broken links, every unknown marked as a placeholder. It shipped a phone overflow on a brief that stresses phones. The cause is unknown. |
| Audit | 1 | 1 | 0 | 4 | It used the code measurement and said plainly that it could not find the cause [22]. 'Please fix it and re-run' edges into repair and scheduling, which the role forbids. The overflow-x:hidden cause is a guess, though marked 'may'. Its prose says 9 of 10 pass, but the code counts all_pass true. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v4: 9 pass, 1 warn, 0 fail; mechanical: phone overflow 10px

## What went well (reviewer)
- Clean run: 0 invalid moves, 0 validator refusals, 13 AI calls, 5.8 minutes, 90 of 200 spent.
- Placeholders were respected: 6 menu rows with placeholder names and prices [13], 'not sent' on the order summary [16], and the exact loyalty line [19].
- The single-writer lock serialized W-1 to W-4 without collisions, and HOLD released budget back [11].
- The code overflow measurement [21] gave Audit a hard fact to cite.

## Problems (reviewer)
- The 360px no-scroll rule is in standards but not in done-when. Done-when item 8 only checks the viewport meta tag and responsive CSS. So the harness reads 'all pass' while Identity reads 'not done' [24], and the run ends with no rework.
- The route check at [23] sent Audit's pick of Adaptation to Identity because 'everything passes'. team.md allows Audit to Adaptation for correctable defects, and F-11 was NEEDS_REVISION. The code's all_pass ignored that finding.
- The mechanical check ran only on v4, so there is no way to tell which workflow introduced the overflow. A guess is the W-4 loyalty graphic, unverified.
- The Requester was asked nothing about 8 open inputs. This is allowed by the charter, but the page is a template, with no real menu, hours or address.
- The envelope estimates equal the charges exactly (rate card). Budget data says nothing about estimation accuracy.

## Learnings (reviewer)
- Put 'no horizontal scroll at 360px' into done-when, or state that standards count toward done. Evidence: [24] and the outcome line.
- Compute all_pass from findings (any NEEDS_REVISION means not pass) and allow Audit to Adaptation on those. Evidence: [22][23] and metrics.
- Continue the cycle after Identity rules for rework. Otherwise this test cannot show whether the 8-cost fix works. Next test: rerun from v4 with the rework allowed.
- Run the code mechanical check after every workflow, not only at the end. It is cheap and would pin the defect to one run.
- Keep the one-proposal, serial, rate-card setup. Test next: a brief with real menu and hours, to see how agents treat supplied facts.
- Evidence is thin: one cycle, one model, one brief. It does not show whether rework or Requester questions work.
