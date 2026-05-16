# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Embedding module for generating code and text embeddings"""

from .embedding_generator import EmbeddingGenerator
from .code_chunker import CodeChunker

__all__ = ["EmbeddingGenerator", "CodeChunker"]
