"""Offline check of the J2 flow in mock mode: python j2_flow_test.py [--fast [--browser]] [--chat]

--fast stubs the headless-browser measurement (the render check and tap targets read the page without Chrome) and
skips the tests that drive the page in Chrome; --fast --browser runs those and the real render check, with only tap
targets stubbed. Without --fast everything uses Chrome.

Each scenario runs with J2_FIXES=0 (baseline) and J2_FIXES=1 (fixes):
1. A vague brief: J2.a asks the Requester, a conflict the charter can't decide goes to the Requester, Audit and
   Adaptation settle a finding between themselves, the run ends Done. Then a change request after done.
   Run twice: the Requester keeps Priority's position, or picks the stories option (baseline: the validator
   rejects it because Priority refused it; fixes: Priority reprices the ruling and funds it).
2. A full brief (Brew Lab): J2.a passes without questions; Identity resolves the conflict from the charter.
   Baseline: the ruling goes straight to the validator, which rejects what Priority refused.
   Fixes: the ruling goes back to Priority once; with too little budget, Identity asks the Requester.
3. Only Identity talks to the Requester: an agent that addresses the Requester is redirected to Identity.
B. One agent per workflow: each owns a marked section; it retries within its envelope; "revises" hands over a section.
C. Workable loop: the same failure twice, the cycle limit and to-be-confirmed facts each pause for the Requester
   (keep working, drop, ship); the J2.c bargain's time bound escalates to Identity; workable() unit checks.
D. Memory: a confirmed fix saves a lesson, the next run's Adaptation uses it, J2_MEMORY=0 reads and writes nothing.
E. The page: Agents and Lessons tabs, the state they read, and the clear-memory endpoint.
I. Cost follows the work (runs/j2-20261007-190411: 13 items for 35 by bundling, a fix relabelled as styling): each
   covered item has a rate-card minimum, a fix is priced as a fix, Priority sees cost per item.
H. Any business, better each run: J2.a proposes visitor needs for the business type; the first workflow writes the
   style guide everyone follows; Audit's design rubric loops a measured failure back; playbooks saved at Done and
   reused for a similar business; no cafe examples in live prompts.
G. The Simple view (default page): rendered in headless Chrome for a start screen, questions, a limit question and a
   finished run; its visible text never has agent names, J2 codes, "budget" or other internals.
F. J2_FORCE_AUDIT_FAIL=<item>: a forced cycle-1 failure that agents can't tell from a real finding (no test label in
   any prompt), then a real fix, a real re-check and a saved lesson. summary.json exists before the reviewer call.
   J2_MEMORY_TEST_LESSONS=1 lets J2.b read test lessons (off by default), flagged in the chat and the lanes.
Runs are written to a temp folder (J2_RUNS_DIR), never the real runs/; each ended run has summary.json. Memory is off (J2_MEMORY=0) except in
the memory test, which uses its own lessons file.
"""
import json
import os
import re
import sys
import time

import hashlib
import tempfile

os.environ["STUDIO_MOCK"] = "1"
os.environ["J2_MEMORY"] = "0"        # clean runs: the memory tests turn it on
# Every memory file of this test session lives in a temp folder, set before j2 is imported, so no test can write
# lessons or playbooks into the real memory/ (it once wrote 109 mock cafe playbooks there; a live run reused one).
SESSION_MEMORY = tempfile.mkdtemp(prefix="j2-test-memory-")
os.environ["J2_MEMORY_FILE"] = os.path.join(SESSION_MEMORY, "lessons.jsonl")
os.environ["J2_PLAYBOOK_FILE"] = os.path.join(SESSION_MEMORY, "playbooks.jsonl")
os.environ["J2_RUNS_DIR"] = os.path.join(SESSION_MEMORY, "runs")   # runs/ holds real runs only: report evidence
REAL_MEMORY = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory", f) for f in ("lessons.jsonl", "playbooks.jsonl")]


def fingerprint(paths):
    return {p: hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None for p in paths}


REAL_BEFORE = fingerprint(REAL_MEMORY)
import j2  # noqa: E402
ATOM = [j2.mock_atom({})]            # a complete work atom for workflows a test registers directly

BREW_LAB = ("A one-page website for Brew Lab, a small specialty coffee shop in Indiranagar, Bengaluru. Visitors should "
            "see the menu with prices, the opening hours, and where to find us, and be able to pre-order a coffee for "
            "pickup. It should feel warm and modern and work well on a phone. Include a section about our beans and the "
            "farms they come from, and a simple loyalty-card explainer (buy 9, get the 10th free).")
SHOW = "--chat" in sys.argv
FAST = "--fast" in sys.argv
BROWSER = not FAST or "--browser" in sys.argv        # the tests that drive the page in Chrome
REAL_FIND, REAL_TAP, REAL_CHECK = j2.j2_check.find_chrome, j2.j2_check.tap_targets, j2.j2_check.check


def fake_tap_targets(html, selector, min_px=j2.j2_check.TAP_MIN):
    """--fast: no browser. The inline width/height (or min-width/min-height) in px of the buttons, links and fields
    inside the elements matching selector; a control with no inline size counts as big enough."""
    name, kind = selector.lstrip("#."), selector[:1]
    attr = "id" if kind == "#" else "class"
    roots, small, checked = 0, [], 0
    for m in re.finditer(rf'<(\w+)\b[^>]*\b{attr}="(?:[^"]*\s)?{re.escape(name)}(?:\s[^"]*)?"[^>]*>', html):
        roots += 1
        tag, depth, end = m.group(1), 0, len(html)
        for t in re.finditer(rf"<(/?){tag}\b[^>]*>", html[m.start():]):
            depth += -1 if t.group(1) else 1
            if not depth:
                end = m.start() + t.end()
                break
        for c in re.finditer(r'<(button|a|input|select|textarea)\b([^>]*)>([^<]*)', html[m.start():end]):
            if c.group(1) == "a" and "href" not in c.group(2) or 'type="hidden"' in c.group(2):
                continue
            checked += 1
            style = dict(re.findall(r"(min-height|min-width|height|width)\s*:\s*(\d+)px", c.group(2)))
            h = max(int(style.get("height", 0)), int(style.get("min-height", 0))) or min_px
            w = max(int(style.get("width", 0)), int(style.get("min-width", 0))) or min_px
            if h < min_px or w < min_px:
                small.append(f'{c.group(1)} "{c.group(3).strip()[:25]}" {w}x{h}')
    return {"available": True, "roots": roots, "checked": checked, "small_count": len(small), "small": small[:6]}


def fake_check(html):
    """--fast: the render check without a browser: static checks, no overflow, no JS errors, forms submit."""
    st = j2.j2_check.static_checks(html)
    return {"available": True, **st, "phone": {"width": 360, "overflow_px": 0},
            "desktop": {"width": 1280, "overflow_px": 0}, "js_errors": [], "design": {},
            "form_results": [{"index": i + 1, "has_submit": True, "submitted": True, "invalid": [], "errors_during": [],
                              "ok": True} for i in range(st["forms"])]}


if FAST:
    j2.j2_check.tap_targets = fake_tap_targets
    if not BROWSER:     # --fast --browser keeps the real render check: the rubric tests need its measurements
        j2.j2_check.check = fake_check
        j2.j2_check.find_chrome = lambda: None      # the page-driving tests skip; screenshots aren't taken


def say(run, text):
    assert run.user_says(text)
    while run.status != "waiting":
        time.sleep(0.02)


def show(run):
    if SHOW:
        print(f"\n===== {run.dir}")
        for m in run.chat:
            print(f"[{m['id']}] {j2.NAMES.get(m['who'], m['who'])}: {m['text']}")


def finish(run):
    """Answer what a person would, until the run ends: a conflict question with the simpler option, a budget
    limit with "keep working"."""
    for _ in range(6):
        if not run.paused:
            return
        say(run, "Option 2" if run.paused["kind"] == "conflict" else "1")


def add_budget_if_asked(run):
    """J2_FIXES=1 funds Identity's ruling (the stories), so the viewport fix later finds the budget spent and Identity
    asks for more. Answer "1" (keep working, +30), only for that reason."""
    while run.paused and run.paused["kind"] == "limit":
        assert run.paused["handoff"]["limit"].startswith("Out of budget"), run.paused["handoff"]["limit"]
        say(run, "1")


def only_identity_addresses_user(run):
    for m in run.chat:
        if m.get("next") == "user" or m.get("to_user"):
            assert m["who"] == "identity", m


def summary(run):
    with open(os.path.join(run.dir, "summary.json"), encoding="utf-8") as f:
        s = json.load(f)
    with open(os.path.join(run.dir, "chat.jsonl"), encoding="utf-8") as f:
        head = json.loads(f.readline())
    assert head["meta"] and head["j2_fixes"] == s["j2_fixes"] == int(run.fixes), (head, s["j2_fixes"])
    return s


def vague(fixes):
    run = j2.J2Run()
    say(run, "a website for my cafe")
    assert run.paused and run.paused["kind"] == "info" and not run.goal, run.outcome
    say(run, "It's called Little Fig, in Koramangala, Bengaluru. Visitors should see our menu with prices, opening "
             "hours and where to find us. Cozy and simple, and it must work on phones.")
    assert run.goal and run.paused and run.paused["kind"] == "conflict", run.outcome
    c = run.conflicts[0]
    assert c["escalated"] and c["attempts_before_escalation"] == 4 and c["user_question"], c
    say(run, "Option 2: skip the stories, keep the reserve for fixes.")
    c = run.conflicts[0]
    assert c["resolved_by"] == "identity_after_user" and c["user_answer"] and c["winner"] == "priority", c
    f = next(x for x in run.conflicts if x["topic"] == "finding")
    assert f["resolved_by"] == "agents" and not f["escalated"] and f["winner"] == "audit", f
    assert run.outcome.startswith("Done"), run.outcome
    s = summary(run)
    assert s["status"] == "done" and len(s["questions_to_user"]) == 2 and len(s["conflicts"]) == 2, s
    n = len(run.chat)
    say(run, "Add a section for visiting hours")
    first = next(m for m in run.chat[n:] if m["who"] not in ("user", "system"))
    assert first["who"] == ("identity" if fixes else "adaptation"), first   # fix (b): J2.a before J2.b
    assert run.outcome.startswith("Done"), run.outcome
    assert summary(run)["change_requests"] == ["Add a section for visiting hours"]
    only_identity_addresses_user(run)
    show(run)


def vague_stories(fixes):
    """J2.d asks the Requester and they pick the stories option. Baseline: Identity rules it in, but the ruling goes
    straight to the validator, which rejects what Priority refused (the Requester's choice doesn't override it).
    Fixes: the ruling costs more than Priority granted, so Priority reprices it once and funds it."""
    run = j2.J2Run()
    say(run, "a website for my cafe")
    say(run, "It's called Little Fig, in Koramangala, Bengaluru. Visitors should see our menu with prices, opening "
             "hours and where to find us. Cozy and simple, and it must work on phones.")
    assert run.paused and run.paused["kind"] == "conflict", run.outcome
    say(run, "Option 1: fund the stories section.")
    c = run.conflicts[0]
    assert c["resolved_by"] == "identity_after_user" and c["winner"] == "split" and c["user_answer"], c
    stories = [w for w in run.workflows if w["name"] == "Stories section"]
    if fixes:
        assert c["repriced"] and c["repricing"]["decision"] == "GRANT" and stories and not run.rejections, c
    else:
        assert not c.get("repriced") and not stories, c
        assert [r["workflow"] for r in run.rejections] == ["Stories section"] and "Priority" in run.rejections[0]["reason"]
    assert run.outcome.startswith("Done"), run.outcome
    s = summary(run)
    assert s["conflicts"][0]["user_answer"].startswith("Option 1") and s["validator_rejections"] == run.rejections, s
    only_identity_addresses_user(run)
    show(run)


def full(fixes):
    run = j2.J2Run()
    say(run, BREW_LAB)
    assert not any(e["type"] == "pause" and e.get("pause") == "info" for e in run.events), "J2.a asked questions"
    c = run.conflicts[0]
    assert c["resolved_by"] == "identity" and not c["escalated_to_user"] and c["winner"] == "split", c
    stories = [w for w in run.workflows if w["name"] == "Stories section"]
    if fixes:   # repriced by Priority, granted, registered
        assert c["repriced"] and c["repricing"]["decision"] == "GRANT" and stories, c
    else:       # straight to the validator, which rejects what Priority refused
        assert not c.get("repriced") and not stories, c
        assert any(r["workflow"] == "Stories section" and "Priority" in r["reason"] for r in run.rejections), run.rejections
        assert any(m["who"] == "system" and m["text"].startswith("Validator rejected 'Stories section'") for m in run.chat)
    assert run.outcome.startswith("Done"), run.outcome
    s = summary(run)
    assert s["status"] == "done" and all(d["pass"] for d in s["done_when"]) and s["route_check_violations"], s
    only_identity_addresses_user(run)
    show(run)


def ruling_over_budget():
    """Fixes only: the ruling (90) is over the 85 left; Priority counters; Identity asks; the Requester adds budget.
    The ruling then takes the whole budget, so the viewport fix can't be funded: the run doesn't stop, Identity asks
    (keep working with +30, drop, ship). Keep working funds the fix and the site becomes workable."""
    os.environ["J2_FIXES"] = "1"
    run = j2.J2Run()
    run.budget = 85
    say(run, BREW_LAB)
    assert run.paused and run.paused["kind"] == "ruling_budget", run.outcome
    say(run, "1, add the units")
    c = run.conflicts[0]
    assert c["repricing"]["decision"] == "COUNTER" and c["resolved_by"] == "identity_after_user", c
    assert run.budget == 90 and any(w["name"] == "Stories section" for w in run.workflows), run.budget
    assert run.paused and run.paused["kind"] == "limit" and run.paused["handoff"]["limit"].startswith("Out of budget"), \
        run.outcome
    q = run.paused["questions"][0]
    assert q["options"][0].startswith("Add 30 work credits and keep going") and q["budget"][0] == 30 and q["options"][-1].startswith("Finish as it is")
    say(run, "1")
    assert run.budget == 120 and run.outcome.startswith("Done"), (run.budget, run.outcome)
    s = summary(run)
    assert s["status"] == "done" and s["limits_hit"] and not s["workable"], s


def built_first(run):
    """runs/j2-20261009-133203: the decision question about unfunded items comes after the funded work is built and
    audited, never while registered work is unbuilt."""
    assert run.paused and run.paused["kind"] == "limit" and not run.paused["handoff"].get("after_ruling"), run.outcome
    assert run.sites and run.audits and run.audits[-1]["version"] == len(run.sites), run.outcome
    assert not any(w["status"] in ("registered", "held", "running") for w in run.workflows), run.workflows
    reg = next(m["id"] for m in run.chat if m["who"] == "validator" and m.get("register"))
    order = [m["who"] for m in run.chat if m["id"] > reg]
    assert order.index("coordination") < order.index("audit") < len(order) - 1 - order[::-1].index("identity"), order


def policy_budget(fixes):
    """runs/j2-20261008-153402 (budget 40, rate-card floor 110): Adaptation asked about affordability twice and never
    proposed, so Priority was never called and nothing was built. Now a budget POLICY_QUESTION is rejected by code and
    Adaptation is asked once more; it proposes the best set that fits, Priority rules, and only then Identity asks one
    decision question (add credits or leave out; no "finish", there's no site). An unclear answer is asked once more;
    "option 1" raises the budget by code; the rest is proposed, granted and built."""
    run = j2.J2Run()
    run.budget = 60                                          # Brew Lab's floor is 70
    orig, asked = run.call, []

    def call(fn, fmt, task, mock, **k):
        if fn == "adaptation" and "WHY YOU ARE UP" in task:
            asked.append("REJECTED" in task)
            if len(asked) == 1:
                return {"say": "@Identity Policy question: 60 can't cover the charter's sections. Can we add budget?",
                        "act": "POLICY_QUESTION", "question": "60 can't cover the charter's sections. Add budget?"}
        assert not (fn == "identity" and task.startswith("QUESTION FROM")), "a budget question reached Identity"
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    say(run, BREW_LAB)
    assert asked[:2] == [False, True], asked                 # regenerated once, with the rejection in the task
    assert any(m["who"] == "system" and m["text"].startswith("Adaptation's question about budget was rejected")
               for m in run.chat)
    i = {m["who"]: m["id"] for m in reversed(run.chat) if m["who"] != "validator" or m.get("register")}
    assert i["adaptation"] < i["priority"] < i["validator"], i   # proposal, then Priority's ruling, then registration
    built_first(run)
    q = run.paused["questions"][0]
    assert run.paused["handoff"]["choices"] == ["continue", "drop", "ship"], run.paused["handoff"]
    assert q["options"][0].startswith("Add 10 work credits and keep going") and q["options"][1].startswith("Leave out"), q
    say(run, "the bigger one I think")                       # unclear: no guess, Identity asks once more
    assert run.paused and run.paused["handoff"].get("reasked") and run.budget == 60, run.paused
    say(run, "option 1")
    assert run.budget == 70 and run.raises[0]["asked"] == 10, run.raises
    d = [x for x in run.decisions if x["kind"] == "limit"]
    assert d[0].get("unclear") and d[1]["decision"] == "continue" and d[1]["budget_added"] == 10, d
    assert run.spent == 70 and all(w["status"] == "done" for w in run.workflows), (run.spent, run.workflows)
    assert run.outcome.startswith("Done") and not run.goal.get("dropped_by_requester"), run.outcome
    assert summary(run)["budget"]["granted"] == 70
    only_identity_addresses_user(run)
    show(run)


def connections():
    """Every J2 link works at three budgets: generous (2x the rate-card floor), tight (floor - 15, cap above the
    floor) and impossible (cap below the floor). Adaptation proposes, Priority rules on every proposal, the validator
    registers or rejects with a reason, Coordination schedules, Audit checks what was built, and every run ends with
    a site built (the Requester always picks leave-out or keep going here). summary.json counts the links."""
    j2.load_rates()
    floor = sum(j2.item_min(c) for c in j2.mock_charter(BREW_LAB)["done_when"])
    assert floor == 70, floor
    for name, budget, cap in (("generous", 2 * floor, None), ("tight", floor - 15, None),
                              ("impossible", floor - 30, floor - 30)):
        old_cap = j2.BUDGET_CAP
        try:
            if cap:
                j2.BUDGET_CAP = cap
            assert j2.BUDGET_CAP > floor if name != "impossible" else j2.BUDGET_CAP < floor, name
            run = j2.J2Run()
            run.budget = budget
            say(run, BREW_LAB)
            asked = []
            for _ in range(6):
                if not run.paused:
                    break
                p = run.paused
                asked.append(p)
                assert p["kind"] != "limit" or not any(w["status"] in ("registered", "held") for w in run.workflows), \
                    (name, "paused with registered, unbuilt work")
                if p["kind"] == "limit":
                    ch = p["handoff"]["choices"]
                    say(run, str(ch.index("drop" if "drop" in ch else "continue") + 1))
                else:
                    say(run, "Option 2" if p["kind"] == "conflict" else "1")
        finally:
            j2.BUDGET_CAP = old_cap
        s, chat = summary(run), run.chat
        links = s["links"]
        assert links.get("adaptation->priority", 0) >= 1, (name, links)                     # Adaptation proposed
        for i, m in enumerate(chat):                     # Priority ruled on every proposal sent to it
            if m["who"] == "adaptation" and m.get("next") == "priority":
                ruling = next((x for x in chat[i + 1:] if x["who"] == "priority"), None)
                assert ruling and ruling.get("decision") in ("grant", "counter", "refuse"), (name, m["text"], ruling)
        reg = [m for m in chat if m["who"] == "validator" and "register" in m]
        assert reg and all(m["register"] or "Rejected:" in m["text"] for m in reg), (name, reg)
        assert all(r["reason"] for r in run.rejections), (name, run.rejections)
        assert links.get("coordination->priority", 0) >= 1 and links.get("priority->W", 0) >= 1, (name, links)
        assert run.sites and run.audits and links.get("audit->identity", 0) >= 1, (name, run.outcome)
        decisions = [m for m in chat if m["who"] == "identity" and m.get("pause") in j2.DECISION_PAUSES]
        assert s["identity_to_requester_decisions"] == len(decisions), (name, s["identity_to_requester_decisions"])
        facts = [m for m in chat if m["who"] == "identity" and m.get("pause") in ("fact", "info")]
        assert s["identity_to_requester_facts"] == len(facts), (name, s["identity_to_requester_facts"])
        rulings = [m["decision"] for m in chat if m["who"] == "priority" and m.get("decision")]
        assert s["priority_rulings"] == {d: rulings.count(d) for d in ("grant", "counter", "refuse")} \
            and sum(s["priority_rulings"].values()) == len(rulings) >= 1, (name, s["priority_rulings"], rulings)
        limits = [p for p in asked if p["kind"] == "limit"]
        for p in limits:                                 # "finish" only once a site exists; never one option
            opts = p["questions"][0]["options"]
            assert len(opts) >= 2, (name, opts)
            built = any(re.match(r"W-\d+$", m["who"]) and m["id"] < p["msg"] for m in chat)
            assert built or not any(o.startswith("Finish as it is") for o in opts), (name, opts)   # finish needs a site
        if name == "tight":
            assert any(m.get("decision") == "counter" for m in chat) or \
                any("drop" in p["handoff"]["choices"] for p in limits), (name, links)
        if name == "impossible":
            first = limits[0] if limits else None
            assert first and "drop" in first["handoff"]["choices"] and "continue" not in first["handoff"]["choices"], first
            # the finish code applied (the only option left) tells the Requester why, and what's missing
            i = next(i for i, m in enumerate(chat) if m["text"].startswith("Only one option was possible"))
            told = chat[i + 1]
            form = next(c for c in run.goal["done_when"] if "pre-order" in c)
            assert told["who"] == "identity" and told.get("to_user") and told.get("done"), told
            assert "We've reached a limit: you've approved the most work credits allowed" in told["text"], told["text"]
            assert f"{form} can't be paid for and can't be left out" in told["text"], told["text"]
            assert f"Still not right (1):\n- item {run._no(form)} {j2.short(form)} (unfunded)" in told["text"], told["text"]
            assert run.outcome.startswith("Done with open items: shipped as is as the only option"), run.outcome
            plain_for_requester(run)
        if name == "generous":
            assert run.outcome == j2.WORKABLE_OUTCOME, run.outcome


