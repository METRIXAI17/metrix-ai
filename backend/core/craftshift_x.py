"""CraftShift — Metrix derivative for X posts and video.

Not a hobby coach. One situation → one post + one video prompt.
Built with Metrix lines 3 (brand) and 6 (quality).
"""

from __future__ import annotations

from typing import Any

from backend.core.complexity_boundary import lattice
from backend.core.resonance import new_id, remember
from backend.core.voice import DISCLAIMER, HANDLE, X_URL, clip, first_sentence


def _name(brief: str) -> str:
    sit = first_sentence(brief, "сдвиг")
    words = [w for w in sit.replace(".", "").split() if len(w) > 3][:2]
    if not words:
        return "Door Cut"
    return " ".join(w.capitalize() for w in words)


def run(brief: str, *, kind: str = "both") -> dict[str, Any]:
    text = (brief or "").strip() or "нужен пост и кадр, без эссе"
    lat = lattice(text)
    name = _name(text)
    sit = first_sentence(text, "контур")
    post = (
        f"{name}.\n\n"
        f"{clip(sit, 110)}\n\n"
        "Не платформа. Объект, который можно взять.\n"
        "Один код открывает стор и производные. Друг не спрашивает паспорт дважды.\n\n"
        f"{HANDLE} · CraftShift — производная Metrix AI\n{X_URL}"
    )
    video = (
        "YouTube promo, 35–50s, 9:16 then 16:9 crop.\n"
        "Shot 1 (6s): emerald home studio, one monitor, snow-leopard with blue throat "
        "feathers beside a friend, tungsten lamp. Slow push-in.\n"
        "Shot 2 (6s): seven brass keys on velvet. One key lifts. Super: Metrix Store.\n"
        "Shot 3 (6s): a table of axes fills in — not an essay. Super: one poke.\n"
        "Shot 4 (6s): X post appears as an object on the desk, then a video frame.\n"
        "Shot 5 (8s): door code stamps into brass. VO: «создано в том числе с помощью "
        "производного проекта от ИИ Metrix AI — CraftShift».\n"
        "End card: mtrx.ai/store · t.me/metrix_ai_bot · @karimmetrix\n"
        "Voice: quiet, no guru, no yield promise. Friendship is the door."
    )
    art = {
        "id": new_id(),
        "kind": "craftshift.x",
        "lane": "craftshift",
        "title": name,
        "one_liner": "Пост для X. Кадр для видео. Производная Metrix AI.",
        "break": f"Ситуация «{clip(sit, 72)}» ещё не стала объектом для ленты.",
        "move": "CraftShift собирает пост и промпт ролика из той же решётки.",
        "post": post,
        "video_prompt": video,
        "lattice": lat,
        "steps": [
            "Имя работы — короткое, своё.",
            "Пост: 4–8 строк, объект, без платформы.",
            "Видео: 5 шотов, студия, ключ, таблица, дверь.",
            "Промо: «создано в том числе с помощью производного проекта от ИИ Metrix AI».",
        ],
        "artifact_week": "1 пост + 1 промпт ролика. Если не ставится в X — мимо.",
        "anti": ["Не тред-эссе.", "Не обещать доходность.", "Не прятать происхождение от Metrix."],
        "disclaimer": DISCLAIMER,
        "promo_line": "Создано в том числе с помощью производного проекта от ИИ Metrix AI.",
        "wow": f"{name} — объект на стол. Не стратегия в Notion.",
        "meta": {"engine": "metrix_ai", "derivative": "craftshift", "kind": kind},
    }
    remember(art)
    return art
