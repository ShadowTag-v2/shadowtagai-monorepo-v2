# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 Grounded Governance Client

Layer 3 (JURA) implementation with Vertex AI Search grounding.
All governance queries go through doctrine datastore for citation-backed decisions.

Mode: "Always Grounded" - every query retrieves from sovereign memory

Target Metrics:
- Latency: <150ms (50-100ms retrieval overhead acceptable)
- Accuracy: 95%+ with citation backing
- Cost: $0.001-0.01/query
"""

import asyncio
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class GovernanceDecision(StrEnum):
    """Governance decision outcomes."""

    APPROVE = "APPROVE"
    DENY = "DENY"
    REVIEW = "REVIEW"


@dataclass
class ComplianceFlags:
    """Compliance domain flags."""

    gdpr: bool = False
    ccpa: bool = False
    pci_dss: bool = False
    coppa: bool = False
    hipaa: bool = False

    def active_domains(self) -> list[str]:
        """Get list of active compliance domains."""
        domains = []
        if self.gdpr:
            domains.append("GDPR")
        if self.ccpa:
            domains.append("CCPA")
        if self.pci_dss:
            domains.append("PCI-DSS")
        if self.coppa:
            domains.append("COPPA")
        if self.hipaa:
            domains.append("HIPAA")
        return domains


@dataclass
class GroundingChunk:
    """Citation from Vertex AI Search."""

    source: str
    content: str
    relevance_score: float
    document_id: str


@dataclass
class GroundedGovernanceResult:
    """Result from grounded governance scoring."""

    request_id: str
    decision: GovernanceDecision
    risk_score: int  # 0-100
    compliance_flags: ComplianceFlags
    reasoning: str
    citations: list[GroundingChunk]
    latency_ms: float
    grounded: bool  # True if citations were retrieved
    cost_usd: float
    timestamp: str


class Judge6Grounded:
    """Grounded governance scoring using Vertex AI Search.

    "Always Grounded" mode: Every governance query retrieves from
    the doctrine datastore for citation-backed, auditable decisions.

    Example:
        judge = Judge6Grounded()
        await judge.initialize()

        result = await judge.score_governance(
            request_type="purchase",
            content="Buy iPhone 15 Pro",
            user_region="EU",
            transaction_value=1199.00,
        )

        print(f"Decision: {result.decision}")
        print(f"Citations: {len(result.citations)}")
        for cite in result.citations:
            print(f"  - {cite.source}: {cite.content[:100]}")

    """

    # Compliance domain keywords
    COMPLIANCE_DOMAINS = {
        "gdpr": [
            "eu",
            "europe",
            "gdpr",
            "consent",
            "pii",
            "delete",
            "erasure",
            "data subject",
        ],
        "ccpa": ["california", "ccpa", "opt-out", "sell", "personal information"],
        "pci_dss": [
            "payment",
            "card",
            "credit",
            "checkout",
            "paypal",
            "stripe",
            "cardholder",
        ],
        "coppa": ["child", "minor", "kids", "under13", "parental"],
        "hipaa": ["health", "medical", "patient", "hipaa", "phi", "healthcare"],
    }

    # Risk weights by compliance domain
    DOMAIN_WEIGHTS = {
        "gdpr": 1.5,
        "ccpa": 1.2,
        "pci_dss": 2.0,
        "coppa": 2.5,
        "hipaa": 2.0,
    }

    # Base risk by request type
    TYPE_RISK = {
        "purchase": 30,
        "checkout": 40,
        "query": 10,
        "generate": 15,
        "delete": 50,
        "export": 35,
    }

    def __init__(
        self,
        project_id: str | None = None,
        location: str = "global",
        datastore_id: str | None = None,
    ):
        self.project_id = project_id or os.getenv("VERTEX_PROJECT_ID", "acquired-jet-478701-b3")
        self.location = location
        self.datastore_id = datastore_id or os.getenv(
            "JUDGE6_DATASTORE_ID",
            "judge6-doctrine-store",
        )

        # Derived paths
        self.collection_id = "default_collection"
        self.datastore_path = (
            f"projects/{self.project_id}/locations/{self.location}/"
            f"collections/{self.collection_id}/dataStores/{self.datastore_id}"
        )

        # Clients (lazy initialized)
        self._search_client = None
        self._genai_model = None
        self._grounding_tool = None
        self._initialized = False

        # Stats
        self.request_count = 0
        self.total_latency_ms = 0.0
        self.cache_hits = 0

        # Simple LRU cache for repeated queries
        self._cache: dict[str, GroundedGovernanceResult] = {}
        self._cache_max_size = 100

    async def initialize(self):
        """Initialize Vertex AI clients."""
        if self._initialized:
            return

        logger.info(f"Initializing Judge 6 Grounded with datastore: {self.datastore_id}")

        try:
            # Initialize Vertex AI
            import vertexai
            from vertexai.preview.generative_models import (
                GenerativeModel,
                Tool,
                grounding,
            )

            vertexai.init(project=self.project_id, location="us-central1")

            # Create grounding tool from datastore
            self._grounding_tool = Tool.from_retrieval(
                grounding.Retrieval(source=grounding.VertexAISearch(datastore=self.datastore_path)),
            )

            # Initialize Gemini model with grounding
            self._genai_model = GenerativeModel(
                "gemini-3.1-flash-lite-preview",
                tools=[self._grounding_tool],
            )

            self._initialized = True
            logger.info("✓ Judge 6 Grounded initialized with Vertex AI Search")

        except ImportError as e:
            logger.warning(f"Vertex AI SDK not available: {e}")
            logger.info("Running in mock mode without grounding")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise

    def _generate_request_id(self, content: str) -> str:
        """Generate unique request ID."""
        timestamp = time.time()
        return hashlib.sha256(f"{content}{timestamp}".encode()).hexdigest()[:16]

    def _check_compliance_domains(self, content: str, user_region: str | None) -> ComplianceFlags:
        """Determine which compliance domains apply."""
        combined_text = f"{content} {user_region or ''}".lower()

        return ComplianceFlags(
            gdpr=any(kw in combined_text for kw in self.COMPLIANCE_DOMAINS["gdpr"]),
            ccpa=any(kw in combined_text for kw in self.COMPLIANCE_DOMAINS["ccpa"]),
            pci_dss=any(kw in combined_text for kw in self.COMPLIANCE_DOMAINS["pci_dss"]),
            coppa=any(kw in combined_text for kw in self.COMPLIANCE_DOMAINS["coppa"]),
            hipaa=any(kw in combined_text for kw in self.COMPLIANCE_DOMAINS["hipaa"]),
        )

    def _calculate_risk_score(
        self,
        request_type: str,
        compliance_flags: ComplianceFlags,
        transaction_value: float | None,
    ) -> int:
        """Calculate risk score (0-100)."""
        # Base risk from request type
        base_risk = self.TYPE_RISK.get(request_type.lower(), 20)

        # Transaction value risk
        if transaction_value:
            if transaction_value > 1000:
                base_risk += 25
            elif transaction_value > 100:
                base_risk += 10

        # Compliance domain penalties
        for domain in ["gdpr", "ccpa", "pci_dss", "coppa", "hipaa"]:
            if getattr(compliance_flags, domain):
                weight = self.DOMAIN_WEIGHTS.get(domain, 1.0)
                base_risk += int(10 * weight)

        return min(base_risk, 100)

    def _make_decision(self, risk_score: int) -> tuple[GovernanceDecision, str]:
        """Make governance decision based on risk score."""
        if risk_score <= 25:
            return GovernanceDecision.APPROVE, "Low risk - auto-approved"
        if risk_score <= 50:
            return GovernanceDecision.APPROVE, "Medium risk - approved with monitoring"
        if risk_score <= 75:
            return GovernanceDecision.REVIEW, "High risk - requires human review"
        return GovernanceDecision.DENY, "Critical risk - auto-denied"

    async def _retrieve_grounding(
        self,
        query: str,
        compliance_flags: ComplianceFlags,
    ) -> list[GroundingChunk]:
        """Retrieve grounding from Vertex AI Search."""
        if not self._genai_model:
            return []

        try:
            # Build governance-focused prompt
            active_domains = compliance_flags.active_domains()
            prompt = f"""Based on our governance doctrine, evaluate this request:

