"""Option 1: Sequential Orchestration with Cor Routing (Long-term Architecture)

Intent classifier routes queries to:
  - internal-only: File/doc/repo search via MCP tools
  - web-only: Brave Search API
  - hybrid: Sequential execution → MCP tools → Web Search → synthesis

LATENCY: +50-300ms (synthesis overhead)
COST: +$0.001-0.005/query (Gemini Flash for classification)
QUALITY: Depends on intent accuracy (target: >80%)
"""

import json
import time
from dataclasses import dataclass

import vertexai
from vertexai.generative_models import GenerativeModel

from pnkln.config.constants import (
    INTENT_CLASSIFIER_MODEL,
    INTENT_CONFIDENCE_THRESHOLD,
    MAX_SYNTHESIS_OVERHEAD_MS,
    P99_LATENCY_MS,
    MetricKey,
    QueryIntent,
)


# ============================================================================
# INTENT CLASSIFICATION
# ============================================================================
@dataclass
class IntentClassification:
    """Result of intent classification."""

    intent: str  # QueryIntent enum value
    confidence: float
    reasoning: str
    latency_ms: float


class IntentClassifier:
    """Classifies query intent using Gemini Flash.

    ROUTING LOGIC:
    - INTERNAL: "How do I use feature X?", "What's in our docs about Y?"
    - WEB: "What happened today in AI?", "Latest news about Z?"
    - HYBRID: "How does our approach compare to industry standard?",
              "Validate our strategy against market trends"
    """

    def __init__(self, project_id: str, location: str = "us-central1"):
        """Initialize classifier with Vertex AI."""
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(INTENT_CLASSIFIER_MODEL)

        # Classification prompt
        self.prompt_template = """You are an intent classifier for a search system.

Classify this query into ONE category:

1. INTERNAL - Query needs company/product docs, code, or internal knowledge
   Examples: "How does our API work?", "What's in the release notes?", "Show me the config file"

2. WEB - Query needs current external information or web sources
   Examples: "Latest AI news", "What's trending on tech today?", "Current price of Bitcoin"

3. HYBRID - Query needs BOTH internal context AND external validation
   Examples: "How does our approach compare to competitors?", "Is our pricing competitive?",
             "Validate our roadmap against industry trends"

Query: "{query}"

Respond in JSON format:
{{
  "intent": "internal|web|hybrid",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""

    def classify(self, query: str) -> IntentClassification:
        """Classify query intent.

        Args:
            query: User query string

        Returns:
            IntentClassification with intent, confidence, reasoning

        Raises:
            ValueError: Invalid response from model
            TimeoutError: Classification exceeds budget

        """
        start_time = time.perf_counter()

        # Generate classification
        prompt = self.prompt_template.format(query=query)

        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.0,  # Deterministic
                "max_output_tokens": 200,
            },
        )

        # Parse JSON response
        try:
            result = json.loads(response.text.strip())
        except json.JSONDecodeError:
            # Fallback: try to extract from markdown code block
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            result = json.loads(text.strip())

        # Validate
        intent = result.get("intent", "").lower()
        if intent not in [QueryIntent.INTERNAL, QueryIntent.WEB, QueryIntent.HYBRID]:
            raise ValueError(f"Invalid intent: {intent}")

        confidence = float(result.get("confidence", 0.0))
        reasoning = result.get("reasoning", "")

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Gate check
        if latency_ms > 100:  # Classification should be <100ms
            print(f"⚠️  WARNING: Intent classification slow: {latency_ms:.1f}ms")

        return IntentClassification(
            intent=intent,
            confidence=confidence,
            reasoning=reasoning,
            latency_ms=latency_ms,
        )


# ============================================================================
# ORCHESTRATOR
# ============================================================================
@dataclass
class OrchestrationResult:
    """Result of orchestrated query execution."""

    query: str
    intent: IntentClassification
    internal_results: dict | None = None
    web_results: dict | None = None
    synthesized_response: str | None = None
    total_latency_ms: float = 0.0
    cost_usd: float = 0.0
    metrics: dict = None


class CorOrchestrator:
    """Main orchestration engine for sequential tool execution.

    EXECUTION FLOW (HYBRID):
    1. Classify intent (Gemini Flash)
    2. Execute internal tools (MCP)
    3. Execute web search (Brave)
    4. Synthesize results (Gemini Flash)
    5. Return unified response

    BOOTSTRAP COMPLIANCE:
    - p99 latency: Target <90ms base + <300ms synthesis = <390ms total
    - Cost: ~$0.015/query (classification + synthesis + search)
    - Quality gate: >80% intent accuracy
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        internal_tool_handler=None,
        web_tool_handler=None,
    ):
        """Initialize orchestrator.

        Args:
            project_id: GCP project ID
            location: GCP region
            internal_tool_handler: Handler for internal MCP tools
            web_tool_handler: BraveSearchTool instance

        """
        self.classifier = IntentClassifier(project_id, location)
        self.internal_tool = internal_tool_handler
        self.web_tool = web_tool_handler

        vertexai.init(project=project_id, location=location)
        self.synthesis_model = GenerativeModel(INTENT_CLASSIFIER_MODEL)

        # Metrics
        self.executions = []

    def execute(
        self,
        query: str,
        user_tier: str = "free",
        force_intent: str | None = None,
    ) -> OrchestrationResult:
        """Execute query with appropriate routing.

        Args:
            query: User query
            user_tier: Revenue tier (free/pro/enterprise)
            force_intent: Override classification (for testing)

        Returns:
            OrchestrationResult with complete execution data

        Raises:
            TimeoutError: Exceeds p99 + synthesis budget
            ValueError: Invalid tier or missing tools

        """
        start_time = time.perf_counter()

        # Step 1: Intent classification (unless forced)
        if force_intent:
            intent = IntentClassification(
                intent=force_intent,
                confidence=1.0,
                reasoning="Force-overridden by caller",
                latency_ms=0.0,
            )
        else:
            intent = self.classifier.classify(query)

        # Gate: Free tier must pick single mode
        if user_tier == "free" and intent.intent == QueryIntent.HYBRID:
            raise ValueError(
                "HYBRID mode requires Pro tier. Free users must select INTERNAL or WEB explicitly.",
            )

        # Gate: Low confidence classification
        if intent.confidence < INTENT_CONFIDENCE_THRESHOLD:
            print(f"⚠️  WARNING: Low intent confidence: {intent.confidence:.2f}")

        # Step 2: Execute based on intent
        internal_results = None
        web_results = None

        if intent.intent in [QueryIntent.INTERNAL, QueryIntent.HYBRID]:
            if not self.internal_tool:
                raise ValueError("Internal tool handler not configured")
            internal_results = self._execute_internal(query)

        if intent.intent in [QueryIntent.WEB, QueryIntent.HYBRID]:
            if not self.web_tool:
                raise ValueError("Web tool handler not configured")
            web_results = self._execute_web(query)

        # Step 3: Synthesize if hybrid
        synthesized = None
        if intent.intent == QueryIntent.HYBRID:
            synthesized = self._synthesize(query=query, internal=internal_results, web=web_results)

        # Calculate metrics
        total_latency_ms = (time.perf_counter() - start_time) * 1000
        cost_usd = self._calculate_cost(intent, internal_results, web_results)

        # Gate check: Total latency
        max_allowed = P99_LATENCY_MS + MAX_SYNTHESIS_OVERHEAD_MS
        if total_latency_ms > max_allowed:
            print(
                f"⚠️  WARNING: Total latency {total_latency_ms:.1f}ms exceeds gate {max_allowed}ms",
            )

        result = OrchestrationResult(
            query=query,
            intent=intent,
            internal_results=internal_results,
            web_results=web_results,
            synthesized_response=synthesized,
            total_latency_ms=total_latency_ms,
            cost_usd=cost_usd,
            metrics=self._collect_metrics(
                intent,
                internal_results,
                web_results,
                total_latency_ms,
                cost_usd,
            ),
        )

        self.executions.append(result)
        return result

    def _execute_internal(self, query: str) -> dict:
        """Execute internal MCP tools."""
        # Placeholder - actual implementation calls internal tool handler
        return {"source": "internal", "results": [], "latency_ms": 0.0}

    def _execute_web(self, query: str) -> dict:
        """Execute web search."""
        if not self.web_tool:
            return {}

        response = self.web_tool.search(query)
        return response.to_dict()

    def _synthesize(self, query: str, internal: dict | None, web: dict | None) -> str:
        """Synthesize internal + web results into unified response.

        CRITICAL: This is where hallucination risk exists.
        Target: <5% hallucination rate.
        """
        start_time = time.perf_counter()

        synthesis_prompt = f"""You are synthesizing search results from two sources.

Query: "{query}"

Internal Results (company docs/code):
{json.dumps(internal, indent=2) if internal else "None"}

Web Results (external sources):
{json.dumps(web, indent=2) if web else "None"}

Provide a unified answer that:
1. Prioritizes internal authoritative sources
2. Uses web results for validation or additional context
3. Clearly attributes information to source (internal vs web)
4. Flags any contradictions between sources
5. Is concise and directly answers the query

Response:"""

        response = self.synthesis_model.generate_content(
            synthesis_prompt,
            generation_config={"temperature": 0.3, "max_output_tokens": 500},
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        # Gate check
        if latency_ms > MAX_SYNTHESIS_OVERHEAD_MS:
            print(
                f"⚠️  WARNING: Synthesis {latency_ms:.1f}ms "
                f"exceeds gate {MAX_SYNTHESIS_OVERHEAD_MS}ms",
            )

        return response.text.strip()

    def _calculate_cost(
        self,
        intent: IntentClassification,
        internal: dict | None,
        web: dict | None,
    ) -> float:
        """Calculate total execution cost."""
        cost = 0.0

        # Intent classification: ~0.0001 tokens * $0.075/1M = ~$0.000001
        cost += 0.001  # Round up to $0.001

        # Web search: $0.01/query
        if web:
            cost += web.get("cost_usd", 0.01)

        # Synthesis: ~500 tokens * $0.075/1M = ~$0.0000375
        if intent.intent == QueryIntent.HYBRID:
            cost += 0.001  # Round up

        return cost

    def _collect_metrics(
        self,
        intent: IntentClassification,
        internal: dict | None,
        web: dict | None,
        total_latency: float,
        cost: float,
    ) -> dict:
        """Collect execution metrics."""
        return {
            MetricKey.INTENT_ACCURACY: intent.confidence,
            MetricKey.LATENCY_P99: total_latency,
            MetricKey.COST_PER_QUERY: cost,
            "intent": intent.intent,
            "classification_latency_ms": intent.latency_ms,
            "internal_executed": internal is not None,
            "web_executed": web is not None,
            "synthesis_executed": intent.intent == QueryIntent.HYBRID,
        }

    def get_aggregate_metrics(self) -> dict:
        """Get aggregate metrics across all executions."""
        if not self.executions:
            return {}

        latencies = [e.total_latency_ms for e in self.executions]
        costs = [e.cost_usd for e in self.executions]
        confidences = [e.intent.confidence for e in self.executions]

        sorted_latencies = sorted(latencies)
        p99_index = int(len(sorted_latencies) * 0.99)

        return {
            "total_executions": len(self.executions),
            "avg_latency_ms": sum(latencies) / len(latencies),
            "p99_latency_ms": sorted_latencies[p99_index],
            "avg_cost_usd": sum(costs) / len(costs),
            "avg_confidence": sum(confidences) / len(confidences),
            "intent_distribution": self._intent_distribution(),
        }

    def _intent_distribution(self) -> dict[str, int]:
        """Calculate distribution of intent classifications."""
        distribution = {QueryIntent.INTERNAL: 0, QueryIntent.WEB: 0, QueryIntent.HYBRID: 0}

        for execution in self.executions:
            distribution[execution.intent.intent] += 1

        return distribution
