"""Safety Moderation for V2X Mesh

Integrates with:
- Google Cloud Content Safety API
- Hive Moderation API
- Custom safety filters

Filters:
- Model outputs before broadcast
- Shared media (images, video from sensors)
- User-generated map updates
- Writes audit trail to ShadowTag
"""

import hashlib
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any


class SafetyCategory(Enum):
    """Safety violation categories"""

    VIOLENCE = "violence"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    SPAM = "spam"
    MALICIOUS_CODE = "malicious_code"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    PRIVACY_VIOLATION = "privacy_violation"


@dataclass
class ModerationResult:
    """Result of content moderation"""

    is_safe: bool
    confidence: float  # 0.0 - 1.0
    categories: list[SafetyCategory]
    scores: dict[str, float]  # category -> score
    flagged_elements: list[str]  # Specific elements flagged
    audit_id: str  # Reference to audit trail
    processing_time_ms: float


class GoogleContentSafety:
    """Google Cloud Content Safety API integration

    Ref: https://cloud.google.com/natural-language/docs/moderating-text
    """

    def __init__(self, api_key: str | None = None, threshold: float = 0.5):
        self.api_key = api_key
        self.threshold = threshold
        self.endpoint = "https://language.googleapis.com/v1/documents:moderateText"

    async def moderate_text(self, text: str) -> ModerationResult:
        """Moderate text content"""
        start_time = time.time()

        # In production, this calls actual Google API
        # For now, simulate with simple keyword matching
        categories = []
        scores = {}

        # Simulate safety checks
        violence_score = self._check_violence(text)
        harassment_score = self._check_harassment(text)
        spam_score = self._check_spam(text)

        scores["violence"] = violence_score
        scores["harassment"] = harassment_score
        scores["spam"] = spam_score

        if violence_score > self.threshold:
            categories.append(SafetyCategory.VIOLENCE)
        if harassment_score > self.threshold:
            categories.append(SafetyCategory.HARASSMENT)
        if spam_score > self.threshold:
            categories.append(SafetyCategory.SPAM)

        is_safe = len(categories) == 0
        max_score = max(scores.values()) if scores else 0.0

        processing_time = (time.time() - start_time) * 1000

        return ModerationResult(
            is_safe=is_safe,
            confidence=1.0 - max_score,
            categories=categories,
            scores=scores,
            flagged_elements=[],
            audit_id=self._generate_audit_id(),
            processing_time_ms=processing_time,
        )

    def _check_violence(self, text: str) -> float:
        """Check for violent content"""
        violence_keywords = ["kill", "attack", "weapon", "explosive", "harm"]
        text_lower = text.lower()
        matches = sum(1 for kw in violence_keywords if kw in text_lower)
        return min(1.0, matches * 0.3)

    def _check_harassment(self, text: str) -> float:
        """Check for harassment"""
        harassment_keywords = ["stupid", "idiot", "hate", "worthless"]
        text_lower = text.lower()
        matches = sum(1 for kw in harassment_keywords if kw in text_lower)
        return min(1.0, matches * 0.3)

    def _check_spam(self, text: str) -> float:
        """Check for spam"""
        spam_indicators = ["click here", "buy now", "limited offer", "www.", "http"]
        text_lower = text.lower()
        matches = sum(1 for kw in spam_indicators if kw in text_lower)
        return min(1.0, matches * 0.4)

    def _generate_audit_id(self) -> str:
        """Generate audit ID"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]


class HiveModeration:
    """Hive AI Moderation API integration

    Ref: https://docs.thehive.ai/
    Specialized for image/video moderation
    """

    def __init__(self, api_key: str | None = None, threshold: float = 0.5):
        self.api_key = api_key
        self.threshold = threshold
        self.endpoint = "https://api.thehive.ai/api/v2/task/sync"

    async def moderate_image(self, image_data: bytes) -> ModerationResult:
        """Moderate image content"""
        start_time = time.time()

        # In production, this calls Hive API
        # For now, simulate
        scores = {"violence": 0.1, "inappropriate": 0.05, "spam": 0.02}

        categories = [
            SafetyCategory(cat)
            for cat, score in scores.items()
            if score > self.threshold and cat in [e.value for e in SafetyCategory]
        ]

        is_safe = len(categories) == 0
        max_score = max(scores.values())

        processing_time = (time.time() - start_time) * 1000

        return ModerationResult(
            is_safe=is_safe,
            confidence=1.0 - max_score,
            categories=categories,
            scores=scores,
            flagged_elements=[],
            audit_id=self._generate_audit_id(),
            processing_time_ms=processing_time,
        )

    async def moderate_video(self, video_data: bytes) -> ModerationResult:
        """Moderate video content"""
        # Similar to image but processes frames
        return await self.moderate_image(video_data)

    def _generate_audit_id(self) -> str:
        """Generate audit ID"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]