REQUEST: {query}

COMPLIANCE DOMAINS: {", ".join(active_domains) if active_domains else "General"}

Provide:
1. Applicable policy citations
2. Risk factors identified
3. Recommended controls

Be specific and cite relevant doctrine sections."""

            # Generate with grounding
            response = await asyncio.to_thread(
                self._genai_model.generate_content,
                prompt,
            )

            # Extract grounding chunks from response
            citations = []
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "grounding_metadata"):
                    grounding_metadata = candidate.grounding_metadata
                    if hasattr(grounding_metadata, "grounding_chunks"):
                        for chunk in grounding_metadata.grounding_chunks:
                            citations.append(
                                GroundingChunk(
                                    source=getattr(chunk, "web", {}).get("uri", "doctrine"),
                                    content=getattr(chunk, "web", {}).get("title", "")[:200],
                                    relevance_score=getattr(chunk, "relevance_score", 0.8),
                                    document_id=hashlib.sha256(str(chunk).encode()).hexdigest()[:8],
                                ),
                            )

            return citations

        except Exception as e:
            logger.warning(f"Grounding retrieval failed: {e}")
            return []

    async def score_governance(
        self,
        request_type: str,
        content: str,
        user_region: str | None = None,
        transaction_value: float | None = None,
        use_cache: bool = True,
    ) -> GroundedGovernanceResult:
        """Score governance request with Vertex AI Search grounding.

        Args:
            request_type: Type of request (purchase, checkout, query, generate, delete)
            content: Request content/query
            user_region: User's region (EU, US-CA, etc.)
            transaction_value: Transaction value in USD (optional)
            use_cache: Whether to use cached results

        Returns:
            GroundedGovernanceResult with decision, risk score, citations, and reasoning

        """
        if not self._initialized:
            await self.initialize()

        start_time = time.time()

        # Check cache
        cache_key = hashlib.sha256(
            f"{request_type}{content}{user_region}{transaction_value}".encode(),
        ).hexdigest()
        if use_cache and cache_key in self._cache:
            self.cache_hits += 1
            logger.debug("Cache hit for governance request")
            return self._cache[cache_key]

        # Generate request ID
        request_id = self._generate_request_id(content)

        # Check compliance domains
        compliance_flags = self._check_compliance_domains(content, user_region)

        # Calculate risk score
        risk_score = self._calculate_risk_score(request_type, compliance_flags, transaction_value)

        # Make decision
        decision, base_reasoning = self._make_decision(risk_score)

        # Retrieve grounding (Always Grounded mode)
        citations = await self._retrieve_grounding(content, compliance_flags)

        # Enhance reasoning with compliance info
        reasoning = base_reasoning
        active_domains = compliance_flags.active_domains()
        if active_domains:
            reasoning += f" | Compliance: {', '.join(active_domains)}"
        if citations:
            reasoning += f" | {len(citations)} doctrine citations"

        # Calculate latency and cost
        latency_ms = (time.time() - start_time) * 1000
        cost_usd = 0.001 if not citations else 0.005  # Higher cost with grounding

        # Build result
        result = GroundedGovernanceResult(
            request_id=request_id,
            decision=decision,
            risk_score=risk_score,
            compliance_flags=compliance_flags,
            reasoning=reasoning,
            citations=citations,
            latency_ms=round(latency_ms, 2),
            grounded=len(citations) > 0,
            cost_usd=cost_usd,
            timestamp=datetime.now(UTC).isoformat(),
        )

        # Update stats
        self.request_count += 1
        self.total_latency_ms += latency_ms

        # Cache result
        if use_cache:
            if len(self._cache) >= self._cache_max_size:
                # Remove oldest entry
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[cache_key] = result

        logger.info(
            f"Governance scored: {decision.value} (risk={risk_score}, "
            f"latency={latency_ms:.0f}ms, citations={len(citations)})",
        )

        return result

    async def batch_score(
        self,
        requests: list[dict[str, Any]],
        max_concurrent: int = 10,
    ) -> list[GroundedGovernanceResult]:
        """Score multiple governance requests concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def score_with_semaphore(req: dict[str, Any]) -> GroundedGovernanceResult:
            async with semaphore:
                return await self.score_governance(**req)

        tasks = [score_with_semaphore(req) for req in requests]
        return await asyncio.gather(*tasks)

    def get_stats(self) -> dict[str, Any]:
        """Get governance stats."""
        return {
            "request_count": self.request_count,
            "avg_latency_ms": round(self.total_latency_ms / max(1, self.request_count), 2),
            "cache_size": len(self._cache),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": round(self.cache_hits / max(1, self.request_count) * 100, 1),
            "datastore_path": self.datastore_path,
            "initialized": self._initialized,
        }


