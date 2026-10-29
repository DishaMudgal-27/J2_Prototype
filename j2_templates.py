"""templates/1: the three templates a work atom's builder is held to, and the proof that it was held to them.

Behind J2_TEMPLATES=1 (default off), so with the flag unset nothing here runs and the plain flow, its prompts, its
atoms and its files stay byte for byte what they were.

Three templates, one per thing that can drift:
  1. the prompt template, prompts/builder.md: the agent card and the rules, sent inside an XML envelope whose tags
     (TAGS) carry exactly the facts the plain prompt carries, only tagged;
  2. the reply model, j2_types.BuilderReply: the field names the builder's JSON line already uses;
  3. the output template, artifacts/templates/<artifact>.json: the sections in code order, each with the rules J2
     already enforces (conditions/<artifact>.json, assemble(), parse_style), named one by one.

Every value this module returns is computed from the run's own records (the prompt text that was sent, the reply that
came back, the receipts code wrote). Nothing is written by an agent, and anything a run didn't record reads
"not recorded", never a pass. Pure functions and file reads; no model call.
"""
import hashlib
import json
import os
import re

import j2_types

SCHEMA = "templates/1"
HERE = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE = os.path.join(HERE, "prompts", "builder.md")
TEMPLATE_DIR = os.path.join(HERE, "artifacts", "templates")
PROMPT_TEMPLATE = "builder/1"
CHECK_TYPE = "template-match"
# The envelope's tags, in the order the prompt carries them. All of them are required: a prompt missing one did not
# go through the template, so the atom's "prompt used" row fails and names the tag.
TAGS = ("agent_card", "workflow", "work_atom", "output_template", "context", "board", "task", "reply_schema")
ARTIFACTS = ("prd", "hld", "lld", "website", "design")
NOT_RECORDED = "not recorded"


def enabled():
    return os.environ.get("J2_TEMPLATES") == "1"


# ---------------------------------------------------------------- the prompt template
_CARD = {}


def prompt_card():
    """(version, sha256, card text) of prompts/builder.md, read once. The version is its YAML header's template
    field, so the file and the code can't disagree about which template was used."""
    if not _CARD:
        raw = open(PROMPT_FILE, encoding="utf-8").read()
        m = re.match(r"---\n(.*?)\n---\n", raw, re.S)
        head, body = (m.group(1), raw[m.end():]) if m else ("", raw)
        ver = (re.search(r"(?m)^template:\s*(\S+)", head) or [None, PROMPT_TEMPLATE])[1]
        _CARD.update(version=ver, sha=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
                     card=(head + "\n" + body).strip())
    return _CARD["version"], _CARD["sha"], _CARD["card"]


def envelope(parts):
    """The builder prompt as an XML envelope: one tag per part, in TAGS order, each on its own lines. A part a run
    has nothing for still gets its tag, with "not recorded" inside, so the envelope is always readable."""
    out = []
    for tag in TAGS:
        body = parts.get(tag)
        out.append(f"<{tag}>\n{(body if str(body or '').strip() else NOT_RECORDED)}\n</{tag}>")
    return "\n".join(out)


def tags_in(text):
    """The envelope tags the prompt text really carries (opened and closed), in TAGS order. Read from the text that
    was sent, never from what the code meant to send."""
    t = str(text or "")
    return [x for x in TAGS if f"<{x}>" in t and f"</{x}>" in t]


def missing_tags(text):
    return [x for x in TAGS if x not in tags_in(text)]


def work_atom_tag(atom):
    """The <work_atom> body: the atom's goal, how, constraints and defined output as named tags, then the rest of the
    atom exactly as the plain prompt sends it (its context and verification), so no fact is lost."""
    a = atom or {}
    rest = {k: v for k, v in a.items() if k not in ("goal", "how", "constraints", "expected_output")}
    return "\n".join([f"<goal>{json.dumps(a.get('goal'), ensure_ascii=False)}</goal>",
                      f"<how>{json.dumps(a.get('how'), ensure_ascii=False)}</how>",
                      f"<constraints>{json.dumps(a.get('constraints') or [], ensure_ascii=False)}</constraints>",
                      f"<defined_output>{json.dumps(a.get('expected_output') or [], ensure_ascii=False)}"
                      "</defined_output>",
                      f"<rest>{json.dumps(rest, ensure_ascii=False)}</rest>"])


