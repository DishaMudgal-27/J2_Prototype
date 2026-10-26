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


def _version(d, t, single):
    """The latest build of a deliverable, from the version files in site/: hld-v3.md, v3.html (a one-document run keeps
    plain names: v3.md)."""
    site = os.path.join(d, "site")
    if not os.path.isdir(site):
        return None
    if t["form"] == "page":
        pat = r"v(\d+)\.html"
    else:
        pat = rf"{t['name']}-v(\d+)\.md" + (r"|v(\d+)\.md" if single else "")
    n = [int(next(g for g in m.groups() if g)) for f in os.listdir(site) for m in [re.fullmatch(pat, f)] if m]
    return max(n) if n else None


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
        rechecked = sorted({q for w in wf for q in (board.get(("_wf", w)) or {}).get("rechecked_after") or []}, key=_num)
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
    p = os.path.join(d, name)
    return p if name in ok and os.path.isfile(p) and os.path.getsize(p) <= MAX_BYTES else None
