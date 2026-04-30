import logging
import os
from typing import Any

import google.generativeai as genai
from google.api_core import exceptions

logger = logging.getLogger(__name__)


class GroundedAgent:
    def __init__(self, model_name: str = "gemini-pro", api_key: str | None = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not found in environment.")
        else:
            genai.configure(api_key=self.api_key)

        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)

    def generate_grounded_content(
        self,
        prompt: str,
        tools: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Generates content using the Gemini model, potentially using tools for grounding."""
        try:
            logger.info(f"Generating content for prompt: {prompt[:50]}...")

            # Configure tools (e.g., Google Search Retrieval) if provided
            # Note: In real usage, 'tools' would be a list of Tool objects or configuration
            request_options = {}
            if tools:
                request_options["tools"] = tools

            response = self.model.generate_content(prompt, **request_options)

            # Check for empty response or blocking
            if not response.parts:
                logger.warning("Model returned no content parts. Checking safety ratings...")
                if response.prompt_feedback:
                    logger.warning(f"Prompt Feedback: {response.prompt_feedback}")
                return {
                    "text": "",
                    "error": "No content generated (Safety or Empty)",
                    "citations": [],
                }

            text_content = response.text

            # Extract citations if available (Grounding)
            citations = []
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "grounding_metadata") and candidate.grounding_metadata:
                    # Parse grounding metadata for citations
                    for grounding_chunk in candidate.grounding_metadata.grounding_chunks:
                        if hasattr(grounding_chunk, "web"):
                            citations.append(
                                {
                                    "uri": grounding_chunk.web.uri,
                                    "title": grounding_chunk.web.title,
                                },
                            )

            return {"text": text_content, "citations": citations, "error": None}

        except exceptions.InvalidArgument as e:
            logger.error(f"Invalid Argument error: {e}")
            return {"text": "", "error": f"Invalid Argument: {e}", "citations": []}
        except Exception as e:
            logger.error(f"Unexpected error in generation: {e}")
            return {"text": "", "error": str(e), "citations": []}

    def basic_search_check(self, query: str):
        # Placeholder for 'error handling for empty search results' logic
        # If this method wraps a search tool, it should check if results exist before calling generate.
        if not query.strip():
            raise ValueError("Empty search query provided.")


if __name__ == "__main__":
    # Test stub
    logging.basicConfig(level=logging.INFO)
    agent = GroundedAgent()
    print("GroundedAgent initialized.")
