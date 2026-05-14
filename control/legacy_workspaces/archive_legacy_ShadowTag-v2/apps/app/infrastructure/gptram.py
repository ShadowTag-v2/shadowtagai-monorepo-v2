#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
GPTRAM: Redis-based Long-term Memory for AI Agents

Provides:
- Verdict caching (avoid re-judging same content)
- Violation tracking (pattern detection)
- Context persistence (session continuity)
- Integration with FlyingMonkeys/Judge governance

Part of PNKLN governance stack.
"""

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class Verdict:
    """Cached verdict for a task context."""

    approved: bool
    consensus_ratio: float
    risk_category: str
    severity: str
    risk_level: str
    has_brake: bool
    timestamp: str
    rule_ids: list[str]
    metadata: dict[str, Any]


@dataclass
class Violation:
    """Recorded violation event."""

    rule_id: str
    severity: str
    timestamp: str
    context_hash: str
    details: dict[str, Any]


class GPTRAM:
    """
    GPU-accelerated Redis AI Memory

    Long-term memory layer for FlyingMonkeys/Judge governance.
    Caches verdicts, tracks violations, maintains context.

    Features:
    - Verdict caching with 24h TTL
    - Violation tracking with 7d TTL
    - Session persistence
    - In-memory fallback when Redis unavailable
    """

    VERSION = "1.0"
    VERDICT_TTL = 86400  # 24 hours
    VIOLATION_TTL = 604800  # 7 days
    SESSION_TTL = 86400  # 24 hours

    def __init__(self, redis_url: str = None, prefix: str = "gptram"):
        """
        Initialize GPTRAM.

        Args:
            redis_url: Redis connection URL (default: REDIS_URL env or localhost)
            prefix: Key prefix for all Redis keys
        """
        self.prefix = prefix
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")

        # Stats tracking
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "verdicts_saved": 0,
            "violations_logged": 0,
            "sessions_created": 0,
        }

        if REDIS_AVAILABLE:
            try:
                self.client = redis.from_url(self.redis_url, decode_responses=True)
                self._test_connection()
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis connection failed: {e}")
                self.client = None
                self._memory = {}
        else:
            self.client = None
            self._memory = {}  # Fallback in-memory store

        mode = "Redis" if self.client else "Memory"
        print(f"///▞ GPTRAM :: v{self.VERSION} :: {mode} mode")

    def _test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            self.client.ping()
            return True
        except Exception as e:
            print(f"///▞ GPTRAM :: Redis ping failed: {e}")
            self.client = None
            self._memory = {}
            return False

    def _hash_context(self, context: str) -> str:
        """Create deterministic hash of context."""
        return hashlib.sha256(context.encode()).hexdigest()[:16]

    def _key(self, *parts) -> str:
        """Build Redis key with prefix."""
        return f"{self.prefix}:{':'.join(str(p) for p in parts)}"

    # === Verdict Operations ===

    async def get_prior_verdict(self, task_context: str) -> dict[str, Any] | None:
        """
        Check if we've already judged this context.

        Args:
            task_context: The task/content to check

        Returns:
            Cached verdict if exists, None otherwise
        """
        ctx_hash = self._hash_context(task_context)
        key = self._key("verdict", ctx_hash)

        if self.client:
            try:
                data = self.client.get(key)
                if data:
                    self.stats["cache_hits"] += 1
                    return json.loads(data)
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis get error: {e}")

        if not self.client and key in self._memory:
            self.stats["cache_hits"] += 1
            return self._memory[key]

        self.stats["cache_misses"] += 1
        return None

    async def save_verdict(self, task_context: str, verdict: dict[str, Any]) -> str:
        """
        Cache a verdict for future lookups.

        Args:
            task_context: The judged content
            verdict: The verdict to cache

        Returns:
            Context hash key
        """
        ctx_hash = self._hash_context(task_context)
        key = self._key("verdict", ctx_hash)

        verdict_data = {
            **verdict,
            "context_hash": ctx_hash,
            "cached_at": datetime.now(UTC).isoformat(),
        }

        if self.client:
            try:
                self.client.setex(key, self.VERDICT_TTL, json.dumps(verdict_data))
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis set error: {e}")
                self._memory[key] = verdict_data
        else:
            self._memory[key] = verdict_data

        self.stats["verdicts_saved"] += 1
        return ctx_hash

    # === Violation Tracking ===

    async def log_violation(
        self,
        rule_id: str,
        severity: str,
        context_hash: str = "",
        details: dict[str, Any] = None,
    ) -> str:
        """
        Record a violation event.

        Args:
            rule_id: ATP_519_xxx rule identifier
            severity: I/II/III/IV severity level
            context_hash: Optional link to verdict
            details: Additional violation details

        Returns:
            Violation key
        """
        violation = Violation(
            rule_id=rule_id,
            severity=severity,
            timestamp=datetime.now(UTC).isoformat(),
            context_hash=context_hash,
            details=details or {},
        )

        # Unique key for this violation
        ts = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
        violation_key = self._key("violation", rule_id, ts)

        if self.client:
            try:
                # Store individual violation
                self.client.setex(violation_key, self.VIOLATION_TTL, json.dumps(asdict(violation)))

                # Increment violation counter
                counter_key = self._key("violation_count", rule_id)
                self.client.incr(counter_key)

                # Track by severity
                severity_key = self._key("severity_count", severity)
                self.client.incr(severity_key)

                # Track total
                self.client.incr(self._key("violation_total"))
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis violation log error: {e}")
                self._memory[violation_key] = asdict(violation)
        else:
            self._memory[violation_key] = asdict(violation)

        self.stats["violations_logged"] += 1
        return violation_key

    async def get_violation_stats(self) -> dict[str, Any]:
        """Get violation statistics."""
        stats = {"by_rule": {}, "by_severity": {}, "total": 0}

        if self.client:
            try:
                # Get all violation counts by rule
                for key in self.client.scan_iter(f"{self.prefix}:violation_count:*"):
                    rule_id = key.split(":")[-1]
                    count = int(self.client.get(key) or 0)
                    stats["by_rule"][rule_id] = count

                # Get severity counts
                for severity in ["I", "II", "III", "IV"]:
                    key = self._key("severity_count", severity)
                    count = int(self.client.get(key) or 0)
                    stats["by_severity"][severity] = count

                # Get total
                total_key = self._key("violation_total")
                stats["total"] = int(self.client.get(total_key) or 0)
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis stats error: {e}")
        else:
            # Count from memory
            for key, value in self._memory.items():
                if "violation:" in key and isinstance(value, dict):
                    rule_id = value.get("rule_id", "unknown")
                    severity = value.get("severity", "IV")

                    stats["by_rule"][rule_id] = stats["by_rule"].get(rule_id, 0) + 1
                    stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
                    stats["total"] += 1

        return stats

    async def get_recent_violations(self, limit: int = 10, rule_id: str = None) -> list[dict[str, Any]]:
        """Get recent violations."""
        violations = []

        if self.client:
            try:
                pattern = self._key("violation", rule_id or "*", "*")
                for key in self.client.scan_iter(pattern):
                    data = self.client.get(key)
                    if data:
                        violations.append(json.loads(data))
                    if len(violations) >= limit:
                        break
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis scan error: {e}")
        else:
            for key, value in self._memory.items():
                if "violation:" in key:
                    if rule_id is None or rule_id in key:
                        violations.append(value)
                if len(violations) >= limit:
                    break

        # Sort by timestamp descending
        violations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return violations[:limit]

    # === Session Persistence ===

    async def save_session(self, session_id: str, context: dict[str, Any]) -> None:
        """Save session context for continuity."""
        key = self._key("session", session_id)

        context_data = {**context, "updated_at": datetime.now(UTC).isoformat()}

        if self.client:
            try:
                self.client.setex(key, self.SESSION_TTL, json.dumps(context_data))
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis session save error: {e}")
                self._memory[key] = context_data
        else:
            self._memory[key] = context_data

        self.stats["sessions_created"] += 1

    async def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session context."""
        key = self._key("session", session_id)

        if self.client:
            try:
                data = self.client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis session get error: {e}")

        if not self.client:
            return self._memory.get(key)

        return None

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        key = self._key("session", session_id)

        if self.client:
            try:
                return bool(self.client.delete(key))
            except Exception as e:
                print(f"///▞ GPTRAM :: Redis session delete error: {e}")

        if key in self._memory:
            del self._memory[key]
            return True

        return False

    # === Utility ===

    def flush(self, pattern: str = "*") -> int:
        """Clear matching keys (use carefully)."""
        if not self.client:
            count = len(self._memory)
            self._memory.clear()
            return count

        count = 0
        try:
            for key in self.client.scan_iter(f"{self.prefix}:{pattern}"):
                self.client.delete(key)
                count += 1
        except Exception as e:
            print(f"///▞ GPTRAM :: Redis flush error: {e}")

        return count

    def get_stats(self) -> dict[str, Any]:
        """Get GPTRAM statistics."""
        return {
            "version": self.VERSION,
            "mode": "redis" if self.client else "memory",
            "redis_url": self.redis_url if self.client else None,
            **self.stats,
            "cache_hit_ratio": (self.stats["cache_hits"] / max(self.stats["cache_hits"] + self.stats["cache_misses"], 1)),
        }

    def health_check(self) -> dict[str, Any]:
        """Check GPTRAM health."""
        result = {
            "healthy": True,
            "mode": "redis" if self.client else "memory",
            "version": self.VERSION,
        }

        if self.client:
            try:
                self.client.ping()
                result["redis_connected"] = True
            except Exception as e:
                result["healthy"] = False
                result["redis_connected"] = False
                result["error"] = str(e)
        else:
            result["redis_connected"] = False
            result["memory_keys"] = len(self._memory)

        return result