class V2XSafetyModerator:
    """V2X-specific safety moderation

    Combines Google Content Safety and Hive with custom V2X rules
    """

    def __init__(
        self,
        google_api_key: str | None = None,
        hive_api_key: str | None = None,
        shadowtag_endpoint: str = "http://shadowtag-service:8003",
    ):
        self.google = GoogleContentSafety(api_key=google_api_key, threshold=0.5)
        self.hive = HiveModeration(api_key=hive_api_key, threshold=0.5)
        self.shadowtag_endpoint = shadowtag_endpoint

        # Audit trail
        self.audit_log: list[dict] = []

        # Statistics
        self.stats = {
            "total_checks": 0,
            "blocked": 0,
            "allowed": 0,
            "text_checks": 0,
            "image_checks": 0,
            "video_checks": 0,
        }

    async def moderate_event_message(
        self,
        event_data: dict[str, Any],
    ) -> tuple[bool, ModerationResult]:
        """Moderate event message before broadcast

        Returns: (is_safe, moderation_result)
        """
        self.stats["total_checks"] += 1
        self.stats["text_checks"] += 1

        # Extract text description
        description = event_data.get("description", "")

        # Run text moderation
        result = await self.google.moderate_text(description)

        # Apply V2X-specific rules
        result = self._apply_v2x_rules(event_data, result)

        # Log to audit trail
        await self._log_moderation(
            content_type="event_message",
            content_id=event_data.get("event_id", "unknown"),
            result=result,
        )

        if result.is_safe:
            self.stats["allowed"] += 1
        else:
            self.stats["blocked"] += 1

        return result.is_safe, result

    async def moderate_map_update(
        self,
        map_feature: dict[str, Any],
    ) -> tuple[bool, ModerationResult]:
        """Moderate map feature update

        Checks for:
        - Spam (excessive updates)
        - Misinformation (fake work zones, etc.)
        - Privacy violations (home addresses, etc.)
        """
        self.stats["total_checks"] += 1
        self.stats["text_checks"] += 1

        # Check feature properties
        properties = map_feature.get("properties", {})
        text_content = " ".join(str(v) for v in properties.values())

        result = await self.google.moderate_text(text_content)

        # Check for privacy violations
        privacy_score = self._check_privacy_violation(map_feature)
        if privacy_score > 0.5:
            result.categories.append(SafetyCategory.PRIVACY_VIOLATION)
            result.scores["privacy_violation"] = privacy_score
            result.is_safe = False

        # Log
        await self._log_moderation(
            content_type="map_update",
            content_id=map_feature.get("feature_id", "unknown"),
            result=result,
        )

        if result.is_safe:
            self.stats["allowed"] += 1
        else:
            self.stats["blocked"] += 1

        return result.is_safe, result

    async def moderate_sensor_data(
        self,
        sensor_type: str,
        data: bytes,
        metadata: dict[str, Any],
    ) -> tuple[bool, ModerationResult]:
        """Moderate sensor data (images, video)

        Used when vehicles share sensor data for verification
        """
        self.stats["total_checks"] += 1

        if sensor_type == "image":
            self.stats["image_checks"] += 1
            result = await self.hive.moderate_image(data)
        elif sensor_type == "video":
            self.stats["video_checks"] += 1
            result = await self.hive.moderate_video(data)
        else:
            # Unknown type - allow but log
            result = ModerationResult(
                is_safe=True,
                confidence=0.5,
                categories=[],
                scores={},
                flagged_elements=[],
                audit_id=self._generate_audit_id(),
                processing_time_ms=0.0,
            )

        # Log
        await self._log_moderation(
            content_type=f"sensor_{sensor_type}",
            content_id=metadata.get("sensor_id", "unknown"),
            result=result,
        )

        if result.is_safe:
            self.stats["allowed"] += 1
        else:
            self.stats["blocked"] += 1

        return result.is_safe, result

    def _apply_v2x_rules(self, event_data: dict, result: ModerationResult) -> ModerationResult:
        """Apply V2X-specific safety rules"""
        # Rule 1: Emergency events always allowed (but logged)
        event_type = event_data.get("event_type", "")
        if event_type in ["collision_risk", "emergency_vehicle", "hard_brake"]:
            result.is_safe = True
            result.flagged_elements.append("emergency_override")

        # Rule 2: Check for duplicate/spam events
        # (In production, track recent events by vehicle)

        # Rule 3: Severity bounds check
        severity = event_data.get("severity", 0)
        if severity > 10 or severity < 0:
            result.is_safe = False
            result.categories.append(SafetyCategory.MALICIOUS_CODE)
            result.scores["malicious_code"] = 1.0

        return result

    def _check_privacy_violation(self, map_feature: dict) -> float:
        """Check for privacy violations in map feature"""
        properties = map_feature.get("properties", {})

        # Check for residential addresses
        privacy_keywords = ["home", "residence", "apartment", "house number"]
        text = " ".join(str(v).lower() for v in properties.values())

        matches = sum(1 for kw in privacy_keywords if kw in text)
        return min(1.0, matches * 0.4)

    async def _log_moderation(self, content_type: str, content_id: str, result: ModerationResult):
        """Log moderation decision to audit trail"""
        audit_entry = {
            "timestamp": int(time.time() * 1000),
            "content_type": content_type,
            "content_id": content_id,
            "is_safe": result.is_safe,
            "confidence": result.confidence,
            "categories": [c.value for c in result.categories],
            "scores": result.scores,
            "audit_id": result.audit_id,
        }

        self.audit_log.append(audit_entry)

        # Keep audit log size manageable
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]

        # In production, send to ShadowTag service
        # await self._submit_to_shadowtag(audit_entry)

    async def _submit_to_shadowtag(self, audit_entry: dict):
        """Submit audit entry to ShadowTag service"""
        # TODO: HTTP POST to ShadowTag
        # await http_client.post(f"{self.shadowtag_endpoint}/v1/moderation-audit", json=audit_entry)

    def _generate_audit_id(self) -> str:
        """Generate audit ID"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

    def get_stats(self) -> dict:
        """Get moderation statistics"""
        return {
            **self.stats,
            "block_rate": (
                self.stats["blocked"] / self.stats["total_checks"]
                if self.stats["total_checks"] > 0
                else 0.0
            ),
            "audit_log_size": len(self.audit_log),
        }

    def export_audit_log(self, limit: int = 100) -> list[dict]:
        """Export recent audit log entries"""
        return self.audit_log[-limit:]


# Cost estimation
class ModerationCostEstimator:
    """Estimate moderation costs based on usage

    Google Content Safety: ~$1-3 per 1000 requests
    Hive: ~$0.50-2 per 1000 images, ~$5-15 per 1000 videos
    """

    @staticmethod
    def estimate_monthly_cost(
        events_per_day: int,
        map_updates_per_day: int,
        images_per_day: int,
        videos_per_day: int,
    ) -> dict[str, float]:
        """Estimate monthly moderation costs"""
        # Cost per 1000 items
        text_cost_per_1k = 2.0  # Google Content Safety
        image_cost_per_1k = 1.0  # Hive images
        video_cost_per_1k = 10.0  # Hive videos

        # Monthly totals
        monthly_events = events_per_day * 30
        monthly_maps = map_updates_per_day * 30
        monthly_images = images_per_day * 30
        monthly_videos = videos_per_day * 30

        # Costs
        text_cost = ((monthly_events + monthly_maps) / 1000) * text_cost_per_1k
        image_cost = (monthly_images / 1000) * image_cost_per_1k
        video_cost = (monthly_videos / 1000) * video_cost_per_1k

        total = text_cost + image_cost + video_cost

        return {
            "text_moderation": round(text_cost, 2),
            "image_moderation": round(image_cost, 2),
            "video_moderation": round(video_cost, 2),
            "total_monthly": round(total, 2),
            "total_annual": round(total * 12, 2),
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    import json

    async def main():
        # Create moderator
        moderator = V2XSafetyModerator()

        # Test event moderation
        event = {
            "event_id": "evt-001",
            "event_type": "hard_brake",
            "severity": 8,
            "description": "Emergency braking due to pedestrian",
        }

        is_safe, result = await moderator.moderate_event_message(event)
        print(f"Event moderation: {'SAFE' if is_safe else 'BLOCKED'}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Categories: {[c.value for c in result.categories]}")

        # Test map update moderation
        map_feature = {
            "feature_id": "feat-001",
            "feature_type": "work_zone",
            "properties": {"name": "Road Construction", "severity": "high"},
        }

        is_safe, result = await moderator.moderate_map_update(map_feature)
        print(f"\nMap update moderation: {'SAFE' if is_safe else 'BLOCKED'}")

        # Stats
        print("\nModeration Statistics:")
        print(json.dumps(moderator.get_stats(), indent=2))

        # Cost estimation
        print("\nCost Estimation (1000 vehicles, active city):")
        costs = ModerationCostEstimator.estimate_monthly_cost(
            events_per_day=10000,  # 10 events/vehicle/day
            map_updates_per_day=1000,  # 1 update/vehicle/day
            images_per_day=5000,  # 5 images/vehicle/day
            videos_per_day=500,  # 0.5 videos/vehicle/day
        )
        print(json.dumps(costs, indent=2))

    asyncio.run(main())
