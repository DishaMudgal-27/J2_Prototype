# J2 run report: 20261014-102914

Brief: Make a website for Riverside Run 2027, a city running event in Pune. Runners should be able to compare the three races, work out what they will pay with a fee calculator, register with a form, see the race-day and expo-day schedule, see the route and water stations for each race, read FAQs, and see sponsors by tier. Volunteers should be able to sign up with a separate form. Add a countdown to race day, a menu that stays on screen and shows which section you are in, and a high-contrast mode that works across the whole page. It should feel sporty and clear and work well on phones.

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department delivered a workable site in 2 cycles inside the raised budget (222 of 230), with all 15 done-when items and all 8 necessary conditions met at v23 [145], but about a third of the spend (72 of 222 credits) went on fixing avoidable errors such as invented content.

## Measured (counted by code)
- 64 AI calls, 2 cycles, 31.8 min, model sonnet
- Budget 222/230 (started 200, 1 raise(s) approved by the Requester, cap 400; rate card on), 23 site versions, final site 81 KB
- Negotiation: 3 proposals, 2 GRANT / 1 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 1: 1 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 3 {'limit': 1, 'info': 1, 'fact': 1}
- Validator refusals 1 (role 0), limit failures 0, warnings 13

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 7 | 0 | 0 | 4 | Asked the Requester one clear question about T-shirt sizes instead of guessing [78], and gave a decision-ready budget choice [122]. Drifted from role by prescribing the fix wording ('Choose a race to see your total') [127] and detailed fixes [82]. Also missed the missing size list when recording the charter. |
| Adaptation | 4 | 0 | 0 | 3 | Accepted Priority's counter within 2 attempts [86] and kept fixes small. Did not flag that the registration form needed a size list nobody supplied. The W-1 before W-5 order forced a fallback CTA and a later rework (W-17). The first W-21 proposal was rejected by the validator [128]. Accepted the over-60 KB file [129]. |
| Priority | 24 | 0 | 0 | 4 | Granted 13 at rate-card minimum with a 50 reserve [9]. Its counter was reasoned, but the F-20 it parked came back as F-23 in cycle 2 [85]. It rewrote W-21's steps itself [130], which is design work the role file forbids. 24 near-identical 'within limits' turns. |
| Coordination | 21 | 0 | 0 | 4 | Stated its scheduling rule every time. Holds named the exact missing condition [44]. Ordering W-2 after the section targets avoided a second failed link check [17]. Repeated the same unresolved CTA note about nine times without an owner acting [17, 26, 30, 44, 49, 54, 59, 64, 69]. |
| Audit | 3 | 0 | 0 | 5 | Found the invented sizes, invented badges, fee-form destination, covered countdown labels, and the 'SECONDS' wrap, each with a finding id [77, 121]. Said plainly that high-contrast was checked in code only [145]. |
| W-1 Builder | 1 | 0 | 0 | 3 | Failed the #register link check and used a JS fallback it named as a shortcut [13, 16]. Left a duplicate title and countdown labels that broke at 360px. |
| W-2 Builder | 1 | 0 | 0 | 4 | Clean first attempt [61]. Menu later needed a gallery link, which was not its fault. |
| W-3 Builder | 1 | 0 | 0 | 5 | Clean, supplied facts only [20]. |
| W-4 Builder | 1 | 0 | 0 | 3 | Needed a retry for the submit button [23]. Wrapped the calculator in a form it did not need and was reworked twice (W-16, W-20). |
| W-5 Builder | 1 | 0 | 0 | 3 | Invented sizes S to XXL, though it disclosed this [29], against the 'supplied facts only' rule. |
| W-6 Builder | 1 | 0 | 0 | 5 | Clean, no added times [33]. |
| W-7 Builder | 1 | 0 | 0 | 5 | Clean, placeholders only [37]. |
| W-8 Builder | 1 | 0 | 0 | 4 | Failed the 44px check, then rebuilt with real buttons [40, 43]. Acceptable fix. |
| W-9 Builder | 1 | 0 | 0 | 3 | Added 'Top tier', 'Second tier' and 'Supporters' badges nobody supplied [48, 82]. |
| W-10 Builder | 1 | 0 | 0 | 5 | Clean, correct destination [52]. |
| W-11 Builder | 1 | 0 | 0 | 5 | Clean [57]. |
| W-12 Builder | 1 | 0 | 0 | 3 | Fixed-position toggle covered the countdown labels at 360px [77]. |
| W-13 Builder | 1 | 0 | 0 | 3 | Built the gallery with no menu link. Added a 'Contact the team' link mainly to give the tap-target check something to measure [72]. |
| W-14 Builder | 1 | 0 | 0 | 5 | Sizes fixed first time [111]. |
| W-15 Builder | 1 | 0 | 0 | 5 | Badges removed first time [116]. |
| W-16 Builder | 1 | 0 | 0 | 4 | Removed the form wrapper, but the default total still failed N6 [121]. |
| W-17 Builder | 1 | 0 | 0 | 4 | Static CTA and countdown moved into the hero. Label wrap remained for the next fix [121]. |
| W-18 Builder | 1 | 0 | 0 | 3 | Gallery link added, but its note on highlight order is garbled [101]. Menu order differs from page order [145]. |
| W-19 Builder | 1 | 0 | 0 | 4 | Covering problem fixed [96]. Visual check of high-contrast still missing. |
| W-20 Builder | 1 | 0 | 0 | 5 | Total blank until a race is chosen, rules kept [135]. |
| W-21 Builder | 1 | 0 | 0 | 4 | Labels and title fixed, confirmed by Audit [145]. Its own report only said 'should' [140]. |

