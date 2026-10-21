"""Send deeds, phase 1: a test email and a test Slack message built by code from a finished document.

No network code lives here. A send is dry-run (the default: nothing leaves, the deed stays open) or mock (an in-process
recorder, for tests). The recipient comes only from J2_TEST_EMAIL and J2_TEST_SLACK_TARGET, never from the brief, and
allowed() refuses anything else. Receipts hold a masked recipient and hashes: never an address in full, never a secret.
"""
import hashlib
import os
import re

DEEDS = {"send_email": {"channel": "email", "var": "J2_TEST_EMAIL", "words": "test email", "label": "Send a test email"},
         "send_slack_message": {"channel": "slack", "var": "J2_TEST_SLACK_TARGET", "words": "test Slack message",
                                "label": "Send a test Slack message"}}
TARGET_VAR = {d["channel"]: d["var"] for d in DEEDS.values()}
MODES = ("dry-run", "mock")      # live sending is not built yet: any other J2_SEND_MODE falls back to dry-run
SENT = []      # the mock recorder: every message a mock send "delivered" (tests read it; reset() empties it)

_SEND_EMAIL = re.compile(r"\b(?:send|forward|mail)\b[^.!?\n]{0,40}\be-?mail\b|\be-?mail\s+(?:it|them|this|me|the)\b", re.I)
_SEND_SLACK = re.compile(r"\b(?:send|post|share|message|dm|notify|ping|drop)\b[^.!?\n]{0,40}\bslack\b|"
                         r"\bslack\s+(?:it|them|this|me|the)\b", re.I)
_ADDRESS = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_SLACK_TARGET = re.compile(r"(?<![\w@])([#@][\w.-]+)")


def detect_deeds(*texts):
    """The sends the brief asks for, in order (email, then Slack); [] when none. A send verb must sit near "email" or
    "Slack": a mere mention (a Slack link in the footer, an email field) matches nothing."""
    text = " ".join(str(t or "") for t in texts)
    return [k for k, rx in (("send_email", _SEND_EMAIL), ("send_slack_message", _SEND_SLACK)) if rx.search(text)]


def mode():
    m = os.getenv("J2_SEND_MODE", "dry-run").strip().lower()
    return m if m in MODES else "dry-run"


def digest(s):
    return hashlib.sha256(str(s).encode("utf-8")).hexdigest()


def mask(to):
    """Enough to recognise the target, not enough to use it: d***@testlify.com, #t***."""
    to = str(to or "")
    local, at, domain = to.partition("@") if "@" in to[1:] else (to, "", "")
    return f"{local[:1]}***{at}{domain}" if at else f"{to[:2]}***"


def target(channel):
    """The one configured test target of a channel; "" when its variable is not set."""
    return (os.getenv(TARGET_VAR.get(channel, ""), "") or "").strip()


def allowed(channel, to):
    """(ok, reason): True only when `to` is the one configured test target. Everything is refused when the variable is
    unset. One recipient: no list, no cc or bcc, no CR or LF. Reasons name variables, never values."""
    var = TARGET_VAR.get(channel)
    if not var:
        return False, f"unknown channel {channel!r}"
    want = target(channel)
    if not want:
        return False, f"{var} is not set, so nothing is sent"
    if not isinstance(to, str):
        return False, "exactly one recipient is allowed"
    if re.search(r"[\r\n]", to):
        return False, "the recipient has a line break"
    to = to.strip()
    if re.search(r"[\s,;]", to):
        return False, "exactly one recipient is allowed"
    if to.lower() != want.lower():
        return False, f"the recipient is not the one in {var}"
    return True, ""


def names_other(kind, *texts):
    """True when the brief names a recipient other than the configured test target (an address, or a Slack channel or
    person). The brief never chooses the recipient; code uses this only to tell the Requester."""
    text = " ".join(str(t or "") for t in texts)
    want = target(DEEDS[kind]["channel"]).lower().lstrip("#@")
    named = _ADDRESS.findall(text) if kind == "send_email" else [m.lstrip("#@") for m in _SLACK_TARGET.findall(text)]
    return any(n.lower().lstrip("#@") != want for n in named)


