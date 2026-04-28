# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import logging

from pydantic import ValidationError

from atomic_pipeline.clients.gemini_client import GeminiClient, GeminiConfig, GeminiModel
from atomic_pipeline.schemas import IntelEvent

logger = logging.getLogger(__name__)


async def extract_intel_event(
    text: str,
    model_name: str = GeminiModel.GEMINI_20_FLASH.value,
) -> IntelEvent | None:
    """Calls Gemini to extract a structured IntelEvent from raw text.

    Args:
        text: The raw text content to be analyzed.
        model_name: The specific Gemini model to use. Defaults to Gemini 2.0 Flash.

    Returns:
        An IntelEvent object on success, or None if parsing or validation fails.

    """
    # Construct the prompt with the document text
    # Note: We use double braces {{ }} to escape them in the f-string for the JSON schema
    prompt = f"""You are a specialized intelligence processing service. Your task is to analyze the provided text and convert it into a structured JSON object based on the schema provided below.

Analyze the following document:
--- DOCUMENT START ---
{text}
--- DOCUMENT END ---

Your output MUST be a single, valid JSON object and nothing else. Do not include any explanatory text, markdown, or other characters before or after the JSON.

The JSON object must conform to the following schema:
{{
  "source_type": "Choose one from: regulation, news, rfp, competitor-doc, blog, draft_bill, lawsuit, guidance",
  "jurisdiction": "The ISO 3166-2 code for the relevant jurisdiction (e.g., 'US-CA', 'EU', 'GB'). If global or not applicable, use 'GLOBAL'.",
  "effective_date": "The date the event becomes effective in 'YYYY-MM-DD' format. If not present, use null.",
  "topic": ["A list of 1-3 specific, machine-readable topics in snake_case (e.g., 'ai_disclosure', 'data_residency')."],
  "change_type": "Choose one from: new_law, amendment, guidance, ruling, proposal, cancellation",
  "summary": "A concise, neutral, 2-3 sentence summary of the core event.",
  "impacts": ["A list of direct, first-order consequences or requirements for affected entities."],
  "risk_tags": ["A list of zero or more tags from this exact list: compliance_deadline, fine_per_violation, reputational_risk, operational_impact, new_opportunity"],
  "confidence": "Your confidence in the accuracy of the extraction, as a float between 0.0 and 1.0."
}}"""

    try:
        # Initialize configuration with the requested model
        # We try to use the enum if possible, otherwise pass the string (which might fail validation if not in Enum)
        try:
            model_enum = GeminiModel(model_name)
            config = GeminiConfig(
                model=model_enum,
                temperature=0.0,
            )  # Low temperature for extraction
        except ValueError:
            # Fallback or error if model_name is not in GeminiModel
            # For now, we'll log a warning and try to proceed if we can, or just default to Flash
            logger.warning(
                f"Model '{model_name}' not found in GeminiModel enum. Using default Gemini 2.0 Flash.",
            )
            config = GeminiConfig(model=GeminiModel.GEMINI_20_FLASH, temperature=0.0)

        async with GeminiClient(config) as client:
            # 1. Call the LLM with the prepared prompt.
            # We use json_mode=True if the client supports it via config (enable_json_mode is True by default in GeminiConfig)
            response = await client.generate(prompt)

            response_str = response.content
            if not response_str:
                logger.warning("Empty response from Gemini.")
                return None

            # 2. Parse the JSON response.
            # Clean up potential markdown code blocks if present
            if "```json" in response_str:
                response_str = response_str.split("```json")[1].split("```")[0].strip()
            elif "```" in response_str:
                response_str = response_str.split("```")[1].split("```")[0].strip()

            data = json.loads(response_str)

            # 3. Validate the data against the Pydantic schema.
            event = IntelEvent(**data)
            return event

    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        logger.warning(f"Failed to parse event: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in extract_intel_event: {e}")
        return None