def build_before_asking():
    """runs/j2-20261009-133203: 6 workflows were registered across two rulings, but the run went validator -> Identity's
    decision question each time and the site stayed at v0; Identity told the Requester "the site now has..." about
    unbuilt work; the gate item was extended with filters; Audit filed items 5-7 under their pre-drop numbers."""
    # (1) budget 40: the funded workflows are built and audited before the question
    run = j2.J2Run()
    run.budget = 40
    say(run, BREW_LAB)
    built_first(run)
    assert all(w["status"] == "done" for w in run.workflows) and len(run.workflows) >= 1, run.workflows
    # (2) nothing has passed Audit: Identity may not describe anything as built ("will build" instead)
    run = j2.J2Run()
    run.goal = j2.mock_charter(BREW_LAB)
    run.workflows = [{"id": "W-1", "name": "Menu", "status": "registered", "covers_text": [run.goal["done_when"][0]]}]
    run.call = lambda fn, fmt, task, mock, **k: {"say": "So far the page has the earthy look and all your prices."} \
        if fn == "identity" else json.loads(mock())
    run._identity_limit({"reason": "Priority's ruling", "left_out": run.goal["done_when"][1:], "budget_needed": 20})
    text = run.chat[-1]["text"]
    assert "page has" not in text and "will build 1 funded part" in text, text
    assert any(e["type"] == "invalid_move" and "as built" in e["detail"] for e in run.events)
    # (3) the gate's wording is fixed by code: it can't name features
    run = j2.J2Run()
    orig = run.call

    def call(fn, fmt, task, mock, **k):
        if fn == "identity" and '"core": [bool]' in fmt:
            r = json.loads(mock())
            r["goal"]["done_when"] = r["goal"]["done_when"] + [
                "The page runs with no JavaScript errors, filters and category browsing work, and every in-page link "
                "points to an existing section."]
            r["goal"]["core"] = [False] * (len(r["goal"]["done_when"]) - 1) + [True]
            return r
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    run.budget = 200
    say(run, BREW_LAB)
    gate = run.goal["done_when"][-1]
    assert gate == j2.GATE_TEXT and not re.search(r"filter|categor", gate, re.I), gate
    assert gate in run.goal["core_items"] and j2.must_keep(gate, run.goal), run.goal["core_items"]
    # (5) after a drop, Audit's pre-drop numbers are read by text; dropped items get no finding; nothing is "missing"
    run = j2.J2Run()
    orig_items = [c for c, _ in THREAD_AND_LOOM]
    keep = [orig_items[i] for i in (0, 1, 6, 8, 11)]
    run.goal = {"done_when": keep, "charter_items": orig_items,
                "dropped_by_requester": [c for c in orig_items if c not in keep]}
    findings = [{"id": f"F-{i}", "item": i, "criterion": c[:70], "verdict": "PASS", "evidence": "seen"}
                for i, c in ((1, keep[0]), (2, keep[1]))]
    findings += [{"id": "F-3", "item": 7, "criterion": "Every product has an order button to WhatsApp", "verdict": "PASS",
                  "evidence": "seen"},                                   # old number 7 -> item 3
                 {"id": "F-4", "item": 9, "criterion": "Store section with address, hours and map link",
                  "verdict": "PASS", "evidence": "seen"},                # old number 9 -> item 4
                 {"id": "F-5", "item": 12, "criterion": "No JavaScript errors", "verdict": "PASS", "evidence": "seen"},
                 {"id": "F-6", "item": 8, "criterion": "Lookbook with 3 styled outfits", "verdict": "NEEDS_REVISION",
                  "evidence": "absent"},                                 # dropped: no finding
                 {"id": "F-7", "item": None, "criterion": "A reviews section shows three reviews", "verdict":
                  "NEEDS_REVISION", "evidence": "absent"}]               # dropped, unnumbered: no finding
    results, extras = run._audit_findings(findings, keep)
    # findings are named by the items' run-long numbers: 1, 2, 7, 9, 12 (never renumbered after the drop)
    assert [r["id"] for r in results] == ["F-1", "F-2", "F-7", "F-9", "F-12"] and all(r["pass"] for r in results), results
    assert not extras, extras


def below_floor():
    """runs/j2-20261008-153402: budget below the rate-card floor. Adaptation proposes the best set that fits and lists
    the rest in left_out (core facts first); Priority rules; the funded work is built and audited; then Identity asks
    one decision question with a leave-out option. A question never has one option; "finish" needs a site."""
    run = j2.J2Run()
    run.budget = 50                                          # Brew Lab's floor is 70; its core items cost 45
    say(run, BREW_LAB)
    assert run.goal["core_items"] == [c for c in run.goal["done_when"] if re.search(r"menu|hours|address|order", c)]
    a = next(m for m in run.chat if m["who"] == "adaptation")
    p = next(m for m in run.chat if m["who"] == "priority")
    assert a["id"] < p["id"] and a.get("proposal") and p.get("decision") == "grant", (a, p)
    crit = run.goal["done_when"]
    funded = {t for w in run.workflows for t in w["covers_text"]}
    assert all(c in funded for c in crit if j2.must_keep(c, run.goal)), funded    # core facts are never left out
    left = [c for c in crit if c not in funded]
    built_first(run)
    assert run.paused["handoff"]["choices"] == ["continue", "drop", "ship"], run.paused
    assert [crit[i - 1] for i in run.paused["handoff"]["failing_items"]] == left, run.paused["handoff"]
    assert len([e for e in run.events if e.get("type") == "pause"]) == 1, "more than one question"
    say(run, "2")
    assert run.goal["dropped_by_requester"] == left and not run.paused, run.goal
    assert run.sites and run.outcome == j2.WORKABLE_OUTCOME, run.outcome
    # at the cap: the funded work is built first, so the question has a site to finish (and no "add credits")
    run = j2.J2Run()
    run.budget = j2.BUDGET_CAP = 40
    try:
        say(run, BREW_LAB)
        built_first(run)
        q = run.paused["questions"][0]
        assert run.paused["handoff"]["choices"] == ["drop", "ship"] and q["options"][1].startswith("Finish as it is"), q
    finally:
        j2.BUDGET_CAP = 2 * j2.BUDGET
    # only "add credits" would be possible (every left-out item is a core fact): stop here is the second option
    run = j2.J2Run()
    run.goal = {"done_when": ["The menu with prices is shown", "Opening hours are listed"]}
    run._identity_limit({"reason": "Priority's ruling", "left_out": run.goal["done_when"], "budget_needed": 20})
    assert run.paused["handoff"]["choices"] == ["continue", "ship"], run.paused["handoff"]



THREAD_AND_LOOM = [   # runs/j2-20261008-153402's charter (12 items, floor 110), with Identity's core marks
    ("The page shows the name Thread & Loom and Pune, has a viewport meta tag, and uses an earthy colour palette "
     "defined in the CSS.", True),
    ("The site lists exactly these 10 products with their prices: Indigo block-print kurta 1,499; Mustard handloom "
     "kurta 1,699; White chikankari kurta 2,199; Ikat handloom saree 3,499; Khadi silk saree 4,999; Cotton jamdani "
     "saree 3,999; Khadi cotton shirt 1,299; Linen-blend shirt 1,599; Block-print dupatta 899; Chanderi dupatta 1,099.", True),
    ("Visitors can filter products by category (All, Kurtas, Sarees, Shirts, Dupattas), by size, and by price, and the "
     "filters work together.", False),
    ("Size options match the supplied data: Indigo block-print kurta S to XXL; Mustard handloom kurta S to XL; White "
     "chikankari kurta XS to XL; Khadi cotton shirt S to XXL; Linen-blend shirt M to XXL; all sarees and dupattas Free "
     "size.", False),
    ("A size guide table shows chest in inches: XS 32, S 34, M 36, L 38, XL 40, XXL 42.", False),
    ("A New Arrivals section shows exactly the White chikankari kurta, Ikat handloom saree and Linen-blend shirt.", False),
    ("Every product has an order button that opens a WhatsApp link to 910000011111 with the product name and chosen "
     "size in the message text.", True),
    ("A lookbook section shows 3 styled outfits, each built only from the listed products and naming them.", False),
    ("A store section shows 18 FC Road, Shivajinagar, Pune 411005; hours 11am to 9pm, Tuesday to Sunday, closed "
     "Monday; shop phone +91 00000 22222; and a map link for the address.", True),
    ("A policy section states: exchange within 7 days if unworn with tags; no returns on sale items; and delivery in "
     "Pune in 2 days for Rs 79, free above 2,999, pay on delivery.", False),
    ("A reviews section shows these three reviews: \"Beautiful fabric, fits perfectly\" - Meera K.; \"Fast delivery and "
     "lovely packing\" - Arjun S.; \"My go-to for festive kurtas\" - Priya D.", False),
    ("The page has no JavaScript errors, no horizontal overflow at 360px or 1280px, and no broken in-page links.", True)]


def thread_and_loom_core():
    """Follow-up to 3a8960c: "any number" made prices, sizes, "3 styled outfits" and "360px" core, so almost nothing in
    the Thread & Loom charter could be left out. Identity marks core items at J2.a; at budget 40 the decision question
    offers the lookbook, reviews and new arrivals as leave-out options, never a core item."""
    run = j2.J2Run()
    run.budget = 40
    orig = run.call

    def call(fn, fmt, task, mock, **k):
        if fn == "identity" and '"core": [bool]' in fmt:              # J2.a records the charter with core marks
            r = json.loads(mock())
            r["goal"].update(site_name="Thread & Loom", business_type="clothing boutique",
                             done_when=[c for c, _ in THREAD_AND_LOOM], core=[k for _, k in THREAD_AND_LOOM])
            return r
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    say(run, "A website for Thread & Loom, a handloom clothing boutique in Pune. " * 3)
    crit = run.goal["done_when"]
    expect = [j2.GATE_TEXT if "JavaScript errors" in c else c for c, k in THREAD_AND_LOOM if k]
    assert run.goal["core_items"] == expect, run.goal["core_items"]
    built_first(run)
    offered = [crit[i - 1] for i in run.paused["handoff"]["failing_items"]]
    for words in ("lookbook", "reviews section", "New Arrivals"):
        assert any(words in c for c in offered), (words, offered)
    assert not any(j2.must_keep(c, run.goal) for c in offered), offered
    # the keyword fallback no longer treats a number as a core fact
    assert not j2.must_keep(THREAD_AND_LOOM[7][0], {}) and j2.must_keep(THREAD_AND_LOOM[1][0], {})


def deferred_twice():
    """The same done-when item left out or refused in 2 rounds: Identity asks the Requester even though budget remains."""
    run = j2.J2Run()
    run.goal = {"done_when": ["The menu with prices is shown", "A lookbook section shows 3 styled outfits"],
                "core_items": ["The menu with prices is shown"]}
    run.budget, look = 100, "A lookbook section shows 3 styled outfits"
    run.a_named = [look]
    run._parked("Priority refused it")                       # round 1: budget remains, Adaptation proposes again
    assert run.turn == "adaptation" and run.handoff.get("new_cycle"), run.handoff
    run.cycle += 1
    run.a_named = [look]
    run._parked("Priority refused it")                       # round 2: the Requester decides
    assert run.turn == "identity" and run.handoff["kind"] == "limit" and run.handoff["deferred"], run.handoff
    run._identity_limit(run.handoff)
    q, h = run.paused["questions"][0], run.paused["handoff"]
    assert h["choices"] == ["continue", "drop"] and h["failing_items"] == [2], h
    assert q["question"].startswith("Some parts were put off twice.") and "budget" not in q, q

def redirect():
    """Audit addresses the Requester: the message goes to Identity first, with a Route check note."""
    run = j2.J2Run()
    run.goal = {"done_when": ["a", "b", "c"]}
    run.cycle = 1
    run._handoff("audit", kind="audit")
    run._say("audit", "@Requester can you send the phone number?", "adaptation")
    assert run.relay and run.relay["from"] == "audit"
    notes = [m["text"] for m in run.chat if m["who"] == "system"]
    assert notes and notes[-1].startswith("Route check: Audit addressed the Requester"), notes
    assert run.chat[-2]["text"].startswith("@Identity"), run.chat[-2]


def workflow_agents():
    """B: every registered workflow gets its own agent and section; the site file is assembled from the sections."""
    run = j2.J2Run()
    orig, bad = run.call, []

    def call(fn, fmt, task, mock, **k):                 # W-2's first reply can't be used: it retries once
        if fn == "W-2" and not bad:
            bad.append(1)
            return '{"say": "@Coordination here is the page"}\n```html\n<!doctype html><html><body>x</body></html>\n```'
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    say(run, BREW_LAB)
    assert run.outcome.startswith("Done"), run.outcome
    site = run.sites[-1]
    for w in run.workflows:
        assert w["agent"] == f"{w['id']} Builder" and w["section"] == w["id"] and w["status"] == "done", w
        assert any(m["who"] == w["id"] for m in run.chat), f"{w['id']} never spoke"
        assert f"<!-- J2:{w['id']} " in site, w["id"]
    assert not any(m["who"] == "builder" for m in run.chat)
    w2 = run._wf("W-2")
    assert w2["retries_used"] == 1 and any(m["text"].startswith("W-2 attempt 1 can't be used") for m in run.chat), w2
    assert site.index("<!-- J2:W-1 start") < site.index("<!-- J2:W-2 start"), "sections out of order"
    vp = next(w for w in run.workflows if "viewport" in w["name"].lower())
    assert f'<!-- J2:{vp["id"]} head start' in site and site.index('name="viewport"') < site.index("</head>")
    assert os.path.exists(os.path.join(run.dir, "sections.json")) and run.write_lock is None
    # revises: a new workflow rewrites W-2's section and becomes its owner
    run.budget, run.p_refused = 500, {}
    reg, refused, _ = run._register([{"name": "Core sections rework", "goal_gap": "tighter copy", "outputs": ["W-2"], "atoms": ATOM,
                                      "completion_check": "same items", "parts": ["fix"], "revises": "W-2"}])
    assert reg and not refused and reg[0]["section"] == "W-2" and reg[0]["revises"] == "W-2", (reg, refused)
    run._turn_workflow_agent({"wid": reg[0]["id"]})
    assert run.sections["W-2"]["owner"] == reg[0]["id"] and f"(owner {reg[0]['id']})" in run.sites[-1]
    # past retry_limit: the agent reports the failure to Coordination and its section is unchanged
    reg, _, _ = run._register([{"name": "Broken one", "goal_gap": "x", "outputs": ["y"], "completion_check": "z", "atoms": ATOM,
                                "parts": ["fix"], "fixes": ["F-9"]}])
    run.call = lambda fn, *a, **k: "no blocks at all"
    n = len(run.sites)
    run._turn_workflow_agent({"wid": reg[0]["id"]})
    assert reg[0]["status"] == "failed" and len(run.sites) == n and run.turn == "coordination", reg[0]
    assert run.chat[-1]["who"] == reg[0]["id"] and "failed" in run.chat[-1]["text"]
    show(run)


def same_failure():
    """C: Audit fails item 1 every time; the same failure twice in a row pauses with keep / drop / ship. Drop
    removes the item, Audit re-checks, the site is workable."""
    def failing_run():
        run = j2.J2Run()
        orig = run.call

        def call(fn, fmt, task, mock, **k):
            r = orig(fn, fmt, task, mock, **k)
            if fn == "audit" and "findings" in r:          # not Audit's dispute turns
                f = next((x for x in r["findings"] if x["item"] == 1), None)    # charter item 1, the menu
                if f and "menu" in f["criterion"].lower():
                    f.update(verdict="NEEDS_REVISION", evidence="Prices missing")
            if fn == "adaptation" and "WHY YOU ARE UP" in task and run.audits and not run.audits[-1]["results"][0]["pass"]:
                r = {"say": "@Priority Menu fix.", "act": "PROPOSE", "next": "Priority", "workflows": j2.with_atoms([
                    {"name": "Menu fix", "goal_gap": "prices", "parts": ["fix"], "fixes": ["F-1"], "outputs": ["menu"],
                     "completion_check": "prices"}])}
            return r
        run.call = call
        return run
    run = failing_run()
    say(run, BREW_LAB)
    assert run.paused and run.paused["kind"] == "limit" and "same failure" in run.paused["handoff"]["limit"], run.outcome
    opts = run.paused["questions"][0]["options"]
    assert run.paused["handoff"]["choices"] == ["continue", "drop", "ship"] and len(opts) == 3, opts
    say(run, "2, drop it")
    assert run.outcome.startswith("Done") and run.goal["dropped_by_requester"][0].startswith("The menu"), run.outcome
    assert summary(run)["dropped_by_requester"]
    only_identity_addresses_user(run)

    run2 = failing_run()
    say(run2, BREW_LAB)
    say(run2, "3, ship it as is")
    s = summary(run2)
    assert run2.outcome.startswith("Done with open items") and s["status"] == "done_with_open_items" and s["workable"], run2.outcome


def cycle_limit():
    """C: J2_MAX_CYCLES=1. Audit fails the phone item in cycle 1, so the next cycle would pass the limit: Identity
    asks. "Keep working" gives a fresh allowance and the run goes on to a workable site."""
    old, j2.MAX_CYCLES = j2.MAX_CYCLES, 1
    try:
        run = j2.J2Run()
        say(run, BREW_LAB)
        assert run.paused and run.paused["kind"] == "limit" and "1 cycles" in run.paused["handoff"]["limit"], run.outcome
        assert not run.paused["questions"][0].get("budget"), "no budget to add when the budget isn't the limit"
        say(run, "Option 1, keep going")
        assert run.outcome.startswith("Done") and run.decisions[-1]["decision"] == "continue", run.outcome
    finally:
        j2.MAX_CYCLES = old


def to_be_confirmed():
    """C / A.2: the Requester can't give the menu prices yet. Item 1 is to be confirmed, so it fails at Audit and the
    site isn't workable; once only that is left, Identity asks; the Requester gives the prices; workable."""
    run = j2.J2Run()
    orig = run.call

    def call(fn, fmt, task, mock, **k):
        r = orig(fn, fmt, task, mock, **k)
        if fn == "identity" and task.startswith("REQUESTER'S BRIEF") and r.get("goal"):
            r["goal"]["to_be_confirmed"] = [{"item": 1, "fact": "the real menu prices"}]
        return r
    run.call = call
    say(run, BREW_LAB)
    assert run.goal["to_be_confirmed"][0]["criterion"] == run.goal["done_when"][0]
    first = run.audits[0]["results"][0]
    assert first["verdict"] == "TO_BE_CONFIRMED" and not first["pass"], first
    assert run.paused and run.paused["kind"] == "limit" and run.paused["handoff"]["limit"].startswith("Only you"), \
        (run.paused or {}).get("handoff", {}).get("limit") or run.outcome
    say(run, "1. Espresso 120, latte 180")
    assert not run.goal["to_be_confirmed"] and run.goal["confirmed_facts"], run.goal
    add_budget_if_asked(run)
    assert run.outcome.startswith("Done"), run.outcome


def bargain_time():
    """C / A.4: the J2.c bargain is bounded by time too; at 0 minutes the first COUNTER goes straight to Identity."""
    old, j2.BARGAIN_MINUTES = j2.BARGAIN_MINUTES, 0
    try:
        run = j2.J2Run()
        say(run, BREW_LAB)
        c = run.conflicts[0]
        assert c["escalated"] and c["attempts_before_escalation"] == 1 and "minute" in c["escalated_because"], c
        add_budget_if_asked(run)
        assert run.outcome.startswith("Done"), run.outcome
    finally:
        j2.BARGAIN_MINUTES = old


def workable_unit():
    ok = {"results": [{"item": 1, "id": "F-1", "verdict": "PASS", "criterion": "a", "pass": True}],
          "mechanical": {"available": True, "phone": {"overflow_px": 0}, "desktop": {"overflow_px": 0}, "js_errors": [],
                         "broken_in_page_links": [], "form_results": [{"index": 1, "ok": True}]}}
    assert j2.workable(ok) == []
    bad = json.loads(json.dumps(ok))
    bad["mechanical"]["phone"]["overflow_px"] = 40
    bad["mechanical"]["form_results"] = [{"index": 1, "ok": False, "has_submit": False, "errors_during": []}]
    assert j2.workable(bad) == ["phone overflow 40px", "form 1 has no submit button"], j2.workable(bad)
    off = {**ok, "mechanical": {"available": False, "note": "Chrome not found"}}
    assert j2.workable(off)[0].startswith("render check didn't run"), "unverified must not count as workable"


def memory():
    """D: a fix Audit confirms becomes a lesson; the next run's Adaptation reads it and says which one it used;
    J2_MEMORY=0 reads and writes nothing; clear_lessons empties the file."""
    tmp = tempfile.mkdtemp()
    old, j2.MEMORY_FILE = j2.MEMORY_FILE, os.path.join(tmp, "lessons.jsonl")
    os.environ["J2_MEMORY"] = "1"
    try:
        run = j2.J2Run()
        say(run, BREW_LAB)                 # cycle 1 fails the phone item, the viewport fix closes it in cycle 2
        lessons = j2.load_lessons()
        assert lessons and lessons[0]["run"] == run.run_id and all(lessons[0][k] for k in ("problem", "cause", "fix"))
        assert any(m.get("act") == "LESSON" for m in run.chat) and run.lessons_saved
        run2 = j2.J2Run()
        say(run2, BREW_LAB)
        m = next(m for m in run2.chat if m.get("lesson_used"))
        assert m["who"] == "adaptation" and m["lesson_used"] in m["text"] and run2.lessons_used, m
        assert summary(run2)["lessons"]["used"][0]["lesson"] == m["lesson_used"]
        n = len(j2.load_lessons())
        os.environ["J2_MEMORY"] = "0"
        run3 = j2.J2Run()
        say(run3, BREW_LAB)
        assert not run3.memory and not any(x.get("lessons_offered") or x.get("act") == "LESSON" for x in run3.chat)
        os.environ["J2_MEMORY"] = "1"
        assert len(j2.load_lessons()) == n, "J2_MEMORY=0 wrote a lesson"
        assert j2.clear_lessons() == n and j2.load_lessons() == [] and j2.clear_lessons() == 0
    finally:
        j2.MEMORY_FILE = old
        os.environ["J2_MEMORY"] = "0"


