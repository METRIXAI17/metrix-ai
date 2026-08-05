"""
R&D Reader-Converter — turns Core structure into justified research language.

Not a dump of templates: each decision is framed as hypothesis → rationale →
evidence → risk → next experiment (lab memo style).
"""

from __future__ import annotations

from datetime import date
from typing import Any


def _lang(lang: str) -> str:
    return "en" if (lang or "").lower().startswith("en") else "ru"


def _d(lang: str, ru: str, en: str) -> str:
    return en if _lang(lang) == "en" else ru


# R&D features we inject as first-class research dimensions
RD_FEATURES = (
    "decision_warrant",      # why this choice is justified
    "falsifiability",        # how we would kill it
    "evidence_grade",        # A/B/C evidence quality
    "transfer_risk",         # risk of wrong niche transfer
    "instrument_chain",      # what instruments prove the claim
    "author_stance",         # how author personality shows up
    "autonomy_band",         # what AI/assist may do alone
    "golden_example",        # reference specimen for quality
)


def convert_to_rd(
    *,
    core_report: dict[str, Any],
    personality: dict[str, Any] | None = None,
    routing: dict[str, Any] | None = None,
    skills: list[dict[str, Any]] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    """Build R&D memo (markdown + structured sections) from core deliverable."""
    L = _lang(lang)
    cr = core_report or {}
    title = cr.get("title") or "Core"
    profile = cr.get("profile") or {}
    arch = cr.get("architecture_cards") or []
    decisions = cr.get("decision_cards") or []
    tests = cr.get("concept_tests") or []
    value = cr.get("value_vs_core") or {}
    answers = cr.get("inferred_answers") or {}
    clog = cr.get("channel_log_7d") or {}
    pers = personality or {}
    route = routing or {}

    sections: list[dict[str, Any]] = []

    # ── Abstract
    abstract = _d(
        L,
        (
            f"Исследовательская записка по ядру «{title}». "
            f"Профиль `{profile.get('profile', '—')}`. "
            f"Цель: зафиксировать **обоснованность** выбранных решений, "
            f"критерии опровержения и следующий эксперимент. "
            f"Не мотивационный текст — lab memo для билдера."
        ),
        (
            f"Research memo for core «{title}». "
            f"Profile `{profile.get('profile', '—')}`. "
            f"Goal: lock **decision warrants**, falsifiers, and next experiment. "
            f"Not motivational copy — a lab memo for builders."
        ),
    )
    sections.append({"id": "S0", "kind": "abstract", "title": _d(L, "Абстракт", "Abstract"), "body": abstract})

    # ── Research questions
    rqs = [
        _d(L, f"RQ1 · Кто платит first cycle? → {answers.get('who_pays', '—')}", f"RQ1 · Who pays first cycle? → {answers.get('who_pays', '—')}"),
        _d(L, f"RQ2 · Какой unit доказуем за {answers.get('constraint_time', '21d')}? → {answers.get('unit_of_value', '—')}", f"RQ2 · Which unit is provable in {answers.get('constraint_time', '21d')}? → {answers.get('unit_of_value', '—')}"),
        _d(L, f"RQ3 · Какой kill на календаре снимает illusion of progress?", f"RQ3 · Which calendar kill removes illusion of progress?"),
    ]
    sections.append(
        {
            "id": "S1",
            "kind": "research_questions",
            "title": _d(L, "Исследовательские вопросы", "Research questions"),
            "items": rqs,
        }
    )

    # ── Decision warrants (from S1–S4)
    warrants = []
    for d in decisions:
        warrants.append(
            {
                "decision_id": d.get("id"),
                "title": d.get("title"),
                "chosen": d.get("chosen"),
                "resolved_as": d.get("resolved_as"),
                "warrant": _d(
                    L,
                    f"Обоснование: выбор `{d.get('chosen')}` минимизирует scope creep и даёт измеримый exit за пилот. "
                    f"Kill: {d.get('kill')}.",
                    f"Warrant: choosing `{d.get('chosen')}` minimises scope creep and yields a measurable pilot exit. "
                    f"Kill: {d.get('kill')}.",
                ),
                "evidence_grade": "B",  # structured inference, not field data
                "falsifier": d.get("kill"),
                "feature": "decision_warrant",
            }
        )
    sections.append(
        {
            "id": "S2",
            "kind": "decision_warrants",
            "title": _d(L, "Обоснования решений (warrants)", "Decision warrants"),
            "items": warrants,
        }
    )

    # ── Architecture as design claims
    claims = []
    for c in arch[:12]:
        claims.append(
            {
                "id": c.get("id"),
                "niche": c.get("niche"),
                "claim": c.get("title"),
                "context": c.get("context"),
                "instrument_chain": c.get("blocks"),
                "boundary": c.get("boundary"),
                "falsifier": c.get("failure"),
                "proof": c.get("proof"),
                "evidence_grade": "B" if c.get("niche") else "C",
                "transfer_risk": _d(
                    L,
                    f"Риск переноса с ниши «{c.get('niche')}» на другой ICP без sample.",
                    f"Transfer risk from niche «{c.get('niche')}» to another ICP without sample.",
                ),
                "feature": "instrument_chain",
            }
        )
    sections.append(
        {
            "id": "S3",
            "kind": "design_claims",
            "title": _d(L, "Дизайн-утверждения (architecture claims)", "Design claims"),
            "items": claims,
        }
    )

    # ── Experiments (calendar)
    experiments = []
    for t in tests:
        experiments.append(
            {
                "id": t.get("id"),
                "hypothesis": t.get("hypothesis"),
                "metric": t.get("metric"),
                "start": t.get("start_date"),
                "kill": t.get("kill_date"),
                "go": t.get("go_date"),
                "stop_rule": t.get("stop"),
                "go_rule": t.get("go"),
                "feature": "falsifiability",
            }
        )
    sections.append(
        {
            "id": "S4",
            "kind": "experiments",
            "title": _d(L, "Эксперименты и calendar kill", "Experiments & calendar kill"),
            "items": experiments,
        }
    )

    # ── Author stance (from personality product)
    if pers:
        sections.append(
            {
                "id": "S5",
                "kind": "author_stance",
                "title": _d(L, "Позиция автора (author stance)", "Author stance"),
                "body": pers.get("rd_paragraph") or pers.get("summary"),
                "axes": pers.get("axes") or {},
                "feature": "author_stance",
            }
        )

    # ── Autonomy band (context engineering / harness)
    auto_band = {
        "may_do_alone": _d(
            L,
            "Ранжирование ниш, сборка карточек, R&D memo, CSV/PDF pack, skill distill draft.",
            "Niche ranking, card assembly, R&D memo, CSV/PDF pack, skill distill draft.",
        ),
        "needs_human": _d(
            L,
            "Signer numbers (cash/days), implementation approval, live channel execution, final tune.",
            "Signer numbers (cash/days), implementation approval, live channel execution, final tune.",
        ),
        "success_criteria": answers.get("success_metric") or profile.get("metric"),
        "intent": pers.get("intent") or _d(L, "Собрать доказуемое ядро, не «контент ради контента».", "Ship a provable core, not content for its own sake."),
        "feature": "autonomy_band",
    }
    sections.append(
        {
            "id": "S6",
            "kind": "autonomy",
            "title": _d(L, "Полоса автономии (harness)", "Autonomy band (harness)"),
            "body": auto_band,
        }
    )

    # ── Routing note
    if route:
        sections.append(
            {
                "id": "S7",
                "kind": "routing",
                "title": _d(L, "Маршрут системы", "System route"),
                "body": route.get("narrative") or route.get("summary"),
                "path": route.get("path") or [],
            }
        )

    # ── Skills distilled
    if skills:
        sections.append(
            {
                "id": "S8",
                "kind": "skills",
                "title": _d(L, "Навыки из успешных прогонов", "Skills from successful runs"),
                "items": skills[:5],
            }
        )

    # ── Channel as field protocol
    sections.append(
        {
            "id": "S9",
            "kind": "field_protocol",
            "title": _d(L, "Полевой протокол (7-day log)", "Field protocol (7-day log)"),
            "body": {
                "touches": clog.get("touch_target"),
                "artifact": (clog.get("artifact") or {}).get("name"),
                "window": f"{clog.get('start_date')} → {clog.get('end_date')}",
                "rule": clog.get("rule"),
            },
        }
    )

    # ── Value as epistemic status
    sections.append(
        {
            "id": "S10",
            "kind": "epistemic_status",
            "title": _d(L, "Эпистемический статус ценности", "Epistemic status of value"),
            "body": {
                "realized_mid_usd": value.get("realized_mid_usd"),
                "band": value.get("band"),
                "verdict": value.get("verdict"),
                "note": value.get("honesty_note"),
                "evidence_grade": "B" if value.get("band") == "near_core" else "C",
            },
        }
    )

    md = _render_rd_markdown(title, sections, lang=L)
    html = _render_rd_html(title, sections, lang=L)

    return {
        "module": "RDReaderConverter",
        "version": "1.0",
        "features": list(RD_FEATURES),
        "title": title,
        "generated_on": date.today().isoformat(),
        "lang": L,
        "sections": sections,
        "markdown": md,
        "html": html,
        "primary_surface": "rd_html",
        "note": _d(
            L,
            "R&D reader — обоснования решений, не сырой MD-отчёт.",
            "R&D reader — decision warrants, not a raw MD dump.",
        ),
    }


def _render_rd_markdown(title: str, sections: list[dict[str, Any]], *, lang: str) -> str:
    lines = [
        f"# R&D Memo · {title}",
        "",
        f"_{'Лабораторная записка' if lang == 'ru' else 'Laboratory memo'} · {date.today().isoformat()}_",
        "",
    ]
    for s in sections:
        lines.append(f"## {s.get('id')} · {s.get('title')}")
        body = s.get("body")
        items = s.get("items")
        if isinstance(body, str) and body:
            lines.append(body)
            lines.append("")
        elif isinstance(body, dict):
            for k, v in body.items():
                if k == "feature":
                    continue
                lines.append(f"- **{k}:** {v}")
            lines.append("")
        if items:
            for it in items:
                if isinstance(it, str):
                    lines.append(f"- {it}")
                elif isinstance(it, dict):
                    head = it.get("title") or it.get("claim") or it.get("id") or it.get("decision_id") or it.get("name") or "—"
                    lines.append(f"### {head}")
                    for k, v in it.items():
                        if k in ("title", "claim", "feature") or v is None:
                            continue
                        lines.append(f"- **{k}:** {v}")
                    lines.append("")
            lines.append("")
    lines.append("---")
    lines.append(
        "Evidence grades: **A** field-proven · **B** structured inference · **C** exploratory."
        if lang == "en"
        else "Оценки evidence: **A** полевые данные · **B** структурный вывод · **C** exploratory."
    )
    return "\n".join(lines)


def _esc(s: Any) -> str:
    return (
        str(s if s is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _render_rd_html(title: str, sections: list[dict[str, Any]], *, lang: str) -> str:
    """Beautiful standalone HTML for on-screen reader + free PDF print."""
    cards = []
    for s in sections:
        inner = []
        body = s.get("body")
        items = s.get("items")
        if isinstance(body, str) and body:
            inner.append(f"<p class='rd-p'>{_esc(body)}</p>")
        elif isinstance(body, dict):
            inner.append("<ul class='rd-ul'>")
            for k, v in body.items():
                if k == "feature":
                    continue
                inner.append(f"<li><span class='k'>{_esc(k)}</span> {_esc(v)}</li>")
            inner.append("</ul>")
        if items:
            for it in items:
                if isinstance(it, str):
                    inner.append(f"<p class='rd-li'>· {_esc(it)}</p>")
                elif isinstance(it, dict):
                    head = it.get("title") or it.get("claim") or it.get("id") or it.get("name") or "—"
                    grade = it.get("evidence_grade") or ""
                    badge = f"<span class='grade g-{_esc(grade)}'>{_esc(grade)}</span>" if grade else ""
                    inner.append(f"<div class='rd-claim'><h4>{_esc(head)} {badge}</h4>")
                    for k, v in it.items():
                        if k in ("title", "claim", "feature", "evidence_grade") or v is None:
                            continue
                        inner.append(f"<div class='rd-row'><span class='k'>{_esc(k)}</span><span>{_esc(v)}</span></div>")
                    inner.append("</div>")
        cards.append(
            f"<section class='rd-sec' id='{_esc(s.get('id'))}'>"
            f"<div class='rd-sec-h'><span class='rd-id'>{_esc(s.get('id'))}</span>"
            f"<h3>{_esc(s.get('title'))}</h3></div>"
            f"{''.join(inner)}</section>"
        )

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>R&amp;D Memo · {_esc(title)}</title>
<style>
  :root {{
    --bg:#0a0f16; --card:#121a24; --line:rgba(94,234,212,.22);
    --text:#e8eef7; --muted:#94a3b8; --accent:#5eead4; --a2:#38bdf8; --gold:#fbbf24;
  }}
  * {{ box-sizing:border-box; }}
  body {{
    margin:0; font-family: ui-sans-serif, system-ui, Segoe UI, sans-serif;
    background: radial-gradient(ellipse at 20% 0%, #132033 0%, var(--bg) 55%);
    color:var(--text); line-height:1.55; padding:2rem 1.25rem 4rem;
  }}
  .wrap {{ max-width:860px; margin:0 auto; }}
  .hero {{
    border:1px solid var(--line); border-radius:16px; padding:1.4rem 1.5rem;
    background: linear-gradient(135deg, rgba(94,234,212,.08), rgba(56,189,248,.05));
    margin-bottom:1.25rem;
  }}
  .eyebrow {{ color:var(--accent); letter-spacing:.08em; text-transform:uppercase; font-size:.72rem; font-weight:700; }}
  h1 {{ font-size:1.45rem; margin:.35rem 0 .5rem; }}
  .meta {{ color:var(--muted); font-size:.9rem; }}
  .free-badge {{
    display:inline-block; margin-top:.6rem; padding:.2rem .55rem; border-radius:999px;
    background:rgba(251,191,36,.15); color:var(--gold); font-size:.75rem; font-weight:700;
  }}
  .rd-sec {{
    border:1px solid rgba(148,163,184,.14); border-radius:14px; padding:1rem 1.15rem;
    background:var(--card); margin-bottom:.85rem;
  }}
  .rd-sec-h {{ display:flex; gap:.65rem; align-items:baseline; margin-bottom:.55rem; }}
  .rd-id {{
    font-family: ui-monospace, Consolas, monospace; color:var(--a2); font-size:.8rem;
  }}
  h3 {{ margin:0; font-size:1.05rem; }}
  h4 {{ margin:.4rem 0 .35rem; font-size:.95rem; color:#f1f5f9; }}
  .rd-p {{ margin:.25rem 0; color:#dbe4f0; }}
  .rd-li {{ margin:.2rem 0; color:#cbd5e1; }}
  .rd-ul {{ margin:.2rem 0 .4rem 1rem; color:#cbd5e1; }}
  .rd-claim {{
    border-left:2px solid var(--accent); padding:.35rem 0 .35rem .75rem; margin:.45rem 0;
  }}
  .rd-row {{ display:grid; grid-template-columns: 120px 1fr; gap:.4rem; font-size:.9rem; margin:.15rem 0; }}
  .k {{ color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.04em; }}
  .grade {{
    display:inline-block; font-size:.68rem; padding:.05rem .4rem; border-radius:6px;
    border:1px solid rgba(148,163,184,.3); color:var(--muted); vertical-align:middle;
  }}
  .g-A {{ color:#86efac; border-color:rgba(134,239,172,.4); }}
  .g-B {{ color:var(--accent); border-color:rgba(94,234,212,.4); }}
  .g-C {{ color:var(--gold); border-color:rgba(251,191,36,.35); }}
  footer {{ margin-top:1.5rem; color:var(--muted); font-size:.82rem; }}
  @media print {{
    body {{ background:#fff; color:#0f172a; padding:.6cm; }}
    .rd-sec, .hero {{ border-color:#cbd5e1; background:#fff; break-inside:avoid; }}
    .k, .meta, .rd-id {{ color:#475569; }}
    h1,h3,h4,.rd-p,.rd-li,.rd-ul,.rd-row {{ color:#0f172a; }}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="eyebrow">Metrix · R&amp;D Reader</div>
      <h1>{_esc(title)}</h1>
      <p class="meta">{'Лабораторная записка с обоснованиями решений' if lang=='ru' else 'Laboratory memo with decision warrants'} · {date.today().isoformat()}</p>
      <span class="free-badge">{'FREE DOWNLOAD' if lang=='en' else 'БЕСПЛАТНО СКАЧАТЬ'}</span>
    </header>
    {''.join(cards)}
    <footer>
      Evidence: A field · B structured · C exploratory · Metrix AI Core · no auto-yield claims
    </footer>
  </div>
</body>
</html>
"""
