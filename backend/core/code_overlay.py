"""Translate recursive methodology + specs into a same-engine Python overlay.

The overlay must parse, recurse, and return a Metrix-shaped artifact.
No stubs. Generation quality lives here — eval must not bounce on empty code.
"""

from __future__ import annotations

import ast
import re
from typing import Any


def _lit(s: str, n: int = 720) -> str:
    t = re.sub(r"\s+", " ", (s or "").strip())
    t = t.replace("\\", "\\\\").replace('"""', "'''")[:n]
    return t


def _ident(s: str, fallback: str = "slot") -> str:
    t = re.sub(r"[^a-zA-Z0-9_]+", "_", (s or "").strip())[:28].strip("_")
    if not t or t[0].isdigit():
        t = fallback
    return t or fallback


def build_overlay(
    *,
    ticker: str,
    problem: str,
    solution: str,
    specs: dict[str, Any] | None = None,
    answers: dict[str, str] | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    ru = not (lang or "ru").lower().startswith("en")
    specs = dict(specs or {})
    specs.setdefault("bound", problem or "named leak")
    specs.setdefault("kill", "новая линейка / обещание дохода / эссе вместо двух строк")
    specs.setdefault("slot", solution or "named slot")
    specs.setdefault("library", "concrete library already in hand")
    specs.setdefault("monday", (answers or {}).get("monday") or "one Monday number")
    specs.setdefault("owner", (answers or {}).get("who") or "named owner")
    src = _source(
        ticker=ticker,
        problem=_lit(problem),
        solution=_lit(solution),
        specs=specs,
        ru=ru,
    )
    quality = inspect_overlay(src, ticker=ticker)
    return {
        "module": "CodeOverlay",
        "ticker": ticker,
        "filename": f"{ticker.replace(' ', '_')}.py",
        "source": src,
        "quality": quality,
        "interface": ["Overlay.run", "Overlay.eval_help", "recurse", "generate"],
    }


def inspect_overlay(src: str, *, ticker: str = "") -> dict[str, Any]:
    """Structural eval. No exec of untrusted input — we generated this source."""
    reasons: list[str] = []
    score = 0.0
    try:
        tree = ast.parse(src or "")
        reasons.append("syntax_ok")
        score += 0.22
    except SyntaxError as exc:
        return {"ok": False, "score": 0.0, "reasons": [f"syntax:{exc.msg}"], "go": False}

    names: set[str] = set()
    funcs: set[str] = set()
    assigns: set[str] = set()
    has_recurse_call = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            names.add(node.name)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    funcs.add(item.name)
        elif isinstance(node, ast.FunctionDef):
            funcs.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    assigns.add(t.id)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "recurse":
            has_recurse_call = True
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "recurse":
            has_recurse_call = True

    if "Overlay" in names:
        score += 0.18
        reasons.append("class_overlay")
    if "run" in funcs:
        score += 0.12
        reasons.append("run")
    if "eval_help" in funcs:
        score += 0.08
        reasons.append("eval_help")
    if "recurse" in funcs or has_recurse_call:
        score += 0.14
        reasons.append("recurse")
    if "generate" in funcs:
        score += 0.08
        reasons.append("generate")
    if "TICKER" in assigns and (not ticker or ticker in src):
        score += 0.08
        reasons.append("ticker_bound")
    if "SPECS" in assigns:
        score += 0.06
        reasons.append("specs")
    banned = ("TODO", "NotImplemented", "raise NotImplemented", "pass  # stub")
    if any(b in src for b in banned):
        score -= 0.35
        reasons.append("stub")
    if "pass\n" in src and src.count("pass") > 2:
        score -= 0.1
        reasons.append("too_many_pass")
    score = max(0.0, min(1.0, score))
    go = score >= 0.72 and "stub" not in reasons
    return {"ok": go, "score": round(score, 3), "reasons": reasons, "go": go}


def _source(
    *,
    ticker: str,
    problem: str,
    solution: str,
    specs: dict[str, Any],
    ru: bool,
) -> str:
    spec_items = ",\n    ".join(
        f'"{_ident(k, "k")}": "{_lit(str(v), 220)}"' for k, v in list(specs.items())[:8]
    )
    monday = _lit(str(specs.get("monday") or "Monday number"), 80)
    owner = _lit(str(specs.get("owner") or "owner"), 80)
    kill = _lit(str(specs.get("kill") or "new product line"), 160)
    library = _lit(str(specs.get("library") or "library"), 120)
    title = "надстройка" if ru else "overlay"
    return f'''# {ticker} — same engine overlay. Denser specs, same contour.
# Recursive methodology translated into code. Rooms, not a new product line.

from __future__ import annotations

from typing import Any

TICKER = "{_lit(ticker, 24)}"
PROBLEM = "{problem}"
SOLUTION = "{solution}"
SPECS: dict[str, str] = {{
    {spec_items}
}}
KILL = "{kill}"
LIBRARY = "{library}"
OWNER = "{owner}"
MONDAY = "{monday}"
MAX_DEPTH = 4


def expand_spec(node: dict[str, Any]) -> list[dict[str, Any]]:
    """One recursive step: bound → kill / slot / library / Monday."""
    kind = str(node.get("kind") or "bound")
    text = str(node.get("text") or node.get("id") or "")
    if kind == "bound":
        return [
            {{"id": "kill", "kind": "kill", "text": KILL}},
            {{"id": "slot", "kind": "slot", "text": SOLUTION}},
            {{"id": "library", "kind": "library", "text": LIBRARY}},
        ]
    if kind == "slot":
        return [
            {{"id": "in", "kind": "edge", "text": "in: hours that must not burn"}},
            {{"id": "out", "kind": "edge", "text": "out: handoff with a name"}},
            {{"id": "owner", "kind": "owner", "text": OWNER}},
        ]
    if kind == "owner":
        return [
            {{"id": "monday", "kind": "metric", "text": MONDAY}},
            {{"id": "escalate", "kind": "rule", "text": "N minutes, then escalate"}},
        ]
    if kind in ("kill", "library", "edge", "metric", "rule"):
        return []
    return [{{"id": "leaf", "kind": "leaf", "text": text}}]


def recurse(node: dict[str, Any] | None = None, depth: int = 0, max_depth: int = MAX_DEPTH) -> dict[str, Any]:
    node = node or {{"id": "bound", "kind": "bound", "text": PROBLEM}}
    if depth >= max_depth:
        return {{"node": node, "leaf": True, "depth": depth, "children": []}}
    kids = expand_spec(node)
    if not kids:
        return {{"node": node, "leaf": True, "depth": depth, "children": []}}
    return {{
        "node": node,
        "leaf": False,
        "depth": depth,
        "children": [recurse(k, depth + 1, max_depth) for k in kids],
    }}


def flatten(tree: dict[str, Any], acc: list[str] | None = None) -> list[str]:
    acc = acc if acc is not None else []
    node = tree.get("node") or {{}}
    text = str(node.get("text") or "")
    if text:
        acc.append(text)
    for ch in tree.get("children") or []:
        flatten(ch, acc)
    return acc


class Overlay:
    """Same interface as the Metrix generator surface: run(brief) → artifact."""

    ticker = TICKER

    def eval_help(self, brief: str = "") -> dict[str, Any]:
        t = (brief or PROBLEM).lower()
        score = 0.4
        if any(w in t for w in ("лом", "host", "owner", "хозя", "касс", "slot")):
            score += 0.2
        if MONDAY:
            score += 0.1
        score = max(0.12, min(0.93, score))
        return {{"score": round(score, 3), "ticker": TICKER, "verdict": "sit" if score >= 0.5 else "ask"}}

    def run(self, brief: str = "") -> dict[str, Any]:
        tree = recurse()
        steps = flatten(tree)[:8]
        if not steps:
            steps = [SOLUTION, "sit in the slot", "Monday number"]
        return {{
            "id": TICKER.lower().replace(" ", "-"),
            "ticker": TICKER,
            "title": f"{title} · " + TICKER,
            "one_liner": SOLUTION,
            "break": PROBLEM,
            "move": "unusual sit into an existing slot — denser specs, same contour",
            "steps": steps,
            "anti": [KILL, "essay instead of two lines", "new product line"],
            "artifact_week": LIBRARY,
            "specs": dict(SPECS),
            "tree_depth": MAX_DEPTH,
            "eval": self.eval_help(brief or PROBLEM),
            "disclaimer": "Code of an agreed overlay. Not a yield promise.",
        }}


def generate(brief: str = "", **kwargs: Any) -> dict[str, Any]:
    _ = kwargs
    return Overlay().run(brief)


if __name__ == "__main__":
    art = generate(PROBLEM)
    print(art["ticker"], art["one_liner"])
'''
