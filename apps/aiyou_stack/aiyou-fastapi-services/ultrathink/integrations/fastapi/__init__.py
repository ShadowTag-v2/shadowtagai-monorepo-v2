# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FastAPI integration: middleware, decorators, route enhancers."""

from ultrathink.integrations.fastapi.decorators import ultrathink_route, with_reasoning
from ultrathink.integrations.fastapi.middleware import UltrathinkMiddleware

__all__ = ["UltrathinkMiddleware", "ultrathink_route", "with_reasoning"]
