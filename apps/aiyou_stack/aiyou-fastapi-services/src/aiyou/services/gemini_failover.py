# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Gemini Vertex AI Client
=======================

Vertex AI-only Gemini client with GCP credits utilization.

Features:
- Vertex AI primary (using $350K GCP credits)
- Exponential backoff on rate limits
- Health monitoring and metrics
- Model-specific configuration

Architecture:
    Vertex AI (Primary) → Error Handling

Usage:
    client = GeminiFailoverClient()
    response = await client.generate_content("Your prompt here")
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

# Redis removed - local metrics only
redis = None

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel as VertexModel
    from vertexai.generative_models import HarmBlockThreshold, HarmCategory
except ImportError:
    vertexai = None
    VertexModel = None
    HarmCategory = None
    HarmBlockThreshold = None


logger = logging.getLogger(__name__)


class GeminiFailoverError(Exception):
    """Raised when all failover attempts fail."""


class KeyStatus(Enum):
    """API key health status"""

    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXCEEDED = "quota_exceeded"
    FAILED = "failed"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class APIKeyMetrics:
    """Track metrics for a single API key"""

    key_id: str
    status: KeyStatus = KeyStatus.HEALTHY
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limit_hits: int = 0
    quota_exceeded_count: int = 0
    last_success: float = 0
    last_failure: float = 0
    circuit_failures: int = 0
    backoff_until: float = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100

    @property
    def is_available(self) -> bool:
        """Check if key is available for use"""
        if self.status == KeyStatus.CIRCUIT_OPEN:
            return False
        if self.backoff_until > time.time():
            return False
        return self.status in [KeyStatus.HEALTHY, KeyStatus.RATE_LIMITED]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "key_id": self.key_id,
            "status": self.status.value,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "rate_limit_hits": self.rate_limit_hits,
            "quota_exceeded_count": self.quota_exceeded_count,
            "success_rate": f"{self.success_rate:.2f}%",
            "is_available": self.is_available,
            "backoff_seconds": max(0, int(self.backoff_until - time.time())),
        }


class GeminiFailoverClient:
    """Vertex AI-only Gemini client utilizing GCP credits.

    Uses Vertex AI directly for all requests - leverages $350K GCP credits.
    No standard API keys needed.

    Example:
        export GCP_PROJECT_ID="your-project"

        client = GeminiFailoverClient()
        response = await client.generate_content("Hello, Gemini!")

    """

    def __init__(
        self,
        project_id: str | None = None,
        location: str = "us-central1",
        model_name: str = "gemini-3-pro-preview",
        redis_host: str = "localhost",
        redis_port: int = 6379,
        max_retries: int = 3,
        base_backoff: float = 1.0,
        circuit_threshold: int = 5,
        **kwargs,  # Ignore legacy api_keys parameter
    ):
        """Initialize Vertex AI client.

        Args:
            project_id: GCP project ID (default: acquired-jet-478701-b3)
            location: GCP region for Vertex AI
            model_name: Gemini model to use
            redis_host: Redis host for metrics storage
            redis_port: Redis port
            max_retries: Maximum retry attempts per request
            base_backoff: Base backoff time in seconds (exponential)
            circuit_threshold: Failures before opening circuit breaker

        """
        self.model_name = model_name
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.circuit_threshold = circuit_threshold

        # Vertex AI setup (primary and only provider)
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID", "acquired-jet-478701-b3")
        self.location = location
        self.vertex_model = None

        # Metrics tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.rate_limit_hits = 0

        if vertexai and VertexModel:
            try:
                vertexai.init(project=self.project_id, location=self.location)
                self.vertex_model = VertexModel(self.model_name)
                logger.info(f"✅ Vertex AI initialized: {self.project_id}/{self.model_name}")
            except Exception as e:
                logger.error(f"❌ Vertex AI initialization failed: {e}")
                raise RuntimeError(f"Vertex AI required but failed to initialize: {e}") from e
        else:
            raise RuntimeError("vertexai package not installed - required for Vertex-only mode")

        # Redis connection removed - standardizing on local/Easy-button metrics
        self.redis_client = None

        # Safety configuration
        if HarmCategory and HarmBlockThreshold:
            self.safety_config = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        else:
            self.safety_config = {}

        logger.info(f"🚀 GeminiFailoverClient initialized (Vertex AI only): {self.project_id}")

    def _update_metrics(self, success: bool, error_type: str | None = None):
        """Update metrics for Vertex AI requests"""
        self.total_requests += 1

        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            if error_type == "rate_limit":
                self.rate_limit_hits += 1

        # Persistence logic removed - local metrics only

    async def generate_content(
        self,
        prompt: str,
        system_instruction: str | None = None,
        json_output: bool = False,
        **kwargs,
    ) -> Any:
        """Generate content using Vertex AI.

        Args:
            prompt: The input prompt
            system_instruction: Optional system instruction
            json_output: Whether to return JSON formatted output
            **kwargs: Additional arguments passed to generate_content

        Returns:
            Generated response

        Raises:
            Exception: If Vertex AI fails after retries

        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                # Extract and merge generation_config from kwargs
                gen_config = kwargs.pop("generation_config", {})
                if json_output:
                    gen_config["response_mime_type"] = "application/json"

                # Use asyncio.to_thread to avoid blocking
                response = await asyncio.to_thread(
                    self.vertex_model.generate_content,
                    prompt,
                    generation_config=gen_config or None,
                    **kwargs,
                )

                # Success!
                self._update_metrics(success=True)
                logger.debug(f"✅ Vertex AI request succeeded (attempt {attempt + 1})")
                return response

            except Exception as e:
                error_str = str(e).lower()
                last_error = e

                # Classify error type
                if "429" in error_str or "rate" in error_str:
                    self._update_metrics(success=False, error_type="rate_limit")
                    logger.warning("⏳ Vertex AI rate limit hit, retrying...")
                else:
                    self._update_metrics(success=False)
                    logger.error(f"❌ Vertex AI error: {e}")

                # Exponential backoff before retry
                if attempt < self.max_retries - 1:
                    backoff = self.base_backoff * (2**attempt)
                    await asyncio.sleep(backoff)

        # Complete failure
        raise Exception(
            f"Vertex AI failed after {self.max_retries} attempts. Last error: {last_error}",
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics for Vertex AI"""
        success_rate = 0.0
        if self.total_requests > 0:
            success_rate = (self.successful_requests / self.total_requests) * 100

        return {
            "provider": "vertex_ai",
            "project_id": self.project_id,
            "model": self.model_name,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "rate_limit_hits": self.rate_limit_hits,
            "success_rate": f"{success_rate:.2f}%",
            "vertex_ai_available": self.vertex_model is not None,
        }

    def reset_metrics(self):
        """Reset all metrics"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.rate_limit_hits = 0
        logger.info("🔄 Metrics reset")

    def health_check(self) -> dict[str, Any]:
        """Perform health check on Vertex AI"""
        health_status = "healthy" if self.vertex_model else "critical"

        return {"status": health_status, "timestamp": time.time(), "metrics": self.get_metrics()}


# Convenience singleton for global use
_global_client: GeminiFailoverClient | None = None


def get_failover_client() -> GeminiFailoverClient:
    """Get or create global failover client instance"""
    global _global_client
    if _global_client is None:
        _global_client = GeminiFailoverClient()
    return _global_client
