# J2 run report: 20261008-190919

Brief: make a website for my friend's south indian restaurant called Kaveri Kitchen in Pune. people should be able to see the menu with prices, filter it by veg and non-veg, see today's specials, book a table on whatsapp, find the address and opening hours, see photos of the dishes, and read a few customer reviews. it should feel warm and homely and work well on phones

**Outcome:** Done with open items: shipped as is on the Requester's decision (Cycle 1 used 30 turns (the per-cycle cap) without finishing.). Still not workable: .
**Reviewer verdict:** The department built a site that meets all 10 done-when items with no conflicts, but the 30-turn cap fired after Audit had already found the site workable, so a finished run was labelled unfinished and the Requester got an unneeded question.

## Measured (counted by code)
- 26 AI calls, 1 cycles, 8.3 min, model sonnet
- Budget 105/200 (started 200, 0 raise(s) approved by the Requester, cap 400; rate card on), 9 site versions, final site 31 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 0: 0 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 2 {'info': 1, 'limit': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 3 | Good first question [2] and clean charter [6]. But [6] dictates implementation ('one easy-to-edit list'), which its role forbids. [41] offers 'more of the missing parts' when Audit [40] found none missing, and Identity never declared J2.h done itself. |
| Adaptation | 1 | 0 | 0 | 4 | One message [8] with nine section-sized workflows, ordered shell first and styling last, all facts from the charter. Stayed in role. Nine may be more than needed (see learnings). Whether the proposals met the required format is not visible in the chat. |
| Priority | 10 | 0 | 0 | 4 | Granted all nine in one pass [9] with a reason (rate-card minimum, 95 in reserve). Envelope checks [12] to [36] were in role. It never countered or refused, so its bargaining is untested. 10 turns, 9 of them routine. |
| Coordination | 9 | 0 | 0 | 4 | Stated its rule every turn and kept dependency order (W-1 first, W-9 last). No holds were needed. 9 near-identical turns, partly because the single write lock forces one writer at a time. |
| Audit | 1 | 0 | 0 | 4 | Checked each item against the file and the mechanical results [39], and named the duplicate <title> and <meta charset> as the one warning [40]. It did not name which section caused it, and the defect shipped. |
| W-1 Builder | 1 | 0 | 0 | 5 | Title, viewport, header and six-link nav [13]. Link targets resolved later (no broken links per [39]). |
| W-2 Builder | 1 | 0 | 0 | 5 | 11 dishes at charter prices; counts All 11, Veg 8, Non-veg 3 [16] match the charter. |
| W-3 Builder | 1 | 0 | 0 | 5 | Mysore dosa and Fish curry meal at menu prices, no offer wording [19]. |
| W-4 Builder | 1 | 0 | 0 | 5 | wa.me link with prefilled message and '1 to 8 people' [22]. Audit passed it. |
| W-5 Builder | 1 | 0 | 0 | 5 | Six empty labelled photo spots, no images [25], as the rules require. |
| W-6 Builder | 1 | 0 | 0 | 5 | Exactly the three reviews, no ratings added [28]. |
| W-7 Builder | 1 | 0 | 0 | 5 | Address, hours, kitchen close and tel link all match the charter [31]. |
| W-8 Builder | 1 | 0 | 0 | 4 | Footer repeats address and hours, which no done-when item asked for. Checked banned words by reading the file [34]. |
| W-9 Builder | 1 | 0 | 0 | 5 | Scoped CSS with overflow guards and tap targets [37]. The mechanical check [39] confirms no overflow at 360px or 1280px. |

## Conflicts (full log in conflicts.json)
- None

## Audit by cycle
- Cycle 1, v9: 9 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Identity collected every missing fact in one round [2][4], so no facts were invented and to_be_confirmed ended empty.
- Zero validator refusals, role refusals, redirects or retries across 34 agent turns.
- The code-run mechanical check [39] gave real evidence (overflow, JS errors, links, 117 contrast checks) after builders admitted they had not run a browser.
- Spend was 105 of 200, and each workflow was charged exactly its estimate.

## Problems (reviewer)
- The cap event [41] fired after Audit said workable [40]. The outcome text says 'Still not workable: .' with an empty list, which contradicts the audit data (all_pass true).
- The Requester was asked 'keep going or finish' [41] when nothing was missing.
- Duplicate <title> and <meta charset> shipped. The chat does not show whether the cause is W-1 or the assembler.
- Envelope checks report 'model calls 0/N' [12] to [36] although builders ran. Cause not visible; treat as unverified.

## Learnings (reviewer)
- Fix the turn cap. Turn counts by agent sum to 34 against a cap of 30, and 19 turns were Priority and Coordination envelope checks (9 each, plus the grant). Scale the cap with workflow count, or run routine envelope checks in code and skip counting them. Test: same brief with a cap of 45, expecting a clean finish.
- Do not let the cap override a code-confirmed pass. If Audit is all_pass and mechanical checks are clean, report done. Also fix the outcome string that printed an empty 'Still not workable' list.
- Test fewer workflows. Nine serial workflows cost 18 routine turns for a 31 KB page. Try 4 to 5 (shell, menu and specials, booking and contact, photos and reviews, styling) and compare turns and Audit results. This is a hypothesis; this run cannot show it.
- This brief was too easy to test the design. Conflicts, counters, refusals, holds and lessons were all zero. Next runs: a budget below the 105 estimate, a brief with a missing fact, and one request that breaks a rule.
- Check where the duplicate head tags come from (assembler or W-1) and make the mechanical check fail on them, since Audit only warned.
- Keep the up-front Identity question and the code mechanical check.
