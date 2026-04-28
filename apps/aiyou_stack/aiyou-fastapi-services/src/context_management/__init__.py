# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Context Window Management for AI Analysis Sessions

Tracks AI chat sessions with metadata, summaries, and context indices
to manage conversation history and ensure effective analysis workflows.
"""

from .api import router
from .models import AnalysisSession, ChatSummary, ContextIndex
from .service import ContextManager

__all__ = [
    "AnalysisSession",
    "ChatSummary",
    "ContextIndex",
    "ContextManager",
    "router",
]
