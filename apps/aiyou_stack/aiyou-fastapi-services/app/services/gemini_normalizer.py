"""Gemini Normalization Layer - Semantic Extraction Service

Transforms raw scraped documents into structured IntelEvent objects
with metadata, classifications, and JR Engine hints.

Position in pipeline:
  Raw Scrape → Text Extraction → [GEMINI NORMALIZER] → IntelEvent → JR Scoring

Cost estimate: ~$0.005-0.01 per item using gemini-3.1-flash-lite-preview
"""

import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime
from typing import Any

import httpx

from app.models.intel_event import (
    ChangeType,
    DeltaResult,
    DocumentType,
    Impact,
    IntelEvent,
    IntelEventBatch,
    JRHints,
    RiskTag,
)

logger = logging.getLogger(__name__)


# Extraction prompt for structured IntelEvent output
EXTRACTION_SYSTEM_PROMPT = """You are an intelligence analyst extracting structured metadata from documents.

Your task: Transform raw text into a structured JSON event object with precise classifications.

CRITICAL RULES:
1. Output ONLY valid JSON - no markdown, no explanation, no preamble
2. Use null for unknown/uncertain fields - never guess
3. Dates must be ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)
4. Confidence score reflects your certainty (0.0 = guess, 1.0 = certain)
5. Be conservative with risk_tags - only tag what's explicitly stated"""


EXTRACTION_USER_PROMPT = """Extract structured intelligence from this document.

SOURCE METADATA:
- URL: {source_url}
- Fetch Date: {fetch_date}
- Source Hint: {source_hint}

DOCUMENT TEXT:
{raw_text}

---

Output a JSON object with this EXACT structure:
{{
    "source_type": "regulation|draft_bill|news|rfp|competitor_release|product_doc|blog|lawsuit|guidance|academic|announcement|unknown",
    "jurisdiction": "US|US-CA|US-NY|EU|UK|CN|JP|null for unknown",
    "effective_date": "YYYY-MM-DD or null",
    "publication_date": "YYYY-MM-DD or null",
    "title": "Document title",
    "topic_tags": ["AI_disclosure", "chatbot_labeling", "data_privacy", "..."],
    "change_type": "new_law|amendment|guidance|announcement|update|repeal|enforcement_action|initial",
    "summary": "2-3 sentence summary of key points",
    "impacts": [
        {{
            "description": "What this means for business",
            "affected_area": "pricing|operations|legal|product|sales|general",
            "severity": "low|medium|high|critical",
            "timeline": "immediate|30_days|90_days|1_year|null"
        }}
    ],
    "risk_tags": ["compliance_deadline", "fine_per_violation", "ai_specific", "..."],
    "jr_hints": {{
        "purpose_candidates": ["How this advances/threatens revenue..."],
        "reasons_candidates": ["Defensible business impact..."],
        "brakes_candidates": ["Risk level, failure modes, mitigations..."],
        "suggested_tier": 1|2|3,
        "urgency_score": 0.0-1.0
    }},
    "confidence": 0.0-1.0
}}"""


DELTA_SYSTEM_PROMPT = """You are a change analyst comparing document versions.

Your task: Identify what changed between two versions of the same document.

CRITICAL RULES:
1. Output ONLY valid JSON - no markdown, no explanation
2. Focus on substantive changes, not formatting
3. Urgency 5 = immediate regulatory deadline, 1 = minor wording change
4. Be specific about what changed, not just "section updated" """


DELTA_USER_PROMPT = """Compare these two document versions and identify changes.

PREVIOUS VERSION:
{previous_text}

---

CURRENT VERSION:
{current_text}

---

Output a JSON object:
{{
    "changes": [
        "Specific change 1: X was modified to Y",
        "Specific change 2: New section Z added regarding..."
    ],
    "change_tags": ["reg_deadline", "pricing", "enforcement", "definition_change", "procedure_change", "misc"],
    "urgency": 1-5,
    "summary": "Brief summary of what changed and why it matters"
}}"""


