"""Create a dependency-free GitHub Pages dashboard."""
from __future__ import annotations

import json
from pathlib import Path


def write_dashboard(destination: Path, payload: dict) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = f'''<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CME Gold Options OI</title><style>
body{{font-family:system-ui,sans-serif;max-width:1000px;margin:32px auto;padding:0 16px;color:#18212f;background:#f7f8fa}} h1{{margin-bottom:4px}}.muted{{color:#596579}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:24px 0}}.card{{background:#fff;padding:18px;border-radius:10px;border:1px solid #e3e7ed}}.value{{font-size:1.5rem;font-weight:700}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}table{{width:100%;border-collapse:collapse;background:#fff}}th,td{{padding:9px 12px;border-bottom:1px solid #e3e7ed;text-align:right}}th:first-child,td:first-child{{text-align:left}}@media(max-width:600px){{.cards,.grid{{grid-template-columns:1fr}}}}</style></head>
<body><h1>CME Gold Options Open Interest</h1><p class="muted" id="date"></p><div class="cards" id="cards"></div><div class="grid"><section><h2>Call OI สูงสุด</h2><table id="calls"></table></section><section><h2>Put OI สูงสุด</h2><table id="puts"></table></section></div><p class="muted">แหล่งข้อมูล: CME Daily Bulletin PG64 (อัปโหลดด้วยมือ) · End-of-day data · ไม่ใช่คำแนะนำการลงทุน · <a href="cot/">ดู CFTC COT รายสัปดาห์</a></p>
<script>const d={data};document.getElementById('date').textContent='Trade date: '+d.trade_date+' · อัปเดต: '+d.generated_at+' UTC';const s=d.summary;document.getElementById('cards').innerHTML=[['Call OI',s.total_call_oi.toLocaleString()],['Put OI',s.total_put_oi.toLocaleString()],['Put/Call ratio',s.put_call_ratio]].map(x=>`<div class="card"><div class="muted">${{x[0]}}</div><div class="value">${{x[1]}}</div></div>`).join('');function table(id,rows){{document.getElementById(id).innerHTML='<tr><th>Strike</th><th>Open Interest</th></tr>'+rows.map(r=>`<tr><td>${{r.strike.toLocaleString()}}</td><td>${{r.open_interest.toLocaleString()}}</td></tr>`).join('')}}table('calls',s.top_calls);table('puts',s.top_puts);</script></body></html>'''
    (destination / "index.html").write_text(html, encoding="utf-8")


def write_cot_dashboard(destination: Path, payload: dict) -> None:
    """Render the CFTC Commitments of Traders (COMEX Gold) page under docs/cot/."""
    destination.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = f'''<!doctype html>
<html lang="th"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CFTC COT — COMEX Gold</title><style>
body{{font-family:system-ui,sans-serif;max-width:1000px;margin:32px auto;padding:0 16px;color:#18212f;background:#f7f8fa}} h1{{margin-bottom:4px}}.muted{{color:#596579}}.cards{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:24px 0}}.card{{background:#fff;padding:18px;border-radius:10px;border:1px solid #e3e7ed}}.value{{font-size:1.5rem;font-weight:700}}table{{width:100%;border-collapse:collapse;background:#fff;margin-top:16px}}th,td{{padding:9px 12px;border-bottom:1px solid #e3e7ed;text-align:right}}th:first-child,td:first-child{{text-align:left}}@media(max-width:600px){{.cards{{grid-template-columns:1fr}}}}</style></head>
<body><h1>CFTC Commitments of Traders — COMEX Gold</h1><p class="muted" id="date"></p><div class="cards" id="cards"></div><table id="categories"></table><p class="muted">แหล่งข้อมูล: CFTC Disaggregated Futures &amp; Options Combined (รายสัปดาห์) · ไม่ใช่คำแนะนำการลงทุน · <a href="../">ดูแดชบอร์ด CME Gold Options</a></p>
<script>const d={data};document.getElementById('date').textContent='Report date: '+d.report_date+' · อัปเดต: '+d.generated_at+' UTC';const s=d.summary;const oiChange=s.change_open_interest>=0?'+'+s.change_open_interest.toLocaleString():s.change_open_interest.toLocaleString();document.getElementById('cards').innerHTML=[['Total Open Interest',s.open_interest.toLocaleString()],['เปลี่ยนแปลง OI (WoW)',oiChange]].map(x=>`<div class="card"><div class="muted">${{x[0]}}</div><div class="value">${{x[1]}}</div></div>`).join('');const labels={{producer_merchant:'Producer/Merchant',swap_dealers:'Swap Dealers',managed_money:'Managed Money',other_reportables:'Other Reportables'}};const fmt=v=>v>=0?'+'+v.toLocaleString():v.toLocaleString();document.getElementById('categories').innerHTML='<tr><th>ประเภทเทรดเดอร์</th><th>Long</th><th>Short</th><th>Net</th><th>Net Δ (WoW)</th></tr>'+Object.entries(s.categories).map(([key,c])=>`<tr><td>${{labels[key]||key}}</td><td>${{c.long.toLocaleString()}}</td><td>${{c.short.toLocaleString()}}</td><td>${{fmt(c.net)}}</td><td>${{fmt(c.net_change)}}</td></tr>`).join('');</script></body></html>'''
    (destination / "index.html").write_text(html, encoding="utf-8")

