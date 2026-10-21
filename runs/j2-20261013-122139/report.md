# J2 run report: 20261013-122139

Brief: make a website for our college tech fest called Spark 2026 at Northfield College of Engineering in Pune. students should be able to see the schedule day by day, browse events by category, register for an event with a form, see the sponsors, find the venue, and contact the organisers on whatsapp. it should feel energetic and modern and work well on phones

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department finished in one cycle with a clean render check, but a bad check target in the first batch forced a re-registration, left five dead workflows behind, and the form only opens the student's email app.

## Measured (counted by code)
- 30 AI calls, 1 cycles, 11.9 min, model sonnet
- Budget 85/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 10 site versions, final site 38 KB
- Negotiation: 2 proposals, 2 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 3 | 0 | 0 | 4 | Asked one clear round of questions [2], recorded a charter that uses only the Requester's facts [6], and told the Requester plainly about the mailto limit [56]. It declared done with item 4 ('sends the details by email') only partly met, and did not ask the Requester whether mailto was acceptable. |
| Adaptation | 2 | 0 | 0 | 3 | The first proposal [8] used bare tap-targets names that broke W-1 [13][15]. It fixed them only after Coordination flagged it [19][28]. It re-registered five workflows instead of revising them [29], never parked the old ones, and left the invented <j2-hero> tag in because 'no open finding' [29]. |
| Priority | 10 | 0 | 0 | 4 | Ran an envelope check before every run and stayed within role. Priority's [9] warning named the wrong cause (check type, not selector) and was outside its role. [30] says 'Nothing is cut' although the W-3 estimate of 20 became 10 for W-9 (metrics); unverified whether that matters. |
| Coordination | 10 | 0 | 0 | 4 | Correctly predicted the other bare-target failures from W-1's evidence [19] and held those workflows. Skipped held work and ran W-5 first [23], and flagged the superseded duplicates [52]. It resent a near-identical 5-line HOLD list six times [32][36][40][44][48][52], and [36] repeats the rule sentence twice. |
| Audit | 1 | 0 | 0 | 4 | Clear finding with the right hand-off to Identity [55] and two honest low-severity warnings. It rated the mailto form low, which understates a risk to the site's main action. It said 'looks workable', which is Identity's call. It cites no check of times or prices, and the mechanical check [54] does not cover them. |
| W-1 Builder | 1 | 0 | 0 | 3 | Used all 3 attempts [13][15][17]. It passed by inventing a <j2-hero> element to satisfy a malformed check, but reported the shortcut honestly [18]. The invalid tag shipped. |
| W-2 Builder | 1 | 0 | 0 | 5 | Passed on attempt 1 [21]. Report [22] gives counts (3 days, 8 slots). Content correctness is unverified beyond code checks. |
| W-3 Builder | 0 | 0 | 0 |  |  |
| W-4 Builder | 0 | 0 | 0 |  |  |
| W-5 Builder | 1 | 0 | 0 | 5 | Passed on attempt 1 [26]. Sponsors by name only, no logos, as the rules require [27]. |
| W-6 Builder | 0 | 0 | 0 |  |  |
| W-7 Builder | 0 | 0 | 0 |  |  |
| W-8 Builder | 0 | 0 | 0 |  |  |
| W-9 Builder | 1 | 0 | 0 | 5 | Passed all 4 checks on attempt 1 [34]. Filters, 8 cards and prices were delivered [35]. |
| W-10 Builder | 1 | 0 | 0 | 4 | Passed on attempt 1 [38]. It reports plainly that the form opens a mailto [39], which cannot truly send. Unverified whether its confirmation message claims the registration was sent. |
| W-11 Builder | 1 | 0 | 0 | 5 | Passed on attempt 1 [42]. Address and a maps link delivered [43]. |
| W-12 Builder | 1 | 0 | 0 | 5 | Passed on attempt 1 [46]. The wa.me digits (910000033333) match +91 00000 33333 [47]. Email shown. |
| W-13 Builder | 1 | 0 | 0 | 5 | Passed on attempt 1 [50]. Nav links to existing ids, overflow protection and viewport meta delivered [51]. Mechanical check shows no overflow at 360px or 1280px [54]. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v10: 8 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- No role breaks in 29 AI calls: 0 invalid moves, 0 redirects, 0 validator refusals, 0 conflicts (metrics).
- Coordination caught the bare-selector fault from one failing run [19]. All five replacement workflows then passed on attempt 1 [34][38][42][46][50].
- No invented facts. Identity asked one round of questions [2] and the Requester's answers were used verbatim [4].
- The mailto limitation was disclosed in the Audit finding [55] and to the Requester [56].
- The single write lock with one section per agent caused no collisions. The final render check is clean: no overflow, no JS errors, no broken in-page links [54].

## Problems (reviewer)
- Bare tap-targets targets in the first batch cost W-1 two failed attempts [13][15]. The fix needed five new registrations (W-9 to W-13), so 13 workflows were registered for 8 sections.
- W-3, W-4, W-6, W-7 and W-8 were never parked. There are 40 hold events, and Coordination asked for parking at [52]. Adaptation took no turn after [29], yet [53] says 'after Adaptation's attempt', which the log does not show.
- The shipped page keeps the invalid <j2-hero> tag. Adaptation declined to clean it, and Audit only warned [55].
- Done-when item 4 says submitting 'sends' an email. The form opens the email app and the student must press send. Audit rated it low and Identity still closed the work. If signups matter most, this is the biggest open risk.
- Coordination re-posted identical hold lists six times [32][36][40][44][48][52], which wasted tokens.
- Audit's PASS on the schedule times and prices is unsupported in the log. The mechanical check [54] only covers layout, JS errors, links and forms.
- Spend figures are not real cost. Estimate equals charged for all 13 workflows (metrics), so Priority's pricing was never tested.

## Learnings (reviewer)
- Change the validator to reject, or rewrite, a tap-targets target that is not an id, class or real tag at registration. validator_refusals was 0, so the fault surfaced at runtime and cost retries plus a re-registration.
- Let Adaptation revise a registered workflow in place, or auto-park the old one when a same-section replacement registers. Evidence: 5 zombie workflows and [52].
- Have Coordination send 'holds unchanged' instead of repeating the full list. Evidence: six repeats.
- Put the form mechanism in the charter. If only mailto is possible, Identity should ask the Requester one question before building, and Audit should rate it medium. Next test: a brief that needs a real backend, to see whether it lands in to_be_confirmed.
- Run the same brief with lessons memory on. It was off here (lessons.memory false, saved empty), and the selector mistake is the obvious lesson to see recur or not.
- Add content checks to the code-run mechanical pass: the 8 event times and prices, the mailto address and the wa.me number. Then Audit's PASS does not rest on narrative.
- Charge actual calls or tokens instead of the flat rate card, and log why [53] mentions an Adaptation attempt that is not in the log.
- Evidence is thin on the loop. This was one cycle with 0 counters, 0 refusals, 0 conflicts and no Audit rework, so those paths are untested. Next test: a tighter budget to force COUNTER and REFUSE.