def forced_fail():
    """F: J2_FORCE_AUDIT_FAIL=2 forces item 2 to NEEDS_REVISION in cycle 1 only, marked as a test. Identity sends it
    back, Adaptation proposes a fix, its workflow agent runs, Audit re-checks for real, the lesson is saved (flagged
    as a test lesson, so later runs don't read it). Off when unset; an item number the charter lacks is ignored."""
    tmp = tempfile.mkdtemp()
    old, j2.MEMORY_FILE = j2.MEMORY_FILE, os.path.join(tmp, "lessons.jsonl")
    os.environ.update(J2_MEMORY="1", J2_FORCE_AUDIT_FAIL="2")
    try:
        run = j2.J2Run()
        run.budget = 150      # room for the extra fix in both modes (J2_FIXES=1 also funds the stories)
        say(run, BREW_LAB)
        add_budget_if_asked(run)
        first, last = run.audits[0], run.audits[-1]
        r1 = next(x for x in first["results"] if x["item"] == 2)
        assert r1["verdict"] == "NEEDS_REVISION" and r1["forced_test"] and r1["real_verdict"].startswith("PASS"), r1
        assert r1["note"] == j2.forced_note(r1["criterion"]) and "Sunday" in r1["note"], r1["note"]   # item 2: hours
        # humans see the test: the red note, the tag, chat.jsonl and summary.json
        assert any(m.get("test") and m["text"].startswith("TEST SWITCH J2_FORCE_AUDIT_FAIL=2") for m in run.chat)
        audit_msg = next(m for m in run.chat if m["who"] == "audit")
        assert audit_msg.get("forced_test") == 2 and "F-2 item 2 NEEDS_REVISION" in audit_msg["text"], audit_msg["text"]
        with open(os.path.join(run.dir, "chat.jsonl"), encoding="utf-8") as f:
            assert json.loads(f.readline())["force_audit_fail"] == 2
        # agents can't tell: no prompt or reply format of any AI call carries a test label or Audit's real verdict
        with open(os.path.join(run.dir, "calls.jsonl"), encoding="utf-8") as f:
            calls = [json.loads(ln) for ln in f]
        for c in calls:
            seen = (c["system"] + c["prompt"]).lower()
            for bad in ("forced test", "test switch", "j2_force_audit_fail", "forced_test", "real_verdict", "own verdict",
                        "test failure", "not a real finding"):
                assert bad not in seen, (c["id"], c["fn"], bad)
        ident = next(c for c in calls if c["fn"] == "identity" and "AUDIT'S FINDINGS" in c["prompt"])
        assert r1["note"] in ident["prompt"], "Identity must see the forced finding as a normal one"
        fix = next(w for w in run.workflows if w["name"] == "Fix item 2")
        assert fix["status"] == "done" and fix["revises"] == "W-2" and fix["cycle"] > 1, fix
        r2 = next(x for x in last["results"] if x["item"] == 2)
        assert last["cycle"] > 1 and r2["verdict"] == "PASS" and not r2.get("forced_test"), r2   # the re-check is real
        assert sum(1 for a in run.audits for x in a["results"] if x.get("forced_test")) == 1, "forced more than once"
        assert run.outcome.startswith("Done"), run.outcome
        test_lessons = [x for x in j2.load_lessons() if x.get("test")]
        assert test_lessons and fix["id"] in test_lessons[0]["workflows"], j2.load_lessons()
        assert not any(x.get("test") for x in j2.relevant_lessons(j2.load_lessons(), "forced test failure item opening hours"))
        s = summary(run)
        assert s["force_audit_fail"] == 2 and s["status"] == "done", s
        os.environ["J2_FORCE_AUDIT_FAIL"] = "99"            # no such item: a warning, nothing forced
        run = j2.J2Run()
        say(run, BREW_LAB)
        add_budget_if_asked(run)
        assert any("J2_FORCE_AUDIT_FAIL=99 ignored" in m["text"] for m in run.chat) and run.outcome.startswith("Done")
        os.environ.pop("J2_FORCE_AUDIT_FAIL")                # unset: off
        run = j2.J2Run()
        assert run.force_fail == 0 and run.snapshot()["force_audit_fail"] is None
    finally:
        j2.MEMORY_FILE = old
        os.environ["J2_MEMORY"] = "0"
        os.environ.pop("J2_FORCE_AUDIT_FAIL", None)


def test_lessons():
    """J2_MEMORY_TEST_LESSONS=1 (demo only) lets Adaptation read test lessons at J2.b; by default they're filtered.
    A used test lesson is flagged in the chat (tag + TEST LESSON note) and on Adaptation's lane."""
    tmp = tempfile.mkdtemp()
    old, j2.MEMORY_FILE = j2.MEMORY_FILE, os.path.join(tmp, "lessons.jsonl")

    def only_test_lesson():
        with open(j2.MEMORY_FILE, "w") as f:
            f.write(json.dumps({"id": "L-test-1", "test": True, "problem": "Layout works on a phone: no viewport meta "
                                "tag", "cause": "forced test failure", "fix": "Viewport fix", "run": "x"}) + "\n")
    only_test_lesson()
    os.environ["J2_MEMORY"] = "1"
    try:
        run = j2.J2Run()                                    # default: the test lesson is never offered
        say(run, BREW_LAB)
        add_budget_if_asked(run)
        assert not run.test_lessons and not any(m.get("lessons_offered") for m in run.chat), "test lesson offered"
        os.environ["J2_MEMORY_TEST_LESSONS"] = "1"
        only_test_lesson()                                  # drop the real lesson the first run saved
        run = j2.J2Run()
        say(run, BREW_LAB)
        add_budget_if_asked(run)
        m = next(m for m in run.chat if m.get("lesson_used"))
        assert m["lesson_used"] == "L-test-1" and m["lesson_test"] and m["who"] == "adaptation", m
        assert any(x.get("test") and x["text"].startswith("TEST LESSON: Adaptation used L-test-1") for x in run.chat)
        snap = run.snapshot()
        lane = next(x for x in snap["lanes"] if x["id"] == "adaptation")
        assert snap["test_lessons"] and lane["test_lesson"] == "L-test-1", lane
        s = summary(run)
        assert s["test_lessons"] and s["lessons"]["used"][0]["test"], s["lessons"]
    finally:
        j2.MEMORY_FILE = old
        os.environ["J2_MEMORY"] = "0"
        os.environ.pop("J2_MEMORY_TEST_LESSONS", None)


def summary_before_review():
    """summary.json is written the moment a run ends, before the slow reviewer call (runs/j2-20261007-134200 had none
    for 98 s after "Done", and none at all if the server stopped then). Also when the reviewer fails or a turn crashes."""
    run = j2.J2Run()
    seen = []

    def review(metrics):
        seen.append(os.path.exists(os.path.join(run.dir, "summary.json")))
        raise RuntimeError("reviewer down")
    run._review = review
    say(run, BREW_LAB)
    add_budget_if_asked(run)
    assert seen and all(seen), seen
    assert summary(run)["status"] == "done" and "Reviewer call failed" in run.report["review"]["verdict"]
    run = j2.J2Run()                                     # a crash mid-run still leaves summary.json
    run._turn_coordination = lambda h: (_ for _ in ()).throw(RuntimeError("boom"))
    say(run, BREW_LAB)
    assert run.outcome.startswith("Crashed") and summary(run)["status"] == "crashed", run.outcome


SIMPLE_FORBIDDEN = re.compile(r"\b(Identity|Adaptation|Priority|Coordination|Audit|Validator|Builder|Requester)\b|J2|"
                              r"budget|\bW-\d|@|\bcycles?\b|AI calls?|\bmock\b|charter|done[-_ ]when|workflow|\bthe you\b",
                              re.I)
SIMPLE_FORBIDDEN_CASE = re.compile(r"\b(COUNTER|GRANT|REFUSE|Clause|NEEDS_REVISION|PASS)\b"
                                   r"|\b(?:after|before|by|from|until|than) the team\b")   # e.g. "after Audit" -> not "after the team"


def simple_text(base):
    """Visible text of the Simple view (#sview) after the page has rendered, from headless Chrome's DOM."""
    import html.parser
    import subprocess
    chrome = j2.j2_check.find_chrome()
    out = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--virtual-time-budget=6000", "--dump-dom",
                          base + "/?view=simple"], capture_output=True, text=True, timeout=90).stdout

    class P(html.parser.HTMLParser):
        depth, skip, text, buttons = 0, 0, [], []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if self.depth or a.get("id") == "sview":
                self.depth += 1
                if tag in ("script", "style") or "hidden" in a:
                    self.skip += 1
                if tag == "button":
                    self.buttons.append(a)

        def handle_endtag(self, tag):
            if self.depth:
                self.depth -= 1
                if self.skip and tag in ("script", "style"):
                    self.skip -= 1

        def handle_data(self, d):
            if self.depth and not self.skip:
                self.text.append(d)
    p = P()
    p.text, p.buttons = [], []
    p.feed(out)
    body = re.search(r'<body class="([^"]*)"', out)
    return " ".join(" ".join(p.text).split()), p.buttons, (body.group(1).split() if body else [])


def simple_view():
    """G: the Simple view in five states. Plain words only; options are buttons; ready card when done."""
    import threading
    import j2_server
    if not j2.j2_check.find_chrome():
        print("Simple view test skipped: Chrome not found")
        return
    srv = j2_server.http.server.ThreadingHTTPServer(("127.0.0.1", 0), j2_server.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    keep = j2_server.RUN

    def check(run, *want, opts=0, once=(), site=None):
        j2_server.RUN = run
        text, buttons, cls = simple_text(base)
        bad = SIMPLE_FORBIDDEN.findall(text) + SIMPLE_FORBIDDEN_CASE.findall(text)
        assert not bad, (bad, text[:600])
        for w in want:
            assert w in text, (w, text[:600])
        assert sum(1 for b in buttons if b.get("data-opt")) >= opts, (opts, buttons)
        for w in once:                         # a question with buttons is shown once, not also as a numbered list
            assert text.count(w) == 1, (w, text.count(w), text[-500:])
        if site is not None:                   # phone: the Chat | Preview toggle only once a site exists
            assert ("has-site" in cls) == site, cls
        return text
    try:
        os.environ["J2_FIXES"] = "0"
        check(j2.J2Run(), "Describe the website you want", "A website for my cafe", "Understanding your request",
              site=False)
        run = j2.J2Run()
        say(run, "a website for my cafe")
        check(run, "Your website team", "What is the business called", site=False)          # J2.a questions
        say(run, "It's called Little Fig, in Koramangala, Bengaluru. Visitors should see our menu with prices, opening "
                 "hours and where to find us. Cozy and simple, and it must work on phones.")
        check(run, opts=2, once=("Do you want a section about your coffee's story?",
                                 "Add a section about your coffee's story (takes a bit longer)",
                                 "Keep it simple, no story section"))                       # a conflict: once, as buttons
        say(run, "Option 2")
        check(run, "Your website is ready", "Open full screen", "Download the HTML file", "Ask for a change",
              "Keep it simple, no story section", site=True)                                # the chosen label shows
        os.environ["J2_FIXES"] = "1"
        run = j2.J2Run()
        run.budget = 85
        say(run, BREW_LAB)
        say(run, "Option 1")                                                                 # ruling: add effort
        assert run.paused and run.paused["kind"] == "limit", run.outcome
        check(run, opts=2, once=("Add more and keep going, leave out the missing parts, or finish as it is?",
                                 "Finish as it is: you get the site as it is now"))
        # (c) the Simple view shows only messages for you: no agent-tagged message, no agent content
        text = check(run, opts=2)
        for m in run.chat:
            if m["who"] == "identity" and not m.get("to_user"):
                body = re.sub(r"^@[\w-]+[,:]?\s*", "", m["text"])[:40]
                assert body not in text, ("agent message in the Simple view", m["text"][:80])
        # (d) the Detailed view shows both parts of a reply, each labelled with who it is for
        import subprocess
        dom = subprocess.run([j2.j2_check.find_chrome(), "--headless=new", "--disable-gpu", "--virtual-time-budget=6000",
                              "--dump-dom", base + "/?view=detail"], capture_output=True, text=True, timeout=90).stdout
        assert "for Requester (you)" in dom and "for Adaptation" in dom, "Detailed view must label both audiences"
    finally:
        j2_server.RUN = keep
        srv.shutdown()
        os.environ["J2_FIXES"] = "0"


def work_atoms():
    """Adaptation writes each workflow's work atom (goal, constraints, context, how, verification). The validator
    rejects a workflow whose atom lacks a field, naming it, and Adaptation gets one retry; still incomplete after it,
    the workflow is dropped. Registered workflows store their atoms (W-n.a1) and each build call is tagged with one."""
    run = j2.J2Run()
    say(run, BREW_LAB)
    assert run.outcome.startswith("Done"), run.outcome
    assert run.workflows and not [x for x in run.rejections if "atom" in x["reason"]], run.rejections
    for w in run.workflows:
        assert [a["id"] for a in w["atoms"]] == [f"{w['id']}.a1"] and not j2.atom_missing(w), w
    saved = json.load(open(os.path.join(run.dir, "workflows.json"), encoding="utf-8"))
    assert all(x["atoms"] == w["atoms"] for x, w in zip(saved, run.workflows)), "atoms not in workflows.json"
    built = [c for c in run.call_log if j2.is_wf_agent(c["fn"])]
    assert built and all(c["atom"] == f"{c['fn']}.a1" for c in built), [(c["fn"], c.get("atom")) for c in built]
    assert not any("atom" in c for c in run.call_log if not j2.is_wf_agent(c["fn"]))
    assert "WORK ATOMS" in next(c["prompt"] for c in calls_of(run) if c["fn"] == "adaptation")

    def broken(field, times):
        run, orig, asked = j2.J2Run(), None, []
        orig = run.call

        def call(fn, fmt, task, mock, **k):
            r = orig(fn, fmt, task, mock, **k)
            if fn == "adaptation" and isinstance(r, dict) and r.get("workflows") and len(asked) < times:
                asked.append(task)
                a = r["workflows"][0]["atoms"][0]
                a[field] = [] if field == "verification" else a.pop(field) and None
            return r
        run.call = call
        say(run, BREW_LAB)
        return run, asked
    for f in j2.ATOM_FIELDS:
        run, asked = broken(f, 1)
        assert len(asked) == 1 and run.rejections[0]["reason"] == f"missing {f} in work atom 1", (f, run.rejections)
        retry = [c for c in calls_of(run) if c["fn"] == "adaptation" and "THE VALIDATOR REJECTED" in c["prompt"]]
        assert len(retry) == 1 and f in retry[0]["prompt"], f
        assert run.outcome.startswith("Done") and all(not j2.atom_missing(w) for w in run.workflows), f
    run, asked = broken("goal", 2)                      # still missing after the one retry: dropped, not retried again
    first = run.rejections[0]["workflow"]
    assert [x["workflow"] for x in run.rejections[:2]] == [first, first], run.rejections
    assert len([c for c in calls_of(run) if "THE VALIDATOR REJECTED" in c["prompt"]]) == 1
    # dropping the scaffold left N8 (the nav) with no workflow: the plan is flagged and re-asked, and the clean reply
    # brings it back
    assert any(x["workflow"] == "plan" and "N8" in x["reason"] for x in run.rejections), run.rejections
    assert first in [w["name"] for w in run.workflows if w["cycle"] == 1], first
    # the validator itself: no atoms at all, or an empty verification list, is rejected with the field named
    reg, refused, _ = run._register([{"name": "Bare", "goal_gap": "x", "outputs": ["y"], "completion_check": "z",
                                      "parts": ["fix"], "fixes": ["F-9"]}])
    assert not reg and refused == ["Bare (missing atoms)"], refused


def work_atom_cards():
    """Detailed view: opening a workflow lists its work atoms as cards (one atom opens expanded, two open collapsed),
    each with six plain rows and its own Run details listing only the calls tagged with that atom."""
    import html as htmllib
    import subprocess
    import threading
    import j2_server
    chrome = j2.j2_check.find_chrome()
    if not chrome:
        print("work atom cards test skipped: Chrome not found")
        return
    run = j2.J2Run()
    say(run, BREW_LAB)
    w1, w2 = run.workflows[0], run.workflows[1]
    w1["atoms"].append({**w1["atoms"][0], "id": "W-1.a2", "goal": "The second atom's goal holds"})
    other = next(c for c in run.call_log if c["fn"] == "priority")
    other["atom"] = "W-1.a2"
    mine = [c["id"] for c in run.call_log if c.get("atom") == "W-1.a1"]
    assert mine
    keep, j2_server.RUN = j2_server.RUN, run
    srv = j2_server.http.server.ThreadingHTTPServer(("127.0.0.1", 0), j2_server.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        dom = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000", "--dump-dom",
                              f"http://127.0.0.1:{srv.server_address[1]}/?view=detail"],
                             capture_output=True, text=True, timeout=120).stdout
    finally:
        j2_server.RUN = keep
        srv.shutdown()

    def block(key):              # the <details data-key=key> element's HTML (balanced on nested details)
        i = dom.index(f'data-key="{key}"')
        i, depth, j = dom.rindex("<details", 0, i), 0, i
        for m in re.finditer(r"<details\b|</details>", dom[i:]):
            depth += 1 if m.group(0) == "<details" else -1
            if not depth:
                return dom[i:i + m.end()]
    one, two = block(f"wf-{w2['id']}"), block("wf-W-1")
    assert two.count('class="atom"') == 2 and "Work atom 1" in two and "Work atom 2" in two, two[:300]
    assert one.count('class="atom"') == 1 and re.search(r'class="atom"[^>]*\bopen\b', one), "one atom opens expanded"
    assert not re.search(r'class="atom"[^>]*\bopen\b', two), "two atoms open collapsed"
    a1 = block("atom-W-1.a1")
    for label, gloss in (("Goal", "What must be true when this is done"), ("Constraints", "What must never break"),
                         ("Context", "What it needs to know"), ("How", "Who builds it"),
                         ("Expected output", "What must exist when it is done"), ("Verification", "The check that proves the goal is met")):
        assert f"<dt>{label}<br>" in a1 and gloss in a1, label
    assert re.search(r"Passed</span>: [^<]+ <span class=\"empty\">Attempt 1 of 3", a1) and "not run" not in a1 and "{" not in re.sub(r"<[^>]+>", "", a1.split("Run details")[0])
    run1, run2 = block("run-W-1.a1"), block("run-W-1.a2")
    labels = re.findall(r"<(?:h4|summary)>([^<]*)<", run1)
    assert labels == ["Run details", "Prompt sent", "Reply received", "Reason given", "Cost", "Attempts"], labels
    assert not any(n.lower() in x.lower() for x in labels for n in j2.ATOM_FIELDS), labels
    assert all(f"call {i}<" in run1 for i in mine) and f"call {other['id']}<" not in run1, run1[:400]
    assert f"call {other['id']}<" in run2 and not any(f"call {i}<" in run2 for i in mine), run2[:400]
    pane = dom.split('id="pane-workflows"')[1].split('id="pane-conflicts"')[0]
    pane = re.sub(r"<h4>Prompt sent</h4>.*?<h4>", "", pane, flags=re.S)       # the prompt is shown as it was sent
    pane = htmllib.unescape(re.sub(r"<[^>]+>", " ", pane))
    assert "Limits" in pane and not re.search(r"envelope|done.when", pane, re.I), "plain words in the Detailed view"


def atom_checks():
    """Verification is real: the validator's check rules, code running each atom's checks into receipts.jsonl, and a
    third failed attempt going to Adaptation before Identity (Identity only for a wrong build that doesn't fit)."""
    run = j2.J2Run()
    say(run, BREW_LAB)
    finish(run)
    src, a = run._fact_source(), j2.mock_atom({"covers": [1]})
    assert not j2.check_problems(a, src), j2.check_problems(a, src)
    # facts-present: every string must come from the charter or the Requester's answers (no invented facts)
    fact = {"text": "Name and area shown", "type": "facts-present", "target": ["brew  LAB", "Indiranagar"], "expect": True}
    assert not j2.check_problems({**a, "verification": [fact]}, src)
    bad = j2.check_problems({**a, "verification": [{**fact, "target": ["Brew Lab", "+91 98450 12345"]}]}, src)
    assert len(bad) == 1 and "['+91 98450 12345'], not found in the charter" in bad[0], bad
    # counts: label and expect must agree; targets only ids and classes the atom tells the builder to create
    how = {"kind": "AI", "agent": "Builder", "steps": "Write section #events with one .event-option per event"}
    opt = {"text": "8 event options", "type": "element-count", "target": ".event-option", "expect": 9}
    bad = j2.check_problems({**a, "how": how, "verification": [opt]}, src)
    assert bad == ["check 1 says '8 event options' but expects 9"], bad
    assert not j2.check_problems({**a, "how": how, "verification": [{**opt, "expect": 8}]}, src)
    for t in ("Day 1", "hello@brewlab.in", ".untold-class"):
        bad = j2.check_problems({**a, "how": how, "verification": [{**opt, "text": "event options", "target": t}]}, src)
        assert len(bad) == 1 and "targets" in bad[0], (t, bad)
    assert j2.check_problems({**a, "verification": [{**opt, "type": "screenshot-diff"}]}, src)[0].startswith(
        "check 1 has type 'screenshot-diff'")
    # expected output: every item is covered by at least one check; an item no check can verify is rejected, and a
    # derived check follows the same rules (facts from the charter, counts only on ids the atom creates)
    cov = j2.normalise_checks([json.loads(json.dumps(j2.mock_atom({"parts": ["form"]})))])[0]
    assert all(any(c.get("item") == n for c in cov["verification"]) for n in range(1, len(cov["expected_output"]) + 1))
    assert len(cov["verification"]) == 3, cov["verification"]          # matched by type and target, not duplicated
    item = lambda **x: run._atom_problems({"atoms": [{**a, "expected_output": [{"text": "x", **x}]}]})
    assert "has kind 'heading', which no check can verify" in item(kind="heading", target="Menu")[0]
    assert "expected output item 1 facts-present lists ['+91 98450 12345']" in item(kind="facts", target=["+91 98450 12345"])[0]
    assert "expected output item 1 element-count targets '#events'" in item(kind="section", target="#events")[0]
    assert not item(kind="facts", target=["Indiranagar"]) and run._atom_problems({"atoms": [{**a, "expected_output": []}]})
    # a goal naming times whose checks only count headings is flagged, and sent back to Adaptation once
    timed = {**a, "goal": "Opening hours 8am to 9pm are listed", "how": {**how, "steps": "h2 headings, class hours-head"},
             "expected_output": [{"text": "2 hours headings", "kind": "element", "target": ".hours-head", "count": 2}],
             "verification": [{"text": "2 hours headings", "type": "element-count", "target": ".hours-head", "expect": 2}]}
    assert j2.check_problems(timed, src) == ["its goal names a time, price, number or email but no check is "
                                             "facts-present or a named test"], j2.check_problems(timed, src)

    def patched(edit, reply=lambda r, fn: r, done=True):
        """A run whose first Adaptation proposal has its first atom changed by edit (once)."""
        run, hit = j2.J2Run(), []
        orig = run.call

        def call(fn, fmt, task, mock, **k):
            r = orig(fn, fmt, task, mock, **k)
            if fn == "adaptation" and isinstance(r, dict) and r.get("workflows") and not run.workflows and not hit:
                hit.append(1)
                edit(r["workflows"][0]["atoms"][0])
            return reply(r, fn)
        run.call = call
        say(run, BREW_LAB)
        if done:
            finish(run)
        return run
    run = patched(lambda at: at.update({k: v for k, v in timed.items() if k != "context"}))
    assert "names a time, price, number or email" in run.rejections[0]["reason"], run.rejections
    assert len([c for c in calls_of(run) if "THE VALIDATOR REJECTED" in c["prompt"]]) == 1
    assert run.outcome.startswith("Done"), run.outcome

    # three failed attempts: the receipts go to Adaptation; it corrects the check and Identity is never called
    def four_cards(at):
        at["how"] = {**at["how"], "steps": "Give every card the class j2-card."}
        at["verification"].append({"text": "4 cards", "type": "element-count", "target": ".j2-card", "expect": 4})
    run = patched(four_cards)
    calls = calls_of(run)
    i = next(n for n, c in enumerate(calls) if "WORK ATOM FAILED" in c["prompt"])
    assert calls[i]["fn"] == "adaptation" and [c["fn"] for c in calls[i - 3:i]] == ["W-1"] * 3, [c["fn"] for c in calls]
    assert "ATTEMPT 3 OF 3" in calls[i - 1]["prompt"] and "0 element(s) match '.j2-card'" in calls[i - 1]["prompt"]
    nxt = next(n for n, c in enumerate(calls) if n > i and c["fn"] != "adaptation")
    assert calls[nxt]["fn"] != "identity" and not any(c["fn"] == "identity" for c in calls[i:nxt]), calls[nxt]["fn"]
    at = run._wf("W-1")["atoms"][0]
    card = [r for r in run.receipts if r["target"] == ".j2-card"]
    assert [(r["attempt"], r["expect"], r["actual"], r["pass"]) for r in card] == \
        [(1, 4, 0, False), (2, 4, 0, False), (3, 4, 0, False), (3, 0, 0, True)], card
    assert card[-1]["recheck"] == "check corrected by Adaptation" and at["status"] == "passed", at
    assert run.outcome.startswith("Done"), run.outcome
    # receipts: written by code only, one per check run, matching each atom's checks
    lines = [json.loads(x) for x in open(os.path.join(run.dir, "receipts.jsonl"), encoding="utf-8")]
    met = [r for r in lines if "expected" in r]          # per expected-output item: met or not met
    lines = [r for r in lines if "expected" not in r]
    assert met and all(r["by"] == "code" and r["met"] in (True, False, None) and r["checks"] for r in met), met[:3]
    assert lines == run.receipts and all(r["by"] == "code" and r["of"] == 3 and r["t"] for r in lines)
    for w in run.workflows:
        for x in w["atoms"]:
            ran = [(r["check"], r["type"], r["target"], r["expect"]) for r in lines
                   if r["atom"] == x["id"] and r["attempt"] == x["attempts"]][-len(x["verification"]):]
            assert ran == [(c["text"], c["type"], c["target"], c["expect"]) for c in x["verification"]], (x["id"], ran)
            assert x["results"] == [r for r in lines if r["atom"] == x["id"]][-len(x["verification"]):]
    assert not any("receipts.jsonl" in str(c.get("raw")) for c in calls), "an agent wrote a receipt"
    v = json.load(open(os.path.join(run.dir, "summary.json"), encoding="utf-8"))["verification"]
    assert v == {"passed": len(run.workflows), "failed": 0, "escalated": 0, "could_not_run": 0,
                 "checks_run": len(lines)}, v

    # a wrong build the budget left can't fix: Adaptation first, then Identity; the atom is ESCALATED
    def missing_fact(at):
        at["verification"].append({**fact, "target": ["Indiranagar"]})

    def unaffordable(r, fn):
        if fn == "adaptation" and isinstance(r, dict) and r.get("verdict") == "BUILD_WRONG":
            r["affordable"] = False
        return r
    run = patched(missing_fact, unaffordable, done=False)
    calls = calls_of(run)
    i = next(n for n, c in enumerate(calls) if "WORK ATOM FAILED" in c["prompt"])
    assert calls[i]["fn"] == "adaptation" and not any(c["fn"] == "identity" for c in calls[i - 3:i])
    assert calls[i + 1]["fn"] == "identity" and "fails its checks" in calls[i + 1]["prompt"], calls[i + 1]["fn"]
    assert run._wf("W-1")["atoms"][0]["status"] == "escalated"
    finish(run)
    v = json.load(open(os.path.join(run.dir, "summary.json"), encoding="utf-8"))["verification"]
    assert v["escalated"] == 1, v


