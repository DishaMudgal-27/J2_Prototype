# J2 run report: 20261015-114723

Brief: Make a website for CodeSprint Pune 2027, a two-day student and professional hackathon in Pune. Participants should be able to compare the three tracks, work out what they will pay with a fee calculator, register their team with a form, see the day-one and day-two schedule, see the prizes for each track, read FAQs, and see sponsors by tier. Mentors should be able to sign up with a separate form. Add a countdown to the start of the hackathon, a menu that stays on screen and shows which section you are in, and a high-contrast mode that works across the whole page. It should feel energetic and clear and work well on phones.
Day one: Saturday 6 March 2027. Day two: Sunday 7 March 2027. Venue: Lakeside Tech Hall, 12 Lake Road, Pune 411002. Tracks: Web Track (team size 1 to 4, build time 24 hours, first prize Rs 50000); AI Track (team size 2 to 4, build time 24 hours, first prize Rs 75000); Hardware Track (team size 2 to 4, build time 30 hours, first prize Rs 60000). Entry fee per participant: Student Rs 400, Professional Rs 800. Meal pass: Rs 200 each, optional. Early-bird: 10% off entry fees only (not meal passes) for registrations up to 15 February 2027. Fee calculator: choose ticket type (Student or Professional), number of participants (1 to 4) and number of meal passes; show the total. Registration form: team name, lead name, lead email, lead phone, track (dropdown), ticket type (Student or Professional), college name (only shown if ticket type is Student, and required only then), number of participants (1 to 4), meal passes yes/no, dietary preference (Vegetarian or Non-vegetarian, only shown if meal passes is yes); sends to register@example.com. Mentor form: name, email, area of expertise (Web, AI, Hardware), available Saturday / Sunday / both; sends to mentors@example.com. Schedule: Day one 9:00am check-in opens, 10:00am opening and kickoff, 1:00pm lunch, 8:00pm mentor round. Day two 10:00am final submissions close, 11:00am demos begin, 3:00pm prize ceremony. FAQs: Can I change my track? Yes, until 20 February 2027 by email. Is there parking? Yes, free at the north gate. Are refunds available? No. Do I need my own laptop? Yes. Is there Wi-Fi? Yes, at the hall. Can I join without a team? Yes, we will match you with a team on day one. Sponsors: Gold: Northwind Cloud; Silver: Bytecraft Labs, Circuit House; Community: Pune Coders Club. Contact: code@example.com, WhatsApp +91 00000 55555. No photos yet, use placeholders for photos and sponsor logos.

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** J2 shipped a workable site (all 15 done-when items pass on v23, N1 to N8 met, 187 of 200 spent), but cycle 1 produced nothing and 32 of the 187 went on rework that the workflow checks should have caught.

