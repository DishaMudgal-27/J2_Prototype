"""J2: the five functions run one department until Identity's goal is met (Native docs, system/department).
The flow follows the J2 diagram (docs/j2-flow.jpg):

  J2.a  Identity reads the Requester's brief: enough information to work? If not, it asks the Requester specific
        questions and the run waits; it asks as many rounds as it needs, then records the charter. It invents
        nothing. A fact the Requester can't supply yet is recorded as "to be confirmed" against its done-when item.
  J2.b  Adaptation proposes workflows (or disputes an Audit finding or a Coordination HOLD), using the most
        relevant lessons from earlier runs (memory/lessons.jsonl)
  J2.c  Priority prices the proposal: GRANT, COUNTER or REFUSE. The bargain is bounded by four hops, fifteen
        minutes and its spend (AI calls); past any of them it goes to Identity
  J2.d  Any two agents that disagree get 4 attempts to settle it themselves; then Identity resolves it from the
        charter, or, if the charter doesn't decide it, asks the Requester one decision-ready question and rules
  J2.e  Validator (plain code) checks and registers the agreed workflows; each one gets its own workflow agent
        ("W-1 Builder") that owns one marked section of the site file
  J2.f  Coordination schedules; Priority checks each run's envelope; the workflow's agent writes its section,
        retries within its envelope and reports back to Coordination
  J2.g  Audit checks the result against the charter's done-when list and files its findings to Identity. A
        missing fact only the Requester knows becomes Identity's question to the Requester
  J2.h  Identity: is the site workable (see workable())? Yes: Identity tells the Requester the goal is reached.
        No: back to J2.b. When Audit confirms a fix worked, Adaptation saves a lesson

Only Identity talks to the Requester: any other agent that addresses the Requester is redirected to Identity.
Each function's instructions come from agents/j2/team.md + agents/j2/<function>.md, read fresh on every call.
Speaking order is dynamic: every reply names "next", and code allows only the routes in ROUTES (an illegal pick
is redirected with a "Route check" note). Code also enforces the limits: 4 attempts per disagreement, budget,
max cycles, max turns per cycle and the same failure twice in a row. A limit never stops the run silently:
Identity asks the Requester to add budget, drop the failing items or ship as is. A run that waits on the
Requester stops and resumes on the reply, so it can't loop on its own.

J2_FIXES (default 0) picks the mode, so findings can compare the two:
  0  baseline, as close to the diagram as possible: an Identity ruling goes straight to the validator (J2.d ->
     J2.e), and a change request after done goes straight to Adaptation (J2.b).
  1  fixes: (a) an Identity ruling that costs more than Priority granted goes back to Priority (J2.c) once for
     pricing; Priority's answer is final, and if the ruling is still over budget Identity asks the Requester.
     (b) a change request after done goes to Identity at J2.a first, then J2.b.
"""
import html
import json
import os
import re
import threading
import time

import j2_check
import llm

HERE = os.path.dirname(os.path.abspath(__file__))
J2_DIR = os.path.join(HERE, "agents", "j2")
RUNS_DIR = os.getenv("J2_RUNS_DIR") or os.path.join(HERE, "runs")
BUDGET = int(os.getenv("J2_BUDGET", "100"))           # starting budget
BUDGET_CAP = int(os.getenv("J2_BUDGET_CAP", str(2 * BUDGET)))   # most the Requester's approvals can raise it to
MAX_ATTEMPTS = 4           # attempts two disagreeing agents get before Identity rules (priority.md: four exchanges)
BARGAIN_MINUTES = float(os.getenv("J2_BARGAIN_MINUTES", "15"))   # J2.c bargain: four hops, fifteen minutes...
BARGAIN_CALLS = int(os.getenv("J2_BARGAIN_CALLS", "8"))          # ...and its spend, in AI calls (4 hops x 2 sides)
MAX_CYCLES = int(os.getenv("J2_MAX_CYCLES", "6"))   # plan -> build -> audit loops before Identity asks the Requester
LIMIT_ADD = int(os.getenv("J2_LIMIT_ADD", "30"))    # budget the "keep working" option adds when the budget ran out
MEMORY_FILE = os.getenv("J2_MEMORY_FILE") or os.path.join(HERE, "memory", "lessons.jsonl")
MAX_LESSONS = 5            # lessons Adaptation reads at J2.b
MAX_TURNS = int(os.getenv("J2_MAX_TURNS", "30"))       # agent turns per cycle
CHAT_FULL_CHARS = int(os.getenv("J2_CHAT_FULL_CHARS", "60000"))   # above this, summary + recent messages
CHAT_TAIL = 40             # messages always shown in full once the chat is summarised
SUMMARY_REFRESH = 20       # re-summarise once this many more messages have scrolled out of the tail
SITE_LIMIT = 150_000       # characters of the site the workflow agents and Audit see
SITE_WARN_BYTES = 60_000   # builder.md asks for a single page under ~60 KB
DELAY = 0 if llm.MOCK else float(os.getenv("J2_DELAY", "2"))   # spacing for free-tier rate limits

NAMES = {"validator": "Validator", "identity": "Identity", "adaptation": "Adaptation",
         "priority": "Priority", "coordination": "Coordination", "audit": "Audit", "user": "Requester (you)",
         "system": "System"}
# Who may hand the turn to whom (J2 routes). Code narrows these further by situation. Only Identity reaches the
# Requester ("user"); an agent that addresses the Requester anyway is redirected to Identity.
ROUTES = {"identity": ("user", "adaptation", "priority", "coordination", "audit"),
          "adaptation": ("priority", "identity", "audit", "coordination"),    # Audit/Coordination: to dispute
          "priority": ("adaptation", "identity", "coordination"),   # Coordination: envelope check (HOLD)
          "coordination": ("priority", "adaptation", "identity"),
          "audit": ("adaptation", "identity")}
# Workflow agents ("W-1" -> "W-1 Builder") are added to NAMES and ROUTES when their workflow is registered.
# ponytail: module-level registry; ids restart at W-1 each run, so names stay correct for one run at a time.


def add_workflow_agent(wid):
    NAMES[wid] = f"{wid} Builder"
    ROUTES[wid] = ("coordination",)


def is_wf_agent(fn):
    return bool(re.fullmatch(r"W-\d+", str(fn or "")))
# J2 steps, labelled as in the diagram, for the progress strip in the UI
STEPS = {1: "J2.a Enough information to work?", 2: "J2.b Adaptation proposes workflows",
         3: "J2.c Priority prices the proposal", 4: "J2.d Identity resolves conflict",
         5: "J2.e Validator registers workflow", 6: "J2.f Coordination schedules, workflow agents build",
         7: "J2.g Audit checks result", 8: "J2.h Is the site workable?"}
TOPICS = {"proposal": "what to fund", "finding": "an Audit finding", "hold": "a Coordination HOLD"}
PAUSES = {"info": "J2.a: not enough information to work yet",
          "charter_drop": "the charter leaves out items from the brief",
          "conflict": "J2.d: a conflict the charter doesn't decide",
          "question": "a question the charter can't answer",
          "approval": "approval for a run over its envelope",
          "ruling_budget": "J2_FIXES=1: Identity's ruling is over budget after Priority's final answer",
          "audit": "J2.h: a done-when item only the Requester can close",
          "fact": "J2.g: a fact only the Requester knows",
          "limit": "a safety limit was hit: add budget, drop the failing items or ship as is"}
TO_USER = re.compile(r"@(?:requester|user)\b", re.I)


def system_prompt(fn, reply_format):
    parts = []
    for name in ("team.md", "builder.md" if is_wf_agent(fn) else f"{fn}.md"):
        path = os.path.join(J2_DIR, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                parts.append(f.read().strip())
    parts.append(f"You are {NAMES[fn]}.\n\n## Reply format (required)\n{reply_format}")
    return "\n\n".join(parts)


def wf_cost(w):
    """Official proposals put cost in estimated_resources.money; the mock uses "cost"."""
    est = w.get("estimated_resources") or {}
    try:
        return int(float(w.get("cost") or est.get("money") or 0))
    except (TypeError, ValueError):
        return 0


def cost_of(wfs):
    return sum(wf_cost(w) for w in wfs or [])


ENVELOPE_DEFAULTS = {"model_call_limit": 2, "retry_limit": 1}   # used only when Priority leaves them out


def as_int(x, default=0):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return default


RATES_ON = os.getenv("J2_RATES", "1") != "0"
RATES = {}      # agents/j2/rates.json, reloaded at each reset so edits apply without a restart


def load_rates():
    global RATES
    RATES = {}
    path = os.path.join(J2_DIR, "rates.json")
    if RATES_ON and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            RATES = {k: int(v) for k, v in (json.load(f).get("rates") or {}).items()}


def price(w):
    """(rate-card cost, unknown parts) for a workflow's "parts"; (None, []) when the rate card is off or parts are missing."""
    parts = w.get("parts")
    if not RATES or not isinstance(parts, list) or not parts:
        return None, []
    unknown = [str(p) for p in parts if str(p) not in RATES]
    return sum(RATES.get(str(p), 0) for p in parts), unknown


def granted(w):
    """Rate-card price when the rate card is on; otherwise the money Priority granted (envelope.money_limit),
    and Adaptation's estimate only if no limit was given."""
    c, _ = price(w)
    if c is not None:
        return c
    m = as_int((w.get("envelope") or {}).get("money_limit"))
    return m if m > 0 else wf_cost(w)


def granted_total(wfs):
    return sum(granted(w) for w in wfs or [])


def norm(wfs):
    """Keep only workflow objects and give each a plain "cost" (the UI and validator read it):
    the rate-card price of its parts when the rate card is on, else the agent's estimate."""
    out = []
    for w in wfs or []:
        if isinstance(w, dict):
            c, _ = price(w)
            est = w.get("estimate", wf_cost(w))   # the agent's own estimate, kept for the run report
            out.append({**w, "estimate": est, "cost": c if c is not None else wf_cost(w)})
    return out


def key(name):
    s = str(name or "").strip().lstrip("@").strip().lower()
    s = s.split()[0] if s else ""
    return "user" if s in ("requester", "user") else s


def address(text, who):
    """Make the message's @name match the agent that actually speaks next."""
    tag, text = "@Requester" if who == "user" else "@" + NAMES[who], (text or "").strip()
    if tag.lower() in text.lower():
        return text
    return f"{tag} " + re.sub(r"^@\w+[,:]?\s*", "", text)


def next_field(allowed, hint=""):
    return f'"next": "{"|".join("Requester" if a == "user" else NAMES[a] for a in allowed)}"' + (f" ({hint})" if hint else "")


def line(m):
    return f"[{m['id']}] {NAMES.get(m['who'], m['who'])}: {m['text']}"


def clean_questions(raw):
    """[{question, options, budget?}] from whatever shape the model returned. An option may be a string or
    {"text", "budget_increase"}; "budget" (one int per option) is kept only when some option adds budget."""
    out = []
    for x in raw or []:
        if isinstance(x, dict):
            q = str(x.get("question") or x.get("summary") or "").strip()
            raw_opts = [o for o in x.get("options") or [] if str(o.get("text") if isinstance(o, dict) else o).strip()]
            opts = [str(o.get("text") if isinstance(o, dict) else o).strip() for o in raw_opts]
            budget = [max(0, as_int(o.get("budget_increase"))) if isinstance(o, dict) else 0 for o in raw_opts]
        else:
            q, opts, budget = str(x or "").strip(), [], []
        if q:
            out.append({"question": q, "options": opts, **({"budget": budget} if any(budget) else {})})
    return out


def numbered(qs):
    def opt(q, j, o):
        add = q["budget"][j - 1] if q.get("budget") else 0
        return f"\n   Option {j}: {o}" + (f" [adds {add} units to the budget]" if add else "")
    return "\n".join(f"{i}. {q['question']}" + "".join(opt(q, j, o) for j, o in enumerate(q["options"], 1))
                     for i, q in enumerate(qs, 1))


OPTION_FMT = ('{"text": str, "budget_increase": int (units this option adds to the budget if the Requester picks it; '
              '0 if none. Code applies it; you can\'t change the budget yourself)}')


def option_picked(q, answer):
    """Index of the one option the answer names (by number or by its full text), or None if it isn't clear."""
    nums = {int(n) for n in re.findall(r"(?<!\d)(?<!\d\.)([1-9])(?!\d)(?!\.\d)", str(answer))} & set(range(1, len(q["options"]) + 1))
    texts = {j for j, o in enumerate(q["options"], 1) if o and o.lower() in str(answer).lower()}
    hits = nums | texts
    return hits.pop() - 1 if len(hits) == 1 else None


def brief_list(pos):
    """A final position as one line: workflow names and costs, or the text itself."""
    if isinstance(pos, list):
        return ", ".join(f"{w.get('name')} ({w.get('cost')})" for w in pos) or "nothing"
    return str(pos or "")[:300]


# ---- mock mode helpers (scripted functions, no model): a generic charter and page built from the text
def mock_charter(text):
    t = text.lower()
    m = re.search(r"\b(?:for|called)\s+([A-Z][\w']*(?:\s+[A-Z][\w']*)*)", text)
    name = m.group(1) if m else "Our cafe"
    items = [d for k, d in (("menu", "The menu with prices is shown"), ("hour", "Opening hours are listed"),
                            ("where", "The address and a map link are shown"),
                            ("order", "Visitors can pre-order a coffee for pickup with a form"),
                            ("bean", "A section about the beans and the farms they come from"),
                            ("loyalty", "A loyalty-card explainer (buy 9, get the 10th free)")) if k in t]
    items.append("Layout works on a phone")
    return {"statement": f"A one-page website for {name} where visitors find what they need and come in",
            "site_name": name, "audience": "Local customers, mostly on phones",
            "standards": ["Warm, modern feel", "Fast first screen on a phone"],
            "rules": ["Plain HTML/CSS/JS in one file", "No real customer data"],
            "done_when": items, "to_be_confirmed": [], "dropped_from_brief": []}


def mock_section(w, goal, sections):
    """(head, body) a scripted workflow agent writes: the scaffold styles the page, a viewport fix adds the meta tag,
    anything else adds the done-when items no other section covers yet (or a plain section named after it)."""
    g, n = goal or {}, w["name"].lower()
    if "scaffold" in n:
        return ("<style>body{font:16px system-ui;margin:0 auto;max-width:900px;padding:24px;background:#fbf7f2;"
                "color:#2b211b}section{padding:16px 0;border-top:1px solid #e6dccf}</style>",
                f"<header><h1>{html.escape(g.get('site_name') or 'Our site')}</h1>"
                f"<p>{html.escape(g.get('statement') or '')}</p></header>")
    if "viewport" in n:
        return '<meta name="viewport" content="width=device-width, initial-scale=1">', ""
    others = "".join(x["body"] for sid, x in sections.items() if sid != w["section"])
    items = "".join(f'<section data-item="{i}"><h2>{html.escape(str(d))}</h2><p>Sample content (replace before '
                    "launch).</p></section>" for i, d in enumerate(g.get("done_when") or [], 1)
                    if "phone" not in str(d).lower() and f'data-item="{i}"' not in others)
    return "", items or f"<section><h2>{html.escape(w['name'])}</h2><p>Sample content.</p></section>"


# ---- the site file: one marked section per workflow agent, assembled by code
def assemble(title, sections):
    head = "".join(f"\n<!-- J2:{sid} head start (owner {x['owner']}) -->\n{x['head']}\n<!-- J2:{sid} head end -->"
                   for sid, x in sections.items() if x.get("head"))
    body = "".join(f"\n<!-- J2:{sid} start (owner {x['owner']}) -->\n{x['body']}\n<!-- J2:{sid} end -->"
                   for sid, x in sections.items() if x.get("body"))
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<title>{html.escape(title)}</title>'
            f"{head}\n</head>\n<body>{body}\n</body>\n</html>\n")


def parse_section(raw):
    """(head, body) from a workflow agent's reply; ValueError with the reason when it can't be used."""
    hm = re.search(r"```head\s*(.*?)```", raw, re.S | re.I)
    bm = re.search(r"```(?:section|html)\s*(.*?)```", raw, re.S | re.I)
    head, body = (hm.group(1).strip() if hm else ""), (bm.group(1).strip() if bm else "")
    if not head and not body:
        raise ValueError("the reply has no ```section or ```head block")
    if re.search(r"<\s*(?:!doctype|html|body|head)\b", body, re.I):
        raise ValueError("the section contains <html>, <head> or <body> tags; write only your section's markup")
    if re.search(r"<\s*(?:!doctype|html|body)\b", head, re.I):
        raise ValueError("the head block may hold only meta, link, style and script tags")
    return head, body


def workable(audit):
    """Code's verdict on the latest audit, no model: what stops the site being workable ([] = workable).
    Every done-when item passes Audit (a "to be confirmed" item never does), and the render check found no JS
    errors, no horizontal overflow at 360px or 1280px, no broken form and no broken in-page link."""
    if not audit:
        return ["no site has been audited yet"]
    out = [f"done-when item {r['item']} ({r['id']} {r['verdict']}): {r['criterion']}" for r in audit["results"]
           if not r["pass"]]
    mech = audit.get("mechanical") or {}
    if not mech.get("available"):
        return out + [f"render check didn't run, so JS errors, overflow and forms are unverified: {mech.get('note')}"]
    return out + j2_check.problems(mech)


def failure_signature(audit):
    return sorted(f"{r['criterion']}|{r['verdict']}" for r in audit["results"] if not r["pass"]) \
        + sorted(j2_check.problems(audit.get("mechanical") or {}))


# ---- Adaptation's memory: lessons from fixes Audit confirmed, kept across runs in memory/lessons.jsonl
def memory_on():
    return os.getenv("J2_MEMORY", "1") != "0"


def load_lessons():
    if not memory_on() or not os.path.exists(MEMORY_FILE):
        return []
    out = []
    with open(MEMORY_FILE, encoding="utf-8") as f:
        for ln in f:
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def save_lesson(lesson):
    if not memory_on():
        return
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(lesson, ensure_ascii=False) + "\n")


def clear_lessons():
    """Delete memory/lessons.jsonl; returns how many lessons it held."""
    if not os.path.exists(MEMORY_FILE):
        return 0
    with open(MEMORY_FILE, encoding="utf-8") as f:
        n = sum(1 for ln in f if ln.strip())
    os.remove(MEMORY_FILE)
    return n


WORD = re.compile(r"[a-z]{4,}")


def relevant_lessons(lessons, text, n=MAX_LESSONS, include_test=False):
    """The n lessons sharing the most words with the current gap; newest first on a tie. Test lessons (from a
    J2_FORCE_AUDIT_FAIL run) are left out unless include_test (J2_MEMORY_TEST_LESSONS=1, demo runs only).
    ponytail: word overlap, swap for embeddings if the lesson file grows past a few hundred lines."""
    want = set(WORD.findall(text.lower()))
    lessons = [x for x in lessons if include_test or not x.get("test")]
    scored = [(len(want & set(WORD.findall(" ".join(str(x.get(k, "")) for k in ("problem", "cause", "fix")).lower()))),
               i, x) for i, x in enumerate(lessons)]
    return [x for sc, i, x in sorted(scored, key=lambda t: (-t[0], -t[1])) if sc > 0][:n]


# ---- behind-the-scenes view: one lane per agent, live or from a saved run
FUNCTIONS = ("identity", "adaptation", "priority", "coordination", "audit", "validator")


