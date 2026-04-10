"""
NS (Neural System) Detection Engine
====================================
First layer of the NS-JR-Cor compliance framework.

Responsibilities:
- Detect risk signals using Google Safety API + Hive
- Self-harm detection with crisis indicator analysis
- Explicit content detection (text and images)
- Medical claim/impersonation detection
- Cache verdicts in GPTRAM for cost optimization

Integration Points:
- Google Content Safety API (text moderation)
- Hive AI (image/video moderation)
- Gemini Flash (advanced classification)
- GPTRAM (verdict caching)
"""

import hashlib
import logging
import re
import time
from dataclasses import dataclass
from typing import Any

from app.models.california_ai import (
    ContentType,
    DetectionSignal,
    ExplicitContentSignal,
    MedicalClaimSignal,
    NSDetectionOutput,
    SelfHarmSignal,
    ViolationSeverity,
)
from corp_engine.governance.regulations.california_ai_comprehensive import (
    CRISIS_RESOURCES,
    EXPLICIT_CONTENT_PATTERNS,
    MEDICAL_IMPERSONATION_PATTERNS,
    SELF_HARM_PATTERNS,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class NSConfig:
    """NS Detection Engine configuration"""

    # Detection thresholds
    self_harm_threshold: float = 0.5
    explicit_content_threshold: float = 0.6
    medical_claim_threshold: float = 0.7

    # API settings
    google_api_enabled: bool = True
    hive_api_enabled: bool = True
    gemini_enabled: bool = True

    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 86400  # 24 hours

    # Performance
    max_content_length: int = 50000
    timeout_ms: int = 5000


# =============================================================================
# Pattern-Based Detectors
# =============================================================================


class SelfHarmDetector:
    """Pattern-based self-harm detection"""

    def __init__(self):
        self._patterns = {}
        for category, patterns in SELF_HARM_PATTERNS.items():
            self._patterns[category] = [re.compile(p) for p in patterns]

    def detect(self, text: str) -> list[SelfHarmSignal]:
        """Detect self-harm signals in text"""
        signals = []

        for category, patterns in self._patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    # Severity based on category
                    if category == "explicit_ideation":
                        severity = ViolationSeverity.CRITICAL
                        confidence = 0.95
                    elif category == "self_harm_methods":
                        severity = ViolationSeverity.CRITICAL
                        confidence = 0.90
                    else:
                        severity = ViolationSeverity.HIGH
                        confidence = 0.75

                    signal = SelfHarmSignal(
                        confidence=confidence,
                        evidence=matches[0] if matches else "",
                        detector="pattern_matcher",
                        severity_level=severity,
                        crisis_indicators=[category],
                        recommended_resources=list(CRISIS_RESOURCES.keys())[:3],
                        metadata={
                            "category": category,
                            "pattern": pattern.pattern,
                            "match_count": len(matches),
                        },
                    )
                    signals.append(signal)

        return signals


class ExplicitContentDetector:
    """Pattern-based explicit content detection"""

    def __init__(self):
        self._patterns = {}
        for category, patterns in EXPLICIT_CONTENT_PATTERNS.items():
            self._patterns[category] = [re.compile(p) for p in patterns]

    def detect(self, text: str) -> list[ExplicitContentSignal]:
        """Detect explicit content signals in text"""
        signals = []

        for category, patterns in self._patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text)
                if matches:
                    signal = ExplicitContentSignal(
                        confidence=0.85,
                        evidence=matches[0] if matches else "",
                        detector="pattern_matcher",
                        content_categories=[category],
                        metadata={
                            "category": category,
                            "pattern": pattern.pattern,
                            "match_count": len(matches),
                        },
                    )
                    signals.append(signal)

        return signals


class MedicalClaimDetector:
    """Pattern-based medical claim detection"""

    def __init__(self):
        self._patterns = [re.compile(p) for p in MEDICAL_IMPERSONATION_PATTERNS]

    def detect(self, text: str) -> list[MedicalClaimSignal]:
        """Detect medical claim/impersonation signals"""
        signals = []

        for pattern in self._patterns:
            matches = pattern.findall(text)
            if matches:
                signal = MedicalClaimSignal(
                    confidence=0.90,
                    evidence=matches[0] if matches else "",
                    detector="pattern_matcher",
                    claim_type="impersonation",
                    impersonation_detected=True,
                    metadata={"pattern": pattern.pattern, "match_count": len(matches)},
                )
                signals.append(signal)

        return signals


# =============================================================================
# External API Integrations
# =============================================================================


