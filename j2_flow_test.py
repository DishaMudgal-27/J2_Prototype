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
F. J2_FORCE_AUDIT_FAIL=<item>: a forced cycle-1 failure that agents can't tell from a real finding (no test label in
   any prompt), then a real fix, a real re-check and a saved lesson. summary.json exists before the reviewer call.
   J2_MEMORY_TEST_LESSONS=1 lets J2.b read test lessons (off by default), flagged in the chat and the lanes.
Runs are written to runs/ (or J2_RUNS_DIR); each ended run has summary.json. Memory is off (J2_MEMORY=0) except in
the memory test, which uses its own lessons file.
"""
import json
import os
import sys
import time

import tempfile

os.environ["STUDIO_MOCK"] = "1"
os.environ["J2_MEMORY"] = "0"        # clean runs: the memory test turns it on with its own file
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
    assert q["options"][0].startswith("Keep working: add 30") and q["budget"][0] == 30 and q["options"][-1].startswith("Ship")
    say(run, "1")
    assert run.budget == 120 and run.outcome.startswith("Done"), (run.budget, run.outcome)
    s = summary(run)
    assert s["status"] == "done" and s["limits_hit"] and not s["workable"], s


def policy_budget(fixes):
    """Bug from runs/j2-20261006-130411: the Requester picked a budget-raise option on a policy question and the
    ledger didn't change. Adaptation asks a policy question; Identity offers an option that adds 40 units; the first
    answer is unclear (Identity asks once more); "option 1" raises the budget by code; the work is granted and built."""
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
                    "user_question": {"question": "Add budget so the charter's sections can be built?", "options": [
                        {"text": "Add 40 units (60 to 100)", "budget_increase": 40},
                        {"text": "Keep 60 and build less", "budget_increase": 0}]}}
        return orig(fn, fmt, task, mock, **k)
    run.call = call
    say(run, BREW_LAB)
    assert run.paused and run.paused["kind"] == "question" and run.budget == 60, run.outcome
    say(run, "the bigger one I think")                       # unclear: no guess, Identity asks once more
    assert run.paused and run.paused.get("reasked") and run.budget == 60, run.paused
    say(run, "option 1")
    assert run.budget == 100 and run.raises[0]["asked"] == 40, run.raises
    d = [x for x in run.decisions if x["kind"] == "question"]
    assert d[0].get("unclear") and d[1]["option"] == 1 and d[1]["budget_added"] == 40, d
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
                                "parts": ["fix"]}])
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
                    {"name": "Menu fix", "goal_gap": "prices", "parts": ["fix"], "outputs": ["menu"],
                     "completion_check": "prices"}]}
            return r
        run.call = call
        return run
    run = failing_run()
    say(run, BREW_LAB)
    assert run.paused and run.paused["kind"] == "limit" and "same failure" in run.paused["handoff"]["limit"], run.outcome
    opts = run.paused["questions"][0]["options"]
    assert [o.split(":")[0] for o in opts] == ["Keep working", "Drop the failing done-when items", "Ship as is"], opts
    say(run, "2, drop it")
    assert run.outcome.startswith("Done") and run.goal["dropped_by_requester"][0].startswith("The menu"), run.outcome
    assert summary(run)["dropped_by_requester"]
    only_identity_addresses_user(run)

    run2 = failing_run()
    say(run2, BREW_LAB)
    say(run2, "ship it as is")
    s = summary(run2)
    assert run2.outcome.startswith("Shipped") and s["status"] == "shipped" and s["workable"], run2.outcome


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
    assert run.paused and run.paused["kind"] == "limit" and run.paused["handoff"]["limit"].startswith("Only you"), run.outcome
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
        assert w1["section"] == "W-1" and w1["attempts"] == 1 and w1["last_check"].startswith("usable"), w1
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
        summary_before_review()
        print(f"J2_FIXES={mode}: B workflow agents, C workable loop and limits, D memory, F forced audit failure (hidden from agents) and test lessons, summary before review ok")
    ruling_over_budget()
    redirect()
    workable_unit()
    page()
    print("E behind-the-scenes view (lanes, detail, timeline, saved runs, redaction, lessons) ok")
    print("j2 flow checks passed")
