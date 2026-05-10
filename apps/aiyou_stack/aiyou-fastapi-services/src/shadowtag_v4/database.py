# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Re-export database primitives from the canonical ``src.database`` module.

Packages like ``activeshield_medical`` import from
``src.shadowtag_v4.database``.  This shim forwards those
references to the single canonical database module so that
there is only ONE engine / Base / session-factory in the process.
"""

from src.database import AsyncSessionLocal, Base, close_db, engine, get_db, init_db

__all__ = [
    "AsyncSessionLocal",
    "Base",
    "close_db",
    "engine",
    "get_db",
    "init_db",
]
