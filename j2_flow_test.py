"""Offline check of the J2 flow in mock mode: python j2_flow_test.py [--chat]

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

BREW_LAB = ("A one-page website for Brew Lab, a small specialty coffee shop in Indiranagar, Bengaluru. Visitors should "
            "see the menu with prices, the opening hours, and where to find us, and be able to pre-order a coffee for "
            "pickup. It should feel warm and modern and work well on a phone. Include a section about our beans and the "
            "farms they come from, and a simple loyalty-card explainer (buy 9, get the 10th free).")
SHOW = "--chat" in sys.argv


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
    assert q["options"][0].startswith("Add 30 units and keep going") and q["budget"][0] == 30 and q["options"][-1].startswith("Finish as it is")
    say(run, "1")
    assert run.budget == 120 and run.outcome.startswith("Done"), (run.budget, run.outcome)
    s = summary(run)
    assert s["status"] == "done" and s["limits_hit"] and not s["workable"], s


def policy_budget(fixes):
    """Bug from runs/j2-20261006-130411: the Requester picked a budget-raise option on a policy question and the
    ledger didn't change. Adaptation asks a policy question; Identity says the Requester must decide and 40 is needed,
    so code asks the decision question (Identity can't offer money itself); the first answer is unclear (asked once
    more); "option 1" raises the budget by code; the work is granted and built."""
    run = j2.J2Run()
    run.budget = 60
    orig, asked = run.call, []

    def call(fn, fmt, task, mock, **k):
        if fn == "adaptation" and not asked and "WHY YOU ARE UP" in task:
            asked.append(1)
            return {"say": "@Identity Policy question: 60 can't cover the charter's sections. Can we add budget?",
                    "act": "POLICY_QUESTION", "question": "60 can't cover the charter's sections. Add budget?"}
        if fn == "identity" and task.startswith("QUESTION FROM"):
            return {"say": "@Adaptation The charter doesn't set the budget; asking the Requester.", "clause": "authority",
                    "needs_decision": True, "budget_needed": 40}
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    say(run, BREW_LAB)
    assert run.paused and run.paused["kind"] == "limit" and run.budget == 60, run.outcome
    assert run.paused["questions"][0]["options"][0].startswith("Add 40 units and keep going"), run.paused
    say(run, "the bigger one I think")                       # unclear: no guess, Identity asks once more
    assert run.paused and run.paused["handoff"].get("reasked") and run.budget == 60, run.paused
    say(run, "option 1")
    assert run.budget == 100 and run.raises[0]["asked"] == 40, run.raises
    d = [x for x in run.decisions if x["kind"] == "limit"]
    assert d[0].get("unclear") and d[1]["decision"] == "continue" and d[1]["budget_added"] == 40, d
    built = [w for w in run.workflows if w["status"] == "done"]
    assert built and run.spent > 60, (run.spent, built)       # work beyond the old 60 was granted and built
    assert run.outcome.startswith("Done"), run.outcome
    assert summary(run)["budget"]["granted"] == 100
    only_identity_addresses_user(run)
    show(run)


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
    reg, refused, _ = run._register([{"name": "Core sections rework", "goal_gap": "tighter copy", "outputs": ["W-2"],
                                      "completion_check": "same items", "parts": ["fix"], "revises": "W-2"}])
    assert reg and not refused and reg[0]["section"] == "W-2" and reg[0]["revises"] == "W-2", (reg, refused)
    run._turn_workflow_agent({"wid": reg[0]["id"]})
    assert run.sections["W-2"]["owner"] == reg[0]["id"] and f"(owner {reg[0]['id']})" in run.sites[-1]
    # past retry_limit: the agent reports the failure to Coordination and its section is unchanged
    reg, _, _ = run._register([{"name": "Broken one", "goal_gap": "x", "outputs": ["y"], "completion_check": "z",
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
                f = next(x for x in r["findings"] if x["item"] == 1)
                if "menu" in run.goal["done_when"][0].lower():
                    f.update(verdict="NEEDS_REVISION", evidence="Prices missing")
            if fn == "adaptation" and "WHY YOU ARE UP" in task and run.audits and not run.audits[-1]["results"][0]["pass"]:
                r = {"say": "@Priority Menu fix.", "act": "PROPOSE", "next": "Priority", "workflows": [
                    {"name": "Menu fix", "goal_gap": "prices", "parts": ["fix"], "fixes": ["F-1"], "outputs": ["menu"],
                     "completion_check": "prices"}]}
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
    cases = {"only 10 units stay for fixes after Audit": "Only 10 effort points stay for fixes after our checks",
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
    base = {"goal_gap": "x", "outputs": ["index.html"], "completion_check": "y"}
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
    # after the first Audit: a fix relabelled as a cheaper part is rejected, with or without listing the finding
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

    run = at_cap()
    say(run, "Option 3")
    assert run.outcome.startswith("Done with open items") and not run.paused, run.outcome
    assert summary(run)["status"] == "done_with_open_items"


def budget_cap():
    """The cap shows in the option text; an option that adds budget the cap won't allow is never offered, and
    "keep working" isn't offered when it can't fund anything or when it already changed nothing."""
    run = j2.J2Run()
    q = {"question": "More?", "options": ["Add more building", "Ship"], "budget": [30, 0]}
    run._ask_user("x", [q], "question")             # only the decision question may carry money
    assert "budget" not in run.paused["questions"][0], run.paused
    run.budget = j2.BUDGET_CAP - 40                 # Identity says 78 is needed; the cap allows 40
    run._identity_limit({"reason": "Adaptation asked", "budget_needed": 78})
    o = run.paused["questions"][0]["options"][0]
    assert o.startswith("Add 40 units (the most allowed)") and run.paused["questions"][0]["budget"][0] == 40, o
    run.budget = j2.BUDGET_CAP
    run._identity_limit({"reason": "Adaptation asked", "budget_needed": 78})
    assert not any(o.startswith(("Add ", "Keep going")) for o in run.paused["questions"][0]["options"]), run.paused
    cheapest = min(j2.RATES.values())
    run.spent = run.budget - cheapest + 1                       # less than the cheapest part left, no room to add
    run._identity_limit({"reason": "Out of budget", "out_of_budget": True})
    assert not any(o.startswith(("Add ", "Keep going")) for o in run.paused["questions"][0]["options"]), run.paused
    run.spent = 0                                               # money left: keep working is offered once
    run._identity_limit({"reason": "turn cap"})
    assert run.paused["questions"][0]["options"][0].startswith(("Add ", "Keep going")), run.paused
    run.last_limit["decision"] = "continue"                     # ...and changed nothing: not offered again
    run._identity_limit({"reason": "turn cap"})
    assert not any(o.startswith(("Add ", "Keep going")) for o in run.paused["questions"][0]["options"]), run.paused


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
    run._turn_adaptation(h)
    assert asked == ["adaptation"] and run.turn == "identity" and run.handoff["kind"] == "question", run.handoff
    run.agent_turns["adaptation"] = 2
    run._turn_adaptation(h)
    assert asked == ["adaptation"], "Adaptation was asked again with nothing changed"
    assert run.turn == "identity" and run.handoff["kind"] == "limit" and run.handoff["out_of_budget"], run.handoff
    assert run.chat[-1]["who"] == "system" and "isn't asked again" in run.chat[-1]["text"]
    for change in (lambda: run.decisions.append({"answer": "1"}),               # a new Requester answer
                   lambda: run.goal["done_when"].pop(),                        # an item dropped
                   lambda: setattr(run, "budget", run.budget + 1)):            # budget raised (still short)
        change()
        n = len(asked)
        run._turn_adaptation(h)
        assert len(asked) == n + 1, "a change must let Adaptation re-plan"


def identity_decisions():
    """runs/j2-20261008-123848: when the money ran out, Identity asked its own free-form question (msgs 22, 48), so
    code applied nothing: "2. Add 25 more. Leave out ..." added nothing and the items came back (msg 24 -> 56), and
    "option 2: finish as is" led to a rejected done and the limit question again (msg 50 -> 56). Now money, leaving
    items out and finishing are only ever asked by code's decision question, and a typed answer is applied."""
    def out_of_money():
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
    later = " ".join(m["text"] for m in run.chat[n + 1:] if m["who"] == "identity")
    assert not any(c in later for c in gone), "dropped items came back"

    # msg 50: "finish as is" ends the run, no rejected done and no limit question straight after
    run = out_of_money()
    n = len(run.chat)
    say(run, "option 2: finish as is")
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
    assert len(mine) == 1 and mine[0]["text"] == "@Requester Thanks, got it.", mine        # the regenerated reply
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
        say(run, f"{key} ship")
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
    assert len(re.findall(r"(?m)(?:^|\s)\d+\.(?:\s|$)", txt)) == 1 and "1.\n1." not in txt, txt

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
    listed = run.chat[-1]["text"].split("Still not right: ")[1].split("\n")[0].rstrip(".").split("; ")
    assert len(listed) == len(gaps) and q["options"][-1].endswith(f"with {len(gaps)} things still not right"), (listed, q)
    for o in q["options"]:
        assert "you get" in o, o
    run.spent = run.budget                                    # money: the option says the amount
    run._identity_limit({"reason": "Out of budget", "out_of_budget": True})
    q = run.paused["questions"][0]
    assert q["question"].startswith("The work you approved is used up. Add more and keep going"), q["question"]
    assert re.match(r"Add \d+ units", q["options"][0]) and all("you get" in o for o in q["options"]), q["options"]


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
        listed = text.split("Still not right: ")[1].split(".")[0].split("; ")
        return text, listed, run.paused["questions"][0]["options"][-1]

    # (a) 1 audit failure + 3 unfinished workflows (registered, running, unfunded) -> 4 items, "4 things"
    run = paused_run()
    unfinished(run, [2]), unfinished(run, [3], "running"), unfinished(run, [5], "unfunded")
    text, listed, ship = ask(run)
    crit = run.goal["done_when"]
    assert len(listed) == 4 and ship.endswith("with 4 things still not right"), (listed, ship)
    assert listed[0] == crit[0] and listed[1] == f"{crit[1]} (not built yet)", listed

    # (b) an item both failing in the audit and covered by an unfinished workflow appears once
    run = paused_run()
    unfinished(run, [1, 2])
    text, listed, ship = ask(run)
    assert listed == [crit[0], f"{crit[1]} (not built yet)"] and ship.endswith("with 2 things still not right"), listed

    # (c) the site is newer than the last audit: what was built since is marked, and the message says so
    run = paused_run()
    run.sites.append(run.sites[-1])
    run.workflows.append({"id": "W-99", "name": "y", "status": "done", "covers": [1, 4], "version": len(run.sites)})
    text, listed, ship = ask(run)
    assert listed == [f"{crit[0]} (not checked yet)", f"{crit[3]} (not checked yet)"], listed
    assert "built after the last check, so they're not checked yet" in text and ship.endswith("with 2 things still not right"), text


