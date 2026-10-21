# J2 run report: 20261007-151441

Brief: Brew Lab, Indiranagar, Bengaluru. One-page site. Must-haves, each one will be checked: today's opening hours are highlighted automatically; the pre-order form shows a running total in rupees; the loyalty section shows 10 stamp circles with the 10th marked FREE; every menu item shows a price; the location section has a "Get directions" link; the page works at 360px wide.

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department built a workable 6-section site in 2 cycles and handled a fake Audit failure correctly on process, but it recorded a lesson for a fault that never existed.

## Measured (counted by code)
- 26 AI calls, 2 cycles, 7.7 min, model sonnet
- Budget 80/80 (started 80, 0 raise(s) approved by the Requester, cap 160; rate card on), 6 site versions, final site 28 KB
- Negotiation: 3 proposals, 2 GRANT / 0 COUNTER / 1 REFUSE (0 converted by code), 0 parked
- Conflicts 1: 1 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 1

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 4 | Bundled four questions into one message [2], recorded a 9-item checkable charter [5], and gave an honest closing caveat [42]. Two slips: [29] tells Adaptation how to investigate, and [42] says nobody has rendered the page while the mechanical check at 360px and 1280px passed [39] and the system says the render check is clean [43]. |
| Adaptation | 4 | 0 | 0 | 3 | Sensible one-workflow-per-section plan [7] and an honest dispute [30-32]. But it relabelled the same W-2 rewrite from the 8 fix part to the 5 styling part to fit the budget [32], and it saved a lesson [41] saying the rewrite made prices visible, when Audit's own v5 verdict was that all prices were present. |
| Priority | 9 | 0 | 0 | 4 | Clear GRANT/REFUSE with named risks [8][31][33], and envelope checks matched estimates. Weaknesses: [31] pushes the item to Identity instead of simply bargaining, and [33] dictates scope ('nothing else'). It accepted a relabel at the same scope. |
| Coordination | 6 | 0 | 0 | 4 | Stated its scheduling rule and dependencies every time, one writer at a time, no holds needed [10][13][22]. Budget commentary in [19] and [22] is outside its role, and [35] repeats the rule sentence. |
| Audit | 2 | 0 | 0 | 4 | Findings tied to criteria; in v6 it rated item 2 medium confidence because no cause was found [40] and kept the real warnings (closing-time pickup, duplicate head, unclosed main). Its first verdict was overridden by the test switch, so [28] is not its own judgement. |
| W-1 Builder | 1 | 0 | 0 | 4 | Shell, hours and shared hours data delivered in one run [12]; item 1 passed. Honest that it was not browser-tested. |
| W-2 Builder | 1 | 0 | 0 | 5 | Menu was correct: Audit's own v5 verdict was PASS before the override [27]. Not at fault for the forced failure. |
| W-3 Builder | 1 | 0 | 0 | 4 | Full form with live total and WhatsApp handoff [18]. Accepts a pickup at exactly closing time (F-4 warning), never fixed. |
| W-4 Builder | 1 | 0 | 0 | 5 | Exactly 10 circles, 10th FREE, free-drink text [21]; passed first time. |
| W-5 Builder | 1 | 0 | 0 | 5 | Exact address and charter URL [24]; passed first time. |
| W-6 Builder | 1 | 0 | 0 | 3 | Said plainly it could not reproduce the fault [37]. But it added a load-time script to restore missing prices, which goes beyond the styling-only scope that was funded. |

## Conflicts (full log in conflicts.json)
- C-1 (cycle 2, proposal): Adaptation vs Priority, 3 attempt(s), resolved by agents. Outcome: Priority granted Adaptation's revision: Menu price visibility fix (5) goes to the validator.

## Audit by cycle
- Cycle 1, v5: 7 pass, 1 warn, 1 fail; mechanical: clean
- Cycle 2, v6: 8 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- All 6 workflows registered, ran and finished with 0 validator refusals, 0 redirects, 0 invalid moves, 0 holds.
- Identity collected all facts up front, so nothing was left to be confirmed [4][5].
- The fix loop worked mechanically: Audit fail, Identity ruling [29], Adaptation and Priority settled it themselves in 3 attempts (C-1), re-audit pass [40].
- Honest confidence reporting from W-6 [37], Audit [40] and Identity [42].

## Problems (reviewer)
- The F-2 failure was injected by J2_FORCE_AUDIT_FAIL, and Audit had judged the menu PASS. The department chased a fault that did not exist, so repair skill went untested.
- Lesson L-20261007-151441-1 records a cause-and-fix that is unsupported. It will mislead later runs if memory is reused.
- Reserve was 5 against a fix price of 8 [7]. Recovery worked only because Adaptation repriced the same work [32].
- Final message and system message disagree on whether the page was rendered [42] vs [43].
- Three low findings shipped unfixed with 0 budget left [42].

## Learnings (reviewer)
- Test system: make the forced failure a real injected defect (for example strip two prices from the site) so builders and Audit have something to find. Today the switch tests only the loop, not repair.
- Test system: mark lessons saved during a forced-failure run as test artifacts, or skip saving them (evidence: [41] vs Audit's PASS).
- J2 design: the rate card prices by part type, so scope can be relabelled to a cheaper part [32]. Price by scope, or require a reserve at or above the fix price. Test next: same brief with reserve of 8 or more and compare cost and outcome.
- Keep: Identity's up-front question bundle, per-run envelope checks, and the confidence labels in Audit and Identity messages.
- Fix wording: define what 'render check' means. Overflow and JS checks cannot catch hidden or clipped text, which is the fault Audit described; add a visible-text check for prices.
- Evidence is thin: one run, 2 cycles, 0 counters, 0 holds. The counter and hold paths are untested.
