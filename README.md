# Agent Studio: three agents and a user build a website together

Product, Design and Development share one group chat with the user. Tell them what
you want ("I want a hospital website") and they ask questions, plan, get your
approval, build, review each other's work, and take change requests.

## Run

```bash
pip install -r requirements.txt
# Paste your key into .env (GEMINI_API_KEY= or ANTHROPIC_API_KEY=), or export it in the shell.
python server.py                  # opens http://127.0.0.1:8770
```

No key? `STUDIO_MOCK=1 python server.py` runs scripted agents. Add `STUDIO_MOCK_DELAY=4` to make each
mock reply stream over 4 seconds, so you can see the progress UI. The mock is written
for the hospital demo; real mode handles any kind of website.
If both keys are set, Claude is used. Claude defaults to `claude-sonnet-4-5`
(override with `ANTHROPIC_MODEL`); Gemini tries `gemini-3.8-flash`, then `gemini-3.5-flash` if busy (override
with `GEMINI_MODEL`, a comma-separated list). On Gemini's free tier, Google may use prompts to improve its
products, so don't send real customer data through a free key.

## The agents

| Agent | Job | Output |
|---|---|---|
| Product | Talks to the user, writes the brief, **decides who speaks next** | Brief (JSON), routing |
| Design | Turns the brief into a spec; reviews every built version | Palette, fonts, sections; review with issues |
| Development | Builds the site as one HTML file; applies fixes and user changes | `site/vN.html` |
| User | Answers questions, approves the plan, asks for changes | |

## How they communicate

- **One shared chat.** Every agent reads the full conversation plus the current
  brief, design spec and latest site, so nobody works without context.
- **Product moderates.** After each message Product picks the next speaker
  (`user`, `design`, `development` or `done`). Agents never talk over each other.
- **Design and Development talk directly.** Either can ask the other one question when blocked
  ("@Design, menu as tabs or one list?"); the answer goes straight back, with no Product hand-off.
  At most 2 questions per user message. Development can push back on a review issue in its
  message, and Design's next review accepts the reason or insists with one.
- **Fixed hand-offs skip the model.** When only one next step makes sense (spec → plan to
  the user, build → Design review, review → fix or deliver), code posts Product's message
  and routes it. Product's model is only asked after the user speaks. This cuts a full run
  from about 19 calls to 12 (mock run, hospital demo); the spec check adds 1, and each
  teammate question adds 2. Those messages are tagged
  "routed without an AI call" in the chat.
- **Messages use @names** (`@Design, please review v1`) so the chat reads like a real team.

## The flow

1. User gives a brief → Product asks 2-3 questions
2. Product writes the brief → Design proposes a spec → Development checks it can be built
   (once per project; if not, Design revises)
3. Product shows the plan → **user approves** (or asks for changes, which go back to Design)
4. Development builds v1 → Design reviews it
5. Issues? Development fixes (or pushes back with a reason) → Design reviews again (max 2 rounds)
6. Product delivers → user asks for changes or says done

## Guardrails (enforced in code, not left to the model)

- No building before the user approves the plan.
- At most 24 agent turns per run and 2 Design ↔ Development fix rounds.
- The user can't type while an agent is working, so turns never collide.

## Seeing what the agents are doing

- A step tracker under the header: Questions → Brief → Design → Approval → Build → Review → Delivered.
- Under the chat, the working agent's task, seconds elapsed, and reply size so far. For Development
  it also shows the section being written, and for edits a bar comparing size with the previous version.
- The preview shows the page as Development streams it, refreshed every 2.5 seconds.
- Retries and model switches (for example "gemini-3.8-flash is busy (503), trying the next option")
  appear in the status line and are no longer silent.

## Speed settings

- Replies are streamed, so progress is visible and long Development replies don't block.
- Product and Design use a small Gemini thinking budget (512 tokens); Development keeps full thinking.
- On a 503 or 429, the next model in `GEMINI_MODEL` is tried at once; one 4 s pause, then one more
  round, then the error is shown.

## Files

