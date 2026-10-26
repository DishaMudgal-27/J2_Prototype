"""Realization pilot: plan and judge charters with j2_realization, outside J2. Nothing is built.

python realization_pilot.py                    all briefs in scenarios/realization_briefs.json
python realization_pilot.py sudoku phone       only these ids
python realization_pilot.py --no-web           research workflows not allowed (no outside sources)
STUDIO_MOCK=1 python realization_pilot.py      offline, scripted replies

Writes runs/realization-pilot-<time>/<id>/trace.json and report.md, and summary.md comparing the briefs.
"""
import json
import os
import sys
import time

import j2_realization as R

HERE = os.path.dirname(os.path.abspath(__file__))


def load_briefs(path=os.path.join(HERE, "scenarios", "realization_briefs.json")):
    with open(path, encoding="utf-8") as f:
        briefs = json.load(f)["briefs"]
    for b in briefs:
        if b.get("from_run"):
            with open(os.path.join(HERE, "runs", b["from_run"], "goal.json"), encoding="utf-8") as f:
                b["charter"] = json.load(f)
    return briefs


def summary(rows):
    out = ["# Realization pilot", "", "| Brief | Items | Stages | Workflows (research / decide / deliver) | "
           "Factors (brief / general / research) | Rounds | First → final plan confidence | Waiting on Identity | "
           "Not ready | Held | Faults left | Calls | Time |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for b, r in rows:
        if r is None:
            out.append(f"| {b['label']} | failed | | | | | | | | | | | |")
            continue
        p = r["plan"]
        wfs = R.lst(p.get("workflows"))
        kinds = [R.kind(w) for w in wfs]
        src = [f.get("source") for f in R.lst(p.get("factors")) if isinstance(f, dict)]
        first = R.rollup(r["rounds"][0]["plan"], r["rounds"][0]["scores"])[1]
        out.append(
            f"| {b['label']} | {len(b['charter'].get('done_when') or [])} | "
            f"{', '.join(s.get('id', '?') for s in R.lst(p.get('stages')))} | "
            f"{len(wfs)} ({kinds.count('research')} / {kinds.count('decide')} / {kinds.count('deliver')}) | "
            f"{src.count('brief')} / {src.count('general')} / {src.count('research')} | {len(r['rounds']) - 1} | "
            f"{first:.2f} → {r['plan_confidence']:.2f} | {len(r['waiting_on_identity'])} | {len(r['not_ready'])} | "
            f"{len(r['held'])} | "
            f"{len(r['plan_faults'])} | {r['calls']} | {r['seconds']:.0f}s |")
    return "\n".join(out) + "\n"


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):      # Windows consoles default to cp1252; reports use arrows and rupees
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    web = "--no-web" not in argv
    ids = [a for a in argv if not a.startswith("--")]
    briefs = [b for b in load_briefs() if not ids or b["id"] in ids]
    if not briefs:
        sys.exit(f"no briefs match {ids}")
    root = os.path.join(os.getenv("J2_RUNS_DIR") or os.path.join(HERE, "runs"),
                        "realization-pilot-" + time.strftime("%Y%m%d-%H%M%S"))
    print(f"{len(briefs)} brief(s), web {'on' if web else 'off'}, {R.llm.MODEL or 'mock'} -> {root}")
    rows = []
    for b in briefs:
        print(f"\n== {b['label']}")
        try:
            r = R.plan_goal(b["charter"], web=web, out_dir=os.path.join(root, b["id"]))
            print(f"  plan confidence {r['plan_confidence']:.2f}, {len(r['not_ready'])} not ready, "
                  f"{r['calls']} calls")
        except Exception as e:    # one failed brief must not lose the others
            print(f"  failed: {type(e).__name__}: {e}")
            r = None
        rows.append((b, r))
        os.makedirs(root, exist_ok=True)
        with open(os.path.join(root, "summary.md"), "w", encoding="utf-8") as f:
            f.write(summary(rows))
    print(f"\n{summary(rows)}")


if __name__ == "__main__":
    main(sys.argv[1:])
