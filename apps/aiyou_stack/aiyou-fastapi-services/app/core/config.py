"""Configuration bridge — re-exports from app.core.settings.

28+ modules import ``from app.core.config import settings`` /
``get_settings``.  The canonical definitions live in
``app.core.settings``; this thin shim keeps every call-site working
without a mass-rename.
"""

from app.core.settings import Settings, get_settings, settings

__all__ = ["Settings", "get_settings", "settings"]