# Singleton instance
_gptram: GPTRAM | None = None


def get_gptram() -> GPTRAM:
    """Get or create GPTRAM singleton."""
    global _gptram
    if _gptram is None:
        _gptram = GPTRAM()
    return _gptram


def create_gptram(redis_url: str = None) -> GPTRAM:
    """Create a new GPTRAM instance."""
    return GPTRAM(redis_url=redis_url)


# Standalone test
if __name__ == "__main__":
    import asyncio

    async def main():
        print("=" * 60)
        print("GPTRAM Test Suite")
        print("=" * 60)

        gptram = get_gptram()

        # Test 1: Health check
        print("\n[Test 1] Health Check")
        health = gptram.health_check()
        print(f"  Health: {health}")

        # Test 2: Verdict caching
        print("\n[Test 2] Verdict Caching")
        context = "Test task: Deploy new feature to production"

        # Check for prior verdict (should be None)
        prior = await gptram.get_prior_verdict(context)
        print(f"  Prior verdict: {prior}")

        # Save a verdict
        verdict = {
            "approved": True,
            "consensus_ratio": 0.85,
            "risk_category": "D",
            "severity": "III",
            "risk_level": "L",
            "has_brake": True,
            "rule_ids": ["ATP_519_001"],
        }
        ctx_hash = await gptram.save_verdict(context, verdict)
        print(f"  Saved verdict hash: {ctx_hash}")

        # Retrieve it (should hit cache)
        cached = await gptram.get_prior_verdict(context)
        print(f"  Cached verdict: {cached.get('approved') if cached else None}")

        # Test 3: Violation logging
        print("\n[Test 3] Violation Logging")
        violation_key = await gptram.log_violation(
            rule_id="ATP_519_001",
            severity="III",
            context_hash=ctx_hash,
            details={"reason": "Missing brake mechanism"},
        )
        print(f"  Logged violation: {violation_key}")

        # Log another violation
        await gptram.log_violation(
            rule_id="ATP_519_002",
            severity="II",
            details={"reason": "High risk without approval"},
        )

        # Get stats
        violation_stats = await gptram.get_violation_stats()
        print(f"  Violation stats: {violation_stats}")

        # Get recent violations
        recent = await gptram.get_recent_violations(limit=5)
        print(f"  Recent violations: {len(recent)}")

        # Test 4: Session persistence
        print("\n[Test 4] Session Persistence")
        session_id = "test_session_123"
        await gptram.save_session(
            session_id,
            {
                "user_id": "user_001",
                "agent_id": "agent_042",
                "context": "Working on feature X",
            },
        )
        print(f"  Saved session: {session_id}")

        session = await gptram.get_session(session_id)
        print(f"  Retrieved session: {session.get('user_id') if session else None}")

        # Test 5: Stats
        print("\n[Test 5] GPTRAM Stats")
        stats = gptram.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    asyncio.run(main())
