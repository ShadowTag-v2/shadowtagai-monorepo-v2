"""Core utilities and clients.

Lazy imports — heavy clients (ClaudeClient, VectorDB) are imported on
first access to prevent module-level side-effects (API key validation,
network calls) from blocking unrelated imports like app.core.config.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.claude_client import ClaudeClient
    from app.core.vector_db import VectorDB

__all__ = [
    "ClaudeClient",
    "VectorDB",
    "claude_client",
    "vector_db",
]


def __getattr__(name: str):
    """Lazy module-level attribute access."""
    if name == "ClaudeClient":
        from app.core.claude_client import ClaudeClient

        return ClaudeClient
    if name == "claude_client":
        from app.core.claude_client import claude_client

        return claude_client
    if name == "VectorDB":
        from app.core.vector_db import VectorDB

        return VectorDB
    if name == "vector_db":
        from app.core.vector_db import vector_db

        return vector_db
    raise AttributeError(f"module 'app.core' has no attribute {name!r}")
