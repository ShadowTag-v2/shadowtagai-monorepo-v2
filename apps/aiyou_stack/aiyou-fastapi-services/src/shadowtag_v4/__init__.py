# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""shadowtag_v4 — Compatibility shim.

Provides `shadowtag_v4.database` for packages that reference
the old ``src.shadowtag_v4.database`` import path.
Delegates to ``src.database`` which holds the canonical
SQLAlchemy engine, session factory, and Base declaration.
"""