class GeminiNormalizer:
    """Transforms raw documents into structured IntelEvent objects using Gemini.

    Features:
    - Document classification (regulation, news, RFP, etc.)
    - Metadata extraction (jurisdiction, dates, topics)
    - Impact analysis with severity ratings
    - JR Engine hint generation
    - Delta detection between versions
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-3.1-flash-lite-preview",
        timeout: float = 60.0,
        max_input_chars: int = 100000,
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = model
        self.timeout = timeout
        self.max_input_chars = max_input_chars
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Use 'async with' context manager")
        return self._client

    def _build_url(self) -> str:
        """Build Gemini API URL"""
        return f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"

    def _truncate_text(self, text: str) -> str:
        """Truncate text to max length, preserving beginning and end"""
        if len(text) <= self.max_input_chars:
            return text
        half = self.max_input_chars // 2
        return text[:half] + "\n\n[...TRUNCATED...]\n\n" + text[-half:]

    def _redact_secrets(self, text: str) -> str:
        """Redact potential secrets before sending to Gemini"""
        patterns = [
            (r'(?i)(api[_-]?key|apikey)["\s:=]+["\']?[\w-]{20,}["\']?', "[REDACTED_API_KEY]"),
            (r'(?i)(secret|password|token)["\s:=]+["\']?[\w-]{8,}["\']?', "[REDACTED_SECRET]"),
            (r"(?i)(bearer\s+)[\w-]{20,}", r"\1[REDACTED_TOKEN]"),
            (r"[a-zA-Z0-9+/]{40,}={0,2}", "[REDACTED_BASE64]"),
        ]
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        return result

    async def _call_gemini(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
    ) -> tuple[str, dict[str, int]]:
        """Make a Gemini API call and return response + usage"""
        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json",
            },
        }

        response = await self.client.post(self._build_url(), json=payload)
        response.raise_for_status()
        data = response.json()

        content = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = {}
        if "usageMetadata" in data:
            usage = {
                "prompt_tokens": data["usageMetadata"].get("promptTokenCount", 0),
                "completion_tokens": data["usageMetadata"].get("candidatesTokenCount", 0),
            }

        return content, usage

    def _parse_json_response(self, content: str) -> dict[str, Any]:
        """Parse JSON from Gemini response, handling markdown blocks"""
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text)
            text = re.sub(r"\n?```$", "", text)
        return json.loads(text)

    def _map_source_type(self, value: str) -> DocumentType:
        """Map string to DocumentType enum"""
        mapping = {
            "regulation": DocumentType.REGULATION,
            "draft_bill": DocumentType.DRAFT_BILL,
            "news": DocumentType.NEWS,
            "rfp": DocumentType.RFP,
            "competitor_release": DocumentType.COMPETITOR_RELEASE,
            "product_doc": DocumentType.PRODUCT_DOC,
            "blog": DocumentType.BLOG,
            "lawsuit": DocumentType.LAWSUIT,
            "guidance": DocumentType.GUIDANCE,
            "academic": DocumentType.ACADEMIC,
            "announcement": DocumentType.ANNOUNCEMENT,
        }
        return mapping.get(value.lower(), DocumentType.UNKNOWN)

    def _map_change_type(self, value: str) -> ChangeType:
        """Map string to ChangeType enum"""
        mapping = {
            "new_law": ChangeType.NEW_LAW,
            "amendment": ChangeType.AMENDMENT,
            "guidance": ChangeType.GUIDANCE,
            "announcement": ChangeType.ANNOUNCEMENT,
            "update": ChangeType.UPDATE,
            "repeal": ChangeType.REPEAL,
            "enforcement_action": ChangeType.ENFORCEMENT_ACTION,
            "initial": ChangeType.INITIAL,
        }
        return mapping.get(value.lower(), ChangeType.INITIAL)

    def _map_risk_tags(self, tags: list[str]) -> list[RiskTag]:
        """Map strings to RiskTag enums"""
        mapping = {
            "compliance_deadline": RiskTag.COMPLIANCE_DEADLINE,
            "fine_per_violation": RiskTag.FINE_PER_VIOLATION,
            "criminal_penalty": RiskTag.CRIMINAL_PENALTY,
            "license_requirement": RiskTag.LICENSE_REQUIREMENT,
            "disclosure_mandate": RiskTag.DISCLOSURE_MANDATE,
            "data_retention": RiskTag.DATA_RETENTION,
            "audit_requirement": RiskTag.AUDIT_REQUIREMENT,
            "consumer_protection": RiskTag.CONSUMER_PROTECTION,
            "ai_specific": RiskTag.AI_SPECIFIC,
            "competitive_threat": RiskTag.COMPETITIVE_THREAT,
            "opportunity": RiskTag.OPPORTUNITY,
            "market_shift": RiskTag.MARKET_SHIFT,
        }
        return [mapping[t.lower()] for t in tags if t.lower() in mapping]

    def _parse_date(self, value: str | None) -> datetime | None:
        """Parse date string to datetime"""
        if not value:
            return None
        try:
            if "T" in value:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            return datetime.strptime(value, "%Y-%m-%d")
        except (ValueError, TypeError):
            return None

    async def extract_intel_event(
        self,
        raw_text: str,
        source_url: str,
        source_hint: str = "",
        event_id: str | None = None,
    ) -> IntelEvent:
        """Extract a structured IntelEvent from raw document text.

        Args:
            raw_text: Raw document text (will be truncated if too long)
            source_url: Original source URL
            source_hint: Optional hint about source type
            event_id: Optional pre-assigned event ID

        Returns:
            IntelEvent with all extracted fields

        """
        # Prepare text
        clean_text = self._redact_secrets(raw_text)
        truncated_text = self._truncate_text(clean_text)
        text_hash = hashlib.sha256(raw_text.encode()).hexdigest()

        # Build prompt
        user_prompt = EXTRACTION_USER_PROMPT.format(
            source_url=source_url,
            fetch_date=datetime.utcnow().isoformat(),
            source_hint=source_hint or "unknown",
            raw_text=truncated_text,
        )

        # Call Gemini
        try:
            content, usage = await self._call_gemini(
                EXTRACTION_SYSTEM_PROMPT,
                user_prompt,
                temperature=0.2,
            )
            data = self._parse_json_response(content)
        except Exception as e:
            logger.error(f"Gemini extraction failed: {e}")
            # Return minimal event on failure
            return IntelEvent(
                id=event_id or str(uuid.uuid4()),
                source_url=source_url,
                raw_text_hash=text_hash,
                gemini_model=self.model,
                gemini_confidence=0.0,
                summary=f"Extraction failed: {str(e)[:100]}",
            )

        # Parse impacts
        impacts = []
        for imp in data.get("impacts", []):
            if isinstance(imp, dict):
                impacts.append(
                    Impact(
                        description=imp.get("description", ""),
                        affected_area=imp.get("affected_area", "general"),
                        severity=imp.get("severity", "medium"),
                        timeline=imp.get("timeline"),
                    ),
                )

        # Parse JR hints
        jr_data = data.get("jr_hints", {})
        jr_hints = JRHints(
            purpose_candidates=jr_data.get("purpose_candidates", []),
            reasons_candidates=jr_data.get("reasons_candidates", []),
            brakes_candidates=jr_data.get("brakes_candidates", []),
            suggested_tier=jr_data.get("suggested_tier"),
            urgency_score=float(jr_data.get("urgency_score", 0.5)),
        )

        # Build IntelEvent
        return IntelEvent(
            id=event_id or str(uuid.uuid4()),
            source_url=source_url,
            source_type=self._map_source_type(data.get("source_type", "unknown")),
            jurisdiction=data.get("jurisdiction"),
            effective_date=self._parse_date(data.get("effective_date")),
            publication_date=self._parse_date(data.get("publication_date")),
            title=data.get("title", ""),
            topic_tags=data.get("topic_tags", []),
            change_type=self._map_change_type(data.get("change_type", "initial")),
            summary=data.get("summary", ""),
            impacts=impacts,
            risk_tags=self._map_risk_tags(data.get("risk_tags", [])),
            jr_hints=jr_hints,
            raw_text_hash=text_hash,
            gemini_model=self.model,
            gemini_confidence=float(data.get("confidence", 0.5)),
        )

    async def detect_delta(
        self,
        previous_text: str,
        current_text: str,
        previous_id: str,
        current_id: str,
    ) -> DeltaResult:
        """Detect changes between two document versions.

        Args:
            previous_text: Previous version text
            current_text: Current version text
            previous_id: ID of previous IntelEvent
            current_id: ID of current IntelEvent

        Returns:
            DeltaResult with changes, tags, and urgency

        """
        prev_truncated = self._truncate_text(self._redact_secrets(previous_text))
        curr_truncated = self._truncate_text(self._redact_secrets(current_text))

        user_prompt = DELTA_USER_PROMPT.format(
            previous_text=prev_truncated,
            current_text=curr_truncated,
        )

        try:
            content, _ = await self._call_gemini(
                DELTA_SYSTEM_PROMPT,
                user_prompt,
                temperature=0.2,
            )
            data = self._parse_json_response(content)
        except Exception as e:
            logger.error(f"Delta detection failed: {e}")
            return DeltaResult(
                previous_id=previous_id,
                current_id=current_id,
                changes=[f"Delta detection failed: {str(e)[:100]}"],
                urgency=3,
            )

        return DeltaResult(
            previous_id=previous_id,
            current_id=current_id,
            changes=data.get("changes", []),
            change_tags=data.get("change_tags", []),
            urgency=int(data.get("urgency", 3)),
            summary=data.get("summary", ""),
        )

    async def extract_batch(
        self,
        documents: list[dict[str, Any]],
        batch_id: str | None = None,
        job_id: str | None = None,
    ) -> IntelEventBatch:
        """Extract IntelEvents from a batch of documents.

        Args:
            documents: List of dicts with 'text', 'url', 'source_hint' keys
            batch_id: Optional batch identifier
            job_id: Optional parent job identifier

        Returns:
            IntelEventBatch with all extracted events and metrics

        """
        batch_id = batch_id or str(uuid.uuid4())
        events = []
        errors = 0

        for doc in documents:
            try:
                event = await self.extract_intel_event(
                    raw_text=doc.get("text", ""),
                    source_url=doc.get("url", ""),
                    source_hint=doc.get("source_hint", ""),
                )
                events.append(event)
            except Exception as e:
                logger.error(f"Batch extraction error for {doc.get('url')}: {e}")
                errors += 1

        return IntelEventBatch(
            events=events,
            batch_id=batch_id,
            source_job_id=job_id,
            total_raw_documents=len(documents),
            extraction_errors=errors,
        )
