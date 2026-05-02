# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""shadowtag_v4.config — thin bridge to app.config.

Tests import ``from src.shadowtag_v4.config import Settings, get_settings``.
The canonical definitions live in ``app.config``; this shim re-exports them.
"""

from app.config import AppSettings as Settings
from app.config import get_settings

__all__ = ["Settings", "get_settings"]