def leave_out_named():
    """runs/j2-20261012-170632 msgs 58-63: "Leave out the 2 unfinished checklist parts" named nothing; Identity then
    told the team fees and sponsors, while code dropped sponsors and the colour scheme. Now the question lists every
    unfinished item with its run-long number, short text and status, each option says what it drops and keeps, the
    drop is exactly what the option named, and numbers never shift after a drop."""
    six = BREW_LAB.replace(", and a simple loyalty-card explainer (buy 9, get the 10th free)", "")
    run = j2.J2Run()
    say(run, six)
    finish(run)
    crit = list(run.goal["done_when"])
    assert len(crit) == 6, crit
    hours, beans = (next(i for i, c in enumerate(crit, 1) if k in c.lower()) for k in ("hours", "beans"))
    last = run.audits[-1]
    for r in last["results"]:
        if r["item"] in (hours, beans):
            r.update(verdict="NEEDS_REVISION", note="missing", **{"pass": False})
    last["rubric"] = [{"id": "R-6", "criterion": j2.RUBRIC[5][1], "verdict": "NEEDS_REVISION", "pass": False,
                       "note": "button 30px", "rubric": True}]
    run.outcome, run.done = None, False
    run._identity_limit({"reason": "The same failure came back twice."})
    q = run.paused["questions"][0]
    text = run.chat[-1]["text"]
    for i in (hours, beans):
        assert re.search(rf"\n- item {i} {re.escape(j2.short(crit[i - 1]))} \((built but failing|not built|unfunded)\)",
                         text), text
    assert "\n- Tap targets are big enough on phones (failing)" in text, text
    drop = next(o for o in q["options"] if o.startswith("Leave out"))
    named = [f"item {hours} {j2.short(crit[hours - 1])}", f"item {beans} {j2.short(crit[beans - 1])}"]
    assert drop == (f"Leave out {named[0]} and {named[1]}: you get the site without them. Tap targets are big "
                    "enough on phones stays as it is, still failing."), drop
    ship = q["options"][-1]
    assert ship.endswith(f"still not right: {named[0]}, {named[1]} and Tap targets are big enough on phones"), ship
    assert run.paused["handoff"]["drop_named"] == named
    say(run, str(q["options"].index(drop) + 1))
    d = next(x for x in reversed(run.decisions) if x.get("decision") == "drop")
    assert d["named"] == d["dropped"] == named, d                          # the dropped set is the named set
    assert [c for c in crit if c not in run.goal["done_when"]] == [crit[hours - 1], crit[beans - 1]]
    ack = next(m for m in run.chat if m.get("to_user") and "Got it. We'll leave out" in m["text"])
    assert named[0] in ack["text"] and named[1] in ack["text"], ack["text"]
    # numbers don't shift: the items after the dropped ones keep theirs, in the next audit and the next question
    for i, c in enumerate(crit, 1):
        if c in run.goal["done_when"]:
            assert run._no(c) == i and next(r["id"] for r in run.audits[-1]["results"] if r["criterion"] == c) == f"F-{i}"
    late = run.goal["done_when"][-1]
    assert run._gap_rows([late], run.audits[-1], None)[0]["name"].startswith(f"item {crit.index(late) + 1} ")
    # a typed answer names items by those numbers too
    assert j2.parse_decision("leave out F-6", {}, ["drop"], run.goal["done_when"],
                             [run._no(c) for c in run.goal["done_when"]])["drop_items"] == [6]


def rubric_and_credits():
    """Every builder's brief carries the design rubric R-1 to R-6; the section holding buttons has a tap-targets
    check code runs at 360px (it fails on a 30px button); no user-facing string says "units"."""
    run = j2.J2Run()
    say(run, BREW_LAB)
    finish(run)
    built = [c for c in calls_of(run) if j2.is_wf_agent(c["fn"])]
    assert built and all(f"{rid} {txt}" in c["prompt"] for c in built for rid, txt in j2.RUBRIC[:6])
    form = next(i for i, c in enumerate(run.goal["done_when"], 1) if j2.item_kind(c) == "form")
    w = next(w for w in run.workflows if form in run._wf_items(w))
    tap = [c for a in w["atoms"] for c in a["verification"] if c["type"] == "tap-targets"]
    assert tap and tap[0]["target"] == ".order-form" and "order-form" in json.dumps(w["atoms"][0]["how"]), w["atoms"]
    assert 'class="order-form"' in run.sites[-1] and "<button" in run.sites[-1].split('class="order-form"')[1]
    got = [r for r in run.receipts if r["type"] == "tap-targets"]
    assert got and got[-1]["pass"] and "at 360px" in got[-1]["evidence"], got
    page = ('<!doctype html><html><body><section class="order-form"><form><button type="submit" '
            'style="height:30px;width:120px">Send</button></form></section></body></html>')
    r = j2.run_check(tap[0], run.dir, page)
    assert r["pass"] is False and "1 of 1 tap target(s)" in r["evidence"] and "120x30" in r["evidence"], r
    # "units": never in the outcome, the report, summary.json or any chat message; the page uses it only to parse
    run = j2.J2Run()
    run.budget = 12
    say(run, BREW_LAB)
    say(run, "finish as it is")
    assert run.outcome.startswith("Done with open items"), run.outcome
    texts = [run.outcome, open(os.path.join(run.dir, "report.md"), encoding="utf-8").read(),
             open(os.path.join(run.dir, "summary.json"), encoding="utf-8").read()] + [m["text"] for m in run.chat]
    assert "work credits" in " ".join(texts)
    bad = [t[:200] for t in texts if re.search(r"\bunits?\b", t)]
    assert not bad, bad
    ui = [ln for ln in open(os.path.join(j2.HERE, "j2_ui.html"), encoding="utf-8") if re.search(r"\bunits\b", ln)]
    assert all(re.search(r"/[^/]*\bunits\b[^/]*/|\(\?:units", ln) for ln in ui), ui     # regex patterns only


def charter_numbers():
    """Agents' prompts and covers use each item's charter number, never its position: after item 2 is dropped, an
    agent's covers [5] still means charter item 5, and every number an agent reads is a charter number."""
    run = j2.J2Run()
    say(run, BREW_LAB)
    finish(run)
    crit = list(run.goal["done_when"])
    run._override("drop 2")
    assert crit[1] not in run.goal["done_when"] and run.goal["done_when"][1] == crit[2]   # position 2 is now item 3
    run.budget, run.p_refused = 500, {}
    reg, refused, _ = run._register([{"name": "Beans again", "goal_gap": "x", "outputs": ["x"], "completion_check": "y",
                                      "atoms": ATOM, "parts": ["page_section"], "covers": [5]}])
    assert reg and not refused, refused
    assert reg[0]["covers"] == [5] and reg[0]["covers_text"] == [crit[4]] and run._wf_items(reg[0]) == [4], reg[0]
    assert run._covers({"covers": [2]}) == [], "a dropped charter number covers nothing"
    nums = [1, 3, 4, 5, 6, 7]
    st = json.loads(run.state("adaptation"))
    assert [x["item"] for x in st["charter"]["done_when"]] == nums and "charter_items" not in st["charter"], st["charter"]
    assert [x["item"] for x in st["rate_card"]["item_minimums"]] == nums
    assert run._per_item([{"name": "x", "parts": ["page_section"], "covers": [5]}])[0]["covers"] == [5]
    run._turn_audit({"kind": "audit"})
    prompt = calls_of(run)[-1]["prompt"]
    assert '{"item": 5, "criterion": ' + json.dumps(crit[4]) in prompt and '"item": 2,' not in prompt
    assert [r["id"] for r in run.audits[-1]["results"]] == [f"F-{n}" for n in nums], run.audits[-1]["results"]
    fails = [{**r, "item": run._no(r["criterion"])} for r in run.audits[-1]["results"]]
    assert all(f["item"] == int(f["id"][2:]) for f in fails)
    # code's own proposal (cheapest fit) writes charter numbers too
    run.workflows = []
    fit = run._cheapest_fit()
    assert {i for w in fit["workflows"] for i in w["covers"]} | {x["item"] for x in fit["left_out"]} <= set(nums), fit


def chrome_unavailable():
    """No Chrome: a browser check records "could not run"; it isn't a failed attempt and nothing escalates."""
    old_env, old_tap, old_check = os.environ.get("J2_CHROME"), j2.j2_check.tap_targets, j2.j2_check.check
    os.environ["J2_CHROME"], j2.j2_check.tap_targets = "none", REAL_TAP
    j2.j2_check.check = fake_check      # Audit's render check isn't under test here (without Chrome it pauses the run)
    try:
        run = j2.J2Run()
        say(run, BREW_LAB)
        finish(run)
    finally:
        j2.j2_check.tap_targets, j2.j2_check.check = old_tap, old_check
        if old_env is None:
            os.environ.pop("J2_CHROME", None)
        else:
            os.environ["J2_CHROME"] = old_env
    tap = [r for r in run.receipts if r["type"] == "tap-targets"]
    assert tap and all(r["pass"] is None and r["evidence"].startswith("could not run") for r in tap), tap
    assert all(r["attempt"] == 1 for r in tap), "a check that could not run isn't retried"
    a = next(a for w in run.workflows for a in w["atoms"] if any(c["type"] == "tap-targets" for c in a["verification"]))
    assert a["status"] == "could not run" and a["attempts"] == 1, a
    assert not any("WORK ATOM FAILED" in c["prompt"] for c in calls_of(run)), "it went to Adaptation"
    assert not any(e["type"] == "atom_escalated" for e in run.events)
    v = json.load(open(os.path.join(run.dir, "summary.json"), encoding="utf-8"))["verification"]
    assert v["could_not_run"] == 1 and v["failed"] == v["escalated"] == 0, v
    assert run.outcome.startswith("Done"), run.outcome


def unique_short_names():
    """Short item names are unique within a list: items sharing their first 7 words get longer names until they
    differ (past the first clause if need be), in the leave-out question too."""
    a = "Each event card shows its fee and the room for events in Hall A"
    b = "Each event card shows its fee and the room for events in Hall B"
    names = j2.shorts([a, b, "Opening hours are listed"])
    assert names == [a, b, "Opening hours are listed"], names
    g = ["A gallery: photos of the shop, outside", "A gallery: photos of the team"]
    assert len(set(j2.shorts(g))) == 2 and all(n.startswith("A gallery: photos of the") for n in j2.shorts(g))
    assert j2.shorts(["The menu with prices is shown", "Opening hours are listed"]) == \
        ["The menu with prices is shown", "Opening hours are listed"], "names that already differ stay short"
    run = j2.J2Run()
    say(run, BREW_LAB)
    finish(run)
    run.goal["done_when"] += [a, b]
    gaps = [a, b, run.goal["done_when"][0]]
    rows = run._gap_rows(gaps, run.audits[-1], None)
    shown = [r["name"].split(" ", 1)[1] for r in rows]
    assert len(set(shown)) == 3 and shown[0].endswith("Hall A") and shown[1].endswith("Hall B"), shown


def detail_stays_open():
    """The Detailed view re-renders on every poll. An opened screenshot (under Audit), the report's event log, and an
    opened message detail view (with its full text) must stay open while the run changes, until the user closes them.
    Real browser: the page opens them, then the server changes the run (a new audit and a new message) mid-test."""
    import html as htmllib
    import shutil
    import subprocess
    import threading
    import j2_server
    chrome = j2.j2_check.find_chrome()
    if not chrome:
        print("detail view test skipped: Chrome not found")
        return
    run = j2.J2Run()
    say(run, BREW_LAB)
    add_budget_if_asked(run)
    v = run.audits[-1]["version"]
    os.makedirs(os.path.join(run.dir, "site", "shots"), exist_ok=True)
    shutil.copy(os.path.join(j2.HERE, "docs", "ui-simple-start-390.png"), os.path.join(run.dir, "site", "shots", f"v{v}.png"))
    run.audits[-1]["screenshot"] = f"site/shots/v{v}.png"
    msg = next(m["id"] for m in run.chat if m.get("calls"))
    # found by their visible text, so the same test also runs against an older page
    hook = ("const pick = (pane, t) => [...document.querySelectorAll(pane + ' details')].find(d => d.textContent.includes(t));\n"
            "setTimeout(async () => { const q = s => document.querySelector(s);\n"
            "  pick('#pane-audit', 'Screenshot').open = true; pick('#pane-report', 'Event log').open = true;\n"
            f"  await openDetail({msg}); q('#full').open = true;\n"
            "  await fetch('/test/bump');   // the server changes the run: a new audit and a new message\n"
            "  setTimeout(() => { document.body.dataset.r = JSON.stringify({shot: !!pick('#pane-audit', 'Screenshot')?.open,"
            " events: !!pick('#pane-report', 'Event log')?.open, dialog: q('#detail').open, full: q('#full').open,"
            " audits: q('#pane-audit').innerText.split('Cycle ').length - 1}); }, 4000); }, 1500);")
    ui = open(os.path.join(j2.HERE, "j2_ui.html"), encoding="utf-8").read().replace("poll();\n</script>", f"poll();\n{hook}\n</script>")
    orig = j2_server.Handler.do_GET

    def do_GET(self):
        if self.path.startswith("/?"):
            return self._send(200, ui, "text/html")
        if self.path == "/test/bump":
            run.audits.append({**run.audits[-1], "version": v, "cycle": run.audits[-1]["cycle"] + 1})
            run.post("system", "A new message while the detail view is open.")
            return self._send(200, "{}")
        return orig(self)
    j2_server.Handler.do_GET = do_GET
    keep, j2_server.RUN = j2_server.RUN, run
    srv = j2_server.http.server.ThreadingHTTPServer(("127.0.0.1", 0), j2_server.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        before = len(run.audits)
        out = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--virtual-time-budget=12000", "--dump-dom",
                              f"http://127.0.0.1:{srv.server_address[1]}/?view=detail"],
                             capture_output=True, text=True, timeout=120).stdout
        m = re.search(r'data-r="([^"]*)"', out)
        assert m, "the page never reported"
        r = json.loads(htmllib.unescape(m.group(1)))
        assert len(run.audits) == before + 1 and r["audits"] == before + 1, (r, "the Audit pane didn't re-render")
        assert r == {**r, "shot": True, "events": True, "dialog": True, "full": True}, r
    finally:
        j2_server.Handler.do_GET = orig
        j2_server.RUN = keep
        srv.shutdown()


def plain_words():
    """The Simple view's word list (fallback only): Audit becomes "our checks", never "the team", so nothing reads
    "after the team"; other function names become "the team"; budget becomes effort. Runs the page's own JS in node."""
    import shutil
    import subprocess
    if not shutil.which("node"):
        print("plain-words check skipped: node not found")
        return
    with open(os.path.join(j2.HERE, "j2_ui.html"), encoding="utf-8") as f:
        ui = f.read()
    js = ui[ui.index("const AGENT ="):ui.index("const STAGES =")]
    cases = {"only 10 units stay for fixes after Audit": "Only 10 work credits stay for fixes after our checks",
             "Every done-when item passes with Audit's evidence.": "Every checklist item passes with our checks' evidence.",
             "@Adaptation Priority's final answer was COUNTER.": "The team's final answer was a smaller offer.",
             "The Requester picked; the budget is over budget.": "You picked; the effort is more than planned."}
    out = subprocess.run(["node", "-e", js + "\nconst c = " + json.dumps(list(cases)) +
                          ";\nprocess.stdout.write(JSON.stringify(c.map(plain)));"], capture_output=True, text=True)
    got = json.loads(out.stdout or "null") or sys.exit(out.stderr)
    for (src, want), g in zip(cases.items(), got):
        assert g == want, (src, g, want)
        assert not re.search(r"\b(?:after|before|by|from|until|than) the team\b", g), g


def identity_prompt_is_plain():
    """Item 1: every Identity call carries the plain-language rule for what it writes to the Requester; no one else's."""
    run = j2.J2Run()
    say(run, BREW_LAB)
    add_budget_if_asked(run)
    with open(os.path.join(run.dir, "calls.jsonl"), encoding="utf-8") as f:
        calls = [json.loads(ln) for ln in f]
    assert any(c["fn"] == "identity" for c in calls)
    for c in calls:
        assert ("college student with no tech background" in c["prompt"]) == (c["fn"] == "identity"), (c["id"], c["fn"])


FLORIST = "A website for Petal & Stem, a florist in Jaipur"


def calls_of(run):
    with open(os.path.join(run.dir, "calls.jsonl"), encoding="utf-8") as f:
        return [json.loads(ln) for ln in f]


def style_guide():
    """H: the first workflow that runs writes the style guide (retrying within its envelope if it leaves it out);
    code puts it first in the head; every later workflow agent gets it and is told to follow it."""
    run = j2.J2Run()
    orig, dropped = run.call, []

    def call(fn, fmt, task, mock, **k):              # W-1's first reply leaves the style guide out: it retries
        raw = orig(fn, fmt, task, mock, **k)
        if fn == "W-1" and not dropped:
            dropped.append(1)
            raw = re.sub(r"```style.*?```", "", raw, flags=re.S)
        return raw
    run.call = call
    say(run, BREW_LAB)
    add_budget_if_asked(run)
    w1 = run._wf("W-1")
    assert run.style and run.style["palette"]["primary"] and w1["retries_used"] == 1 and w1.get("style_guide"), w1
    assert list(run.sections)[0] == "style" and run.sections["style"]["owner"] == "W-1"
    site = run.sites[-1]
    assert "--j2-primary" in site and site.index("<!-- J2:style head start") < site.index("</head>")
    assert os.path.exists(os.path.join(run.dir, "style.json")) and run.snapshot()["style"] == run.style
    cs = calls_of(run)
    w1_calls = [c for c in cs if c["fn"] == "W-1"]
    assert all("YOU RUN FIRST, SO YOU ALSO WRITE THE STYLE GUIDE" in c["prompt"] for c in w1_calls), "W-1 not told"
    later = [c for c in cs if j2.is_wf_agent(c["fn"]) and c["fn"] != "W-1"]
    assert later and all("STYLE GUIDE (follow it exactly)" in c["prompt"] for c in later), [c["fn"] for c in later]
    assert any("the reply has no ```style block" in m["text"] for m in run.chat), "retry reason not shown"


def rubric_loop():
    """H: W-2's first build has a tap target too small for a phone. Code measures it, Audit's R-6 can't pass, the
    site isn't workable, Identity sends it back, Adaptation proposes a fix, the re-check passes, Done."""
    if not j2.j2_check.find_chrome():
        print("rubric loop skipped: Chrome not found")
        return
    run = j2.J2Run()
    run.budget = 150      # room for the extra fix in both modes (J2_FIXES=1 also funds the stories)
    orig, planted = run.call, []

    def call(fn, fmt, task, mock, **k):
        raw = orig(fn, fmt, task, mock, **k)
        if fn == "W-2" and not planted:
            planted.append(1)
            raw = raw.replace("```section\n", '```section\n<a href="https://example.com" style="display:inline-block;'
                                              'font-size:10px">Book</a>\n', 1)
        return raw
    run.call = call
    say(run, BREW_LAB)
    add_budget_if_asked(run)
    first, last = run.audits[0], run.audits[-1]
    assert [r["id"] for r in first["rubric"]] == [rid for rid, _ in j2.RUBRIC]
    r6 = next(r for r in first["rubric"] if r["id"] == "R-6")
    assert r6["verdict"] == "NEEDS_REVISION" and r6["note"].startswith("Measured by code") and "Book" in r6["note"], r6
    assert any(x.startswith("design rubric R-6") for x in j2.workable(first))
    fix = next(w for w in run.workflows if w["name"] == "Fix item R-6")
    assert fix["status"] == "done" and fix["revises"] == "W-2", fix
    assert next(r for r in last["rubric"] if r["id"] == "R-6")["pass"] and run.outcome.startswith("Done"), run.outcome
    assert any("DESIGN AND USABILITY RUBRIC" in c["prompt"] for c in calls_of(run) if c["fn"] == "audit")


