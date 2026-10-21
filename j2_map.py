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
NODE_KINDS = ("person", "function", "engine", "work", "know")      # v1 draws person, engine and work
EDGE_KINDS = ("handoff", "step", "speaks_to", "draws_on")           # v1 draws handoff and step
STATUSES = ("filed", "running", "waiting_on_you", "fault", "left_open", "not_made", "idle")
WORDS = {"filed": "filed and checked", "running": "running now", "waiting_on_you": "waiting on you", "fault": "fault",
         "left_open": "left open", "not_made": "not made", "idle": "idle"}
STEP_VERB = {"doc-sections": "Write", "site-parts": "Build", "send": "Send"}      # what the workflows of that kind do
LEGEND = [
    {"key": "function", "label": "function", "drawn": False},
    {"key": "engine", "label": "engine", "drawn": True},
    {"key": "work", "label": "work with its version", "drawn": True},
    {"key": "filed", "label": "filed and checked", "drawn": True},
    {"key": "running", "label": "running now", "drawn": True},
    {"key": "left_open", "label": "left open", "drawn": True},
    {"key": "waiting_on_you", "label": "waiting on you", "drawn": True},
    {"key": "fault", "label": "fault", "drawn": True},
    {"key": "not_made", "label": "not made", "drawn": True},
    {"key": "handoff", "label": "hand-off", "drawn": True},
    {"key": "speaks_to", "label": "speaks to", "drawn": False},
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
    # steps: what turned one box into the next (named by what its workflows do), with counts
    edges, work = [], [n for n in nodes if n["kind"] == "work"]
    steps = []
    for a, b in zip(work, work[1:]):
        ats = b.get("_atoms") or []
        ch = _checks(ats)
        wf = len(b["workflows"])
        detail = (f"{wf} workflow{'s' if wf != 1 else ''} · {ch['passed']} of {ch['run']} checks passed" if wf else "not recorded")
        sid = f"step:{a['id'].split(':')[1]}>{b['id'].split(':')[1]}"
        steps.append({"id": sid, "kind": "engine", "row": "work", "label": STEP_VERB.get(b.get("template"), "Make"), "status": b["status"],
                      "version": None, "detail": detail, "file": None, "workflows": b["workflows"], "tag": None, "color": None})
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
    if state == "not recorded":
        nr.append("how the run ended (summary.json)")
    # interleave the steps with the boxes in drawing order
    order = []
    for i, n in enumerate(work):
        order.append(n)
        if i < len(steps):
            order.append(steps[i])
    out_nodes = [person] + order
    for n in out_nodes:
        n.pop("_atoms", None)
        n.pop("_order", None)
        n.pop("template", None)
    ch = _checks(atoms)
    return {"schema": SCHEMA, "run": os.path.basename(d), "live": bool(live),
            "status": {"state": state, "state_status": state_status, "checks": ch},
            "nodes": out_nodes, "edges": edges + handoffs, "legend": LEGEND, "built_from": built_from,
            "not_recorded": list(dict.fromkeys(nr + ["which function made each step (Functions row, later version)",
                                                     "what the work draws on (Knows row, later version)"]))}


def write(d):
    """map.json beside atoms.json (additive)."""
    m = build(d)
    with open(os.path.join(d, "map.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
    return m