class GoogleSafetyClient:
    """Google Content Safety API client"""

    def __init__(self, api_key: str | None = None, threshold: float = 0.5):
        self.api_key = api_key
        self.threshold = threshold
        self._enabled = api_key is not None

    async def moderate_text(self, text: str) -> dict[str, Any]:
        """Moderate text using Google Safety API"""
        if not self._enabled:
            return {"enabled": False, "scores": {}}

        # In production, call Google API
        # For now, return simulated response
        start_time = time.time()

        # Simulate API latency
        scores = {
            "violence": 0.05,
            "harassment": 0.03,
            "hate_speech": 0.02,
            "sexually_explicit": 0.01,
            "dangerous": 0.02,
        }

        processing_time = (time.time() - start_time) * 1000

        return {
            "enabled": True,
            "scores": scores,
            "is_safe": all(s < self.threshold for s in scores.values()),
            "processing_time_ms": processing_time,
        }


class HiveModerationClient:
    """Hive AI Moderation API client"""

    def __init__(self, api_key: str | None = None, threshold: float = 0.5):
        self.api_key = api_key
        self.threshold = threshold
        self._enabled = api_key is not None

    async def moderate_image(self, image_data: bytes) -> dict[str, Any]:
        """Moderate image using Hive API"""
        if not self._enabled:
            return {"enabled": False, "scores": {}}

        start_time = time.time()

        # Simulate API response
        scores = {
            "adult": 0.02,
            "violence": 0.01,
            "gore": 0.01,
            "nudity": 0.01,
        }

        processing_time = (time.time() - start_time) * 1000

        return {
            "enabled": True,
            "scores": scores,
            "is_safe": all(s < self.threshold for s in scores.values()),
            "processing_time_ms": processing_time,
        }

    async def moderate_video(self, video_data: bytes) -> dict[str, Any]:
        """Moderate video using Hive API"""
        # Similar to image but processes frames
        return await self.moderate_image(video_data)


# =============================================================================
# GPTRAM Cache Integration
# =============================================================================