def reply_schema_tag(fields):
    """The <reply_schema> body: the reply-format line and the JSON Schema, both generated from the reply model."""
    text, schema = j2_types.format_for(fields=fields)
    return f"{j2_types.MODEL}\n{text}\n{json.dumps(schema, ensure_ascii=False)}"


# ---------------------------------------------------------------- the output templates
_TEMPLATES = {}


def load_template(kind):
    """artifacts/templates/<kind>.json, read once. Unknown kinds give None (never an invented template)."""
    k = str(kind or "")
    if k not in ARTIFACTS:
        return None
    if k not in _TEMPLATES:
        with open(os.path.join(TEMPLATE_DIR, k + ".json"), encoding="utf-8") as f:
            _TEMPLATES[k] = json.load(f)
    return _TEMPLATES[k]


def template_sections(kind):
    """The section names a template fixes, in code order ([] for a page or the style guide, whose parts are the
    run's own)."""
    t = load_template(kind) or {}
    return [s["name"] for s in t.get("sections") or []]


def rules_for(kind, section):
    """The rules one produced part is held to: its own section's rules in a document, the template's section_rules
    for a page or the style guide. A document section the template doesn't name gives []."""
    t = load_template(kind) or {}
    if t.get("sections"):
        want = _norm(section)
        for s in t["sections"]:
            if _norm(s["name"]) == want or want.startswith(_norm(s["name"])):
                return list(s.get("rules") or [])
        return []
    return list(t.get("section_rules") or [])


def template_name(kind):
    return (load_template(kind) or {}).get("template")


def _norm(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t or "").lower()).strip()


def _words(text):
    return len([w for w in re.split(r"\s+", re.sub(r"[*_`#|-]+", " ", str(text or ""))) if w])