# Global instance
_judge: Judge6Grounded | None = None


async def get_judge() -> Judge6Grounded:
    """Get or create global Judge 6 instance."""
    global _judge
    if _judge is None:
        _judge = Judge6Grounded()
        await _judge.initialize()
    return _judge


# Convenience function
async def score_governance(
    request_type: str,
    content: str,
    user_region: str | None = None,
    transaction_value: float | None = None,
) -> GroundedGovernanceResult:
    """Quick governance scoring."""
    judge = await get_judge()
    return await judge.score_governance(
        request_type=request_type,
        content=content,
        user_region=user_region,
        transaction_value=transaction_value,
    )


if __name__ == "__main__":

    async def test():
        print("=== Judge 6 Grounded Governance Test ===\n")

        judge = Judge6Grounded()
        await judge.initialize()

        # Test cases
        test_cases = [
            {
                "request_type": "purchase",
                "content": "Buy iPhone 15 Pro Max 256GB",
                "user_region": "EU",
                "transaction_value": 1199.00,
            },
            {
                "request_type": "delete",
                "content": "Delete all user data for GDPR request",
                "user_region": "EU",
            },
            {
                "request_type": "checkout",
                "content": "Process payment with credit card ending 4242",
                "user_region": "US-CA",
                "transaction_value": 299.99,
            },
            {
                "request_type": "query",
                "content": "Search for kids toys under $50",
                "user_region": "US",
            },
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"--- Test {i}: {test['request_type'].upper()} ---")
            result = await judge.score_governance(**test)

            print(f"Decision: {result.decision.value}")
            print(f"Risk Score: {result.risk_score}/100")
            print(f"Compliance: {result.compliance_flags.active_domains()}")
            print(f"Grounded: {result.grounded}")
            print(f"Citations: {len(result.citations)}")
            print(f"Latency: {result.latency_ms:.0f}ms")
            print(f"Reasoning: {result.reasoning}")
            print()

        print("=== Stats ===")
        print(judge.get_stats())

    asyncio.run(test())