def lone_rubric_failure():
    """Bug from runs/j2-20261007-184146: the first audit's only failure was R-6 (tap targets), with budget left in
    cycle 1, and the run paused with a limit question. A normal failure with budget left must loop back to J2.b
    without asking the Requester: Adaptation proposes the fix, it runs, Audit re-checks, Done, no limit hit."""
    if not j2.j2_check.find_chrome():
        print("lone rubric failure test skipped: Chrome not found")
        return
    os.environ["J2_FIXES"], mode = "1", os.environ.get("J2_FIXES", "0")    # stories funded: the beans item is paid
    run = j2.J2Run()
    os.environ["J2_FIXES"] = mode
    run.budget = 150
    orig, done = run.call, set()

    def call(fn, fmt, task, mock, **k):
        raw = orig(fn, fmt, task, mock, **k)
        if fn == "adaptation" and isinstance(raw, dict) and raw.get("workflows") and not run.workflows:
            raw["workflows"][0]["covers"] = raw["workflows"][0].get("covers", []) + [7]   # the scaffold pays for item 7
        if fn == "W-1" and fn not in done:          # the scaffold already has the viewport tag: phones pass
            done.add(fn)
            raw = raw.replace("```head\n", '```head\n<meta name="viewport" content="width=device-width, initial-scale=1">\n', 1)
        if fn == "W-2" and fn not in done:          # and one tap target is too small: R-6 is the only failure
            done.add(fn)
            raw = raw.replace("```section\n", '```section\n<a href="https://example.com" style="display:inline-block;'
                                              'font-size:10px">Call us</a>\n', 1)
        return raw
    run.call = call
    say(run, BREW_LAB)
    first = run.audits[0]
    fails = j2.workable(first)
    assert len(fails) == 1 and fails[0].startswith("design rubric R-6"), fails   # the bug's exact situation
    assert not any(e["type"] == "limit" for e in run.events), [e["detail"] for e in run.events if e["type"] == "limit"]
    assert not any(m.get("pause") == "limit" for m in run.chat), "asked the Requester a limit question"
    assert any(w["name"] == "Fix item R-6" and w["status"] == "done" for w in run.workflows), run.workflows
    assert run.outcome.startswith("Done") and summary(run)["limits_hit"] == [], run.outcome


def pricing():
    """I: the validator ties price to the work, not to labels."""
    run = j2.J2Run()
    run.goal = j2.mock_charter(BREW_LAB)    # 1 menu, 2 hours, 3 address, 4 order (form), 5 beans, 6 loyalty, 7 phone
    run.budget, run.cycle = 500, 1
    base = {"goal_gap": "x", "outputs": ["index.html"], "completion_check": "y", "atoms": ATOM}
    kinds = [j2.item_kind(c) for c in run.goal["done_when"]]
    assert kinds == ["page_section"] * 3 + ["form"] + ["page_section"] * 2 + ["styling"], kinds
    # bundling: six items in one 20-unit workflow (as in the run) is rejected; the same work priced honestly passes
    reg, refused, _ = run._register([{**base, "name": "Shop", "parts": ["page_section", "interactive_feature"],
                                      "covers": [1, 2, 3, 4, 5, 6]}])
    assert not reg and "costs 20, below the rate-card minimum of 65" in refused[0], refused
    assert "item 4 form 15" in refused[0], refused[0]
    reg, refused, _ = run._register([{**base, "name": "Shop", "covers": [1, 2, 3, 4, 5, 6],
                                      "parts": ["page_section"] * 5 + ["form"]}])
    assert reg and reg[0]["cost"] == 65 and reg[0]["covers"] == [1, 2, 3, 4, 5, 6], refused
    # page_section/form parts must say which items they build
    reg, refused, _ = run._register([{**base, "name": "Page frame and store info", "parts": ["page_section", "styling"]}])
    assert not reg and "covers no done-when item" in refused[0], refused
    # revising a section whose workflow hasn't run yet is a new section, not a fix (runs/j2-20261009-133203 msg 27
    # rejected "Browse by category" for revising W-2 before W-2 had built anything)
    assert run._wf("W-1")["status"] == "registered"
    reg, refused, _ = run._register([{**base, "name": "Browse by category", "parts": ["page_section"], "covers": [5],
                                      "revises": "W-1"}])
    assert reg and reg[0]["cost"] == 10 and not refused, refused
    # after the first Audit: a fix relabelled as a cheaper part is rejected, with or without listing the finding
    run._wf("W-1")["status"] = "done"                        # W-1 ran: rewriting its section is a fix now
    run.audits = [{"cycle": 1, "version": 1, "results": [], "rubric": [], "mechanical": {}, "all_pass": False}]
    for w in ({"fixes": ["R-6"], "revises": "W-1"}, {"revises": "W-1"}, {"fixes": ["R-6", "F-2"]}):
        reg, refused, _ = run._register([{**base, "name": "Header tap area", "parts": ["styling"], **w}])
        assert not reg and "a fix is priced as a fix" in refused[0], (w, refused)
    reg, refused, _ = run._register([{**base, "name": "Header tap area", "parts": ["fix", "fix"], "fixes": ["R-6", "F-2"]}])
    assert reg and reg[0]["cost"] == 16, refused
    # a fix to an item already paid for isn't charged the item again; styling with no item or finding is rejected now
    reg, refused, _ = run._register([{**base, "name": "Hours fix", "parts": ["fix"], "fixes": ["F-2"], "covers": [2]}])
    assert reg and reg[0]["cost"] == 8, refused
    reg, refused, _ = run._register([{**base, "name": "Polish", "parts": ["styling"]}])
    assert not reg and "covers no done-when item" in refused[0], refused
    # Priority is told the cost per done-when item and to question plans far below the rate card
    run = j2.J2Run()
    say(run, BREW_LAB)
    finish(run)
    p = next(c for c in calls_of(run) if c["fn"] == "priority" and "ON THE TABLE" in c["prompt"])
    assert "COST PER DONE-WHEN ITEM" in p["prompt"] and "rate_card_minimum_for_items" in p["prompt"], p["prompt"][-800:]
    assert "far below the rate-card minimums" in p["prompt"]
    assert all(w.get("covers") or w.get("fixes") or w["name"] in ("Stories section", "Animations") for w in run.workflows)


def unpaid_items():
    """Cost follows the work, on the page: a done-when item that passes although no workflow paid for it is a normal
    finding (UNPAID). Baseline Brew Lab: the stories workflow (covering the beans item) is refused, yet the mock
    builds that item anyway. Audit flags it, Adaptation registers a workflow that covers it, and the run ends Done."""
    os.environ["J2_FIXES"], mode = "0", os.environ.get("J2_FIXES", "0")
    try:
        run = j2.J2Run()
        say(run, BREW_LAB)
        finish(run)
        beans = next(i for i, c in enumerate(run.goal["done_when"], 1) if "bean" in c.lower())
        first = next(r for r in run.audits[0]["results"] if r["item"] == beans)
        assert first["verdict"] == "UNPAID" and not first["pass"] and "no workflow covers" in first["note"], first
        assert any(x.startswith(f"done-when item {beans}") and "UNPAID" in x for x in j2.workable(run.audits[0]))
        pay = next(w for w in run.workflows if w.get("covers") == [beans] and w["status"] == "done")
        assert pay["cost"] >= j2.item_min(run.goal["done_when"][beans - 1]), pay
        assert beans in run.paid_items() and run.outcome.startswith("Done"), run.outcome
        assert not any(r["verdict"] == "UNPAID" for r in run.audits[-1]["results"])
        # unit: an item a fix paid for (via its finding) isn't flagged; an undeclared one is
        run = j2.J2Run()
        run.goal = {"done_when": ["A", "B"]}
        run.audits = [{"results": [{"id": "F-2", "item": 2}]}]
        run.workflows = [{"status": "done", "covers": [1]}, {"status": "done", "fixes": ["F-2"]}]
        rows = [{"item": 1, "pass": True, "criterion": "A"}, {"item": 2, "pass": True, "criterion": "B"}]
        run._flag_unpaid(rows)
        assert all(r["pass"] for r in rows), rows
        run.workflows = run.workflows[:1]
        run._flag_unpaid(rows)
        assert rows[0]["pass"] and rows[1]["verdict"] == "UNPAID", rows
    finally:
        os.environ["J2_FIXES"] = mode


def playbook_matching():
    """Playbooks: the same business type only; mock playbooks never reach a live run; tests write to a temp folder."""
    assert j2.PLAYBOOK_FILE.startswith(SESSION_MEMORY) and j2.MEMORY_FILE.startswith(SESSION_MEMORY), j2.PLAYBOOK_FILE
    cafe = {"id": "P-cafe", "business_type": "cafe", "brief": "A website for a cafe shop in Pune with a menu"}
    boutique = {"id": "P-shop", "business_type": "Clothing  Boutique", "brief": "A clothing boutique in Pune"}
    pbs = [cafe, boutique]
    # a clothing brief that shares words with the cafe brief still doesn't get the cafe playbook
    assert [x["id"] for x in j2.relevant_playbooks(pbs, "clothing boutique", "A website for a shop in Pune")] == ["P-shop"]
    assert j2.relevant_playbooks(pbs, "florist", cafe["brief"]) == []
    assert j2.relevant_playbooks(pbs, "", cafe["brief"]) == [] and j2.relevant_playbooks(pbs, "business", "x") == []
    # a playbook written by a mock run is never offered to a live run
    mock_pb = {**cafe, "id": "P-mock", "mock": True}
    live = j2.llm.MOCK
    try:
        j2.llm.MOCK = False
        assert j2.relevant_playbooks([mock_pb, cafe], "cafe", "cafe") == [cafe]
        assert j2.relevant_lessons([{"id": "L-m", "mock": True, "problem": "cafe menu", "fix": "x"}], "cafe menu") == []
    finally:
        j2.llm.MOCK = live
    # what mock runs save is marked mock
    os.environ["J2_MEMORY"] = "1"
    try:
        j2.save_playbook({"id": "P-t", "business_type": "cafe"})
        assert j2.load_playbooks()[-1]["mock"] is True
    finally:
        os.environ["J2_MEMORY"] = "0"
        j2.clear_playbooks()


def intake_needs():
    """H: at J2.a Identity proposes what this kind of business's visitors need and asks the Requester to confirm."""
    run = j2.J2Run()
    say(run, FLORIST)
    q = " ".join(x["question"] for x in run.paused["questions"])
    assert "florist" in q and "browse bouquets" in q and "Is that right" in q, q
    say(run, "Yes, and add wedding flowers. Petal & Stem, Jaipur. Elegant, must work on phones.")
    finish(run)
    assert run.goal["business_type"] == "florist" and run.goal["visitor_needs"], run.goal


def playbooks():
    """H: a Done run saves a playbook for its business type with the measured outcome; the next run for the same
    type reads it at J2.b and says which it used and what it changed; another type doesn't get it; a forced-failure
    run's playbook is a test playbook and isn't reused; J2_MEMORY=0 reads and writes nothing."""
    tmp = tempfile.mkdtemp()
    old = j2.MEMORY_FILE, j2.PLAYBOOK_FILE
    j2.MEMORY_FILE, j2.PLAYBOOK_FILE = os.path.join(tmp, "lessons.jsonl"), os.path.join(tmp, "playbooks.jsonl")
    os.environ["J2_MEMORY"] = "1"
    try:
        run = j2.J2Run()
        say(run, BREW_LAB)
        add_budget_if_asked(run)
        pb = j2.load_playbooks()[-1]
        assert pb["id"] == f"P-{run.run_id}" and pb["business_type"] == "cafe" and pb["build_order"], pb
        o = pb["outcome"]
        assert o["first_pass_audit"] is False and o["cycles"] >= 2 and o["ai_calls"] > 0 and pb["what_failed"], o
        assert any(m.get("act") == "PLAYBOOK" for m in run.chat) and summary(run)["playbooks"]["saved"] == pb["id"]
        first_id = pb["id"]
        run = j2.J2Run()                                   # a florist: the cafe playbook isn't offered
        say(run, FLORIST)
        say(run, "Yes. Petal & Stem, Jaipur. Elegant, must work on phones.")
        finish(run)
        assert run.outcome.startswith("Done"), run.outcome
        assert not any(m.get("playbooks_offered") for m in run.chat), "cafe playbook offered to a florist"
        assert j2.load_playbooks()[-1]["business_type"] == "florist"
        run = j2.J2Run()                                   # another cafe: reads it, says which, and what changed
        say(run, BREW_LAB)
        add_budget_if_asked(run)
        m = next(m for m in run.chat if m.get("playbook_used"))
        assert m["who"] == "adaptation" and m["playbook_used"] == first_id and first_id in m["text"] and m["playbook_changes"]
        assert run.playbooks_used[0]["playbook"] == first_id and summary(run)["playbooks"]["used"][0]["playbook"] == first_id
        assert j2.load_playbooks()[-1]["used_playbook"] == first_id
        n = len(j2.load_playbooks())
        os.environ["J2_FORCE_AUDIT_FAIL"] = "2"            # a test run: its playbook is flagged and not reused
        run = j2.J2Run()
        run.budget = 150
        say(run, BREW_LAB)
        add_budget_if_asked(run)
        os.environ.pop("J2_FORCE_AUDIT_FAIL")
        assert j2.load_playbooks()[-1]["test"] and len(j2.load_playbooks()) == n + 1
        assert not any(x.get("test") for x in j2.relevant_playbooks(j2.load_playbooks(), "cafe", BREW_LAB, n=10))
        os.environ["J2_MEMORY"] = "0"                      # memory off: nothing read, nothing written
        run = j2.J2Run()
        say(run, BREW_LAB)
        assert not any(m.get("playbooks_offered") or m.get("act") == "PLAYBOOK" for m in run.chat)
        os.environ["J2_MEMORY"] = "1"
        assert len(j2.load_playbooks()) == n + 1
        assert j2.clear_playbooks() == n + 1 and j2.load_playbooks() == []
    finally:
        j2.MEMORY_FILE, j2.PLAYBOOK_FILE = old
        os.environ["J2_MEMORY"] = "0"
        os.environ.pop("J2_FORCE_AUDIT_FAIL", None)


def generalist_units():
    """H: the design measurements and the screenshot on a planted page; no cafe examples in any live prompt of a
    florist run; the start screen lists a florist and a photographer."""
    if j2.j2_check.find_chrome():
        bad = ('<!doctype html><html><head><meta name="viewport" content="width=device-width"></head><body>'
               '<h1>A</h1><h1>B</h1><p style="color:#bbb">pale text</p><nav><a href="https://example.com" '
               'style="display:inline-block;font-size:10px">tiny</a></nav><img src="x.png"></body></html>')
        dp = j2.j2_check.design_problems(j2.j2_check.check(bad))
        assert set(dp) == {"R-2", "R-3", "R-6", "R-7"}, dp
        shot = os.path.join(tempfile.mkdtemp(), "s.png")
        assert j2.j2_check.screenshot(bad, shot) and os.path.getsize(shot) > 1000
    run = j2.J2Run()
    say(run, FLORIST)
    say(run, "Yes. Petal & Stem, Jaipur.")
    finish(run)
    # Our instructions carry no cafe examples: every system prompt (role files + reply formats, incl. Audit's) and the
    # plain-language rule. Chat history may still quote mock replies, which can stay.
    for bad in ("coffee's story", "cafe's phone"):
        assert bad not in j2.J2Run.PLAIN_TO_REQUESTER, bad
        for c in calls_of(run):
            assert bad not in c["system"], (c["fn"], bad)
    with open(os.path.join(j2.HERE, "j2_ui.html"), encoding="utf-8") as f:
        ui = f.read()
    assert "a florist in Jaipur" in ui and "wedding and portrait photographer" in ui


