"""Live page for the J2 department demo.

Run:  python j2_server.py                         opens http://127.0.0.1:8773
      STUDIO_MOCK=1 python j2_server.py           offline, scripted functions
Every response goes through redact(): API keys, tokens and .env values never reach the page.
"""
import argparse
import http.server
import json
import os
import re
import webbrowser
from urllib.parse import parse_qs, urlparse

import j2
import llm
from j2 import HERE, J2Run, clear_lessons

RUN = J2Run()
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def secrets():
    """Values the page must never show: every .env value and any env var whose name looks like a credential."""
    vals = {v for k, v in os.environ.items() if any(w in k.upper() for w in ("KEY", "TOKEN", "SECRET", "PASSWORD", "AUTH"))}
    try:
        with open(os.path.join(HERE, ".env"), encoding="utf-8") as f:
            vals |= {ln.split("=", 1)[1].strip().strip("\"'") for ln in f if "=" in ln and not ln.lstrip().startswith("#")}
    except OSError:
        pass
    return sorted((v for v in vals if len(v) >= 8), key=len, reverse=True)


def redact(text):
    for v in secrets():
        text = text.replace(v, "[redacted]")
    return text


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        if ctype in ("image/png", DOCX):     # a screenshot or a .docx: binary, no text to redact
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            if ctype == DOCX:
                self.send_header("Content-Disposition", 'attachment; filename="prd.docx"')
            self.end_headers()
            return self.wfile.write(body)
        data = redact(body if isinstance(body, str) else body.decode("utf-8", "replace")).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            with open(os.path.join(HERE, "j2_ui.html"), encoding="utf-8") as f:
                return self._send(200, f.read(), "text/html")
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        run = q.get("run")              # a saved run's folder name, opened read-only
        if u.path == "/api/state":
            since = int(q.get("since", "0"))
            snap = j2.saved_snapshot(run, since) if run else {**RUN.snapshot(since), "saved": None}
            return self._send(200, json.dumps(snap, ensure_ascii=False)) if snap else self._send(404, '{"error": "no such run"}')
        if u.path == "/api/runs":
            return self._send(200, json.dumps({"live": os.path.basename(RUN.dir), "runs": j2.list_runs()}))
        if u.path == "/api/call":       # one AI call in full, for the detail view's "full text" toggle
            d = j2.saved_dir(run) if run else RUN.dir
            rec = j2.call_record(d, int(q.get("id", "0") or 0))
            return self._send(200, json.dumps(rec, ensure_ascii=False)) if rec else self._send(404, '{"error": "no such call"}')
        if u.path.startswith("/shot/"):        # the screenshot Audit looked at for site vN
            d, n = (j2.saved_dir(run) if run else RUN.dir), u.path.rsplit("/", 1)[-1]
            path = os.path.join(d or "", "site", "shots", f"v{n}.png")
            if not (d and n.isdigit() and os.path.exists(path)):
                return self._send(404, "not found", "text/plain")
            with open(path, "rb") as f:
                return self._send(200, f.read(), "image/png")
        if u.path.startswith("/file/"):        # a document run's prd.md or prd.docx, to download
            d, name = (j2.saved_dir(run) if run else RUN.dir), u.path.rsplit("/", 1)[-1]
            o = j2.OUTPUTS[j2.saved_output(d) if run else RUN.output]
            allowed = [o["file"], o["file"][:-3] + ".docx"] if o.get("file") else []
            path = os.path.join(d or "", name)
            if name not in allowed or not os.path.exists(path):
                return self._send(404, "not found", "text/plain")
            with open(path, "rb") as f:
                data = f.read()
            return self._send(200, data, DOCX) if name.endswith(".docx") else \
                self._send(200, data, "text/markdown")
        if u.path.startswith("/site/") and run:
            d, key = j2.saved_dir(run), u.path.rsplit("/", 1)[-1]
            site = os.path.join(d or "", "site")
            num = lambda f: int(f[1:].split(".")[0])
            vs = sorted((f for f in os.listdir(site) if re.fullmatch(r"v\d+\.(?:html|md)", f)), key=num) \
                if d and os.path.isdir(site) else []
            name = vs[-1] if key == "latest" and vs else next((f for f in vs if f.split(".")[0] == key), None)
            if not name:
                return self._send(200, "<p style='font:14px system-ui;color:#667;padding:24px'>No site in this run.</p>",
                                  "text/html")
            with open(os.path.join(site, name), encoding="utf-8") as f:
                text = f.read()
            return self._send(200, j2.md_html(text) if name.endswith(".md") else text, "text/html")
        if u.path.startswith("/site/"):
            if not RUN.sites:
                return self._send(200, "<p style='font:15px system-ui;color:#667;padding:24px'>Your "
                                       f"{'document' if RUN.doc else 'website'} will appear here once it's built.</p>",
                                  "text/html")
            key = u.path.rsplit("/", 1)[-1]
            i = len(RUN.sites) if key == "latest" else int(key.lstrip("v") or 0)
            if not 1 <= i <= len(RUN.sites):
                return self._send(404, "not found", "text/plain")
            return self._send(200, j2.md_html(RUN.sites[i - 1], RUN.out["label"]) if RUN.doc else RUN.sites[i - 1],
                              "text/html")
        self._send(404, "not found", "text/plain")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/api/say":
            text = (body.get("text") or "").strip()
            if not text:
                return self._send(400, '{"error": "empty"}')
            ok = RUN.user_says(text)
            return self._send(200 if ok else 409, json.dumps({"ok": ok}))
        if self.path == "/api/playbooks/clear":    # the Playbooks tab's "Clear playbooks" (the page confirms first)
            return self._send(200, json.dumps({"ok": True, "cleared": j2.clear_playbooks()}))
        if self.path == "/api/lessons/clear":      # the Lessons tab's "Clear memory" (the page confirms first)
            return self._send(200, json.dumps({"ok": True, "cleared": clear_lessons()}))
        if self.path == "/api/output":           # the start page's output type, before the first message
            ok = RUN.set_output(body.get("type"))
            return self._send(200 if ok else 409, json.dumps({"ok": ok, "output": RUN.output}))
        if self.path == "/api/reset":
            if RUN.status == "running":
                return self._send(409, '{"ok": false}')
            RUN.reset()
            return self._send(200, '{"ok": true}')
        self._send(404, "{}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8773)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    url = f"http://127.0.0.1:{a.port}/"
    print("Mode:", "MOCK (scripted functions)" if llm.MOCK else f"{llm.PROVIDER} ({llm.MODEL})")
    print("Open:", url)
    if not a.no_browser:
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
