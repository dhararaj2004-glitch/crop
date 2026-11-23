"""Builds a self-contained, printable HTML report (open in a browser -> Print -> Save as PDF)."""
import base64
import html
import io
from datetime import datetime

import numpy as np
from PIL import Image


def _png_b64(arr: np.ndarray, max_side: int = 420) -> str:
    img = Image.fromarray(arr)
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _ul(items):
    return "<ul>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ul>" if items else "<p>-</p>"


def build_html_report(d: dict) -> str:
    e = d.get("entry")
    plan = d.get("plan")
    esc = html.escape
    top_rows = "".join(
        f"<tr><td>{esc(n)}</td><td>{p*100:.1f}%</td></tr>" for n, p in d.get("top", [])
    )
    contacts = "".join(
        f"<li><b>{esc(c['name'])}</b>"
        + (f" - <b>{esc(c['phone'])}</b>" if c.get("phone") else "")
        + f"<br><small>{esc(c['detail'])}</small></li>"
        for c in d.get("contacts", [])
    )
    treat = ""
    if e:
        treat = f"""
        <h2>About this condition</h2>
        <p><b>Type:</b> {esc(e['type'])} &nbsp; <b>Cause:</b> {esc(e['pathogen'])} &nbsp; <b>Urgency:</b> {esc(e['urgency'])}</p>
        <p><b>Symptoms:</b> {esc(e['symptoms'])}</p>
        <p><b>Favoured by:</b> {esc(e['favours'])}</p>
        <h3>Cultural / field practices</h3>{_ul(e['cultural'])}
        <h3>Organic / biological options</h3>{_ul(e['organic'])}
        <h3>Chemical options (confirm locally)</h3>{_ul(e['chemical'])}
        <h3>Prevention</h3>{_ul(e['prevention'])}"""
    plan_html = ""
    if plan:
        plan_html = f"<h2>Action plan: {esc(plan['headline'])}</h2><p><i>{esc(plan['timeframe'])}</i></p>{_ul(plan['steps'])}"
    imgs = f"<img src='data:image/png;base64,{_png_b64(d['rgb'])}' height='220'> "
    if d.get("overlay") is not None:
        imgs += f"<img src='data:image/png;base64,{_png_b64(d['overlay'])}' height='220'>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Plant health report</title>
<style>body{{font-family:Arial,Helvetica,sans-serif;max-width:820px;margin:30px auto;color:#1b2a1b;line-height:1.45}}
h1{{color:#1b5e20}}h2{{color:#2e7d32;border-bottom:1px solid #c8e6c9;padding-bottom:4px}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:4px 10px}}
.box{{background:#f1f8e9;padding:10px 14px;border-radius:8px}}small{{color:#555}}</style></head><body>
<h1>Plant Health Report</h1>
<p><small>Generated {datetime.now().strftime('%d %b %Y, %H:%M')} by the Crop Disease Detector</small></p>
<div class="box"><p><b>Plant:</b> {esc(d.get('plant','-'))} &nbsp; <b>Condition:</b> {esc(d.get('condition','-'))}
&nbsp; <b>Confidence:</b> {esc(d.get('confidence_text','-'))}</p>
<p><b>Affected leaf area:</b> {d.get('severity',0):.1f}% &nbsp; <b>Grade:</b> {esc(d.get('grade','-'))}
&nbsp; <b>Leaf health score:</b> {max(0, 100 - d.get('severity',0)):.0f}/100</p>
<p><b>Location:</b> {esc(d.get('place') or 'not provided')}</p></div>
<p>{imgs}</p>
<h2>Possible conditions</h2><table><tr><th>Condition</th><th>Probability</th></tr>{top_rows or '<tr><td colspan=2>Model not loaded</td></tr>'}</table>
{plan_html}{treat}
<h2>Who to contact</h2><ul>{contacts}</ul>
<p><small>{esc(d.get('safety',''))}</small></p>
<p><small>This report is an AI-assisted estimate and does not replace diagnosis by a qualified expert.</small></p>
</body></html>"""
