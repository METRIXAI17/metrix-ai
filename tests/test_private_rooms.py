"""Private rooms — unique link + password.

Skipped when pilot_private/ is absent (public clone / CI).
"""

from __future__ import annotations

import pytest

pytest.importorskip("pilot_private.private_rooms")
from pilot_private.private_rooms import PrivateRoomRegistry  # noqa: E402


def test_mint_unlock_wrong_password():
    reg = PrivateRoomRegistry()
    room = reg.mint(
        client_name="Test Co",
        industry="ai-agencies",
        lang="ru",
        base_url="http://127.0.0.1:8790",
    )
    assert room["ok"]
    assert room["password"]
    assert room["unique_url_path"].startswith("/w/")
    assert "Ваша уникальная ссылка" in room["message_for_client_ru"]
    assert "Не тратьте время на регистрацию" in room["message_for_client_ru"]
    assert "флагманские" in room["message_for_client_ru"] or "флагман" in room["message_for_client_ru"]

    bad = reg.unlock(room["slug"], "WRONG")
    assert bad["ok"] is False

    good = reg.unlock(room["slug"], room["password"])
    assert good["ok"] is True
    assert good["workspace"]["tests_left"] == 5
    assert good["workspace"]["reworks_left"] == 2
    assert good["workspace"]["return_url"]


def test_public_meta_welcome_copy():
    reg = PrivateRoomRegistry()
    room = reg.mint(client_name="Meta", lang="ru")
    meta = reg.public_meta(room["slug"])
    assert meta["ok"]
    w = meta["welcome"]
    assert "регистрацию" in w["no_reg"].lower() or "регистрац" in w["no_reg"]
    assert "DM" in w["pay_dm"] or "dm" in w["pay_dm"].lower() or "karimmetrix" in w["pay_dm"]
    assert meta["includes"]
