# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""core/rag_evolve — LanceDB-backed RAG search with Prompt Repetition.

Provides corpus search using LanceDB vector similarity, and a RAG
generation path that applies prompt repetition (arXiv 2512.14982)
for non-reasoning models.

The module is used by:
  - scripts/gemini_agent_swarm.py (Autoresearch Triad)
  - LanceDB RAG Automator skill
  - Any agent needing grounded search + generation

Usage:
    from core.rag_evolve import search_corpus, rag_generate
    hits = search_corpus("my query", top_k=5)
    answer = await rag_generate("my query", hits)
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger("core.rag_evolve")

REPO_ROOT = Path(__file__).parent.parent
LANCEDB_PATH = REPO_ROOT / "data" / "lancedb" / "workspace_knowledge"

# Non-reasoning models where prompt repetition boosts accuracy
_NON_REASONING_MODELS = {
    "gemini-3.1-flash-lite-preview",
    "gpt-4.1",
    "gpt-4o-mini",
    "claude-3.5-haiku",
    "pplx-api",
}


def search_corpus(query: str, *, top_k: int = 8) -> list[dict]:
    """Search the LanceDB corpus for relevant documents.

    Falls back to an empty list if LanceDB is not available or empty.

    Returns:
        List of dicts with keys: doc_id, text, class, name, score
    """
    try:
        import lancedb
    except ImportError:
        logger.warning("lancedb not installed — returning empty corpus")
        return []

    if not LANCEDB_PATH.exists():
        logger.warning("LanceDB path does not exist: %s", LANCEDB_PATH)
        return []

    try:
        db = lancedb.connect(str(LANCEDB_PATH))
        tables = db.table_names()
        if "documents" not in tables:
            logger.warning("No 'documents' table in LanceDB")
            return []

        table = db.open_table("documents")

        # Embed query using Gemini Embedding API
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("No API key for embedding — falling back to FTS")
            return _fts_fallback(table, query, top_k)

        from google import genai

        client = genai.Client(api_key=api_key)
        resp = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=query,
        )
        query_vector = resp.embeddings[0].values

        results = table.search(query_vector).limit(top_k).to_pandas()
        return [
            {
                "doc_id": row.get("doc_id", ""),
                "text": row.get("text", ""),
                "class": "lancedb",
                "name": row.get("doc_id", ""),
                "score": row.get("_distance", 0.0),
            }
            for _, row in results.iterrows()
        ]

    except Exception as e:
        logger.error("LanceDB search failed: %s", e)
        return []


def _fts_fallback(table, query: str, top_k: int) -> list[dict]:
    """Full-text search fallback when embedding API is unavailable."""
    try:
        results = table.search(query, query_type="fts").limit(top_k).to_pandas()
        return [
            {
                "doc_id": row.get("doc_id", ""),
                "text": row.get("text", ""),
                "class": "fts",
                "name": row.get("doc_id", ""),
                "score": row.get("_score", 0.0),
            }
            for _, row in results.iterrows()
        ]
    except Exception:
        logger.warning("FTS fallback also failed")
        return []


def _apply_rag_prompt_repetition(
    system_prompt: str,
    user_content: str,
    model_id: str,
) -> tuple[str, str]:
    """Apply prompt repetition for non-reasoning models in RAG generation.

    Repeats the instruction at the end of user content to reduce
    attention drift. Zero cost, 1-8% accuracy improvement.

    Source: arXiv 2512.14982 (Leviathan, Kalman, Matias — Google Research)
    """
    if model_id not in _NON_REASONING_MODELS:
        return system_prompt, user_content

    repeated = (
        f"{user_content}\n\n---\n\n"
        f"[INSTRUCTION REPEAT — RAG GENERATION]\n"
        f"{system_prompt}\n\n"
        f"Use ONLY the context provided above. Cite sources by doc_id."
    )
    return system_prompt, repeated


async def rag_generate(
    query: str,
    context_hits: list[dict],
    *,
    model_id: str | None = None,
    system_prompt: str | None = None,
) -> dict:
    """Generate a RAG response using retrieved context + prompt repetition.

    Args:
        query: The user's query
        context_hits: Results from search_corpus()
        model_id: LLM model to use (default: env SWARM_MODEL)
        system_prompt: Custom system prompt (default: built-in RAG prompt)

    Returns:
        Dict with keys: answer, model, tokens, sources
    """
    model_id = model_id or os.environ.get("SWARM_MODEL", "gemini-3.1-flash-lite-preview")

    if not system_prompt:
        system_prompt = (
            "You are a knowledge assistant. Answer the query using ONLY the provided context. "
            "If the context doesn't contain enough information, say so explicitly. "
            "Always cite the doc_id of each source you reference."
        )

    # Assemble context from hits
    context_blocks = []
    for hit in context_hits:
        doc_id = hit.get("doc_id", "unknown")
        text = hit.get("text", "")[:2000]
        context_blocks.append(f"[{doc_id}] {text}")

    user_content = f"CONTEXT:\n{''.join(context_blocks) if context_blocks else '(no context available)'}\n\nQUERY: {query}"

    # Apply prompt repetition
    sys_prompt, user_msg = _apply_rag_prompt_repetition(system_prompt, user_content, model_id)

    try:
        import litellm

        response = await litellm.acompletion(
            model=model_id,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=4096,
            temperature=0.2,
        )

        content = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0

        return {
            "answer": content,
            "model": model_id,
            "tokens": tokens,
            "sources": [h.get("doc_id", "") for h in context_hits],
            "prompt_repetition_applied": model_id in _NON_REASONING_MODELS,
        }

    except ImportError:
        logger.warning("litellm not installed — returning stub response")
        return {
            "answer": f"[RAG stub] Query: {query} — litellm not installed",
            "model": model_id,
            "tokens": 0,
            "sources": [h.get("doc_id", "") for h in context_hits],
            "prompt_repetition_applied": False,
        }
    except Exception as e:
        logger.error("RAG generation failed: %s", e)
        return {
            "answer": f"[RAG error] {e!s}",
            "model": model_id,
            "tokens": 0,
            "sources": [],
            "prompt_repetition_applied": False,
        }
