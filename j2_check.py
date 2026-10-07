"""Mechanical check of a built site, run by code before Audit (audit.md: "Run mechanical checks first").

Renders the page in headless Chrome at phone (360px) and desktop (1280px) width and reports what code can
measure: JavaScript errors, horizontal overflow, in-page links that point nowhere, external resources and size.
Forms: in the phone frame each form is filled with sample values and submitted (navigation is blocked). A form
fails when it has no submit control, throws a JS error on submit, or never fires its submit event although every
field is valid. Sample values a field's own rules reject (e.g. a pattern) are reported, not counted as a failure.
Headless Chrome won't make a window narrower than 500px, so each width is an iframe inside a wrapper page.
It never judges content; Audit does that. If Chrome isn't found, it says so and Audit works from the code alone.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

WIDTHS = {"phone": 360, "desktop": 1280}
CAPTURE = ("<script>window.__j2e=[];addEventListener('error',e=>__j2e.push(String(e.message||e)));"
           "addEventListener('unhandledrejection',e=>__j2e.push('Unhandled promise rejection: '+String(e.reason)));"
           "</script>")
WRAPPER = """<!doctype html><html><body>%s
<script>
const out = {}, frames = [...document.querySelectorAll('iframe')];
let left = frames.length;
const SAMPLE = {email:'test@example.com', tel:'5550100', number:'1', range:'1', date:'2030-01-15', time:'10:00',
  'datetime-local':'2030-01-15T10:00', month:'2030-01', week:'2030-W03', url:'https://example.com', color:'#336699'};
