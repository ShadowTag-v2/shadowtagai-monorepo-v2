"""
Perplexity MCP Server - Model Context Protocol Server for Perplexity Integration

Routes Comet browser queries through Judge #6 for compliance scoring,
stamps SHADOWTAG watermarks on AI-generated content, and logs all
transactions to Apertus-compatible manifest for "Total Recall" audit.

Target Metrics:
- Judge #6 latency: <35ms
- Watermark overhead: <5ms
- Manifest write: <2ms
"""

import asyncio
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class GovernanceResult:
    """Result of Judge #6 governance check."""

    decision: str  # APPROVE, DENY, REVIEW
    risk_score: int  # 0-100
    compliance_flags: dict[str, bool]  # GDPR, CCPA, PCI-DSS, etc.
    latency_ms: float
    reasoning: str
    request_id: str


@dataclass
class WatermarkResult:
    """Result of SHADOWTAG watermarking."""

    content: str
    signature: str
    merkle_root: str
    timestamp: str
    metadata: dict[str, Any]


@dataclass
class ManifestEntry:
    """Apertus-compatible manifest entry."""

    run_id: str
    timestamp: str
    context_id: str
    content: str
    decision: str
    risk_score: int
    watermark_sig: str
    safety_scores: dict[str, Any]
    meta: dict[str, Any]


