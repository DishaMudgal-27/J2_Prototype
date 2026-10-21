# J2 testing: handoff summary (6 Oct 2026)

Paste this into a new chat, or point Claude at this file (docs/j2-handoff.md in the agent-studio folder).

## Goal
The developer (intern, Testlify) is testing **J2**, a multi-agent flow designed by the project owner (diagram: docs/j2-flow.jpg),
using a prototype that builds a cafe website. The output is a findings report for the project owner, focused on
**how conflicts are resolved** and **budget**. Findings are about the J2 concept, not prototype bugs.

Two Claude Docs are already started (outlines only, finish after all tests):
- Findings: https://claude.ai/code/artifact/4503e532-d714-45ad-9cdc-5b3872fb533d (summary section drafted)
- Proposed solutions: https://claude.ai/code/artifact/f6201d73-93a9-4a24-b4e4-f2dd7759ad29

Label every finding as one of: **J2 works** / **J2 needs improving** (concept gap) / **prototype bug** (appendix only).

## Rules agreed with the project owner / head
- Agents: Identity, Adaptation, Priority, Coordination, Audit (official md files in agents/j2/, do not edit), plus Builder.
  Validator (J2.e) is plain code, no AI call: "the final check before anything is built".
- No CEO (head confirmed). Official md files still mention a CEO; team.md says Identity asks the user instead.
- Only Identity talks to the user. Agents argue up to **4 attempts (4 messages)**, then go to Identity, which rules from the
  charter or asks the user one question with options.
- J1 is out of scope.
- Budget = made-up units from a rate card (5 = cheapest part), not money or tokens. Real cost = ai_calls in summary.json.

## How to run (Mac Terminal, in ~/Downloads/agent-studio)
    J2_FIXES=0 J2_BUDGET=<n> STUDIO_PROVIDER=claude-cli J2_DELAY=0 python3 j2_server.py
- J2_FIXES=0 = baseline (close to diagram). J2_FIXES=1 = fixes: Identity ruling repriced once by Priority;
  change requests after done go via Identity J2.a.
- Answer Identity with the option number only. Ctrl+C between runs.
- Each run saves runs/j2-<time>/ with chat.jsonl and summary.json.
- Prompts/briefs: docs/j2-prompts.md. Test plan: docs/j2-test-plan.md.
- Mock tests: j2_flow_test.py, j2_check.py (Claude Code runs these).

## Live runs so far
| Run | Test | Mode | Budget | Result | What it shows |
|---|---|---|---|---|---|
| 123218 | T1 | 0 | 200 | stopped, 90 used | All done-when passed but Identity refused "done" over a 10px phone overflow; run stopped instead of reworking (diagram says J2.h No -> J2.b) |
| 124308 | T2 | 0 | 100 | done, 70 used | Identity asked twice, invented nothing; "done" declared on placeholders |
| 125414 | T6 | 0 | 50 | done, 50/50 | Agents settled in 2 attempts by trimming; 0 reserve, 0 retries; known bug shipped |
| 130411 | T6 | 0 | 35 | stuck | User approved a budget raise, ledger never updated (bug); Identity claimed "budget is 60" while ledger said 35; stuck check worked |
| 132605 | T6 | 0 | 35 | done, 40 | Agents dropped core pre-order to keep gallery+stories; user asked 4 times for one decision (A/B vs 1/2 bug); raise applied after "1" |
| 134820 | T6 | 1 | 35 | out of budget, 58/58 | Core features funded first this time; raise +23 applied; user dropped gallery but done-when not updated, so run could not finish |
| 140038 | T5 | 0 | 70 | done, 60/70 | Identity resolved video vs speed at charter stage (tap-to-play middle ground); no conflict, J2.d not reached live |
| 154229 | T11 | 0 | 100 | done, 85/100 | No conflict at all: missing farm coordinates became placeholders, so Coordination never HOLDs and Audit raised nothing on warmth; 1 route-check (Builder named no one); no summary.json written |
| 155146 | T3 | 0 | 60 | out of budget, 60/60 | No counter loop: Adaptation proposed core only (menu/hours/location + pre-order with payment) and Priority granted at once, 0 reserve. Page overflowed (34px phone, 21px desktop) and could not be fixed. Identity wrote its budget/scope question to @Adaptation instead of the user; route check redirected it and the out-of-budget stop ended the run before the user was ever asked. Identity said it had not seen Audit's F-13/F-14 text. |

Mock runs (j2-20261006-1222xx) cover: J2.d ruling blocked by validator in baseline, repriced and built in fixes mode,
ruling using up the fix budget, route-check redirect.

## Findings so far
**J2 works**
- Identity as the single contact; other agents redirected when they address the user.
- J2.a: asks when brief is vague, uses placeholders, never invents facts.
- Escalation ladder: most conflicts settled by agents; only real trade-offs reach the user as priced options.
- Identity refuses to change the budget itself; code blocks overspending; stuck/out-of-budget stops cleanly.
- Identity can find middle grounds early (T5 tap-to-play video).

**J2 needs improving**
1. J2.d -> J2.e has no pricing step: ruling is blocked (baseline) or can overspend / starve Audit fixes.
2. Spending starts before the full scope is checked against budget (T6@35: 30 of 35 spent first).
3. No core vs nice-to-have marking: agents dropped pre-order in one run, kept it in another (same brief, same budget).
4. No fix reserve rule: Priority sometimes keeps 30 spare, sometimes 0; known bugs ship.
5. Estimates vary: same brief priced 60 vs 80; Priority corrected its own price mid-run.
6. "Done" = sections exist, not real content (placeholders pass).
7. User decisions don't amend the charter/done-when (T6 fixes: dropped gallery blocks "done").
8. Unclear whether Identity may judge beyond done-when (T1), and J2.h "No" should loop to rework.
9. Identity resolving at charter stage is not in the diagram.
10. "Hold, wait" loop has no limit; official md files still mention CEO.
11. Budget units not tied to real cost (AI calls/tokens).
13. No path to ask the user for budget once it is spent: at J2.h with failing items and 0 budget, the run stops instead of Identity asking (T3). The diagram only has "request approval" at the envelope step.
14. Identity does not see Audit's full findings (T3: F-13, F-14 not ruled on).
12. Placeholders defuse conflicts: missing inputs never trigger Coordination's HOLD or a dispute (T11), so done is declared with key inputs (map coordinates) still missing.

**Prototype bugs (appendix)**
- Budget raise not applied (fixed). A/B vs 1/2 answer labels; budget question without amount tag (fix prompt sent / to send to Claude Code).
- Identity can claim state changes it cannot make (left as a finding, not fixed).

## Remaining tests (all planned tests done)
- T11 done (no conflict, see table). Other-pair conflicts are covered by mock runs only.
- T3 done (no counter loop, see table).
- Optional: T5 with J2_FIXES=1.

## After tests
Read all runs (runs/ folder), then fill both docs:
Findings doc: Summary, How tests were run, Conflict findings path by path, Budget findings, Baseline vs fixes, Other findings, Appendix (bugs + coverage table: live / mock only / not tested).
Solutions doc: ranked changes for conflicts, budget, done-when/charter, diagram and md files, what to test next.
