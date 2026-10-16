"""atom/1: one simple, standard shape for a work atom (docs/atom-schema.md, docs/atom-schema.json).

atom_view adapts a stored atom (no stored field is renamed or changed); validate_atom and validate_views give warnings
only: they never change an outcome, a prompt or a retry. Pure functions, no model call.
"""
SCHEMA = "atom/1"
STATUSES = ("open", "closed", "verify_failed", "abandoned")
KINDS = ("doc", "code", "page", "test", "plan", "skill", "app")      # an open list: unknown kinds are recorded, never rejected
EFFECT_KINDS = ("behaviour", "fetch", "send")      # behaviour has scope self; fetch and send are external and not produced yet
FINAL_KINDS = ("page", "doc")      # outputs that are part of the deliverable itself
MAX_ATTEMPTS = 3
ARTIFACT_CHECKS = {"file-exists": "exists", "element-count": "exists", "grep-count": "exists", "heading-present": "exists",
                   "section-not-empty": "exists", "facts-present": "matches the defined output",
                   "lld-slice": "matches the defined output"}      # anything else: "valid under the rules"
EFFECT_CHECKS = {"behavior-steps": "occurred"}      # "observed result" and "within limits" are defined, not produced yet


def atom_status(atom, wf=None, ended=False):
    """One of STATUSES from today's names. atom: passed, failed (after every attempt, and also after each one that will be
    retried), escalated, could not run, or none yet. wf: its workflow's status (registered, held, running, done, failed,
    unfunded). ended: the run is over, so what was never built is abandoned."""
    s, ws = atom.get("status"), (wf or {}).get("status")
    if s == "passed":
        return "closed"
    if s == "escalated" or (s == "failed" and (ws != "running" or (atom.get("attempts") or 0) >= MAX_ATTEMPTS)):
        return "verify_failed"
    if ws == "unfunded" or (ended and not s and ws not in (None, "done")):
        return "abandoned"
    return "open"      # none yet, retrying after a failed attempt, or a check that could not run


def atom_view(atom, wf=None, edges=None, ended=False):
    """The atom/1 view of a stored atom. wf: its workflow (for the name); edges: [{atom, why}] it depends on."""
    ag, a = atom.get("agent_output") or {}, atom
    wid = str(a["id"]).split(".")[0]
    name = (wf or {}).get("name") or ag.get("section_names", [None])[0] or a["id"]
    out, ver = _outputs(a, ag), []
    for r in a.get("results") or []:
        kind = "effect" if r.get("type") in EFFECT_CHECKS else "artifact"
        ver.append({"check": EFFECT_CHECKS[r["type"]] if kind == "effect" else ARTIFACT_CHECKS.get(r.get("type"), "valid under the rules"),
                    "applies_to": _applies_to(kind, r, out), "method": f"{r.get('type')}: {r.get('check')}",
                    "met": r.get("pass"), "evidence": r.get("evidence")})
    details = {k: ag[k] for k in ("selectors", "ids", "section", "anchor") if ag.get(k)}
    els = [x for x in a.get("expected_output") or [] if isinstance(x, dict) and x.get("kind") == "element"]
    if els:
        details["elements"] = [x.get("target") for x in els]
    if any(o["type"] == "effect" for o in out):
        details["scope"] = "self"
    return {"schema": SCHEMA, "id": a["id"], "workflow": wid, "name": name, "owner": (a.get("how") or {}).get("agent"),
            "status": atom_status(a, wf, ended), "attempt": a.get("attempts") or ag.get("attempt"),
            "goal": a.get("goal"), "how": a.get("how"), "constraints": a.get("constraints") or [],
            "context": a.get("context") or [], "defined_output": a.get("expected_output") or [],
            "verification": ver, "output": out, "depends_on": [dict(e) for e in edges or []], "used_by": [],
            "notes": (a.get("human_output") or {}).get("text") or "", "details": details}


