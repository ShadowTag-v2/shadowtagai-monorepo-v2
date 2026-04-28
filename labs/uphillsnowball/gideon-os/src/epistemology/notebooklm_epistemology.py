# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Cor.NotebookLM 6-Step Epistemology Engine.

The Epistemological Crucible. Applied during KAIROS Auto-Dream and Vanguard Scout.
If you can't state a book's central argument in two sentences, you haven't finished it.

6-Step Protocol:
  1. Core Argument Extraction
  2. Assumption Audit
  3. Personal Relevance Filter
  4. Steelman & Challenger
  5. Action Extractor (30-day horizon)
  6. Permanent Zettelkasten Note Builder
"""

from __future__ import annotations

import logging

from google import genai

logger = logging.getLogger("NotebookLM-Crucible")


class EpistemologicalCrucible:
    """Runs the 6-Step Deep Read protocol against raw text.

    Extracts permanent knowledge atoms for the AlloyDB Zettelkasten.
    """

    def __init__(self, tenant_id: str) -> None:
        self.client = genai.Client()
        self.model = "gemini-3-pro-preview"
        self.tenant_id = tenant_id

    async def execute_6_step_extraction(self, raw_text: str, user_context: str) -> dict:
        """Execute the full 6-stage epistemological extraction pipeline.

        Args:
            raw_text: The source material to analyze.
            user_context: The user's current operational context for relevance filtering.

        Returns:
            A dict with 'argument', 'actions', and 'permanent_notes' keys.
        """
        logger.info("📚 [EPISTEMOLOGY] Initiating 6-Stage Deep Read...")

        # Step 1: Core Argument Extractor
        arg = await self._prompt(
            "Identify the single central argument in 2 sentences max. "
            "Identify 3-5 sub-arguments. For each, how strong is the evidence?\n\n"
            f"{raw_text}"
        )

        # Step 2: Assumption Auditor
        _assump = await self._prompt(
            f"Identify every significant unstated assumption. Which assumption, if wrong, collapses the thesis?\n\n{arg.text}"
        )

        # Step 3: Personal Relevance Filter
        _relevance = await self._prompt(
            f"Context: [{user_context}]. Which specific frameworks are directly applicable to this context?\n\n{raw_text}"
        )

        # Step 4: Steelman & Challenger
        _steelman = await self._prompt(
            "Steelman the central argument. Then build the strongest possible "
            "counter-argument citing external evidence. Does it hold up?\n\n"
            f"{raw_text}"
        )

        # Step 5: Action Extractor
        actions = await self._prompt(
            f"Generate 5 specific, immediately actionable changes for the next 30 days. Rank by Impact vs Friction.\n\n{raw_text}"
        )

        # Step 6: Permanent Note Builder
        notes = await self._prompt(
            f"Synthesize into 5 permanent Zettelkasten notes. State idea, connect domain, end with open question.\n\n{raw_text}"
        )

        logger.info("✅ [EPISTEMOLOGY] 6-Stage extraction complete.")

        return {
            "argument": arg.text,
            "actions": actions.text,
            "permanent_notes": notes.text,
        }

    async def _prompt(self, text: str):
        """Send a prompt to the Gemini model."""
        return await self.client.models.generate_content_async(model=self.model, contents=text)
