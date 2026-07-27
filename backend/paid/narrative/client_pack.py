"""
Beautiful client-facing paid file (HTML + Markdown).
Written as a senior consultant would package a paid orientation deliverable.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from backend.config import public_api_url


class ClientPackWriter:
    name = "Client Pack Writer"

    def write(
        self,
        *,
        project_root: Path,
        request_id: str,
        industry_id: str,
        business: str,
        idea_title: str,
        narrative: dict[str, Any],
        commercial: dict[str, Any] | None = None,
        paid: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        commercial = commercial or {}
        paid = paid or {}
        memo = narrative.get("memo") or {}
        products = narrative.get("product_templates") or []
        quality = narrative.get("quality") or {}
        offer = commercial.get("commercial_offer") or {}
        tariff = offer.get("tariff") or {}

        out_dir = project_root / "backend" / "workspace" / request_id / "10_client_pack"
        out_dir.mkdir(parents=True, exist_ok=True)

        md = self._markdown(
            request_id,
            industry_id,
            business,
            idea_title,
            memo,
            products,
            quality,
            tariff,
            narrative,
        )
        html_doc = self._html(
            request_id,
            industry_id,
            business,
            idea_title,
            memo,
            products,
            quality,
            tariff,
            narrative,
            offer,
        )

        md_path = out_dir / "CLIENT_ORIENTATION_MEMO.md"
        html_path = out_dir / "CLIENT_ORIENTATION_MEMO.html"
        json_path = out_dir / "narrative_engine.json"
        md_path.write_text(md, encoding="utf-8")
        html_path.write_text(html_doc, encoding="utf-8")
        json_path.write_text(
            json.dumps(
                {
                    "request_id": request_id,
                    "quality": quality,
                    "values": narrative.get("values"),
                    "products": products[:6],
                    "consistency": narrative.get("consistency"),
                    "memo": memo,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        # Also root-level convenience copy for last run
        root_html = project_root / "client-pack-latest.html"
        root_html.write_text(html_doc, encoding="utf-8")

        return {
            "markdown": str(md_path),
            "html": str(html_path),
            "json": str(json_path),
            "latest_html": str(root_html),
            "url": public_api_url(f"/api/v1/packages/{request_id}/result"),
        }

    def _markdown(
        self,
        rid: str,
        industry: str,
        business: str,
        idea: str,
        memo: dict[str, Any],
        products: list[dict[str, Any]],
        quality: dict[str, Any],
        tariff: dict[str, Any],
        narrative: dict[str, Any],
    ) -> str:
        lines = [
            f"# {memo.get('title') or 'Metrix Orientation Memo'}",
            "",
            f"**Request:** `{rid}` · **Industry:** `{industry}`",
            "",
            "---",
            "",
        ]
        for sec in memo.get("sections") or []:
            lines += [f"## {sec.get('title')}", "", sec.get("body") or "", ""]
        lines += [
            "## Recommended products",
            "",
        ]
        for p in products[:5]:
            lines.append(
                f"- **{p.get('name')}** — ${p.get('price_usd')} "
                f"(fit {p.get('recommend_score')}) — {p.get('when')}"
            )
        lines += [
            "",
            f"**Suggested tariff now:** {tariff.get('name', '—')} "
            f"(${tariff.get('price_usd', '—')})",
            "",
            "**Consult + Tech Write package:** $1290",
            "",
            "## Where to open first",
            "",
            "→ `12_package_result/YOUR_RESULT.html` (full client result)",
            "→ `10_consult_metareality/CONSULTATION.html`",
            "→ `11_tech_write_specsforge/TECH_SPEC.html`",
            "",
            "## Quality gates (internal)",
            "",
            f"- Client anchor rate: {quality.get('client_anchor_rate')}",
            f"- Anticlone pass: {quality.get('anticlone_pass')}",
            f"- Distortion rate: {quality.get('distortion_rate')}",
            "",
            "---",
            "",
            "*Prepared by Metrix AI. Not a guarantee of commercial outcomes. "
            "Numbers are client-supplied or model-bound.*",
            "",
        ]
        return "\n".join(lines)

    def _html(
        self,
        rid: str,
        industry: str,
        business: str,
        idea: str,
        memo: dict[str, Any],
        products: list[dict[str, Any]],
        quality: dict[str, Any],
        tariff: dict[str, Any],
        narrative: dict[str, Any],
        offer: dict[str, Any],
    ) -> str:
        def e(x: Any) -> str:
            return html.escape(str(x if x is not None else ""))

        sections = ""
        for sec in memo.get("sections") or []:
            sections += f"""
            <section class="card">
              <h2>{e(sec.get('title'))}</h2>
              <p>{e(sec.get('body'))}</p>
            </section>"""

        prows = ""
        for p in products[:5]:
            prows += (
                f"<tr><td><strong>{e(p.get('name'))}</strong></td>"
                f"<td>${e(p.get('price_usd'))}</td>"
                f"<td>{e(p.get('recommend_score'))}</td>"
                f"<td>{e(p.get('when'))}</td></tr>"
            )

        vals = narrative.get("values") or {}
        vchips = "".join(
            f'<span class="chip">{e(v.get("label"))}</span>'
            for v in (vals.get("values_present") or [])[:8]
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{e(memo.get('title') or 'Metrix Client Pack')}</title>
  <style>
    :root {{
      --bg: #071019;
      --card: #0f172a;
      --line: #1e293b;
      --accent: #5eead4;
      --accent2: #38bdf8;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --warn: #fbbf24;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; font-family: "Segoe UI", ui-sans-serif, system-ui, sans-serif;
      background: radial-gradient(900px 480px at 0% 0%, #134e4a33, transparent),
                  radial-gradient(700px 400px at 100% 0%, #1e3a5f44, var(--bg));
      color: var(--text); line-height: 1.65;
    }}
    .wrap {{ max-width: 880px; margin: 0 auto; padding: 2.25rem 1.25rem 4rem; }}
    .hero {{
      border: 1px solid var(--line); border-radius: 20px; padding: 1.5rem 1.6rem;
      background: linear-gradient(145deg, #0f172aee, #042f2e99);
      margin-bottom: 1.25rem;
    }}
    .badge {{
      display: inline-block; font-size: .72rem; font-weight: 700; letter-spacing: .04em;
      padding: .25rem .65rem; border-radius: 999px; background: #134e4a; color: var(--accent);
    }}
    h1 {{ font-size: 1.65rem; margin: .6rem 0 .4rem; letter-spacing: -0.02em; }}
    h2 {{ font-size: 1.05rem; color: var(--accent); margin: 0 0 .6rem; }}
    .muted {{ color: var(--muted); font-size: .92rem; }}
    .card {{
      background: var(--card); border: 1px solid var(--line); border-radius: 16px;
      padding: 1.15rem 1.35rem; margin-bottom: 0.9rem;
    }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }}
    @media (max-width: 700px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .kpi {{ font-size: 1.35rem; font-weight: 800; color: var(--accent); }}
    .kpi small {{ display: block; font-size: .72rem; color: var(--muted); font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .9rem; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: .5rem .35rem; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 600; }}
    .chip {{
      display: inline-block; margin: .2rem .25rem .2rem 0; padding: .2rem .55rem;
      border-radius: 999px; border: 1px solid #134e4a; color: var(--accent); font-size: .78rem;
    }}
    .price {{ font-size: 1.8rem; font-weight: 800; color: var(--accent2); }}
    footer {{ margin-top: 1.5rem; color: var(--muted); font-size: .82rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <span class="badge">METRIX AI · PAID ORIENTATION MEMO</span>
      <h1>{e(memo.get('title') or idea or 'Client Orientation')}</h1>
      <p class="muted">Request {e(rid)} · {e(industry)} · suggested tariff
        <strong>{e(tariff.get('name') or '—')}</strong></p>
      <p>{e(business[:320])}{'…' if len(business) > 320 else ''}</p>
    </div>

    <div class="grid">
      <div class="card"><div class="kpi">${e(tariff.get('price_usd') or '1290')}<small>Suggested path now</small></div></div>
      <div class="card"><div class="kpi">{e(quality.get('client_anchor_rate') if quality.get('client_anchor_rate') not in (None, '', 0, 0.0) else '—')}<small>Client anchor rate</small></div></div>
      <div class="card"><div class="kpi">$1290<small>Consult + Tech Write bundle</small></div></div>
      <div class="card"><div class="kpi">{e('pass' if quality.get('anticlone_pass') else 'review')}<small>Anticlone gate</small></div></div>
    </div>
    <p class="muted" style="margin:-0.2rem 0 1rem">Primary client file is in workspace folder
      <strong>12_package_result/YOUR_RESULT.html</strong> — open that first for the full Consult+Tech Write pack.</p>

    {sections}

    <section class="card">
      <h2>Value board</h2>
      <div>{vchips or '<span class="muted">No strong values yet</span>'}</div>
    </section>

    <section class="card">
      <h2>Product path</h2>
      <table>
        <tr><th>Product</th><th>Price</th><th>Fit</th><th>When</th></tr>
        {prows}
      </table>
      <p class="price" style="margin-top:1rem">${e(tariff.get('price_usd') or '')}</p>
      <p class="muted">{e(tariff.get('name') or '')} · {e(offer.get('next_human_step') or 'Review memo with client')}</p>
    </section>

    <footer>
      Generated by Metrix Narrative Semantic Engine (relations · probability map · anticlone · product closure).
      Not financial advice. Voids and open must-ask items remain binding honesty constraints.
    </footer>
  </div>
</body>
</html>"""