- `agents/*.md`: each agent's rules (`team.md` is shared by all). Edit these to change behaviour; changes apply on the next message, no restart
- `studio.py`: the three agents, their reply formats, the moderator loop and the gates
- `server.py`: local web server and API (`/api/state`, `/api/say`, `/api/reset`, `/site/vN`, `/site/live`)
- `ui.html`: group chat on the left; Preview, Brief, Design and Code tabs on the right
- `mock_site.py`: scripted site used only in mock mode
- `projects/<timestamp>/`: `transcript.jsonl`, `brief.json`, `design.json`, `site/v1.html…`

## Known limits

- Gemini free tier allows 20 requests per day per model (seen on 2026-09-29). A full
  run takes about 6-12 calls, so expect roughly one site a day on a free key.

- Tested end to end in mock mode only. With a real key, a very large site can hit
  the 16k-token output limit for Development.
- One project at a time; no login; the site is a single HTML file.

## Conflict demo: budget negotiation with a CEO

`python negotiate.py` runs a separate, terminal-only demo. Marketing, Engineering and Sales split a
$10,000 launch budget. Each has a private minimum, and the minimums add up to more than the budget, so they
have to argue. Nothing is scripted: each turn the speaking agent reads the whole chat and decides to
propose a split, accept, reject, or escalate, and who speaks next.

- They settle it themselves if all three accept the same split.
- Escalation to the CEO unlocks after 6 turns; after 10 turns without agreement the CEO is called anyway.
- The CEO picks a middle ground with conditions. Each agent accepts with a plan or objects once;
  objections get one final ruling from the CEO.
- Code enforces only the limits: splits must add up, no early escalation, the turn cap.

**Live web page:** `python negotiate_server.py` opens http://127.0.0.1:8771. Press Start to watch the chat,
the split on the table against each department's private minimum, the CEO's reserve, and the final decision.
Offline preview: `STUDIO_MOCK=1 STUDIO_MOCK_DELAY=1 python negotiate_server.py`.

Edit `scenarios/budget.json` (goal, budget, roles, private goals, limits) or `scenarios/rules.md`, or pass
another scenario: `python negotiate.py scenarios/mine.json`. Output goes to `runs/<timestamp>/`
(`transcript.jsonl`, `summary.md`). A run takes about 10-16 short model calls. `STUDIO_MOCK=1` uses simple
rule-based agents for an offline check. Live runs pause 4 s between calls to stay under the free tier's
per-minute limit (`NEGOTIATE_DELAY=3` to change it).

## J2 mode: J2 agents build a website in a group chat (test of J2, no Sutra)

```bash
source .venv/bin/activate
STUDIO_PROVIDER=claude-cli python j2_server.py   # opens http://127.0.0.1:8773, runs on your Claude subscription
python j2_server.py                              # same page, uses the API keys in .env instead
STUDIO_MOCK=1 python j2_server.py                # offline demo, scripted agents
```

The page opens in the **Simple view**, made for someone who knows nothing about agents (screenshots in
`docs/ui-simple-*.png`):
- **Layout:** chat on the left, a large preview of the site on the right. On a phone the preview stays hidden
  until a site exists; then a "Chat | Preview" toggle at the top shows one at a time.
- **One voice:** only the messages addressed to you, from one assistant called "Your website team". No agent
  names, @mentions, step codes or internal messages.
