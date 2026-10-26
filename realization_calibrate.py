"""Calibrate the confidence judge on plans that already exist; nothing is planned or built.

python realization_calibrate.py j2-20261014-111512 [--pilot runs/realization-pilot-.../taprush] [--n 2]
    The plan today's J2 made for a saved run, next to the realization pilot's plan for the same charter.
python realization_calibrate.py --rejudge [--n 2]
    The latest realization pilot plan for every brief in scenarios/realization_briefs.json.

Each plan is judged n times. The item questions (the checklist) are written once per charter, so every plan for that
charter answers the same ones. Today's plan is translated as it stands, adding nothing: one build stage, no factors (it
lists none), each workflow delivering what it covered, its atom goal as goal, its completion check and atom checks as
done-test, and no certainty reading (operate; approach says so).
Writes runs/realization-calibrate-<time>/calibration.json and prints a comparison.
"""
import glob
import json
import os
import statistics
import sys
import time

import j2_realization as R
import realization_pilot as P

HERE = os.path.dirname(os.path.abspath(__file__))


def original_plan(run, cycle=1):
    """The run's first proposal in the realization shape, without adding anything it did not have."""
    with open(os.path.join(HERE, "runs", run, "workflows.json"), encoding="utf-8") as f:
        wfs = json.load(f)
    wfs = wfs if isinstance(wfs, list) else wfs.get("workflows", wfs)
    wfs = [w for w in wfs if w.get("cycle") == cycle]
    names = {}
    for w in wfs:   # dependencies name sections ("tr-start") or workflow ids ("W-1")
        names[w.get("id")] = w.get("name")
        if w.get("section"):
            names[w["section"]] = w.get("name")
        for o in w.get("outputs") or []:
            for tok in str(o).replace("#", " ").split():
                names.setdefault(tok, w.get("name"))
    out = []
    for w in wfs:
        a = (w.get("atoms") or [{}])[0]
        checks = "; ".join(v.get("text", "") for v in a.get("verification") or [])
        deps = [names.get(d) or names.get(str(d).replace("tr-", "")) for d in w.get("dependencies") or []]
        out.append({"name": w.get("name"), "stage": "build", "certainty": "operate", "certainty_signals": [],
                    "approach": "As proposed by today's Adaptation (no certainty reading).",
                    "goal": a.get("goal") or w.get("purpose"), "done_test": f"{w.get('completion_check')} Checks: {checks}",
                    "delivers": w.get("covers") or [], "informs": [], "inputs_from": [d for d in deps if d],
                    "experiment": None, "research": None})
    return {"certainty_assessment": None, "factors": [], "unplaced": [],
            "stages": [{"id": "build", "thinking": "making", "tiers": ["implementation"], "goal": "the page",
                        "done_test": "Audit passes", "method": None, "owns_factors": [], "inputs_from": []}],
            "workflows": out, "open_facts": [], "not_ready": []}


def judge_n(goal, plan, checklist, n, s):
    runs = []
    for _ in range(n):
        scores, faults = s.judge(goal, plan, checklist, lambda spec: R.mock_judge(spec))
        runs.append({"scores": scores, "faults": faults, "plan_confidence": R.rollup(plan, scores)[1]})
    return runs


def stats(runs):
    per = {}
    for r in runs:
        for name, sc in r["scores"].items():
            per.setdefault(name, []).append(sc["score"])
    spread = [max(v) - min(v) for v in per.values()]
    return {"plan_confidence": [r["plan_confidence"] for r in runs],
            "mean": statistics.mean(x for v in per.values() for x in v),
            "below": {n: v for n, v in per.items() if min(v) < R.THRESHOLD},
            "max_spread": max(spread), "mean_spread": statistics.mean(spread),
            "flips": sum(1 for v in per.values() if min(v) < R.THRESHOLD <= max(v)), "workflows": len(per)}


def describe(label, st):
    return "\n".join([
        f"\n{label}: {st['workflows']} workflows",
        "  plan confidence per judging: " + ", ".join(f"{x:.2f}" for x in st["plan_confidence"]),
        f"  mean workflow score {st['mean']:.2f}; spread between judgings: max {st['max_spread']:.2f}, "
        f"mean {st['mean_spread']:.3f}; workflows that flip across the gate: {st['flips']}",
        f"  below {R.THRESHOLD:.2f}: " + (", ".join(f"{n} ({'/'.join(f'{x:.2f}' for x in v)})"
                                            for n, v in st["below"].items()) or "none")])


def latest_pilot_plans():
    latest = {}
    for t in sorted(glob.glob(os.path.join(HERE, "runs", "realization-pilot-*", "*", "trace.json"))):
        latest[os.path.basename(os.path.dirname(t))] = t       # later runs win
    return latest


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    n = int(argv[argv.index("--n") + 1]) if "--n" in argv else 2
    s = R.Session()
    out, text = {}, ""
    if "--rejudge" in argv:
        briefs = {b["id"]: b for b in P.load_briefs()}
        for bid, path in latest_pilot_plans().items():
            if bid not in briefs:
                continue
            goal = briefs[bid]["charter"]
            with open(path, encoding="utf-8") as f:
                plan = json.load(f)["plan"]
            checklist = s.checklist(goal, lambda: json.dumps({"items": []}))
            runs = judge_n(goal, plan, checklist, n, s)
            out[bid] = {"trace": path, "checklist": checklist, "judgings": runs, "stats": stats(runs)}
            text += describe(briefs[bid]["label"], out[bid]["stats"])
    else:
        run = next(a for a in argv if not a.startswith("--") and "/" not in a and "\\" not in a)
        pilot = argv[argv.index("--pilot") + 1] if "--pilot" in argv else None
        with open(os.path.join(HERE, "runs", run, "goal.json"), encoding="utf-8") as f:
            goal = json.load(f)
        checklist = s.checklist(goal, lambda: json.dumps({"items": []}))
        orig = original_plan(run)
        runs = judge_n(goal, orig, checklist, n, s)
        out["original"] = {"run": run, "plan": orig, "checklist": checklist, "judgings": runs, "stats": stats(runs)}
        text += describe("Today's J2 plan (cycle 1)", out["original"]["stats"])
        if pilot:
            with open(os.path.join(pilot, "trace.json"), encoding="utf-8") as f:
                rp = json.load(f)["plan"]
            runs = judge_n(goal, rp, checklist, n, s)
            out["realization"] = {"plan": rp, "judgings": runs, "stats": stats(runs)}
            text += describe("Realization pilot plan", out["realization"]["stats"])
    d = os.path.join(HERE, "runs", "realization-calibrate-" + time.strftime("%Y%m%d-%H%M%S"))
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "calibration.json"), "w", encoding="utf-8") as f:
        json.dump({**out, "trail": s.trail, "calls": s.calls, "seconds": round(s.seconds, 1)}, f, ensure_ascii=False,
                  indent=1)
    print(text + f"\n\n{s.calls} judge calls, {s.seconds:.0f}s -> {d}")


if __name__ == "__main__":
    main(sys.argv[1:])
