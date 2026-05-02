# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""pnkln_file_search.config.verticals — Vertical configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VerticalConfig:
    """Configuration for a search vertical."""

    name: str = ""
    corpus_display_name: str = ""
    description: str = ""
    embedding_model: str = "textembedding-gecko@003"
    chunk_size: int = 512
    chunk_overlap: int = 100
    similarity_top_k: int = 10
    extra: dict[str, Any] = field(default_factory=dict)


_VERTICALS: dict[str, VerticalConfig] = {
    "legal": VerticalConfig(
        name="legal",
        corpus_display_name="Legal Corpus",
        description="Legal document search vertical",
    ),
    "default": VerticalConfig(
        name="default",
        corpus_display_name="Default Corpus",
        description="Default search vertical",
    ),
}


def get_vertical_config(vertical: str = "default") -> VerticalConfig:
    """Get vertical configuration by name."""
    return _VERTICALS.get(vertical, _VERTICALS["default"])
