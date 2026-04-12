#!/usr/bin/env python3
import logging
from typing import Any

import google.generativeai as genai

logger = logging.getLogger("GroundedAgent")


class GroundingError(Exception):
    """Raised when safety blockations or lack of candidates occur during generation."""

    pass


class GroundedAgent:
    """
    Agent implementation wrapper around genai.GenerativeModel.generate_content
    equipped with robust response.parts validation and integrated grounding metadata extraction.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-3.1-pro"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"GroundedAgent initialized with model: {model_name}")

    def generate_grounded_response(self, prompt: str) -> dict[str, Any]:
        """
        Executes Google Search grounded queries using generate_content, validating
        that the response contains valid parts and safety filters were not violated.
        Returns the stripped response payload along with extracted citations.
        """
        try:
            # Enable Google Search grounding dynamically via tools
            response = self.model.generate_content(
                prompt, tools=[genai.Tool(google_search=genai.GoogleSearch())]
            )
        except Exception as e:
            logger.error(f"Failed to reach Generative API: {e}")
            raise GroundingError(f"API Connection Failure: {e}") from e

        # 1. Error Handling: Check empty parts or blocks
        self._validate_response_safety(response)

        # 2. Extract Response text
        try:
            reply_text = response.text
        except ValueError as e:
            # response.text raises ValueError if parts are empty or blocked
            raise GroundingError("Failed to extract text from response parts.") from e

        # 3. Extract Citations & Grounding Metadata
        citations: list[dict[str, str]] = []
        try:
            # Depending on the GenAI SDK version, grounding metadata exists inside Candidate
            candidate = response.candidates[0]
            if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                metadata = candidate.grounding_metadata

                # If webSearchQueries is present
                getattr(metadata, "web_search_queries", [])

                # Standard grounding chunks (URIs and Titles)
                chunks = getattr(metadata, "grounding_chunks", [])
                for chunk in chunks:
                    if hasattr(chunk, "web"):
                        citations.append({"title": chunk.web.title, "uri": chunk.web.uri})
        except IndexError:
            logger.warning("No candidates found in response.")
        except Exception as e:
            logger.warning(f"Failed to extract grounding citations: {e}")

        return {"text": reply_text, "citations": citations, "validation_status": "success"}

    def _validate_response_safety(self, response: Any):
        """Internal helper to validate the prompt feedback structure."""
        if hasattr(response, "prompt_feedback") and response.prompt_feedback:
            block_reason = getattr(response.prompt_feedback, "block_reason", None)
            if block_reason and block_reason != 0:  # 0 implies no block
                raise GroundingError(
                    f"Prompt triggered safety filters. Reason Code: {block_reason}"
                )

        if not response.parts:
            # Fallback check on safety ratings if there are no parts at all
            ratings = [
                f"{rating.category}: {rating.probability}"
                for rating in getattr(response.candidates[0], "safety_ratings", [])
            ]
            raise GroundingError(f"Generation returned empty parts. Safety Evaluation: {ratings}")
