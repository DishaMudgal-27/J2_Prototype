# J2 run report: 20261013-164543

Brief: make a website for our college tech fest called Spark 2026 at Northfield College of Engineering in Pune. students should be able to see the schedule day by day, browse events by category, register for an event with a form, see the sponsors, find the venue, and contact the organisers on whatsapp. it should feel energetic and modern and work well on phones

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department built a workable site in 2 cycles, 9 minutes and 98 of 200 budget with no role violations by code, but the run was easy: nothing was contested, and one gap (the viewport tag) was missed in planning.

## Measured (counted by code)
- 30 AI calls, 2 cycles, 9.0 min, model sonnet
- Budget 98/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 9 site versions, final site 29 KB
- Negotiation: 2 proposals, 2 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 1 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 3 | Good: one round of questions [2], nothing invented, a final message that discloses the mailto limit [57]. Overreach: in [45] it picked the owner (W-1), the scope ('change nothing else') and told Audit what to test, which identity.md bars. It declared done [57] without telling the Requester the filter buttons were never click-tested, though it asked for that test itself [45]. |
| Adaptation | 2 | 0 | 0 | 3 | [8] says the 7 workflows cover items 1-10, but none added the viewport tag that item 8 needs, so a second cycle was needed. The fix proposal [47] was clean after the validator rejected the first draft [46]. No lesson was saved after Audit confirmed the fix [56]. |
| Priority | 10 | 0 | 0 | 4 | Granted both proposals and kept 110 in reserve for fixes [9], [48]. Envelope checks were consistent and in scope. Slight drift: it commented on bundling [9] and spoke to the Validator in [48]. It never countered or refused, so its bargaining judgment is untested. |
| Coordination | 8 | 0 | 0 | 4 | Stated its scheduling rule each time and kept one writer on the lock. The W-7 HOLD [31] was correct but redundant, since [11] already said W-7 waits on all six, and it caused a release and recharge of 15 [32], [36]. Its messages repeat a long boilerplate rule. |
| Audit | 2 | 0 | 0 | 4 | Found the real defect, the missing viewport tag, by reading the code [44], filed it as one finding, and sent it to Identity. It was honest in [56] that it has no click tool, so the filter check stays at read-only. Identity's request to re-measure tap targets [45] shows no visible result. |
| W-1 Builder | 1 | 0 | 0 | 4 | Delivered the style base, nav and hero as declared [14], with all 7 checks passing. The missing viewport tag was a gap in the declared scope, not a skipped step. |
| W-2 Builder | 1 | 0 | 0 | 4 | Three day blocks with dates and 8 cards at the supplied times, no rooms [18]. Audit passed it. |
| W-3 Builder | 1 | 0 | 0 | 4 | Five filter buttons and 8 cards with correct data [22]. The filter behaviour was only code-read, never clicked [56]. |
| W-4 Builder | 1 | 0 | 0 | 4 | Four required fields, an 8-event dropdown and a mailto [26]. The mailto only opens a draft, which Audit warned about and Identity disclosed [56], [57]. |
| W-5 Builder | 1 | 0 | 0 | 5 | Three text-only sponsor cards, no logos [30]. Matches the charter exactly. |
| W-6 Builder | 1 | 0 | 0 | 4 | Address plus a map link built from the address only, and no invented building or room names [35]. |
| W-7 Builder | 1 | 0 | 0 | 4 | Fixed the failed WhatsApp check on attempt 2 and said plainly what it did [41]. The cost is a raw 'wa.me/...' string visible on the page, added to satisfy a text-only check [38]. |
| W-8 Builder | 1 | 0 | 0 | 5 | Added exactly one viewport meta tag and touched nothing else [53]. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v8: 8 pass, 1 warn, 1 fail; mechanical: clean
- Cycle 2, v9: 8 pass, 2 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Zero redirects and zero invalid moves for every agent, and zero conflicts. Hand-offs followed the allowed list throughout.
- Code checks and Audit each caught a real defect: the WhatsApp text [38] and the missing viewport tag [44]. Both were fixed within limits.
- Only supplied facts were used. Rooms were excluded [6], [35], and sponsors and prices match the charter.
- The fix loop was cheap: 8 money and one extra cycle, with no budget raise and 102 left unspent.

## Problems (reviewer)
- The viewport tag was missed in planning [8] even though item 8 requires it. This forced cycle 2 [44] to [56].
- The mechanical render check reported 'no horizontal overflow at 360px' on v8 [43] while the page had no viewport tag. It has no viewport check, so only Audit's code read caught it.
- Identity [45] chose the owner and scope of the fix and told Audit what to test. That is Adaptation's and Audit's work per identity.md.
- The filter buttons (core item 3) were never click-tested [56]. Identity asked for it [45] and then declared done [57] without telling the Requester.
- W-7's check read page text, not the link href [38]. The builder had to add a visible raw URL to pass it [41].
- The validator rejected the first fix draft because its tap-targets check pointed at a selector the fix did not create [46]. This cost one extra round.
- No lesson was saved after Audit confirmed the fix, though team.md calls for one. The metrics show memory off, so this may be test configuration.
- Evidence is thin on negotiation and conflict. There were 0 counters, 0 refusals and 0 conflicts. Estimates equalled charges for all 8 workflows, so rate-card pricing hid any cost judgment.

## Learnings (reviewer)
- Add a 'viewport meta present' check to the code render check, and list it in Adaptation's base-workflow checklist. Evidence: [43], [44].
- Give Audit a headless click tool, or add a code check that clicks the filters and submits the form. Item 3 is still unverified after two audits [56].
- Make code checks that look for links read the href as well as the text. Evidence: [38], [41].
- Tighten Identity's prompt: after a finding, cite the failed criterion and let Adaptation choose owner and shape. Test whether [45] repeats.
- Keep the one-writer lock with the stated scheduling rule and the Priority envelope check per run. They produced zero redirects here.
- Test next: a brief with missing or conflicting facts, a budget that forces COUNTER or REFUSE, and memory switched on. This run exercised none of the bargain, conflict or lesson paths.