def check_output(kind, section, text, where=None):
    """{"pass", "rules": [{rule, from, met, note}], "evidence"}: does what the builder produced follow its output
    template? kind is the artifact (prd, hld, lld, website, design), section the part the atom wrote, text the
    assembled document or page, where extra facts code already has ({"sid", "run_dir"}).

    Every rule here is one J2 already enforces, and each result names it ("H4: C3 names no R id"), so a miss reads
    the same way whether it comes from a condition or from this check. A template or section with no rules gives
    pass None: not recorded, never a pass.
    """
    import j2      # late: j2 imports this module; by call time it is loaded
    where = where or {}
    rules = rules_for(kind, section)
    if not load_template(kind) or not rules:
        return {"pass": None, "rules": [], "evidence": f"no output template rule for {kind} {section!r}"}
    page, head_only = str(text or ""), False
    if kind == "website":      # a page: the atom's own marked section, as code assembled it into the file
        sid = str(where.get("sid") or section or "")
        m = re.search(r"<!-- J2:%s start[^>]*-->(.*?)<!-- J2:%s end" % (re.escape(sid), re.escape(sid)), page, re.S)
        body = m.group(1) if m else None
        head_only = body is None and f"<!-- J2:{sid} head start" in page
    elif kind == "design":
        body = text
    else:
        body = j2.md_section(page, section)
    out = []

    def add(rule, met, note):
        out.append({"rule": rule.get("rule"), "from": rule.get("from"), "met": met, "note": note})

    for r in rules:
        name = r.get("rule")
        if name == "heading":
            add(r, body is not None, f"heading {section!r} " + ("found" if body is not None else "not found"))
        elif name in ("min-words", "section-not-empty"):
            n, need = _words(body), max(1, int(r.get("words") or 1))
            if body is None and kind == "website":      # head tags only, or no section of its own: nothing to count
                add(r, None, f"no section body for {section!r} in the page")
            else:
                add(r, body is not None and n >= need, f"{section!r} has {n} word(s), needs {need}")
        elif name in ("ids-unique", "ids-sequential"):
            ids = j2.md_ids(body or "", r["prefix"])
            dup = sorted({i for i in ids if ids.count(i) > 1})
            seq = ids == list(range(1, len(ids) + 1))
            if name == "ids-unique":
                need = r.get("present", True)
                add(r, (bool(ids) or not need) and not dup,
                    f"no {r['prefix']}1, {r['prefix']}2, ... ids" if not ids else
                    f"duplicate {r['prefix']} id(s): {dup}" if dup else f"{len(ids)} unique {r['prefix']} id(s)")
            else:
                add(r, bool(ids) and seq, f"{r['prefix']} ids are "
                    + ("sequential" if seq and ids else f"not sequential: {ids}"))
        elif name == "ids-covered":
            src = j2.md_ids(j2.md_section(str(text or ""), r["of"]) or "", r["prefix"])
            here = set(j2.md_ids(body or "", r["prefix"]))
            miss = [f"{r['prefix']}{i}" for i in src if i not in here]
            add(r, not miss and bool(src), f"{r['of']} defines no {r['prefix']} id" if not src else
                f"{', '.join(miss)} from {r['of']} not covered here" if miss else
                f"every {r['prefix']} id from {r['of']} is covered")
        elif name == "components-have-responsibility":
            comps = j2.parse_hld(str(text or ""))
            bad = [c["id"] for c in comps if not str(c.get("responsibility") or "").strip()]
            add(r, bool(comps) and not bad, "no C ids in Components" if not comps else
                f"{', '.join(bad)} states no responsibility" if bad else
                f"all {len(comps)} component(s) state a responsibility")
        elif name == "components-cover-requirements":
            comps = j2.parse_hld(str(text or ""))
            bad = [c["id"] for c in comps if not c.get("covers")]
            add(r, bool(comps) and not bad, "no C ids in Components" if not comps else
                "; ".join(f"{c} names no {r.get('covers', 'R')} id" for c in bad) if bad else
                f"all {len(comps)} component(s) name their {r.get('covers', 'R')} ids")
        elif name in ("sections-have-id", "sections-implement-components", "elements-have-parts",
                      "fields-have-parts"):
            lld = j2.parse_lld(str(text or ""))
            if name == "sections-have-id":
                bad = [s["id"] for s in lld["sections"] if not s.get("anchor")]
                add(r, bool(lld["sections"]) and not bad, "no S ids" if not lld["sections"] else
                    f"{', '.join(bad)} has no anchor" if bad else f"all {len(lld['sections'])} section(s) have an anchor")
            elif name == "sections-implement-components":
                bad = [s["id"] for s in lld["sections"] if not s.get("implements")]
                add(r, bool(lld["sections"]) and not bad, "no S ids" if not lld["sections"] else
                    "; ".join(f"{s} names no {r.get('covers', 'C')} id" for s in bad) if bad else
                    f"all {len(lld['sections'])} section(s) name their {r.get('covers', 'C')} ids")
            else:
                key, parts = ("elements", r.get("parts") or []) if name == "elements-have-parts" \
                    else ("fields", r.get("parts") or [])
                items = lld[key]
                bad = [f"{x['id']} has no " + ", ".join(p for p in parts if x.get(p) is None)
                       for x in items if any(x.get(p) is None for p in parts)]
                add(r, bool(items) and not bad, f"no {key[0].upper()} ids" if not items else
                    "; ".join(bad) if bad else f"all {len(items)} {key[:-1]}(s) have {', '.join(parts)}")
        elif name == "section-markers":
            sid = where.get("sid") or section
            add(r, None if head_only else body is not None,
                f"section {sid} writes head tags only, no body in the page" if head_only else
                f"section {sid} is " + ("between its markers in the page" if body is not None
                                        else "not between its markers"))
        elif name == "anchor-present" and kind == "website":
            sel = str(section or "")
            if not sel.startswith(("#", ".")):      # this atom recorded no anchor of its own: the rule can't run
                add(r, None, "no anchor recorded for this section")
            else:
                n = len(j2.PageScan(page).matching(sel))
                add(r, n == 1, f"{n} element(s) match {sel!r}, expected 1")
        elif name == "anchor-present":
            sel = str(section or "")
            if not sel.startswith(("#", ".")):      # this atom recorded no anchor of its own: the rule can't run
                add(r, None, "no anchor recorded for this section")
            else:
                n = len(j2.PageScan(str(text or "")).matching(sel))
                add(r, n == 1, f"{n} element(s) match {sel!r}, expected 1")
        elif name in ("style-keys", "style-hex", "style-present", "style-css-safe"):
            guide = where.get("style")
            if guide is None:
                add(r, None, "style.json not recorded")
                continue
            if name == "style-css-safe":
                flat = [str(v) for v in _flat(guide) if v is not None]
                bad = [v for v in flat if not j2.CSS_SAFE.match(str(v))]
                add(r, not bad, f"{len(bad)} value(s) are not plain CSS: {bad[:3]}" if bad else
                    f"all {len(flat)} value(s) are plain CSS")
            else:
                miss = [k for k in r.get("keys") or [] if _dig(guide, k) in (None, "", {}, [])]
                if name == "style-hex":
                    miss = [k for k in r.get("keys") or [] if not j2.HEX.fullmatch(str(_dig(guide, k) or ""))]
                kind_txt = "colour(s)" if name == "style-hex" else "key(s)"
                add(r, not miss, f"missing or not a colour: {', '.join(miss)}" if name == "style-hex" and miss else
                    f"missing: {', '.join(miss)}" if miss else f"all {len(r.get('keys') or [])} {kind_txt} present")
        else:
            add(r, None, f"unknown rule {name!r}")
    met = [x for x in out if x["met"] is True]
    missed = [x for x in out if x["met"] is False]
    unknown = [x for x in out if x["met"] is None]
    ok = False if missed else True if met else None
    ev = f"{len(met)} of {len(out) - len(unknown)} rule(s) met" + (f", {len(unknown)} could not run" if unknown else "")
    detail = "; ".join(f"{x['from']}: {x['note']}" for x in (missed or unknown)[:4])
    return {"pass": ok, "rules": out, "evidence": ev + (f": {detail}" if detail else "")}


