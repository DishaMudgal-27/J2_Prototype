"""The Map of a run (schema map/1): the work in order, drawn from what the run recorded. Version 1 has the Requester and
the Work row (artifacts with version and status, the steps between them, hand-offs); the Functions and Knows rows are
later versions (their node kinds are in the schema, nothing is drawn or invented for them).

build(run_dir, live=None) is code only, no model call: it reads artifacts.json (or scans the folder as j2_artifacts does),
atoms.json (atom/1), summary.json, goal.json and chat.jsonl. live is the running run's own state, so a run in progress
shows its current statuses: {"snapshot": run.snapshot(), "stages": [...], "stage_words": {...}}. Anything the run did not
record is listed in not_recorded and shown as "not recorded"; nothing is guessed. map.json is written beside atoms.json.
"""
import json
import os
import re

import j2_artifacts as A

SCHEMA = "map/1"
NODE_KINDS = ("person", "function", "engine", "work", "know")      # v2 draws person, function, engine and work
EDGE_KINDS = ("handoff", "step", "speaks_to", "draws_on", "asks", "uses")   # asks/uses: the message board (board/1),
                                                                            # between deliverables only (J2_BOARD=1)
STATUSES = ("filed", "running", "waiting", "waiting_on_you", "fault", "left_open", "not_made", "idle")
WORDS = {"filed": "filed and checked", "running": "running now", "waiting_on_you": "waiting on you", "waiting": "waiting", "fault": "fault",
         "left_open": "left open", "not_made": "not made", "idle": "idle"}
FUNCS = ("identity", "adaptation", "priority", "coordination", "audit")
NAMES = {"identity": "Identity", "adaptation": "Adaptation", "priority": "Priority", "coordination": "Coordination", "audit": "Audit"}
# the existing tab that shows each function's work (declared here; a box links to it)
FN_TAB = {"identity": "charter", "adaptation": "workflows", "priority": "conflicts", "coordination": "timeline", "audit": "audit"}
STEP_VERB = {"doc-sections": "Write", "site-parts": "Build", "send": "Send"}      # what the workflows of that kind do
LEGEND = [
    {"key": "function", "label": "function", "drawn": True},
    {"key": "engine", "label": "engine", "drawn": True},
    {"key": "work", "label": "work with its version", "drawn": True},
    {"key": "filed", "label": "filed and checked", "drawn": True},
    {"key": "running", "label": "running now", "drawn": True},
    {"key": "left_open", "label": "left open", "drawn": True},
    {"key": "waiting_on_you", "label": "waiting on you", "drawn": True},
    {"key": "fault", "label": "fault", "drawn": True},
    {"key": "not_made", "label": "not made", "drawn": True},
    {"key": "handoff", "label": "hand-off", "drawn": True},
    {"key": "speaks_to", "label": "speaks to", "drawn": True},
    {"key": "asks", "label": "asks (board)", "drawn": True},
    {"key": "uses", "label": "uses (board)", "drawn": True},
]


