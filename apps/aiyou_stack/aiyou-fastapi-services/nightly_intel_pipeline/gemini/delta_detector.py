# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Delta Detector - Change Detection Between Document Versions
============================================================
Detects and summarizes changes between previous and current versions.
"""

import contextlib
import json
from dataclasses import dataclass, field
from datetime import date

import structlog

from .config import GEMINI_INGESTION_CONFIG
from .extractor import GeminiExtractor
from .prompts import DELTA_DETECTION_PROMPT

logger = structlog.get_logger(__name__)


@dataclass
class Change:
    """A single change between versions"""

    field: str
    old_value: str
    new_value: str
    significance: str  # low, medium, high, critical


@dataclass
class DeadlineChange:
    """A deadline-related change"""

    type: str  # new, modified, removed
    date: date | None
    description: str


@dataclass
class DeltaSummary:
    """Summary of changes between document versions"""

    has_changes: bool
    change_summary: str
    changes: list[Change] = field(default_factory=list)
    deadline_changes: list[DeadlineChange] = field(default_factory=list)
    urgency: int = 1  # 1-5 scale
    action_required: str = "none"  # none, review, immediate

    def is_urgent(self) -> bool:
        """Check if changes require immediate attention"""
        return self.urgency >= 4 or self.action_required == "immediate"

    def has_deadline_changes(self) -> bool:
        """Check if there are deadline-related changes"""
        return len(self.deadline_changes) > 0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "has_changes": self.has_changes,
            "change_summary": self.change_summary,
            "changes": [
                {
                    "field": c.field,
                    "old_value": c.old_value,
                    "new_value": c.new_value,
                    "significance": c.significance,
                }
                for c in self.changes
            ],
            "deadline_changes": [
                {
                    "type": dc.type,
                    "date": dc.date.isoformat() if dc.date else None,
                    "description": dc.description,
                }
                for dc in self.deadline_changes
            ],
            "urgency": self.urgency,
            "action_required": self.action_required,
        }


class DeltaDetector:
    """Detects changes between document versions using Gemini.

    Used to surface "what's new vs yesterday" for the AM briefing.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or GEMINI_INGESTION_CONFIG
        self._extractor = GeminiExtractor(config)

    def detect(
        self,
        previous_text: str,
        current_text: str,
        content_id: str = "",
    ) -> DeltaSummary:
        """Detect changes between previous and current versions.

        Args:
            previous_text: Previous version text
            current_text: Current version text
            content_id: Content identifier for logging

        Returns:
            DeltaSummary with detected changes

        """
        if not self.config.get("enable_delta_detection", True):
            logger.warning("delta_detection_disabled")
            return DeltaSummary(
                has_changes=False,
                change_summary="Delta detection disabled",
            )

        # Quick check: if texts are identical, no changes
        if previous_text.strip() == current_text.strip():
            return DeltaSummary(
                has_changes=False,
                change_summary="No changes detected",
            )

        # Truncate texts if too long
        max_chars = 30000  # ~7500 tokens per version
        prev_truncated = previous_text[:max_chars]
        curr_truncated = current_text[:max_chars]

        # Build prompt
        prompt = DELTA_DETECTION_PROMPT.format(
            previous_text=prev_truncated,
            current_text=curr_truncated,
        )

        try:
            # Call Gemini
            response_text, usage = self._extractor._call_gemini(prompt)

            # Parse response
            data = self._parse_response(response_text)

            # Build DeltaSummary
            changes = [
                Change(
                    field=c.get("field", ""),
                    old_value=c.get("old_value", ""),
                    new_value=c.get("new_value", ""),
                    significance=c.get("significance", "low"),
                )
                for c in data.get("changes", [])
            ]

            deadline_changes = []
            for dc in data.get("deadline_changes", []):
                dc_date = None
                if dc.get("date"):
                    with contextlib.suppress(ValueError):
                        dc_date = date.fromisoformat(dc["date"])

                deadline_changes.append(
                    DeadlineChange(
                        type=dc.get("type", "unknown"),
                        date=dc_date,
                        description=dc.get("description", ""),
                    ),
                )

            summary = DeltaSummary(
                has_changes=data.get("has_changes", True),
                change_summary=data.get("change_summary", ""),
                changes=changes,
                deadline_changes=deadline_changes,
                urgency=data.get("urgency", 1),
                action_required=data.get("action_required", "none"),
            )

            logger.info(
                "delta_detected",
                content_id=content_id,
                has_changes=summary.has_changes,
                change_count=len(changes),
                urgency=summary.urgency,
            )

            return summary

        except Exception as e:
            logger.error(
                "delta_detection_error",
                content_id=content_id,
                error=str(e),
            )
            # Return a summary indicating detection failed
            return DeltaSummary(
                has_changes=True,  # Assume changes to be safe
                change_summary=f"Delta detection failed: {e!s}",
                urgency=2,  # Medium urgency - needs manual review
                action_required="review",
            )

    def _parse_response(self, response: str) -> dict:
        """Parse JSON from Gemini response"""
        text = response.strip()

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        return json.loads(text)

    def get_stats(self) -> dict:
        """Get statistics from underlying extractor"""
        return self._extractor.get_stats()

    def close(self):
        """Close resources"""
        self._extractor.close()


# Convenience function
def detect_delta(
    previous_text: str,
    current_text: str,
    content_id: str = "",
) -> DeltaSummary:
    """Detect changes between document versions.

    Convenience wrapper around DeltaDetector.

    Args:
        previous_text: Previous version text
        current_text: Current version text
        content_id: Content identifier for logging

    Returns:
        DeltaSummary with detected changes

    Usage:
        delta = detect_delta(
            previous_text=yesterday_content,
            current_text=today_content,
            content_id="regulation-123"
        )
        if delta.is_urgent():
            alert_executive()

    """
    detector = DeltaDetector()
    try:
        return detector.detect(
            previous_text=previous_text,
            current_text=current_text,
            content_id=content_id,
        )
    finally:
        detector.close()
