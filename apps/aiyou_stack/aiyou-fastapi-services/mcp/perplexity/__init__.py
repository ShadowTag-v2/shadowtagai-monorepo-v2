"""Perplexity MCP Server - Governance Bridge for Comet Browser & AI Shopping

Integrates:
- Judge #6 compliance scoring for transaction governance
- SHADOWTAG watermarking for AI-generated content
- Apertus manifest logging for audit trail
"""

from mcp.perplexity.server import PerplexityMCPServer
from mcp.perplexity.tools import (
    governance_score,
    log_to_manifest,
    watermark_content,
)

__all__ = [
    "PerplexityMCPServer",
    "governance_score",
    "log_to_manifest",
    "watermark_content",
]
