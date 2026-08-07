"""Security helpers + supabase sync redaction + online niche rework."""

from __future__ import annotations

from backend.security.hardening import sanitize_text, is_suspicious, strip_secrets_from_dict
from backend.services.supabase_sync import redact_for_store, _summarize, is_enabled
from backend.core.business_gen.online_niche_rework import (
    rework_online_niches,
    is_online_executor,
    ONLINE_NICHE_PROMPT,
)
from backend.core.business_gen.implement_model import build_implement_model


def test_sanitize_and_suspicious():
    assert "\x00" not in sanitize_text("hi\x00there")
    assert len(sanitize_text("x" * 50_000, max_len=100)) == 100
    assert is_suspicious("foo ../../../etc/passwd")
    assert not is_suspicious("normal business brief about saas")


def test_redact_store_hides_price():
    payload = {
        "module": "X",
        "hook_plan": {"price_usd": 790, "cta": "go"},
        "ops_commercial": {"price_usd": 790},
        "output": {
            "acceptance_forecast": {"acceptance_p": 0.7},
            "gencore": {"generation": "v5", "slots_ready": 4},
            "wayd": {"terminal": {"ship_gate": "near_core", "acceptance_p": 0.7}},
            "client_segmentation": {"primary": {"id": "b2b_knowledge"}},
            "user_path": {"path": {"id": "library_ship"}},
            "live_log": {"id": "log_x"},
            "originality": {"originality": 0.6},
        },
    }
    safe = redact_for_store(payload)
    assert "ops_commercial" not in safe
    assert "price_usd" not in (safe.get("hook_plan") or {})
    s = _summarize(safe)
    assert s.get("segment_id") == "b2b_knowledge"
    assert s.get("path_id") == "library_ship"
    # without env, disabled
    assert is_enabled() in (True, False)


def test_strip_secrets():
    d = strip_secrets_from_dict({"a": 1, "api_key": "x", "nested": {"token": "y", "ok": 2}})
    assert "api_key" not in d
    assert d["nested"]["ok"] == 2
    assert "token" not in d["nested"]


def test_online_niche_rework_executes():
    brief = (
        "Online architecture design library for IT product builders with "
        "niche cards, unit packs and warm builder channel."
    )
    assert is_online_executor(brief)
    assert "Orient" in ONLINE_NICHE_PROMPT or "wayD" in ONLINE_NICHE_PROMPT
    out = rework_online_niches(brief, lang="ru", multi_pass=2, project_name="Lib")
    assert out["online_executor"] is True
    assert len(out["niches_reworked"]) >= 5
    assert out["acceptance"]["acceptance_p"] is not None
    assert out["wayd"]["terminal"]["ship_gate"] in ("hold", "near_core", "ship")
    assert out["originality"]["originality"] >= 0.3


def test_implement_price_hidden_by_default():
    m = build_implement_model(lang="ru", expose_price=False)
    assert m.get("ops_commercial") is None
    assert m.get("price_redacted") is True