## Conflicts (full log in conflicts.json)
- C-1 (cycle 1, proposal): Adaptation vs Priority, 2 attempt(s), resolved by agents. Outcome: Adaptation accepted Priority's COUNTER: T-shirt sizes S, M, L, XL only (8), Remove unsupplied sponsor badges (8), Fee calculator is not a form (8), Hero CTA static to #register, countdown inside hero (8), Menu link to gallery (8), Contrast toggle no longer covers content (8) goes to the validator.

## Audit by cycle
- Cycle 1, v15: 11 pass, 4 warn, 0 fail; mechanical: clean
- Cycle 1, v21: 13 pass, 2 warn, 0 fail; mechanical: clean
- Cycle 2, v23: 12 pass, 3 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- 0 failed workflows, 0 redirects, 0 invalid moves, 0 role refusals. Estimates matched charges on all 21 workflows.
- The Adaptation vs Priority conflict settled itself in 2 attempts, with no escalation [85, 86].
- Code checks caught real defects early: the #register link [13], the missing submit button [23], the FAQ tap target [40].
- Audit stopped three invented-content or layout problems from shipping [77, 121]. Identity asked the Requester instead of keeping the invented sizes [78].

## Problems (reviewer)
- Invented content got in twice (sizes [29], badges [48]) despite the charter rule, and was caught only at the first Audit [77].
- The fix reserve of 50 ran out at v21 with 2 credits left [122]. Rework was 72 of 222 credits (32%) and forced a Requester pause.
- The N6 check flagged Rs 270, which Identity confirmed is correct [127]. This looks like a checker false positive. It forced a UX change (W-20) and extra audit rounds.
- The file grew from 62 KB (v11) to 81 KB against the ~60 KB rule. It drew 13 warnings and no owner acted [53, 129].
- Role drift: Priority rewrote proposal steps [130], where team.md says rejected proposals go back to Adaptation. Identity prescribed the fix text [127]. Code did not catch either.
- Priority and Coordination took 45 of 80 turns for 21 builds, mostly repeated 'within limits' handoffs and the same CTA note.
- High-contrast was judged from code only [145]. W-13 and W-8 added or changed markup partly to satisfy a check [72, 43].
- Lessons were off (memory false, none saved), so the 'save a lesson after a confirmed fix' step went untested.

## Learnings (reviewer)
- Make Identity list missing option lists (sizes) as to-be-confirmed at J2.a, and add a builder rule: report a missing fact to Coordination, do not invent it. Test: rerun with sizes absent and see whether W-5 flags it. Evidence [29, 78].
- Run N6 (no invented content) as a per-workflow code check, not only after the last build. It would have caught W-5 and W-9 at once. Evidence [76].
- Fix the test system's N6 so it allows values derived from the charter's formulas, such as Rs 270. Evidence [120, 127].
- Set the fix reserve from observed rework (about 30% here), not a fixed 50. Test 30% on the next brief. Evidence [122].
- Either enforce the 60 KB limit in the validator (one trim step in W-13) or drop it. Warnings nobody owns are noise. Evidence: 13 warnings.
- Batch Priority and Coordination handoffs when runs are within limits, and keep hold messages. Test: compare turns and AI calls. Savings unmeasured.
- Add a rendered high-contrast check (toggle on, measure contrast) so that done-when item is not verified from code alone.
- Route validator rejections to Adaptation, as team.md says, and keep Priority and Identity from rewriting proposals.
- Evidence is thin: one brief, one run, Sonnet, memory off. Do not generalise the 32% rework or the turn counts.
