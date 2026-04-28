# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from src.config import Settings, settings
from src.config.settings import settings as settings_instance
from src.models import User


def test_settings_exports_singleton_instance() -> None:
    assert settings is settings_instance


def test_settings_coerces_release_style_debug_values() -> None:
    assert Settings(debug="release").debug is False
    assert Settings(debug="production").debug is False
    assert Settings(debug="debug").debug is True


def test_user_model_supports_password_backed_auth() -> None:
    user = User(
        user_id="redacted@shadowtag-v4.local",
        email="redacted@shadowtag-v4.local",
        hashed_password="[VAPORIZED_PWD]",
    )

    assert user.user_id == "redacted@shadowtag-v4.local"
    assert user.email == "redacted@shadowtag-v4.local"
    assert user.hashed_password == "[VAPORIZED_PWD]"