def build(kind, name, text):
    """{subject, body} for a finished document, by code: its file name, hash and section headings. No model writes it."""
    heads = [m.group(1).strip() for m in re.finditer(r"^#{2}\s+(.+?)\s*#*\s*$", text, re.M)]
    lines = [f"J2 test send: {name} is ready.", f"File: {name} (sha256 {digest(text)[:12]})",
             "Sections: " + (", ".join(heads) if heads else "none")]
    if kind == "send_email":
        return {"subject": f"J2 test: {name}", "body": "\n".join(lines)}
    return {"subject": None, "body": " | ".join(lines)}


def deliver(msg):
    """Dry-run or mock only. Refuses a recipient that is not the configured test target, here as the last guard.
    Returns {sent, result, refused}."""
    ok, why = allowed(msg.get("channel"), msg.get("to"))
    if not ok:
        return {"sent": False, "result": "refused", "refused": why}
    if set(msg) - {"channel", "to", "subject", "body"}:
        return {"sent": False, "result": "refused", "refused": "only channel, to, subject and body are allowed (no cc or bcc)"}
    if mode() == "mock":
        SENT.append(dict(msg))
        return {"sent": True, "result": "mock", "refused": None}
    return {"sent": False, "result": "dry-run", "refused": None}


def send(kind, name, text, artifact=None):
    """Build the message, send it (dry-run or mock) to the configured target, and return the receipt record. The
    recipient is read from the environment here and nowhere else."""
    ch = DEEDS[kind]["channel"]
    msg = {"channel": ch, "to": target(ch), **build(kind, name, text)}
    res = deliver(msg)
    return {"deed": kind, "channel": ch, "mode": mode(), "to_masked": mask(msg["to"]) if msg["to"] else None,
            "to_hash": digest(msg["to"].lower())[:16] if msg["to"] else None, "subject": msg["subject"],
            "body_sha256": digest(msg["body"]), "body_chars": len(msg["body"]), "artifact": artifact,
            "artifact_sha256": digest(text), "transport": "mock-recorder" if res["result"] == "mock" else None,
            "sent": res["sent"], "result": res["result"], "refused": res["refused"]}


def read_record(run_dir, atom_id):
    """The latest send record of an atom in receipts.jsonl, or None."""
    import json
    path = os.path.join(run_dir, "receipts.jsonl")
    if not os.path.exists(path):
        return None
    rows = [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
    return next((r for r in reversed(rows) if r.get("atom") == atom_id and r.get("type") == "deed-send-record"), None)


def check(c, run_dir):
    """{actual, pass, evidence} for a deed-send check. It only reads: the record in receipts.jsonl and the artifact on
    disk. It never sends. pass None = not sent but nothing went wrong (dry run): the atom stays open."""
    rec = read_record(run_dir, c.get("atom"))
    if not rec:
        return {"actual": None, "pass": False, "evidence": "no send receipt in receipts.jsonl"}
    if rec.get("refused"):
        return {"actual": rec.get("result"), "pass": False, "evidence": f"not sent: {rec['refused']}"}
    kind, art = rec.get("deed"), rec.get("artifact")
    path = os.path.join(run_dir, art or "")
    if kind not in DEEDS or not art or not os.path.isfile(path):
        return {"actual": None, "pass": False, "evidence": "the receipt does not name a document that exists"}
    text = open(path, encoding="utf-8").read()
    if digest(text) != rec.get("artifact_sha256") or digest(build(kind, art, text)["body"]) != rec.get("body_sha256"):
        return {"actual": None, "pass": False, "evidence": f"{art} changed since the receipt was written"}
    want = target(rec.get("channel"))
    if not want or digest(want.lower())[:16] != rec.get("to_hash"):
        return {"actual": None, "pass": False, "evidence": f"the receipt's recipient is not the one in {TARGET_VAR[rec['channel']]}"}
    if rec.get("mode") == "dry-run" or not rec.get("sent"):
        return {"actual": rec.get("result"), "pass": None, "evidence": "Not sent (dry run)"}
    return {"actual": rec.get("result"), "pass": True,
            "evidence": f"{rec['result']} send recorded to {rec['to_masked']} ({rec['body_chars']} characters)"}
