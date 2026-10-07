"""Mechanical check of a built site, run by code before Audit (audit.md: "Run mechanical checks first").

Renders the page in headless Chrome at phone (360px) and desktop (1280px) width and reports what code can
measure: JavaScript errors, horizontal overflow, in-page links that point nowhere, external resources and size.
Forms: in the phone frame each form is filled with sample values and submitted (navigation is blocked). A form
fails when it has no submit control, throws a JS error on submit, or never fires its submit event although every
field is valid. Sample values a field's own rules reject (e.g. a pattern) are reported, not counted as a failure.
Design measurements for Audit's rubric (design()): text contrast against its background (WCAG AA: 4.5, or 3 for
large text), tap targets under TAP_MIN px at phone width (inline links inside text are exempt), images without alt,
h1 count and skipped heading levels, fonts in use, nav and in-page links, styled actions on the first screen.
screenshot() renders both widths side by side into one PNG for Audit to look at.
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
TAP_MIN = int(os.getenv("J2_TAP_MIN", "44"))   # px; WCAG 2.5.5 (AAA) and the common phone guideline
CAPTURE = ("<script>window.__j2e=[];addEventListener('error',e=>__j2e.push(String(e.message||e)));"
           "addEventListener('unhandledrejection',e=>__j2e.push('Unhandled promise rejection: '+String(e.reason)));"
           "</script>")
WRAPPER = """<!doctype html><html><body>%s
<script>
const out = {}, frames = [...document.querySelectorAll('iframe')];
let left = frames.length;
const SAMPLE = {email:'test@example.com', tel:'5550100', number:'1', range:'1', date:'2030-01-15', time:'10:00',
  'datetime-local':'2030-01-15T10:00', month:'2030-01', week:'2030-W03', url:'https://example.com', color:'#336699'};