class PerplexityMCPServer:
    """
    MCP Server for Perplexity Comet Browser Integration.

    Provides three core tools:
    1. governance_score - Judge #6 compliance check
    2. watermark_content - SHADOWTAG DCT watermarking
    3. log_to_manifest - Apertus JSONL logging

    Example:
        ```python
        server = PerplexityMCPServer()

        # Score a shopping transaction
        result = await server.governance_score(
            request_type="purchase",
            content="Buy iPhone 15 Pro",
            user_context={"region": "EU", "payment": "PayPal"}
        )

        # Watermark AI response
        watermarked = await server.watermark_content(
            content="Based on reviews, the iPhone 15 Pro...",
            source="perplexity_comet"
        )

        # Log to manifest
        await server.log_to_manifest(result, watermarked)
        ```
    """

    def __init__(
        self,
        manifest_path: str | None = None,
        judge6_latency_target_ms: int = 35,
        enable_shadowtag: bool = True,
    ):
        self.manifest_path = Path(manifest_path or "./logs/pnkln/perplexity/manifest.jsonl")
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)

        self.judge6_latency_target = judge6_latency_target_ms
        self.enable_shadowtag = enable_shadowtag

        # Performance tracking
        self.governance_latencies: list[float] = []
        self.watermark_latencies: list[float] = []

        # Compliance domain weights
        self.compliance_domains = {
            "GDPR": {
                "keywords": ["eu", "europe", "gdpr", "consent", "pii", "delete"],
                "weight": 1.5,
            },
            "CCPA": {"keywords": ["california", "ccpa", "opt-out", "sell"], "weight": 1.2},
            "PCI_DSS": {
                "keywords": ["payment", "card", "credit", "checkout", "paypal", "shopify"],
                "weight": 2.0,
            },
            "COPPA": {"keywords": ["child", "minor", "kids", "under13"], "weight": 2.5},
            "HIPAA": {"keywords": ["health", "medical", "patient", "hipaa"], "weight": 2.0},
        }

        print("Perplexity MCP Server initialized")
        print(f"  Manifest: {self.manifest_path}")
        print(f"  Judge #6 target: <{judge6_latency_target_ms}ms")
        print(f"  SHADOWTAG: {'enabled' if enable_shadowtag else 'disabled'}")

    async def governance_score(
        self,
        request_type: str,
        content: str,
        user_context: dict[str, Any],
        transaction_value: float | None = None,
    ) -> GovernanceResult:
        """
        Judge #6 governance scoring for Perplexity requests.

        Evaluates compliance requirements and risk level for:
        - Shopping transactions (Comet checkout)
        - Content generation (AI responses)
        - Data access (user queries)

        Args:
            request_type: Type of request (purchase, query, generate)
            content: Request content/query
            user_context: User context (region, payment method, etc.)
            transaction_value: Optional transaction amount in USD

        Returns:
            GovernanceResult with decision, risk score, and reasoning
        """
        start_time = time.time()
        request_id = hashlib.sha256(f"{content}{time.time()}".encode()).hexdigest()[:16]

        # Analyze compliance requirements
        compliance_flags = self._check_compliance_domains(content, user_context)

        # Calculate risk score
        risk_score = self._calculate_risk_score(
            request_type, content, user_context, compliance_flags, transaction_value
        )

        # Make decision
        if risk_score <= 25:
            decision = "APPROVE"
            reasoning = "Low risk - auto-approved"
        elif risk_score <= 50:
            decision = "APPROVE"
            reasoning = "Medium risk - approved with monitoring"
        elif risk_score <= 75:
            decision = "REVIEW"
            reasoning = "High risk - requires human review"
        else:
            decision = "DENY"
            reasoning = "Critical risk - auto-denied"

        # Add compliance-specific reasoning
        active_compliance = [k for k, v in compliance_flags.items() if v]
        if active_compliance:
            reasoning += f" | Compliance: {', '.join(active_compliance)}"

        latency_ms = (time.time() - start_time) * 1000
        self.governance_latencies.append(latency_ms)

        # SLA check
        if latency_ms > self.judge6_latency_target:
            print(
                f"  SLA BREACH: Judge #6 took {latency_ms:.1f}ms (target: {self.judge6_latency_target}ms)"
            )

        return GovernanceResult(
            decision=decision,
            risk_score=risk_score,
            compliance_flags=compliance_flags,
            latency_ms=latency_ms,
            reasoning=reasoning,
            request_id=request_id,
        )

    def _check_compliance_domains(
        self, content: str, user_context: dict[str, Any]
    ) -> dict[str, bool]:
        """Check which compliance domains apply."""
        flags = {}
        combined_text = f"{content} {json.dumps(user_context)}".lower()

        for domain, config in self.compliance_domains.items():
            flags[domain] = any(kw in combined_text for kw in config["keywords"])

        return flags

    def _calculate_risk_score(
        self,
        request_type: str,
        content: str,
        user_context: dict[str, Any],
        compliance_flags: dict[str, bool],
        transaction_value: float | None,
    ) -> int:
        """Calculate risk score (0-100)."""
        base_risk = 0

        # Request type risk
        type_risks = {
            "purchase": 30,
            "checkout": 40,
            "query": 10,
            "generate": 15,
            "delete": 50,
        }
        base_risk += type_risks.get(request_type.lower(), 20)

        # Transaction value risk
        if transaction_value:
            if transaction_value > 1000:
                base_risk += 25
            elif transaction_value > 100:
                base_risk += 10

        # Compliance domain penalties
        for domain, active in compliance_flags.items():
            if active:
                weight = self.compliance_domains[domain]["weight"]
                base_risk += int(10 * weight)

        # Content length penalty (longer = more risk surface)
        if len(content) > 1000:
            base_risk += 5

        return min(base_risk, 100)

    async def watermark_content(
        self,
        content: str,
        source: str,
        metadata: dict[str, Any] | None = None,
    ) -> WatermarkResult:
        """
        Apply SHADOWTAG watermark to AI-generated content.

        Creates cryptographic signature and Merkle root for:
        - Provenance tracking
        - Tamper detection
        - Attribution

        Args:
            content: Content to watermark
            source: Source identifier (e.g., "perplexity_comet")
            metadata: Additional metadata to include

        Returns:
            WatermarkResult with signature and merkle root
        """
        start_time = time.time()

        timestamp = datetime.utcnow().isoformat() + "Z"
        full_metadata = {
            "source": source,
            "timestamp": timestamp,
            **(metadata or {}),
        }

        # Create message for signing
        message = json.dumps(
            {
                "content": content,
                "metadata": full_metadata,
            },
            sort_keys=True,
        )

        # Generate signature (simplified - in production use ed25519)
        signature = f"shadowtag:{hashlib.sha256(message.encode()).hexdigest()}"

        # Generate Merkle root
        merkle_root = f"sha256:{hashlib.sha256(f'{content}{timestamp}'.encode()).hexdigest()}"

        latency_ms = (time.time() - start_time) * 1000
        self.watermark_latencies.append(latency_ms)

        return WatermarkResult(
            content=content,
            signature=signature,
            merkle_root=merkle_root,
            timestamp=timestamp,
            metadata=full_metadata,
        )

    async def log_to_manifest(
        self,
        governance_result: GovernanceResult,
        watermark_result: WatermarkResult | None = None,
        context_id: str = "perplexity_comet",
    ) -> str:
        """
        Log transaction to Apertus-compatible JSONL manifest.

        Creates entry for future Elasticsearch indexing with:
        - Full-text searchable content
        - Faceted filtering by context_id
        - Compliance flag indexing

        Args:
            governance_result: Result from governance_score
            watermark_result: Optional watermark result
            context_id: Context identifier for faceting

        Returns:
            Run ID for the logged entry
        """
        run_id = governance_result.request_id
        timestamp = datetime.utcnow().isoformat() + "Z"

        entry = ManifestEntry(
            run_id=run_id,
            timestamp=timestamp,
            context_id=context_id,
            content=watermark_result.content if watermark_result else "",
            decision=governance_result.decision,
            risk_score=governance_result.risk_score,
            watermark_sig=watermark_result.signature if watermark_result else "",
            safety_scores={
                "compliance_flags": governance_result.compliance_flags,
                "risk_score": governance_result.risk_score,
                "decision": governance_result.decision,
            },
            meta={
                "latency_ms": governance_result.latency_ms,
                "reasoning": governance_result.reasoning,
                "merkle_root": watermark_result.merkle_root if watermark_result else "",
                "source": "perplexity_mcp",
            },
        )

        # Write to manifest
        with open(self.manifest_path, "a") as f:
            f.write(json.dumps(asdict(entry)) + "\n")

        return run_id

    def get_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        return {
            "total_governance_calls": len(self.governance_latencies),
            "avg_governance_latency_ms": (
                sum(self.governance_latencies) / len(self.governance_latencies)
                if self.governance_latencies
                else 0
            ),
            "p99_governance_latency_ms": (
                sorted(self.governance_latencies)[int(len(self.governance_latencies) * 0.99)]
                if len(self.governance_latencies) > 100
                else max(self.governance_latencies, default=0)
            ),
            "total_watermarks": len(self.watermark_latencies),
            "manifest_path": str(self.manifest_path),
        }


