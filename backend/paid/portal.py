"""
Paid portal payload + static HTML generator.

Commercial offer, tariff, payment link (placeholder), situation snapshot.
Served as file under project root for /app/ and written per request.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


def build_portal_payload(
    *,
    request_id: str,
    industry_id: str,
    business: str,
    idea_title: str,
    tangible: dict[str, Any],
    metrics: dict[str, Any] | None = None,
    questions: dict[str, Any] | None = None,
    paid: dict[str, Any] | None = None,
) -> dict[str, Any]:
    offer = (tangible or {}).get("commercial_offer") or {}
    return {
        "request_id": request_id,
        "industry_id": industry_id,
        "idea_title": idea_title,
        "business_excerpt": (business or "")[:280],
        "offer": offer,
        "situation_score": (metrics or {}).get("situation_score"),
        "top_leak": (metrics or {}).get("top_leak"),
        "must_ask": (questions or {}).get("must_ask") or [],
        "paid_status": (paid or {}).get("status"),
        "paid_score": (paid or {}).get("paid_score"),
        "reader_plain": ((paid or {}).get("reader") or {}).get("plain_summary"),
        "portal_path": f"/app/paid-portal.html?request_id={request_id}",
    }


def render_portal_html(payload: dict[str, Any]) -> str:
    offer = payload.get("offer") or {}
    tariff = offer.get("tariff") or {}
    payment = offer.get("payment") or {}
    catalog = offer.get("tariff_catalog") or []
    must = payload.get("must_ask") or []
    leak = payload.get("top_leak") or {}

    def esc(x: Any) -> str:
        return html.escape(str(x if x is not None else ""))

    rows = ""
    for t in catalog:
        rows += (
            f"<tr><td>{esc(t.get('name'))}</td>"
            f"<td>${esc(t.get('price_usd'))}</td>"
            f"<td>{esc(t.get('best_for'))}</td></tr>"
        )
    q_li = "".join(f"<li>{esc(q.get('question'))}</li>" for q in must[:6])
    includes = "".join(
        f"<li>{esc(x)}</li>" for x in (tariff.get("includes") or [])
    )

    ui = payload.get("ui_status") or {}
    ui_color = esc(ui.get("color") or "#fbbf24")
    ui_label = esc(ui.get("label") or "PREVIEW ONLY")
    ui_note = esc(ui.get("note") or "Orientation-grade. Not packageable.")
    sellable = ui.get("sellable")
    meaning_rows = ""
    for row in payload.get("metric_meaning_table") or []:
        meaning_rows += (
            f"<tr><td><strong>{esc(row.get('metric'))}</strong></td>"
            f"<td>{esc(row.get('means'))}</td>"
            f"<td class='muted'>{esc(row.get('does_not_mean'))}</td></tr>"
        )
    capital = payload.get("capital_snapshot") or {}
    cap_html = ""
    if capital:
        po = capital.get("per_orientation_usd") or {}
        cap_html = f"""
    <div class="card">
      <h2>Capital efficiency (snapshot)</h2>
      <p class="muted">Ops cost per orientation — model, not invoice</p>
      <table>
        <tr><th>Architecture</th><th>USD / run</th></tr>
        <tr><td>A Pure LLM cloud</td><td>${esc(po.get('A_pure_llm_cloud'))}</td></tr>
        <tr><td>B Hybrid</td><td>${esc(po.get('B_hybrid'))}</td></tr>
        <tr><td>C Metrix pipeline</td><td>${esc(po.get('C_metrix_architecture'))}</td></tr>
      </table>
      <p class="muted">Save vs LLM: {esc((capital.get('comparisons') or {}).get('savings_C_vs_A_pct'))}% ·
         <a href="/app/capital-efficiency.html" style="color:var(--accent)">full charts →</a></p>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Metrix Paid Portal · {esc(payload.get('idea_title'))}</title>
  <style>
    :root {{ --bg:#0b1220; --card:#121a2b; --accent:#5eead4; --text:#e2e8f0; --muted:#94a3b8; }}
    body {{ font-family: ui-sans-serif, system-ui, sans-serif; background:var(--bg); color:var(--text);
           margin:0; padding:2rem; line-height:1.5; }}
    .wrap {{ max-width:920px; margin:0 auto; }}
    .card {{ background:var(--card); border:1px solid #1e293b; border-radius:16px; padding:1.25rem 1.5rem; margin-bottom:1rem; }}
    h1 {{ font-size:1.5rem; margin:0 0 .5rem; }}
    h2 {{ font-size:1.1rem; color:var(--accent); margin:0 0 .75rem; }}
    .muted {{ color:var(--muted); font-size:.9rem; }}
    .price {{ font-size:2rem; color:var(--accent); font-weight:700; }}
    .btn {{ display:inline-block; background:var(--accent); color:#042f2e; font-weight:700;
            padding:.75rem 1.25rem; border-radius:999px; text-decoration:none; margin-top:.75rem; }}
    .btn.secondary {{ background:transparent; border:1px solid var(--accent); color:var(--accent); }}
    table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
    td,th {{ border-bottom:1px solid #1e293b; padding:.5rem; text-align:left; vertical-align:top; }}
    .badge {{ display:inline-block; padding:.15rem .5rem; border-radius:999px; background:#134e4a; color:var(--accent); font-size:.75rem; }}
    .status-pill {{ display:inline-block; padding:.35rem .75rem; border-radius:999px; font-weight:700; font-size:.8rem;
                    color:#0b1220; background:{ui_color}; margin-right:.5rem; }}
    .status-box {{ border-left:4px solid {ui_color}; padding-left:1rem; margin:.75rem 0; }}
    .warn {{ color:#fbbf24; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <span class="badge">Metrix AI · Paid Portal</span>
      <span class="status-pill">{ui_label}</span>
      <h1>{esc(offer.get('headline') or payload.get('idea_title'))}</h1>
      <div class="status-box">
        <p><strong>UI status:</strong> {ui_label}
           · sellable=<strong>{esc(sellable)}</strong></p>
        <p class="muted">{ui_note}</p>
        <p class="muted">raw paid_status={esc(payload.get('paid_status'))}
           · score={esc(payload.get('paid_score'))}
           · anti_down={esc(payload.get('anti_down_gate'))}
           · plan={esc(payload.get('plan_code'))}</p>
      </div>
      <p class="muted">request {esc(payload.get('request_id'))} · {esc(payload.get('industry_id'))}</p>
      <p>{esc(payload.get('business_excerpt'))}</p>
    </div>

    <div class="card">
      <h2>Коммерческое предложение</h2>
      <p><strong>Проблема (leak):</strong> {esc(leak.get('label') or offer.get('client_problem'))}</p>
      <p><strong>Решение (hypothesis):</strong> {esc(offer.get('proposed_solution'))}</p>
      <p><strong>Главный рычаг:</strong> {esc(offer.get('top_lever'))}</p>
      <p class="muted">{esc(payload.get('reader_plain'))}</p>
    </div>

    <div class="card">
      <h2>Рекомендуемый тариф</h2>
      <div class="price">${esc(tariff.get('price_usd'))}</div>
      <p><strong>{esc(tariff.get('name'))}</strong></p>
      <ul>{includes}</ul>
      <a class="btn" href="{esc(payment.get('checkout_url') or '#')}">Перейти к оплате (demo link)</a>
      <p class="muted">{esc(payment.get('note'))}</p>
    </div>

    <div class="card">
      <h2>Все тарифы showcase</h2>
      <table>
        <tr><th>Тариф</th><th>Цена</th><th>Для кого</th></tr>
        {rows}
      </table>
    </div>

    {cap_html}

    <div class="card">
      <h2>Что число значит / чего НЕ значит</h2>
      <table>
        <tr><th>Метрика</th><th>Значит</th><th>Не значит</th></tr>
        {meaning_rows or '<tr><td colspan="3" class="muted">Нет таблицы — введите 5 чисел в metrics form</td></tr>'}
      </table>
      <p class="muted">Форма «5 чисел» важнее 10 красивых графиков без данных.</p>
    </div>

    <div class="card">
      <h2>Перед полным пилотом — ответьте</h2>
      <ol>{q_li or '<li>Нет критичных вопросов — можно котировать</li>'}</ol>
      <a class="btn secondary" href="/app/">← Назад в Metrix</a>
      <a class="btn secondary" href="/app/capital-efficiency.html">Capital efficiency report</a>
    </div>
  </div>
  <script type="application/json" id="portal-data">{json.dumps(payload, ensure_ascii=False)}</script>
</body>
</html>
"""


def write_portal_files(
    project_root: Path,
    payload: dict[str, Any],
    *,
    request_id: str,
) -> dict[str, str]:
    """Write shared portal + per-request snapshot."""
    html_doc = render_portal_html(payload)
    portal_path = project_root / "paid-portal.html"
    portal_path.write_text(html_doc, encoding="utf-8")

    snap_dir = project_root / "backend" / "workspace" / request_id / "09_paid_portal"
    snap_dir.mkdir(parents=True, exist_ok=True)
    (snap_dir / "portal.html").write_text(html_doc, encoding="utf-8")
    (snap_dir / "offer.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {
        "portal_html": str(portal_path),
        "snapshot_html": str(snap_dir / "portal.html"),
        "offer_json": str(snap_dir / "offer.json"),
        "url": f"/app/paid-portal.html?request_id={request_id}",
    }
