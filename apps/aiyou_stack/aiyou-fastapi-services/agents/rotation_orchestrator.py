"""
Rotation Orchestrator - Intelligent Model Pool Manager

Manages 10 Antigravity instances × 3 tiers = 30 endpoints with:
- Rate limit tracking
- Auto-switchback to higher tiers
- Priority-based selection
"""

import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum


class ModelTier(Enum):
    """Model tier priority (lower = higher priority)"""

    GEMINI_HIGH = 1
    GEMINI_LOW = 2
    FALLBACK = 3


@dataclass
class ModelEndpoint:
    """Represents a single model endpoint"""

    id: str
    tier: ModelTier
    model_name: str
    api_key: str
    provider: str  # "gemini", "openai", "grok", "perplexity", "codestral"
    rate_limited_until: datetime | None = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    def is_available(self) -> bool:
        """Check if endpoint is currently available"""
        if self.rate_limited_until is None:
            return True
        return datetime.now() >= self.rate_limited_until

    def mark_rate_limited(self, duration_seconds: int = 60):
        """Mark endpoint as rate limited"""
        self.rate_limited_until = datetime.now() + timedelta(seconds=duration_seconds)

    def clear_rate_limit(self):
        """Clear rate limit"""
        self.rate_limited_until = None


class RotationOrchestrator:
    """
    Manages model rotation across 10 instances × 3 tiers.

    Always selects the highest-tier available endpoint and automatically
    switches back when higher tiers become available.
    """

    def __init__(self):
        self.endpoints: list[ModelEndpoint] = []
        self.monitor_thread: threading.Thread | None = None
        self.running = False
        self._lock = threading.Lock()

        self._initialize_endpoints()

    def _initialize_endpoints(self):
        """Initialize the 5 Antigravity Gemini endpoint pool (3 High + 2 Low)"""

        # Tier 1: Gemini 3 Pro High (3 instances)
        for i in range(3):
            self.endpoints.append(
                ModelEndpoint(
                    id=f"antigravity-gemini-high-{i + 1:02d}",
                    tier=ModelTier.GEMINI_HIGH,
                    model_name="gemini-3-pro-high",
                    api_key=os.getenv(f"GEMINI_API_KEY_{i + 1}", os.getenv("GEMINI_API_KEY", "")),
                    provider="gemini",
                )
            )

        # Tier 2: Gemini 3 Pro Low (2 instances)
        for i in range(2):
            self.endpoints.append(
                ModelEndpoint(
                    id=f"antigravity-gemini-low-{i + 1:02d}",
                    tier=ModelTier.GEMINI_LOW,
                    model_name="gemini-3-pro-low",
                    api_key=os.getenv(
                        f"GEMINI_API_KEY_{i + 3 + 1}", os.getenv("GEMINI_API_KEY", "")
                    ),
                    provider="gemini",
                )
            )

        print(
            f"///▞ ROTATION ORCHESTRATOR :: Initialized {len(self.endpoints)} Antigravity Gemini endpoints"
        )

    def start_monitoring(self):
        """Start background thread to monitor rate limits"""
        if self.running:
            return
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("///▞ ROTATION ORCHESTRATOR :: Rate limit monitor started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def _monitor_loop(self):
        """Background loop to check and clear expired rate limits"""
        while self.running:
            now = datetime.now()
            with self._lock:
                for endpoint in self.endpoints:
                    if endpoint.rate_limited_until and now >= endpoint.rate_limited_until:
                        print(f"///▞ ROTATION :: Cleared rate limit for {endpoint.id}")
                        endpoint.clear_rate_limit()
            time.sleep(10)  # Check every 10 seconds

    def get_best_endpoint(self) -> ModelEndpoint | None:
        """
        Select the best available endpoint based on tier priority.
        Returns None if all endpoints are rate limited.
        """
        with self._lock:
            # Sort by tier (ascending) then by availability
            available = [e for e in self.endpoints if e.is_available()]

            if not available:
                return None

            # Sort by tier priority
            available.sort(key=lambda e: e.tier.value)

            # Return the first (highest priority) available endpoint
            return available[0]

    def execute_with_rotation(self, task_fn, *args, **kwargs):
        """
        Execute a task with automatic tier rotation on rate limits.

        Args:
            task_fn: Function that takes (endpoint, *args, **kwargs) and returns result
            *args, **kwargs: Arguments to pass to task_fn

        Returns:
            Result from task_fn

        Raises:
            RuntimeError: If all endpoints are rate limited
        """
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            endpoint = self.get_best_endpoint()

            if endpoint is None:
                # All endpoints rate limited
                print("///▞ ROTATION :: WARNING - All endpoints rate limited!")
                time.sleep(5)  # Wait before retry
                retry_count += 1
                continue

            try:
                # Execute task with selected endpoint
                print(f"///▞ ROTATION :: Using {endpoint.id} (Tier {endpoint.tier.name})")
                with self._lock:
                    endpoint.total_requests += 1

                result = task_fn(endpoint, *args, **kwargs)

                with self._lock:
                    endpoint.successful_requests += 1

                return result

            except Exception as e:
                with self._lock:
                    endpoint.failed_requests += 1

                # Check if it's a rate limit error
                if "429" in str(e) or "rate" in str(e).lower():
                    print(f"///▞ ROTATION :: Rate limit hit on {endpoint.id}, switching...")
                    endpoint.mark_rate_limited(duration_seconds=60)
                    retry_count += 1
                    continue
                else:
                    # Other error, re-raise
                    raise

        raise RuntimeError("All endpoints exhausted or rate limited")

    def get_stats(self) -> dict:
        """Get orchestrator statistics"""
        with self._lock:
            total_requests = sum(e.total_requests for e in self.endpoints)
            successful = sum(e.successful_requests for e in self.endpoints)
            failed = sum(e.failed_requests for e in self.endpoints)
            rate_limited = sum(1 for e in self.endpoints if not e.is_available())

            tier_stats = {}
            for tier in ModelTier:
                tier_endpoints = [e for e in self.endpoints if e.tier == tier]
                tier_stats[tier.name] = {
                    "total": len(tier_endpoints),
                    "available": sum(1 for e in tier_endpoints if e.is_available()),
                    "requests": sum(e.total_requests for e in tier_endpoints),
                }

            return {
                "total_endpoints": len(self.endpoints),
                "available_endpoints": len(self.endpoints) - rate_limited,
                "rate_limited_endpoints": rate_limited,
                "total_requests": total_requests,
                "successful_requests": successful,
                "failed_requests": failed,
                "tier_breakdown": tier_stats,
            }