# MCP Tool Definitions for Claude Code integration
PERPLEXITY_MCP_TOOLS = [
    {
        "name": "perplexity_governance_score",
        "description": "Score a Perplexity Comet browser request for compliance using Judge #6. Returns risk score and decision (APPROVE/DENY/REVIEW).",
        "input_schema": {
            "type": "object",
            "properties": {
                "request_type": {
                    "type": "string",
                    "description": "Type of request: purchase, checkout, query, generate, delete",
                },
                "content": {"type": "string", "description": "The request content or query"},
                "user_region": {"type": "string", "description": "User's region (e.g., EU, US-CA)"},
                "transaction_value": {
                    "type": "number",
                    "description": "Transaction value in USD (optional)",
                },
            },
            "required": ["request_type", "content"],
        },
    },
    {
        "name": "perplexity_watermark",
        "description": "Apply SHADOWTAG cryptographic watermark to AI-generated content for provenance tracking.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Content to watermark"},
                "source": {
                    "type": "string",
                    "description": "Source identifier (e.g., perplexity_comet, perplexity_shopping)",
                },
            },
            "required": ["content", "source"],
        },
    },
    {
        "name": "perplexity_audit_search",
        "description": "Search the Apertus manifest for past governance decisions. For 'Total Recall' audit queries.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'GDPR decisions', 'denied transactions')",
                },
                "context_id": {"type": "string", "description": "Filter by context ID"},
                "decision": {
                    "type": "string",
                    "description": "Filter by decision: APPROVE, DENY, REVIEW",
                },
            },
            "required": ["query"],
        },
    },
]


async def test_perplexity_mcp():
    """Test the Perplexity MCP Server."""
    print("\n=== Perplexity MCP Server Test ===\n")

    server = PerplexityMCPServer()

    # Test 1: Governance scoring for EU purchase
    print("Test 1: EU Shopping Transaction")
    result = await server.governance_score(
        request_type="purchase",
        content="Buy iPhone 15 Pro Max 256GB",
        user_context={"region": "EU", "payment": "PayPal"},
        transaction_value=1199.00,
    )
    print(f"  Decision: {result.decision}")
    print(f"  Risk Score: {result.risk_score}")
    print(f"  Compliance: {result.compliance_flags}")
    print(f"  Latency: {result.latency_ms:.2f}ms")
    print(f"  Reasoning: {result.reasoning}")

    # Test 2: Watermark AI response
    print("\nTest 2: SHADOWTAG Watermarking")
    watermark = await server.watermark_content(
        content="Based on user reviews and specifications, the iPhone 15 Pro Max offers excellent camera performance...",
        source="perplexity_comet",
        metadata={"query": "best phone 2024", "model": "gemini-2.0"},
    )
    print(f"  Signature: {watermark.signature[:50]}...")
    print(f"  Merkle Root: {watermark.merkle_root[:50]}...")

    # Test 3: Log to manifest
    print("\nTest 3: Apertus Manifest Logging")
    run_id = await server.log_to_manifest(result, watermark)
    print(f"  Logged run_id: {run_id}")

    # Test 4: Stats
    print("\nTest 4: Server Stats")
    stats = server.get_stats()
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    asyncio.run(test_perplexity_mcp())