const TAP_MIN = %d;
function design(w, phone){
  const d = w.document, cs = el => w.getComputedStyle(el);
  const vis = el => { const r = el.getBoundingClientRect(), c = cs(el); return r.width > 0 && r.height > 0 && c.visibility !== 'hidden' && c.display !== 'none' && +c.opacity !== 0; };
  const rgb = c => (c.match(/[\d.]+/g) || []).map(Number);
  const rel = ([r, g, b]) => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const bgOf = el => { for (; el && el.nodeType === 1; el = el.parentElement){ const c = cs(el);
      if (c.backgroundImage !== 'none') return null;          // text over an image or gradient: not measurable here
      const v = rgb(c.backgroundColor); if (v.length && (v.length < 4 || v[3] > 0.5)) return v.slice(0, 3); } return [255, 255, 255]; };
  const low = [], seen = new Set(); let checked = 0;
  const tw = d.createTreeWalker(d.body, NodeFilter.SHOW_TEXT);
  while (tw.nextNode() && checked < 400){ const el = tw.currentNode.parentElement;
    if (!tw.currentNode.textContent.trim() || !el || seen.has(el) || !vis(el)) continue; seen.add(el); checked++;
    const bg = bgOf(el); if (!bg) continue;
    const c = cs(el), a = rel(rgb(c.color)), b = rel(bg), ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    const size = parseFloat(c.fontSize), need = size >= 24 || (+c.fontWeight >= 700 && size >= 18.66) ? 3 : 4.5;
    if (ratio < need) low.push(`"${tw.currentNode.textContent.trim().slice(0, 30)}" ${ratio.toFixed(2)}:1 (needs ${need}:1)`); }
  const lv = [...d.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(vis).map(h => +h.tagName[1]);
  const out = {contrast: {checked, low_count: low.length, low: low.slice(0, 6)},
    headings: {h1: d.querySelectorAll('h1').length, skipped_levels: lv.filter((x, i) => i && x > lv[i - 1] + 1).length},
    images_without_alt: [...d.querySelectorAll('img:not([alt])')].map(i => (i.getAttribute('src') || '').slice(0, 60)).slice(0, 6),
    images: d.querySelectorAll('img').length,
    fonts: [...new Set([...d.querySelectorAll('body *')].filter(vis).slice(0, 800).map(e => cs(e).fontFamily.split(',')[0].replace(/["']/g, '').trim()))].slice(0, 8),
    nav: {nav_elements: d.querySelectorAll('nav').length, in_page_links: d.querySelectorAll('a[href^="#"]').length},
    first_screen_actions: [...d.querySelectorAll('a[href],button')].filter(vis).filter(el => el.getBoundingClientRect().top < w.innerHeight)
      .filter(el => { const v = rgb(cs(el).backgroundColor); return v.length && (v.length < 4 || v[3] > 0); })
      .map(el => (el.textContent || '').trim().slice(0, 30)).slice(0, 8)};
  if (phone){
    const small = [...d.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,[role=button]')].filter(vis)
      .filter(el => !(el.tagName === 'A' && cs(el).display === 'inline' && el.closest('p,li,td,span')))   // links inside text are exempt
      .map(el => [el, el.getBoundingClientRect()]).filter(([, r]) => r.height < TAP_MIN || r.width < TAP_MIN);
    out.small_tap_targets = {min_px: TAP_MIN, count: small.length, examples: small.slice(0, 6).map(([el, r]) =>
      `${el.tagName.toLowerCase()} "${(el.textContent || el.value || el.name || '').trim().slice(0, 25)}" ${Math.round(r.width)}x${Math.round(r.height)}`)};
  }
  return out;
}
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
    out[f.dataset.name].design = design(w, !!f.dataset.forms);
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
            f.write(WRAPPER % (frames, TAP_MIN))
        m = None
        for attempt in range(2):       # one retry: a rare Chrome hang mustn't count as "the site failed the check"
            try:
                p = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
                                    "--window-size=1400,1000", "--virtual-time-budget=4000", "--dump-dom",
                                    "file://" + os.path.join(tmp, "wrap.html")],
                                   capture_output=True, text=True, timeout=90)
            except subprocess.TimeoutExpired:
                out["note"] = "Chrome timed out after 90s (twice)."
                continue
            m = re.search(r'data-j2="([^"]*)"', p.stdout)
            if m:
                break
            out["note"] = "Chrome ran but the page never finished loading in both widths (twice)."
    if not m:
        return out
    out.pop("note", None)
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
        if "design" in r:
            out.setdefault("design", {})[name] = r["design"]
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


def design_problems(c):
    """Rubric items code can measure: {"R-2" contrast, "R-3" hierarchy, "R-6" tap targets, "R-7" alt text: [problems]}.
    Audit may not pass an item that has a measured problem. Empty when the render check didn't run."""
    d, out = c.get("design") or {}, {}
    for n, x in d.items():
        if x["contrast"]["low_count"]:
            out.setdefault("R-2", []).append(f"{n}: {x['contrast']['low_count']} text element(s) below WCAG AA contrast, "
                                             f"e.g. {'; '.join(x['contrast']['low'][:2])}")
    x = d.get("desktop") or d.get("phone")
    if x and x["headings"]["h1"] != 1:
        out.setdefault("R-3", []).append(f"{x['headings']['h1']} h1 headings (the page needs exactly one)")
    if x and x["headings"]["skipped_levels"]:
        out.setdefault("R-3", []).append(f"heading levels skipped {x['headings']['skipped_levels']} time(s)")
    t = (d.get("phone") or {}).get("small_tap_targets") or {}
    if t.get("count"):
        out["R-6"] = [f"{t['count']} tap target(s) under {t['min_px']}x{t['min_px']}px at 360px, e.g. "
                      + "; ".join(t["examples"][:3])]
    if x and x["images_without_alt"]:
        out["R-7"] = [f"{len(x['images_without_alt'])} image(s) without alt: {', '.join(x['images_without_alt'][:3])}"]
    return out


def screenshot(html, path):
    """Phone (360px) and desktop (1280px) first screens side by side in one PNG, for Audit. Returns path or None."""
    chrome = find_chrome()
    if not chrome:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "site.html"), "w", encoding="utf-8") as f:
            f.write(html)
        frames = "".join(f'<iframe src="site.html" style="width:{w}px;height:900px;border:0;margin-right:20px;'
                         f'background:#fff"></iframe>' for w in WIDTHS.values())
        with open(os.path.join(tmp, "shot.html"), "w", encoding="utf-8") as f:
            f.write(f'<!doctype html><body style="margin:0;background:#888;display:flex">{frames}</body>')
        try:
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                            f"--window-size={sum(WIDTHS.values()) + 40},900", "--virtual-time-budget=4000",
                            f"--screenshot={os.path.abspath(path)}", "file://" + os.path.join(tmp, "shot.html")],
                           capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:
            return None
    return path if os.path.exists(path) and os.path.getsize(path) > 0 else None


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
    dp = design_problems(c)
    parts.append("design measurements: " + ("; ".join(f"{k} {v[0]}" for k, v in dp.items()) if dp else "no problems"))
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