if __name__ == "__main__":
    for mode in ("0", "1"):
        os.environ["J2_FIXES"] = mode
        vague(mode == "1")
        vague_stories(mode == "1")
        full(mode == "1")
        policy_budget(mode == "1")
        print(f"J2_FIXES={mode}: vague brief (both answers), full brief, policy-question budget raise ok")
        workflow_agents()
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
        print(f"J2_FIXES={mode}: B workflow agents, C workable loop and limits, D memory, F forced audit failure (hidden from agents) and test lessons, summary before review, H style guide, rubric loop, needs, playbooks, I pricing and unpaid items ok")
    ruling_over_budget()
    redirect()
    workable_unit()
    playbook_matching()
    limit_answers()
    budget_cap()
    repeats()
    adaptation_idle()
    identity_decisions()
    two_audiences()
    audiences_everywhere()
    limit_wording()
    open_list()
    simple_messages()
    owner_override()
    form_submit()
    print("second pass: two audiences, simple messages, owner override, form submit ok")
    print("limit answers (turn cap, own amount, drop with reason, done with open items), budget cap, repeats, idle Adaptation, decisions applied by code (msgs 24, 50) ok")
    page()
    print("E behind-the-scenes view (lanes, detail, timeline, saved runs, redaction, lessons) ok")
    generalist_units()
    detail_stays_open()
    print("Detailed view: opened screenshot, event log and message detail stay open while the run updates ok")
    simple_view()
    plain_words()
    identity_prompt_is_plain()
    print("G simple view (plain words at the source and as fallback, buttons once, phone toggle, ready card) ok")
    assert fingerprint(REAL_MEMORY) == REAL_BEFORE, "the tests changed the real memory/ files"
    print("playbooks: same business type only, mock memory kept from live runs; real memory/ untouched ok")
    print("j2 flow checks passed")