def page():
    """E: the behind-the-scenes view. Lanes with live status, a detail view per agent message (inputs, decision,
    reason, cost), the timeline's J2 steps, workflow-agent progress, saved runs opened afterwards, no secrets."""
    import threading
    import urllib.error
    import urllib.request
    import j2_server
    tmp = tempfile.mkdtemp()
    old, j2.MEMORY_FILE = j2.MEMORY_FILE, os.path.join(tmp, "lessons.jsonl")
    with open(j2.MEMORY_FILE, "w") as f:
        f.write('{"id": "L-x-1", "problem": "p", "cause": "c", "fix": "f"}\n')
    os.environ["J2_MEMORY"] = "1"
    os.environ["J2_TEST_API_KEY"] = "sk-test-not-a-real-key-123"
    srv = j2_server.http.server.ThreadingHTTPServer(("127.0.0.1", 0), j2_server.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    get = lambda path: urllib.request.urlopen(base + path).read().decode()
    try:
        j2_server.RUN.reset()
        say(j2_server.RUN, BREW_LAB + " Test key: sk-test-not-a-real-key-123")
        html = get("/")
        for x in ('data-tab="timeline"', 'data-tab="lessons"', 'id="lanes"', 'id="detail"', "renderLanes", "openDetail",
                  "renderTimeline", 'id="runsel"', "clear-lessons", "--wf0"):
            assert x in html, x
        raw = get("/api/state")
        st = json.loads(raw)
        assert "sk-test-not-a-real-key-123" not in raw and "[redacted]" in raw, "secret reached the page"
        assert st["agents"]["W-1"] == "W-1 Builder" and st["sections"] and st["write_lock"] is None
        assert st["workable"] == [] and st["memory"] and st["lessons"][0]["id"] == "L-x-1"
        # lanes: every function, the validator and each workflow agent; idle once done; workflow progress
        ids = [x["id"] for x in st["lanes"]]
        assert ids[:6] == list(j2.FUNCTIONS) and set(ids[6:]) == {w["id"] for w in st["workflows"]}, ids
        assert all(x["status"] == "idle" for x in st["lanes"]), [x["status"] for x in st["lanes"]]
        w1 = next(x for x in st["lanes"] if x["id"] == "W-1")["progress"]
        assert w1["section"] == "W-1" and w1["attempts"] == 1 and "usable section" in w1["last_check"], w1
        # detail view data: every AI message links its calls; each call has inputs, a reason, time; tokens or None
        ai = [m for m in st["chat"] if m.get("calls")]
        assert ai and all(m["step"] for m in st["chat"] if m["who"] not in ("user", "system")), \
            "agent messages need their J2 step for the timeline"
        log = {c["id"]: c for c in st["call_log"]}
        for m in ai:
            for cid in m["calls"]:
                c = log[cid]
                assert c["fn"] == m["who"] and c["inputs"] and c["reason"] and c["seconds"] >= 0, c
        assert all(c["tokens"] is None for c in st["call_log"]), "mock mode must not invent token counts"
        assert any(m.get("charged") for m in st["chat"] if m["who"] == "validator"), "budget charged per step"
        full = json.loads(get(f"/api/call?id={ai[0]['calls'][0]}"))
        assert full["system"] and full["prompt"] and full["raw"], full.keys()
        assert '"reason": str' in full["system"] or '"reason": str' in full["prompt"] or "reason" in full["system"]
        # a lane is "waiting" when it handed off and nobody answered yet; "blocked" for a failed workflow
        fake = [{"id": 1, "who": "adaptation", "text": "@Priority", "next": "priority"}]
        assert j2.lanes(fake, [], None, None, "running", None, 3, None)[1]["status"] == "waiting"
        wf = [{"id": "W-1", "name": "x", "status": "failed", "last_check": "no section", "envelope": {}}]
        j2.add_workflow_agent("W-1")
        assert j2.lanes([], wf, None, None, "waiting", None, 8, None)[6]["status"] == "blocked"
        # saved runs: listed, opened read-only with the same view, its site and its calls
        name = os.path.basename(j2_server.RUN.dir)
        runs = json.loads(get("/api/runs"))
        assert runs["live"] == name
        j2_server.RUN.reset()                               # the old run is now a saved run
        assert any(r["id"] == name for r in json.loads(get("/api/runs"))["runs"])
        sv = json.loads(get(f"/api/state?run={name}"))
        assert sv["saved"] == name and sv["status"] == "saved" and sv["total"] == st["total"] and sv["lanes"], sv["status"]
        assert sv["workable"] == [] and sv["call_log"] and "prompt" not in sv["call_log"][0]
        assert "J2:W-1" in get(f"/site/latest?run={name}")
        assert json.loads(get(f"/api/call?id=1&run={name}"))["id"] == 1
        for bad in ("../memory", "j2-../../etc", "nope"):
            try:
                get(f"/api/state?run={bad}")
                raise AssertionError(f"opened {bad}")
            except urllib.error.HTTPError as e:
                assert e.code == 404
        n = len(j2.load_lessons())             # the seeded lesson plus the one this run saved
        assert n == 2, n
        req = urllib.request.Request(base + "/api/lessons/clear", method="POST", data=b"{}")
        assert json.loads(urllib.request.urlopen(req).read())["cleared"] == n and not os.path.exists(j2.MEMORY_FILE)
    finally:
        srv.shutdown()
        j2.MEMORY_FILE = old
        os.environ["J2_MEMORY"] = "0"
        os.environ.pop("J2_TEST_API_KEY", None)


def limit_answers():
    """runs/j2-20261008-110419: the Requester answered a limit question while the cycle was at its turn cap, and the
    cap fired again before the answer was handled, so Identity re-asked forever. Now every answer is handled:
    "25 units" adds that amount, "2" drops the failing items with the reason, "3" ends Done with open items."""
    def at_cap():
        old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"   # fix (a) asks about a ruling first
        run = j2.J2Run()
        os.environ["J2_FIXES"] = old
        run.budget = 12                          # out of budget after the first cycle: a limit question
        say(run, BREW_LAB)
        assert run.paused and run.paused["kind"] == "limit", run.outcome
        run.cycle_turns = j2.MAX_TURNS           # the live run's state when the Requester answered
        return run
    run = at_cap()
    say(run, "i want a different option so go with 25 units")
    assert run.raises and run.raises[0]["asked"] == 25 and run.raises[0]["to"] == 37, run.raises
    assert "25 units" in run.raises[0]["why"] and run.decisions[0]["budget_added"] == 25, run.decisions
    assert not any(e["type"] == "limit" and "turns" in e["detail"] for e in run.events), "turn cap fired on the answer"

    run = at_cap()
    asked = run.paused["questions"]
    say(run, "2")
    g = run.goal
    assert g["dropped_by_requester"] and len(g["dropped_reasons"]) == len(g["dropped_by_requester"]), g
    assert all(c not in g["done_when"] for c in g["dropped_by_requester"]) and "leave it out" in g["dropped_reasons"][0]["reason"]
    assert not (run.paused and run.paused["questions"] == asked), "asked the same question again"

    run = at_cap()                           # the funded work was built first, so "finish as it is" is an option
    built_first(run)
    assert run.paused["handoff"]["choices"] == ["continue", "drop", "ship"], run.paused["handoff"]
    say(run, "Option 3")
    assert run.outcome.startswith("Done with open items") and not run.paused, run.outcome
    assert summary(run)["status"] == "done_with_open_items"


def nine_workflows():
    """runs/j2-20261008-190919: Audit passed every item at msg 40, then the 30-turn cap fired before J2.h, so Identity
    asked "keep going or finish?" about a finished site and the outcome listed no open items. The cap now scales
    with the workflows registered this cycle, J2.h always runs after a passing Audit, and finishing a workable
    site is "Done", never "Done with open items" with an empty list."""
    def nine(cap=None):
        old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
        run = j2.J2Run()
        os.environ["J2_FIXES"] = old
        run.budget, orig = 400, run.call
        if cap:
            run._turn_cap = lambda: cap

        def call(fn, fmt, task, mock, **k):          # cycle 1: nine workflows, one item each, all of them pass
            if fn == "adaptation" and "WHY YOU ARE UP" in task and not run.workflows:
                crit = run.goal["done_when"]

                def wf(name, i, parts=("page_section",)):
                    return {"name": name, "goal_gap": crit[i - 1], "parts": list(parts), "covers": [i],
                            "outputs": ["index.html"], "completion_check": crit[i - 1]}
                phone = next(i for i, c in enumerate(crit, 1) if "phone" in c.lower())
                form = next(i for i, c in enumerate(crit, 1) if "form" in c.lower())
                rest = [i for i in range(2, len(crit) + 1) if i not in (phone, form)]
                wfs = [wf("Scaffold and styling", 1, ("page_section", "styling")), wf("Viewport fix", phone, ("fix",)),
                       wf("Pre-order form", form, ("form",))] + [wf(f"Section {i}", i) for i in rest]
                return {"say": "@Priority Nine workflows.", "act": "PROPOSE", "next": "Priority",
                        "workflows": j2.with_atoms(wfs + [wf(f"Extra {i}", i) for i in rest][:9 - len(wfs)])}
            return orig(fn, fmt, task, mock, **k)
        run.call = call
        say(run, BREW_LAB)
        return run
    run = nine()
    assert len(run.workflows) == 9 and all(w["cycle"] == 1 and w["status"] == "done" for w in run.workflows), run.workflows
    assert run.cycle_turns > j2.MAX_TURNS and run._turn_cap() == 10 + 4 * 9, (run.cycle_turns, run._turn_cap())
    assert run.outcome == j2.WORKABLE_OUTCOME and not run.paused, run.outcome
    assert not any(e["type"] == "limit" for e in run.events) and summary(run)["status"] == "done"
    # (1) the cap is reached exactly when Audit hands a passing site to Identity: J2.h still runs
    turns = run.cycle_turns
    run = nine(cap=turns - 1)
    assert run.outcome == j2.WORKABLE_OUTCOME and not any(e["type"] == "limit" for e in run.events), run.outcome
    # (3) "finish as it is" on a workable site is Done, not Done with open items and an empty list
    assert run._ship_outcome("on the Requester's decision") == j2.WORKABLE_OUTCOME


def budget_cap():
    """The cap shows in the option text; an option that adds budget the cap won't allow is never offered, and
    "keep working" isn't offered when it can't fund anything or when it already changed nothing. When that leaves
    one option, code applies it instead of asking."""
    run = j2.J2Run()
    q = {"question": "More?", "options": ["Add more building", "Ship"], "budget": [30, 0]}
    run._ask_user("x", [q], "question")             # only the decision question may carry money
    assert "budget" not in run.paused["questions"][0], run.paused
    run.sites = ["<!doctype html><p>v1</p>"]       # a site exists, so "finish as it is" is an option
    run.budget = j2.BUDGET_CAP - 40                 # Identity says 78 is needed; the cap allows 40
    run._identity_limit({"reason": "Adaptation asked", "budget_needed": 78})
    o = run.paused["questions"][0]["options"][0]
    assert o.startswith("Add 40 work credits (the most allowed)") and run.paused["questions"][0]["budget"][0] == 40, o
    def only_finish(h):                         # one option left: applied by code, never a one-option question
        n, run.paused = len(run.chat), None
        run._identity_limit(h)
        assert any(m["text"].startswith("Only one option was possible (Finish as it is") for m in run.chat[n:]), run.chat[n:]
        assert run.outcome.startswith("Done with open items: shipped as is as the only option") and not run.paused, run.outcome
    run.budget = j2.BUDGET_CAP
    only_finish({"reason": "Adaptation asked", "budget_needed": 78})
    cheapest = min(j2.RATES.values())
    run.spent = run.budget - cheapest + 1                       # less than the cheapest part left, no room to add
    only_finish({"reason": "Out of budget", "out_of_budget": True})
    run.spent = 0                                               # money left: keep working is offered once
    run._identity_limit({"reason": "turn cap"})
    assert run.paused["questions"][0]["options"][0].startswith(("Add ", "Keep going")), run.paused
    run.last_limit["decision"] = "continue"                     # ...and changed nothing: not offered again
    only_finish({"reason": "turn cap"})


def repeats():
    """An agent message the same as that agent's last one isn't posted again; Identity takes the turn."""
    run = j2.J2Run()
    run._say("adaptation", "@Identity No budget left, so I propose nothing.", "identity")
    n = len(run.chat)
    m = run._say("adaptation", "No budget left,  so I propose NOTHING.", "identity")
    assert m is run.chat[n - 1] and run.chat[n:] and all(x["who"] == "system" for x in run.chat[n:]), run.chat[n:]
    assert run.relay and run.relay["from"] == "adaptation" and any(e["type"] == "repeat" for e in run.events)
    run.relay = None
    run._say("adaptation", "@Identity A different message.", "identity")
    assert run.chat[-1]["who"] == "adaptation" and not run.relay


def adaptation_idle():
    """runs/j2-20261008-110419 msgs 93-103: with less left than the cheapest part, Adaptation said it could propose
    nothing, Identity answered, and Adaptation was asked again, four times. Once it has said so, it isn't asked again
    until something changes (budget raised, item dropped, a new Requester answer); Identity asks the Requester."""
    run = j2.J2Run()
    run.goal = {"done_when": ["The menu with prices is shown", "Opening hours are listed"]}
    run.budget, run.spent = 40, 38
    asked = []

    def call(fn, fmt, task, mock, **k):
        asked.append(fn)
        return {"say": "@Identity 2 left, the cheapest part costs more, so I propose nothing.",
                "act": "POLICY_QUESTION", "workflows": [], "next": "Identity"}
    run.call = call
    h = {"kind": "propose", "why": "Identity answered."}
    run.agent_turns["adaptation"] = 1
    run._turn_adaptation(h)       # a budget question: rejected, asked once more, then code's fallback fits nothing
    assert asked == ["adaptation"] * 2 and run.turn == "identity" and run.handoff["kind"] == "limit", run.handoff
    assert run.handoff["left_out"] == run.goal["done_when"], run.handoff
    run.agent_turns["adaptation"] = 2
    run._turn_adaptation(h)
    assert asked == ["adaptation"] * 2, "Adaptation was asked again with nothing changed"
    assert run.turn == "identity" and run.handoff["kind"] == "limit" and run.handoff["out_of_budget"], run.handoff
    assert run.chat[-1]["who"] == "system" and "isn't asked again" in run.chat[-1]["text"]
    for change in (lambda: run.decisions.append({"answer": "1"}),               # a new Requester answer
                   lambda: run.goal["done_when"].pop(),                        # an item dropped
                   lambda: setattr(run, "budget", run.budget + 1)):            # budget raised (still short)
        change()
        n = len(asked)
        run._turn_adaptation(h)
        assert len(asked) > n, "a change must let Adaptation re-plan"


def identity_decisions():
    """runs/j2-20261008-123848: when the money ran out, Identity asked its own free-form question (msgs 22, 48), so
    code applied nothing: "2. Add 25 more. Leave out ..." added nothing and the items came back (msg 24 -> 56), and
    "option 2: finish as is" led to a rejected done and the limit question again (msg 50 -> 56). Now money, leaving
    items out and finishing are only ever asked by code's decision question, and a typed answer is applied."""
    def out_of_money(built=False):
        old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
        run = j2.J2Run()
        os.environ["J2_FIXES"] = old
        orig = run.call

        def call(fn, fmt, task, mock, **k):
            if fn == "identity" and "AUDIT'S FINDINGS" in task:   # what Identity did live: money in its own question
                return {"say": "@Requester The money is used up.", "done": False, "needs_requester": True,
                        "requester_questions": ["Option 1: Add more money so everything is built. Option 2: Add a "
                                                "smaller amount and drop some parts. Option 3: Finish as is."]}
            return orig(fn, fmt, task, mock, **k)
        run.call = call
        run.budget = 12
        say(run, BREW_LAB)
        if built:       # below the floor: the funded work is built and audited before the decision question
            built_first(run)
        assert run.paused and run.paused["kind"] == "limit", run.paused and run.paused["kind"]
        assert not any(m.get("pause") == "fact" for m in run.chat), "Identity asked about money in free form"
        return run

    # msg 24: add and leave out in one typed answer, both applied by code
    run = out_of_money()
    n = len(run.chat)
    gone = [c for c in run.goal["done_when"] if re.search(r"opening hours|loyalty|beans", c, re.I)]
    say(run, "2. Add 25 more. Leave out the opening hours, loyalty-card explainer and beans.")
    assert run.raises and run.raises[0]["asked"] == 25 and run.raises[0]["from"] == 12, run.raises
    g = run.goal
    assert len(gone) == 3 and all(c not in g["done_when"] for c in gone), g["done_when"]
    assert [x["criterion"] for x in g["dropped_reasons"]] == gone, g["dropped_reasons"]
    later = " ".join(m["text"] for m in run.chat[n + 1:] if m["who"] == "identity"
                     and not re.search(r"leave out|left out", m["text"]))     # not the drop's own acknowledgement
    assert not any(c in later for c in gone), "dropped items came back"

    # msg 50: "finish as is" ends the run, no rejected done and no limit question straight after
    run = out_of_money(built=True)
    n = len(run.chat)
    say(run, "finish as is")
    assert run.outcome.startswith("Done with open items") and not run.paused, run.outcome
    assert not any(m.get("pause") for m in run.chat[n:]), [m["text"][:80] for m in run.chat[n:] if m.get("pause")]
    assert not any("Identity declared done" in m["text"] for m in run.chat[n:])
    assert summary(run)["status"] == "done_with_open_items"


BANNED_FOR_REQUESTER = re.compile(r"building time|\bcaps?\b|\bcycles?\b|done[-_ ]when|\bestimate", re.I)


def plain_for_requester(run):
    """Everything Identity sends the Requester: no @ in front, no internal words, at most 3 sentences plus one
    question, at most one question with at most 3 options."""
    for m in run.chat:
        if m["who"] != "identity" or not m.get("to_user"):
            continue
        say = m["text"].split("\n")[0]
        assert say.startswith("@Requester ") and not re.search(r"@(?!Requester\b)\w", say), m["text"]
        assert not BANNED_FOR_REQUESTER.search(m["text"].replace("checklist item", "")), m["text"]
        parts = [x for x in re.split(r"(?<=[.!?])\s+", say[len("@Requester "):]) if x.strip()]
        assert len([x for x in parts if not x.endswith("?")]) <= 3 and len([x for x in parts if x.endswith("?")]) <= 1, say
        qs = re.findall(r"^\d+\. ", m["text"], re.M)
        assert len(qs) <= 1 and len(re.findall(r"^\s+Option \d+:", m["text"], re.M)) <= 3, m["text"]


def two_audiences():
    """Item 4, corrected: one message, one addressee, the tag matches the text. (a) Live run 8 Oct 14:06 sent "@Adaptation
    Thanks, I have everything I need. I'll start building..." as one message: it becomes one @Requester and one
    @Adaptation message. (b) A to_requester with agent content ("re-price", "W-3") is rejected and regenerated. Agents
    never get the to_requester text."""
    old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
    run = j2.J2Run()
    os.environ["J2_FIXES"] = old
    orig, seen = run.call, []

    def call(fn, fmt, task, mock, **k):
        if fn == "identity" and task.startswith("REQUESTER'S BRIEF"):          # (a) what Identity said live
            def mixed():
                r = json.loads(mock())
                r.pop("to_requester", None), r.pop("to_agents", None)
                if r.get("enough"):
                    r["say"] = "@Adaptation Thanks, I have everything I need. I'll start building the Brew Lab site now."
                return json.dumps(r)
            return orig(fn, fmt, task, mixed, **k)
        if fn == "identity" and task.startswith("YOU ASKED THE REQUESTER"):   # (b) agent content, then a clean retry
            seen.append(task)
            def first():                       # bad only on the first attempt; the retry gets a clean reply
                r = json.loads(mock())
                if len(seen) == 1:
                    r["to_requester"] = "Got it. I'll re-price W-3 for Priority and drop those items."
                return json.dumps(r)
            return orig(fn, fmt, task, first, **k)
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    run.budget = 12
    say(run, BREW_LAB)
    ch = next(i for i, m in enumerate(run.chat) if m.get("artifact") == "charter")
    pair = run.chat[ch - 1:ch + 1]
    assert pair[0]["text"] == "@Requester Thanks, I have everything I need. I'm starting the build now." and \
        pair[0]["to_user"] and pair[0]["audience"] == "user", pair
    assert pair[1]["text"].startswith("@Adaptation Charter is ready") and not pair[1].get("to_user") \
        and pair[1]["audience"] == "adaptation", pair
    assert any(e["type"] == "audience_template" for e in run.events)
    n = len(run.chat)
    say(run, "2")
    assert len(seen) == 2 and "MIXED THE TWO AUDIENCES" in seen[1] and "re-pric" in seen[1], seen[-1][-300:]
    mine = [m for m in run.chat[n:] if m.get("requester_only")]
    # the answer left items out, so code writes the reply naming them (Identity's own words could name others)
    assert len(mine) == 1 and mine[0]["text"].startswith("@Requester Got it. We'll leave out item "), mine
    assert not any("re-price" in m["text"] for m in run.chat if m.get("to_user"))
    assert "@Requester Thanks, got it." not in run.chat_view(), "agents must not get to_requester"
    plain_for_requester(run)


def simple_messages():
    """Item 5: what the Requester reads is short and plain; one question, at most 3 options; the decision question's
    options say what they get."""
    t = j2.to_requester("@Requester The building time is used up. We hit the cap after 3 cycles. The done-when "
                        "list has 4 items (estimate). One more sentence. And another. Which do you want? Really?")
    assert t == ("The work is used up. We hit the limit after 3 rounds. The checklist list has 4 items. Which do you "
                 "want?"), t
    assert j2.to_requester("Done. What now?", question=False) == "Done."
    run = j2.J2Run()
    run._ask_user("Two things. What is your phone number?", [{"question": "What is your phone number?"},
                                                              {"question": "What are your hours?"}], "info")
    q = run.paused["questions"]
    assert len(q) == 1 and q[0]["question"] == "Please send these: What is your phone number; What are your hours.", q
    assert "?" not in run.chat[-1]["text"].split("\n")[0], run.chat[-1]["text"]
    run._ask_user("Pick one.", [{"question": "Which?", "options": ["a", "b", "c", "d"]}], "question")
    assert run.paused["questions"][0]["options"] == ["a", "b", "c"], run.paused
    run.budget, run.spent = 40, 38
    run._identity_limit({"reason": "Out of budget", "out_of_budget": True})
    opts = run.paused["questions"][0]["options"]                # no site yet: "stop here", never "finish"
    assert opts[0].startswith("Add ") and "you get" in opts[0] and opts[-1].startswith("Stop here: nothing is built"), opts
    run.sites = ["<!doctype html><p>v1</p>"]
    run._identity_limit({"reason": "Out of budget", "out_of_budget": True})
    opts = run.paused["questions"][0]["options"]
    assert opts[0].startswith("Add ") and "you get" in opts[0] and opts[-1].startswith("Finish as it is: you get"), opts
    plain_for_requester(run)


def owner_override():
    """Item 6: a message starting with J2_OVERRIDE_KEY and a command is applied by code; the key is never posted,
    stored or sent to an agent, and the server redacts it."""
    import j2_server
    key = "test-override-key-123"
    old_key, os.environ["J2_OVERRIDE_KEY"] = os.environ.get("J2_OVERRIDE_KEY"), key
    old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
    try:
        run = j2.J2Run()
        os.environ["J2_FIXES"] = old
        run.budget = 12
        say(run, BREW_LAB)
        assert run.paused and run.paused["kind"] == "limit"
        say(run, f"{key} budget +500")
        assert run.budget == 512 and run.raises[-1]["override"] and run.budget > j2.BUDGET_CAP, run.raises
        assert run.chat[-1]["text"].startswith("Owner override applied: budget +500") and run.paused, run.chat[-1]
        crit = run.goal["done_when"][1]
        say(run, f"{key} drop 2")
        assert crit not in run.goal["done_when"] and run.goal["dropped_reasons"][-1]["reason"] == "Owner override"
        say(run, f"{key} paint it blue")
        assert run.chat[-1]["text"].startswith("Owner override not applied"), run.chat[-1]
        say(run, f"{key} ship")                    # the funded work was built before the question
        assert run.outcome.startswith("Done with open items") and not run.paused and run.done, run.outcome
        assert summary(run)["status"] == "done_with_open_items"
        for name in ("chat.jsonl", "calls.jsonl", "goal.json", "summary.json"):
            path = os.path.join(run.dir, name)
            assert not os.path.exists(path) or key not in open(path, encoding="utf-8").read(), name
        assert key not in run.chat_view() and key not in json.dumps(run.chat)
        assert key not in j2_server.redact(f"typed: {key} ship"), "the server must redact the key"
    finally:
        os.environ["J2_FIXES"] = old
        if old_key is None:
            os.environ.pop("J2_OVERRIDE_KEY", None)
        else:
            os.environ["J2_OVERRIDE_KEY"] = old_key


def form_submit():
    """Item 7 (run 20261008-123848 msg 46: a form with no submit button): a section whose form has no submit button
    is rejected so the agent retries; the browser check still makes such a site not workable."""
    for body, ok in (('<form><input name="n"><button type="button">Order</button></form>', False),
                     ('<form><input name="n"></form>', False),
                     ('<form><input name="n"><button>Order on WhatsApp</button></form>', True),
                     ('<form><input type="submit" value="Send"></form>', True)):
        try:
            j2.parse_section("```section\n" + body + "\n```")
            got = True
        except ValueError as e:
            got = False
            assert "submit button" in str(e), e
        assert got == ok, body
    bad = {"results": [{"item": 1, "id": "F-1", "verdict": "PASS", "criterion": "a", "pass": True}],
           "mechanical": {"available": True, "phone": {"overflow_px": 0}, "desktop": {"overflow_px": 0},
                          "js_errors": [], "broken_in_page_links": [],
                          "form_results": [{"index": 1, "ok": False, "has_submit": False, "errors_during": []}]}}
    assert "form 1 has no submit button" in j2.workable(bad)


def audiences_everywhere():
    """Follow-up to 5ba8160. J2.h's reply has the same two parts and check: "@Adaptation Thanks, your site is almost
    ready..." is regenerated into one @Requester and one @Adaptation message. REPLY_FMT allows the @Requester tag.
    post() never re-tags an @agent message as @Requester; it records an event."""
    assert "never starts with @" not in j2.REPLY_FMT and "tagged @Requester or no tag" in j2.REPLY_FMT, j2.REPLY_FMT
    run = j2.J2Run()
    orig, seen = run.call, []

    def call(fn, fmt, task, mock, **k):
        if fn == "identity" and task.startswith("AUDIT'S FINDINGS") and len(seen) < 2:
            seen.append(task)
            def h():
                if len(seen) == 1:      # what Identity sends live: user talk addressed to an agent
                    return json.dumps({"say": "@Adaptation Thanks, your site is almost ready. Fix the phone layout next.",
                                       "clause": "done_when", "done": False, "next": "Adaptation"})
                return json.dumps({"to_requester": "Your site is almost ready. We're fixing the phone layout now.",
                                   "to_agents": "@Adaptation Fix the phone layout next.", "clause": "done_when",
                                   "done": False, "next": "Adaptation"})
            return orig(fn, fmt, task, h, **k)
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    say(run, BREW_LAB)
    assert len(seen) == 2 and "MIXED THE TWO AUDIENCES" in seen[1], "J2.h's mixed reply must be regenerated"
    i = next(j for j, m in enumerate(run.chat) if "Your site is almost ready" in m["text"])
    req, ag = run.chat[i], run.chat[i + 1]
    assert req["text"] == "@Requester Your site is almost ready. We're fixing the phone layout now." and req["to_user"], req
    assert ag["text"] == "@Adaptation Fix the phone layout next." and not ag.get("to_user") \
        and ag["audience"] == "adaptation", ag
    assert not any("Thanks, your site" in m["text"] for m in run.chat)
    n = len(run.events)
    m = run.post("identity", "@Adaptation Re-price W-3.", to_user=True)
    assert m["text"] == "@Adaptation Re-price W-3." and run.events[n]["type"] == "misaddressed", (m, run.events[n:])


def listed_gaps(text):
    """The "Still not right" entries of a decision message: one per line, "- " in front."""
    return [ln[2:] for ln in text.split("\n") if ln.startswith("- ")]


def limit_wording():
    """Run 20261008-154537: msg 5 printed "1.\n1." (Identity's own numbered list plus code's); msgs 45/46 paused at
    the per-cycle turn cap with a money banner although no money option was offered, and "1 thing still not right"
    didn't match the gaps the message listed. The list is numbered once; the question and the banner say why the team
    paused and offer only what's on offer; the gap list and its count come from one list; every option says what you
    get, with the amount when money is involved."""
    run = j2.J2Run()
    run._ask_user("Thanks, that covers most of it. A few things are still missing.\n1. Which products are new?\n"
                  "2. Which sizes?", [{"question": "Which products are new arrivals?"},
                                      {"question": "Which sizes does each product come in?"}], "info")
    txt = run.chat[-1]["text"]
    assert not re.findall(r"(?m)(?:^|\s)\d+\.(?:\s|$)", txt) and txt.endswith("Which sizes does each product come in."), txt

    old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
    run = j2.J2Run()
    os.environ["J2_FIXES"] = old
    say(run, BREW_LAB)
    run.audits[-1]["results"][0].update(verdict="NEEDS_REVISION", **{"pass": False})
    run.audits[-1]["results"][2].update(verdict="NEEDS_REVISION", **{"pass": False})
    run._identity_limit({"reason": f"Cycle {run.cycle} used {j2.MAX_TURNS} turns (the per-cycle cap) without finishing."})
    q = run.paused["questions"][0]
    assert q["question"] == "The team paused after a round of work. Keep going, leave out the missing parts, or " \
                            "finish as it is?", q["question"]
    assert "budget" not in q and "add budget" not in run.outcome and q["question"] in run.outcome, run.outcome
    gaps = j2.workable(run.audits[-1])
    listed = listed_gaps(run.chat[-1]["text"])
    assert len(listed) == len(gaps) and f"with {len(gaps)} things still not right: item " in q["options"][-1], (listed, q)
    for o in q["options"]:
        assert "you get" in o, o
    run.spent = run.budget                                    # money: the option says the amount
    run._identity_limit({"reason": "Out of budget", "out_of_budget": True})
    q = run.paused["questions"][0]
    assert q["question"].startswith("The work you approved is used up. Add more and keep going"), q["question"]
    assert re.match(r"Add \d+ work credits", q["options"][0]) and all("you get" in o for o in q["options"]), q["options"]


def open_list():
    """Follow-up to 6e5aa59 (run 20261008-154537 msg 45: the audit had 1 problem, but reviews, styling and menu links
    weren't built yet). The list combines the last audit's failures with every checklist item an unfinished workflow
    covers, one entry per item; the count is its length; items built after the last audit are marked."""
    def paused_run():
        old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
        run = j2.J2Run()
        os.environ["J2_FIXES"] = old
        say(run, BREW_LAB)                                      # done and workable: a clean last audit
        run.audits[-1]["results"][0].update(verdict="NEEDS_REVISION", **{"pass": False})   # 1 audit failure: item 1
        return run

    def unfinished(run, covers, status="registered"):
        run.workflows.append({"id": f"W-{len(run.workflows) + 1}", "name": "x", "status": status, "covers": covers})

    def ask(run):
        run._identity_limit({"reason": f"Cycle {run.cycle} used {j2.MAX_TURNS} turns (the per-cycle cap) without "
                                       "finishing."})
        text = run.chat[-1]["text"]
        listed = listed_gaps(text)
        return text, listed, run.paused["questions"][0]["options"][-1]

    # (a) 1 audit failure + 3 unfinished workflows (registered, running, unfunded) -> 4 items, "4 things"
    run = paused_run()
    unfinished(run, [2]), unfinished(run, [3], "running"), unfinished(run, [5], "unfunded")
    text, listed, ship = ask(run)
    crit = run.goal["done_when"]
    assert len(listed) == 4 and "with 4 things still not right: " in ship, (listed, ship)
    row = lambda i, st: f"item {i} {j2.short(crit[i - 1])} ({st})"           # run-long number, short text, status
    assert listed[:2] == [row(1, "built but failing"), row(2, "not built")] and listed[3] == row(5, "unfunded"), listed

    # (b) an item both failing in the audit and covered by an unfinished workflow appears once
    run = paused_run()
    unfinished(run, [1, 2])
    text, listed, ship = ask(run)
    assert listed == [row(1, "built but failing"), row(2, "not built")] and "with 2 things still not right: " in ship, \
        listed

    # (c) the site is newer than the last audit: what was built since is marked, and the message says so
    run = paused_run()
    run.sites.append(run.sites[-1])
    run.workflows.append({"id": "W-99", "name": "y", "status": "done", "covers": [1, 4], "version": len(run.sites)})
    text, listed, ship = ask(run)
    assert listed == [row(1, "built, not checked yet"), row(4, "built, not checked yet")], listed
    assert "built after the last check, so they're not checked yet" in text and "with 2 things still not right: " in ship, text


def covers_by_text():
    """Follow-up to 0543422: a workflow stores the text of the done-when items it covers, so dropping an item (which
    renumbers the list) can't point an unfinished workflow at the wrong item, and a dropped item never shows."""
    old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
    run = j2.J2Run()
    os.environ["J2_FIXES"] = old
    say(run, BREW_LAB)
    crit = list(run.goal["done_when"])
    run.budget, run.p_refused = 500, {}
    reg, refused, _ = run._register([
        {"name": f"Item {i}", "goal_gap": crit[i - 1], "outputs": ["x"], "completion_check": "y", "atoms": ATOM,
         "parts": ["form" if "form" in crit[i - 1].lower() else "page_section"], "covers": [i]} for i in (4, 5, 6)])
    assert len(reg) == 3 and not refused, refused
    assert [w["covers_text"] for w in reg] == [[crit[3]], [crit[4]], [crit[5]]], [w.get("covers_text") for w in reg]
    run.audits[-1]["results"][3].update(verdict="NEEDS_REVISION", **{"pass": False})     # item 4 also fails the audit
    run._override("drop 4")                                                          # renumbers: 5 -> 4, 6 -> 5
    assert run.goal["done_when"] == crit[:3] + crit[4:], run.goal["done_when"]
    items = [r for r in run.audits[-1]["results"] if not r["pass"]]
    listed = run._open_list(run.audits[-1], items)
    # (a) the unfinished workflows still name their own items, at their new numbers
    assert listed == [f"{crit[4]} (not built yet)", f"{crit[5]} (not built yet)"], listed
    assert [run._wf_items(w) for w in reg] == [[], [4], [5]], [run._wf_items(w) for w in reg]
    # (b) the dropped item never appears: not from its workflow, not from the audit that still lists it
    assert not any(crit[3] in x for x in listed), listed
    # (c) runs saved before covers_text still load and fall back to the numbers
    for w in run.workflows:
        w.pop("covers_text", None)
    run.save("workflows.json", run.workflows)
    snap = j2.saved_snapshot(os.path.basename(run.dir))
    assert snap and len(snap["workflows"]) == len(run.workflows), "an old run must load"
    # covers holds charter numbers: item 5 sits at position 4 after the drop
    assert run._wf_items(reg[1]) == [4] and run._open_list(run.audits[-1], []), "old workflows use their numbers"


def readable_decision():
    """Follow-up to bab0ca7: the decision question is readable without shortening the gaps. (1) one gap per line,
    full text, after at most 2 sentences, then the question and options; (2) no "1." before the question; (3) work
    credits, not units; (4) an unclear answer gets one short line and the options only; (5) the counts add up, and a
    difference is explained."""
    old, os.environ["J2_FIXES"] = os.environ.get("J2_FIXES"), "0"
    run = j2.J2Run()
    os.environ["J2_FIXES"] = old
    say(run, BREW_LAB)                                          # done and workable: a clean last audit
    run.spent = run.budget                                      # then out of money: add / leave out / finish
    crit = run.goal["done_when"]
    last = run.audits[-1]
    for i in (1,):
        last["results"][i].update(verdict="NEEDS_REVISION", **{"pass": False})
    last["rubric"][0].update(verdict="NEEDS_REVISION", **{"pass": False})
    for i in (3, 4, 5):
        run.workflows.append({**run.workflows[0], "id": f"W-{90 + i}", "status": "registered", "covers": [i + 1],
                              "covers_text": [crit[i]]})
    run._identity_limit({"reason": "Out of budget", "out_of_budget": True})
    text = run.chat[-1]["text"]
    lines = text.split("\n")
    gaps = listed_gaps(text)
    q = run.paused["questions"][0]
    # (1) intro (at most 2 sentences), the header, one full gap per line, then the question, then the options
    intro = lines[0][len("@Requester "):]
    assert len([x for x in re.split(r"(?<=[.!?])\s+", intro) if x]) <= 2, intro
    i = lines.index(next(ln for ln in lines if ln.startswith("Still not right (")))
    assert lines[i + 1:i + 1 + len(gaps)] == [f"- {g}" for g in gaps], lines
    # each line: the item's run-long number (a rubric item: no id), its short text and Audit's status
    assert len(gaps) == 5 and all(re.fullmatch(r"(item \d+ )?.+ \((built but failing|not built|unfunded|failing)\)", g)
                                  and not j2.INTERNAL_ID.search(g)
                                  for g in gaps), gaps
    assert lines[i + 1 + len(gaps)] == q["question"] and lines[i + 2 + len(gaps)].startswith("   Option 1: "), lines
    # (2) no "1." before the question
    assert not any(re.match(r"\d+\. ", ln) for ln in lines), lines
    # (3) work credits, never units
    assert "work credits" in q["options"][0] and not re.search(r"\bunits?\b", text), text
    # (5) counts: the header explains the mix; finish counts the whole list; leave-out explains the difference
    assert lines[i] == f"Still not right ({len(gaps)}: 2 built but failing, 3 not built yet):", lines[i]
    assert f"with {len(gaps)} things still not right: " in q["options"][-1], q["options"]
    drop = next(o for o in q["options"] if o.startswith("Leave out"))
    assert drop.startswith("Leave out item ") and drop.count("item ") == 4 and drop.endswith(
        "Consistent styling stays as it is, still failing."), drop
    # (4) unclear answer: one short line, then the options only
    say(run, "hmm, not sure")
    re_ask = next(m for m in reversed(run.chat) if m["who"] == "identity")["text"].split("\n")
    assert re_ask[0] == "@Requester I couldn't tell which option you chose. Reply 1, 2 or 3, or type what to add or " \
                        "leave out.", re_ask[0]
    assert len(re_ask) == 4 and all(ln.startswith("   Option ") for ln in re_ask[1:]), re_ask


PRD_BRIEF = ("Write a PRD for QuickQueue, a mobile app that lets clinic patients join a waiting line remotely. Users: "
             "patients at small clinics and the front-desk staff who manage the line. Problem: patients wait 45 minutes on "
             "average in crowded waiting rooms. Must-have features: join the queue from a phone, live position updates, SMS "
             "alert when 2 patients are ahead, staff dashboard to call the next patient. Constraints: works on low-end "
             "Android phones; no patient health data stored. Success: average in-room wait under 10 minutes; 60% of "
             "patients join remotely within 3 months.")
BROWSER_FNS = ("check", "screenshot", "tap_targets", "find_chrome", "design_problems")


def prd_run():
    """J2_OUTPUT=prd: a mock PRD brief reaches Done workable with prd.md and prd.docx; no browser check is ever called;
    only P-conditions and the D-rubric are listed, never a website's; the validator keeps the facts-present rule and
    the document's own check types."""
    called, saved = [], {k: getattr(j2.j2_check, k) for k in BROWSER_FNS}

    def boom(name):
        def f(*a, **k):
            called.append(name)
            raise AssertionError(f"a PRD run called the browser check {name}")
        return f
    for k in BROWSER_FNS:
        setattr(j2.j2_check, k, boom(k))
    os.environ["J2_OUTPUT"] = "prd"
    try:
        run = j2.J2Run()
        assert run.output == "prd" and run.doc and j2.RATES == {"doc_section": 10, "requirements_section": 15, "fix": 8}
        say(run, PRD_BRIEF)
    finally:
        os.environ.pop("J2_OUTPUT")
        for k, v in saved.items():
            setattr(j2.j2_check, k, v)
    assert not called, called
    assert run.outcome.startswith("Done: the PRD is workable"), run.outcome
    s = summary(run)
    with open(os.path.join(run.dir, "chat.jsonl"), encoding="utf-8") as f:
        assert json.loads(f.readline())["output"] == "prd"
    assert s["output_type"] == "prd" and s["status"] == "done" and s["workable"] == [], s
    assert [x["heading"] for x in s["sections"]] == list(j2.PRD_SECTIONS) and all(x["words"] for x in s["sections"]), s
    # P8 is a warning ("under 10 minutes" states no window): shown, and the PRD is still workable
    assert (s["conditions"]["met"], s["conditions"]["total"], s["conditions"]["warnings"]) == (7, 8, 1), s["conditions"]
    assert s["export"]["written"], s
    assert s["verification"]["passed"] == 6 and not s["verification"]["failed"] and s["verification"]["checks_run"], s
    # one workflow per section, one atom each, priced from the document rate card
    assert [w["name"] for w in run.workflows] == [f"Write {x}" for x in j2.PRD_SECTIONS], run.workflows
    assert all(len(w["atoms"]) == 1 for w in run.workflows) and run.spent == 65, run.spent
    md = open(os.path.join(run.dir, "prd.md"), encoding="utf-8").read()
    assert md.startswith("# QuickQueue") and [h for lv, h, _ in j2.md_sections(md) if lv == 2] == list(j2.PRD_SECTIONS)
    assert "1. **R1**:" in md and "<" not in md, md
    conds = json.load(open(os.path.join(run.dir, "conditions.json"), encoding="utf-8"))
    assert [c["id"] for c in conds] == [f"P{i}" for i in range(1, 9)], conds
    assert all(c["met"] for c in conds[:7]) and not conds[7]["met"] and conds[7]["severity"] == "warn", conds
    # never a website condition: no render check, no R-rubric, no tap-targets rule in any prompt
    a = run.audits[-1]
    assert [r["id"] for r in a["rubric"]] == ["D-1", "D-2", "D-3", "D-4", "D-5"] and not a["mechanical"], a["rubric"]
    assert a["output"] == "prd" and a["read"] and a["conditions"] == conds, a
    assert not any(m["text"].startswith("Mechanical check") for m in run.chat)
    calls = [json.loads(x) for x in open(os.path.join(run.dir, "calls.jsonl"), encoding="utf-8")]
    for c in calls:
        text = c["system"] + c["prompt"]
        assert "tap-targets" not in text and "Tap targets are big enough" not in text and "R-6" not in text, c["fn"]
    assert any("OUTPUT TYPE: PRD document" in c["prompt"] for c in calls)
    assert any(c["fn"].startswith("W-") and "Workflow agent for a PRD section" in c["system"] for c in calls)
    # the .docx: headings, numbered requirements and the metrics table come through
    import docx
    d = docx.Document(os.path.join(run.dir, "prd.docx"))
    heads = [p.text for p in d.paragraphs if p.style.name.startswith("Heading")]
    assert heads == list(j2.PRD_SECTIONS), heads
    reqs = [p.text for p in d.paragraphs if p.style.name == "List Number"]
    assert reqs[0].startswith("R1:") and len(reqs) == 4, reqs
    assert d.tables and d.tables[0].cell(1, 0).text == "G1", [t.cell(0, 0).text for t in d.tables]
    # the validator: facts-present keeps its rule (charter or the Requester's answers only); document check types only
    atom = j2.mock_doc_atom({"name": "Write Problem"})
    fact = {"text": "Product name", "type": "facts-present", "target": ["QuickQueue", "45 minutes"], "expect": True}
    assert not run._atom_problems({"atoms": [{**atom, "verification": atom["verification"] + [fact]}]})
    bad = run._atom_problems({"atoms": [{**atom, "verification": [{**fact, "target": ["QuickQueue", "99.9% uptime"]}]}]})
    assert len(bad) == 1 and "['99.9% uptime'], not found in the charter" in bad[0], bad
    for chk, why in (({"type": "tap-targets", "target": ".x", "expect": 44}, "allowed: facts-present, heading-present"),
                     ({"type": "ids-unique", "target": "Requirement", "expect": True}, "only an id prefix"),
                     ({"type": "section-not-empty", "target": "Users", "expect": 0}, "minimum word count")):
        bad = run._atom_problems({"atoms": [{**atom, "verification": [{"text": "x", **chk}]}]})
        assert len(bad) == 1 and why in bad[0], (chk, bad)
    # a website run after it is a website again
    assert j2.J2Run().output == "website" and "page_section" in j2.RATES
    show(run)
    return run


def prd_checks():
    """heading-present, section-not-empty and ids-unique pass and fail correctly (a duplicate R2 is rejected); each
    necessary condition fails on the document that breaks it."""
    doc = "# X\n\n## Users\n\nClinic patients and front-desk staff.\n\n## Requirements\n\n1. **R1**: Join the queue\n2. **R2**: See the position\n"
    chk = lambda t, target, expect=True, d=doc: j2.doc_check({"type": t, "target": target, "expect": expect}, d)
    assert chk("heading-present", "Requirements")["pass"] and chk("heading-present", "users")["pass"]
    assert not chk("heading-present", "Goals")["pass"]
    assert chk("section-not-empty", "Users", 5)["pass"] and not chk("section-not-empty", "Users", 50)["pass"]
    assert not chk("section-not-empty", "Goals", 1)["pass"]
    assert not chk("section-not-empty", "Users", 1, "## Users\n\n## Goals\n\n- G1: x\n")["pass"]     # empty section
    assert chk("ids-unique", "R")["pass"] and chk("ids-unique", "R")["actual"] == [1, 2]
    dup = chk("ids-unique", "R", d=doc + "3. **R2**: Get an SMS\n")
    assert not dup["pass"] and "duplicate id(s): R2" in dup["evidence"], dup
    assert not chk("ids-unique", "R", d="## Requirements\n\nJoin the queue.\n")["pass"]
    assert chk("ids-unique", "R", d=doc + "\nThe SMS alert also serves R2.\n")["pass"]   # a mention, not an id
    # the same checks through run_check, as code runs a work atom's verification
    assert not j2.run_check({"type": "ids-unique", "target": "R"}, "", doc + "- **R2**: again\n", doc=True)["pass"]
    # necessary conditions, each on a document that breaks it
    conds = {c["id"]: c for c in j2.load_conditions("prd.json")}
    goal = {"product_name": "QuickQueue", "facts": ["QuickQueue", "SMS alert"], "to_be_confirmed": []}
    src = j2.squash("QuickQueue SMS alert 45 minutes 10 minutes 60% 3 months")
    good = ("# QuickQueue\n\n## Problem\n\nPatients wait 45 minutes.\n\n## Users\n\nClinic patients.\n\n## Goals\n\n- **G1**: "
            "Short waits\n\n## Requirements\n\n1. **R1**: SMS alert\n2. **R2**: Join from a phone\n\n## Success metrics\n\n"
            "| Goal | Metric |\n|---|---|\n| G1 | Under 10 minutes, measured monthly |\n\n## Out of scope\n\n- Payments\n")
    met = lambda cid, d, g=goal: j2.condition_met(conds[cid], d, g, src, j2.PRD_SECTIONS)
    assert all(met(c, good)[0] for c in conds), [(c, met(c, good)) for c in conds]
    assert not met("P1", good.replace("## Out of scope\n\n- Payments\n", "## Out of scope\n"))[0]
    assert not met("P1", good.replace("## Users", "## People"))[0]
    assert not met("P2", good.replace("phone\n", "phone\n3. **R2**: Duplicate\n"))[0] and not met("P2", good.replace("**R2**", "**R3**"))[0]
    assert not met("P3", good.replace("SMS alert", "text message"))[0]
    p4 = met("P4", good.replace("Under 10 minutes", "Under 7 minutes"))
    assert not p4[0] and "7" in p4[1], p4
    assert not met("P5", good.replace("Payments", "Payments (to be confirmed)"))[0]
    assert not met("P5", good, {**goal, "to_be_confirmed": [{"criterion": "x", "fact": "y"}]})[0]
    assert not met("P6", good.replace("| G1 | Under", "| Wait | Under"))[0]
    assert not met("P6", good.replace("- **G1**: Short waits", "- Short waits"))[0]
    # workable() for a document: conditions and the D-rubric count, the render check doesn't
    audit = {"output": "prd", "results": [], "rubric": [], "mechanical": {},
             "conditions": [{"id": "P2", "text": "ids", "met": False, "evidence": "R2 twice"}]}
    assert j2.workable(audit) == ["necessary condition P2 not met: ids (R2 twice)"], j2.workable(audit)
    assert j2.workable({**audit, "conditions": []}) == []


def prd_groups_metrics_assumptions():
    """P7 user groups, P8 metric windows (a warning), P4 with Assumption: lines and proper names, the closing
    assumptions section, the window in Identity's number question, and short item names cut at a natural break."""
    conds = {c["id"]: c for c in j2.load_conditions("prd.json")}
    goal = {"product_name": "LabSlot", "users": "Students (book slots) and lab staff", "facts": ["LabSlot"],
            "to_be_confirmed": []}
    src = j2.squash("LabSlot students lab staff book a slot 80% of bookings are made without staff help")
    doc = ("# LabSlot\n\n## Users\n\nStudents and lab staff.\n\n## Requirements\n\n1. **R1**: A student can book a slot\n\n"
           "## Success metrics\n\n- **G1**: 80% of bookings are made without staff help\n")
    met = lambda cid, d, g=goal: j2.condition_met(conds[cid], d, g, src, j2.PRD_SECTIONS)
    assert j2.user_groups(goal) == ["Students", "lab staff"], j2.user_groups(goal)
    p7 = met("P7", doc)
    assert not p7[0] and "lab staff" in p7[1] and "Students" not in p7[1], p7       # "a student" covers Students
    assert met("P7", doc.replace("lab staff.\n", "lab staff.\n\nLab staff have no actions in this version.\n"))[0]
    assert met("P7", doc, {**goal, "user_groups": [{"name": "students", "actions": ["book"]}]})[0]
    # P8: a warning, never a blocker
    p8 = met("P8", doc)
    assert not p8[0] and "80% of bookings" in p8[1], p8
    for window in (" per term", ", measured weekly", " (measurement window not set)", " within 3 months"):
        assert met("P8", doc.replace("staff help\n", f"staff help{window}\n"))[0], window
    rows = j2.check_conditions(j2.load_conditions("prd.json"), doc, goal, src, j2.PRD_SECTIONS)
    w = next(c for c in rows if c["id"] == "P8")
    assert w["severity"] == "warn" and not w["met"] and not j2.blocks(w), w
    assert all("severity" not in c for c in rows if c["id"] != "P8")             # the others stay blocking
    audit = {"output": "prd", "results": [], "rubric": [], "mechanical": {}, "conditions": [w]}
    assert j2.workable(audit) == [], j2.workable(audit)
    # P4: a number or proper name not in the charter fails outside an Assumption: line and passes inside one
    for claim in ("Bookings open 7 days ahead.", "Northfield College runs the labs."):
        bad = met("P4", doc + f"\nOut of scope: {claim}\n")
        assert not bad[0] and ("7" in bad[1] or "Northfield" in bad[1]), (claim, bad)
        assert met("P4", doc + f"\n- Assumption: {claim}\n")[0], claim
    secs = {"W-1": {"body": "## Users\n\nStudents and lab staff.\n\n- Assumption: Bookings open 7 days ahead."},
            "W-2": {"body": "## Requirements\n\n1. **R1**: A student can book a slot"}}
    md = j2.assemble_doc("LabSlot", secs, j2.PRD_SECTIONS)
    assert md.endswith("## Assumptions to confirm\n\n- Bookings open 7 days ahead.\n"), md
    assert j2.doc_assumptions(md) == ["Bookings open 7 days ahead."] and met("P4", md)[0]
    assert "Assumptions to confirm" not in j2.assemble_doc("LabSlot", {"W-2": secs["W-2"]}, j2.PRD_SECTIONS)
    p4 = next(c for c in j2.check_conditions(j2.load_conditions("prd.json"), md, goal, src, j2.PRD_SECTIONS)
              if c["id"] == "P4")
    assert p4["met"] and p4["assumptions"] == ["Bookings open 7 days ahead."], p4
    assert "quote each" in dict(j2.DOC_RUBRIC)["D-5"] or "quotes each" in dict(j2.DOC_RUBRIC)["D-5"]

    # a mock PRD run whose Out of scope builder adds an assumption: in conditions.json and the closing section
    os.environ["J2_OUTPUT"] = "prd"
    try:
        run = j2.J2Run()
        orig = run.call

        def call(fn, *a, **k):
            raw = orig(fn, *a, **k)
            if isinstance(raw, str) and "## Out of scope" in raw:
                head, _, tail = raw.rpartition("```")
                raw = head + "- Assumption: Clinics may want a printed ticket within 2 weeks.\n```" + tail
            return raw
        run.call = call
        say(run, PRD_BRIEF)
        q = run._fact_question({"needs_requester_fact": "A target for in-room wait", "item": None})["question"]
        assert "over what time" in q, q                                       # the window in the same question
    finally:
        os.environ.pop("J2_OUTPUT")
    assert run.outcome.startswith("Done: the PRD is workable"), run.outcome
    md = open(os.path.join(run.dir, "prd.md"), encoding="utf-8").read()
    assert md.endswith("## Assumptions to confirm\n\n- Clinics may want a printed ticket within 2 weeks.\n"), md[-300:]
    saved = json.load(open(os.path.join(run.dir, "conditions.json"), encoding="utf-8"))
    p4 = next(c for c in saved if c["id"] == "P4")
    assert p4["met"] and p4["assumptions"] == ["Clinics may want a printed ticket within 2 weeks."], p4
    assert next(c for c in saved if c["id"] == "P7")["met"], saved
    site = j2.J2Run()
    site.goal = {"done_when": ["x"]}
    q = site._fact_question({"needs_requester_fact": "A target for in-room wait", "item": None})["question"]
    assert "over what time" not in q, q                                       # websites: as before

    # short names: cut at a natural break, at most 12 words, "..." when cut mid-clause, never on a joining word
    texts = ["The Requirements section lists every must-have feature as R1, R2, ...",
             "Visitors can see every event of the three-day fest grouped by day with its start time and the room it is in",
             "A section about the beans and the farms they come from",
             "Opening hours are listed"]
    for t in texts:
        n = j2.short(t)
        words = n.rstrip(".").split()
        assert len(words) <= 12 and not (n.endswith("...") and words[-1].lower() in j2.JOINING), n
        first = re.split(r"[,:;(]| - ", t)[0].strip()
        assert n == first or (n.endswith("...") and first.startswith(n[:-3])), (t, n)
    assert j2.short(texts[1]).endswith("...") and j2.short(texts[3]) == texts[3]
    assert j2.short(texts[2]) == texts[2]                                     # 11 words: whole, no "..."
    names = j2.shorts([texts[1], texts[1].replace("room", "hall")])
    assert len(set(names)) == 2, names                                        # still unique within a list


def prd_recovery():
    """runs/j2-20261013-185235: heading targets are normalised ("## Problem" is "Problem"); a wrong target after three
    failures ends in CHECK_WRONG by code without asking Identity, and the corrected check re-runs on the same document;
    an unusable Adaptation reply twice gets a code-built revision and the run goes on; the PRD question lists
    sections only, says "document", never drops everything and never repeats with nothing changed."""
    assert j2.heading_target("## Problem") == j2.heading_target(" #Problem") == "Problem"
    doc = "# X\n\n## Problem\n\nBooking is done on paper and slots get double-booked.\n"
    for t in ("## Problem", "Problem"):
        assert j2.doc_check({"type": "heading-present", "target": t}, doc)["pass"], t
        assert j2.doc_check({"type": "section-not-empty", "target": t, "expect": 5}, doc)["pass"], t
    atom = j2.mock_doc_atom({"name": "Write Problem"})
    assert not j2.check_problems({**atom, "verification": [{"text": "x", "type": "heading-present", "target": "## Problem",
                                                            "expect": True}]}, "", j2.DOC_CHECK_TYPES)
    assert "no # characters" in j2.PRD_ATOM_RULES

    def prd(patch):
        """A mock PRD run whose AI calls pass through patch(fn, reply, n) (n: that function's call count)."""
        os.environ["J2_OUTPUT"] = "prd"
        try:
            run, seen = j2.J2Run(), {}
            orig = run.call

            def call(fn, *a, **k):
                seen[fn] = seen.get(fn, 0) + 1
                return patch(fn, orig(fn, *a, **k), seen[fn])
            run.call = call
            say(run, PRD_BRIEF)
            finish(run)
        finally:
            os.environ.pop("J2_OUTPUT")
        return run, seen

    def target(t):              # Adaptation's first plan writes the Problem heading checks with target t
        def patch(fn, r, n):
            if fn == "adaptation" and n == 1 and isinstance(r, dict):
                for w in r.get("workflows") or []:
                    for c in w["atoms"][0]["verification"] if "Problem" in w["name"] else []:
                        if c["type"] in j2.HEADING_CHECKS:
                            c["target"] = t
            return r
        return patch
    # (1) "## Problem" behaves exactly like "Problem", and the normalised form is stored
    run, seen = prd(target("## Problem"))
    assert run.outcome.startswith("Done: the PRD is workable"), run.outcome
    w1 = run.workflows[0]
    assert [c["target"] for c in w1["atoms"][0]["verification"] if c["type"] in j2.HEADING_CHECKS] == ["Problem"] * 2
    saved = json.load(open(os.path.join(run.dir, "workflows.json"), encoding="utf-8"))[0]
    assert all(c["target"] == "Problem" for c in saved["atoms"][0]["verification"] if c["type"] in j2.HEADING_CHECKS)
    recs = [r for r in run.receipts if r["atom"] == "W-1.a1" and r["type"] in j2.HEADING_CHECKS]
    assert recs and all(r["target"] == "Problem" and r["pass"] for r in recs) and seen["W-1"] == 1, recs

    # (2) a wrong target fails three times: code checks the obvious case, CHECK_WRONG, re-run on the same document
    run, seen = prd(target("Problem section"))
    assert run.outcome.startswith("Done: the PRD is workable"), run.outcome
    assert seen["W-1"] == j2.MAX_CHECK_ATTEMPTS, seen                      # no new build after the correction
    assert any(e["type"] == "check_wrong_default" for e in run.events), run.events
    note = next(m for m in run.chat if m["text"].startswith("Code checked the obvious case first"))
    assert "'Problem section' passes as the heading text 'Problem'" in note["text"], note["text"]
    re_run = [r for r in run.receipts if r["atom"] == "W-1.a1" and r.get("recheck")]
    assert re_run and all(r["pass"] for r in re_run) and {r["target"] for r in re_run if r["type"] in
                                                           j2.HEADING_CHECKS} == {"Problem"}, re_run
    assert run.workflows[0]["atoms"][0]["status"] == "passed"
    assert not any(m["who"] == "identity" and "fails its checks" in m["text"] for m in run.chat)
    call = next(c for c in calls_of(run) if "WORK ATOM FAILED" in c["prompt"])
    assert "the check's target looks wrong" in call["prompt"], call["prompt"][-600:]

    # (3) the build is really wrong (W-1 writes "## Background"), then Adaptation's reply is a bare "say" twice:
    # code builds the revision of W-1 itself and the run gets to Done
    blob = {"say": '{"say":"One proposal: a W-1 revision covering items 1 and 8, priced at 28. The builder writes'}

    def patch(fn, r, n):
        if fn == "W-1":
            return r.replace("## Problem", "## Background")
        if fn == "adaptation" and n in (3, 4):          # 1: the plan, 2: the failed atom, 3-4: the next proposals
            return dict(blob)
        return r
    run, seen = prd(patch)
    assert run.outcome.startswith("Done: the PRD is workable"), run.outcome
    assert run.workflows[0]["atoms"][0]["status"] == "escalated", run.workflows[0]["atoms"]
    retry = [c for c in calls_of(run) if "YOUR LAST REPLY COULD NOT BE USED" in c["prompt"]]
    assert len(retry) == 1 and '"revises": "W-1"' in retry[0]["prompt"], retry
    fix = next(w for w in run.workflows if w.get("revises") == "W-1")
    assert fix["name"] == "Revise W-1 Write Problem" and fix["cost"] == j2.RATES["fix"] and fix["status"] == "done", fix
    assert any(m["text"].startswith("Adaptation's reply couldn't be used twice") for m in run.chat)
    md = open(os.path.join(run.dir, "prd.md"), encoding="utf-8").read()
    assert "## Problem" in md and "## Background" not in md, md[:300]

    # (4) the PRD question: sections only, "document", never an option that drops everything, never a repeat
    run, _ = prd(lambda fn, r, n: r)
    crit, last = list(run.goal["done_when"]), run.audits[-1]
    for r in last["results"][1:]:                       # every section but Problem fails
        r.update(verdict="NEEDS_REVISION", note="missing", **{"pass": False})
    last["rubric"][0].update(verdict="NEEDS_REVISION", **{"pass": False})
    last["conditions"][0].update(met=False, evidence="missing")
    run.outcome, run.done = None, False
    run._identity_limit({"reason": "The same failure came back twice."})
    text, q = run.chat[-1]["text"], run.paused["questions"][0]
    rows = [ln[2:] for ln in text.split("\n") if ln.startswith("- ")]
    assert rows and all(re.fullmatch(r"the (Users|Goals|Requirements|Success metrics|Out of scope) section \(.+\)", x)
                        for x in rows), rows
    assert not re.search(r"\b(?:web)?site\b", text + json.dumps(q), re.I), text
    assert not re.search(r"\bP[1-8]\b|\bD-\d\b", text), text
    assert not any(o.startswith("Leave out") for o in q["options"]), q   # it would leave only Problem
    run.paused = None
    for r in last["results"][1:4]:
        r.update(verdict="PASS", **{"pass": True})
    run.last_limit = {"state": (len(run.sites), len(run.workflows), run.spent), "decision": "continue"}
    run._identity_limit({"reason": "The same failure came back twice."})
    q = run.paused["questions"][0]
    assert q["question"].startswith("The last round produced no new work"), q
    assert not any(o.startswith("Keep going") for o in q["options"]), q          # only options that change something
    assert any(o.startswith("Leave out the Success metrics section and the Out of scope section") for o in q["options"]), q


def prd_page():
    """The page: the output type is picked before the first message and shown; the preview renders prd.md; the .md
    and .docx download, for the live run and once it is saved."""
    import threading
    import urllib.error
    import urllib.request
    import j2_server
    srv = j2_server.http.server.ThreadingHTTPServer(("127.0.0.1", 0), j2_server.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    get = lambda path: urllib.request.urlopen(base + path).read()
    post = lambda path, body: urllib.request.urlopen(urllib.request.Request(
        base + path, json.dumps(body).encode(), {"Content-Type": "application/json"}))
    try:
        j2_server.RUN.reset()
        assert json.loads(post("/api/output", {"type": "prd"}).read())["output"] == "prd"
        st = json.loads(get("/api/state"))
        assert st["output"] == "prd" and st["output_label"] == "PRD document" and st["doc"], st["output"]
        html = get("/").decode()
        assert 'id="outsel"' in html and 'id="otype"' in html and 'id="doclinks"' in html and "/api/output" in html
        say(j2_server.RUN, PRD_BRIEF)
        try:
            post("/api/output", {"type": "website"})
            raise AssertionError("the output type changed after the run started")
        except urllib.error.HTTPError as e:
            assert e.code == 409
        st = json.loads(get("/api/state"))
        assert st["files"] == ["prd.md", "prd.docx"] and st["conditions"] and st["rubric"][0][0] == "D-1", st["files"]
        prev = get("/site/latest").decode()
        assert "<h2>Problem</h2>" in prev and "<table>" in prev and "<ol>" in prev, prev[:300]
        assert get("/file/prd.md").decode().startswith("# QuickQueue") and get("/file/prd.docx")[:2] == b"PK"
        if j2.j2_check.find_chrome():            # the Simple view in Chrome: plain words, document links
            text, _, _ = simple_text(base)
            bad = SIMPLE_FORBIDDEN.findall(text) + SIMPLE_FORBIDDEN_CASE.findall(text)
            assert not bad and "Your document team" in text and "Your document is ready" in text, (bad, text[-600:])
            assert "Download the Word file (.docx)" in text and "Download the markdown (.md)" in text, text[-400:]
            assert "Download the HTML file" not in text, text[-400:]
        name = os.path.basename(j2_server.RUN.dir)
        j2_server.RUN.set_output("website")
        j2_server.RUN.reset()                    # the PRD run is now a saved run
        sv = json.loads(get(f"/api/state?run={name}"))
        assert sv["output"] == "prd" and sv["versions"] == 6 and sv["files"] == ["prd.md", "prd.docx"], sv["output"]
        assert "<h2>Requirements</h2>" in get(f"/site/latest?run={name}").decode()
        assert get(f"/file/prd.docx?run={name}")[:2] == b"PK"
        try:
            get(f"/file/goal.json?run={name}")
            raise AssertionError("/file/ served a file that isn't the document")
        except urllib.error.HTTPError as e:
            assert e.code == 404
    finally:
        srv.shutdown()
        j2_server.RUN.reset()


def website_conditions():
    """conditions/website.json: a page that breaks each of N1 to N8 is reported not met, with evidence; a plan with no
    workflow for the nav is flagged before building; workable() needs every condition; Identity's question for a
    fact shows no "None" and no internal id."""
    conds = j2.load_conditions("website.json")
    assert [c["id"] for c in conds] == [f"N{i}" for i in range(1, 9)], conds
    goal = {"site_name": "Little Fig", "facts": ["Little Fig", "+91 98765 43210"], "to_be_confirmed": []}
    src = j2.squash("Little Fig is open 8 to 10. Call +91 98765 43210 or write to hello@littlefig.in")
    good = ('<!doctype html><html><head><title>Little Fig</title></head><body><header id="hero"><nav>'
            '<a href="#menu">Menu</a> <a href="#visit">Visit</a></nav><h1>Little Fig</h1>'
            '<a class="j2-btn" href="#visit">Visit us</a></header><section id="menu"><h2>Menu</h2><p>Open 8 to 10.</p>'
            '</section><section id="visit"><h2>Visit</h2><a href="tel:+919876543210">+91 98765 43210</a> '
            '<a href="https://wa.me/919876543210">WhatsApp</a><form action="mailto:hello@littlefig.in">'
            '<input name="n"><button type="submit">Send</button></form></section></body></html>')
    clean = {"available": True, "js_errors": [], "phone": {"width": 360, "overflow_px": 0},
             "desktop": {"width": 1280, "overflow_px": 0}}

    def check(page, mech=clean, g=goal):
        return {c["id"]: c for c in j2.check_conditions(conds, " ".join(j2.PageScan(page).visible), g, src, (),
                                                         page, mech)}
    ok = check(good)
    assert all(c["met"] for c in ok.values()), ok
    breaks = {"N1": (good.replace("</h2><p>Open", "<p>Open"), clean, goal),
              "N2": (good, {**clean, "js_errors": ["ReferenceError: menu is not defined"]}, goal),
              "N3": (good, {**clean, "phone": {"width": 360, "overflow_px": 40}}, goal),
              "N4": (good.replace("https://wa.me/919876543210", "https://wa.me/+91 98765"), clean, goal),
              "N5": (good, clean, {**goal, "to_be_confirmed": ["the opening hours"]}),
              "N6": (good.replace("<p>Open 8 to 10.</p>", "<p>Open 8 to 10. Free delivery over 500.</p>"), clean, goal),
              "N7": (good.replace(' action="mailto:hello@littlefig.in"', ""), clean, goal),
              "N8": (good.replace('<a href="#menu">Menu</a> ', ""), clean, goal)}
    for cid, (page, mech, g) in breaks.items():
        r = check(page, mech, g)[cid]
        assert not r["met"] and r["evidence"] and r["evidence"] != ok[cid]["evidence"], (cid, r)
    assert "500" in check(*breaks["N6"])["N6"]["evidence"] and "#menu" in check(*breaks["N8"])["N8"]["evidence"]
    assert "wa.me/+91" in check(*breaks["N4"])["N4"]["evidence"]
    r = check(good.replace('<a class="j2-btn" href="#visit">Visit us</a>', ""))["N8"]      # no main action in the hero
    assert not r["met"] and "hero" in r["evidence"], r
    r = check(good, {"available": False, "note": "Chrome not found"})
    assert not r["N2"]["met"] and r["N2"]["evidence"].startswith("could not run"), r["N2"]
    assert not check(good, clean, {**goal, "facts": ["Koramangala"]})["N5"]["met"]

    # workable(): Audit accepts and the render check is clean; every condition met, or not workable
    row = {"id": "F-1", "item": 1, "criterion": "Menu", "verdict": "PASS", "pass": True}
    audit = {"results": [row], "rubric": [], "mechanical": fake_check(good), "conditions": list(ok.values())}
    assert j2.workable(audit) == [], j2.workable(audit)
    bad = {**audit, "conditions": list(check(*breaks["N8"]).values())}
    assert j2.workable(bad) and all("necessary condition N8 not met" in x for x in j2.workable(bad)), j2.workable(bad)

    # the plan check: no workflow for the nav is flagged before anything is built
    run = j2.J2Run()
    assert [c["id"] for c in run._plan_gaps([{"name": "Menu section", "goal_gap": "the menu"}])] == ["N8"]
    assert run._plan_gaps([{"name": "Header", "goal_gap": "a nav bar to every section and a main action"}]) == []
    orig = run.call

    def call(fn, fmt, task, mock, **k):
        r = orig(fn, fmt, task, mock, **k)
        if fn == "adaptation" and isinstance(r, dict) and "FLAGGED" not in task and r.get("workflows"):
            r["workflows"] = json.loads(json.dumps(r["workflows"]).replace(        # the first plan names no nav
                " with a nav to every section and a main action in the hero", ""))
        return r
    run.call = call
    say(run, BREW_LAB)
    finish(run)
    i = next(n for n, m in enumerate(run.chat) if m["text"].startswith("Validator flagged the plan before building"))
    assert "N8" in run.chat[i]["text"] and not any(m["who"].startswith("W-") for m in run.chat[:i]), run.chat[i]
    retry = [c for c in calls_of(run) if c["fn"] == "adaptation" and "THE VALIDATOR FLAGGED YOUR PLAN" in c["prompt"]]
    assert len(retry) == 1 and "N8" in retry[0]["prompt"], retry
    assert "NECESSARY CONDITIONS" in retry[0]["prompt"] and "N8: A nav reaches every section" in retry[0]["prompt"]
    assert run.outcome.startswith("Done"), run.outcome
    s = summary(run)
    assert s["necessary_conditions"]["met"] == s["necessary_conditions"]["total"] == 8, s["necessary_conditions"]
    saved = json.load(open(os.path.join(run.dir, "conditions.json"), encoding="utf-8"))
    assert [c["id"] for c in saved] == [f"N{i}" for i in range(1, 9)] and all(c["met"] for c in saved), saved
    assert run.snapshot()["conditions"] == run.audits[-1]["conditions"]

    # Identity's question for a fact only the Requester knows: no "None", no internal ids, no agent-facing wording
    run = j2.J2Run()
    run.goal = {"done_when": ["Opening hours are listed", "Bookings never clash"]}
    fact = ("A measurable target for double-booked slots. The brief gives none, so any number would be invented. "
            "Alternatives: Requester supplies a target, or G2 is stated as covered by the requirement R5 instead of a "
            "metric.")
    for item, ref in ((None, None), (2, "(checklist item 2: Bookings never clash)")):
        q = run._fact_question({"needs_requester_fact": fact, "item": item})["question"]
        assert "None" not in q and not j2.INTERNAL_ID.search(q) and "Alternatives" not in q, q
        assert q.startswith("A measurable target for double-booked slots. The brief gives none"), q
        assert (ref in q) if ref else "checklist item" not in q, q
    q = run._fact_question({"needs_requester_fact": "Confirm option B (G2 covered by R5, no metric)", "item": None})
    assert q["question"].startswith("Confirm option B. If you can't"), q
    run._ask_user("Nearly done. F-3 needs one number.", [q, run._fact_question({"needs_requester_fact": fact,
                                                                                  "item": 1})], "fact")
    text = run.chat[-1]["text"]
    assert "None" not in text and not j2.INTERNAL_ID.search(text) and "Alternatives" not in text and ".." not in text, text
    assert j2.requester_words("Meet in Room G2.", j2.squash("the venue is Room G2")) == "Meet in Room G2."


if __name__ == "__main__":
    if FAST:
        print("--fast: browser measurement stubbed" + ("" if BROWSER else "; tests that drive the page in Chrome are "
                                                       "skipped below (add --browser to run them)"))
    for mode in ("0", "1"):
        os.environ["J2_FIXES"] = mode
        vague(mode == "1")
        vague_stories(mode == "1")
        full(mode == "1")
        policy_budget(mode == "1")
        below_floor()
        thread_and_loom_core()
        deferred_twice()
        connections()
        build_before_asking()
        print(f"J2_FIXES={mode}: vague brief (both answers), full brief, budget question rejected and re-asked, below-floor proposal with left_out, one decision question after the ruling, core marks from J2.a, deferred twice, connections at three budgets, funded work built before the question ok")
        workflow_agents()
        atom_checks()
        leave_out_named()
        rubric_and_credits()
        charter_numbers()
        chrome_unavailable()
        unique_short_names()
        same_failure()
        cycle_limit()
        to_be_confirmed()
        bargain_time()
        memory()
        forced_fail()
        test_lessons()
        style_guide()
        rubric_loop()
        lone_rubric_failure()
        pricing()
        unpaid_items()
        intake_needs()
        playbooks()
        summary_before_review()
        prd_run()
        prd_checks()
        prd_groups_metrics_assumptions()
        prd_recovery()
        website_conditions()
        print(f"J2_FIXES={mode}: website necessary conditions: N1 to N8 each reported not met with evidence, nav plan "
              "flagged before building, workable needs every condition, no None or internal ids for the Requester ok")
        print(f"J2_FIXES={mode}: PRD output: mock PRD brief Done workable with prd.md and prd.docx, document checks pass "
              "and fail (duplicate R2 rejected), invented facts-present rejected, no browser check, no website "
              "conditions, P7 user groups, P8 window warning, assumptions labelled and listed, short names, heading targets "
              "normalised, wrong target is CHECK_WRONG, unusable reply twice gets a code fix, sections-only question ok")
        print(f"J2_FIXES={mode}: B workflow agents, atom checks (rules, receipts, third failure to Adaptation), leave-out question names its items, rubric in briefs, tap targets, no \"units\", charter numbers for agents, no Chrome = could not run, unique short names, C workable loop and limits, D memory, F forced audit failure (hidden from agents) and test lessons, summary before review, H style guide, rubric loop, needs, playbooks, I pricing and unpaid items ok")
    ruling_over_budget()
    redirect()
    workable_unit()
    playbook_matching()
    limit_answers()
    nine_workflows()
    budget_cap()
    repeats()
    adaptation_idle()
    identity_decisions()
    two_audiences()
    audiences_everywhere()
    limit_wording()
    open_list()
    covers_by_text()
    readable_decision()
    simple_messages()
    owner_override()
    form_submit()
    print("second pass: two audiences, simple messages, owner override, form submit ok")
    print("limit answers (turn cap, nine workflows, own amount, drop with reason, done with open items), budget cap, repeats, idle Adaptation, decisions applied by code (msgs 24, 50) ok")
    page()
    prd_page()
    print("PRD page: output picked before the first message and shown, preview from prd.md, .md and .docx downloads ok")
    print("E behind-the-scenes view (lanes, detail, timeline, saved runs, redaction, lessons) ok")
    generalist_units()
    detail_stays_open()
    work_atoms()
    work_atom_cards()
    print("work atoms: validator names a missing field and retries once, atoms stored and tagged, cards render ok")
    print("Detailed view: opened screenshot, event log and message detail stay open while the run updates ok")
    simple_view()
    plain_words()
    identity_prompt_is_plain()
    print("G simple view (plain words at the source and as fallback, buttons once, phone toggle, ready card) ok")
    assert fingerprint(REAL_MEMORY) == REAL_BEFORE, "the tests changed the real memory/ files"
    print("playbooks: same business type only, mock memory kept from live runs; real memory/ untouched ok")
    print("j2 flow checks passed")
