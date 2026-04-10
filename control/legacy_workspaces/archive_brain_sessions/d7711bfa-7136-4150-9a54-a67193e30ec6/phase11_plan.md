# Phase 11: Pitch Deck Engine Implementation Plan

## Goal
Implement the core business logic to transform ingested documents into a high-fidelity Pitch Deck (JSON/Markdown format) using Gemini 1.5 Pro, adhering to the "Isometric Cube" visual aesthetic.

## Architecture
1.  **Input:** Text/PDF content from `ingest` endpoint (stored in GCS).
2.  **Processing:** `deck_generator.py` uses Vertex AI (Gemini) to extract:
    -   Problem/Solution
    -   Market Size
    -   Visual Prompts (Dynamic, based on `PRODUCT_BUILD_PROMPT.md`)
3.  **Output:** Structured JSON payload returned to Frontend.
4.  **UI:** `DeckViewer.tsx` renders the JSON (and eventually generates images via Imagen if enabled, or placeholders).

## Steps
1.  **Backend (`judge-sentinel`):**
    -   Create `apps/judge-sentinel/agents/deck_generator.py`.
    -   Define `PitchDeck` Pydantic model.
    -   Implement `generate_deck(context: str)` function using Gemini.
    -   Create `POST /api/v1/generate-deck` endpoint.
2.  **Frontend (`shadowtag-web`):**
    -   Create `components/DeckViewer.tsx`.
    -   Connect to `/api/proxy/generate-deck`.

## Governance (Judge 6)
-   **Constraint:** Pitch Deck must NOT contain hallucinated metrics.
-   **Check:** Cross-reference generated stats with Source Doc (RAG check).
