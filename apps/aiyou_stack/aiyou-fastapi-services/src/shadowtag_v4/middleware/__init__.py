# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""shadowtag_v4.middleware — security middleware package.

Re-exports from the compat module and security submodule.
"""

from __future__ import annotations

from src.shadowtag_v4.middleware_compat import SecurityHeadersMiddleware

__all__ = ["SecurityHeadersMiddleware"]
