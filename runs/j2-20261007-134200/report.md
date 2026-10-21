# J2 run report: 20261007-134200

Brief: Brew Lab, Indiranagar, Bengaluru. One-page site. Must-haves, each one will be checked: today's opening hours are highlighted automatically; the pre-order form shows a running total in rupees; the loyalty section shows 10 stamp circles with the 10th marked FREE; every menu item shows a price; the location section has a "Get directions" link; the page works at 360px wide.

**Outcome:** Done: the site is workable. Every done-when item passes with Audit's evidence and the render check is clean.
**Reviewer verdict:** The department built the site, passed all nine checks in 2 cycles at ₹65 of ₹80 with no redirects or invalid moves, but the only stress, a forced Audit failure, was labelled as a test in the chat, so it tested label reading, not judgment.

## Measured (counted by code)
- 18 AI calls, 2 cycles, 7.0 min, model sonnet
- Budget 65/80 (started 80, 0 raise(s) approved by the Requester, cap 160; rate card on), 4 site versions, final site 25 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 parked
- Conflicts 1: 1 settled by the agents, 0 resolved by Identity from the charter, 0 needed the Requester
- Questions to the Requester 1 {'info': 1}
- Validator refusals 0 (role 0), limit failures 0, warnings 1

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 4 | 0 | 0 | 4 | Asked all four needed questions in one round [2], recorded a charter with nothing to confirm [5], saw the forced failure for what it was [27], and declared done only after Audit's PASS [29][30]. Weak points: it told Adaptation what workflow to propose [27) when a direct re-audit by Audit was cheaper. Its message to the Requester cites a 'forced test failure' and a past-time gap that Audit's chat message never reported [30] (unverified). |
| Adaptation | 2 | 0 | 0 | 4 | Put four workflows in one proposal with a stated trade-off and a ₹15 reserve [7]. Pushed back on a ₹8 fix for a correct section, with a reason and a cheaper path [28]. The rework and lesson-saving duties were never exercised, so there is no evidence on them. |
| Priority | 5 | 0 | 0 | 4 | Granted at the ask and ran a clean envelope check per run [8][11][15][18][21]. It never countered, and the line that 360px overflow must be handled inside each section [8] is a design constraint, not a resource one. Cost judgment can't be assessed because charged equals estimate for all four workflows. |
| Coordination | 4 | 0 | 0 | 4 | Stated the scheduling rule each time and gave the exact HOLD condition [13], lifting it when W-2 finished [17]. The HOLD was cosmetic: lowest-id order already ran W-2 before W-3. It also quoted 'Audit-ready' as a start condition [10][13] yet started W-3 and W-4 before any audit, and dropped the wording in [17]. |
| Audit | 2 | 0 | 0 | 4 | Used headless Chrome plus code reading, gave per-item results and two low warnings [26], and agreed quickly when challenged [29]. [26] says all nine pass while also reporting a NEEDS_REVISION, which is the test override. The re-audit [29] repeats the first verdict with no new evidence, which is fair because site v4 did not change. No sign it checked what the WhatsApp message actually contains (thin evidence). |
| W-1 Builder | 1 | 0 | 0 | 5 | Page shell, viewport tag and menu in one turn, no retry, and it said plainly it was code-reviewed only [12]. Item 2 passed on re-audit [29]. |
| W-2 Builder | 1 | 0 | 0 | 5 | Seven day rows, today-highlight script and the Get directions link in one turn [16]. No warning or failure against it in [26]. |
| W-3 Builder | 1 | 0 | 0 | 4 | Form with live ₹ total, hours check, WhatsApp link and pay-at-pickup message in one turn [19]. Both Audit warnings sit in this section: closing time accepted as a pickup time and the phone placeholder [26]. |
| W-4 Builder | 1 | 0 | 0 | 5 | Exactly 10 circles, 10th marked FREE, free-drink text, 5 per row at 360px [22]. No warning. |

## Conflicts (full log in conflicts.json)
- C-1 (cycle 2, finding): Adaptation vs Audit, 2 attempt(s), resolved by agents. Outcome: Finding F-2 withdrawn.

## Audit by cycle
- Cycle 1, v4: 6 pass, 2 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- One round of questions gave a charter with zero to-be-confirmed items and a first-pass validator accept [2][4][6].
- Clean process: 0 redirects, 0 invalid moves, 0 validator or role refusals, 0 retries, 7 minutes, 17 calls, ₹15 reserve unspent.
- The code check ran before Audit: no overflow at 360 or 1280px, no JS errors, no broken links, 25 KB [24].
- Adaptation and Audit settled the finding in 2 attempts without Identity, and no money went on a needless fix [28][29].
- Builders said honestly that they only reviewed code and had not rendered the page [12][16][19][22].

## Problems (reviewer)
- The forced-fail test announces itself: [25] calls it a test and quotes Audit's real PASS, and [27][28] cite the switch. It shows whether agents read a label, not how they handle a bad finding.
- Conflict C-1 was not a real disagreement; Audit agreed at once [29], so 'settled_by_agents' overstates the negotiation.
- Large parts of the flow ran untested: 1 proposal and 1 GRANT (no COUNTER or REFUSE), no fix workflow, no validator refusal, lessons saved is empty.
- The HOLD on W-3 [13] changed nothing about order; it only caused a ₹25 release and recharge [14].
- Done-when item 4 says to reject times outside opening hours, yet the closing time is accepted [26]. Identity parked it with ₹15 unspent [27][30]. That is defensible, but the item's wording left the edge case open.
- Identity's message to the Requester uses test vocabulary ('forced test failure') [30], which a real client would not understand.
- Metrics look off (unverified): the audit record shows 6 pass + 2 warn + 0 fail = 8 of 9 items, so the overridden item vanished after it was withdrawn. Agent turns sum to 21 against 17 ai_calls.

## Learnings (reviewer)
- Change the test: keep the override out of the agents' chat, or better inject a real defect (for example delete one price from the built site) so the whole fix loop runs: proposal, Priority at ₹8, validator, run, Audit confirm, lesson saved. Evidence: [25][27][28] and an empty lessons list.
- Test next with a tighter budget (about ₹50 against the ₹65 ask) to force COUNTER, park or REFUSE; ₹80 produced a straight GRANT [8]. Add a run that overspends to exercise the envelope stop.
- Test HOLD properly by blocking the lowest-id workflow so Coordination must pick another ready one; here W-2 was next anyway [13].
- Design: have Identity write edge behaviour into done-when items (is closing time allowed, are past times rejected, does a placeholder attribute count as placeholder text). Both warnings [26] came from that ambiguity and Identity ruled on them alone [27].
- Keep: stated scheduling rule, per-run envelope check, and the code render check before Audit. All produced zero redirects. Evidence is thin: one run, one small site.
- Fix the metrics: count an item once its override is withdrawn, define ai_calls versus turns, and count a conflict only when positions differ.
