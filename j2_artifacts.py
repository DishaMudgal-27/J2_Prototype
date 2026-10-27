"""Artifacts of a run, listed from artifacts/types.json (read-only; j2.py's flow does not read the list).

rows(run_dir) scans a run folder against the list: one row per deliverable the run built and per record file it kept.
write(run_dir) saves those rows as artifacts.json at the end of a run; listing(run_dir) reads that file, or scans an older
run that has none. Code only, no model call.
"""
import glob
import hashlib
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TYPES_PATH = os.path.join(HERE, "artifacts", "types.json")
OPEN = {"doc": "text", "data": "text", "page": "preview", "image": "image"}      # how the Artifacts tab shows a form
TEXT = {".md": "text/markdown", ".json": "application/json", ".jsonl": "text/plain", ".txt": "text/plain",
        ".html": "text/html", ".png": "image/png"}
MAX_BYTES = 2_000_000


def load_types():
    with open(TYPES_PATH, encoding="utf-8") as f:
        return json.load(f)


def _read(d, name, default=None):
    try:
        with open(os.path.join(d, name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _num(path):
    m = re.search(r"(\d+)", os.path.basename(path))
    return int(m.group(1)) if m else 0


def _stat(d, rel):
    p = os.path.join(d, rel)
    with open(p, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    return sha, time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(p)))


def _version_files(d, t, single):
    """[(version, path relative to the run)] of every saved build of a deliverable, oldest first, from the version
    files in site/: hld-v3.md, v3.html (a one-document run keeps plain names: v3.md)."""
    site = os.path.join(d, "site")
    if not os.path.isdir(site):
        return []
    if t["form"] == "page":
        pat = r"v(\d+)\.html"
    else:
        pat = rf"{t['name']}-v(\d+)\.md" + (r"|v(\d+)\.md" if single else "")
    out = [(int(next(g for g in m.groups() if g)), f"site/{f}")
           for f in os.listdir(site) for m in [re.fullmatch(pat, f)] if m]
    return sorted(out)


def _version(d, t, single):
    """The latest build of a deliverable, or None when it saved none."""
    ns = [n for n, _ in _version_files(d, t, single)]
    return max(ns) if ns else None


def _atoms(d):
    """The atom/1 views of a run: atoms.json, else built from the stored workflows (older runs)."""
    rows = (_read(d, "atoms.json", {}) or {}).get("atoms")
    if rows is None:
        import j2_schema
        rows = j2_schema.run_views(_read(d, "workflows.json", []) or [], ended=True)[0]
    return rows


def _board(d, atoms):
    """What the message board (board/1) changed and re-checked, per deliverable type: {type: {"changed_by": [Q-n],
    "rechecked_after": [Q-n]}}, from board.json only. Empty when the run has no board."""
    entries = (_read(d, "board.json", {}) or {}).get("entries") or []
    wf_of = {v["id"]: v.get("workflow") for v in atoms}
    out = {}
    for e in entries:
        up = e.get("artifact_update") or {}
        if up.get("doc"):
            out.setdefault(up["doc"], {}).setdefault("changed_by", []).append(e["id"])
            # the changed document itself: its own conditions and the owner's checks were re-run
            out[up["doc"]].setdefault("rechecked_after", []).append(e["id"])
        for x in e.get("impact") or []:
            wid = wf_of.get(x.get("atom"))
            if wid:
                out.setdefault(("_wf", wid), {}).setdefault("rechecked_after", []).append(e["id"])
    return out


def rows(d, types=None):
    """[{name, type, kind, form, file, deliverable, workflows, depends_on, version, sha256, time}] for a run folder,
    plus changed_by and rechecked_after when the message board changed or re-checked it."""
    types = types or load_types()
    if not d or not os.path.isdir(d):
        return []
    atoms, docs, out = _atoms(d), _read(d, "documents.json", {}) or {}, []
    board = _board(d, atoms)
    for t in types["types"]:
        files = [os.path.relpath(p, d) for p in sorted(glob.glob(os.path.join(d, t["file"])), key=_num)] \
            if "*" in t["file"] else [t["file"]] if os.path.isfile(os.path.join(d, t["file"])) else []
        wf = []
        if t["kind"] == "type":
            rx = re.compile(t["workflow"]["refs"])
            wf = sorted({v["workflow"] for v in atoms for o in v.get("output") or []
                         if o.get("verb") == "make" and rx.search(str(o.get("ref") or ""))}, key=_num)
        changed = sorted(set((board.get(t["name"]) or {}).get("changed_by") or []), key=_num)
        rechecked = sorted({q for w in wf for q in (board.get(("_wf", w)) or {}).get("rechecked_after") or []}
                           | set((board.get(t["name"]) or {}).get("rechecked_after") or []), key=_num)
        for rel in files:
            sha, when = _stat(d, rel)
            out.append({"name": t["label"] if len(files) == 1 or t["kind"] == "type" else
                        f"{t['label']} {os.path.splitext(os.path.basename(rel))[0]}",
                        "type": t["name"], "kind": t["kind"], "form": t["form"], "file": rel, "deliverable": t["deliverable"],
                        "workflows": wf, "depends_on": list(t["depends_on"]) if "depends_on" in t else [],
                        "version": _version(d, t, len(docs) <= 1) if t["kind"] == "type" else None,
                        **({"changed_by": changed} if changed else {}),
                        **({"rechecked_after": rechecked} if rechecked else {}),
                        "sha256": sha, "time": when})
    built = {r["type"] for r in out}
    for r in out:      # what it depends on in this run: only the types that were built
        r["depends_on"] = [x for x in r["depends_on"] if x in built]
    return out


def write(d):
    """artifacts.json in the run folder (additive: nothing else is touched)."""
    r = {"schema": "artifacts/1", "rows": rows(d)}
    with open(os.path.join(d, "artifacts.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    return r


def listing(d):
    """What the Artifacts tab shows: the saved artifacts.json when the run has one, else the same rows built by
    scanning the folder. Each row gets its type's label, tag, colour and how to open it."""
    types = load_types()
    by = {t["name"]: t for t in types["types"]}
    saved = _read(d, "artifacts.json") if d else None
    base = saved["rows"] if saved else rows(d, types)
    full = [{**r, "label": by[r["type"]]["label"], "tag": by[r["type"]]["tag"], "color": by[r["type"]]["color"],
             "open": OPEN[r["form"]], "depends_on_labels": [by[x]["label"] for x in r["depends_on"] if x in by],
             "saved": bool(saved)} for r in base if r["type"] in by]
    return {"deliverables": [r for r in full if r["deliverable"]], "records": [r for r in full if not r["deliverable"]]}


def served(d, name):
    """The path of a file named in the run's artifact rows (saved, or found now by the types list), else None. Nothing
    else is ever served."""
    name = str(name or "")
    if not d or ".." in name.split("/") or os.path.isabs(name):
        return None
    ok = {r["file"] for r in (listing(d)["deliverables"] + listing(d)["records"])} | {r["file"].replace(os.sep, "/")
                                                                                     for r in rows(d)}
    if name not in ok:
        ok |= set(tree_files(tree(d)))      # the tree's files: versions, the style guide, exports and the run's other records
    p = os.path.join(d, name)
    return p if name in ok and os.path.isfile(p) and os.path.getsize(p) <= MAX_BYTES else None


# ---------------------------------------------------------------------------------------------------------------- the tree
# The Artifacts tab as a tree (artifacts-tree/1): Plan, Specs, Deliverables, Proof, Records. Makers, readers and statuses come
# from j2_map.build, the same data the Map draws, so the two always agree; the files come from listing() and the run folder, each
# exactly once. Nothing names a run, a workflow or a stage: only file kinds (types.json) and the map's own fields.
TREE_STATUS = {"filed": "filed", "done_unchecked": "checks did not pass", "fault": "failed", "left_open": "open", "running": "open",
               "waiting": "open", "waiting_on_you": "open", "not_made": "not made", "idle": "filed"}
RECORD_MAKER = {"goal.json": "Client Lead (Identity)", "realization.json": "Adaptation (scored by the confidence judge)", "audits.json": "Quality Reviewer (Audit)", "receipts.jsonl": "Checker (automatic)",
                "chat.jsonl": "every function (the chat)", "calls.jsonl": "every function (AI calls)"}      # who writes each kind of record
PROOF = ("receipts.jsonl", "audits.json", "conditions.json")
RECORD_NAME = {"calls.jsonl": "AI calls", "outputs.jsonl": "Workflow outputs", "map.json": "Map data", "artifacts.json": "Artifact list",
               "report.json": "Run report (data)", "sections.json": "Sections", "documents.json": "Documents record"}      # files types.json does not list


def _lines(d, f):
    try:
        with open(os.path.join(d, f), encoding="utf-8") as fh:
            return sum(1 for x in fh if x.strip())
    except OSError:
        return 0


def tree(d, m=None):
    import j2_map
    if not d or not os.path.isdir(d):
        return {"schema": "artifacts-tree/1", "groups": []}
    m = m or j2_map.build(d)
    lst, types = listing(d), {t["file"]: t for t in load_types()["types"] if "*" not in t["file"]}
    # versions/1: the same history and handoffs versions.json holds, so a version row can say who made it and why
    vers = versions(d)
    vhist = {r["file"]: r for a in vers["artifacts"] for r in a["history"]}
    vart = {a["file"]: a for a in vers["artifacts"]}
    vhand = {}      # the handoffs that leave each deliverable, by the file the tree shows it under
    for h in vers["handoffs"]:
        f = next((a["file"] for a in vers["artifacts"] if a["artifact"] == h["from_artifact"]), None)
        if f:
            vhand.setdefault(f, []).append(h)
    rowsby = {r["file"]: r for r in lst["deliverables"] + lst["records"]}
    by = {n["id"]: n for n in m["nodes"]}
    made_step = {e["to"]: by[e["from"]] for e in m["edges"] if e["kind"] == "step" and by.get(e["from"], {}).get("kind") == "engine"}
    reads = [e for e in m["edges"] if e["kind"] == "handoff"]
    used = set()

    def size(f):
        return os.path.getsize(os.path.join(d, f)) if f and os.path.isfile(os.path.join(d, f)) else None

    def opener(f):
        r = rowsby.get(f)
        if r:
            return r["open"]
        ext = os.path.splitext(f or "")[1]
        return "image" if ext == ".png" else "preview" if ext == ".html" else "text"

    def vfacts(f):
        """The role that made a deliverable, how many versions it saved and the hand-offs that leave it (versions/1),
        wherever the tree shows that file. A file versions/1 does not cover gets none of these keys."""
        a = vart.get(f)
        return ({"role": a["role"], "versions": a["versions"]} if a else {}) | \
               ({"handoffs": vhand[f]} if vhand.get(f) else {})

    def item(name, f=None, made=None, status="filed", **kw):
        f0 = f
        if f and (f in used or not os.path.isfile(os.path.join(d, f))):
            f = None      # each file once; a send has no file of its own (its receipt is under Proof)
        if f:
            used.add(f)
        return {"name": name, "file": f, "made_by": made, "status": status, "size": size(f),
                "open": opener(f) if f else None, **vfacts(f0), **kw}

    def maker(n):
        st = made_step.get(n["id"])
        return {"persona": st["persona"], "workflows": list(n.get("workflows") or [])} if st else None

    def readers(nid):
        return sorted({w for e in reads if e["from"] == nid for w in e.get("readers") or []}, key=lambda w: int(re.sub(r"\D", "", w) or 0))

    def status(n):
        return n.get("send") or TREE_STATUS.get(n.get("status"), n.get("status") or "filed") if n.get("tag") == "Send" else TREE_STATUS.get(n.get("status"), "filed")

    # 1 Plan
    plan = []
    if "work:charter" in by or os.path.isfile(os.path.join(d, "goal.json")):
        wrote = any(e["kind"] == "speaks_to" and e["to"] == "work:charter" and e["from"] == "fn:identity" for e in m["edges"])
        plan.append(item("Charter", "goal.json", {"function": RECORD_MAKER["goal.json"]} if wrote else None))
    rz = _read(d, "realization.json")
    if rz is not None:
        st = rz.get("stages") or {}
        zone = (((rz.get("plan") or {}).get("certainty_assessment")) or {}).get("zone")
        note = [f"zone {zone}" if zone else "", f"{len(st)} stages: {', '.join(st)}" if st else "",
                f"plan confidence {rz['plan_confidence']}" if rz.get("plan_confidence") is not None else ""]
        kids = [item("Realization plan (text)", "realization.md", {"function": "code"})] if os.path.isfile(os.path.join(d, "realization.md")) else []
        plan.append(item("Realization plan", "realization.json", {"function": RECORD_MAKER["realization.json"]}, note=" · ".join(x for x in note if x), children=kids))
    wfs = _read(d, "workflows.json", []) or []
    if os.path.isfile(os.path.join(d, "workflows.json")):
        plan.append(item("Workflows", "workflows.json", {"function": "Validator (code)"}, note=f"{len(wfs)} workflows"))
    # 2 Specs: every decide workflow's file, with its maker and how many workflows read it
    specs = [item(n["label"], n.get("file"), maker(n), status(n), output=n.get("output") if n.get("output") != n["label"] else None, read_by=len(readers(n["id"])), node=n["id"])
             for n in m["nodes"] if n["kind"] == "work" and n.get("tag") == "Spec"]
    specs += [item(r["name"], f, None, note="no workflow recorded as its maker") for f, r in rowsby.items()
              if r["type"].startswith("workflow_files") and f not in used]
    # 3 Deliverables: each delivered output, with its style guide, its versions, its screenshots and exports, and the sends that report it
    deck = [n for n in m["nodes"] if n["kind"] == "work" and n["id"] != "work:charter" and n.get("tag") not in ("Spec", "Style", "Send")]
    style = [n for n in m["nodes"] if n.get("tag") == "Style"]
    sends = [n for n in m["nodes"] if n.get("tag") == "Send"]
    placed_send = set()
    out = []
    for n in deck:
        kids = []
        for s_ in style:
            if any(e["from"] == s_["id"] and e["to"] == n["id"] for e in reads):
                kids.append(item(s_["label"], s_.get("file"), maker(s_), status(s_), node=s_["id"], read_by=len(readers(s_["id"]))))
        t = next((x for x in load_types()["types"] if x["kind"] == "type" and f"work:{x['name']}" == n["id"]), None)
        site = os.path.join(d, "site")
        if t and os.path.isdir(site):
            pat = r"v(\d+)\.html" if t["form"] == "page" else rf"(?:{re.escape(t['name'])}-)?v(\d+)\.md"
            vs = sorted(((int(mm.group(1)), f"site/{f}") for f in os.listdir(site) for mm in [re.fullmatch(pat, f)] if mm))
            if t["form"] != "page" and any(re.fullmatch(rf"{re.escape(t['name'])}-v\d+\.md", f) for f in os.listdir(site)):
                vs = [(k, f) for k, f in vs if os.path.basename(f).startswith(t["name"] + "-")]      # several documents: only this one's
            if vs:
                kids.append({"name": "Versions", "count": len(vs), "collapsed": True,
                             "children": [_version_item(item, k, f, vhist) for k, f in reversed(vs)]})
            if t["form"] == "page":
                shots = sorted((f for f, r in rowsby.items() if r["type"] == "screenshots"), key=_num)
                if shots:
                    kids.append({"name": "Screenshots", "count": len(shots), "collapsed": False, "children": [item(r_["name"], f) for f in shots for r_ in [rowsby[f]]]})
            base = os.path.splitext(n.get("file") or "")[0]
            for f in sorted(os.listdir(d)):
                if base and f.startswith(os.path.basename(base) + ".") and f != os.path.basename(n.get("file") or "") and f.endswith(".docx"):
                    kids.append(item("Word file", f, {"function": "code (export)"}))
        for s_ in sends:
            if any(e["from"] == n["id"] and e["to"] == s_["id"] for e in reads):
                placed_send.add(s_["id"])
                kids.append(item(s_["label"], None, maker(s_), status(s_), node=s_["id"], note="receipt in Check results"))
        out.append(item(n["label"], n.get("file"), maker(n), status(n), version=n.get("version"), node=n["id"],
                        workflows=len(n.get("workflows") or []), children=kids))
    out += [item(s_["label"], None, maker(s_), status(s_), node=s_["id"], note="receipt in Check results") for s_ in sends if s_["id"] not in placed_send]
    out += [item(s_["label"], s_.get("file"), maker(s_), status(s_), node=s_["id"]) for s_ in style if s_.get("file") not in used]
    # 4 Proof
    proof = []
    for f in PROOF:
        if os.path.isfile(os.path.join(d, f)):
            j = _read(d, f)
            n_ = _lines(d, f) if f.endswith(".jsonl") else len(j) if isinstance(j, (list, dict)) else 0
            proof.append(item({"receipts.jsonl": "Check results", "audits.json": "Audits", "conditions.json": "Necessary conditions"}[f], f,
                              {"function": RECORD_MAKER.get(f, "code")}, note=f"{n_} {('entr' + ('y' if n_ == 1 else 'ies')) if f.endswith('.jsonl') else 'item' + ('' if n_ == 1 else 's')}"))
    for f in sorted(os.listdir(d)):
        if re.fullmatch(r"stage-\w+\.json", f):
            proof.append(item(f"Stage record: {f[6:-5]}", f, {"function": "code"}, note=(lambda k: f"{k} audit{'' if k == 1 else 's'}")(len((_read(d, f, {}) or {}).get('audits') or []))))
    # 5 Records: everything else the run kept
    rec = []
    for f, r in rowsby.items():
        if f not in used:
            rec.append(item(r["name"], f, {"function": RECORD_MAKER.get(f, "code")}))
    for root, _, files in os.walk(d):
        for x in sorted(files):
            f = os.path.relpath(os.path.join(root, x), d).replace(os.sep, "/")
            if f not in used and not x.startswith("."):
                rec.append(item(types.get(f, {}).get("label") or RECORD_NAME.get(f) or f, f, {"function": RECORD_MAKER.get(f, "code")}))
    groups = [("plan", "Plan", plan, False), ("specs", "Specs", specs, False), ("deliverables", "Deliverables", out, False),
              ("proof", "Proof", proof, False), ("records", "Records", rec, True)]
    return {"schema": "artifacts-tree/1", "groups": [{"id": k, "label": lab, "count": len(it), "collapsed": col, "items": it}
                                                       for k, lab, it, col in groups]}


def tree_files(t):
    """Every file the tree shows, once each (for serving and tests)."""
    out = []

    def walk(xs):
        for x in xs:
            if x.get("file"):
                out.append(x["file"])
            walk(x.get("children") or [])
    for g in t.get("groups") or []:
        walk(g["items"])
    return out


# ------------------------------------------------------------------------------------------------ version history
# versions/1: every saved version of each deliverable, who made it, why, and how much changed; then the handoffs
# between the roles (who built from whose work, and whether the receiving check passed). Code only, no model call,
# recorded data only: what a run didn't record reads "not recorded" and never a guess.
# The role names are display labels, in this one place.
ROLES = {"prd": "Product worker", "hld": "Tech writer", "lld": "Tech writer", "design": "Designer",
         "website": "UI developer"}
DESIGN = {"name": "design", "label": "Design (style guide)", "tag": "Design", "file": "style.json", "form": "data"}
ACCEPTED = re.compile(r"finish as it is|ship as is|as it is|accept", re.I)      # a Requester decision, in their own words


def _stage_of(d, docs=None):
    """workflow id -> the deliverable it built: a document stage from documents.json, else the website (the stage
    that writes the page). Only what the run recorded."""
    docs = docs if docs is not None else (_read(d, "documents.json", {}) or {})
    out = {}
    for kind, rec in (docs or {}).items():
        for wid in rec.get("workflows") or []:
            out[wid] = kind
    for w in _read(d, "workflows.json", []) or []:
        out.setdefault(w.get("id"), "website")
    return out


def _diff_lines(d, prev, cur):
    """{"added", "removed"} between two saved versions (difflib over the files themselves); zeros when either file
    can't be read, and zeros for a first version (no previous file)."""
    import difflib
    def read(f):
        with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    if not prev:
        return {"added": 0, "removed": 0}
    try:
        a, b = read(prev), read(cur)
    except OSError:
        return {"added": 0, "removed": 0}
    add = sum(1 for x in difflib.unified_diff(a, b, n=0, lineterm="") if x[:1] == "+" and not x.startswith("+++"))
    rem = sum(1 for x in difflib.unified_diff(a, b, n=0, lineterm="") if x[:1] == "-" and not x.startswith("---"))
    return {"added": add, "removed": rem}


def _accepted(d):
    """True when the run recorded the Requester accepting what was built as it is (their own answer in the chat)."""
    for m in (json.loads(x) for x in _jsonl(d, "chat.jsonl")):
        if m.get("who") == "user" and ACCEPTED.search(str(m.get("text") or "")):
            return True
    for q in (_read(d, "summary.json", {}) or {}).get("questions_to_user") or []:
        if ACCEPTED.search(str(q.get("answer") or "")):
            return True
    return False


def _jsonl(d, name):
    try:
        with open(os.path.join(d, name), encoding="utf-8") as f:
            return [ln for ln in f if ln.strip()]
    except OSError:
        return []


def _made_by(kind, version, wfs, stage, board):
    """[{workflow, atom, role}] for one saved version: the workflows whose own recorded version is this one inside
    that deliverable's stage, else the atom a board answer changed it from (board.json). Empty when the run
    recorded neither."""
    out = []
    for w in wfs:
        if stage.get(w.get("id")) == kind and w.get("version") == version:
            for a in w.get("atoms") or []:
                out.append({"workflow": w["id"], "atom": a.get("id"), "role": ROLES.get(kind)})
            if not (w.get("atoms") or []):
                out.append({"workflow": w["id"], "atom": None, "role": ROLES.get(kind)})
    for e in board:
        up = e.get("artifact_update") or {}
        if up.get("doc") == kind and up.get("to_version") == version and e.get("answered_by"):
            out.append({"workflow": e["answered_by"], "atom": e.get("to"), "role": ROLES.get(kind)})
    return out


def _why(kind, version, first, wfs, stage, board, accepted):
    """Why this version exists, in the run's own words: a board change, a fix, a revise, the first build, the
    Requester accepting it as it is, else "not recorded"."""
    for e in board:
        up = e.get("artifact_update") or {}
        if up.get("doc") == kind and up.get("to_version") == version:
            return f"changed by {e['id']}"
    mine = [w for w in wfs if stage.get(w.get("id")) == kind and w.get("version") == version]
    for w in mine:
        if w.get("fixes"):
            return "fix of " + ", ".join(str(f) for f in w["fixes"])
        if w.get("revises"):
            return f"revise of {w['revises']}"
    if mine:
        return "built"
    return "accepted as is" if accepted else "not recorded"


def versions(d):
    """versions/1 for a run folder: one entry per deliverable it saved (prd, hld, lld, design, website), each with
    its whole history, oldest first, and the handoffs between the roles."""
    if not d or not os.path.isdir(d):
        return {"schema": "versions/1", "artifacts": [], "handoffs": [], "not_recorded": ["the run folder"]}
    types = {t["name"]: t for t in load_types()["types"]}
    docs = _read(d, "documents.json", {}) or {}
    wfs = _read(d, "workflows.json", []) or []
    stage, nr = _stage_of(d, docs), []
    board = (_read(d, "board.json", {}) or {}).get("entries") or []
    accepted, out = _accepted(d), []
    for kind in ("prd", "hld", "lld", "website"):
        t = types.get(kind)
        files = _version_files(d, t, len(docs) <= 1) if t else []
        if not files:
            continue
        first, hist, prev = files[0][0], [], None
        for n, rel in files:
            sha, when = _stat(d, rel)
            made = _made_by(kind, n, wfs, stage, board)
            hist.append({"version": n, "file": rel, "time": when, "sha256": sha,
                         "made_by": made or "not recorded",
                         "why": _why(kind, n, first, wfs, stage, board, accepted),
                         "lines_changed": _diff_lines(d, prev, rel)})
            if not made:
                nr.append(f"who made {kind} v{n}")
            prev = rel
        out.append({"artifact": kind, "label": t["label"], "tag": t["tag"], "role": ROLES[kind],
                    "file": t["file"], "versions": len(hist), "history": hist})
    if os.path.isfile(os.path.join(d, DESIGN["file"])):       # the style guide: one version, by the workflow that wrote it
        sha, when = _stat(d, DESIGN["file"])
        owner = ((_read(d, "sections.json", {}) or {}).get("style") or {}).get("owner") \
            or next((w["id"] for w in wfs if w.get("style_guide") or "style" in str(w.get("name", "")).lower()), None)
        atom = next((a.get("id") for w in wfs if w.get("id") == owner for a in w.get("atoms") or []), None)
        made = [{"workflow": owner, "atom": atom, "role": ROLES["design"]}] if owner else None
        if not made:
            nr.append("who made the style guide")
        out.append({"artifact": "design", "label": DESIGN["label"], "tag": DESIGN["tag"], "role": ROLES["design"],
                    "file": DESIGN["file"], "versions": 1,
                    "history": [{"version": 1, "file": DESIGN["file"], "time": when, "sha256": sha,
                                 "made_by": made or "not recorded", "why": "built" if made else "not recorded",
                                 "lines_changed": {"added": 0, "removed": 0}}]})
    hand, hnr = handoffs(d, out)
    return {"schema": "versions/1", "run": os.path.basename(d), "artifacts": out, "handoffs": hand,
            "roles": dict(ROLES), "not_recorded": nr + hnr}


def _audits(d, kind=None):
    """The audits of one stage, oldest first: the stage file a finished document leaves behind, else the audits of
    that output in audits.json (a one-document run keeps them there). Re-check entries are not audits."""
    au = ((_read(d, f"stage-{kind}.json", {}) or {}).get("audits") or []) if kind else []
    rest = [a for a in (_read(d, "audits.json", []) or []) if (a or {}).get("kind") != "recheck"]
    return au or ([a for a in rest if a.get("output") == kind] if kind else rest)


def _doc_conditions(d, kind):
    """(result, evidence, note) from the receiving document's own necessary conditions (P1-P8 / H1-H6 / L1-L6) as
    its last audit recorded them. A warning never blocks, as j2.blocks has it."""
    au = _audits(d, kind)
    conds = (au[-1].get("conditions") or []) if au else []
    if not conds:
        return "not recorded", [], f"no {kind.upper()} conditions are recorded"
    ids = [c["id"] for c in conds]
    bad = [c["id"] for c in conds if not c.get("met") and c.get("severity") != "warn"]
    return ("fail" if bad else "pass",
            [f"{c} (audit {len(au)})" for c in bad] or [f"{ids[0]}-{ids[-1]} (audit {len(au)})"],
            f"{len(ids) - len(bad)} of {len(ids)} conditions met")


def _slice_receipts(d, wanted):
    """(result, evidence, note) from the website atoms' lld-slice receipts: the latest attempt of each, by code."""
    latest = {}
    for ln in _jsonl(d, "receipts.jsonl"):
        r = json.loads(ln)
        if r.get("type") == "lld-slice" and (not wanted or r.get("atom") in wanted):
            cur = latest.get(r.get("atom"))
            if not cur or (r.get("attempt") or 0) >= (cur.get("attempt") or 0):
                latest[r["atom"]] = r
    if not latest:
        return "not recorded", [], "no lld-slice receipt is recorded"
    bad = [r for r in latest.values() if r.get("pass") is not True]
    return ("fail" if bad else "pass",
            [f"{r['atom']}:{r.get('attempt')}" for r in (bad or latest.values())],
            f"{len(latest) - len(bad)} of {len(latest)} slice check(s) passed")


def _rubric(d, rid="R-1"):
    """(result, evidence, note) from the latest rubric result with this id (R-1: the page follows the style guide)."""
    au = _audits(d)
    for i in range(len(au), 0, -1):
        for r in au[i - 1].get("rubric") or []:
            if r.get("id") == rid:
                ok = r["pass"] if r.get("pass") is not None else str(r.get("verdict") or "").startswith("PASS")
                return ("pass" if ok else "fail"), [f"{rid} (audit {i})"], str(r.get("note") or r.get("evidence") or "")[:120]
    return "not recorded", [], f"no {rid} result is recorded"


def _makers(row):
    """The makers a version row records, or none at all when the run recorded none (made_by is "not recorded")."""
    return [m for m in (row.get("made_by") or []) if isinstance(m, dict)]


def _row_cycle(row, wfs, board):
    """The cycle a version was made in, from the workflow that made it or the board entry that changed it; None when
    the run recorded neither."""
    for m in _makers(row):
        w = wfs.get(m.get("workflow")) or {}
        if w.get("cycle"):
            return w["cycle"]
    for e in board:
        up = e.get("artifact_update") or {}
        if row["file"].endswith(f"-v{row['version']}.md") and up.get("to_version") == row["version"] and e.get("cycle"):
            return e["cycle"]
    return None


def _version_when(hist, wfs, board, cycle, before=None):
    """The version the consumer actually built from: the newest one made in an earlier cycle, or - when the maker
    ran in the consumer's own cycle, as the style guide does - the newest one already saved when the consumer wrote
    its output. "not recorded" when neither the cycles nor the recorded times can tell."""
    rows = [(r, _row_cycle(r, wfs, board)) for r in hist]
    older = [r["version"] for r, c in rows if c and cycle and c < cycle]
    if older:
        return max(older)
    same = [r["version"] for r, c in rows
            if before and r.get("time") and r["time"] <= before and (not c or not cycle or c <= cycle)]
    return max(same) if same else "not recorded"


def handoffs(d, arts):
    """One row per handoff this run has: Product worker -> Tech writer (prd -> hld, prd -> lld), Tech writer -> UI
    developer (lld -> website, or hld -> website when the run has no LLD) and Designer -> UI developer (design ->
    website). consumers are the receiving atoms whose recorded content edges reach the sender's atoms
    (j2_schema.CONTENT_EDGES). realized comes only from checks the run recorded: the receiving document's own
    conditions, the website atoms' lld-slice receipts, or the latest R-1 rubric result; anything else is
    "not recorded", never a pass. Returns (handoffs, what wasn't recorded)."""
    import j2_schema
    have = {a["artifact"]: a for a in arts}
    wfs = {w["id"]: w for w in _read(d, "workflows.json", []) or []}
    board = (_read(d, "board.json", {}) or {}).get("entries") or []
    atoms = {v["id"]: v for v in _atoms(d)}
    stage = _stage_of(d)
    links = [("prd", "hld"), ("prd", "lld")] + ([("lld", "website")] if "lld" in have else [("hld", "website")]) \
        + [("design", "website")]
    out, nr = [], []
    for src, dst in links:
        if src not in have or dst not in have:
            continue
        if src == "design":      # the style guide is one atom's own output, not a stage
            src_atoms = {m["atom"] for m in _makers(have["design"]["history"][0]) if m.get("atom")}
        else:
            src_atoms = {aid for aid, v in atoms.items() if stage.get(v.get("workflow")) == src}
        consumers = sorted({aid for aid, v in atoms.items() if stage.get(v.get("workflow")) == dst
                            and any(e.get("atom") in src_atoms
                                    and (src == "design" or j2_schema.content_edge(e.get("why")))
                                    for e in v.get("depends_on") or [])}, key=_num)
        cycles = [c for c in (wfs.get(atoms[a].get("workflow"), {}).get("cycle") for a in consumers) if c]
        mine = {a for a in consumers}
        made = [r["time"] for r in have[dst]["history"]
                if any(m.get("atom") in mine for m in _makers(r))]
        from_v = _version_when(have[src]["history"], wfs, board, min(cycles) if cycles else None,
                               min(made) if made else None)
        if dst in ("hld", "lld"):
            res, ev, note = _doc_conditions(d, dst)
        elif src == "lld":
            res, ev, note = _slice_receipts(d, set(consumers))
        else:
            res, ev, note = _rubric(d)
        if not consumers:
            res, ev = "not recorded", []
            note = f"no recorded edge from the {have[src]['tag']} to the {have[dst]['tag']}"
        if res == "not recorded":
            nr.append(f"whether {src} -> {dst} was realized ({note})")
        if from_v == "not recorded":
            nr.append(f"the {src} version {dst} was built from")
        out.append({"from_artifact": src, "from_version": from_v, "from_role": ROLES[src], "to_artifact": dst,
                    "to_role": ROLES[dst], "consumers": consumers, "realized": res, "evidence": ev, "note": note})
    return out, nr


def write_versions(d):
    """versions.json in the run folder, written where artifacts.json is (additive: nothing else is touched)."""
    r = versions(d)
    with open(os.path.join(d, "versions.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, indent=2, ensure_ascii=False)
    return r


def _version_item(item, n, f, vhist):
    """One row of a deliverable's Versions list in the tree: who made it and why, from the version history
    (versions/1), so the tree and versions.json say the same thing. "not recorded" where the run recorded neither."""
    r = vhist.get(f) or {}
    made = _makers(r)
    ch = r.get("lines_changed") or {}
    note = " · ".join(x for x in [r.get("why") or "not recorded",
                                  f"+{ch['added']}/-{ch['removed']} lines" if ch.get("added") or ch.get("removed")
                                  else "" if n == 1 else "no line changed"] if x)
    return item(f"v{n}", f, {"persona": made[0].get("role"), "workflows": sorted({m["workflow"] for m in made
                                                                                  if m.get("workflow")})}
                if made else None, "filed", note=note, version=n)
