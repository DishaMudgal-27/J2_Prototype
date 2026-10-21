# J2 run report: 20261005-202237

Brief: A one-page website for Brew Lab, a specialty coffee shop in Indiranagar, Bengaluru: menu with prices, opening hours, location, pre-order a coffee for pickup, a section about our beans and farms, and a loyalty card explainer (buy 9, get the 10th free).

**Outcome:** Done: Identity confirmed every done-when item holds, with Audit's evidence. Open inputs for the Requester (not blocking): Menu items and the price of each; Opening hours for each day; Street address and map pin; Shop WhatsApp number for pre-orders; Pickup slot times and the number of orders the shop can take per slot; Bean origins and farm names for the beans and farms section; Loyalty card details beyond buy 9, get the 10th free, such as which items count.
**Reviewer verdict:** The department finished the site in one cycle (11 calls, 3.1 minutes, 45 of 50 budget, no redirects or validator refusals), but the run was too easy to test its negotiation, ruling or rework paths.

## Measured (counted by code)
- 12 AI calls, 1 cycles, 3.1 min, model sonnet
- Budget 45/50 (started 50, 0 CEO raise(s), cap 100; rate card on), 2 site versions, final site 13 KB
- Negotiation: 1 proposals, 1 GRANT / 0 COUNTER / 0 REFUSE (0 converted by code), 0 withdrawals, 0 conflicts, 3 CEO decisions
- CEO choices 3: picked the option shown first 1, the option Identity listed first 1
- Validator refusals 0 (role 0), pauses 0, limit failures 0, warnings 0

| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |
|---|---|---|---|---|---|
| Identity | 3 | 0 | 0 | 4 | Recorded the charter, sent the CEO real decisions and closed with the open inputs listed [2][4][18]. It bundled three questions into one ASK_CEO, and some options were weak: Q2 options 1 and 2 nearly overlap, and Q3 option 1 (invent facts) was a strawman. |
| CEO | 1 | 0 | 0 | 5 | Picked one option per question, gave a one-sentence reason and named the trade-off [3]. The message is long because it echoes the full options. |
| Adaptation | 1 | 0 | 0 | 4 | One turn, named the shortcut and its cost [6]. It proposed the whole site as two workflows at once instead of the smallest testable first. Estimates equal charges exactly, so their accuracy is untested. |
| Priority | 1 | 0 | 0 | 3 | Gave resource-based reasons and kept 5 in reserve [7]. But it says a fix costs 8, so a 5 reserve cannot fund one. It also told Adaptation how to structure sections (styling inside sections), which is step design, and called a GRANT with a scope constraint. |
| Coordination | 2 | 0 | 0 | 5 | Stated its rule, held W-2 on the shared-file dependency and released it when W-1 finished [9][12]. No role slips. |
| Builder | 2 | 0 | 0 | 5 | Ran both workflows in order, kept W-1 content intact and used TBC everywhere [11][14]. File contents were not shown, so I cannot check drink names or slot labels. |
| Audit | 1 | 0 | 0 | 4 | Honest that the link logic was read, not run [17], and mechanical checks ran at 360px and 1280px [16]. Item 5 passed with a warning even though the button is disabled while the number is TBC, which is lenient against the done-when wording. |

## Conflicts
- None

## Audit by cycle
- Cycle 1, v2: 9 pass, 1 warn, 0 fail; mechanical: clean

## What went well (reviewer)
- Clean run: 0 redirects, 0 invalid moves, 0 validator refusals, 0 stuck, 0 failed workflows.
- No invented facts: the CEO chose TBC placeholders [3], the Builder used them [11][14], and Audit passed item 10 [17].
- Single-writer rule on brewlab.html was applied and explained [9][12].
- Identity did not block done on Requester-only facts and listed the 7 open inputs [18][19].

## Problems (reviewer)
- Negotiation, conflict, Audit-failure and rework paths were never exercised: 0 counters, 0 refusals, 0 conflicts, 0 findings above warning. The design is only proven for the easy case.
- Cost accuracy is unmeasured: estimate equals charge for both workflows (25/25, 20/20) and rate_card is true.
- Priority's reserve logic is inconsistent: 5 held back against an 8 fix [7].
- The CEO's chosen option 3 says the Requester confirms before done [3], but the charter makes open inputs non-blocking and the run ended Done with none supplied [19]. The site cannot go live yet.
- Item 5 and item 7 pull against each other (button should open a link, number must stay TBC). The WhatsApp flow was never run, so this rests on a code read.
- Mechanical check does not test that TBC tags are visible or scan for stray prices, hours or phone numbers. Items 8 and 10 rest on a code read.
- 2 of 11 calls went on Coordination relays for a strictly linear two-step plan.
- CEO position bias cannot be judged from 3 choices (1 shown-first, 1 Identity-first).

## Learnings (reviewer)
- Keep: TBC tags plus non-blocking open_inputs. It produced zero invented facts.
- Test next: a tighter budget (for example 30) so Priority must counter or refuse, with variable charges so estimates can diverge.
- Test next: a Requester change request after Done, which this run never reached.
- Add mechanical checks: render and confirm TBC visibility, scan outside TBC tags for digits, rupee signs and phone patterns, and run the order link builder with a dummy number.
- Reword done-when item 5 to say the button builds the link and stays disabled while the number is TBC, so Audit has a clean criterion.
- Change Identity's CEO questions: one decision per ASK_CEO, distinct options, no strawmen, and option text must match the charter on what blocks done.
- Give Priority a stated reserve rule (reserve at least one fix cost) and keep it out of workflow structure.