def lanes(chat, workflows, thinking, turn, status, paused, step, write_lock):
    """Each agent's status (working / waiting / blocked / idle) and what it is on, worked out by code from the run."""
    ids = list(FUNCTIONS) + [w["id"] for w in workflows]
    last = {}
    for i, m in enumerate(chat):
        if m["who"] in ids:
            last[m["who"]] = i
    live = status == "running" or bool(paused)
    out = []
    for fn in ids:
        w = next((x for x in workflows if x["id"] == fn), None)
        i = last.get(fn)
        m = chat[i] if i is not None else None
        lane = {"id": fn, "name": NAMES.get(fn, f"{fn} Builder" if is_wf_agent(fn) else fn), "status": "idle",
                "doing": (m["text"][:140] if m else ("code: checks and registers workflows" if fn == "validator" else "")),
                "last_msg": m["id"] if m else None}
        nxt = m.get("next") if m else None
        answered = nxt and any(x["who"] == nxt for x in chat[i + 1:])
        if live and (thinking == fn or (turn == fn and status == "running")):
            lane.update(status="working", doing=(f"writing section {w['section']}: {w['name']}" if w else STEPS.get(step, "")))
        elif w and w["status"] in ("held", "unfunded", "failed"):
            lane.update(status="blocked", doing=f"{w['status']}: {w.get('last_check') or w['name']}")
        elif fn == "identity" and paused:
            lane.update(status="waiting", on="Requester", doing=PAUSES.get(paused["kind"], ""))
        elif live and nxt and nxt not in (fn, "user") and not answered:
            lane.update(status="waiting", on=NAMES.get(nxt, nxt))
        tl = [x["lesson_used"] for x in chat if x["who"] == fn and x.get("lesson_test")]
        if tl:
            lane["test_lesson"] = tl[-1]
        if w:
            env = w.get("envelope") or {}
            lane["progress"] = {"workflow": w["name"], "section": w.get("section"), "workflow_status": w["status"],
                                "attempts": w.get("calls_used", 0), "attempt_limit": as_int(env.get("model_call_limit"), 1),
                                "retries": w.get("retries_used", 0), "retry_limit": as_int(env.get("retry_limit")),
                                "last_check": w.get("last_check"), "write_lock": write_lock == fn}
        out.append(lane)
    return out


SAVED = re.compile(r"j2-[\w-]+")


def saved_dir(name):
    """A saved run's folder, or None. Only names like j2-20261007-101500 inside RUNS_DIR (no path tricks)."""
    if not SAVED.fullmatch(str(name or "")):
        return None
    d = os.path.join(RUNS_DIR, name)
    return d if os.path.isdir(d) else None