- **Plain words at the source:** every Identity prompt says that anything written to you must suit a college
  student with no tech background: no internal terms, at most two short sentences of context, and each option
  says what you get and what it costs ("Add a section about your coffee's story (takes a bit longer)" / "Keep
  it simple, no story section").
- **Word list (fallback only):** a word list in the page rewrites whatever still slips through. Function names
  become "the team", Audit becomes "our checks" (so never "after the team"), budget becomes "effort". There are
  no model names, AI-call counts, cycles or badges. When the effort runs out it asks "This needs a bit more work
  than planned. What would you like to do?" with Continue (uses a little more effort) / Skip … / Finish as it
  is.
- **Progress:** a 5-step bar above the chat (solid background, so messages never show through it) (Understanding your request, Planning, Building, Checking, Ready),
  plus one friendly line while the team works, e.g. "Building your menu section…".
- **Questions:** a question with options is shown once, followed by its buttons, so you never type an option
  number; a text box is there for your own answer.
- **Start screen:** example briefs as cards: a cafe, a bakery, a florist and a photographer.
- **When done:** "Your website is ready" with Open full screen, Download the HTML file and Ask for a change.
- **Errors:** a plain "Something went wrong. Try again."; the details stay in the Detailed view.

"See how it works" (top right) opens the **Detailed view**: everything described below, and "Back to simple
view" from there. The choice is remembered in the browser, and `?view=simple` / `?view=detail` in the URL
picks one. The Simple view only changes how the run is shown; the agents and `j2.py` behave the same in both.

You type the brief as the Requester. The flow follows `docs/j2-flow.jpg` and the
[J2 page](https://sankalpasawa.github.io/asawa-site/native/system/department.html) (J2.a to J2.h). Only Identity
talks to you. The run pauses until you answer.

| Participant | File | Job |
|---|---|---|
| Identity | `agents/j2/identity.md` (official) | J2.a: asks until it has enough, records the charter; J2.d: resolves conflicts; J2.h: is the site workable? |
| Adaptation | `adaptation.md` (official) | J2.b: proposes workflows, reads lessons; disputes an Audit finding or a HOLD; saves lessons |
| Priority | `priority.md` (official) | J2.c: GRANT / COUNTER / REFUSE within the budget; checks each run's envelope |
| Coordination | `coordination.md` (official) | J2.f: schedules registered work, holds the write lock on the site file |
| Audit | `audit.md` (official) | J2.g: files PASS / NEEDS_REVISION findings against the done-when list, all to Identity |
| W-1 Builder, W-2 Builder, ... | `builder.md` (placeholder) | One agent per registered workflow; writes only its own section of the site |
| Validator | code in `j2.py` | J2.e: checks the charter and each workflow (cost, outputs, budget), creates the workflow's agent |

`team.md` and `builder.md` are our placeholders (marked at the top); the other five are the official files and
are never edited by this code.

### The loop

1. **J2.a** Identity asks as many rounds as it needs; there is no round cap. It works out what kind of business
   this is and what its visitors usually need: a florist's visitors browse, order and check delivery, and a
   photographer's look at the portfolio, packages and booking. Unless the brief already says it, Identity lists
   those needs and asks you to confirm or change them. The charter records `business_type` and the confirmed
   `visitor_needs`. A fact only you know is a question to you. If you can't give it yet, Identity records it as **to be confirmed** against its done-when item. That
   item is not met: Audit's result for it is forced to `TO_BE_CONFIRMED` by code.
2. **J2.b** Adaptation proposes workflows. With memory on it gets the 5 most relevant lessons and, on the first
   proposal for a brief, the playbooks of similar businesses. It says which one it used and what it changed.
3. **J2.c** Priority prices them. The bargain is bounded by **four hops, fifteen minutes and its spend**. Past
   any bound, both final positions go to Identity (J2.d).
4. **J2.e** The validator registers each agreed workflow and creates its agent, e.g. "W-3 Builder", with the
   workflow's goal, outputs, completion check and envelope.

   **Cost follows the work, not the labels.** Each workflow lists `covers` (the done-when items it builds) and
   `fixes` (the Audit findings it fixes). The validator rejects a workflow that breaks any of these rules:
   - It is priced below the rate-card minimum for the items it newly covers. Each item's minimum comes from its
     kind: a form or ordering item is `form` (15); a filter, search or slider item is `interactive_feature`
     (10); a viewport or phone-layout item is `styling` (5); anything else is `page_section` (10).
   - It is a fix (it lists findings, or rewrites an earlier section) without one `fix` part per finding. A fix
     can't be relabelled as a cheaper part.
   - It covers nothing but has `page_section` or `form` parts, or it covers nothing and fixes nothing after the
     first Audit.

   Items an earlier workflow already paid for aren't charged again. Priority sees each proposal's cost per
   covered item against those minimums and is told to question plans far below them. Each workflow agent is told
   to build only the items it covers.

   Audit checks this on the page too. A done-when item that passes although no built workflow paid for it gets
   the verdict `UNPAID`, a normal finding that loops back. An item counts as paid if a built workflow covers it,
   or fixed a finding on it. A workflow that covers the item at its rate-card minimum makes it paid. This came from `runs/j2-20261007-190411`, where 13 items cost 35 at
   budget 40: everything was bundled into two workflows, and a fix (8) was relabelled as styling (5).
5. **J2.f** Coordination schedules and holds the write lock. Priority checks the envelope. The workflow's agent
   writes its marked section (`<!-- J2:W-3 start (owner W-3) -->` ... `end`, plus an optional head block).
   **Style guide:** the first workflow that runs also writes the style guide for this brief before its section
   is accepted: palette, fonts, spacing, button and card styles suited to the business. Without it the reply
   is retried within the envelope. Code turns it into CSS variables (`--j2-primary`, `--j2-font-body`, ...) and
   the classes `j2-btn`, `j2-btn-secondary` and `j2-card`, first in the page head. Every later workflow agent
   gets the guide and is told to follow it. Values that could break out of CSS or HTML are refused.
   An unusable reply is retried within the envelope's call and retry limits. Then the agent reports to
   Coordination. A workflow with `"revises": "W-2"` rewrites W-2's section and becomes its owner. Code
   assembles the file from the sections, in registration order.
6. **J2.g** Audit checks the site and files every finding (all IDs and text) to Identity. A finding can name a
   fact only you know; Identity then asks you for it. Audit also judges the **design and usability rubric**:
   - R-1 consistent styling (follows the style guide)
   - R-2 readable contrast (WCAG AA)
   - R-3 clear hierarchy (one h1, headings in order)
   - R-4 one obvious main action
   - R-5 easy navigation
   - R-6 tap targets at least 44x44px on phones (`J2_TAP_MIN`)
   - R-7 alt text on images

   In live runs Audit sees a screenshot of the first screen at 360px and 1280px side by side. Code measures
   contrast, headings, tap targets (links inside text are exempt) and images without alt, so Audit can't pass an
   item code measured as failing. A failing rubric item is a normal finding that loops back.
7. **J2.h** Identity: is the site **workable**? If not, back to J2.b. This repeats until it is workable.

**Workable** is decided by code (`workable()` in `j2.py`), not by a model:
- every done-when item passes Audit
- every design rubric item passes
- no JS errors
- no horizontal overflow at 360px and 1280px
- every form submits (`j2_check.py` fills each form with sample values and submits it)
- no broken in-page link
- no done-when item marked to be confirmed

If Chrome isn't found, the render checks can't run, so the site is never called workable.

**Limits never stop a run silently.** Identity asks you to keep working, drop the failing items or ship as is
when one of these is hit:
- the budget (less left than the cheapest rate-card part)
- `J2_MAX_CYCLES` (default 6)
- the same failure twice in a row (same failing items and render problems in two audits)
- 2 cycles that registered nothing
- 30 turns in one cycle

The same question comes up when only to-be-confirmed items are left. "Keep working" adds `J2_LIMIT_ADD`
(default 30) budget units when the budget ran out and allows a fresh set of cycles. The option text shows the
cap (`J2_BUDGET_CAP`), and it is offered only when it can be applied: never when the cap leaves no room, and not
again after "keep working" changed nothing. Instead of the option number, the Requester can type their own amount
("25 units"); code adds it, up to the cap, and Adaptation re-plans within it. "Drop" removes the failing done-when
items (recorded in `goal.json` with the reason), and Audit re-checks. "Ship" ends the run as `Done with open
items` (status `done_with_open_items`) with the open problems listed. An answer always gets a fresh turn
allowance, so the per-cycle turn cap can't re-ask before the answer is handled. An agent message that repeats the
same agent's last message word for word isn't posted again (Audit excepted: a re-check with the same result is news); Identity takes the turn.

### Adaptation's memory (J2.h learns)

- When Audit confirms a fix worked (a problem in one audit is gone in the next and a workflow ran in between),
  Adaptation writes a lesson. Code appends it to `memory/lessons.jsonl` with the problem, cause, fix, run id,
  cycle and workflows.
- At J2.b, code picks the 5 lessons that share the most words with the current gap. Adaptation names the one
  it used (`lesson_used`; shown as a tag in the chat).
- `J2_MEMORY=0` turns memory off: nothing is read or written. Use it for clean test runs; the default is on.
  `J2_MEMORY_FILE` moves the file.
- The **Lessons** tab lists every lesson. Clear memory deletes the file after a confirm prompt.
- **Playbooks (plans, not only fixes):** when a run ends Done, Adaptation saves a playbook for that kind of
  business in `memory/playbooks.jsonl` (`J2_PLAYBOOK_FILE` moves it). One playbook per run; a later Done after
  a change request replaces it. It holds:
  - recorded by code: workflows in build order, costs, what failed and what fixed it, and the measured outcome
    (cycles, whether Audit passed the first time, AI calls, the changes you asked for)
  - written by Adaptation: the sections, mistakes to avoid and advice

  At its first J2.b for a brief, Adaptation reads up to 2 playbooks for the **same business type only**,
  closest brief first. A cafe's plan is never offered to a clothing shop. Lessons and playbooks written by mock
  runs are marked `mock` and never reach a live run. It says which it used (`playbook_used`) and what it changed (`playbook_changes`). Only Done runs
  save one. A `J2_FORCE_AUDIT_FAIL` run's playbook is marked test and follows the test-lesson rule.
  `J2_MEMORY=0` turns off lessons and playbooks alike.
- The **Playbooks** tab lists them, with a progress record per business type: runs, first-pass Audit rate,
  cycles and AI calls per run, and each run in order, so you can see whether it's improving. Clear playbooks
  is there too.

### Behind-the-scenes view

- **Agents panel** (next to the chat): one lane per agent (the five functions, the validator as code, each
  workflow agent). Each lane shows its live status (idle, working, waiting on someone, blocked) and what it's
  on. Workflow agents also show the section they own, attempts used of the call limit, retries used of the
  retry limit, the last check result and the write lock. Click a lane to open its latest message.
- **Detail view**: click any agent message (or a timeline step). It shows:
  - what it read: inputs summarised by code (charter, ledger, workflows, findings, proposal, lessons, task), with
    a toggle for the full system prompt, prompt and raw reply
  - what it decided: the structured reply
  - why: the `reason` field, which code adds to every agent's reply format
  - cost: AI calls, tokens, seconds and budget units charged in that step

  Tokens are shown only when the provider reports them (claude-cli, the Anthropic API and Gemini do); mock mode
  shows characters instead, never an estimate. Code-written messages say "no AI call".
- **Timeline** tab: every step in order on one line, coloured by agent, with each J2 step (J2.a to J2.h)
  marked. Click a step for its details.
- **Saved runs**: the picker in the header opens any `runs/j2-*` folder read-only in the same view (`?run=` in
  the URL). This covers its chat, lanes, timeline, details, site versions and report. Runs from before this
  change open too, but without the per-call details.
- **No secrets**: every server response passes through `redact()` in `j2_server.py`. Every `.env` value and any
  environment variable named like a key, token, secret, password or auth is replaced with `[redacted]`. The
  page never receives request headers.

Each AI call is saved in `runs/j2-*/calls.jsonl` (inputs, full prompt, raw reply, reason, tokens, seconds). Each
section is in `sections.json`.

### Modes and settings

`J2_FIXES` (default 0) is shown in the page header and on the first line of `chat.jsonl`:
- `J2_FIXES=0` is the baseline, as close to the diagram as possible. An Identity ruling goes straight to the
  validator (J2.d -> J2.e). A change request after done goes straight to Adaptation (J2.b).
- `J2_FIXES=1` turns on two fixes:
  - An Identity ruling that costs more than Priority granted goes back to Priority (J2.c) once. Priority's
    answer is final; if the ruling is still over budget, Identity asks you.
  - A change request after done goes to Identity at J2.a first, then J2.b.

Settings:

| Setting | Default | What it does |
|---|---|---|
| `J2_BUDGET` | 100 | Starting budget |
| `J2_BUDGET_CAP` | 2 x budget | Most your approvals can raise the budget to |
| `J2_MAX_CYCLES` | 6 | Cycles before Identity asks what to do |
| `J2_LIMIT_ADD` | 30 | Units "keep working" adds when the budget ran out |
| `J2_BARGAIN_MINUTES` | 15 | J2.c time bound |
| `J2_BARGAIN_CALLS` | 8 | J2.c spend bound (AI calls) |
| `J2_MEMORY` | 1 | 0 turns lessons off |
| `J2_MAX_TURNS` | 30 | Agent turns per cycle |
| `J2_RATES` | 1 | 0 turns the rate card off |
| `J2_FORCE_AUDIT_FAIL` | off | Test switch, see below |
| `J2_MEMORY_TEST_LESSONS` | off | 1 lets J2.b read test lessons (demo runs only), see below |

**Test switch for live runs: `J2_FORCE_AUDIT_FAIL=<done-when item number>`.** It is off unless the variable is
set. In cycle 1 only (Audit's first check), Audit's result for that item is overridden to `NEEDS_REVISION`.

**The agents can't tell it's a test.** They see a normal Audit finding with a concrete, plausible issue chosen
from the item's words, for example "Sunday is missing from the opening hours list, so the hours aren't
complete." Set your own with `J2_FORCE_AUDIT_NOTE="..."`.
- The notes are content gaps only, never overflow or JS claims, so the render check can't contradict them.
- Audit's chat line for that check is written by code from the findings as filed, so it can't say "all pass".
- Messages flagged as tests are never put in any agent's prompt (`chat_view()`), and neither are the test fields
  (`forced_test`, `real_verdict`).
- A mock test scans every saved prompt in `calls.jsonl` to make sure.

The labels are for humans only:
- a red "TEST SWITCH" system note, with Audit's real verdict
- a "TEST: item N forced to fail" tag on Audit's message
- a red badge in the header (also when the run is opened later as a saved run)
- `force_audit_fail` in `chat.jsonl` (first line) and `summary.json`
- `forced_test` and `real_verdict` on the finding in `audits.json`

Audit can still withdraw the finding if Adaptation disputes it and the page shows the item is met. That's the
agents' own judgment, not a leak.

Everything after runs normally: Identity sends it back, Adaptation proposes a fix, the workflow agent runs it,
and Audit re-checks for real. If the fix passes, the lesson is saved. It is marked `"test": true` and by
default is never read back at J2.b, so a forced failure can't steer real runs.

`J2_MEMORY_TEST_LESSONS=1` (opt-in, for demo runs only) lets Adaptation read test lessons at J2.b, so a demo can
show a lesson being saved in one run and used in the next. When a test lesson is used, it's flagged in:
- the chat: a red "used TEST LESSON" tag on Adaptation's message and a "TEST LESSON" system note
- the Agents panel: a "test lesson" badge on Adaptation's lane
- the header badge and the Lessons tab
- `summary.json` (`test_lessons`, and `"test": true` on the lesson used) An item number the charter doesn't have is
ignored, with a warning. The switch is recorded in `chat.jsonl` (first line) and in `summary.json`.

```bash
J2_FORCE_AUDIT_FAIL=2 STUDIO_PROVIDER=claude-cli python j2_server.py   # exercise the fix-and-learn loop live
```

**Our interpretation of "its spend" in J2.c:** the J2 page bounds the bargain by "four hops, fifteen minutes and
its spend" but gives no number for the spend. We read it as the AI calls the bargain itself uses and set the
bound at **8 calls** (four hops x two sides). Change it with `J2_BARGAIN_CALLS`.

Conflicts: any two agents that disagree get 4 attempts to settle it. Then Identity rules from the charter, or
asks you one question with options and rules on your answer. Every conflict is in the Conflicts tab and
`runs/j2-*/conflicts.json`, including what triggered the escalation: 4 attempts, the time bound or the spend
bound.

When a run ends, `runs/j2-*/summary.json` is written at once, before the reviewer's AI call (which can take a
minute or more), so it exists as soon as the chat says the run ended. It is also written when the reviewer
fails or the run crashes. It records (written by code, no AI call):
- run: mode, model, brief, status (`done`, `done_with_open_items`, `stopped`, `crashed`), AI calls
- budget: start, granted, used, raises
- what happened: questions to you, conflicts, validator rejections, HOLDs, audits, limits hit
- the result: workable problems still open, to-be-confirmed facts, items you dropped, each done-when item's
  pass/fail
- agents: each workflow agent (section, status, calls, retries), lessons saved and used, route-check violations

### Tests

```bash
python j2_flow_test.py            # offline, mock mode, both J2_FIXES modes; --chat prints the chats
python j2_check.py site.html      # the render check on any page
```

`j2_flow_test.py` keeps every lesson and playbook in a temp folder, set before `j2` is imported. It ends by
checking that the real `memory/` files are byte-for-byte unchanged. An earlier version wrote 109 mock cafe
playbooks into the real file, and a live clothing run reused one. Those are now in
`_backup/2026-10-07-playbooks-before-cleanup/`, next to a full copy of the file.

`j2_flow_test.py` covers:
- the original flows
- B: one agent per workflow, sections and order, retry within the envelope, failure past the retry limit,
  `revises` handing a section over
- C: same failure twice (drop and ship), the cycle limit (keep working), to-be-confirmed facts, the J2.c time
  bound, out of budget (add budget), `workable()` cases
- D: a lesson saved, then used by the next run; `J2_MEMORY=0` reads and writes nothing; clear
- F: `J2_FORCE_AUDIT_FAIL`: forced once in cycle 1 and marked as a test, real fix and re-check, test lesson saved
  and not reused, an unknown item ignored, off when unset. `J2_MEMORY_TEST_LESSONS`: test lessons filtered by
  default; with the opt-in one is used and flagged in the chat, the lane and `summary.json`
- G: the Simple view rendered in headless Chrome in five states (start, intake questions, a conflict question, a
  limit question, ready). Its visible text never contains agent names, J2 codes, "budget", COUNTER/GRANT/REFUSE,
  "after the team" or other internals. A question with buttons appears once. The phone toggle appears only once
  a site exists. The ready card has its three buttons. Also checked: the word list (run in node: Audit becomes
  "our checks"), and that every Identity prompt, and no other, carries the plain-language rule
- I: unpaid items. A passing item no workflow paid for is flagged `UNPAID`, paid for and passes. Playbooks:
  same business type only (a clothing brief that shares words with a cafe brief gets nothing), mock memory
  kept away from live runs, test memory isolated
- I: pricing. A bundled plan (6 items for 20) is rejected while the same work at 65 passes; a fix relabelled as
  styling is rejected; a fix isn't charged again for items already paid for; Priority's prompt carries the cost
  per item
- H: J2.a proposes visitor needs for a florist and asks to confirm. The style guide comes first, is retried when
  missing and is followed by every later agent. A planted small tap target fails R-6 by measurement, loops
  back, is fixed and passes. Playbooks are saved at Done with the measured outcome, reused for the same business
  type (not for a florist) with the change named, flagged as test after a forced failure, and untouched with
  `J2_MEMORY=0`. Also: design measurements and the screenshot on a planted page, no cafe examples in our
  instructions, the new example briefs
- E: the page's tabs, lanes and their statuses, call links with reasons and no invented tokens, the full call
  record, saved runs opened read-only, path tricks refused, a fake key redacted, clear memory

### Still different from the J2 page

- **Root (J2.e)**: the page says Root checks granted workflows against standards ("designed; not yet built").
  Here a code validator checks fields, price, refusals and budget, not standards.
- **Library workflows**: the page has Adaptation pick from a Library or make custom ones. Here every workflow
  is custom.
- **Engines and triggers**: the page has each function as an engine that wakes when its records exist. Here one
  loop hands the turn from agent to agent.
- **Audit timing**: Audit runs once the build queue is empty, not after every workflow (fewer calls).
- **"Core" done-when items**: every done-when item counts as core; the charter has no core / optional split.
- **"Its spend" in J2.c**: our number (8 AI calls), see above.
- **Item kinds for pricing**: a keyword match on the done-when text. A fix of a failing item pays for that
  item at the fix price, even when the item's own minimum is higher (e.g. a form item at 15).
- **Lesson relevance**: word overlap, not meaning; fine for a small file. Playbooks match on business type
  first, then shared words.
- **Rubric R-1, R-4, R-5** (styling, main action, navigation) are Audit's judgment on the screenshot. Only R-2,
  R-3, R-6 and R-7 are measured by code. Screenshots go to the model in live runs only. Image input through
  `claude -p` (stream-json) is implemented but not yet tried on a live run.
- **Executors**: the official files have no executor. The workflow agents use our placeholder `builder.md`.
- **CEO**: where the official files say CEO, J2 reads it as you, reached only through Identity.
- **No-progress limit**: a run with 2 cycles that registered nothing also triggers Identity's question, a guard
  that isn't on the page.
