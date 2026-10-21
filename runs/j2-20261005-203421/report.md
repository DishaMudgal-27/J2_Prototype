# J2 run report: 20261005-203421

Brief: A portfolio site for Ananya Rao, a wedding photographer in Jaipur: photo gallery, packages and prices, testimonials, and an enquiry form for wedding dates.

**Outcome:** Done: Identity confirmed every done-when item holds, with Audit's evidence. Open inputs for the Requester (not blocking): Form delivery endpoint (for example an email or form-service address) so enquiries reach Ananya; launch blocker.; Real rate card: package names, inclusions and prices.; Real photos for the gallery.; Real client testimonials and quotes.; A packages and prices section renders multiple packages from one editable list, and each price carries the visible label 'sample, replace before launch'..
**Reviewer verdict:** The department built and passed the three sections it funded cleanly in one cycle, but shipped without the packages and prices section the brief asks for, and a charter edit plus a tight budget let 'Done' hide that.

## Measured (counted by code)
- 16 AI calls, 1 cycles, 4.3 min, model sonnet
- Budget 35/40 (started 40, 0 CEO raise(s), cap 80; rate card on), 3 site versions, final site 20 KB
- Negotiation: 1 proposals, 0 GRANT / 1 COUNTER / 0 REFUSE (0 converted by code), 0 withdrawals, 0 conflicts, 3 CEO decisions
- CEO choices 3: picked the option shown first 0, the option Identity listed first 1
- Validator refusals 1 (role 0), pauses 0, limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 3 | Stayed in role, but [6] says nothing from the brief was dropped while packages left the done-when list. It bundled three questions to the CEO in [2] where the role says one. It never ruled on Adaptation's funding request [10] until [21], and never took the shortfall to the CEO, who can raise the budget. [21] was honest about the gap. |
| CEO | 1 | 0 | 0 | 4 | Decided on the merits, named the trade-off for each of the three questions, and told Adaptation what to do [3]. Shown-first picks were 0 of 3, so no position bias is visible. |
| Adaptation | 2 | 0 | 0 | 3 | Proposed four workflows at 45 against 40 [8] and accepted the counter. It offered no cheaper packages scope. [10] asks Identity for a budget exception, which Identity cannot grant. |
| Priority | 1 | 0 | 0 | 4 | Specific counter (35 of 40) with the trade-off and the displaced work named [9]. 'The form I will not cut' edges into goal relevance, though Adaptation had already suggested that order [8]. |
| Coordination | 3 | 0 | 0 | 4 | Stated its rule each time, kept the single-writer lock, and did not schedule unregistered W-4 [12][14][16]. [14] repeats [12] and adds a judgement about the form. |
| Builder | 3 | 0 | 0 | 4 | Three workflows in order, 20 KB, mechanical check clean [13][15][17][19]. W-3 added a nav link and a draft-notice line [17]. The static banner Audit flagged may come from that line (inference). |
| Audit | 1 | 0 | 0 | 5 | Checked all five items, sent the missing packages to Identity as policy, and found the stale banner [20]. It did not repair anything. The F-6 text is not visible, so I could not check its severity. |

## Conflicts
- None

## Audit by cycle
- Cycle 1, v3: 4 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- One cycle, 15 calls, 4.3 minutes, 0 redirects, 0 invalid moves, 0 failed workflows.
- The labelled-placeholder pattern worked: all five done-when items pass, with no overflow at 360px or 1280px and no JS errors [19][20].
- The budget bargain closed in three messages [8][9][10].
- Audit exposed the brief gap that the charter no longer covered [20].

## Problems (reviewer)
- Packages and prices, one of four asks in [1], is unbuilt, yet the run ends 'Done' [21][22]. dropped_from_brief is empty.
- The validator refusal [5] moved a checkable build item into open_inputs. Likely cause is a keyword hit on 'launch' in 'replace before launch' (inference, not verified). The final open_inputs now lists a build item as a Requester input.
- Adaptation's ruling request [10] got no answer for ten messages, and workflows were registered and run anyway [11].
- The funding route went unused: raises is empty, 5 budget left, cap 80.
- Spend is not measured. Charged equals estimate on all three workflows (10, 15, 10).

## Learnings (reviewer)
- Fix the validator first: judge an item by what it checks, not by words inside a quoted label. Test: rerun the same brief with that item reworded without 'launch'. If packages gets built, the cause is confirmed.
- Add a done gate: every ask in the brief must map to a done-when item or a dropped_from_brief entry, and moving an item to open_inputs must count as a drop. Evidence: [6] versus [21].
- Add one line to identity.md: a funding shortfall on a brief deliverable goes to the CEO, who has budget_increase. Test: same brief and the same 40 start, and see whether Identity asks.
- Block scheduling while a blocking question to Identity is open ([10] to [11]). Evidence is one run.
- Log metered calls or tokens per workflow. Rate-card spend cannot show whether estimates are right.
- Word endpoint-note done-when items as 'shown only while unset', to prevent the stale banner (F-5).
- Evidence is thin: one run, three CEO choices, no Requester change round. Draw no conclusion on CEO bias or the change path.
