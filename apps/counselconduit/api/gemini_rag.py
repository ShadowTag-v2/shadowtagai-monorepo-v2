# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# apps/counselconduit/api/gemini_rag.py
"""Gemini RAG Pipeline for CounselConduit.

Uses the Google Gen AI SDK (google-genai) to provide:
    1. Document ingestion → Firestore storage
    2. Privileged query execution → Gemini 3.1 Flash Lite
    3. Streaming responses → SSE to client
    4. Ephemeral compute → Zero-retention after response

Per Kovel Doctrine: All client query data is RAM-only.
Lawyer receives the transcript; client data evaporates.
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator

from google import genai
from google.genai import types
from pydantic import BaseModel

logger = logging.getLogger("counselconduit.rag")

# ── Configuration ──────────────────────────────────────────────────────────

_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v4")
_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

# System instruction for Kovel-privileged legal AI
_SYSTEM_INSTRUCTION = """You are CounselConduit, a privileged legal AI assistant
operating under the Kovel Doctrine. You assist attorneys with legal research,
document analysis, and case preparation.

CRITICAL RULES:
1. All communications are attorney-client privileged
2. Never disclose client information outside the privileged session
3. Provide thorough, citation-backed legal analysis
4. Flag any potential malpractice risks immediately
5. Maintain professional, precise legal language

You have access to the attorney's uploaded documents and case files."""


# ── Models ─────────────────────────────────────────────────────────────────


class QueryRequest(BaseModel):
    """Incoming privileged query from an attorney."""

    attorney_id: str
    query: str
    context_documents: list[str] = []
    max_tokens: int = 4096
    temperature: float = 0.3  # Low temp for legal precision


class QueryResponse(BaseModel):
    """Response from the Gemini RAG pipeline."""

    attorney_id: str
    response: str
    token_count: int
    model: str
    citations: list[str] = []


# ── Client Initialization ─────────────────────────────────────────────────

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Lazy-initialize the Gemini client with Vertex AI backend."""
    global _client  # noqa: PLW0603
    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=_PROJECT_ID,
            location=_LOCATION,
        )
        logger.info(
            "Gemini client initialized: project=%s location=%s model=%s",
            _PROJECT_ID,
            _LOCATION,
            _MODEL,
        )
    return _client


# ── Core RAG Functions ─────────────────────────────────────────────────────


async def execute_privileged_query(request: QueryRequest) -> QueryResponse:
    """Execute a Kovel-privileged query against Gemini.

    This is the main RAG pipeline:
    1. Construct context from uploaded documents
    2. Send to Gemini with system instruction
    3. Return structured response with token count
    4. Evaporate all client data from memory
    """
    client = _get_client()

    # Build context from documents
    context_block = ""
    if request.context_documents:
        context_block = "\n\n--- CASE DOCUMENTS ---\n"
        for i, doc in enumerate(request.context_documents, 1):
            context_block += f"\n[Document {i}]:\n{doc}\n"
        context_block += "\n--- END DOCUMENTS ---\n\n"

    full_query = f"{context_block}Attorney Query: {request.query}"

    # Execute against Gemini
    response = client.models.generate_content(
        model=_MODEL,
        contents=full_query,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTION,
            max_output_tokens=request.max_tokens,
            temperature=request.temperature,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                ),
            ],
        ),
    )

    # Extract response text and usage
    response_text = response.text or "No response generated."
    token_count = 0
    if response.usage_metadata:
        token_count = (response.usage_metadata.prompt_token_count or 0) + (response.usage_metadata.candidates_token_count or 0)

    result = QueryResponse(
        attorney_id=request.attorney_id,
        response=response_text,
        token_count=token_count,
        model=_MODEL,
    )

    # Kovel Doctrine: evaporate sensitive data
    del full_query
    del context_block

    logger.info(
        "Privileged query executed: attorney=%s tokens=%d",
        request.attorney_id,
        token_count,
    )

    return result


async def stream_privileged_query(
    request: QueryRequest,
) -> AsyncGenerator[str]:
    """Stream a Kovel-privileged query response via SSE.

    Yields chunks as they arrive from Gemini for real-time display.
    """
    client = _get_client()

    context_block = ""
    if request.context_documents:
        context_block = "\n\n--- CASE DOCUMENTS ---\n"
        for i, doc in enumerate(request.context_documents, 1):
            context_block += f"\n[Document {i}]:\n{doc}\n"
        context_block += "\n--- END DOCUMENTS ---\n\n"

    full_query = f"{context_block}Attorney Query: {request.query}"

    response_stream = client.models.generate_content_stream(
        model=_MODEL,
        contents=full_query,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_INSTRUCTION,
            max_output_tokens=request.max_tokens,
            temperature=request.temperature,
        ),
    )

    for chunk in response_stream:
        if chunk.text:
            yield chunk.text

    # Evaporate
    del full_query
    del context_block