def _read(d, name, default=None):
    try:
        with open(os.path.join(d, name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _jsonl(d, name):
    out = []
    try:
        with open(os.path.join(d, name), encoding="utf-8") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def list_runs(limit=60):
    out = []
    for name in sorted(os.listdir(RUNS_DIR), reverse=True) if os.path.isdir(RUNS_DIR) else []:
        d = saved_dir(name)
        if not d or not os.path.exists(os.path.join(d, "chat.jsonl")):
            continue
        s = _read(d, "summary.json", {})
        first = next((m for m in _jsonl(d, "chat.jsonl") if m.get("who") == "user"), {})
        out.append({"id": name, "status": s.get("status") or "unfinished", "brief": (s.get("brief") or first.get("text")
                                                                                   or "")[:120]})
        if len(out) >= limit:
            break
    return out


def saved_snapshot(name, since=0):
    """The page's state for a saved run, read from its folder (read-only)."""
    d = saved_dir(name)
    if not d:
        return None
    rows = _jsonl(d, "chat.jsonl")
    head = rows[0] if rows and rows[0].get("meta") else {}
    chat = [m for m in rows if not m.get("meta")]
    s, wfs = _read(d, "summary.json", {}), _read(d, "workflows.json", [])
    sections = _read(d, "sections.json", {})
    audits = _read(d, "audits.json", [])
    site = os.path.join(d, "site")
    versions = len([f for f in os.listdir(site) if re.fullmatch(r"v\d+\.html", f)]) if os.path.isdir(site) else 0
    calls = [{k: v for k, v in c.items() if k not in ("system", "prompt", "raw")} for c in _jsonl(d, "calls.jsonl")]
    b = s.get("budget") or {}
    return {"saved": name, "chat": chat[since:], "total": len(chat), "status": "saved", "thinking": None, "step": 8,
            "steps": STEPS, "goal": _read(d, "goal.json"), "stamped": True, "workflows": wfs,
            "budget": b.get("granted") or BUDGET, "spent": b.get("used") or 0, "conflicts": _read(d, "conflicts.json", []),
            "audits": audits, "versions": versions, "cycle": s.get("cycles") or 0, "calls": s.get("ai_calls") or len(calls),
            "error": None, "done": True, "turn": None, "cycle_turns": 0, "max_turns": MAX_TURNS, "paused": None,
            "mock": head.get("mock"), "model": head.get("model"), "fixes": head.get("j2_fixes", 0), "placeholders": [],
            "force_audit_fail": head.get("force_audit_fail"), "test_lessons": bool(head.get("test_lessons")),
            "report": _read(d, "report.json"), "outcome": s.get("outcome"),
            "sections": [{"id": k, "owner": x["owner"], "workflow": x.get("workflow"),
                          "bytes": len((x["head"] + x["body"]).encode("utf-8"))} for k, x in sections.items()],
            "write_lock": None, "agents": {w["id"]: w.get("agent") or f"{w['id']} Builder" for w in wfs},
            "lanes": lanes(chat, wfs, None, None, "saved", None, 8, None), "call_log": calls,
            "workable": s.get("workable") if s else (workable(audits[-1]) if audits else None),
            "memory": False, "lessons": [], "lessons_used": (s.get("lessons") or {}).get("used", []),
            "lessons_saved": (s.get("lessons") or {}).get("saved", [])}


def call_record(d, cid):
    """One AI call in full (system prompt, prompt, raw reply) from a run folder's calls.jsonl."""
    return next((c for c in _jsonl(d, "calls.jsonl") if c.get("id") == cid), None) if d else None


class J2Run:
    def __init__(self):
        self.lock = threading.Lock()
        self.reset()

    # ------------------------------------------------------------------ state
    def reset(self):
        self.run_id = time.strftime("%Y%m%d-%H%M%S")
        self.dir = os.path.join(RUNS_DIR, "j2-" + self.run_id)
        n = 2
        while os.path.exists(self.dir):          # two runs started in the same second get separate folders
            self.dir = os.path.join(RUNS_DIR, f"j2-{self.run_id}-{n}")
            n += 1
        self.chat, self.workflows, self.conflicts, self.audits, self.sites = [], [], [], [], []
        self.goal, self.stamped, self.request = None, False, ""
        self.spent, self.cycle, self.calls, self.step = 0, 0, 0, 0
        self.budget, self.raises = BUDGET, []
        self.idle_cycles, self.cycle_registered = 0, True
        self.status, self.thinking, self.error, self.done = "idle", None, None, False
        self.feedback = None
        self.turn, self.handoff, self.outcome = None, {}, None
        self.paused = None          # {"kind", "questions", "to", "handoff", "msg"} while the run waits on the Requester
        self.intake, self.decisions = [], []   # J2.a question rounds; every Requester answer to Identity
        self.drop_answer, self.relay, self.a_msg = None, None, None
        self.fixes = os.getenv("J2_FIXES", "0") == "1"   # read per run, so one process can test both modes
        # Test switch, off unless set: in cycle 1, Audit's result for this done-when item is forced to NEEDS_REVISION
        self.force_fail = as_int(os.getenv("J2_FORCE_AUDIT_FAIL"), 0) if os.getenv("J2_FORCE_AUDIT_FAIL") else 0
        self.forced = False
        self.test_lessons = os.getenv("J2_MEMORY_TEST_LESSONS") == "1"   # demo only: J2.b may read test lessons
        self.p_refused = {}         # workflow name -> why: what Priority refused in the current negotiation
        self.rejections = []        # every validator rejection, with its exact reason
        self.events, self.agent_turns, self.report, self.started = [], {}, None, None   # for the run report
        load_rates()
        self.cycle_limit = self.cycle_turns = 0
        self.summary, self.summary_upto = "", 0
        self.sections, self.write_lock, self.bargain = {}, None, None   # section id -> {owner, head, body, workflow}
        self.memory = memory_on()
        self.call_log, self.pending_calls = [], {}     # every AI call (calls.jsonl); calls not yet shown in a message
        self.lessons_used, self.lessons_saved = [], []
        self.fail_floor = 0          # audits before this index don't count for "same failure twice in a row"
        self._begin_cycle(advance=False)

    def _begin_cycle(self, advance=True):
        if advance:
            self.cycle += 1
        self.cycle_turns = self.exchanges = self.hold_bounces = 0
        self.conflict = None                 # the Adaptation <-> Priority negotiation in progress, once they disagree
        self.a_pos, self.p_pos = [], []      # Adaptation's and Priority's latest positions this cycle

    def snapshot(self, since=0):
        return {"chat": self.chat[since:], "total": len(self.chat), "status": self.status,
                "thinking": self.thinking, "step": self.step, "steps": STEPS, "goal": self.goal,
                "stamped": self.stamped, "workflows": self.workflows, "budget": self.budget, "spent": self.spent,
                "conflicts": self.conflicts, "audits": self.audits, "versions": len(self.sites),
                "cycle": self.cycle, "calls": self.calls, "error": self.error, "done": self.done,
                "turn": self.turn, "cycle_turns": self.cycle_turns, "max_turns": MAX_TURNS,
                "paused": ({k: self.paused[k] for k in ("kind", "questions", "msg")}
                           | {"label": PAUSES.get(self.paused["kind"], "")}) if self.paused else None,
                "mock": llm.MOCK, "model": None if llm.MOCK else llm.MODEL, "fixes": int(self.fixes),
                "force_audit_fail": self.force_fail or None, "test_lessons": self.test_lessons,
                "placeholders": self._placeholders(), "report": self.report,
                "sections": [{"id": k, "owner": x["owner"], "workflow": x.get("workflow"),
                              "bytes": len((x["head"] + x["body"]).encode("utf-8"))} for k, x in self.sections.items()],
                "write_lock": self.write_lock, "agents": {w["id"]: NAMES.get(w["id"]) for w in self.workflows},
                "lanes": lanes(self.chat, self.workflows, self.thinking, self.turn, self.status, self.paused, self.step,
                               self.write_lock),
                "call_log": self.call_log,
                "workable": workable(self.audits[-1]) if self.audits else None,
                "memory": self.memory, "lessons": load_lessons() if self.memory else [],
                "lessons_used": self.lessons_used, "lessons_saved": [x["id"] for x in self.lessons_saved]}

    def _placeholders(self):
        out = []
        for fn in ("team", "builder", "identity", "adaptation", "priority", "coordination", "audit"):   # builder.md: workflow agents
            p = os.path.join(J2_DIR, f"{fn}.md")
            if os.path.exists(p) and "PLACEHOLDER" in open(p, encoding="utf-8").read(300):
                out.append(fn)
        return out

    def _event(self, agent, kind, detail, **extra):
        """Something the run report counts: redirects, invalid moves, refusals, holds, limits, pauses, conflicts."""
        self.events.append({"agent": agent, "type": kind, "detail": detail, "msg": len(self.chat) + 1,
                            "cycle": self.cycle, **extra})

    def _raise_budget(self, add, why):
        """Only after the Requester approved more budget in answer to Identity's question; capped at BUDGET_CAP."""
        if add <= 0:
            return
        new = min(self.budget + add, BUDGET_CAP)
        if new <= self.budget:
            self.post("system", f"The Requester approved +{add}, but the budget is already at the cap ({BUDGET_CAP}). "
                                "No change.")
            return
        old, self.budget = self.budget, new
        self.raises.append({"cycle": self.cycle, "asked": add, "from": old, "to": new, "why": why})
        self._event("identity", "budget_raise", f"{old} -> {new} (asked +{add}, cap {BUDGET_CAP}; {why})")
        self.post("system", f"Budget raised on the Requester's approval: {old} -> {new}"
                  + (f" (asked +{add}; capped at {BUDGET_CAP})" if old + add > new else "")
                  + f". Remaining: {self.budget - self.spent}.")

    def post(self, who, text, **meta):
        m = {"id": len(self.chat) + 1, "t": time.strftime("%H:%M:%S"), "who": who, "text": text, "step": self.step, **meta}
        if self.pending_calls.get(who):          # the AI calls behind this message, for the detail view
            m["calls"] = self.pending_calls.pop(who)
        if meta.get("warning"):
            self.events.append({"agent": "system", "type": "warning", "detail": text, "msg": m["id"], "cycle": self.cycle})
        self.chat.append(m)
        os.makedirs(self.dir, exist_ok=True)
        with open(os.path.join(self.dir, "chat.jsonl"), "a", encoding="utf-8") as f:
            if m["id"] == 1:   # first line of the file: which mode and model produced this run
                f.write(json.dumps({"meta": True, "run": self.run_id, "j2_fixes": int(self.fixes),
                                    "force_audit_fail": self.force_fail or None,
                                    "test_lessons": self.test_lessons or None,
                                    "provider": None if llm.MOCK else llm.PROVIDER, "model": None if llm.MOCK else llm.MODEL,
                                    "mock": llm.MOCK}) + "\n")
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
        return m

    def save(self, name, data):
        os.makedirs(self.dir, exist_ok=True)
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    COST_KEYS = ("cost", "estimate", "envelope", "charged", "calls_used", "retries_used")

    def state(self, fn=None):
        """Structured state every agent gets on every call. Identity decides purpose, not resources, so its view
        leaves out the budget, the rate card and workflow costs (resources are Adaptation's and Priority's)."""
        blind = fn == "identity"
        conflicts = [{k: c.get(k) for k in ("id", "cycle", "topic", "between", "subject", "status", "resolved_by",
                                            "outcome")} for c in self.conflicts]
        audits = [{"cycle": a["cycle"], "version": a["version"], "all_pass": a["all_pass"],
                   "results": [{k: r.get(k) for k in ("id", "criterion", "verdict", "severity", "note")} for r in a["results"]]}
                  for a in self.audits]
        return json.dumps({"requester_brief": self.request, "requester_feedback": self.feedback, "charter": self.goal,
                           "requester_decisions": self.decisions,
                           "budget": None if blind else {"total": self.budget, "spent": self.spent,
                                                         "remaining": self.budget - self.spent},
                           "cycle": self.cycle, "negotiation": {"exchanges_used": self.exchanges,
                                                                "max_exchanges": MAX_ATTEMPTS},
                           "workflows": [{k: v for k, v in w.items() if k not in self.COST_KEYS} for w in self.workflows]
                           if blind else self.workflows, "conflicts": conflicts, "audits": audits,
                           "site_versions": len(self.sites),
                           "site_sections": [{"section": k, "owner": x["owner"], "workflow": x.get("workflow")}
                                             for k, x in self.sections.items()],
                           "rate_card": ({"prices": RATES, "rule": "a workflow costs the sum of its parts' prices; "
                                          "estimated_resources.money is ignored; list a part once per unit"}
                                         if RATES and not blind else None)}, ensure_ascii=False)

    def chat_view(self):
        """Whole chat while it's short; otherwise a running summary of the older part plus the recent messages."""
        full = "\n".join(line(m) for m in self.chat)
        if len(full) <= CHAT_FULL_CHARS:
            return full
        older = self.chat[:-CHAT_TAIL]
        if not older:
            return full
        if not self.summary or len(older) - self.summary_upto >= SUMMARY_REFRESH:
            self._summarize(older)
        recent = self.chat[self.summary_upto:]
        return (f"(Long chat: messages 1-{self.summary_upto} are summarised, the last {len(recent)} are in full.)\n"
                f"SUMMARY OF EARLIER MESSAGES:\n{self.summary}\n\nRECENT MESSAGES:\n"
                + "\n".join(line(m) for m in recent))

    def _summarize(self, older):
        if self.calls and DELAY:
            time.sleep(DELAY)
        self.calls += 1
        new = older[self.summary_upto:]
        self.summary = llm.ask(
            "You keep a running summary of a team's group chat. Write at most 12 short bullets: decisions, workflows "
            "agreed or refused, conflicts and how they were settled, audit results, open issues. Facts only.",
            f"PREVIOUS SUMMARY:\n{self.summary or '(none)'}\n\nNEW MESSAGES:\n" + "\n".join(line(m) for m in new),
            lambda: f"- Messages 1-{len(older)}: charter recorded, workflows negotiated, built and audited (mock summary).",
            max_tokens=600, effort="low").strip()
        self.summary_upto = len(older)
        os.makedirs(self.dir, exist_ok=True)
        with open(os.path.join(self.dir, "summary.txt"), "w", encoding="utf-8") as f:
            f.write(f"Messages 1-{self.summary_upto}\n{self.summary}\n")

    def context(self, fn=None):
        return f"STATE:\n{self.state(fn)}\n\nCHAT:\n{self.chat_view()}"

    REASON = '"reason": str (one short sentence: why you decided this)'
    MOCK_REASON = "Scripted mock reply: no model reasoning."

    def call(self, fn, reply_format, task, mock, max_tokens=900, json_reply=True):
        """One agent's AI call. Every JSON reply format gets a "reason" field. Each call is logged to calls.jsonl
        (inputs, reply, reason, tokens, time) and linked to the agent's next chat message for the detail view."""
        if json_reply and reply_format.rstrip().endswith("}") and '"reason"' not in reply_format:
            reply_format = reply_format.rstrip()[:-1] + ", " + self.REASON + "}"
        user = f"{self.context(fn)}\n\nYOUR TURN:\n{task}"
        system = system_prompt(fn, reply_format)
        if self.calls and DELAY:
            time.sleep(DELAY)
        self.calls += 1
        self.thinking = fn
        t0 = time.time()
        try:
            raw = llm.ask(system, user, mock, max_tokens=max_tokens, effort="low" if json_reply else "high",
                          json_mode=json_reply)
        finally:
            self.thinking = None
        reply = raw
        if json_reply:
            try:
                reply = llm.extract_json(raw)
            except ValueError:
                reply = {"say": raw[:400]}
            if llm.MOCK and not reply.get("reason"):
                reply["reason"] = self.MOCK_REASON
        self._log_call(fn, task, system, user, raw, reply if json_reply else None, time.time() - t0)
        return reply

    def _inputs(self, fn, task):
        """What the agent read, summarised by code: [label, text] pairs. The full prompt is in calls.jsonl."""
        g, out = self.goal or {}, []
        if g:
            out.append(["charter", f"{g.get('site_name') or 'site'}: {len(g.get('done_when') or [])} done-when items"
                        + (f", {len(g['to_be_confirmed'])} to be confirmed" if g.get("to_be_confirmed") else "")])
        if fn != "identity":
            out.append(["ledger", f"budget {self.spent}/{self.budget} used, {self.budget - self.spent} left"
                        + (f"; rate card on ({len(RATES)} parts)" if RATES else "")])
        if self.workflows:
            out.append(["workflows", f"{len(self.workflows)} registered: "
                        + ", ".join(f"{w['id']} {w['status']}" for w in self.workflows)])
        if self.audits:
            a = self.audits[-1]
            out.append(["findings", f"audit of v{a['version']}: {sum(r['pass'] for r in a['results'])}/{len(a['results'])} "
                        "pass" + "".join(f"; {r['id']} {r['verdict']}" for r in a["results"] if not r["pass"])])
        for label, mark in (("proposal", "ON THE TABLE:"), ("offer", "PRIORITY OFFERS:"), ("proposal", "RUN THIS WORKFLOW"),
                            ("findings", "AUDIT'S FINDINGS"), ("lessons", "LESSONS FROM EARLIER WORK"),
                            ("workflow", "YOUR WORKFLOW:"), ("conflict", "CONFLICT "), ("dispute", "DISAGREEMENT ")):
            i = task.find(mark)
            if i >= 0:
                out.append([label, task[i:i + 240].split("\n")[0] + ("…" if len(task) > i + 240 else "")])
        out.append(["chat", f"{len(self.chat)} messages" + (f" (1-{self.summary_upto} summarised)" if self.summary else "")])
        out.append(["task", task[:280] + ("…" if len(task) > 280 else "")])
        return out

    def _log_call(self, fn, task, system, user, raw, reply, secs):
        meta = dict(llm.LAST_META)
        rec = {"id": self.calls, "fn": fn, "step": self.step, "cycle": self.cycle, "t": time.strftime("%H:%M:%S"),
               "seconds": round(secs, 2), "model": None if llm.MOCK else meta.get("model") or llm.MODEL,
               "tokens": ({"input": meta.get("input_tokens"), "output": meta.get("output_tokens")}
                          if meta.get("input_tokens") or meta.get("output_tokens") else None),
               "chars": {"prompt": len(system) + len(user), "reply": len(raw)},
               "inputs": self._inputs(fn, task),
               "reply": {k: v for k, v in reply.items() if k != "reason"} if isinstance(reply, dict) else None,
               "reason": reply.get("reason") if isinstance(reply, dict) else None}
        self.call_log.append(rec)
        self.pending_calls.setdefault(fn, []).append(rec["id"])
        os.makedirs(self.dir, exist_ok=True)
        with open(os.path.join(self.dir, "calls.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps({**rec, "system": system, "prompt": user, "raw": raw}, ensure_ascii=False) + "\n")
        return rec

    # ------------------------------------------------------------------ routing
    def _pick(self, frm, wanted, allowed, fallback, why=""):
        """Return (next agent, redirect note or None). Only J2 routes are ever allowed."""
        assert all(a in ROUTES[frm] for a in allowed) and fallback in allowed, (frm, allowed, fallback)
        want = key(wanted)
        if want in allowed:
            return want, None
        if want == "user" and frm != "identity":
            # Only Identity talks to the Requester: _say sends this message to Identity first (see _run).
            self.relay = self.relay or {"from": frm}
            self._event(frm, "redirect", "addressed the Requester, routed to Identity")
            return fallback, (f"Route check: {NAMES[frm]} addressed the Requester. Only Identity talks to the "
                              "Requester, so the message goes to Identity first.")
        label = NAMES.get(want, str(wanted)) if wanted else "no one"
        self._event(frm, "redirect", f"picked {label}, routed to {NAMES[fallback]}" + (f" ({why})" if why else ""))
        return fallback, (f"Route check: {NAMES[frm]} picked {label} to speak next, which isn't an allowed J2 route "
                          f"here{' (' + why + ')' if why else ''}. Passing to {NAMES[fallback]}.")

    def _say(self, who, text, nxt=None, note=None, **meta):
        text = text or ""
        if who in ROUTES and who != "identity" and (self.relay or TO_USER.search(text)):
            if not self.relay:
                self._event(who, "redirect", "addressed the Requester in the message, routed to Identity")
                note = (f"Route check: {NAMES[who]} addressed the Requester. Only Identity talks to the Requester, so "
                        "the message goes to Identity first.")
            self.relay = {"from": who, "text": text}
            nxt = "identity"
        m = self.post(who, address(text, nxt) if nxt else text, **({"next": nxt} if nxt else {}), **meta)
        if note:
            if not note.startswith("Route check"):
                self._event(who, "invalid_move", note)
            self.post("system", note, redirect=True)
        return m

    def _handoff(self, to, **h):
        self.turn, self.handoff = to, h

    def _wf(self, wid):
        return next((w for w in self.workflows if w["id"] == wid), None)

    def _conflict(self, cid):
        return next(c for c in self.conflicts if c["id"] == cid)

    def _save_conflicts(self):
        self.save("conflicts.json", self.conflicts)

    def _ask_user(self, say, questions, kind, to="identity", handoff=None, **meta):
        """Identity asks the Requester and the run pauses. The reply resumes the run at `to` with `handoff`."""
        say = re.sub(r"^@\w+[,:]?\s*", "", str(say or "")).strip()
        if kind in ("approval", "ruling_budget"):   # these apply their own amount after the answer; don't apply twice
            questions = [{k: v for k, v in q.items() if k != "budget"} for q in questions]
        m = self.post("identity", "@Requester " + say + ("\n" + numbered(questions) if questions else ""),
                      act="ASK_REQUESTER", to_user=True, next="user", **meta)
        self.paused = {"kind": kind, "questions": questions, "to": to, "handoff": handoff or {}, "msg": m["id"]}
        self._event("identity", "pause", f"{kind}: {len(questions)} question(s) for the Requester", pause=kind)
        self.outcome = f"Paused: Identity is waiting on the Requester ({PAUSES[kind]})."
        self.turn = None

    # ------------------------------------------------------------------ entry
    def user_says(self, text):
        with self.lock:
            if self.status == "running":
                return False
            self.post("user", text, **({"change": True} if self.done and not self.paused else {}))
            if self.done:
                self.done = False
                if not self.paused:          # an answer to Identity's questions is not a change request
                    self.feedback = text
            self.status = "running"
            threading.Thread(target=self._run_safe, daemon=True).start()
            return True

    def _run_safe(self):
        with self.lock:
            try:
                self._run()
            except Exception as e:  # noqa: BLE001
                self.error = f"{type(e).__name__}: {str(e)[:300]}"
                self.post("system", f"Stopped: {self.error}")
                self.outcome = f"Crashed: {self.error}"
                try:
                    self._make_report()
                    self._write_summary()
                except Exception as e2:  # noqa: BLE001
                    self.post("system", f"Run report failed: {type(e2).__name__}: {str(e2)[:200]}")
                self.turn = None
                self.status = "waiting"

    def _run(self):
        last_user = next(m["text"] for m in reversed(self.chat) if m["who"] == "user")
        self.started = self.started or time.time()
        self.outcome, p = None, self.paused
        if p:
            # The Requester answered Identity: resume where the run stopped. Answers don't renew the cycle allowance.
            self.paused = None
            d = {"kind": p["kind"], "asked": [q["question"] for q in p["questions"]], "answer": last_user}
            self.decisions.append(d)
            # ponytail: one budget question per pause is mapped; Identity asks one decision question at a time
            bq = next((q for q in p["questions"] if q.get("budget")), None)
            if bq:
                i = option_picked(bq, last_user)
                if i is None and not p.get("reasked"):
                    # Don't guess which option changes the budget: Identity asks once more.
                    d["unclear"] = True
                    self._event("identity", "unclear_answer", f"answer to '{bq['question']}' names no single option")
                    self._ask_user("I couldn't tell which option you chose, and one of them changes the budget. "
                                   "Please reply with the option number.", [bq], p["kind"], to=p["to"],
                                   handoff=p["handoff"], auto=True)
                    self.paused["reasked"] = True
                elif i is None:
                    self.post("system", "The answer still doesn't name one option, so no budget change was applied.")
                else:
                    d["option"], d["budget_added"] = i + 1, bq["budget"][i]
                    self._raise_budget(bq["budget"][i], f"the Requester chose option {i + 1}: {bq['options'][i]}")
        if self.paused:
            pass                                        # re-asked above; the run waits again
        elif p:
            h = dict(p["handoff"])
            if h.get("why"):
                h["why"] += f" The Requester answered: {last_user}"
            self._handoff(p["to"], **h, answer=last_user, asked=p["questions"])
        else:
            if not self.goal:
                self.request = last_user
                self._handoff("identity", kind="intake")
            elif self.fixes:   # fix (b): a change request is checked at J2.a before Adaptation works on it
                self._handoff("identity", kind="intake", change=self.feedback, mark=len(self.intake))
            else:
                self._handoff("adaptation", kind="propose", new_cycle=True,
                              why=f"The Requester asked for a change: {self.feedback}")
            self.cycle_limit = self.cycle + MAX_CYCLES   # a new brief or change request gets a fresh allowance
        self.idle_cycles, self.cycle_registered = 0, True                    # a new message is new information
        while self.turn:
            # Safety limits never stop the run silently: Identity asks the Requester what to do (_identity_limit).
            if self.handoff.get("new_cycle"):
                self.idle_cycles = 0 if self.cycle_registered else self.idle_cycles + 1
                self.cycle_registered = False
                cheapest = min(RATES.values()) if RATES else 1
                limit = None
                if self.idle_cycles >= 2:
                    self._event("system", "stuck", f"cycles {self.cycle - 1} and {self.cycle} registered nothing")
                    limit = (f"Cycles {self.cycle - 1} and {self.cycle} both registered nothing, so another cycle would "
                             "repeat the same blocker.")
                elif self.cycle >= self.cycle_limit:
                    limit = f"The department used its {MAX_CYCLES} cycles (J2_MAX_CYCLES) and the site isn't workable yet."
                elif self.goal and self.budget - self.spent < cheapest:
                    self._event("system", "out_of_budget", f"{self.budget - self.spent} left, cheapest part {cheapest}")
                    limit = (f"Out of budget: {self.budget - self.spent} of {self.budget} units left, less than the "
                             f"cheapest rate-card part ({cheapest}), so no new workflow can be funded.")
                if limit:
                    self.idle_cycles, self.cycle_registered = 0, True
                    self._handoff("identity", kind="limit", reason=limit, out_of_budget=limit.startswith("Out of budget"))
                    continue
                self._begin_cycle()
            if self.cycle_turns >= MAX_TURNS and self.handoff.get("kind") != "limit":
                self._handoff("identity", kind="limit", reason=f"Cycle {self.cycle} used {MAX_TURNS} turns (the "
                                                               "per-cycle cap) without finishing.")
                continue
            self.cycle_turns += 1
            self.agent_turns[self.turn] = self.agent_turns.get(self.turn, 0) + 1
            if is_wf_agent(self.turn):
                self._turn_workflow_agent(self.handoff)
            else:
                getattr(self, "_turn_" + self.turn)(self.handoff)
            if self.relay:
                # An agent addressed the Requester: Identity takes it first, then the flow resumes where it was going.
                r, self.relay = self.relay, None
                if self.turn != "identity":
                    resume = {"to": self.turn, "handoff": self.handoff} if self.turn else None
                    self._handoff("identity", kind="question", frm=r["from"], question=r.get("text") or "", resume=resume)
        self.turn, self.done = None, True
        if not self.paused:
            self.step = 8
        self.post("system", (self.outcome or "Stopped.") + f" Site v{len(self.sites)} is in the preview. "
                  + ("Answer Identity's question above to continue." if self.paused else
                     "Tell us if you want changes."))
        self._make_report(review=not self.paused)
        if not self.paused:
            self._write_summary()
        self.feedback = None
        self.status = "waiting"

    # ------------------------------------------------------------------ Identity
    def _turn_identity(self, h):
        return {"intake": self._identity_intake, "resolve": self._identity_resolve, "approval": self._identity_approval,
                "audit": self._identity_audit, "requester_answered": self._identity_hears_requester,
                "ruling_budget": self._identity_ruling_budget, "limit": self._identity_limit,
                }.get(h.get("kind"), self._identity_question)(h)

    CHARTER_FMT = ('{"statement": str, "site_name": str, "audience": str, "standards": [str], "rules": [str], '
                   '"done_when": [str], "to_be_confirmed": [{"item": int (done-when item number), "fact": str}], '
                   '"dropped_from_brief": [str]}')

    def _identity_intake(self, h):
        """J2.a: is there enough information to work? If not, Identity asks the Requester and the run waits; the
        answer comes back here. There is no round cap: Identity asks until it has enough to write the charter.
        A fact the Requester can't supply yet is recorded as to be confirmed; its done-when item is not met."""
        self.step = 1
        feedback = h.get("feedback") or ""
        if h.get("drop"):
            self.drop_answer = h.get("answer")
            feedback = (f"The Requester answered about the brief items the charter left out: {self.drop_answer}. Put "
                        "back what they want kept; list in dropped_from_brief only what they agreed to drop.")
        elif h.get("answer"):
            self.intake.append({"asked": [q["question"] for q in h.get("asked") or []], "answer": h["answer"]})
        change, mark = h.get("change"), h.get("mark", 0)      # J2_FIXES=1: a change request after done
        last = bool(h.get("force"))      # only after a reply with neither questions nor a charter
        if change:
            feedback += (f"\nTHE REQUESTER ASKED FOR A CHANGE AFTER THE GOAL WAS REACHED: {change}\nJ2.a for the change: "
                         "is there enough information to make it? If not, ask. If yes, return the updated charter: keep "
                         "everything already in it and add or adjust done-when items so the change is checkable. "
                         f"CURRENT CHARTER: {json.dumps(self.goal, ensure_ascii=False)}")

        def mock():
            if change:
                return json.dumps({"say": "@Adaptation Charter updated for the change request.", "enough": True,
                                   "next": "Adaptation", "goal": {**self.goal, "done_when": list(self.goal["done_when"])
                                                                  + [f"Change: {change}"]}})
            text = " ".join([self.request] + [x["answer"] for x in self.intake])
            if not self.intake and len(self.request.split()) < 25 and not last:
                return json.dumps({"say": "Before we start I need a few facts the brief doesn't give. I won't guess "
                                          "them.", "enough": False, "next": "Requester", "questions": [
                    {"question": "What is the business called, and where is it?", "options": []},
                    {"question": "What must visitors be able to see or do on the site?", "options": []},
                    {"question": "How should it feel, and must it work well on phones?", "options": []}]})
            return json.dumps({"say": "@Adaptation Charter recorded from the brief"
                                      + (" and the Requester's answers." if self.intake else "; it had enough to work."),
                               "enough": True, "next": "Adaptation", "goal": mock_charter(text)})
        r = self.call("identity", '{"say": str, "enough": bool, "questions": [{"question": str, "options": [str] '
                      '(0-4)}] (when enough is false), "goal": ' + self.CHARTER_FMT + '|null (when enough is true), '
                      + next_field(("user", "adaptation"), "Requester when you ask; Adaptation once the charter is "
                                   "recorded") + "}",
                      f"REQUESTER'S BRIEF: {self.request}\nEARLIER QUESTIONS AND ANSWERS: {json.dumps(self.intake)}\n"
                      f"{feedback}\nJ2.a: is there enough information to work? You need enough to write the charter: "
                      "goal, audience, standards, rules and a checkable done-when list. Never invent a missing fact.\n"
                      "- Not enough: set enough=false and ask the Requester 1-4 specific questions about what the brief "
                      "leaves open (what the site is for, who it serves, what visitors must be able to see or do, hard "
                      "rules). Offer options only for a choice between known alternatives. Don't ask about cost.\n"
                      "- Enough: set enough=true and record the charter from the brief and the Requester's answers only. "
                      "Every done-when item must be checkable by reading the site file itself. Content facts only the "
                      "Requester knows (phone numbers, prices, addresses) are questions for the Requester: ask for them. "
                      "Only if the Requester has said they can't supply a fact yet, record it in to_be_confirmed with the "
                      "number of the done-when item it blocks: that item is not met until they confirm it. Done-when "
                      "may not refer to the Requester, Audit, verification, approval or launch. Keep everything the brief "
                      "asks for; if the charter leaves any of it out, list it in dropped_from_brief with the reason. "
                      "Don't plan costs or resources."
                      + ("\nRecord the charter now (enough=true) from what you have." if last else ""), mock)
        qs = clean_questions(r.get("questions"))
        if not r.get("enough") and not last and qs:
            return self._ask_user(r.get("say", ""), qs, "info", handoff={"kind": "intake", "change": change, "mark": mark})
        goal = r.get("goal") if isinstance(r.get("goal"), dict) else None
        if not goal:
            self._event("identity", "invalid_move", "J2.a reply had neither questions nor a charter")
            if not last:
                self.post("system", "Identity's reply had neither questions nor a charter. Asking it once more to "
                                    "record the charter.", redirect=True)
                return self._handoff("identity", kind="intake", force=True, change=change, mark=mark)
            self.outcome = "Stopped: Identity couldn't record a charter from the brief and the answers."
            self.turn = None
            return
        goal["to_be_confirmed"] = self._tbc(goal.get("to_be_confirmed"), goal.get("done_when") or [])
        goal.pop("open_inputs", None)
        self.goal = goal
        self.save("goal.json", self.goal)
        ok, why = self._stamp_check()
        dropped = [str(d) for d in self.goal.get("dropped_from_brief") or [] if str(d).strip()]
        if ok and dropped and not self.drop_answer:
            return self._ask_user("The charter leaves out these items from your brief: " + "; ".join(dropped)
                                  + ". Work starts after your answer.",
                                  [{"question": "Keep them in scope, or drop them?",
                                    "options": ["Keep them in scope", "Drop them"]}],
                                  "charter_drop", handoff={"kind": "intake", "force": True, "drop": True})
        nxt, note = self._pick("identity", r.get("next"), ("adaptation",), "adaptation",
                               "after the charter, Adaptation proposes")
        self._say("identity", r.get("say", ""), nxt, note, artifact="charter")
        start = dict(kind="propose", new_cycle=True, why=f"The Requester asked for a change: {change}. Identity checked it at "
                     "J2.a and updated the charter." if change else "The charter is recorded. Propose the first workflows.")
        if ok:
            self.stamped = True
            self._say("validator", f"Charter valid: statement present, {len(self.goal['done_when'])} checkable "
                                   "done-when items. Work can start."
                      + (f" Dropped with the Requester's agreement: {'; '.join(dropped)}." if dropped else ""),
                      "adaptation", stamp=True)
            return self._handoff("adaptation", **start)
        if h.get("attempt", 1) < 2:
            self._event("validator", "refused", f"charter: {why}")
            self._say("validator", f"Charter rejected: {why}.", "identity", stamp=False)
            return self._handoff("identity", kind="intake", force=True, attempt=2, change=change, mark=mark,
                                 feedback=f"The validator rejected the charter: {why}. Fix only that.")
        self.stamped = True
        self.post("system", "Charter accepted after two attempts; the validator's concern is on record.")
        self._handoff("adaptation", **start)

    @staticmethod
    def _tbc(raw, crit, keep=()):
        """To-be-confirmed facts keyed by the criterion text (item numbers shift when items are dropped)."""
        out = list(keep)
        for x in raw or []:
            if not isinstance(x, dict):
                continue
            n = as_int(x.get("item"))
            c = crit[n - 1] if 1 <= n <= len(crit) else str(x.get("criterion") or "")
            if c in crit and str(x.get("fact") or "").strip() and all(t["criterion"] != c for t in out):
                out.append({"criterion": c, "fact": str(x["fact"]).strip()})
        return out

    # Done-when must be checkable from the site itself. These words mark items that depend on someone's later
    # action or on the audit process.
    NOT_CHECKABLE = re.compile(r"\b(requester|audit\w*|launch\w*|go(?:es|ing)? live|verif\w*|approv\w*|sign(?:ed)?[- ]?off)\b",
                               re.I)

    def _stamp_check(self):
        g = self.goal or {}
        if not g.get("statement"):
            return False, "goal has no statement"
        if len(g.get("done_when") or []) < 3:
            return False, "fewer than 3 'done when' criteria"
        # Quoted text is a label the site shows (e.g. 'sample, replace before launch'), not a dependency.
        unquoted = lambda d: re.sub(r"'[^']*'|\"[^\"]*\"|‘[^’]*’|“[^”]*”", "", str(d))
        bad = [d for d in g["done_when"] if self.NOT_CHECKABLE.search(unquoted(d))]
        if bad:
            return False, ("these done-when items can't be checked by reading the site (they depend on the Requester, "
                           "Audit, verification, approval or launch); rephrase them as something the site shows, and "
                           "record a fact only the Requester can give in to_be_confirmed: " + json.dumps(bad))
        return True, "passes code checks"

    def _positions(self, c):
        """Each side's final position: for a proposal, its workflow list; otherwise its last attempt's position."""
        if c["topic"] == "proposal":
            return {"adaptation": c.get("adaptation_final") or [], "priority": c.get("priority_final") or []}
        last = {}
        for a in c["attempts"]:
            last[a["who"]] = a.get("position") or a["text"]
        return {w: last.get(w, "") for w in c["between"]}

    def _identity_resolve(self, h):
        """J2.d: rule on a conflict two agents couldn't settle, from the charter. If the charter doesn't decide it,
        ask the Requester one decision-ready question; the answer comes back here and Identity rules with it."""
        self.step = 4
        c = self._conflict(h.get("conflict"))
        a, b = c["between"]
        pos, answer, proposal = self._positions(c), h.get("answer"), c["topic"] == "proposal"
        if answer:
            c["user_answer"] = answer
        rulings = [a, b] + (["split"] if proposal else [])
        fmt = ('{"say": str, "clause": str, "facts": [str], "resolved": bool, "ruling": "' + '"|"'.join(rulings) + '" '
               '(whose final position stands), '
               + ('"workflows": [str] (for split: names of the workflows to register, taken as they are from either '
                  'final position), ' if proposal else '')
               + '"instruction": str (what happens next, one sentence)'
               + ('' if answer else ', "user_question": {"question": str, "options": [' + OPTION_FMT + '] (2-4, each '
                  'text with its consequence, cost and risk; no recommendation)}|null') + "}")
        attempts = "\n".join(f"  attempt {x['n']} {NAMES[x['who']]}: {x['text']}" for x in c["attempts"])
        task = (f"CONFLICT {c['id']} ({TOPICS[c['topic']]}) between {NAMES[a]} and {NAMES[b]}: {c['subject']}\n"
                f"{c.get('detail') or ''}\nTHEIR ATTEMPTS:\n{attempts}\n"
                f"{NAMES[a].upper()}'S FINAL POSITION: {json.dumps(pos[a], ensure_ascii=False)}\n"
                f"{NAMES[b].upper()}'S FINAL POSITION: {json.dumps(pos[b], ensure_ascii=False)}\n")
        if answer:
            task += (f"You asked the Requester: {json.dumps(c.get('user_question'))}\nTHE REQUESTER ANSWERED: {answer}\n"
                     "Rule now, following their answer (resolved=true). Don't rewrite either position.")
        else:
            task += ("J2.d: resolve it using the charter. Name the clause and separate facts from assumptions. If the "
                     "charter decides it, set resolved=true and rule. If it doesn't (purpose, risk, an outside commitment "
                     "or a value trade-off the charter leaves open), set resolved=false and put ONE decision-ready "
                     "question for the Requester in user_question. Don't rewrite either position.")

        def mock():
            names = [w["name"] for w in pos.get("priority") or []] if proposal else []
            extra = [w["name"] for w in pos.get("adaptation") or [] if w["name"] not in names] if proposal else []
            split = {"ruling": "split", "workflows": names + extra}
            beans = next((d for d in (self.goal or {}).get("done_when", []) if re.search(r"bean|farm", d, re.I)), None)
            if not proposal:
                return json.dumps({"say": f"Clause: done_when. {NAMES[b]}'s position stands.", "clause": "done_when",
                                   "resolved": True, "ruling": b, "instruction": "Carry on."})
            if answer:
                fund = re.search(r"\b1\b|fund|include", answer, re.I)
                return json.dumps({"say": "The Requester chose. " + ("The stories section is funded as Adaptation "
                                   "proposed; Priority's other cuts stand." if fund else "Priority's position stands: "
                                   "no stories section, the reserve stays."), "clause": "Requester's decision",
                                   "resolved": True, "instruction": "Register and build.",
                                   **(split if fund else {"ruling": "priority"})})
            if beans:
                return json.dumps({"say": f"Clause: done_when \"{beans}\". The stories cover that item, so they're in; "
                                          "Priority's cut to the animations stands.", "clause": f"done_when: {beans}",
                                   "facts": ["The charter names the beans and farms content"], "resolved": True,
                                   "instruction": "Register the split.", **split})
            return json.dumps({"say": "Clause: done_when has no stories item, and the standards don't settle whether "
                                      "warmth content is worth the fix reserve. The charter can't decide this, so I'm "
                                      "asking the Requester.", "clause": "done_when; standards", "resolved": False,
                               "ruling": None, "instruction": "", "user_question": {
                                   "question": "Fund a stories section, or keep the reserve for fixes?",
                                   "options": ["Fund the stories section (20 units): warmer page, but only 10 units "
                                               "stay for fixes after Audit",
                                               "No stories section: the page has only the charter's sections, and 30 "
                                               "units stay for fixes"]}})
        r = self.call("identity", fmt, task, mock)
        ruling = key(r.get("ruling"))
        c["identity"].append({"say": r.get("say"), "clause": r.get("clause"), "resolved": bool(r.get("resolved")),
                              "ruling": ruling or None, "after_user": bool(answer)})
        if r.get("resolved") and ruling in rulings:
            c["resolved_by"] = "identity_after_user" if answer else "identity"
            self._say("identity", r.get("say", ""), None, None, conflict=c["id"], decision=True)
            return self._apply(c, ruling, r)
        if not answer:
            q = clean_questions([r.get("user_question")]) if isinstance(r.get("user_question"), dict) else []
            if not q or len(q[0]["options"]) < 2:
                self._event("identity", "invalid_move", f"{c['id']}: no decision-ready question; code offered both "
                                                        "final positions")
                q = [{"question": f"{NAMES[a]} and {NAMES[b]} disagree about {c['subject']}, and the charter doesn't "
                                  "decide it. Which position should stand?",
                      "options": [f"{NAMES[a]}'s: {brief_list(pos[a])}", f"{NAMES[b]}'s: {brief_list(pos[b])}"]}]
            c["user_question"], c["escalated_to_user"] = q[0], True
            self._save_conflicts()
            return self._ask_user(r.get("say", ""), q, "conflict", handoff={"kind": "resolve", "conflict": c["id"]},
                                  conflict=c["id"])
        self._event("identity", "invalid_move", f"{c['id']}: no ruling after the Requester's answer")
        self.post("system", f"Identity didn't rule on {c['id']} after the Requester answered. The default for "
                            f"{TOPICS[c['topic']]} applies.", redirect=True)
        c["resolved_by"] = "default"
        self._apply(c, None, r)

    def _identity_question(self, h):
        """A question for Identity: a policy question from Adaptation, or a message another agent addressed to the
        Requester. Identity answers from the charter, or asks the Requester when only they can decide."""
        self.step = 4
        frm = h.get("frm") or "adaptation"
        resume = h.get("resume") or {"to": "adaptation", "handoff": {"kind": "propose", "why": "Identity answered."}}
        r = self.call("identity", '{"say": str (address @' + NAMES[frm] + '), "clause": str, "answer": str|null, '
                      '"user_question": {"question": str, "options": [' + OPTION_FMT + '] (0-4, no '
                      'recommendation)}|null}',
                      f"QUESTION FROM {NAMES[frm]}: {h.get('question')}\nAnswer it from the charter, naming the clause. "
                      "Only if the charter can't decide it and only the Requester can (a fact, an approval or a value "
                      "trade-off), put one decision-ready question in user_question instead.",
                      lambda: json.dumps({"say": f"@{NAMES[frm]} The charter's rules cover this; proceed inside them.",
                                          "clause": "rules", "answer": "Proceed inside the charter's rules.",
                                          "user_question": None}))
        q = clean_questions([r.get("user_question")]) if isinstance(r.get("user_question"), dict) else []
        if q:
            return self._ask_user(r.get("say", ""), q, "question", to=resume["to"], handoff=resume["handoff"])
        self._say("identity", r.get("say") or r.get("answer") or "", frm if frm in ROUTES["identity"] else None)
        h2 = dict(resume["handoff"])
        if h2.get("kind") == "propose":
            h2["why"] = f"{h2.get('why') or ''} Identity answered {NAMES[frm]}: {r.get('answer') or r.get('say')}"
        self._handoff(resume["to"], **h2)

    def _identity_approval(self, h):
        """Priority requested approval for a run over its envelope. Identity may not raise an envelope, so it denies
        from the charter or asks the Requester; a yes raises the budget (capped) and the envelope check runs again."""
        self.step = 6
        w, answer = self._wf(h.get("wid")), h.get("answer")
        need = max(0, w["cost"] - (self.budget - self.spent))
        if answer:
            r = self.call("identity", '{"say": str, "approved": bool, "budget_increase": int|null}',
                          f"YOU ASKED THE REQUESTER about running {w['id']} {w['name']} ({w['cost']} units, {need} more "
                          f"than is left). THE REQUESTER ANSWERED: {answer}\nRecord their decision. Add budget only if "
                          "they approved it.",
                          lambda: json.dumps({"say": "The Requester approved it.", "approved": True,
                                              "budget_increase": need}) if re.search(r"\b1\b|yes|approve", answer, re.I)
                          else json.dumps({"say": "The Requester declined; it stays parked.", "approved": False}))
            self._say("identity", r.get("say", ""), "priority" if r.get("approved") else "coordination")
            if r.get("approved"):
                self._raise_budget(as_int(r.get("budget_increase")) or need, f"{w['id']} over its envelope")
                return self._handoff("priority", kind="envelope", wid=w["id"])
        else:
            r = self.call("identity", '{"say": str, "clause": str, "decision": "DENY"|"ASK", "user_question": '
                          '{"question": str, "options": [str]}|null}',
                          f"Priority requests approval to run {w['id']} {w['name']} over its envelope: "
                          f"{'; '.join(h.get('over') or [])}. You may not raise an envelope or the budget yourself. DENY "
                          "if a charter clause decides it; otherwise ASK the Requester one decision-ready question.",
                          lambda: json.dumps({"say": "Adding budget is the Requester's call.", "clause": "authority",
                                              "decision": "ASK", "user_question": None}))
            if str(r.get("decision")).upper() == "ASK":
                q = clean_questions([r.get("user_question")]) if isinstance(r.get("user_question"), dict) else []
                if not q or len(q[0]["options"]) < 2:
                    q = [{"question": f"Run {w['name']} over the budget?",
                          "options": [f"Approve: add {need} units so it runs", "Don't run it; it stays parked"]}]
                return self._ask_user(r.get("say", ""), q, "approval", handoff={"kind": "approval", "wid": w["id"]})
            self._say("identity", r.get("say", ""), "coordination")
        w["status"] = "unfunded"
        self.save("workflows.json", self.workflows)
        self._handoff("coordination", kind="schedule")

    def _findings(self, audit=None):
        """Audit's full findings for Identity: every id, verdict, severity and text, done-when items and extra issues."""
        a = audit or (self.audits[-1] if self.audits else None)
        keys = ("id", "item", "criterion", "verdict", "severity", "confidence", "note", "needs_requester_fact")
        return [{k: r.get(k) for k in keys if r.get(k) is not None} for r in (a["results"] + a.get("extra_issues", [])
                                                                              if a else [])]

    def _identity_hears_requester(self, h):
        """The Requester answered Identity at J2.g/J2.h (a fact, a limit, or another question Identity asked).
        Facts they supply are recorded; facts they can't supply yet become to be confirmed (that item isn't met).
        After a limit question: keep working, drop the failing items, or ship as is."""
        self.step = 8
        limit, choices, answer = h.get("limit"), h.get("choices") or [], h.get("answer") or ""
        picked = None
        if limit and h.get("asked"):
            i = option_picked(h["asked"][0], answer)
            picked = choices[i] if i is not None and i < len(choices) else None
        g = self.goal or {}
        tbc = g.get("to_be_confirmed") or []
        crit = g.get("done_when") or []

        def mock():
            ship = re.search(r"\bship\b|as is", answer, re.I)
            drop = re.search(r"\bdrop\b", answer, re.I)
            unknown = re.search(r"don'?t know|not yet|later|no idea|can'?t", answer, re.I)
            asked_items = [as_int(n) for n in re.findall(r"item (\d+)", json.dumps(h.get("asked")))]
            items = asked_items or [crit.index(t["criterion"]) + 1 for t in tbc if t["criterion"] in crit]
            facts = [{"item": n, "fact": answer} for n in items]
            return json.dumps({"say": "Thanks, recorded." if not unknown else "Recorded as to be confirmed.",
                               "clause": "done_when", "decision": "ship" if ship else "drop" if drop else "continue",
                               "confirmed": [] if unknown or ship or drop else facts,
                               "still_to_be_confirmed": facts if unknown else [],
                               "instruction_to_adaptation": f"Put the Requester's answer in: {answer}",
                               "next": "Adaptation"})
        r = self.call("identity", '{"say": str, "clause": str, "decision": "continue"|"drop"|"ship", "confirmed": '
                      '[{"item": int, "fact": str}] (facts the Requester supplied, by done-when item), '
                      '"still_to_be_confirmed": [{"item": int, "fact": str}] (facts they said they can\'t supply yet), '
                      '"instruction_to_adaptation": str|null, '
                      + next_field(("audit", "adaptation"), "Audit to re-check the current site when the site needs no "
                                   "change; Adaptation when the site must change (e.g. real details to put in)") + "}",
                      f"YOU ASKED THE REQUESTER: {json.dumps(h.get('asked'), ensure_ascii=False)}\nTHE REQUESTER "
                      f"ANSWERED: {answer}\nDONE-WHEN: {json.dumps(crit, ensure_ascii=False)}\nTO BE CONFIRMED NOW: "
                      f"{json.dumps(tbc, ensure_ascii=False)}\nAUDIT FINDINGS: {json.dumps(self._findings(), ensure_ascii=False)}"
                      "\nRecord what the answer settles against the charter, without changing done-when. A fact they "
                      "gave goes in confirmed; a fact they say they can't give yet goes in still_to_be_confirmed (that "
                      "done-when item is not met until they confirm it)."
                      + (f"\nThis answers a limit question ({limit}). decision: continue (keep working), drop (drop the "
                         "failing done-when items) or ship (ship the site as it is)." if limit else ""), mock)
        decision = picked or (str(r.get("decision") or "").lower() if limit else "continue")
        if decision not in ("continue", "drop", "ship") or (limit and decision not in choices):
            decision = "continue" if "continue" in choices or not limit else "ship"
        confirmed = self._tbc(r.get("confirmed"), crit)
        done_facts = {t["criterion"] for t in confirmed}
        g["confirmed_facts"] = (g.get("confirmed_facts") or []) + confirmed
        g["to_be_confirmed"] = self._tbc(r.get("still_to_be_confirmed"), crit,
                                         keep=[t for t in tbc if t["criterion"] not in done_facts])
        g["to_be_confirmed"] = [t for t in g["to_be_confirmed"] if t["criterion"] not in done_facts]
        self.save("goal.json", g)
        self.fail_floor = len(self.audits)       # the Requester's answer is new information
        if self.decisions:
            self.decisions[-1]["decision"] = decision
        if decision == "ship":
            self.post("identity", address(r.get("say") or "Shipping the site as it is.", "user"), to_user=True,
                      next="user", done=True)
            fails = workable(self.audits[-1]) if self.audits else ["nothing was built"]
            self.outcome = (f"Shipped as is on the Requester's decision ({limit or 'their answer'}). Still not "
                            f"workable: {'; '.join(fails)}.")
            self.turn = None
            return
        if decision == "drop":
            gone = [crit[i - 1] for i in h.get("failing_items") or [] if 1 <= i <= len(crit)]
            g["done_when"] = [c for c in crit if c not in gone]
            g["dropped_by_requester"] = (g.get("dropped_by_requester") or []) + gone
            g["to_be_confirmed"] = [t for t in g["to_be_confirmed"] if t["criterion"] not in gone]
            self.save("goal.json", g)
            self._say("identity", r.get("say") or "", "audit", None)
            self.post("system", f"Dropped from done-when on the Requester's decision: {'; '.join(gone) or 'nothing'}. "
                                "Audit re-checks the current site.")
            return self._handoff("audit", kind="audit")
        if limit:
            self.cycle_limit = self.cycle + MAX_CYCLES      # keep working: a fresh cycle allowance
            nxt, note = "adaptation", None
        else:
            nxt, note = self._pick("identity", r.get("next"), ("audit", "adaptation"), "adaptation")
        self._say("identity", r.get("say", ""), nxt, note)
        if confirmed:
            self.post("system", "Confirmed by the Requester: " + "; ".join(f"{t['criterion']} = {t['fact']}"
                                                                          for t in confirmed))
        if nxt == "audit":
            return self._handoff("audit", kind="audit")
        self._handoff("adaptation", kind="propose", new_cycle=bool(limit),
                      why=f"The Requester answered Identity: {answer}. Instruction: {r.get('instruction_to_adaptation')}"
                          + (f" Facts to put in: {json.dumps(confirmed, ensure_ascii=False)}" if confirmed else ""))

    def _identity_limit(self, h):
        """A safety limit was hit (budget, cycles, turns, the same failure twice in a row) or only the Requester can
        close what's left. Identity asks: keep working (adding budget if it ran out), drop the failing items, or ship
        as is. Options are fixed by code; Identity writes the message. The answer goes to _identity_hears_requester."""
        self.step = 8
        reason, last = h.get("reason") or "", self.audits[-1] if self.audits else None
        fails = workable(last)
        items = [r for r in (last or {}).get("results", []) if not r["pass"]]
        cheapest = min(RATES.values()) if RATES else 1
        add = min(max(LIMIT_ADD, cheapest), BUDGET_CAP - self.budget) if h.get("out_of_budget") else 0
        opts, budget, choices = [], [], []
        if not h.get("out_of_budget") or add > 0:
            opts.append("Keep working: " + (f"add {add} units to the budget and " if add else "")
                        + f"allow {MAX_CYCLES} more cycles" + (" (give the missing facts in your answer)"
                                                               if h.get("tbc") else ""))
            budget.append(add)
            choices.append("continue")
        if items:
            opts.append("Drop the failing done-when items: " + "; ".join(f"{r['item']}. {r['criterion']}" for r in items))
            budget.append(0)
            choices.append("drop")
        opts.append(f"Ship as is: site v{len(self.sites)} stays as it is" + (f", with {len(fails)} open problem(s)"
                                                                            if fails else ""))
        budget.append(0)
        choices.append("ship")
        q = {"question": "What should the department do?", "options": opts, **({"budget": budget} if any(budget) else {})}
        self._event("system", "limit", reason)
        r = self.call("identity", '{"say": str (to the Requester: which limit was hit and what still fails, in plain '
                      'words, 2-3 sentences; no recommendation)}',
                      f"LIMIT: {reason}\nWHAT STILL STOPS THE SITE BEING WORKABLE: {json.dumps(fails, ensure_ascii=False)}"
                      f"\nTHE OPTIONS CODE WILL OFFER: {json.dumps(opts, ensure_ascii=False)}\nTell the Requester.",
                      lambda: json.dumps({"say": f"{reason} Still open: {'; '.join(fails) or 'nothing'}."}))
        self._ask_user(r.get("say") or reason, [q], "limit", handoff={"kind": "requester_answered", "limit": reason,
                                                                       "choices": choices,
                                                                       "failing_items": [x["item"] for x in items]})

    def _identity_audit(self, h):
        """J2.h: is the site workable? Code decides that (workable()); Identity declares done with Audit's evidence.
        Not workable: back to J2.b, unless Audit needs a fact only the Requester knows (Identity asks), only
        to-be-confirmed items are left, or the same failure came back twice in a row (Identity asks what to do)."""
        self.step = 8
        last = self.audits[-1] if self.audits else None
        fails, findings = workable(last), self._findings(last)
        tbc = {t["criterion"] for t in (self.goal or {}).get("to_be_confirmed") or []}
        facts = [x for x in findings if x.get("needs_requester_fact") and x.get("verdict") not in ("PASS", "PASS_WITH_WARNING")
                 and x.get("criterion") not in tbc]
        recent = self.audits[max(self.fail_floor, len(self.audits) - 2):]
        same = len(recent) == 2 and failure_signature(recent[0]) == failure_signature(recent[1]) and fails
        only_tbc = fails and last and all(r["pass"] or r["verdict"] == "TO_BE_CONFIRMED" for r in last["results"]) \
            and not j2_check.problems(last.get("mechanical") or {}) and (last.get("mechanical") or {}).get("available")
        if fails and not facts and (same or only_tbc):
            return self._identity_limit({"reason": "Only you can close what's left: these done-when items are to be "
                                                   "confirmed." if only_tbc else
                                         "The same failure came back twice in a row, so another cycle would likely "
                                         "repeat it.", "tbc": bool(only_tbc)})

        def mock():
            if not fails:
                return json.dumps({"say": "@Requester Goal reached: the site is workable. Every done-when item passes "
                                          "with Audit's evidence and the render check is clean.", "clause": "done_when",
                                   "done": True, "next": "Requester"})
            return json.dumps({"say": "@Adaptation Not workable yet; the failing findings need rework.",
                               "clause": "done_when", "done": False, "needs_requester": bool(facts),
                               "requester_questions": [], "next": "Requester" if facts else "Adaptation"})
        r = self.call("identity", '{"say": str, "clause": str, "done": bool, "needs_requester": bool, '
                      '"requester_questions": [str], "instruction_to_adaptation": str|null, '
                      + next_field(("user", "adaptation"), "Requester when done=true or needs_requester=true; "
                                   "Adaptation for rework") + "}",
                      f"AUDIT'S FINDINGS (all, in full): {json.dumps(findings, ensure_ascii=False)}\n"
                      f"WORKABLE CHECK BY CODE: {'workable' if not fails else 'not workable: ' + json.dumps(fails, ensure_ascii=False)}\n"
                      f"FACTS ONLY THE REQUESTER KNOWS (from Audit): {json.dumps([x.get('needs_requester_fact') for x in facts], ensure_ascii=False)}\n"
                      f"{h.get('why', '')}\nJ2.h: the site is done only when it is workable: every done-when item passes "
                      "Audit, no JS errors, no horizontal overflow at 360px and 1280px, forms work, no broken in-page "
                      "link, nothing to be confirmed. Code checks this. Workable: declare done=true and tell the Requester "
                      "the goal is reached. Not workable: it goes back to Adaptation (J2.b); give the instruction. If a "
                      "fix needs a fact only the Requester knows (facts above, or any you see), set needs_requester=true "
                      "and ask for it in requester_questions; the run pauses until they answer.", mock)
        if not fails and r.get("done"):
            self.post("identity", address(r.get("say", ""), "user"), done=True, to_user=True, next="user")
            self.outcome = "Done: the site is workable. Every done-when item passes with Audit's evidence and the " \
                           "render check is clean."
            self.turn = None
            return
        questions = clean_questions(r.get("requester_questions"))
        questions += [{"question": f"{x['needs_requester_fact']} (done-when item {x.get('item')}). If you can't give it "
                                   "yet, say so and it's marked to be confirmed.", "options": []} for x in facts]
        if questions and (facts or r.get("needs_requester")):
            return self._ask_user(r.get("say", ""), questions, "fact", handoff={"kind": "requester_answered"}, done=False)
        note0 = ("Identity declared done, but the site isn't workable, so done-when can't hold. Back to J2.b."
                 if r.get("done") and fails else
                 "The site is workable, but Identity didn't declare done. Back to J2.b with Identity's reason."
                 if not fails else None)
        nxt, note = self._pick("identity", r.get("next"), ("adaptation",), "adaptation")
        self._say("identity", r.get("say", ""), nxt, note0 or note, done=False)
        self._handoff("adaptation", kind="propose", new_cycle=True,
                      why=f"Identity at J2.h: {r.get('instruction_to_adaptation') or r.get('say')} Not workable yet: "
                          f"{json.dumps(fails, ensure_ascii=False)}")

    # ------------------------------------------------------------------ conflicts between any two agents
    def _open_conflict(self, topic, between, about, subject, detail=None):
        c = {"id": f"C-{len(self.conflicts) + 1}", "cycle": self.cycle, "topic": topic, "between": between,
             "about": about, "subject": subject, "detail": detail, "attempts": [], "status": "open",
             "escalated": False, "attempts_before_escalation": None, "resolved_by": None, "identity": [],
             "escalated_to_user": False, "user_question": None, "user_answer": None, "winner": None, "outcome": None}
        self.conflicts.append(c)
        self._event(between[0], "dispute", f"{c['id']}: {NAMES[between[0]]} vs {NAMES[between[1]]} about {subject}")
        self._save_conflicts()
        return c

    def _attempt(self, c, who, text, position, msg, agree=None, n=None):
        n = n if n is not None else sum(1 for x in c["attempts"] if x["n"] > 0) + 1
        c["attempts"].append({"n": n, "who": who, "msg": msg["id"] if msg else None, "text": text or "",
                              "position": position, "agree": agree})
        self._save_conflicts()

    def _escalate(self, c, why=None):
        """No agreement after MAX_ATTEMPTS (or the J2.c bargain hit its time or spend bound): both final positions
        go to Identity (J2.d)."""
        a, b = c["between"]
        c["status"], c["escalated"] = "escalated", True
        c["attempts_before_escalation"] = sum(1 for x in c["attempts"] if x["n"] > 0)
        why = why or f"didn't settle it in {MAX_ATTEMPTS} attempts"
        c["escalated_because"] = why
        self.bargain = None
        self._event("system", "conflict", f"{c['id']}: {NAMES[a]} and {NAMES[b]}: {why}")
        self.post("system", f"{NAMES[a]} and {NAMES[b]} on {c['id']}: {why}. Passing both final positions to "
                            "Identity (J2.d).")
        self._save_conflicts()
        self._handoff("identity", kind="resolve", conflict=c["id"])

    def _settle(self, c, winner, outcome, by="agents"):
        c["status"], c["winner"], c["outcome"] = "settled", winner, outcome
        c["resolved_by"] = c["resolved_by"] or by
        c["attempts_used"] = sum(1 for x in c["attempts"] if x["n"] > 0)
        self._save_conflicts()

    def _can_dispute(self, other, about):
        """(ok, subject id or reason): Adaptation may dispute a failing Audit finding or a held workflow, once each."""
        about = str(about or "").strip()
        if other == "audit":
            last = self.audits[-1] if self.audits else None
            fails = [r for r in (last["results"] + last.get("extra_issues", []) if last else []) if not r.get("pass")]
            f = next((r for r in fails if about.lower() in (str(r.get("id")).lower(), f"item {r.get('item')}",
                                                             str(r.get("item")))), None)
            if not f:
                return False, f"no failing Audit finding '{about}'"
            sid = f["id"]
        elif other == "coordination":
            w = self._wf(about.upper())
            if not w or w["status"] != "held":
                return False, f"no held workflow '{about}'"
            sid = w["id"]
        else:
            return False, "Adaptation can dispute only an Audit finding or a Coordination HOLD"
        done = next((c for c in self.conflicts if c["about"] == sid and c["topic"] != "proposal"), None)
        return (False, f"{sid} was already disputed in {done['id']}") if done else (True, sid)

    def _turn_dispute(self, fn, h):
        """One attempt in a disagreement between two agents (not Adaptation <-> Priority, which bargain over
        workflows): agree with the other side, or hold a position with a reason. After MAX_ATTEMPTS, Identity rules."""
        c = self._conflict(h.get("conflict"))
        other = next(x for x in c["between"] if x != fn)
        n = sum(1 for x in c["attempts"] if x["n"] > 0) + 1

        def mock():
            if fn == "audit":
                return json.dumps({"say": "@Adaptation The finding stands: without a viewport meta tag, phones render "
                                          "the page at desktop width and shrink it, whatever the CSS does.",
                                   "agree": False, "position": "Finding stands: add the viewport meta tag."})
            return json.dumps({"say": f"@{NAMES[other]} Fair point, I accept that. I'll propose the fix.",
                               "agree": True, "position": f"Accepts {NAMES[other]}'s position."})
        tried = "\n".join(f"  attempt {x['n']} {NAMES[x['who']]}: {x['text']}" for x in c["attempts"])
        r = self.call(fn, '{"say": str (address @' + NAMES[other] + '), "agree": bool (true if you accept their '
                      'position), "position": str (your position in one sentence)}',
                      f"DISAGREEMENT {c['id']}: {NAMES[c['between'][0]]} vs {NAMES[c['between'][1]]} about "
                      f"{c['subject']}\n{c.get('detail') or ''}\nATTEMPTS SO FAR:\n{tried}\nThis is attempt {n} of "
                      f"{MAX_ATTEMPTS}. Settle it with {NAMES[other]} if you can: agree when their reason is better (say "
                      "what you accept), or keep your position with a reason tied to the charter or the evidence. After "
                      f"{MAX_ATTEMPTS} attempts it goes to Identity with both final positions.", mock)
        agree = bool(r.get("agree"))
        last = n >= MAX_ATTEMPTS and not agree
        m = self._say(fn, r.get("say", ""), None if agree else ("identity" if last else other), None,
                      conflict=c["id"], attempt=n, agree=agree)
        self._attempt(c, fn, r.get("say"), r.get("position"), m, agree, n)
        if agree:
            return self._apply(c, other, {"instruction": r.get("say")})
        if last:
            return self._escalate(c)
        self._handoff(other, kind="dispute", conflict=c["id"])

    def _apply(self, c, winner, r=None):
        """Carry out a settled conflict. winner: the agent whose position stands, "split" (proposal only), or None
        (no ruling: the default for the topic applies)."""
        r = r or {}
        topic, sid = c["topic"], c.get("about")
        by = c["resolved_by"] or "agents"
        if topic == "proposal":
            pa, pp = c.get("adaptation_final") or [], c.get("priority_final") or []
            if winner is None:
                self._settle(c, None, "Parked: no ruling, nothing registered from this negotiation.", by)
                self.conflict, self.exchanges, self.a_pos, self.p_pos = None, 0, [], []
                return self._parked(f"{c['id']} ended without a ruling")
            if winner == "split":
                names = [str(x) for x in r.get("workflows") or []]
                wfs = [next((x for x in pp + pa if x.get("name") == n), None) for n in names]
                missing = [n for n, x in zip(names, wfs) if x is None]
                if missing:
                    self._event("identity", "invalid_move", f"{c['id']}: split names unknown workflows {missing}")
                    self.post("system", f"Split check: {', '.join(missing)} isn't in either final position, so it isn't "
                                        "registered.", redirect=True)
                wfs = [x for x in wfs if x]
            else:
                wfs = pa if winner == "adaptation" else pp
            label = "Split" if winner == "split" else f"{NAMES[winner]}'s position stands"
            if self.fixes and not c.get("repriced") and granted_total(wfs) > granted_total(pp):
                # Fix (a): a ruling that costs more than Priority granted goes back to Priority once for pricing.
                c.update(repriced=True, status="repricing", pending_winner=winner, ruled_wfs=wfs)
                self._save_conflicts()
                self.post("system", f"J2_FIXES=1: Identity's ruling on {c['id']} costs {granted_total(wfs)}, more than "
                                    f"Priority granted ({granted_total(pp)}). It goes back to Priority once for pricing; "
                                    "Priority's answer is final.")
                return self._handoff("priority", kind="ruling", table=wfs, conflict=c["id"])
            self._settle(c, winner, f"{label}: {brief_list(wfs)} goes to the validator.", by)
            return self._agree(wfs)
        if topic == "hold":
            w = self._wf(sid)
            if winner == "adaptation" and w:
                w["hold_override"] = True
                self._settle(c, winner, f"HOLD on {sid} lifted: Coordination schedules it.", by)
                return self._handoff("coordination", kind="schedule")
            self._settle(c, winner or "coordination", f"HOLD on {sid} stands: Adaptation reshapes or parks the work.", by)
            return self._handoff("adaptation", kind="propose", why=f"{c['id']}: the HOLD on {sid} stands. "
                                 f"{r.get('instruction') or ''} Reshape the work so the missing condition is met, or park it.")
        # finding
        audit = self.audits[-1]
        f = next((x for x in audit["results"] + audit.get("extra_issues", []) if x.get("id") == sid), None)
        if winner == "adaptation" and f:
            f.update({"pass": True, "verdict": "WITHDRAWN", "note": f"{f.get('note', '')} (withdrawn in {c['id']})"})
            audit["all_pass"] = all(x.get("pass") for x in audit["results"])
            self.save("audits.json", self.audits)
            self._settle(c, winner, f"Finding {sid} withdrawn.", by)
            if audit["all_pass"]:
                return self._handoff("identity", kind="audit")
            return self._handoff("adaptation", kind="propose", why=f"{c['id']}: finding {sid} withdrawn; other "
                                                                   f"findings still fail: {self._gaps()}")
        self._settle(c, winner or "audit", f"Finding {sid} stands: Adaptation proposes the rework.", by)
        self._handoff("adaptation", kind="propose", why=f"{c['id']}: Audit's finding {sid} stands. "
                                                        f"{r.get('instruction') or ''} Propose the rework.")

    def _bargain_over(self):
        """J2.c: the Adaptation <-> Priority bargain is bounded by four hops (MAX_ATTEMPTS exchanges, checked by the
        callers), fifteen minutes and its spend (AI calls). Returns the bound it passed, or None."""
        b = self.bargain
        if not b:
            return None
        mins = (time.time() - b["start"]) / 60
        if mins >= BARGAIN_MINUTES:
            return f"the bargain ran {mins:.1f} min, past its {BARGAIN_MINUTES:g}-minute bound"
        if self.calls - b["calls"] >= BARGAIN_CALLS:
            return f"the bargain spent {self.calls - b['calls']} AI calls, its spend bound is {BARGAIN_CALLS}"
        return None

    def _parked(self, why):
        """Adaptation reshapes or parks it -> J2.b. Work already registered is built first."""
        self.bargain = None
        if self._waiting_work():
            self.post("system", f"Nothing new registered ({why}). Building the work already registered.")
            return self._handoff("coordination", kind="schedule")
        self.post("system", f"Nothing registered in cycle {self.cycle}: {why}. The next cycle starts from the open gaps.")
        self._handoff("adaptation", kind="propose", new_cycle=True, why=f"Nothing was registered last cycle ({why}).")

    # ------------------------------------------------------------------ J2.b / J2.c: Adaptation <-> Priority
    WF_FMT = ('[{"id": str, "name": str, "goal_gap": str, "expected_outcome": str, "outputs": [str], '
              '"completion_check": str, "dependencies": [str], "parts": [rate-card item, repeated for quantity], '
              '"revises": str|null (registered workflow id whose site section this one rewrites; null adds a new '
              'section), "estimated_resources": {"money": int, "calls": int, "time_minutes": int}}]')

    GRANT_FMT = WF_FMT[:-2] + (', "envelope": {"money_limit": int, "model_call_limit": int, "time_limit_minutes": int, '
                               '"retry_limit": int, "stop_loss": str}}]')

    def _gaps(self):
        return [r["criterion"] for r in (self.audits[-1]["results"] if self.audits else []) if not r["pass"]]

    def _turn_adaptation(self, h):
        self.step = 2
        if h.get("kind") == "dispute":
            return self._turn_dispute("adaptation", h)
        if h.get("kind") == "respond":
            return self._adaptation_responds(h)
        last = self.audits[-1] if self.audits else None
        fails = [{k: r.get(k) for k in ("id", "item", "criterion", "verdict", "note")}
                 for r in (last["results"] + last.get("extra_issues", []) if last else []) if not r.get("pass")]
        held = [{"id": w["id"], "name": w["name"]} for w in self.workflows if w["status"] == "held"]
        lessons = relevant_lessons(load_lessons(), " ".join([str(h.get("why") or ""), json.dumps(fails),
                                                             json.dumps((self.goal or {}).get("done_when"))]),
                                   include_test=self.test_lessons) if self.memory else []
        offered = [{k: x.get(k) for k in ("id", "problem", "cause", "fix", "test") if x.get(k) is not None}
                   for x in lessons]

        def mock_plain():
            if self.feedback:
                return json.dumps({"say": f"@Priority The Requester asked: \"{self.feedback}\". One workflow covers it.",
                                   "act": "PROPOSE", "next": "Priority",
                                   "workflows": [{"name": "Requester change", "goal_gap": self.feedback, "parts": ["fix"],
                                                  "outputs": ["index.html"], "completion_check": "Change visible"}]})
            phone = next((f for f in fails if "phone" in str(f["criterion"]).lower()), None)
            if phone and self._can_dispute("audit", phone["id"])[0]:
                return json.dumps({"say": f"@Audit I disagree with {phone['id']}: the layout uses fluid widths and the "
                                          "mechanical check found no overflow at 360px.", "act": "DISPUTE",
                                   "next": "Audit", "dispute": {"with": "Audit", "about": phone["id"],
                                                                "reason": "Fluid layout, no overflow at 360px"}})
            others = [{"name": f"Fix item {f['item']}", "goal_gap": f["criterion"], "parts": ["fix"], "revises": "W-2",
                       "outputs": ["index.html"], "completion_check": f["criterion"]} for f in fails
                      if f is not phone and f.get("item") and f.get("verdict") != "TO_BE_CONFIRMED"]
            if phone:
                return json.dumps({"say": f"@Priority {phone['id']} stands. One small fix closes it: add the viewport "
                                          "meta tag." + (" Plus a fix for each other failing item." if others else ""),
                                   "act": "PROPOSE", "next": "Priority",
                                   "workflows": [{"name": "Viewport fix", "goal_gap": phone["criterion"], "parts": ["fix"],
                                                  "outputs": ["index.html"],
                                                  "completion_check": "viewport meta tag present"}] + others})
            if others and self.cycle > 1:
                return json.dumps({"say": "@Priority One fix per failing item.", "act": "PROPOSE", "next": "Priority",
                                   "workflows": others})
            if self.cycle == 1 and not self.workflows:
                return json.dumps({"say": "@Priority Proposal for cycle 1: scaffold and styling, the charter's core "
                                          "sections, a stories section for warmth, and subtle animations.",
                                   "act": "PROPOSE", "next": "Priority", "workflows": [
                                       {"name": "Scaffold and styling", "goal_gap": "No site exists",
                                        "parts": ["page_section", "styling"], "outputs": ["index.html"],
                                        "completion_check": "index.html loads"},
                                       {"name": "Core sections", "goal_gap": "Every done-when section",
                                        "parts": ["page_section", "page_section", "page_section", "form"],
                                        "outputs": ["index.html"], "completion_check": "All done-when sections present"},
                                       {"name": "Stories section", "goal_gap": "Warm content: the beans, the farms and "
                                        "the people behind the cafe", "parts": ["blog_post"] * 3,
                                        "outputs": ["stories section"], "completion_check": "3 stories visible"},
                                       {"name": "Animations", "goal_gap": "Scroll and hover effects",
                                        "parts": ["interactive_feature", "interactive_feature"], "outputs": ["CSS"],
                                        "completion_check": "Effects run on scroll"}]})
            return json.dumps({"say": "@Priority Nothing left to propose.", "act": "PROPOSE", "next": "Priority",
                               "workflows": []})

        def mock():
            r = json.loads(mock_plain())
            if offered and r.get("act") == "PROPOSE":
                r["say"] += f" Using lesson {offered[0]['id']}: {offered[0]['fix']}"
                r["lesson_used"] = offered[0]["id"]
            return json.dumps(r)
        r = self.call("adaptation", '{"say": str, "act": "PROPOSE"|"POLICY_QUESTION"|"DISPUTE", "workflows": '
                      + self.WF_FMT + ', "question": str|null, "dispute": {"with": "Audit"|"Coordination", "about": str '
                      '(finding id or workflow id), "reason": str}|null, "lesson_used": str|null (id of the lesson '
                      'you applied, if any), '
                      + next_field(("priority", "identity", "audit", "coordination"), "Priority to get your proposal "
                                   "funded; Identity only for a policy question, put in \"question\"; Audit or "
                                   "Coordination only when you DISPUTE their finding or HOLD") + "}",
                      f"WHY YOU ARE UP: {h.get('why')}\nOPEN AUDIT FINDINGS: {json.dumps(fails)}\nHELD WORK: "
                      f"{json.dumps(held)}\nPropose the smallest workflows that close the gap, or ask Identity a policy "
                      "question. If you disagree with an open Audit finding or a Coordination HOLD, DISPUTE it with your "
                      f"reason instead: you and they get {MAX_ATTEMPTS} attempts to settle it before Identity rules. "
                      "Workflows change the site; checking it is Audit's job, so don't propose check, review or report "
                      "workflows. Each registered workflow gets its own agent that owns one section of the site file "
                      "(STATE.site_sections): to change what's inside an earlier workflow's section, set revises to that "
                      "workflow's id; otherwise the workflow adds a new section."
                      + (f"\nLESSONS FROM EARLIER WORK (most relevant first): {json.dumps(offered, ensure_ascii=False)}\n"
                         "If one applies, use it, set lesson_used to its id and say in one clause which one you used. "
                         "A lesson marked test came from a forced test failure; if you use one, call it a test lesson."
                         if offered else "") + (" Price every workflow with rate-card parts (see STATE.rate_card); its cost is "
                                      "fixed by them." if RATES else ""), mock)
        act = str(r.get("act", "")).upper()
        note = None
        if act == "DISPUTE":
            d = r.get("dispute") if isinstance(r.get("dispute"), dict) else {}
            other = key(d.get("with") or r.get("next"))
            ok, sid = self._can_dispute(other, d.get("about"))
            if ok:
                topic = "finding" if other == "audit" else "hold"
                src = next((x for x in fails if x["id"] == sid), None) if topic == "finding" else self._wf(sid)
                c = self._open_conflict(topic, ["adaptation", other], sid,
                                        f"{'finding' if topic == 'finding' else 'HOLD on'} {sid}",
                                        detail=json.dumps(src, ensure_ascii=False))
                m = self._say("adaptation", r.get("say", ""), other, None, act="DISPUTE", conflict=c["id"], attempt=1,
                              agree=False)
                self._attempt(c, "adaptation", r.get("say"), d.get("reason"), m, False, 1)
                return self._handoff(other, kind="dispute", conflict=c["id"])
            note = f"Dispute isn't valid: {sid}. Treated as a proposal."
            self._event("adaptation", "invalid_move", note)
        wfs = norm(r.get("workflows"))
        if act == "POLICY_QUESTION":
            self._say("adaptation", r.get("say", ""), "identity", note, act="POLICY_QUESTION")
            return self._handoff("identity", kind="question", frm="adaptation", question=r.get("question") or r.get("say"),
                                 resume={"to": "adaptation", "handoff": {"kind": "propose", "why": h.get("why")}})
        nxt, note2 = self._pick("adaptation", r.get("next") if act != "DISPUTE" else "priority", ("priority",),
                                "priority")
        used = str(r.get("lesson_used") or "")
        used = used if used in {x["id"] for x in offered} else None
        used_test = bool(used and next(x for x in offered if x["id"] == used).get("test"))
        if used:
            self.lessons_used.append({"cycle": self.cycle, "lesson": used, "offered": [x["id"] for x in offered],
                                      **({"test": True} if used_test else {})})
        self.a_msg = self._say("adaptation", r.get("say", ""), nxt, note or note2, proposal=wfs, cycle=self.cycle,
                               **({"lesson_used": used} if used else {}), **({"lesson_test": True} if used_test else {}),
                               **({"lessons_offered": [x["id"] for x in offered]} if offered else {}))
        if used_test:
            self._event("adaptation", "test_lesson", f"used test lesson {used}")
            self.post("system", f"TEST LESSON: Adaptation used {used}, a lesson from a forced test failure "
                                "(J2_MEMORY_TEST_LESSONS=1, demo runs only). It is not evidence from a real fix.",
                      warning=True, test=True)
        if not wfs:
            # Audit re-checks first, so J2.h never judges a stale audit (e.g. after the Requester confirmed a fact).
            self.post("system", "Adaptation proposed no workflows, so there is nothing to fund or register. Audit "
                                f"re-checks site v{len(self.sites)}, then Identity decides J2.h.")
            return self._handoff("audit", kind="audit")
        self.a_pos = wfs
        self.bargain = {"start": time.time(), "calls": self.calls}      # J2.c starts: hops, minutes, spend
        self._handoff("priority", kind="proposal", table=wfs)

    def _proposal_conflict(self):
        """The Adaptation <-> Priority negotiation becomes a logged conflict at Priority's first COUNTER or REFUSE."""
        if not self.conflict:
            self.conflict = self._open_conflict("proposal", ["adaptation", "priority"], None,
                                                f"what to fund in cycle {self.cycle}")
            m = self.a_msg
            self._attempt(self.conflict, "adaptation", m["text"] if m else "", "opening proposal", m, None, 0)
        return self.conflict

    def _adaptation_responds(self, h):
        offer, dec = h.get("offer") or [], h.get("decision") or ""
        c = self._proposal_conflict()

        def mock():
            if dec == "refuse" or self.exchanges in (1, 3) and self.cycle == 1:
                stories = {"name": "Stories section", "goal_gap": "Warm content: the beans, the farms and the people",
                           "parts": ["blog_post"] * 2, "outputs": ["stories section"], "completion_check": "2 stories"}
                say = ("@Priority The stories are what make a small cafe feel warm and personal. I can shrink them to "
                       "two (20)." if self.exchanges == 1 else
                       "@Priority Without any content beyond listings the page feels empty. I can't accept zero.")
                return json.dumps({"say": say, "act": "REVISE", "workflows": offer + [stories], "next": "Priority"})
            return json.dumps({"say": "@Priority Accepted.", "act": "ACCEPT", "workflows": [], "next": "Priority"})
        r = self.call("adaptation", '{"say": str, "act": "ACCEPT"|"REVISE"|"PARK", "workflows": ' + self.WF_FMT
                      + ' (your revision, for REVISE), ' + next_field(("priority", "identity"), "Priority to answer "
                      "your revision; Identity only for a policy question") + "}",
                      f"PRIORITY'S DECISION: {dec.upper()}\nPRIORITY OFFERS: {json.dumps(offer)}\nACCEPT only if the "
                      "offer is non-empty and still closes the gap. After a REFUSE you must REVISE (reshape it: a smaller "
                      "or different proposal) or PARK it (drop it for now). Exchange "
                      f"{self.exchanges + 1} of {MAX_ATTEMPTS}; after that Identity rules on both final positions.", mock)
        act, wfs = str(r.get("act") or "").upper(), norm(r.get("workflows"))
        act = "PARK" if act == "WITHDRAW" else act
        if act not in ("ACCEPT", "REVISE", "PARK"):
            act = "ACCEPT" if r.get("accept") and offer else ("REVISE" if wfs else "PARK")
        note = None
        if act == "ACCEPT" and (not offer or dec == "refuse"):
            act = "REVISE" if wfs else "PARK"
            note = (f"Accept isn't valid: nothing is on the table after Priority's {dec.upper() or 'answer'}. "
                    f"Treated as {act}.")
        elif act == "REVISE" and not wfs:
            act, note = "PARK", "Adaptation revised to an empty proposal. Treated as PARK."
        self.exchanges += 1
        meta = dict(exchange=self.exchanges, cycle=self.cycle, conflict=c["id"])
        if act == "ACCEPT":
            m = self._say("adaptation", r.get("say", ""), None, note, accept=True, **meta)
            self._attempt(c, "adaptation", r.get("say"), "accepts Priority's offer", m, True, self.exchanges)
            self._settle(c, "priority", f"Adaptation accepted Priority's {dec.upper()}: {brief_list(offer)} goes to "
                                        "the validator.")
            return self._agree(offer)
        if act == "PARK":
            m = self._say("adaptation", r.get("say", ""), None, note, act="PARK", **meta)
            self._attempt(c, "adaptation", r.get("say"), "parks the proposal", m, True, self.exchanges)
            self._settle(c, "priority", "Adaptation parked the proposal; nothing registered.")
            self.conflict, self.exchanges, self.a_pos, self.p_pos = None, 0, [], []
            return self._parked("Adaptation parked its proposal after Priority's " + dec.upper())
        self.a_pos = c["adaptation_final"] = wfs
        over = self._bargain_over()
        if self.exchanges >= MAX_ATTEMPTS or over:
            m = self._say("adaptation", r.get("say", ""), "identity", note, accept=False, proposal=wfs, **meta)
            self._attempt(c, "adaptation", r.get("say"), brief_list(wfs), m, False, self.exchanges)
            return self._escalate(c, over)
        nxt, note2 = self._pick("adaptation", r.get("next"), ("priority", "identity"), "priority")
        m = self._say("adaptation", r.get("say", ""), nxt, note or note2, accept=False, proposal=wfs, **meta)
        self._attempt(c, "adaptation", r.get("say"), brief_list(wfs), m, False, self.exchanges)
        if nxt == "identity":
            return self._handoff("identity", kind="question", frm="adaptation", question=r.get("say"),
                                 resume={"to": "priority", "handoff": {"kind": "proposal", "table": wfs}})
        self._handoff("priority", kind="proposal", table=wfs)

    def _turn_priority(self, h):
        if h.get("kind") == "dispute":
            return self._turn_dispute("priority", h)
        if h.get("kind") == "envelope":
            return self._priority_envelope(h)
        if h.get("kind") == "ruling":
            return self._priority_prices_ruling(h)
        self.step = 3
        table, remaining = h.get("table") or [], self.budget - self.spent

        def env(w):
            return {**w, "envelope": {"money_limit": w["cost"], "model_call_limit": 2, "time_limit_minutes": 10,
                                      "retry_limit": 1, "stop_loss": "stop if the build fails twice"}}

        def mock():
            if self.cycle == 1 and len(table) >= 4:
                offer = [env({**w, "parts": ["interactive_feature"], "cost": 10} if "anim" in w["name"].lower() else w)
                         for w in table if "stories" not in w["name"].lower()]
                say = ("@Adaptation Scaffold and core sections: granted. The stories serve no done-when item, refused. "
                       "Animations cut to 10. I'm keeping the rest in reserve for Audit fixes."
                       if self.exchanges == 0 else
                       "@Adaptation Still no on the stories. The charter's sections are in; the reserve stays.")
                # The first counter deliberately names Identity, to show the route check in mock mode.
                return json.dumps({"say": say, "decision": "COUNTER", "workflows": offer,
                                   "next": "Identity" if self.exchanges == 0 else "Adaptation"})
            return json.dumps({"say": f"@Adaptation Granted ({cost_of(table)} of {remaining} left).",
                               "decision": "GRANT", "workflows": [env(w) for w in table], "next": "Adaptation"})
        p = self.call("priority", '{"say": str (address @Adaptation), "decision": "GRANT"|"COUNTER"|"REFUSE", '
                      '"workflows": ' + self.GRANT_FMT + ' (what you fund, each with its envelope; for COUNTER, your '
                      'smaller version), '
                      + next_field(("adaptation", "identity"), f"Adaptation normally; Identity only once {MAX_ATTEMPTS} "
                                   "exchanges are used") + "}",
                      f"ON THE TABLE: {json.dumps(table)} (cost {cost_of(table)}, remaining budget {remaining}). "
                      f"Exchange {self.exchanges + 1} of {MAX_ATTEMPTS}; after that Identity rules on both final "
                      "positions." + (" Prices are fixed by the rate card: to spend less, remove parts or whole "
                                      "workflows, not the price." if RATES else ""), mock)
        dec = str(p.get("decision") or "").lower()
        wfs = norm(p.get("workflows")) or (table if dec == "grant" else [])
        note = None
        if dec not in ("grant", "counter", "refuse"):
            dec, wfs, note = "refuse", [], f"Priority's decision '{p.get('decision')}' isn't GRANT/COUNTER/REFUSE. Treated as REFUSE."
        elif dec == "grant" and granted_total(wfs) > remaining:
            dec, wfs, note = ("refuse", [], f"GRANT of {granted_total(wfs)} exceeds the remaining budget ({remaining}). "
                                            "Treated as REFUSE.")
        elif dec == "counter" and not wfs:
            dec, note = "refuse", "COUNTER with nothing in it. Treated as REFUSE."
        self.exchanges += 1
        self.p_pos = wfs
        self._track_refused(table, wfs, dec, f"at exchange {self.exchanges}")
        meta = dict(decision=dec, exchange=self.exchanges, cycle=self.cycle)
        if dec == "grant":
            m = self._say("priority", p.get("say", ""), None, note, **meta, **({"conflict": self.conflict["id"]}
                                                                              if self.conflict else {}))
            if self.conflict:
                self._attempt(self.conflict, "priority", p.get("say"), "grants Adaptation's revision", m, True,
                              self.exchanges)
                self._settle(self.conflict, "adaptation", f"Priority granted Adaptation's revision: {brief_list(wfs)} "
                                                          "goes to the validator.")
            return self._agree(wfs)
        c = self._proposal_conflict()
        c["priority_final"] = wfs
        c.setdefault("adaptation_final", self.a_pos)
        meta["conflict"] = c["id"]
        over = self._bargain_over()
        if self.exchanges >= MAX_ATTEMPTS or over:
            m = self._say("priority", p.get("say", ""), "identity", note, **meta)
            self._attempt(c, "priority", p.get("say"), brief_list(wfs), m, False, self.exchanges)
            return self._escalate(c, over)
        nxt, note2 = self._pick("priority", p.get("next"), ("adaptation",), "adaptation",
                                f"Identity only after {MAX_ATTEMPTS} exchanges; this was exchange {self.exchanges}")
        m = self._say("priority", p.get("say", ""), nxt, note or note2, **meta)
        self._attempt(c, "priority", p.get("say"), f"{dec.upper()}: {brief_list(wfs)}", m, False, self.exchanges)
        self._handoff("adaptation", kind="respond", offer=wfs, decision=dec)

    def _track_refused(self, table, offered, dec, when):
        """What Priority refused in this negotiation: everything on a REFUSE, or what a COUNTER left out."""
        names = {w.get("name") for w in offered}
        self.p_refused = {w.get("name"): f"Priority {'refused it' if dec == 'refuse' else 'left it out of its ' + dec.upper()} "
                                         f"{when}" for w in table if w.get("name") not in names}

    def _priority_prices_ruling(self, h):
        """J2_FIXES=1, fix (a): Priority prices Identity's ruling once and its answer is final. If the ruling is still
        over the remaining budget, Identity asks the Requester: add budget, or go with Priority's answer."""
        self.step = 3
        c, table, remaining = self._conflict(h.get("conflict")), h.get("table") or [], self.budget - self.spent

        def mock():
            keep = list(table)
            while keep and granted_total(keep) > remaining:
                keep.pop()
            env = lambda w: {**w, "envelope": {"money_limit": w["cost"], "model_call_limit": 2, "retry_limit": 1}}
            return json.dumps({"say": f"@Adaptation Identity's ruling priced: {granted_total(keep)} of {remaining} left.",
                               "decision": "GRANT" if len(keep) == len(table) else "COUNTER",
                               "workflows": [env(w) for w in keep]})
        p = self.call("priority", '{"say": str, "decision": "GRANT"|"COUNTER"|"REFUSE", "workflows": ' + self.GRANT_FMT
                      + ' (what you fund, each with its envelope)}',
                      f"IDENTITY RULED ON {c['id']}: {(c['identity'] or [{}])[-1].get('say')}\nTHE RULING TO PRICE: "
                      f"{json.dumps(table)} (cost {granted_total(table)}, remaining budget {remaining}).\nPrice it once: "
                      "GRANT, COUNTER (a smaller version you will fund) or REFUSE with a resource reason. Your answer is "
                      "final.", mock)
        dec = str(p.get("decision") or "").lower()
        wfs = norm(p.get("workflows")) or (table if dec == "grant" else [])
        if dec not in ("grant", "counter", "refuse") or granted_total(wfs) > remaining or (dec == "counter" and not wfs):
            dec, wfs = "refuse", []
        m = self._say("priority", p.get("say", ""), None, None, decision=dec, exchange="ruling", conflict=c["id"])
        c["repricing"] = {"decision": dec.upper(), "say": p.get("say"), "msg": m["id"], "workflows": wfs}
        self._track_refused(table, wfs, dec, f"when pricing Identity's ruling on {c['id']}")
        if dec == "grant":
            self._settle(c, c["pending_winner"], f"Priority granted Identity's ruling on repricing: {brief_list(wfs)} goes "
                                                 "to the validator.")
            return self._agree(wfs)
        cost = granted_total(table)
        if cost > remaining:
            need = cost - remaining
            q = {"question": f"Identity's ruling on {c['id']} costs {cost}, but only {remaining} is left. What should happen?",
                 "options": [f"Add {need} units so the ruling is funded in full: {brief_list(table)}",
                             f"Go with Priority's final answer ({dec.upper()}): {brief_list(wfs)}"]}
            c.update(user_question=q, escalated_to_user=True)
            self._save_conflicts()
            return self._ask_user(f"Priority's final answer on Identity's ruling was {dec.upper()}, and the ruling is over "
                                  "budget.", [q], "ruling_budget", handoff={"kind": "ruling_budget", "conflict": c["id"],
                                                                            "need": need},
                                  conflict=c["id"], auto=True)
        self._settle(c, "priority", f"Priority's final answer on Identity's ruling: {dec.upper()} {brief_list(wfs)}.")
        if wfs:
            return self._agree(wfs)
        self.conflict, self.exchanges, self.a_pos, self.p_pos = None, 0, [], []
        self._parked(f"Priority refused Identity's ruling on {c['id']} when pricing it")

    def _identity_ruling_budget(self, h):
        """J2_FIXES=1: the Requester answered whether to add budget for Identity's ruling."""
        self.step = 4
        c, answer, need = self._conflict(h.get("conflict")), h.get("answer"), as_int(h.get("need"))
        c["user_answer"] = answer
        r = self.call("identity", '{"say": str, "choice": 1|2}',
                      f"YOU ASKED THE REQUESTER: {json.dumps(c.get('user_question'))}\nTHE REQUESTER ANSWERED: {answer}\n"
                      "Which option did they choose? Say what happens next.",
                      lambda: json.dumps({"say": "The Requester added the budget; the ruling is registered in full."
                                          if re.search(r"\b1\b|add|yes|fund", answer, re.I) else
                                          "The Requester kept Priority's final answer.",
                                          "choice": 1 if re.search(r"\b1\b|add|yes|fund", answer, re.I) else 2}))
        self._say("identity", r.get("say", ""), None, None, conflict=c["id"], decision=True)
        c["resolved_by"] = "identity_after_user"
        if as_int(r.get("choice")) == 1:
            self._raise_budget(need, f"{c['id']} ruling")
            self.p_refused = {}              # the Requester funded the ruling, so nothing in it counts as refused
            self._settle(c, c["pending_winner"], "The Requester added budget: Identity's ruling goes to the validator.")
            return self._agree(c["ruled_wfs"])
        wfs = (c.get("repricing") or {}).get("workflows") or []
        self._settle(c, "priority", f"The Requester kept Priority's final answer: {brief_list(wfs)}.")
        if wfs:
            return self._agree(wfs)
        self.conflict, self.exchanges, self.a_pos, self.p_pos = None, 0, [], []
        self._parked(f"the Requester kept Priority's refusal on {c['id']}")

    # ------------------------------------------------------------------ J2.e: validator
    def _agree(self, wfs):
        self.step = 5
        registered, refused, defaults = self._register(wfs)
        self.cycle_registered = self.cycle_registered or bool(registered)
        if self.conflict:
            self.conflict["registered"] = [w["name"] for w in registered]
            self._save_conflicts()
        # Agreement closes this negotiation; a later one in the same cycle (e.g. a HOLD fix) starts fresh.
        self.exchanges, self.conflict, self.a_pos, self.p_pos, self.p_refused = 0, None, [], [], {}
        self.bargain = None
        if registered:
            self.feedback = None             # the Requester's change request is now being worked on
            msg = f"Registered {', '.join(w['id'] + ' ' + w['name'] for w in registered)}."
            if refused:
                msg += f" Rejected: {'; '.join(refused)}."
            if defaults:
                msg += f" Envelope defaults applied: {'; '.join(defaults)}."
            msg += " Workflow agents: " + "; ".join(
                f"{w['agent']} owns section {w['section']}" + (f" (rewrites it, was {self.sections[w['section']]['owner']})"
                                                               if w["section"] in self.sections else "")
                for w in registered) + "."
            self._say("validator", msg + f" Budget: {self.spent}/{self.budget} used.", "coordination", register=True,
                      charged=sum(w["cost"] for w in registered))
            return self._handoff("coordination", kind="schedule")
        self._say("validator", f"Rejected: {'; '.join(refused) or 'the agreed set was empty'}. Adaptation reshapes or "
                               "parks it.", "adaptation", register=False)
        self._parked("the validator registered nothing")

    def _waiting_work(self):
        return any(w["status"] in ("registered", "held") for w in self.workflows)

    CHECK_WORK = re.compile(r"\b(audit\w*|check|self[- ]check|verif\w*|qa|review|report|test)\b", re.I)

    REQUIRED = ("name", "goal_gap", "outputs", "completion_check")

    def _reject(self, name, reason):
        """A validator rejection: counted, saved for summary.json, and posted as a system note with the exact reason."""
        self.rejections.append({"cycle": self.cycle, "workflow": name, "reason": reason})
        self._event("validator", "role_refusal" if "Audit's job" in reason else "refused", f"{name}: {reason}")
        self.post("system", f"Validator rejected '{name}': {reason}.", rejected=name)
        return f"{name} ({reason})"

    def _register(self, agreed):
        """J2.e, plain code: every proposal is checked before it is registered, including one from an Identity ruling.
        Checks: required fields present, priced from the rate card, nothing Priority refused, cost fits what's left."""
        remaining, registered, refused, defaults = self.budget - self.spent, [], [], []
        for w in norm(agreed):
            c, name = granted(w), w.get("name") or "?"
            missing = [f for f in self.REQUIRED if not (w.get(f) or (f == "goal_gap" and w.get("purpose")))]
            rc, unknown = price(w)
            reason = ("a check or report on the site is Audit's job, not a workflow" if self.CHECK_WORK.search(str(name))
                      else f"required field(s) missing: {', '.join(missing)}" if missing
                      else f"{self.p_refused[name]}, so it can't be registered" if name in self.p_refused
                      else "no rate-card parts, so it has no price" if RATES and rc is None
                      else f"unknown rate-card parts {unknown}; allowed: {', '.join(RATES)}" if unknown
                      else "its cost is 0" if c <= 0
                      else f"it costs {c}, over the {remaining} left in the budget" if c > remaining else None)
            if reason:
                refused.append(self._reject(name, reason))
                continue
            remaining -= c
            env = {k: (w.get("envelope") or {}).get(k) for k in ("money_limit", "model_call_limit", "time_limit_minutes",
                                                               "retry_limit", "stop_loss")}
            env["money_limit"] = c
            for k, d in ENVELOPE_DEFAULTS.items():
                if env[k] is None:
                    env[k] = d
                    defaults.append(f"{name}: {k}={d}")
            if not RATES and as_int((w.get("envelope") or {}).get("money_limit")) <= 0:
                defaults.append(f"{name}: no money_limit granted, charged the estimate ({c})")
            wf = {"id": f"W-{len(self.workflows) + 1}", "proposal_id": w.get("id"), "name": w.get("name", "workflow"),
                  "purpose": w.get("purpose") or w.get("goal_gap", ""), "cost": c, "estimate": w.get("estimate", wf_cost(w)),
                  "envelope": env, "charged": True, "calls_used": 0, "retries_used": 0, "outputs": w.get("outputs"),
                  "completion_check": w.get("completion_check", ""), "dependencies": w.get("dependencies") or [],
                  "status": "registered", "cycle": self.cycle}
            # J2.e: the workflow gets its own agent, which owns one marked section of the site file. "revises" hands
            # an earlier workflow's section to it (only a section that exists and isn't already being rewritten).
            rv = str(w.get("revises") or "").upper()
            src = self._wf(rv)
            taken = {x["section"] for x in self.workflows if x["status"] in ("registered", "held", "running")}
            wf["section"] = src["section"] if src and src["section"] in self.sections and src["section"] not in taken \
                else wf["id"]
            wf["revises"] = rv if wf["section"] != wf["id"] else None
            add_workflow_agent(wf["id"])
            wf["agent"] = NAMES[wf["id"]]
            self.workflows.append(wf)
            registered.append(wf)
        self._recalc_spent()
        self.save("workflows.json", self.workflows)
        return registered, refused, defaults

    def _recalc_spent(self):
        """Budget used = money of every workflow currently charged (held work is released, not charged)."""
        self.spent = sum(w["cost"] for w in self.workflows if w.get("charged"))

    # ------------------------------------------------------------------ J2.f: Coordination, envelope check, workflow agents
    def _turn_coordination(self, h):
        if h.get("kind") == "dispute":
            return self._turn_dispute("coordination", h)
        self.step = 6
        todo = [w for w in self.workflows if w["status"] in ("registered", "held")]
        if not todo:
            self.agent_turns["coordination"] -= 1
            self.cycle_turns -= 1
            self.post("system", f"Queue empty: no registered work left in cycle {self.cycle}. Hand-off by code: Audit "
                                f"checks site v{len(self.sites)}.")
            return self._handoff("audit", kind="audit")
        ids = [w["id"] for w in todo]
        finished = {x[k] for x in self.workflows if x["status"] == "done" for k in ("id", "name") if x.get(k)}
        waits = {w["id"]: [d for d in w["dependencies"] if d not in finished] for w in todo}
        sched = self.call("coordination", '{"say": str, "rule": str, "order": [workflow id], '
                          '"holds": [{"id": str, "missing": str}], ' + next_field(("priority", "adaptation"),
                          "Priority to check the run envelope of the first workflow in your order; Adaptation only if "
                          "everything is on HOLD") + "}",
                          f"REGISTERED AND WAITING: {json.dumps(todo)}\nDONE OR FAILED: "
                          f"{json.dumps([[w['id'], w['status']] for w in self.workflows if w not in todo])}\n"
                          "Schedule them. Priority checks each run's envelope, then the workflow's own agent runs it "
                          "and reports back to you. One writer at a time on the site file: you hold the write lock.",
                          lambda: json.dumps({"say": "@Priority Schedule: " + " → ".join(f"{w['id']} {w['name']}" for w in todo
                                                                                       if not waits[w["id"]])
                                              + ". Each one writes index.html, so they run one at a time. Please check "
                                                "the first one's envelope.",
                                              "rule": "dependencies first, then registration order; one writer at a "
                                                      "time on index.html", "order": ids, "next": "Priority",
                                              "holds": [{"id": i, "missing": f"waits for {', '.join(d)} to finish"}
                                                        for i, d in waits.items() if d]}))
        order = [i for i in sched.get("order") or [] if i in ids] + [i for i in ids if i not in (sched.get("order") or [])]
        held = {x.get("id"): x.get("missing") for x in sched.get("holds") or [] if x.get("id") in ids}
        lifted = [i for i in held if (self._wf(i) or {}).get("hold_override")]
        for i in lifted:
            held.pop(i)
        released = []
        for w in todo:
            if w["id"] in held and w.get("charged"):
                w["charged"] = False
                released.append(f"{w['cost']} from {w['id']}")
            w["status"] = "held" if w["id"] in held else "registered"
        self._recalc_spent()
        ready = [i for i in order if i not in held]
        text = sched.get("say", "") + (f" Rule: {sched.get('rule')}." if sched.get("rule") else "")
        text += "".join(f"\nHOLD {i}: {why}" for i, why in held.items())
        for i, why in held.items():
            self._event("coordination", "hold", f"{i}: {why}")
        self.save("workflows.json", self.workflows)
        notes = [f"{', '.join(lifted)}: the HOLD was lifted in a settled conflict, so it can't be held again."] if lifted else []
        if released:
            notes.append(f"Released {', '.join(released)} while on HOLD; charged again only when it runs. "
                         f"Budget: {self.spent}/{self.budget} used.")
        if ready:
            nxt, note = self._pick("coordination", sched.get("next"), ("priority",), "priority",
                                   "Priority checks the run envelope before a workflow runs")
            self._say("coordination", text, nxt, note, schedule=ready)
            for n in notes:
                self.post("system", n)
            return self._handoff("priority", kind="envelope", wid=ready[0])
        nxt, note = self._pick("coordination", sched.get("next"), ("adaptation",), "adaptation",
                               "everything is on HOLD, so Adaptation must address the missing conditions")
        self._say("coordination", text, nxt, note, schedule=[])
        for n in notes:
            self.post("system", n)
        self.hold_bounces += 1
        if self.hold_bounces > 1:
            self.post("system", "Everything is still on HOLD after Adaptation's attempt. Audit checks what was built.")
            return self._handoff("audit", kind="audit")
        self._handoff("adaptation", kind="propose", why="Coordination put workflows on HOLD: "
                      + "; ".join(f"{i}: {why}" for i, why in held.items())
                      + ". Address the missing conditions, or DISPUTE a HOLD you think is wrong.")

    def _priority_envelope(self, h):
        """J2.f: Priority checks the run envelope before the workflow runs. The limits are numbers, so code checks
        them and posts Priority's 'allowed' without an AI call; Priority's model is asked only when the run is over a
        limit: HOLD it (it doesn't run), or request approval from Identity (once per workflow)."""
        self.step = 6
        w = self._wf(h.get("wid"))
        if not w:
            self.post("system", f"Priority was handed unknown workflow {h.get('wid')}. Back to Coordination.")
            return self._handoff("coordination", kind="schedule")
        env, remaining = w.get("envelope") or {}, self.budget - self.spent
        calls = as_int(env.get("model_call_limit"), 1)
        over = ([f"money: needs {w['cost']}, {remaining} left"] if not w.get("charged") and w["cost"] > remaining else []) \
            + ([f"model calls: {w['calls_used']} of {calls} used"] if w["calls_used"] >= calls else [])
        if not over:
            recharged = 0
            if not w.get("charged"):
                w["charged"], recharged = True, w["cost"]
                self._recalc_spent()
            self._say("priority", f"Envelope check for {w['id']}: within limits (money {w['cost']}, model calls "
                                  f"{w['calls_used']}/{calls}, retries {w['retries_used']}/{as_int(env.get('retry_limit'))}"
                                  f"). Budget {self.spent}/{self.budget} used. Runs now.", w["id"], None,
                      auto=True, envelope="allowed", charged=recharged)
            return self._handoff(w["id"], kind="build", wid=w["id"])
        asked = w.get("approval_asked")
        p = self.call("priority", '{"say": str, "decision": "HOLD"|"REQUEST_APPROVAL", "reason": str, '
                      + next_field(("coordination", "identity"), "Coordination for HOLD; Identity to request approval")
                      + "}",
                      f"RUN ENVELOPE CHECK for {json.dumps(w)}: over limit ({'; '.join(over)}). Budget "
                      f"{self.spent}/{self.budget} used. HOLD it (it doesn't run; Coordination carries on with other "
                      "work) or REQUEST_APPROVAL from Identity." + (" Approval was already asked for this workflow, so "
                                                                    "HOLD." if asked else ""),
                      lambda: json.dumps({"say": f"@Identity {w['id']} is over its envelope; requesting approval.",
                                          "decision": "HOLD" if asked else "REQUEST_APPROVAL",
                                          "next": "Coordination" if asked else "Identity"}))
        self._event("priority", "hold", f"{w['id']}: over its envelope ({'; '.join(over)})")
        if str(p.get("decision")).upper() == "REQUEST_APPROVAL" and not asked:
            w["approval_asked"] = True
            self._say("priority", p.get("say", ""), "identity", None, envelope="over limit")
            return self._handoff("identity", kind="approval", wid=w["id"], over=over)
        w["status"], w["charged"] = "unfunded", False
        self._recalc_spent()
        self.save("workflows.json", self.workflows)
        self._say("priority", p.get("say", ""), "coordination", None, envelope="hold")
        self._handoff("coordination", kind="schedule")

    def _turn_workflow_agent(self, h):
        """J2.f: the workflow's own agent (e.g. "W-1 Builder") writes only its marked section of the site file, while
        Coordination's write lock is on it. It retries within its envelope (model_call_limit, retry_limit) when a reply
        can't be used, then reports to Coordination. Code assembles the file from every section."""
        self.step = 6
        w = self._wf(h.get("wid") or self.turn)
        if not w:
            self.post("system", f"{self.turn} has no registered workflow. Back to Coordination.")
            return self._handoff("coordination", kind="schedule")
        fn, sid = w["id"], w["section"]
        w["status"] = "running"
        self.write_lock = fn
        env = w.get("envelope") or {}
        max_calls, max_retries = as_int(env.get("model_call_limit"), 1), as_int(env.get("retry_limit"), 0)
        prev = self.sites[-1] if self.sites else ""
        if len(prev) > SITE_LIMIT:
            self.post("system", f"Warning: site v{len(self.sites)} is {len(prev):,} characters. {fn} sees only the "
                                f"first {SITE_LIMIT:,}, so the end of the file may be lost.", warning=True)
        mine = self.sections.get(sid)
        brief = {k: w.get(k) for k in ("id", "name", "purpose", "outputs", "completion_check", "envelope", "revises")}

        def mock():
            head, body = mock_section(w, self.goal, self.sections)
            return (json.dumps({"say": f"@Coordination {fn} done: {w['name']}. Section {sid} written; completion "
                                       f"check: {w['completion_check']}.", "next": "Coordination"})
                    + (f"\n```head\n{head}\n```" if head else "") + (f"\n```section\n{body}\n```" if body else ""))
        got, raw, stop, last_err = None, "", None, None
        while got is None:
            if w["calls_used"] >= max_calls:
                stop = f"it used its envelope's model_call_limit ({max_calls})" + (f"; last problem: {last_err}"
                                                                                  if last_err else "")
                break
            w["calls_used"] += 1
            raw = self.call(fn, 'First line: a JSON object {"say": str (one short line reporting to @Coordination: '
                            'what you changed and whether your completion check holds), "next": "Coordination", '
                            + self.REASON + '}. Then, '
                            'only if your section needs page-head tags, a ```head block (meta, link, style or script '
                            'tags only). Then a ```section block: your section\'s HTML only, no <html>, <head> or <body> '
                            'tags (inline <style> and <script> are fine).',
                            f"YOU ARE {NAMES[fn]}, the agent for one registered workflow.\nYOUR WORKFLOW: "
                            f"{json.dumps(brief, ensure_ascii=False)}\nYOU OWN SECTION {sid} of the site file. Code puts "
                            "your head block in the page head and your section in the body, in section order, between "
                            "markers. Write the whole section each time; don't repeat other sections."
                            + (f"\nYOUR SECTION NOW (last written by {mine['owner']}):\n```head\n{mine['head']}\n```\n"
                               f"```section\n{mine['body']}\n```" if mine else "")
                            + (f"\nYOUR LAST ATTEMPT WAS REJECTED: {last_err}. Fix that." if last_err else "")
                            + f"\nTHE WHOLE SITE FILE NOW (v{len(self.sites)}, read only):\n{prev[:SITE_LIMIT]}",
                            mock, max_tokens=16000, json_reply=False)
            try:
                got = parse_section(raw)
                w["last_check"] = "usable section" + (" and head tags" if got[0] else "")
            except ValueError as e:
                last_err = w["last_check"] = str(e)
                if w["retries_used"] >= max_retries:
                    stop = f"{last_err}, and it used its envelope's retry_limit ({max_retries})"
                    break
                w["retries_used"] += 1
                self.post("system", f"{fn} attempt {w['calls_used']} can't be used: {last_err}. Retry "
                                    f"{w['retries_used']} of {max_retries} (within its envelope).")
        self.write_lock = None
        head = raw.split("```")[0].strip()
        try:
            meta = llm.extract_json(head)
        except ValueError:
            meta = {"say": head}
        log = next((c for c in reversed(self.call_log) if c["fn"] == fn), None)
        if log:   # the structured part of a workflow agent's reply, for the detail view
            log["reply"] = {"say": meta.get("say"), "next": meta.get("next"), "check": w.get("last_check"),
                            "head_chars": len(got[0]) if got else 0, "section_chars": len(got[1]) if got else 0}
            log["reason"] = meta.get("reason") or (self.MOCK_REASON if llm.MOCK else None)
        nxt, note = self._pick(fn, meta.get("next"), ("coordination",), "coordination")
        if got is None:      # code writes the failure report, so the unusable reply isn't route-checked
            w["status"] = "failed"
            self._say(fn, f"@Coordination {fn} failed: {stop}. My section is unchanged.", "coordination", None,
                      workflow=fn)
            self._event(fn, "limit_fail", f"{fn}: {stop}")
            self.save("workflows.json", self.workflows)
            return self._handoff("coordination", kind="schedule")
        self.sections[sid] = {"owner": fn, "head": got[0], "body": got[1], "workflow": w["name"]}
        html_out = assemble((self.goal or {}).get("site_name") or "Site", self.sections)
        self.sites.append(html_out)
        os.makedirs(os.path.join(self.dir, "site"), exist_ok=True)
        for name in (f"v{len(self.sites)}.html", "index.html"):
            with open(os.path.join(self.dir, "site", name), "w", encoding="utf-8") as f:
                f.write(html_out)
        self.save("sections.json", self.sections)
        w["status"], w["version"] = "done", len(self.sites)
        self.save("workflows.json", self.workflows)
        self._say(fn, meta.get("say") or f"{fn} done.", nxt, note, workflow=fn, version=len(self.sites), section=sid,
                  workflow_cost=w["cost"])
        size = len(html_out.encode("utf-8"))
        if size > SITE_WARN_BYTES:
            self.post("system", f"Warning: site v{len(self.sites)} is {size / 1000:.0f} KB, over builder.md's ~60 KB "
                                "single-page rule.", warning=True)
        self._handoff("coordination", kind="schedule")

    # ------------------------------------------------------------------ J2.g: Audit
    def _audit_findings(self, findings, crit):
        """One result per done-when item, matched by item number. A missing item, or a PASS with no evidence, becomes
        BLOCKED_BY_EVIDENCE (audit.md: when evidence is absent, don't guess). Other findings are extra issues."""
        by_item, extras = {}, []
        for i, f in enumerate(x for x in findings if isinstance(x, dict)):
            row = {"id": f.get("id") or f"F-{i + 1}", "criterion": f.get("criterion", ""),
                   "verdict": str(f.get("verdict", "")).upper(), "note": str(f.get("evidence") or "").strip(),
                   "severity": f.get("severity"), "confidence": f.get("confidence"),
                   "needs_requester_fact": str(f.get("needs_requester_fact") or "").strip() or None}
            n = as_int(f.get("item"), 0)
            if not n:   # no item number: match the criterion text instead
                n = next((k for k, c in enumerate(crit, 1) if c and c.lower()[:40] in row["criterion"].lower()), 0)
            if 1 <= n <= len(crit) and n not in by_item:
                by_item[n] = row
            else:
                extras.append(row)
        results = []
        for n, c in enumerate(crit, 1):
            row = by_item.get(n)
            if not row:
                self._event("audit", "invalid_move", f"no finding for done-when item {n}")
                row = {"id": f"F-missing-{n}", "verdict": "BLOCKED_BY_EVIDENCE", "note": "Audit filed no finding for "
                       "this item.", "severity": "medium", "confidence": "high"}
            elif row["verdict"] in ("PASS", "PASS_WITH_WARNING") and not row["note"]:
                self._event("audit", "invalid_move", f"{row['id']} passed item {n} without evidence")
                row = {**row, "verdict": "BLOCKED_BY_EVIDENCE", "note": "Marked PASS with no evidence; treated as "
                       "BLOCKED_BY_EVIDENCE."}
            tbc = next((t for t in (self.goal or {}).get("to_be_confirmed") or [] if t["criterion"] == c), None)
            if tbc:   # J2.g: a fact the Requester hasn't confirmed yet: this item is not met, whatever the page shows
                row = {**row, "verdict": "TO_BE_CONFIRMED", "note": f"Waiting on the Requester: {tbc['fact']}. "
                                                                    f"(Audit's own note: {row.get('note') or 'none'})"}
            results.append({**row, "item": n, "criterion": c, "pass": row["verdict"] in ("PASS", "PASS_WITH_WARNING")})
        return results, extras

    def _audit_tally(self, results, extras):
        """A code-written tally under Audit's message, so the chat and the report always agree."""
        by = {}
        for x in results:
            by.setdefault(x["verdict"], []).append(f"{x['id']} item {x['item']}")
        parts = [f"{len(v)} {k}" + ("" if k == "PASS" else f" ({', '.join(v)})") for k, v in by.items()]
        return (f"Findings (code tally): {'; '.join(parts)}"
                + (f"; extra issues: {', '.join(x['id'] + ' ' + x['verdict'] for x in extras)}" if extras else "") + ".")

    def _turn_audit(self, h):
        if h.get("kind") == "dispute":
            return self._turn_dispute("audit", h)
        self.step = 7
        site = self.sites[-1] if self.sites else ""
        crit = (self.goal or {}).get("done_when", [])
        mech = j2_check.check(site) if site else {"available": False, "note": "no site built yet"}
        if site:
            self.post("system", j2_check.summary(mech) + f" (site v{len(self.sites)})", mechanical=True)
            for p in j2_check.problems(mech):
                self.events.append({"agent": "system", "type": "mechanical", "detail": p, "msg": len(self.chat),
                                    "cycle": self.cycle})
        if len(site) > SITE_LIMIT:
            self.post("system", f"Warning: site v{len(self.sites)} is {len(site):,} characters. Audit sees only the "
                                f"first {SITE_LIMIT:,}, so findings about the end of the file may be wrong.", warning=True)

        def mock():
            fs = []
            for i, c in enumerate(crit, 1):
                phone = "phone" in c.lower()
                ok = 'name="viewport"' in site if phone else f'data-item="{i}"' in site
                fs.append({"id": f"F-{i}", "item": i, "criterion": c, "verdict": "PASS" if ok else "NEEDS_REVISION",
                           "severity": "low" if ok else "high", "confidence": "high",
                           "evidence": ("Viewport meta tag present; layout is fluid" if ok else "No viewport meta tag, so "
                                        "phones render the page at desktop width") if phone else
                                       ("Section present in the page" if ok else "No section for this item")})
            n = sum(f["verdict"] == "NEEDS_REVISION" for f in fs)
            return json.dumps({"say": "@Identity All criteria pass; done-when may hold." if not n else
                               f"@Identity {n} finding needs revision.", "findings": fs, "next": "Identity"})
        r = self.call("audit", '{"say": str, "findings": [{"id": "F-1", "item": int|null (done-when item number; null '
                      'for an extra issue), "criterion": str, "verdict": "PASS"|"PASS_WITH_WARNING"|'
                      '"NEEDS_REVISION"|"BLOCKED_BY_EVIDENCE"|"POLICY_CONCERN", "severity": "low"|"medium"|"high"|'
                      '"critical", "confidence": "low"|"medium"|"high", "evidence": str (one line: what you observed '
                      'in the code or the mechanical check), "needs_requester_fact": str|null (the fact only the '
                      'Requester knows that this item needs, e.g. "the cafe\'s phone number"; null otherwise)}] '
                      '(exactly one finding per done-when item, plus one per extra issue; a PASS needs evidence), '
                      + next_field(("identity",), "Identity: you file every finding to Identity, who decides J2.h") + "}",
                      f"CRITERIA: {json.dumps(crit)}\nMECHANICAL CHECK (run by code in headless Chrome; treat as evidence, and "
                      f"use BLOCKED_BY_EVIDENCE only for what neither it nor the code can show): {json.dumps(mech)}\n"
                      f"SITE v{len(self.sites)}:\n{site[:SITE_LIMIT]}", mock,
                      max_tokens=1200)
        results, extras = self._audit_findings(r.get("findings") or r.get("results") or [], crit)
        forced = self._force_fail(results)
        audit = {"cycle": self.cycle, "version": len(self.sites), "results": results, "extra_issues": extras,
                 "mechanical": mech, "all_pass": bool(results) and all(x.get("pass") for x in results)}
        self.audits.append(audit)
        self.save("audits.json", self.audits)
        nxt, note = self._pick("audit", r.get("next"), ("identity",), "identity",
                               "Audit files its findings to Identity, who decides J2.h")
        fails = workable(audit)
        self._say("audit", r.get("say", "") + "\n" + self._audit_tally(results, extras)
                  + (" Workable (code): yes." if not fails else f" Workable (code): no, {len(fails)} problem(s)."),
                  nxt, note, audit=audit["all_pass"], version=len(self.sites), workable=not fails,
                  **({"forced_test": forced} if forced else {}))
        if self.memory and len(self.audits) >= 2:
            self._learn(self.audits[-2], audit)
        failed = [f"workflow {w['id']} {w['name']} failed (envelope limits)" for w in self.workflows
                  if w["status"] == "failed" and w["cycle"] == self.cycle]
        self._handoff("identity", kind="audit", why=f"Failed workflows this cycle: {failed}" if failed else "")

    def _force_fail(self, results):
        """J2_FORCE_AUDIT_FAIL=<item>: a test switch for live runs. In cycle 1 only (Audit's first check), the item's
        result is overridden to NEEDS_REVISION with the note "forced test failure"; Audit's own verdict is kept in
        the note. Everything after runs normally, and later audits are real. Returns the item number when applied."""
        n = self.force_fail
        if not n or self.forced or self.cycle != 1:
            return None
        self.forced = True
        row = next((x for x in results if x["item"] == n), None)
        if not row:
            self.post("system", f"TEST SWITCH J2_FORCE_AUDIT_FAIL={n} ignored: the charter has no done-when item {n} "
                                f"(it has {len(results)}).", warning=True)
            return None
        real = f"{row['verdict']}: {row.get('note') or 'no note'}"
        row.update(verdict="NEEDS_REVISION", severity="medium", forced_test=True, **{"pass": False},
                   note=f"forced test failure (J2_FORCE_AUDIT_FAIL={n}; Audit's own verdict was {real})")
        self._event("system", "forced_test", f"item {n} forced to NEEDS_REVISION (Audit's own verdict: {real})")
        self.post("system", f"TEST SWITCH J2_FORCE_AUDIT_FAIL={n}: Audit's result for done-when item {n} "
                            f"(\"{row['criterion']}\") is overridden to NEEDS_REVISION. This is a test, not a real "
                            f"finding (Audit's own verdict: {real}). Later audits are real.", warning=True, test=True)
        return n

    def _learn(self, prev, cur):
        """J2.h learns: Audit confirmed a fix worked (a problem in the previous audit is gone, and a workflow ran in
        between), so Adaptation writes a lesson (problem, cause, fix) and code saves it to memory/lessons.jsonl."""
        now_ok = {r["criterion"] for r in cur["results"] if r["verdict"] in ("PASS", "PASS_WITH_WARNING")}
        fixed = [{"id": r["id"], "criterion": r["criterion"], "verdict": r["verdict"], "note": r.get("note"),
                  **({"forced": True} if r.get("forced_test") else {})}
                 for r in prev["results"] if not r["pass"] and r["criterion"] in now_ok]
        gone = set(j2_check.problems(prev.get("mechanical") or {})) - set(j2_check.problems(cur.get("mechanical") or {}))
        fixed += [{"id": "mechanical", "criterion": p, "verdict": "render check", "note": p} for p in sorted(gone)
                  if (cur.get("mechanical") or {}).get("available")]
        ran = [{"id": w["id"], "name": w["name"], "purpose": w["purpose"], "completion_check": w["completion_check"]}
               for w in self.workflows if w["status"] == "done" and prev["version"] < w.get("version", 0) <= cur["version"]]
        if not fixed or not ran:
            return

        def mock():
            return json.dumps({"say": f"Audit confirmed {len(fixed)} fix(es); lesson saved.", "lessons": [
                {"problem": f"{x['criterion']}: {x['note']}", "cause": "The first build left it out",
                 "fix": ", ".join(w["name"] for w in ran)} for x in fixed]})
        r = self.call("adaptation", '{"say": str (one line for the chat), "lessons": [{"problem": str, "cause": str, '
                      '"fix": str}] (one per fixed problem)}',
                      f"AUDIT CONFIRMED THESE FIXES WORKED (failing in v{prev['version']}, passing in v{cur['version']}): "
                      f"{json.dumps(fixed, ensure_ascii=False)}\nWORKFLOWS THAT RAN IN BETWEEN: "
                      f"{json.dumps(ran, ensure_ascii=False)}\nWrite one lesson per fixed problem for future runs on any "
                      "website: the problem in general terms, its cause, and the fix that worked. One sentence each.", mock)
        saved = []
        for x in [x for x in r.get("lessons") or [] if isinstance(x, dict) and x.get("problem") and x.get("fix")][:len(fixed)]:
            lesson = {"id": f"L-{self.run_id}-{len(self.lessons_saved) + 1}", "problem": str(x["problem"]),
                      **({"test": True} if any(f.get("forced") for f in fixed) else {}),
                      "cause": str(x.get("cause") or ""), "fix": str(x["fix"]), "run": self.run_id, "cycle": self.cycle,
                      "versions": [prev["version"], cur["version"]], "workflows": [w["id"] for w in ran],
                      "t": time.strftime("%Y-%m-%d %H:%M:%S")}
            save_lesson(lesson)
            self.lessons_saved.append(lesson)
            saved.append(lesson["id"])
        self.agent_turns["adaptation"] = self.agent_turns.get("adaptation", 0) + 1
        if saved:
            self._say("adaptation", (r.get("say") or "Lesson saved.") + f" Saved {', '.join(saved)} to memory.", None,
                      None, act="LESSON", lessons=saved)

    # ------------------------------------------------------------------ run report
    REVIEW_FMT = ('{"verdict": str (one sentence on how the department did), '
                  '"agents": {"identity"|"adaptation"|"priority"|"coordination"|"audit"|<workflow agent id, e.g. "W-1">: '
                  '{"score": 1-5, "note": str}}, "went_well": [str], "problems": [str], "learnings": [str]}')

    def _metrics(self):
        """Facts counted by code: no model judgment in here."""
        ev = lambda t, a=None: [e for e in self.events if e["type"] == t and (a is None or e["agent"] == a)]
        decisions = [m.get("decision") for m in self.chat if m["who"] == "priority" and m.get("decision")]
        agents = {fn: {"turns": self.agent_turns.get(fn, 0), "redirects": len(ev("redirect", fn)),
                       "invalid_moves": len(ev("invalid_move", fn))}
                  for fn in ("identity", "adaptation", "priority", "coordination", "audit")
                  + tuple(w["id"] for w in self.workflows)}
        est_vs_price = [{"id": w["id"], "name": w["name"], "agent_estimate": w.get("estimate"), "charged": w["cost"]}
                        for w in self.workflows]
        audits = [{"cycle": a["cycle"], "version": a["version"], "all_pass": a["all_pass"],
                   "pass": sum(r["verdict"].upper() == "PASS" for r in a["results"]),
                   "warn": sum(r["verdict"].upper() == "PASS_WITH_WARNING" for r in a["results"]),
                   "fail": sum(not r["pass"] for r in a["results"]),
                   "mechanical": j2_check.problems(a.get("mechanical") or {}),
                   "mechanical_ran": bool((a.get("mechanical") or {}).get("available"))} for a in self.audits]
        cs = self.conflicts
        pauses = [e.get("pause") for e in ev("pause")]
        return {"outcome": self.outcome, "brief": self.request, "model": None if llm.MOCK else llm.MODEL,
                "mock": llm.MOCK, "cycles": self.cycle, "ai_calls": self.calls,
                "minutes": round((time.time() - self.started) / 60, 1) if self.started else 0,
                "budget": {"total": self.budget, "start": BUDGET, "cap": BUDGET_CAP, "raises": self.raises,
                           "spent": self.spent, "rate_card": bool(RATES)},
                "site_versions": len(self.sites), "site_bytes": len(self.sites[-1].encode("utf-8")) if self.sites else 0,
                "agents": agents,
                "negotiation": {"proposals": sum(1 for m in self.chat if m["who"] == "adaptation" and m.get("proposal")),
                                "grants": decisions.count("grant"), "counters": decisions.count("counter"),
                                "refuses": decisions.count("refuse"),
                                "refuses_converted_by_code": sum("Treated as REFUSE" in e["detail"]
                                                                 for e in ev("invalid_move", "priority")),
                                "parks": sum(1 for m in self.chat if m.get("act") == "PARK")},
                "conflicts": {"total": len(cs),
                              "settled_by_agents": sum(c["resolved_by"] == "agents" for c in cs),
                              "resolved_by_identity": sum(c["resolved_by"] == "identity" for c in cs),
                              "asked_requester": sum(bool(c["escalated_to_user"]) for c in cs),
                              "open": sum(c["status"] != "settled" for c in cs),
                              "list": [{"id": c["id"], "cycle": c["cycle"], "topic": c["topic"], "between": c["between"],
                                        "attempts": sum(1 for x in c["attempts"] if x["n"] > 0),
                                        "escalated": c["escalated"], "resolved_by": c["resolved_by"],
                                        "user_question": (c["user_question"] or {}).get("question"),
                                        "user_answer": c["user_answer"], "outcome": c["outcome"]} for c in cs]},
                "requester_questions": {"total": len(pauses), "by_kind": {k: pauses.count(k) for k in set(pauses)}},
                "workflows": {"registered": len(self.workflows),
                              "done": sum(w["status"] == "done" for w in self.workflows),
                              "failed": sum(w["status"] == "failed" for w in self.workflows),
                              "held_ever": len({e["detail"].split(":")[0] for e in ev("hold")}),
                              "estimate_vs_charged": est_vs_price},
                "validator_refusals": len(ev("refused")) + len(ev("role_refusal")),
                "role_refusals": len(ev("role_refusal")), "pauses": len(pauses), "stuck": len(ev("stuck")),
                "limit_failures": len(ev("limit_fail")), "warnings": len(ev("warning")),
                "audits": audits, "to_be_confirmed": (self.goal or {}).get("to_be_confirmed") or [],
                "workable": workable(self.audits[-1]) if self.audits else None,
                "lessons": {"memory": self.memory, "saved": [x["id"] for x in self.lessons_saved],
                            "used": self.lessons_used}}

    def _write_summary(self):
        """runs/<run>/summary.json when a run ends (done, stopped, out of budget or crashed). Code only, no AI call."""
        o = self.outcome or ""
        status = next((k for p, k in (("Done", "done"), ("Shipped", "shipped"), ("Crashed", "crashed"))
                       if o.startswith(p)), "stopped")
        last = self.audits[-1] if self.audits else None
        self.save("summary.json", {
            "run": self.run_id, "j2_fixes": int(self.fixes), "provider": None if llm.MOCK else llm.PROVIDER,
            "force_audit_fail": self.force_fail or None, "test_lessons": self.test_lessons,
            "model": None if llm.MOCK else llm.MODEL, "mock": llm.MOCK, "brief": self.request,
            "change_requests": [m["text"] for m in self.chat if m["who"] == "user" and m.get("change")],
            "status": status, "outcome": o,
            "budget": {"start": BUDGET, "granted": self.budget, "used": self.spent, "raises": self.raises},
            "ai_calls": self.calls, "cycles": self.cycle,
            "questions_to_user": self.decisions,
            "conflicts": [{"id": c["id"], "pair": c["between"], "topic": c["topic"], "subject": c["subject"],
                           "attempts": sum(1 for x in c["attempts"] if x["n"] > 0), "escalated": c["escalated"],
                           "resolved_by": c["resolved_by"], "repriced": bool(c.get("repriced")),
                           "user_question": (c["user_question"] or {}).get("question"), "user_answer": c["user_answer"],
                           "outcome": c["outcome"]} for c in self.conflicts],
            "validator_rejections": self.rejections,
            "holds": [{"cycle": e["cycle"], "by": e["agent"], "detail": e["detail"]} for e in self.events
                      if e["type"] == "hold"],
            "audits": [{"cycle": a["cycle"], "version": a["version"], "all_pass": a["all_pass"],
                        "verdicts": [{"id": r.get("id"), "item": r.get("item"), "verdict": r.get("verdict")}
                                     for r in a["results"] + a.get("extra_issues", [])]} for a in self.audits],
            "site_versions": len(self.sites),
            "workable": workable(last) if last else None,
            "to_be_confirmed": (self.goal or {}).get("to_be_confirmed") or [],
            "dropped_by_requester": (self.goal or {}).get("dropped_by_requester") or [],
            "workflow_agents": [{"id": w["id"], "agent": w.get("agent"), "section": w.get("section"),
                                 "revises": w.get("revises"), "status": w["status"], "calls": w["calls_used"],
                                 "retries": w["retries_used"]} for w in self.workflows],
            "limits_hit": [e["detail"] for e in self.events if e["type"] == "limit"],
            "lessons": {"memory": self.memory, "saved": [x["id"] for x in self.lessons_saved], "used": self.lessons_used},
            "done_when": [{"item": i, "criterion": c,
                           "pass": next((r["pass"] for r in (last or {}).get("results", []) if r.get("item") == i), None)}
                          for i, c in enumerate((self.goal or {}).get("done_when") or [], 1)],
            "route_check_violations": [{"agent": e["agent"], "detail": e["detail"], "msg": e["msg"], "cycle": e["cycle"]}
                                       for e in self.events if e["type"] == "redirect"]})

    def _review(self, metrics):
        """One extra model call, outside J2: a reviewer reads the run and writes learnings. Its scores are judgment."""
        roles = []
        for name in ("team.md", "identity.md", "adaptation.md", "priority.md", "coordination.md", "audit.md",
                     "builder.md"):
            path = os.path.join(J2_DIR, name)
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    roles.append(f"### {name}\n{f.read().strip()}")

        def mock():
            c = metrics["conflicts"]
            return json.dumps({
                "verdict": f"Mock run: {metrics['outcome']}",
                "agents": {fn: {"score": 4 if a["redirects"] + a["invalid_moves"] == 0 else 3,
                                "note": f"{a['turns']} turns, {a['redirects']} redirects, {a['invalid_moves']} invalid moves"}
                           for fn, a in metrics["agents"].items()},
                "went_well": [f"{c['total']} conflict(s): {c['settled_by_agents']} settled by the agents, "
                              f"{c['resolved_by_identity']} by Identity, {c['asked_requester']} needed the Requester."],
                "problems": [f"{sum(a['redirects'] for a in metrics['agents'].values())} illegal route pick(s) were redirected."],
                "learnings": ["Mock replies are scripted, so these learnings only show the report works."]})
        if self.calls and DELAY:
            time.sleep(DELAY)
        self.calls += 1
        raw = llm.ask(
            "You review one test run of J2, a department of AI agents with strict roles (role files below). You are not "
            "part of the department. Judge from the evidence only: the code-counted metrics, the event log and the chat. "
            "Cite chat message ids like [12]. Score each agent 1-5 on staying in its role and moving the goal forward. "
            "Learnings are about J2's design and about this test system: what to change, keep or test next, each tied to "
            "evidence. Say so when the evidence is thin. Plain English, short items, no hype.\n\n"
            "## Reply format (required)\n" + self.REVIEW_FMT + "\n\n## Role files\n" + "\n\n".join(roles),
            f"METRICS:\n{json.dumps(metrics, ensure_ascii=False)}\n\nEVENTS:\n{json.dumps(self.events, ensure_ascii=False)}"
            f"\n\nCHARTER:\n{json.dumps(self.goal, ensure_ascii=False)}\n\nCHAT:\n{self.chat_view()}",
            mock, max_tokens=2000, effort="high", json_mode=True)
        try:
            return llm.extract_json(raw)
        except ValueError:
            return {"verdict": "The reviewer's reply wasn't valid JSON.", "raw": raw[:2000]}

    def _make_report(self, review=True):
        """Metrics always; the reviewer call only when the run ends (not on every pause for the Requester)."""
        metrics = self._metrics()
        self.thinking = None
        try:
            review = self._review(metrics) if review else {"verdict": "Paused for the Requester; the reviewer runs "
                                                                      "when the run ends."}
        except Exception as e:  # noqa: BLE001  the metrics are still worth saving
            review = {"verdict": f"Reviewer call failed: {type(e).__name__}: {str(e)[:200]}"}
        metrics["ai_calls"] = self.calls
        self.report = {"metrics": metrics, "review": review, "events": self.events,
                       "made": time.strftime("%Y-%m-%d %H:%M:%S")}
        self.save("report.json", self.report)
        with open(os.path.join(self.dir, "report.md"), "w", encoding="utf-8") as f:
            f.write(self._report_md())

    def _report_md(self):
        m, r = self.report["metrics"], self.report["review"]
        n, cf = m["negotiation"], m["conflicts"]
        out = [f"# J2 run report: {self.run_id}", "", f"Brief: {m['brief']}", "",
               f"**Outcome:** {m['outcome']}", f"**Reviewer verdict:** {r.get('verdict', '')}", "",
               "## Measured (counted by code)",
               f"- {m['ai_calls']} AI calls, {m['cycles']} cycles, {m['minutes']} min, model {m['model'] or 'mock'}",
               f"- Budget {m['budget']['spent']}/{m['budget']['total']} (started {m['budget']['start']}, "
               f"{len(m['budget']['raises'])} raise(s) approved by the Requester, cap {m['budget']['cap']}; rate card "
               f"{'on' if m['budget']['rate_card'] else 'off'}), {m['site_versions']} site versions, final site "
               f"{m['site_bytes'] / 1000:.0f} KB",
               f"- Negotiation: {n['proposals']} proposals, {n['grants']} GRANT / {n['counters']} COUNTER / "
               f"{n['refuses']} REFUSE ({n['refuses_converted_by_code']} converted by code), {n['parks']} parked",
               f"- Conflicts {cf['total']}: {cf['settled_by_agents']} settled by the agents, {cf['resolved_by_identity']} "
               f"resolved by Identity from the charter, {cf['asked_requester']} needed the Requester",
               f"- Questions to the Requester {m['requester_questions']['total']} {m['requester_questions']['by_kind']}",
               f"- Validator refusals {m['validator_refusals']} (role {m['role_refusals']}), "
               f"limit failures {m['limit_failures']}, warnings {m['warnings']}", "",
               "| Agent | Turns | Redirects | Invalid moves | Reviewer score | Note |", "|---|---|---|---|---|---|"]
        for fn, a in m["agents"].items():
            sc = (r.get("agents") or {}).get(fn) or {}
            out.append(f"| {NAMES.get(fn, fn)} | {a['turns']} | {a['redirects']} | {a['invalid_moves']} | "
                       f"{sc.get('score', '')} | {str(sc.get('note', '')).replace('|', '/')} |")
        out += ["", "## Conflicts (full log in conflicts.json)"] + (
            [f"- {c['id']} (cycle {c['cycle']}, {c['topic']}): {' vs '.join(NAMES[x] for x in c['between'])}, "
             f"{c['attempts']} attempt(s), " + ("escalated to Identity, " if c["escalated"] else "")
             + f"resolved by {c['resolved_by']}"
             + (f"; asked the Requester \"{c['user_question']}\", answer \"{c['user_answer']}\"" if c["user_question"] else "")
             + f". Outcome: {c['outcome']}" for c in cf["list"]] or ["- None"])
        out += ["", "## Audit by cycle"] + [f"- Cycle {a['cycle']}, v{a['version']}: {a['pass']} pass, {a['warn']} warn, "
                                             f"{a['fail']} fail; mechanical: "
                                             + ("not run" if not a.get("mechanical_ran") else
                                                ", ".join(a["mechanical"]) or "clean") for a in m["audits"]]
        for title, k in (("What went well", "went_well"), ("Problems", "problems"), ("Learnings", "learnings")):
            out += ["", f"## {title} (reviewer)"] + [f"- {x}" for x in r.get(k) or []]
        return "\n".join(out) + "\n"