def _flat(obj):
    """Every leaf value of a style guide, for the plain-CSS rule."""
    if isinstance(obj, dict):
        return [v for x in obj.values() for v in _flat(x)]
    if isinstance(obj, list):
        return [v for x in obj for v in _flat(x)]
    return [obj]


def _dig(obj, path):
    for k in str(path).split("."):
        obj = (obj or {}).get(k) if isinstance(obj, dict) else None
    return obj


def check_record(check, page, run_dir):
    """{actual, pass, evidence} for one template-match check, as run_check returns it. The check carries its own
    artifact, section and section id (code wrote it), so nothing here is guessed."""
    kind, section = check.get("template"), check.get("target")
    where = {"sid": check.get("section"), "run_dir": run_dir}
    if kind == "design":
        p = os.path.join(run_dir or "", "style.json")
        try:
            with open(p, encoding="utf-8") as f:
                where["style"] = json.load(f)
        except (OSError, ValueError):
            where["style"] = None
    r = check_output(kind, section, page, where)
    return {"actual": {"met": [x["rule"] for x in r["rules"] if x["met"] is True],
                       "missed": [x["rule"] for x in r["rules"] if x["met"] is False]},
            "pass": r["pass"], "evidence": r["evidence"]}


def atom_checks(atom, kind, sid=None, style=False):
    """The template-match checks code adds to one work atom: one per templated defined-output item (a document's
    heading items, a page's section items), and one for the style guide when this atom's workflow wrote it. Returns
    the new checks; existing ones are never changed."""
    if not load_template(kind):
        return []
    items = [x for x in atom.get("expected_output") or [] if isinstance(x, dict)]
    out, one = [], {"text": f"What it wrote follows the {kind} output template ({template_name(kind)})",
                    "type": CHECK_TYPE, "template": kind, "section": sid, "expect": True}
    if (load_template(kind) or {}).get("form") == "doc":
        # a document: one check per heading item, whose target is the section the atom wrote
        out += [{**one, "target": x["target"], "item": n} for n, x in enumerate(items, 1)
                if x.get("kind") == "heading" and x.get("target")]
    else:
        # a page: the atom's own marked section, named by its anchor when it records one (the section item's
        # target, else the anchor the build recorded). Without one, the anchor rule says so and the markers decide.
        sec = next(((n, x["target"]) for n, x in enumerate(items, 1)
                    if x.get("kind") == "section" and x.get("target")), None)
        anchor = (atom.get("agent_output") or {}).get("anchor")
        out.append({**one, "target": sec[1] if sec else (f"#{anchor}" if anchor else sid),
                    **({"item": sec[0]} if sec else {})})
    if style:
        out.append({"text": f"The style guide follows the design output template ({template_name('design')})",
                    "type": CHECK_TYPE, "template": "design", "target": "style.json", "section": "style",
                    "expect": True})
    return out


