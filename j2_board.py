"""board/1: a shared message board so a blocked builder (atom A) can ask the atom that knows (atom B). B answers by
updating a shared artifact, A reads the answer and continues, and later builders reuse the same entry instead of
asking again (docs/j2-handoff.md).

Behind J2_BOARD=1 (default off): write and log_event are no-ops unless the flag is set, so the plain flow never
creates board.json or board.jsonl and plain_unchanged is unaffected. new_board/new_entry are pure, no disk access.
"""
import json
import os

SCHEMA = "board/1"
STATUSES = ("open", "answered", "unanswered", "refused")


def enabled():
    return os.environ.get("J2_BOARD") == "1"


def new_board():
    """An empty board/1 object."""
    return {"schema": SCHEMA, "entries": []}


def new_entry(entry_id, asked_by, atom, to, about, question, cycle, attempt):
    """A board entry as it is first asked: status open, nothing answered yet, used_by empty."""
    return {"id": entry_id, "asked_by": asked_by, "atom": atom, "to": to, "about": about, "question": question,
            "answer": None, "answered_by": None, "status": "open", "artifact_update": None, "used_by": [],
            "cycle": cycle, "attempt": attempt}


def write(run_dir, board):
    """board.json in the run folder. No-op unless J2_BOARD=1."""
    if not enabled():
        return
    with open(os.path.join(run_dir, "board.json"), "w", encoding="utf-8") as f:
        json.dump(board, f, indent=2, ensure_ascii=False)


def log_event(run_dir, event):
    """Appends one JSON line to board.jsonl. No-op unless J2_BOARD=1."""
    if not enabled():
        return
    with open(os.path.join(run_dir, "board.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