function testForms(w){
  return [...w.document.forms].map((f, i) => {
    const r = {index: i + 1, has_submit: !!f.querySelector('button:not([type=button]):not([type=reset]),input[type=submit],input[type=image]'),
               submitted: false, invalid: [], errors_during: []};
    for (const el of f.elements){
      const t = (el.type || '').toLowerCase();
      if (el.disabled || ['submit','button','reset','hidden','file','image','fieldset'].includes(t)) continue;
      if (el.tagName === 'SELECT'){ const o = [...el.options].find(o => o.value); if (o) el.value = o.value; }
      else if (t === 'checkbox' || t === 'radio') el.checked = true;
      else if (!el.value) el.value = SAMPLE[t] || 'Test';
    }
    const before = (w.__j2e || []).length;
    const stop = e => { if (e.target === f){ r.submitted = true; e.preventDefault(); } };
    w.addEventListener('submit', stop);   // bubble phase on window: runs after the page's own handlers
    try { f.requestSubmit(); } catch (e) { (w.__j2e = w.__j2e || []).push('Form submit: ' + String(e)); }
    w.removeEventListener('submit', stop);
    r.invalid = [...f.elements].filter(x => x.willValidate && !x.checkValidity()).map(x => x.name || x.id || x.type).slice(0, 5);
    r.before = before;
    return r;
  });
}
frames.forEach(f => f.addEventListener('load', () => setTimeout(() => {
  let w;
  try {
    w = f.contentWindow; const d = w.document.documentElement;
    out[f.dataset.name] = {width: w.innerWidth, scroll_width: d.scrollWidth, errors: w.__j2e || []};
    if (f.dataset.forms) out[f.dataset.name].forms = testForms(w);
  } catch (e) { out[f.dataset.name] = {error: String(e)}; }
  setTimeout(() => {   // late errors from submit handlers
    try { const r = out[f.dataset.name]; (r.forms || []).forEach(x => { x.errors_during = (w.__j2e || []).slice(x.before); delete x.before; });
          r.errors = w.__j2e || r.errors; } catch (e) {}
    if (--left === 0) document.body.setAttribute('data-j2', JSON.stringify(out));
  }, 400);
}, 500)));
</script></body></html>"""


def find_chrome():
    for p in (os.getenv("J2_CHROME"), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chromium-browser")):
        if p and os.path.exists(p):
            return p
    return None


def static_checks(html):
    ids = set(re.findall(r'\bid\s*=\s*["\']?([^"\'\s>]+)', html))       # quoted or unquoted attribute
    anchors = set(re.findall(r'href\s*=\s*["\']?#([^"\'\s>]+)', html))
    return {"bytes": len(html.encode("utf-8")),
            "broken_in_page_links": sorted(a for a in anchors if a not in ids),
            "external_resources": sorted(set(re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)["\']', html))),
            "forms": len(re.findall(r"<form\b", html, re.I)), "scripts": len(re.findall(r"<script\b", html, re.I))}


def check(html):
    out = {"available": False, **static_checks(html)}
    chrome = find_chrome()
    if not chrome:
        out["note"] = "Chrome not found (set J2_CHROME); no render or script run."
        return out
    page = re.sub(r"(<head[^>]*>)", r"\1" + CAPTURE, html, count=1, flags=re.I)
    if page == html:
        page = CAPTURE + html
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "site.html"), "w", encoding="utf-8") as f:
            f.write(page)
        frames = "".join(f'<iframe data-name="{n}"{" data-forms=1" if n == "phone" else ""} src="site.html" '
                         f'style="width:{w}px;height:900px;border:0"></iframe>' for n, w in WIDTHS.items())
        with open(os.path.join(tmp, "wrap.html"), "w", encoding="utf-8") as f:
            f.write(WRAPPER % frames)
        try:
            p = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                                "--window-size=1400,1000", "--virtual-time-budget=4000", "--dump-dom",
                                "file://" + os.path.join(tmp, "wrap.html")],
                               capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            out["note"] = "Chrome timed out after 90s."
            return out
    m = re.search(r'data-j2="([^"]*)"', p.stdout)
    if not m:
        out["note"] = "Chrome ran but the page never finished loading in both widths."
        return out
    raw = json.loads(m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))
    errors = []
    for name, r in raw.items():
        if "error" in r:
            out[name] = {"note": r["error"]}
            continue
        out[name] = {"width": r["width"], "overflow_px": max(0, r["scroll_width"] - r["width"])}
        errors += [e for e in r["errors"] if e not in errors]
        if "forms" in r:
            out["form_results"] = [{**x, "ok": form_ok(x)} for x in r["forms"]]
    out.update(available=True, js_errors=errors)
    return out


def form_ok(x):
    """Works = has a submit control, no JS error on submit, and the submit event fired (or a field's own rules
    rejected the sample value, which says nothing about the site)."""
    return x["has_submit"] and not x["errors_during"] and (x["submitted"] or bool(x["invalid"]))


def form_problem(x):
    if not x["has_submit"]:
        return f"form {x['index']} has no submit button"
    if x["errors_during"]:
        return f"form {x['index']} throws on submit: {x['errors_during'][0]}"
    return f"form {x['index']} never submits although every field is valid"


def summary(c):
    """One line for the chat."""
    if not c.get("available"):
        return f"Mechanical check unavailable: {c.get('note')} Static: {c['bytes'] / 1000:.0f} KB."
    parts = []
    for n in WIDTHS:
        r = c.get(n) or {}
        if "overflow_px" in r:
            parts.append(f"{n} {r['width']}px: " + (f"overflows by {r['overflow_px']}px" if r["overflow_px"]
                                                    else "no horizontal overflow"))
    parts.append(f"JS errors: {'; '.join(c['js_errors'][:3]) if c['js_errors'] else 'none'}")
    parts.append(f"broken in-page links: {', '.join(c['broken_in_page_links']) or 'none'}")
    fr = c.get("form_results") or []
    if fr:
        bad = [form_problem(x) for x in fr if not x["ok"]]
        parts.append(f"forms: {len(fr) - len(bad)} of {len(fr)} submit" + (f" ({'; '.join(bad)})" if bad else ""))
    parts.append(f"{c['bytes'] / 1000:.0f} KB, {len(c['external_resources'])} external resources")
    return "Mechanical check by code: " + "; ".join(parts) + "."


def problems(c):
    if not c.get("available"):
        return []
    out = [f"{n} overflow {c[n]['overflow_px']}px" for n in WIDTHS if (c.get(n) or {}).get("overflow_px")]
    return (out + [f"JS error: {e}" for e in c["js_errors"]] + [f"broken link #{a}" for a in c["broken_in_page_links"]]
            + [form_problem(x) for x in c.get("form_results") or [] if not x["ok"]])


if __name__ == "__main__":   # python j2_check.py site.html [...]: print the mechanical check for each file
    import sys
    for path in sys.argv[1:] or sys.exit("usage: python j2_check.py site.html [...]"):
        with open(path, encoding="utf-8") as f:
            print(path, "->", summary(check(f.read())))
