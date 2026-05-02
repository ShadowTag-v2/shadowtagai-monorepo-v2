"""Configuration module — unified re-exports.

Consumers use two import patterns:
  1. ``from app.config import get_settings``  — returns AppSettings
  2. ``from app.config import AppSettings``   — the class itself
  3. ``from app.config import settings``      — AppSettings singleton
  4. ``from app.config import infra_settings`` — GCP/infra Settings singleton

This init bridges both config systems so every call-site works.
"""

from app.config.app_settings import AppSettings, SandboxSettings
from app.config.app_settings import get_app_settings as get_settings
from app.config.settings import Settings
from app.config.settings import settings as infra_settings

# `settings` is the AppSettings instance — monitoring, main.py, etc. expect
# attributes like `app_name`, `app_version`, `environment` from here.
settings = get_settings()

__all__ = [
    "AppSettings",
    "SandboxSettings",
    "Settings",
    "get_settings",
    "infra_settings",
    "settings",
]