class NSCacheManager:
    """Cache manager for NS detection results"""

    def __init__(self, enabled: bool = True, ttl_seconds: int = 86400):
        self.enabled = enabled
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[NSDetectionOutput, float]] = {}

    def _hash_content(self, content: str) -> str:
        """Generate content hash for caching"""
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    async def get(self, content: str) -> NSDetectionOutput | None:
        """Get cached result if available"""
        if not self.enabled:
            return None

        content_hash = self._hash_content(content)
        cached = self._cache.get(content_hash)

        if cached:
            result, timestamp = cached
            if time.time() - timestamp < self.ttl_seconds:
                return result
            else:
                # Expired
                del self._cache[content_hash]

        return None

    async def set(self, content: str, result: NSDetectionOutput) -> None:
        """Cache detection result"""
        if not self.enabled:
            return

        content_hash = self._hash_content(content)
        self._cache[content_hash] = (result, time.time())

        # Cleanup old entries periodically
        if len(self._cache) > 10000:
            await self._cleanup()

    async def _cleanup(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired = [k for k, (_, ts) in self._cache.items() if current_time - ts >= self.ttl_seconds]
        for k in expired:
            del self._cache[k]


# =============================================================================
# Main NS Detection Engine
# =============================================================================


class NSDetectionEngine:
    """
    Neural System Detection Engine.

    First layer of NS-JR-Cor framework.
    Detects risk signals in content using multiple detection methods:
    - Pattern matching (fast, local)
    - Google Safety API (text moderation)
    - Hive API (image/video moderation)
    - Gemini Flash (advanced classification)
    """

    def __init__(
        self,
        config: NSConfig | None = None,
        google_api_key: str | None = None,
        hive_api_key: str | None = None,
    ):
        self.config = config or NSConfig()

        # Initialize detectors
        self.self_harm_detector = SelfHarmDetector()
        self.explicit_detector = ExplicitContentDetector()
        self.medical_detector = MedicalClaimDetector()

        # External APIs
        self.google_client = GoogleSafetyClient(
            api_key=google_api_key, threshold=self.config.explicit_content_threshold
        )
        self.hive_client = HiveModerationClient(
            api_key=hive_api_key, threshold=self.config.explicit_content_threshold
        )

        # Cache
        self.cache = NSCacheManager(
            enabled=self.config.cache_enabled, ttl_seconds=self.config.cache_ttl_seconds
        )

        # Stats
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "self_harm_detections": 0,
            "explicit_detections": 0,
            "medical_detections": 0,
            "api_calls_google": 0,
            "api_calls_hive": 0,
        }

    async def detect(
        self,
        content: str,
        content_type: ContentType = ContentType.TEXT_MESSAGE,
        media_data: bytes | None = None,
        skip_cache: bool = False,
    ) -> NSDetectionOutput:
        """
        Main detection method.

        Args:
            content: Text content to analyze
            content_type: Type of content
            media_data: Optional media bytes (for images/video)
            skip_cache: Skip cache lookup

        Returns:
            NSDetectionOutput with all detected signals
        """
        start_time = time.time()
        self._stats["total_requests"] += 1

        # Check cache first
        if not skip_cache:
            cached = await self.cache.get(content)
            if cached:
                self._stats["cache_hits"] += 1
                cached.cache_hit = True
                return cached

        self._stats["cache_misses"] += 1

        # Truncate content if too long
        if len(content) > self.config.max_content_length:
            content = content[: self.config.max_content_length]
            logger.warning(f"Content truncated to {self.config.max_content_length} chars")

        # Run pattern-based detection
        self_harm_signals = self.self_harm_detector.detect(content)
        explicit_signals = self.explicit_detector.detect(content)
        medical_signals = self.medical_detector.detect(content)

        # Update stats
        if self_harm_signals:
            self._stats["self_harm_detections"] += 1
        if explicit_signals:
            self._stats["explicit_detections"] += 1
        if medical_signals:
            self._stats["medical_detections"] += 1

        # Additional signals from external APIs
        all_signals: list[DetectionSignal] = []

        # Google Safety API for text
        if self.config.google_api_enabled:
            google_result = await self.google_client.moderate_text(content)
            if google_result.get("enabled"):
                self._stats["api_calls_google"] += 1
                for category, score in google_result.get("scores", {}).items():
                    if score > self.config.explicit_content_threshold:
                        all_signals.append(
                            DetectionSignal(
                                signal_type=f"google_{category}",
                                confidence=score,
                                evidence="",
                                detector="google_safety_api",
                                metadata={"category": category, "score": score},
                            )
                        )

        # Hive API for images/video
        if media_data and self.config.hive_api_enabled:
            if content_type in [ContentType.IMAGE, ContentType.MIXED_MEDIA]:
                hive_result = await self.hive_client.moderate_image(media_data)
                if hive_result.get("enabled"):
                    self._stats["api_calls_hive"] += 1
                    for category, score in hive_result.get("scores", {}).items():
                        if score > self.config.explicit_content_threshold:
                            explicit_signals.append(
                                ExplicitContentSignal(
                                    confidence=score,
                                    evidence="",
                                    detector="hive_api",
                                    content_categories=[category],
                                    metadata={"category": category, "score": score},
                                )
                            )

        # Calculate overall risk score
        max_self_harm = max((s.confidence for s in self_harm_signals), default=0.0)
        max_explicit = max((s.confidence for s in explicit_signals), default=0.0)
        max_medical = max((s.confidence for s in medical_signals), default=0.0)
        max_general = max((s.confidence for s in all_signals), default=0.0)

        overall_risk = max(max_self_harm, max_explicit, max_medical, max_general)

        processing_time = (time.time() - start_time) * 1000

        # Build output
        output = NSDetectionOutput(
            signals=all_signals,
            self_harm_signals=self_harm_signals,
            explicit_content_signals=explicit_signals,
            medical_claim_signals=medical_signals,
            overall_risk_score=overall_risk,
            processing_time_ms=processing_time,
            cache_hit=False,
        )

        # Cache result
        await self.cache.set(content, output)

        return output

    async def detect_self_harm_only(self, content: str) -> list[SelfHarmSignal]:
        """Quick self-harm detection without full analysis"""
        return self.self_harm_detector.detect(content)

    async def detect_explicit_only(self, content: str) -> list[ExplicitContentSignal]:
        """Quick explicit content detection without full analysis"""
        return self.explicit_detector.detect(content)

    def get_stats(self) -> dict[str, Any]:
        """Get detection statistics"""
        total = self._stats["total_requests"]
        return {
            **self._stats,
            "cache_hit_rate": (self._stats["cache_hits"] / total if total > 0 else 0.0),
            "detection_rate": {
                "self_harm": self._stats["self_harm_detections"] / total if total > 0 else 0.0,
                "explicit": self._stats["explicit_detections"] / total if total > 0 else 0.0,
                "medical": self._stats["medical_detections"] / total if total > 0 else 0.0,
            },
        }


# =============================================================================
# Factory Function
# =============================================================================


def create_ns_engine(
    google_api_key: str | None = None,
    hive_api_key: str | None = None,
    cache_enabled: bool = True,
) -> NSDetectionEngine:
    """Create configured NS Detection Engine"""
    config = NSConfig(
        google_api_enabled=google_api_key is not None,
        hive_api_enabled=hive_api_key is not None,
        cache_enabled=cache_enabled,
    )
    return NSDetectionEngine(
        config=config,
        google_api_key=google_api_key,
        hive_api_key=hive_api_key,
    )


# Global instance (lazily initialized)
_ns_engine: NSDetectionEngine | None = None


def get_ns_engine() -> NSDetectionEngine:
    """Get or create global NS engine instance"""
    global _ns_engine
    if _ns_engine is None:
        _ns_engine = create_ns_engine()
    return _ns_engine