def add_atom_checks(atoms, kind, sid=None, style=False):
    """The same checks, added in place to each atom that doesn't have one yet (code only, flag-gated by the
    caller)."""
    for a in atoms or []:
        if not isinstance(a, dict):
            continue
        ver = a["verification"] = a.get("verification") if isinstance(a.get("verification"), list) else []
        have = {(c.get("template"), c.get("target")) for c in ver
                if isinstance(c, dict) and c.get("type") == CHECK_TYPE}
        ver += [c for c in atom_checks(a, kind, sid, style) if (c["template"], c["target"]) not in have]
    return atoms


# ---------------------------------------------------------------- the proof, per call and per atom
def call_record(prompt, head, retries=0):
    """The "template" field of a builder's call in calls.jsonl: which prompt template built the prompt, which of its
    tags the prompt text really carries, and what the reply model made of the reply's JSON line."""
    ver, sha, _ = prompt_card()
    reply, errs = j2_types.validate(head) if head else (None, ["reply: no JSON line in the reply"])
    return {"prompt": ver, "prompt_sha": sha, "tags_present": tags_in(prompt), "reply_model": j2_types.MODEL,
            "reply_valid": reply is not None, "errors": errs, "retries": int(retries or 0)}


def _verdict(ok):
    return NOT_RECORDED if ok is None else "pass" if ok else "fail"


def atom_block(atom_id, calls, receipts):
    """The Template block of one work atom (atom/1): was it prompted through the template, did its reply pass the
    reply model, and does its output follow the artifact template. Computed here from the run's records only; each
    row reads "not recorded" when the run recorded nothing for it."""
    ver, sha, _ = prompt_card()
    mine = [c for c in calls or [] if c.get("atom") == atom_id and isinstance(c.get("template"), dict)]
    last = mine[-1] if mine else None
    t = (last or {}).get("template") or {}
    if last is None:
        prompt = {"version": ver, "used": NOT_RECORDED, "evidence": "no builder call recorded for this atom"}
        reply = {"model": j2_types.MODEL, "valid": NOT_RECORDED, "retries": None}
    else:
        miss = [x for x in TAGS if x not in (t.get("tags_present") or [])]
        same = t.get("prompt_sha") == sha
        prompt = {"version": t.get("prompt") or ver, "used": _verdict(not miss and same),
                  "evidence": f"call {last.get('id')}: tags {t.get('tags_present') or []}"
                              + (f"; missing {miss}" if miss else "")
                              + ("" if same else f"; prompt template changed since the run ({t.get('prompt_sha')})")}
        reply = {"model": t.get("reply_model") or j2_types.MODEL, "valid": _verdict(t.get("reply_valid")),
                 "retries": t.get("retries")}
        if t.get("reply_valid") is False and t.get("errors"):
            reply["errors"] = list(t["errors"])
    recs = [r for r in receipts or [] if r.get("atom") == atom_id and r.get("type") == CHECK_TYPE]
    recs = [r for r in recs if r.get("attempt") == max(x.get("attempt") or 0 for x in recs)] if recs else []
    if recs:
        worst = next((r for r in recs if r.get("pass") is False), recs[0])
        out = {"template": template_name(worst.get("template")) or NOT_RECORDED, "section": worst.get("target"),
               "match": _verdict(all(r.get("pass") for r in recs) if None not in
                                 [r.get("pass") for r in recs] else None),
               "evidence": f"{atom_id}:{worst.get('attempt')}", "note": worst.get("evidence")}
    else:
        out = {"template": NOT_RECORDED, "section": None, "match": NOT_RECORDED,
               "evidence": "no template-match receipt recorded for this atom"}
    return {"prompt": prompt, "reply": reply, "output": out}


def atom_blocks(atoms, calls, receipts):
    """{atom id: Template block} for every atom id given."""
    return {a: atom_block(a, calls, receipts) for a in atoms or []}


def output_template_tag(kind, atom, sid=None, style=False):
    """The <output_template> body: the artifact template this atom is held to, the part it writes and the rules code
    will check on it (the same rules the template-match check runs, so the builder is told exactly what is checked)."""
    out = {"template": template_name(kind), "artifact": kind}
    checks = atom_checks(atom or {}, kind, sid, style)
    out["parts"] = [{"section": c["target"], "rules": rules_for(c["template"], c["target"])
                     if c["template"] != "design" else rules_for("design", c["target"])} for c in checks]
    if not checks:
        out["parts"] = [{"section": sid, "rules": rules_for(kind, sid)}]
    out["sections_in_order"] = template_sections(kind)
    return json.dumps(out, ensure_ascii=False)
