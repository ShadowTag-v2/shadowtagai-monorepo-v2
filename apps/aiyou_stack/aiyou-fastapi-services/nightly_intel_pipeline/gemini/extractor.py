"""Gemini Extractor - Semantic Intelligence Extraction
===================================================
Extracts structured IntelEvent objects from raw text using Gemini.
"""

import hashlib
import json
import time

import httpx
import structlog

from .config import GEMINI_INGESTION_CONFIG, estimate_cost
from .intel_event import IntelEvent
from .prompts import INTEL_EVENT_EXTRACTION_PROMPT, get_prompt_for_source_type

logger = structlog.get_logger(__name__)


class GeminiExtractor:
    """Extracts structured IntelEvent objects from raw text using Gemini.

    Uses Gemini Flash 2.0 for cost-efficient extraction (200x cheaper than Claude).
    """

    def __init__(self, config: dict | None = None):
        self.config = config or GEMINI_INGESTION_CONFIG
        self._client: httpx.Client | None = None
        self._total_cost = 0.0
        self._request_count = 0

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.Client(timeout=self.config["timeout"])
        return self._client

    def _build_url(self, model: str) -> str:
        """Build Gemini API URL"""
        base = self.config["base_url"]
        key = self.config["api_key"]
        return f"{base}/models/{model}:generateContent?key={key}"

    def _call_gemini(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> tuple[str, dict]:
        """Call Gemini API and return response.

        Args:
            prompt: Full prompt text
            model: Model to use (defaults to config)
            temperature: Temperature (defaults to config)
            max_tokens: Max tokens (defaults to config)

        Returns:
            Tuple of (response_text, usage_dict)

        """
        model = model or self.config["model"]
        temperature = temperature or self.config["temperature"]
        max_tokens = max_tokens or self.config["max_tokens"]

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        url = self._build_url(model)
        client = self._get_client()

        # Retry with backoff
        last_error = None
        for attempt in range(self.config["max_retries"]):
            try:
                response = client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()
                candidate = data["candidates"][0]
                content = candidate["content"]["parts"][0]["text"]

                # Extract usage
                usage = {}
                if "usageMetadata" in data:
                    usage = {
                        "input_tokens": data["usageMetadata"].get("promptTokenCount", 0),
                        "output_tokens": data["usageMetadata"].get("candidatesTokenCount", 0),
                    }

                    # Track cost
                    cost = estimate_cost(usage["input_tokens"], usage["output_tokens"], model)
                    self._total_cost += cost
                    self._request_count += 1

                return content, usage

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429:  # Rate limited
                    wait_time = self.config["retry_backoff"] ** attempt
                    logger.warning("gemini_rate_limited", attempt=attempt, wait_seconds=wait_time)
                    time.sleep(wait_time)
                else:
                    raise

            except httpx.TimeoutException as e:
                last_error = e
                wait_time = self.config["retry_backoff"] ** attempt
                logger.warning("gemini_timeout", attempt=attempt, wait_seconds=wait_time)
                time.sleep(wait_time)

        raise Exception(
            f"Gemini API failed after {self.config['max_retries']} retries: {last_error}",
        )

    def _parse_json_response(self, response: str) -> dict:
        """Parse JSON from Gemini response, handling markdown code blocks.

        Args:
            response: Raw response text

        Returns:
            Parsed JSON dict

        """
        text = response.strip()

        # Remove markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        return json.loads(text)

    def _detect_source_type(self, text: str, source_url: str) -> str:
        """Detect source type from content and URL.

        Args:
            text: Document text
            source_url: Source URL

        Returns:
            Source type string

        """
        rules = self.config.get("source_type_rules", {})

        for source_type, rule in rules.items():
            # Check URL patterns
            for pattern in rule.get("url_patterns", []):
                if pattern.lower() in source_url.lower():
                    return source_type

            # Check keywords
            text_lower = text.lower()
            keyword_matches = sum(1 for kw in rule.get("keywords", []) if kw.lower() in text_lower)
            if keyword_matches >= 2:  # Require at least 2 keyword matches
                return source_type

        return "unknown"

    def extract(
        self,
        text: str,
        source_url: str = "",
        content_id: str = "",
        source_type_hint: str | None = None,
    ) -> IntelEvent:
        """Extract structured IntelEvent from raw text.

        Args:
            text: Raw document text
            source_url: Source URL
            content_id: Original content identifier
            source_type_hint: Optional hint for source type

        Returns:
            IntelEvent with extracted data

        """
        if not self.config.get("enabled", True):
            logger.warning("gemini_extraction_disabled")
            return IntelEvent.from_raw_text(text, source_url, content_id)

        # Detect source type
        source_type = source_type_hint or self._detect_source_type(text, source_url)

        # Get appropriate prompt
        prompt_template = get_prompt_for_source_type(source_type)

        # Truncate text if too long
        max_tokens = self.config.get("max_tokens_per_doc", 50000)
        # Rough estimate: 4 chars per token
        max_chars = max_tokens * 4
        truncated_text = text[:max_chars] if len(text) > max_chars else text

        # Build prompt
        if "{document_text}" in prompt_template:
            prompt = prompt_template.format(document_text=truncated_text)
        elif "{paper_metadata}" in prompt_template:
            prompt = prompt_template.format(paper_metadata=truncated_text)
        elif "{repo_content}" in prompt_template:
            prompt = prompt_template.format(repo_content=truncated_text)
        else:
            prompt = INTEL_EVENT_EXTRACTION_PROMPT.format(document_text=truncated_text)

        try:
            # Call Gemini
            response_text, usage = self._call_gemini(prompt)

            # Parse response
            data = self._parse_json_response(response_text)

            # Create hash of original text
            text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

            # Build IntelEvent
            event = IntelEvent.from_dict(
                {
                    "source_url": source_url,
                    "original_content_id": content_id,
                    "raw_text_hash": text_hash,
                    "gemini_model": self.config["model"],
                    **data,
                },
            )

            logger.info(
                "intel_event_extracted",
                content_id=content_id,
                source_type=event.source_type.value,
                confidence=event.confidence,
                topic_tags=event.topic_tags,
            )

            return event

        except json.JSONDecodeError as e:
            logger.error("gemini_json_parse_error", content_id=content_id, error=str(e))
            # Return minimal event on parse failure
            return IntelEvent.from_raw_text(text, source_url, content_id)

        except Exception as e:
            logger.error("gemini_extraction_error", content_id=content_id, error=str(e))
            return IntelEvent.from_raw_text(text, source_url, content_id)

    def extract_batch(
        self,
        items: list[tuple[str, str, str]],
        source_type_hint: str | None = None,
    ) -> list[IntelEvent]:
        """Extract IntelEvents from multiple documents.

        Args:
            items: List of (text, source_url, content_id) tuples
            source_type_hint: Optional hint for source type

        Returns:
            List of IntelEvent objects

        """
        events = []
        batch_size = self.config.get("batch_size", 10)

        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]

            for text, source_url, content_id in batch:
                event = self.extract(
                    text=text,
                    source_url=source_url,
                    content_id=content_id,
                    source_type_hint=source_type_hint,
                )
                events.append(event)

            # Delay between batches
            if i + batch_size < len(items):
                delay = self.config.get("delay_between_batches", 1.0)
                time.sleep(delay)

        return events

    def get_stats(self) -> dict:
        """Get extraction statistics"""
        return {
            "total_cost_usd": round(self._total_cost, 4),
            "request_count": self._request_count,
            "avg_cost_per_request": round(self._total_cost / max(self._request_count, 1), 4),
        }

    def close(self):
        """Close HTTP client"""
        if self._client:
            self._client.close()
            self._client = None


# Convenience function
def extract_intel_event(
    text: str,
    source_url: str = "",
    content_id: str = "",
    source_type_hint: str | None = None,
) -> IntelEvent:
    """Extract structured IntelEvent from raw text.

    Convenience wrapper around GeminiExtractor.

    Args:
        text: Raw document text
        source_url: Source URL
        content_id: Original content identifier
        source_type_hint: Optional hint for source type

    Returns:
        IntelEvent with extracted data

    Usage:
        event = extract_intel_event(
            text=paper_content,
            source_url="https://arxiv.org/abs/2401.12345",
            content_id="2401.12345",
            source_type_hint="arxiv"
        )

    """
    extractor = GeminiExtractor()
    try:
        return extractor.extract(
            text=text,
            source_url=source_url,
            content_id=content_id,
            source_type_hint=source_type_hint,
        )
    finally:
        extractor.close()
