# J2 run report: 20261012-165124

Brief: make a website for our college tech fest called Spark 2026 at Northfield College of Engineering in Pune. students should be able to see the schedule day by day, browse events by category, register for an event with a form, see the sponsors, find the venue, and contact the organisers on whatsapp. it should feel energetic and modern and work well on phones

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department delivered a workable site (8 of 8 items pass) in 2 cycles for 96 of 200 budget, but lost one cycle because a rejected workflow was never reshaped, and the run never tested bargaining, conflict handling or lessons.

## Measured (counted by code)
- 31 AI calls, 2 cycles, 8.2 min, model sonnet
- Budget 96/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 9 site versions, final site 28 KB
- Negotiation: 2 proposals, 2 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 2 (role 1), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 4 | Clean charter with the no-rooms and names-only rules [4][6]; honest done message that flags the unverified email [58]. Slip: [47] spells out the workflow content (nav, six links, hero button) and its price, which is Adaptation's and Priority's job. |
| Adaptation | 2 | 0 | 0 | 3 | Fixed the validator error in one round [9]. Its bundle held a 'check' workflow that was rejected [11], and no Adaptation turn followed, so item 8 had no owner and cycle 1 failed on nav [45]. Its [48] proposal mostly restates [47]. |
| Priority | 10 | 0 | 0 | 4 | Grants match the rate card and the 120 reserve is explained [10][49]. Slip: [10] says polish runs last, which is ordering. It never countered, so bargaining is untested. 8 of 10 turns are near-identical envelope checks. |
| Coordination | 8 | 0 | 0 | 5 | States the scheduling rule every time and respects dependencies and the lock [13][51]. No holds were needed. Nothing to fault. |
| Audit | 2 | 0 | 0 | 4 | Mechanical check first, and it labelled email delivery as unverified instead of guessing [45][57]. Weakness: F-9 and F-10 (no nav, no hero Register) are not in done-when, so they are close to style preference. They cost 21 of 96 budget and a cycle. |
| W-1 Builder | 1 | 0 | 0 | 5 | Hero facts and labelled photo placeholder, passed first try [15][16]. |
| W-2 Builder | 1 | 0 | 0 | 5 | Three day tabs, 8 timed items, no rooms [20]. |
| W-3 Builder | 1 | 0 | 0 | 5 | Filter and fees as supplied [24]. |
| W-4 Builder | 1 | 0 | 0 | 4 | Passed first try. It chose a third-party form service and said delivery is unverified [28]. The vendor choice only reached the Requester at the end [58]. |
| W-5 Builder | 1 | 0 | 0 | 5 | Text-only sponsors, as the rule requires [32]. |
| W-6 Builder | 1 | 0 | 0 | 5 | Exact address and a Maps link [36]. |
| W-7 Builder | 1 | 0 | 0 | 4 | Failed its check once (wa.me link missing) and fixed it by printing the URL as visible text [39][42]. That may serve the check more than the student. Attempt-1 code is not shown, so this is unverified. |
| W-8 Builder | 1 | 0 | 0 | 5 | Added only the nav and Register button, hero facts unchanged, passed first try [53][54]. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v8: 6 pass, 1 warn, 1 fail; mechanical: clean
- Cycle 2, v9: 7 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Cycle 2 audit: 14 PASS, 1 warning, mechanical check clean at 360px and 1280px [56][57].
- Rules held: no rooms, no logos, no invented facts.
- 0 redirects, 0 invalid moves, 0 conflicts. 8 of 8 workflows done, and every estimate equalled its charge.
- The unverified email delivery was flagged consistently from builder to Identity [28][29][45][58].

## Problems (reviewer)
- A rejected workflow was dropped [11]. The validator logged 'item 8 ... no workflow covers it', and cycle 1 audit failed [45]. Cause is unclear: the log shows no Adaptation turn, so it may be a system gap rather than an agent miss.
- F-9 and F-10 have no done-when clause. [47] cites item 8, but item 8 covers overflow, JS errors and links, not nav. Reasonable UX, but outside the charter.
- Item 4 can never reach a clean PASS: the address is on example.com [4] and Audit cannot verify delivery.
- The audience_mix event flags '@e' at msgs 46 and 58 [events]. Cause unverified: msg 46 is not in the chat shown and [58] has no email address.

## Learnings (reviewer)
- Design: route any validator rejection back to Adaptation before scheduling, as team.md J2.e says. Next test: confirm an Adaptation turn follows the next rejection.
- Design: make the validator warn at registration when a done-when item has no owning workflow, instead of finding it after the audit. Tell Adaptation that page-wide checks are not workflows.
- Design: Identity should give the gap and finding ids and leave content to Adaptation. Audit findings outside done-when should cite a charter clause or be marked advisory. Trade-off: some useful nav may be skipped. Also reconcile audit.md ('send defects to Adaptation') with team.md ('all findings to Identity').
- Test system: this brief produced 0 counters, 0 refusals, 0 holds, 0 conflicts and memory off. Next run: a tight budget (about 60) to force a COUNTER, and memory on. The nav fix is a ready lesson candidate.
- Test system: use a mock mail endpoint, or check that the form request is sent, so item 4 can pass or fail instead of carrying a permanent warning.
- Test system: core_items has 7 entries and omits the sponsors item. Check this is intended. Evidence is one run, so treat all of this as a hypothesis.
