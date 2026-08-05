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

    # ── Global stop rule ONCE (no kill/falsifier spam on every card)
    global_stop = _d(
        L,
        "Стоп-правило (одно на весь пилот): нет измеримого proof за 7–14 дней → откат на предыдущий шаг, без расширения scope.",
        "Single pilot stop-rule: no measurable proof in 7–14 days → roll back one step, no scope expansion.",
    )
    sections.append(
        {
            "id": "S1b",
            "kind": "stop_rule",
            "title": _d(L, "Стоп-правило пилота", "Pilot stop-rule"),
            "body": global_stop,
        }
    )

    # ── Decision warrants (from S1–S4) — no repeated kill text
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
                    f"Почему так: `{d.get('chosen')}` даёт измеримый exit и меньше scope creep.",
                    f"Why: `{d.get('chosen')}` yields a measurable exit with less scope creep.",
                ),
                "evidence_grade": "B",
                "feature": "decision_warrant",
            }
        )
    sections.append(
        {
            "id": "S2",
            "kind": "decision_warrants",
            "title": _d(L, "Обоснования решений", "Decision warrants"),
            "items": warrants,
        }
    )

    # ── Architecture STEPS A01–A12 (path steps, not “content dump”)
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
                "proof": c.get("proof"),
                "evidence_grade": "B" if c.get("niche") else "C",
                "feature": "path_step",
            }
        )
    sections.append(
        {
            "id": "S3",
            "kind": "path_steps",
            "title": _d(L, "Шаги архитектуры A01–A12", "Architecture steps A01–A12"),
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

    # Drop heavy epistemic $ valuation from client resume (noise)
    sections = [s for s in sections if s.get("kind") != "epistemic_status"]

    md = _render_rd_markdown(title, sections, lang=L)
    html = _render_resume_html(
        title,
        sections,
        lang=L,
        profile=profile,
        answers=answers,
        routing=route,
        skills=skills or [],
    )

    return {
        "module": "RDReaderConverter",
        "version": "1.1",
        "features": list(RD_FEATURES),
        "title": title,
        "generated_on": date.today().isoformat(),
        "lang": L,
        "sections": sections,
        "markdown": md,
        "html": html,
        "primary_surface": "resume_html",
        "note": _d(
            L,
            "Резюме консультации + техконтекст. Стоп-правило — один раз.",
            "Consultation resume + tech context. Stop-rule once.",
        ),
    }


def _render_resume_html(
    title: str,
    sections: list[dict[str, Any]],
    *,
    lang: str,
    profile: dict[str, Any],
    answers: dict[str, str],
    routing: dict[str, Any],
    skills: list[dict[str, Any]],
) -> str:
    """Compact HTML resume with technical context (last-block surface)."""
    L = lang
    stop = next((s for s in sections if s.get("kind") == "stop_rule"), None)
    warrants = next((s for s in sections if s.get("kind") == "decision_warrants"), None)
    steps = next((s for s in sections if s.get("kind") in ("path_steps", "design_claims")), None)
    exp = next((s for s in sections if s.get("kind") == "experiments"), None)

    def items_html(sec: dict | None, limit: int = 6) -> str:
        if not sec:
            return ""
        out = []
        for it in (sec.get("items") or [])[:limit]:
            if not isinstance(it, dict):
                continue
            head = it.get("title") or it.get("claim") or it.get("id") or it.get("decision_id") or "—"
            sub = it.get("warrant") or it.get("context") or it.get("hypothesis") or it.get("chosen") or ""
            out.append(
                f"<div class='row'><b>{_esc(it.get('id') or it.get('decision_id') or '')}</b> "
                f"{_esc(head)}<div class='m'>{_esc(sub)}</div></div>"
            )
        return "".join(out)

    tech_bits = [
        f"profile={_esc(profile.get('profile'))}",
        f"unit={_esc(profile.get('unit_id') or profile.get('unit'))}",
        f"route={_esc((routing or {}).get('domain'))}/{(routing or {}).get('depth')}",
        f"cash={_esc(answers.get('constraint_cash'))}",
        f"window={_esc(answers.get('constraint_time'))}",
        f"skills_loaded={len(skills or [])}",
    ]
    h_title = _d(L, "Резюме консультации", "Consultation resume")
    return f"""<!DOCTYPE html>
<html lang="{L}"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{_esc(h_title)} · {_esc(title)}</title>
<style>
body{{margin:0;font-family:system-ui,Segoe UI,sans-serif;background:#0a0f16;color:#e8eef7;padding:1.25rem;line-height:1.45}}
.wrap{{max-width:820px;margin:0 auto}}
.hero{{border:1px solid rgba(94,234,212,.28);border-radius:14px;padding:1rem 1.15rem;background:linear-gradient(135deg,rgba(94,234,212,.08),rgba(56,189,248,.05));margin-bottom:1rem}}
.eyebrow{{color:#5eead4;font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700}}
h1{{font-size:1.25rem;margin:.3rem 0}}
.m{{color:#94a3b8;font-size:.88rem}}
.card{{border:1px solid rgba(148,163,184,.14);border-radius:12px;padding:.85rem 1rem;background:#121a24;margin:.65rem 0}}
.card h3{{margin:0 0 .5rem;font-size:.95rem;color:#5eead4}}
.row{{padding:.35rem 0;border-bottom:1px solid rgba(148,163,184,.08);font-size:.9rem}}
.row b{{color:#38bdf8;font-family:ui-monospace,Consolas,monospace;margin-right:.4rem}}
.tech{{font-family:ui-monospace,Consolas,monospace;font-size:.75rem;color:#94a3b8;word-break:break-word}}
.stop{{border-color:rgba(251,191,36,.35);background:rgba(251,191,36,.06)}}
</style></head><body><div class="wrap">
<header class="hero">
  <div class="eyebrow">{_esc(h_title)}</div>
  <h1>{_esc(title)}</h1>
  <p class="m">{_esc(profile.get('metric') or '')}</p>
</header>
<div class="card stop"><h3>{_esc((stop or {}).get('title') or 'Stop')}</h3>
<p class="m">{_esc((stop or {}).get('body') or '')}</p></div>
<div class="card"><h3>{_d(L, 'Решения S1–S4', 'Decisions S1–S4')}</h3>{items_html(warrants, 4)}</div>
<div class="card"><h3>{_d(L, 'Шаги A01–A12 (путь, не «наполнение»)', 'Steps A01–A12 (path, not content dump)')}</h3>{items_html(steps, 8)}</div>
<div class="card"><h3>{_d(L, 'Тесты T1–T3', 'Tests T1–T3')}</h3>{items_html(exp, 3)}</div>
<div class="card"><h3>{_d(L, 'Технический контекст', 'Technical context')}</h3>
<pre class="tech">{_esc(' · '.join(tech_bits))}</pre>
<p class="m">{_d(L, 'Стек: FastAPI · skill_memory · smart_router · live_log · identity · GenCore', 'Stack: FastAPI · skill_memory · smart_router · live_log · identity · GenCore')}</p>
</div>
</div></body></html>
"""


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
