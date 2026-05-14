# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Vertex AI init and model accessors."""

from __future__ import annotations
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.language_models import TextEmbeddingModel


def init(project: str, location: str = "us-central1") -> None:
    vertexai.init(project=project, location=location)


def gemini(model: str = "gemini-1.5-flash") -> GenerativeModel:
    return GenerativeModel(model)


def embedding(model: str = "text-embedding-005") -> TextEmbeddingModel:
    return TextEmbeddingModel.from_pretrained(model)