def _read(d, name, default=None):
    try:
        with open(os.path.join(d, name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _jsonl(d, name):
    try:
        with open(os.path.join(d, name), encoding="utf-8") as f:
            return [json.loads(x) for x in f if x.strip()]
    except (OSError, ValueError):
        return []


def _num(wid):
    m = re.search(r"(\d+)", str(wid))
    return int(m.group(1)) if m else 10 ** 6


def empty(why="nothing to draw yet"):
    return {"schema": SCHEMA, "run": None, "live": False, "status": {"state": "not started", "state_status": "idle",
            "checks": {"passed": 0, "run": 0}}, "nodes": [], "edges": [], "legend": LEGEND, "built_from": [],
            "not_recorded": [why]}


def _status(atoms, ended, has_files=True):
    """A work box's status from its atoms (atom closed = filed; open = running now, or left open once the run ended;
    verify_failed = fault; abandoned = not made)."""
    st = [a.get("status") for a in atoms]
    if not st:
        return "filed" if has_files else "not_made"      # a file with no atoms recorded: it exists, nothing contradicts it
    if "verify_failed" in st:
        return "fault"
    if all(s == "closed" for s in st):
        return "filed"
    if all(s == "abandoned" for s in st):
        return "not_made"
    return "left_open" if ended else "running"


def _checks(atoms):
    c = [x for a in atoms for x in a.get("verification") or [] if x.get("met") is not None]
    return {"passed": sum(1 for x in c if x["met"] is True), "run": len(c)}


def _state_line(d, live, atoms, req_waiting):
    """(text, status) for the top pill: who is running now, or how the run ended."""
    if live:
        snap = live.get("snapshot") or {}
        if snap.get("paused"):
            return "Waiting on you", "waiting_on_you"
        work = [x for x in snap.get("lanes") or [] if x.get("status") == "working"]
        if work and snap.get("status") == "running":
            return f"{work[0]['name']} running", "running"
        return {"running": "Running", "waiting": "Waiting"}.get(snap.get("status"), "Idle"), "idle"
    s = _read(d, "summary.json") or {}
    if req_waiting:
        return "Waiting on you", "waiting_on_you"
    word = {"done": "Done", "done_with_open_items": "Done with open items", "stopped": "Stopped", "crashed": "Crashed"}.get(s.get("status"))
    return (word, "idle") if word else ("not recorded", "idle")


def _functions(chat, calls, snap, requester_waiting, nr):
    """The five function boxes. A running run: the lanes (working, waiting, blocked, idle). A finished one: the last known
    state from the chat, never "running": the line says what the function last did. Calls, seconds and tokens come from
    the call log."""
    lanes = {x["id"]: x for x in (snap or {}).get("lanes") or []}
    out = []
    for fn in FUNCS:
        mine = [c for c in calls if c.get("fn") == fn]
        said = [m for m in chat if m.get("who") == fn]
        last = (said[-1].get("text") or "")[:140] if said else ""
        node = {"id": f"fn:{fn}", "kind": "function", "row": "functions", "label": NAMES[fn], "status": "idle", "version": None,
                "tag": None, "color": f"--{fn}", "file": None, "workflows": [], "tab": FN_TAB[fn], "wait_on": None,
                "calls": len(mine), "seconds": round(sum(c.get("seconds") or 0 for c in mine), 1),
                "tokens": {"input": sum((c.get("tokens") or {}).get("input", 0) for c in mine),
                           "output": sum((c.get("tokens") or {}).get("output", 0) for c in mine)}}
        if snap is not None and fn in lanes:
            ln = lanes[fn]
            on = ln.get("on")
            node["status"] = {"working": "running", "waiting": "waiting", "blocked": "fault"}.get(ln.get("status"), "idle")
            if node["status"] == "waiting":
                node["wait_on"] = on
                if on == "Requester":      # "waiting on you" only while a question to the Requester is open (the same source as Needs you)
                    node["status"], node["wait_on"] = ("waiting_on_you", "you") if requester_waiting else ("idle", None)
            doing = (ln.get("doing") or "")[:140]
            node["detail"] = doing if node["status"] != "idle" else (f"last seen: {doing or last}" if (doing or last) else "no message recorded")
        else:
            if fn == "identity" and requester_waiting:
                node["status"], node["wait_on"] = "waiting_on_you", "you"
            node["detail"] = f"last seen: {last}" if last else "no message recorded"
        if not said and not snap:
            nr.append(f"what {NAMES[fn]} did (chat)")
        out.append(node)
    return out


def _work_lines(d, work, calls, docs, nr):
    """speaks_to edges from a function to a work box it acted on, from recorded data only: Identity to the Charter
    (goal.json); each function to a document by its AI calls in the range documents.json recorded; Audit to every box that
    has an audit in stage-*.json. Nothing else is drawn: the rest is listed as not recorded, never guessed."""
    audits = {}
    for f in sorted(os.listdir(d)):
        m = re.fullmatch(r"stage-(\w+)\.json", f)
        if m:
            audits[m.group(1)] = len((_read(d, f, {}) or {}).get("audits") or [])
    site = next((n for n in work if n["id"] == "work:website" and n.get("file")), None)
    if site and "website" not in audits and isinstance(_read(d, "audits.json"), list):      # a plain site run has no stage file: its audits are audits.json
        audits["website"] = len(_read(d, "audits.json"))
    out = []
    for n in work:
        if n["kind"] != "work" or n["status"] == "not_made":
            continue
        k = n["id"].split(":")[1]
        got = {}
        if k == "charter":
            out.append({"from": "fn:identity", "to": n["id"], "kind": "speaks_to", "label": "wrote the charter", "n": None, "basis": "recorded"})
            continue
        rng = (docs.get(k) or {}).get("calls")
        if rng and calls:
            got = {fn: sum(1 for c in calls if c.get("fn") == fn and rng["from"] <= c.get("id", 0) <= rng["to"]) for fn in FUNCS}
            got = {fn: c for fn, c in got.items() if c}
            out += [{"from": f"fn:{fn}", "to": n["id"], "kind": "speaks_to", "label": "calls", "n": c, "basis": "recorded"} for fn, c in got.items()]
        if audits.get(k) and "audit" not in got:
            out.append({"from": "fn:audit", "to": n["id"], "kind": "speaks_to", "label": "audits", "n": audits[k], "basis": "recorded"})
            got["audit"] = audits[k]
        if not rng:      # no call range: only an audit count is recorded, or nothing
            nr.append(f"which other function worked on {n['label']} (only Audit is recorded)" if got else f"which function worked on {n['label']}: not recorded")
    return out


def _speaks(chat, have):
    """speaks_to edges with message counts: the Requester to Identity (their messages), Identity to the Requester
    (messages addressed to them), and function to function (chat who and next)."""
    edges, n = [], {}
    you = sum(1 for m in chat if m.get("who") == "user")
    back = sum(1 for m in chat if m.get("who") == "identity" and m.get("to_user"))
    for a, b, c in (("person:requester", "fn:identity", you), ("fn:identity", "person:requester", back)):
        if c:
            edges.append({"from": a, "to": b, "kind": "speaks_to", "label": None, "n": c, "basis": "recorded"})
    for m in chat:
        a, b = m.get("who"), m.get("next")
        if a in FUNCS and b in FUNCS and a != b:
            n[(a, b)] = n.get((a, b), 0) + 1
    edges += [{"from": f"fn:{a}", "to": f"fn:{b}", "kind": "speaks_to", "label": None, "n": c, "basis": "recorded"}
              for (a, b), c in sorted(n.items(), key=lambda x: (FUNCS.index(x[0][0]), FUNCS.index(x[0][1])))]
    return edges


def build(d, live=None):
    if not d or not os.path.isdir(d):
        return empty("run not found")
    types = A.load_types()
    by = {t["name"]: t for t in types["types"]}
    nr, built_from, ended = [], [], not live
    snap = (live or {}).get("snapshot") or {}
    # deliverable rows: the run's artifacts.json when it has one (a finished run), else a fresh scan of the folder
    saved = None if live else _read(d, "artifacts.json")
    rows = [r for r in (saved["rows"] if saved else A.rows(d, types)) if r["kind"] == "type"]
    built_from.append("artifacts.json" if saved else "folder scan (types.json)")
    if not saved and not live:
        nr.append("artifacts.json (rows rebuilt from the folder)")
    atoms = list(snap.get("atoms_v1", {}).values()) if live else None
    if atoms is None:
        atoms = A._atoms(d)
        built_from.append("atoms.json" if os.path.exists(os.path.join(d, "atoms.json")) else "workflows.json (atoms rebuilt)")
        if not os.path.exists(os.path.join(d, "atoms.json")):
            nr.append("atoms.json (atoms rebuilt from workflows.json)")
    else:
        built_from.append("live run")
    by_wf = {}
    for a in atoms:
        by_wf.setdefault(a["workflow"], []).append(a)
    nodes, handoffs = [], []
    # the charter: Identity's, from goal.json
    if os.path.isfile(os.path.join(d, "goal.json")):
        nodes.append({"id": "work:charter", "kind": "work", "row": "work", "label": "Charter", "tag": "Charter", "color": "--charter",
                      "status": "filed", "version": None, "detail": "the plan every workflow reads", "file": "goal.json",
                      "workflows": [], "_order": -1})
        nr.append("version of Charter")
    # one node per deliverable the run built
    for r in rows:
        t = by[r["type"]]
        mine = [a for w in r["workflows"] for a in by_wf.get(w, [])]
        nodes.append({"id": f"work:{r['type']}", "kind": "work", "row": "work", "label": t["label"], "tag": t["tag"], "color": t["color"],
                      "status": _status(mine, ended), "version": r.get("version"),
                      "detail": f"{len(mine)} work atoms" if mine else "no work atoms recorded", "file": r["file"],
                      "workflows": r["workflows"], "template": t["workflow"]["template"], "_atoms": mine,
                      "_order": min((_num(w) for w in r["workflows"]), default=10 ** 5)})
        if r.get("version") is None:
            nr.append(f"version of {t['label']}")
    # a send deed: atoms whose output has form send (deeds are not in types.json yet)
    for wid, ats in sorted(by_wf.items(), key=lambda x: _num(x[0])):
        sends = [a for a in ats if any(o.get("form") == "send" for o in a.get("output") or [])]
        if sends:
            nodes.append({"id": f"work:{wid}", "kind": "work", "row": "work", "label": sends[0].get("name") or "Send", "tag": "Send",
                          "color": "--other", "status": _status(sends, ended), "version": None,
                          "detail": "; ".join(a.get("notes") or "" for a in sends).strip() or "one deed", "file": "receipts.jsonl",
                          "workflows": [wid], "template": "send", "_atoms": sends, "_order": _num(wid)})
            nr.append(f"version of {sends[0].get('name') or 'send'}")
    # planned but not built yet: a live run's stage list (or a saved run's) names what is still to come
    stages = list((live or {}).get("stages") or ((_read(d, "summary.json") or {}).get("design_documents") or {}).get("stages") or [])
    have = {n["id"] for n in nodes}
    words = (live or {}).get("stage_words") or {}
    late = 0
    for k in stages:
        if k in by and f"work:{k}" not in have:
            late += 1
            nodes.append({"id": f"work:{k}", "kind": "work", "row": "work", "label": by[k]["label"], "tag": by[k]["tag"], "color": by[k]["color"],
                          "status": "not_made", "version": None, "detail": "not started", "file": None, "workflows": [],
                          "template": by[k]["workflow"]["template"], "_atoms": [], "_order": 10 ** 5 + late})
        elif k not in by and k in words and not any(n["tag"] == "Send" for n in nodes):
            late += 1
            nodes.append({"id": f"work:{k}", "kind": "work", "row": "work", "label": words[k][0].upper() + words[k][1:], "tag": "Send",
                          "color": "--other", "status": "not_made", "version": None, "detail": "not started", "file": None,
                          "workflows": [], "template": "send", "_atoms": [], "_order": 10 ** 5 + late})
    nodes.sort(key=lambda n: n["_order"])
    # steps: what turned one box into the next (named by what its workflows do), with counts. The documents and the site are the
    # trunk, in order. A deed (a send) is a side job: its step starts at the document it was built from (its recorded edge, else the
    # last trunk box before it), so it never sits between two documents and the site's step takes the last document as its input.
    edges, work = [], [n for n in nodes if n["kind"] == "work"]
    trunk = [n for n in work if n.get("template") != "send"]
    made_by = {a["id"]: n["id"] for n in work for a in n.get("_atoms") or []}
    pairs = list(zip(trunk, trunk[1:]))
    for n in work:
        n["lane"] = "trunk" if n in trunk else "branch"
        if n in trunk:
            continue
        src = next((made_by.get(e.get("atom")) for a in n.get("_atoms") or [] for e in a.get("depends_on") or []
                    if made_by.get(e.get("atom")) in {t["id"] for t in trunk}), None)
        parent = next((t for t in trunk if t["id"] == src), None) or next((t for t in reversed(trunk) if t["_order"] <= n["_order"]), None) \
            or (trunk[-1] if trunk else None)
        if parent:
            pairs.append((parent, n))
    steps = []
    for a, b in pairs:
        ats = b.get("_atoms") or []
        ch = _checks(ats)
        wf = len(b["workflows"])
        detail = (f"{wf} workflow{'s' if wf != 1 else ''} · {ch['passed']} of {ch['run']} checks passed" if wf else "not recorded")
        sid = f"step:{a['id'].split(':')[1]}>{b['id'].split(':')[1]}"
        steps.append({"id": sid, "kind": "engine", "row": "work", "label": STEP_VERB.get(b.get("template"), "Make"), "status": b["status"],
                      "version": None, "detail": detail, "file": None, "workflows": b["workflows"], "tag": None, "color": None, "lane": b["lane"]})
        edges += [{"from": a["id"], "to": sid, "kind": "step", "label": None, "n": wf, "basis": "recorded" if wf else "declared"},
                  {"from": sid, "to": b["id"], "kind": "step", "label": None, "n": wf, "basis": "recorded" if wf else "declared"}]
        if not wf:
            nr.append(f"workflows of {b['label']}")
    # hand-offs: recorded atom edges between boxes, then declared dependencies (types.json) not already seen, then the charter
    owner = {a["id"]: n["id"] for n in work for a in n.get("_atoms") or []}
    seen = set()
    for n in work:
        for a in n.get("_atoms") or []:
            for e in a.get("depends_on") or []:
                src = owner.get(e["atom"])
                if src and src != n["id"] and (src, n["id"]) not in seen:
                    seen.add((src, n["id"]))
                    handoffs.append({"from": src, "to": n["id"], "kind": "handoff", "label": e.get("why"), "n": 1, "basis": "recorded"})
    ids = {n["id"] for n in work}
    for n in work:
        t = by.get(n["id"].split(":")[1])
        for dep in (t or {}).get("depends_on", []):
            if f"work:{dep}" in ids and (f"work:{dep}", n["id"]) not in seen:
                seen.add((f"work:{dep}", n["id"]))
                handoffs.append({"from": f"work:{dep}", "to": n["id"], "kind": "handoff", "label": "declared dependency", "n": 1, "basis": "declared"})
    if "work:charter" in ids:
        roots = [n for n in work if n["id"] != "work:charter" and not any(h["to"] == n["id"] for h in handoffs)]
        for n in roots[:1]:
            handoffs.append({"from": "work:charter", "to": n["id"], "kind": "handoff", "label": "built from the charter", "n": 1, "basis": "declared"})
    # message board (board/1): an "asks" line from the asking deliverable to the answering one, an "uses" line from
    # each reuser's deliverable to it, labelled with the board id. Recorded data only; a question and its reuse inside
    # the same deliverable (the usual case for one website) have no line to draw, same as any self-referencing edge.
    # A question a function asked (asked_by_role "function") has no deliverable on the asking side, so no line
    # either; the Board tab lists every entry whoever asked it.
    board = ((live or {}).get("board") if live else _read(d, "board.json")) or {}
    board_edges = []
    for e in board.get("entries") or []:
        src, dst = owner.get(e.get("atom")), owner.get(e.get("to"))
        if src and dst and src != dst and e.get("status") == "answered":
            board_edges.append({"from": src, "to": dst, "kind": "asks", "label": e["id"], "n": None, "basis": "recorded"})
            for ra in e.get("used_by") or []:
                rsrc = owner.get(ra)
                if rsrc and rsrc != dst:
                    board_edges.append({"from": rsrc, "to": dst, "kind": "uses", "label": e["id"], "n": None, "basis": "recorded"})
    # the Requester
    chat = _jsonl(d, "chat.jsonl") if not live else (snap.get("chat") or [])
    mine = [m for m in chat if m.get("who") == "user"]
    last = chat[-1] if chat else {}
    waiting = bool(snap.get("paused")) if live else bool(last.get("pause") and last.get("who") == "identity")
    person = {"id": "person:requester", "kind": "person", "row": "people", "label": "You",
              "status": "waiting_on_you" if waiting else "idle", "version": None, "tag": None, "color": "--user", "file": None,
              "detail": f"{len(mine)} message{'s' if len(mine) != 1 else ''} from you" if chat else "not recorded", "workflows": []}
    if not chat:
        nr.append("chat (messages from the Requester)")
    state, state_status = _state_line(d, live, atoms, waiting)
    calls = (snap.get("call_log") if live else _jsonl(d, "calls.jsonl")) or []
    if not calls and not live:
        nr.append("AI calls per function (calls.jsonl)")
    funcs = _functions(chat, calls, snap if live else None, waiting, nr)
    speaks = _speaks(chat, bool(chat))
    docs = _read(d, "documents.json", {}) or {}
    for st in steps:      # which functions made a step: only where documents.json recorded the call range
        rng = (docs.get(st["id"].split(">")[1]) or {}).get("calls")
        if rng and calls:
            per = {fn: sum(1 for c in calls if c.get("fn") == fn and rng["from"] <= c.get("id", 0) <= rng["to"]) for fn in FUNCS}
            st["made_by"] = {"calls": rng, "functions": {fn: n for fn, n in per.items() if n}, "basis": "recorded"}
        else:
            st["made_by"] = None
    lines = _work_lines(d, work, calls, docs, nr)
    if state == "not recorded":
        nr.append("how the run ended (summary.json)")
    # drawing order: each trunk box, then the side jobs that leave it (their step, then the deed), then the step to the next trunk box
    order, into = [], {st["id"].split(">")[1]: st for st in steps}
    for i, n in enumerate(trunk):
        if i:
            order.append(into[n["id"].split(":")[1]])
        order.append(n)
        for b in [x for x in work if x["lane"] == "branch"]:
            st = into.get(b["id"].split(":")[1])
            if st and st["id"].split(">")[0] == "step:" + n["id"].split(":")[1]:
                order += [st, b]
    out_nodes = [person] + funcs + order
    for n in out_nodes:
        n.pop("_atoms", None)
        n.pop("_order", None)
        n.pop("template", None)
    ch = _checks(atoms)
    return {"schema": SCHEMA, "run": os.path.basename(d), "live": bool(live),
            "status": {"state": state, "state_status": state_status, "checks": ch},
            "nodes": out_nodes, "edges": edges + handoffs + speaks + lines + board_edges, "legend": LEGEND, "built_from": built_from,
            "not_recorded": list(dict.fromkeys(nr + ["messages to and from workflow agents (W-n) are not drawn",
                                                     "what the work draws on (Knows row, later version)"]))}


def write(d):
    """map.json beside atoms.json (additive)."""
    m = build(d)
    with open(os.path.join(d, "map.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
    return m