## Measured (counted by code)
- 58 AI calls, 3 cycles, 24.9 min, model sonnet
- Budget 187/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 23 site versions, final site 55 KB
- Negotiation: 3 proposals, 2 GRANT / 1 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 1: 1 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 0 {}
- Validator refusals 19 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 3 | 0 | 0 | 3 | Gated 'done' on evidence [133][134]. But [108] prescribed implementation (empty meals field, script-filled total, which agent does what), which its role forbids. The final message [134] omits the mailto-only forms, the open R-5 warning and the 10:00am IST countdown assumption set in [3]. |
| Adaptation | 5 | 0 | 0 | 3 | Two invalid submissions: selector errors, then missing goal_gap, outputs and completion_check [5-9][12-24]. It also miscounted 14 vs 13 vs 15 workflows [10][11]. Later it accepted the COUNTER explicitly [112] and fixed targeted items. Its W-1 and W-6 checks contradicted each other (see problems). |
| Priority | 22 | 0 | 0 | 4 | Caught the two missing workflows [11]. The COUNTER kept a retry reserve (13 left) and gave a budget reason [111]. Minor creep: it set run order and 'no bundling' [11][28], and judged R-5 'cosmetic' [111]. 22 turns, almost all 'within limits' relays. |
| Coordination | 19 | 0 | 0 | 3 | Stated its scheduling rule every turn, kept the single writer lock, and unblocked work around the escalated W-6 [69]. But it invented a HOLD condition that was not a declared dependency [69] and only admitted it at [98]. W-13's HOLD was repeated 8 times with the same outcome. |
| Audit | 2 | 0 | 0 | 4 | Found real defects (duplicate #register, sponsor wording) and routed N6 to Identity for triage [107]. Its reports name F-5 and F-17 without saying what they are [133]. It never reported on Coordination's request [98] to check that the hero CTA lands on the real form. |
| W-1 Builder | 1 | 0 | 0 | 3 | Added a hidden placeholder #register plus a removal script to pass its own link check [40]. That created a cross-section clash that cost W-6 three failed attempts. |
| W-2 Builder | 1 | 0 | 0 |  |  |
| W-3 Builder | 1 | 0 | 0 |  |  |
| W-4 Builder | 1 | 0 | 0 |  |  |
| W-5 Builder | 1 | 0 | 0 |  |  |
| W-6 Builder | 1 | 0 | 0 | 4 | Correctly refused to touch W-1's section [65]. Attempts 2 and 3 repeated the same failure with no change [62][64]. |
| W-7 Builder | 1 | 0 | 0 |  |  |
| W-8 Builder | 1 | 0 | 0 |  |  |
| W-9 Builder | 1 | 1 | 0 | 3 | Report was only 'W-9 done' with no change summary or check status, and no valid next-speaker pick [80][81]. W-15 did the same [33][34]. |
| W-10 Builder | 1 | 0 | 0 |  |  |
| W-11 Builder | 1 | 0 | 0 |  |  |
| W-12 Builder | 1 | 0 | 0 |  |  |
| W-13 Builder | 1 | 0 | 0 | 3 | Passed on attempt 2 [102] by disabling smooth scroll and polling every 100ms [103]. That changes real behaviour to satisfy a test, and the effect on users is unverified. |
| W-14 Builder | 1 | 0 | 0 |  |  |
| W-15 Builder | 1 | 1 | 0 |  |  |
| W-16 Builder | 1 | 0 | 0 |  |  |
| W-17 Builder | 1 | 0 | 0 |  |  |
| W-18 Builder | 1 | 0 | 0 | 4 | Reported where the flagged 0 was and noted other scripts also contain a 0 [125]. This is useful evidence on N6. |
| W-19 Builder | 1 | 0 | 0 |  |  |

## Conflicts (full log in conflicts.json)
- C-1 (cycle 3, proposal): Adaptation vs Priority, 2 attempt(s), resolved by agents. Outcome: Adaptation accepted Priority's COUNTER: Sponsor tier lines in exact wording (8), Remove duplicate register placeholder (8), Calculator without literal zero defaults (8), Contrast toggle out of the way (8) goes to the validator.

## Audit by cycle
- Cycle 2, v19: 12 pass, 2 warn, 1 fail; mechanical: clean
- Cycle 3, v23: 14 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Zero invalid moves and zero role refusals across all agents. The single-writer lock held: no collisions, 19 of 19 workflows done.
- Most workflows (W-2 to W-5, W-7, W-8, W-10, W-12) passed their checks on attempt 1.
- The Adaptation vs Priority conflict settled in 2 attempts without escalating (C-1).
- Cycle 3 fixed all three workability problems for 32, and the code checks confirm it: N5 and N6 met, no overflow, no JS errors [131][132].

## Problems (reviewer)
- Cycle 1 registered nothing: 19 refusals, and the validator exposed one error class per round [26].
- Workflow checks were weaker than the charter checks. W-11 passed its 4 checks [88] but missed N5 on the exact sponsor wording, and W-5 missed N6. That is 32 spent on W-16 to W-19.
- W-1's check needed #register to exist while W-6's check needed exactly one. W-6 was escalated after 3 attempts [66].
- Identity [108] guessed the source of the N6 '0' and prescribed the fix. W-18 later found zeros in other scripts [125], so N6 looks like a crude check.
- The final message [134] does not tell the Requester that the forms open a mail client rather than send.

## Learnings (reviewer)
- Change: give Adaptation the validator's full required-field and selector rules up front, or pre-run the validator. Test: does cycle 1 register anything? Evidence: [5-9][12-24].
- Change: put the charter's exact fact strings, the N5/N6 checks and cross-workflow checks into each workflow's own checks, or run them after each build. Evidence: 32 of 187 (17%) went on rework.
- Change: let a check be deferred or owned by the section that creates the target. Evidence: W-1 and W-6.
- Test next: make within-limits envelope checks code, and keep Priority for GRANT and COUNTER. Evidence: Priority and Coordination took 41 of 70 turns. Caveat: estimate equalled charge for all 19 workflows [metrics], so the run never tested envelope enforcement.
- Test: tighten the N6 check so defaults like 0 are ignored, and confirm the calculator still shows a usable total before input. Not verified here.
- Gap in this test: lessons memory was off, so the 'save a lesson' step was not exercised. Rerun with memory on.
- Evidence is thin: we see only Audit's tally, not the finding text. The menu highlight and whole-page contrast are covered only by mechanical checks.
