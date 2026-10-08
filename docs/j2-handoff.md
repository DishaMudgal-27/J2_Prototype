# J2 handoff (updated 8 Oct 2026)

Start a new Claude chat, connect the agent-studio folder, and say:
"Read docs/j2-handoff.md in my agent-studio folder and continue from there."
(The round 1 handoff is kept as docs/j2-handoff-round1.md.)

## Who / what
Disha (intern, Testlify) builds and tests a prototype of **J2**, a multi-agent "department" designed by her manager
(Sankalp). Diagram: docs/j2-flow.jpg. J2 page: https://sankalpasawa.github.io/asawa-site/native/system/department.html
Agents: Identity, Adaptation, Priority, Coordination, Audit (official md files in agents/j2/, NEVER edit them),
plus one builder agent per workflow; validator is plain code. No CEO: only Identity talks to the user.
The prototype builds a website from a user's brief. Claude Code (in the project) does all code changes;
this chat plans, writes prompts for Claude Code, reads runs and writes reports.

## Documents (Claude Docs)
- Round 1 findings (already shared with manager): https://claude.ai/code/artifact/4503e532-d714-45ad-9cdc-5b3872fb533d
- Round 1 proposed solutions: https://claude.ai/code/artifact/f6201d73-93a9-4a24-b4e4-f2dd7759ad29
- Round 2 findings (after changes, 7 Oct runs): https://claude.ai/code/artifact/f09ff16a-ea7f-4b9f-b6a0-f565fe27c312
Label findings: J2 design / Agent behaviour / Prototype.

## What the build has now (all in git; Claude Code commits before and after every change)
- Identity asks for real facts (no silent placeholders); user may choose "leave for later".
- One builder agent per workflow; loop J2.b -> J2.h until the site is workable (browser checks).
- Limits ask the user via ONE code-applied decision question: add budget (preset or typed amount), leave items out,
  or finish as is (ends as done_with_open_items). Budget cap = 2x start budget. (commit 94a9a6c, NOT yet live-tested)
- Pricing tied to work: each done-when item has a minimum cost; fixes priced as fixes; unpaid items flagged.
- Adaptation memory: lessons + playbooks (same business type only). J2_MEMORY=0 turns off. Tests use temp folders.
- Style guide + design rubric (screenshots) in Audit. Generalist (cafe, florist, clothing tested).
- Simple view (default, plain language, "Your website team") + Detailed view ("See how it works").
- Test switches: J2_FORCE_AUDIT_FAIL=<n> (hidden from agents), J2_MEMORY_TEST_LESSONS=1.

## How to run (Mac Terminal)
    cd ~/Downloads/agent-studio
    lsof -ti :8773 | xargs kill        # only if "Address already in use"
    source .venv/bin/activate && J2_FIXES=0 J2_BUDGET=40 J2_MEMORY=0 STUDIO_PROVIDER=claude-cli J2_DELAY=0 python3 j2_server.py
Open http://127.0.0.1:8773/ . Sharing: second tab `cloudflared tunnel --url http://127.0.0.1:8773` (temporary link,
uses Disha's Claude subscription, single user at a time, stop with Ctrl+C).
Rules: use only fake numbers starting +91 00000 (a made-up number once hit a real person). Never delete runs/ (evidence).

## Standard test: clothing shop, low budget
Brief: "make a website for my cousin's clothing boutique called Thread & Loom in Pune. it sells handloom kurtas, sarees,
cotton shirts and dupattas. people should be able to browse products by category, filter by size and price, see a size
guide, check new arrivals, and order on whatsapp. also show a lookbook section with styled outfits, the store timings and
location, the return and exchange policy, and a few customer reviews. it should feel earthy and elegant and work well on phones"
Details: WhatsApp +91 00000 11111, phone +91 00000 22222, 18 FC Road Shivajinagar Pune 411005, 11am-9pm Tue-Sun closed Mon,
exchange 7 days unworn with tags; 10 products (kurtas 1,499/1,699/2,199; sarees 3,499/4,999/3,999; shirts 1,299/1,599;
dupattas 899/1,099); size guide XS32..XXL42; 3 reviews; lookbook 3 outfits; delivery Pune 2 days Rs79, free above 2,999.

## Key findings so far (round 2 + 8 Oct)
- Budget bundling/relabelling (fixed by pricing-to-work; confirmed live 8 Oct: conflict now happens and reaches user).
- User decisions were ignored when Identity asked in free form -> stuck loops (runs 20261008-110419, -123848). Fixed in 94a9a6c.
- Identity mixes audiences: messages to the user start with @Adaptation/@Audit; agent instructions leak to the user.
- Memory had 109 mock playbooks polluting it (cleaned); live playbook reuse not yet proven.
- Reserve for fixes inconsistent; Audit reads code more than it tests behaviour in the browser.

## NEXT STEPS
1. Live check of 94a9a6c: clothing test at budget 40. At the money question type
   "Add 25 more. Leave out the lookbook, new arrivals and reviews." (expect 40->65, items never return);
   next time choose "finish as is" (run must end, no repeat question).
2. If OK, send Claude Code the SECOND PASS (manager's 8 Oct asks):
   - to_requester / to_agents split for every Identity reply (user never sees @Agent text); Simple view strips any leading @Agent.
   - Simpler user messages: max 3 short sentences + one question, max 3 options, question shown once, no jargon.
   - Owner override: J2_OVERRIDE_KEY in .env (never committed/shown to agents, redacted); "<key> budget +N" ignores cap,
     "<key> ship", "<key> drop <item>"; visible "Owner override applied" note.
   - Site bug: order form had no submit button (run 20261008-123848 msg 46); browser check must fail on it.
   Mock tests, full suite, commit before/after.
3. Prove memory: same florist brief 3x with J2_MEMORY=1, compare Playbooks tab.
4. Test a non-shop site (college fest) for question quality.
5. Deployment: needs company Anthropic API key + hosting account (manager said ok if not too much effort; Tesla team can help).
6. Update round 2 doc / write round 3 findings after these runs.

## Risks and corrections (added 8 Oct, read before writing prompts)
- Never create or overwrite .env in the project (it holds J2_OVERRIDE_KEY). Hook tests go in a throwaway temp repo.
- The "sent back twice at most" rule is J4 on the department page, not J2. J2's bargain limit is four hops, fifteen minutes and its spend.
- Keep decisions with the agents: add rules the validator enforces, do not hard-code agent choices in code.
- J2 is judged against versions.html: v1 FOLLOW (20 runs, pass rate visible) and v2 REMEMBER (interrupts halved). Log questions asked to the user and pass/fail per run.

## Status (8 Oct, later)
- Step 1 part A passed live (run 20261008-131555, 40 -> 65, dropped items never returned). Part B ("finish as is") NOT yet tested; that run is paused in the old server's memory (port 8773).
- Second pass (two audiences, simple messages, owner override, form submit button) committed as 6f978af. Full mock suite green.
- .env.example not yet committed: pre-commit hook blocks any .env.* file. Prompt 1 (allow exactly .env.example) pending.
- Third pass pending: nav fix rejected as 'styling' (should be 'fix'); fund blocking fixes before optional sections via a validator rule; check-only report on loop and bargain limits.
- After that: live clothing test on new code, grep runs/ and logs for the key value, then steps 3 to 6 above.