def _outputs(a, ag):
    """Artifacts: the section (or document section) the atom wrote and the files it is in. Effects: each behaviour step
    check run on the page (kind "behaviour", scope self), its ref the receipt."""
    out, files = [], ag.get("files") or []     # a built website section is a "page" (ref: its anchor); PRD, HLD, LLD are "doc"
    doc = ag.get("kind") == "doc"
    if ag:
        head = next((x.get("target") for x in a.get("expected_output") or [] if isinstance(x, dict) and x.get("kind") == "heading"), None)
        ref = f"{ag.get('file')}#{head or ag.get('section')}" if doc else f"{files[-1] if files else 'site/index.html'}#{ag['anchor']}" \
            if ag.get("anchor") else None
        if ref:
            out.append({"name": (ag.get("section_names") or [a["id"]])[0], "type": "artifact",
                        "kind": "doc" if doc else "page", "ref": ref})
        out += [{"name": f, "type": "artifact", "kind": "doc" if f.endswith((".md", ".docx")) else "page" if f.endswith(".html")
                 else "file", "ref": f} for f in files]
    out += [{"name": r.get("check"), "type": "effect", "kind": "behaviour", "ref": ag.get("receipt") or f"{a['id']}:{r.get('attempt')}"}
            for r in a.get("results") or [] if r.get("type") in EFFECT_CHECKS]
    return out


def _applies_to(kind, r, out):
    if kind == "effect":
        return next((o["name"] for o in out if o["type"] == "effect" and o["name"] == r.get("check")), r.get("check"))
    t = r.get("target")
    return next((o["name"] for o in out if o["kind"] in FINAL_KINDS), None) or (", ".join(map(str, t)) if isinstance(t, list) else str(t))


def link_views(views):
    """used_by: the exact inverse of depends_on (built here, never by an agent). Mutates and returns the views."""
    by = {v["id"]: v for v in views}
    for v in views:
        v["used_by"] = []
    for v in views:
        for e in v["depends_on"]:
            if e["atom"] in by:
                by[e["atom"]]["used_by"].append({"atom": v["id"], "why": e["why"]})
    return views


def dependency_edges(wf, workflows):
    """Edges from a workflow's declared dependencies (proposal ids), for a builder that was given the whole page and
    nothing can be attributed. Dependencies that name no workflow produce nothing."""
    ids = {w.get("proposal_id"): w for w in workflows}
    return [{"atom": a["id"], "why": f"its workflow depends on {ids[d].get('name')}"}
            for d in wf.get("dependencies") or [] if d in ids and ids[d] is not wf for a in ids[d].get("atoms") or []]


def run_views(workflows, given=None, ended=False):
    """(views, warnings) for a run. given: {workflow id: {"edges": [{atom, why}], "whole": bool}}, what each builder's
    prompt actually held (recorded by the run). Without a record, or with the whole page given and no attributable
    edge, edges come from workflow dependencies, else stay empty."""
    given, views = given or {}, []
    for w in workflows:
        g = given.get(w["id"]) or {}
        edges = g.get("edges") or (dependency_edges(w, workflows) if g.get("whole", True) else [])
        for a in w.get("atoms") or []:
            views.append(atom_view(a, w, [e for e in edges if e["atom"] != a["id"]], ended))
    link_views(views)
    return views, validate_views(views)


def validate_atom(view, known=None):
    """Warnings for one view: an output item without a type, an edge to a missing atom (when known ids are given)."""
    out = [f"{view['id']}: output item {o.get('name')!r} has no type" for o in view.get("output") or [] if not o.get("type")]
    if known is not None:
        out += [f"{view['id']}: depends on {e['atom']}, which is not an atom of this run"
                for e in view.get("depends_on") or [] if e["atom"] not in known]
    return out


def validate_views(views):
    """Warnings for a run: dangling edges, missing types, cycles, outputs never used that are not final outputs."""
    known = {v["id"] for v in views}
    out = [w for v in views for w in validate_atom(v, known)]
    state, stack = {}, []

    def walk(i):
        state[i] = 1
        stack.append(i)
        for e in by[i]["depends_on"]:
            j = e["atom"]
            if j not in by:
                continue
            if state.get(j) == 1:
                out.append("cycle: " + " -> ".join(stack[stack.index(j):] + [j]))
            elif j not in state:
                walk(j)
        stack.pop()
        state[i] = 2
    by = {v["id"]: v for v in views}
    for i in by:
        if i not in state:
            walk(i)
    out += [f"{v['id']}: its output is never used and is not a final output" for v in views
            if v["output"] and not v["used_by"] and not any(o.get("kind") in FINAL_KINDS for o in v["output"])]
    return out
