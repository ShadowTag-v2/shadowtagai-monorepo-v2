"""
UnGPT Atomic Thread Orchestrator
Implements AoT (Atom of Thoughts) with AunCRM compliance integration
"""

import asyncio
import json
import os

# Import AunCRM for compliance
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from aunccrm import Brake, ComplianceContext, Purpose, Reason, RiskLevel


@dataclass
class AtomicThread:
    """
    Single atomic reasoning unit with isolated context and AunCRM compliance
    Failure in one thread does not cascade to others (ATP 5-19 risk isolation)
    """

    thread_id: str

    # AunCRM integration
    purpose: str  # What is this thread solving?
    reasons: list[str]  # Why is this approach valid?
    brakes: list[str]  # What constraints must be enforced?
    risk_level: RiskLevel

    # Execution context
    prompt: str
    agent_type: str
    dependencies: list[str] = field(default_factory=list)

    # Results
    result: dict[str, Any] | None = None
    error: Exception | None = None
    execution_time: float = 0.0
    token_usage: dict[str, int] = field(default_factory=dict)

    # Compliance tracking
    compliance_context: ComplianceContext | None = None

    def get_audit_trail(self) -> dict[str, Any]:
        """Generate audit trail for AunCRM compliance"""
        return {
            "thread_id": self.thread_id,
            "purpose": self.purpose,
            "reasons": self.reasons,
            "brakes": self.brakes,
            "risk_level": self.risk_level.value,
            "execution_time": self.execution_time,
            "token_usage": self.token_usage,
            "success": self.error is None,
            "error": str(self.error) if self.error else None,
            "timestamp": datetime.utcnow().isoformat(),
            "compliance_validated": self.compliance_context is not None,
        }

    def create_compliance_context(self) -> ComplianceContext:
        """Create AunCRM compliance context from thread"""
        purpose_obj = Purpose(
            description=self.purpose,
            business_value="Atomic reasoning component for research automation",
            success_criteria=[
                "Thread executes without errors",
                "Results are coherent and evidence-based",
                "Execution time within acceptable bounds",
            ],
        )

        reason_objs = [
            Reason(
                justification=reason,
                evidence=["Thread decomposition analysis"],
                assumptions=["Input query is well-formed", "LLM is available"],
                confidence_score=0.80,
            )
            for reason in self.reasons
        ]

        brake_objs = [
            Brake(
                constraint=brake, enforcement_method="runtime_check", violation_action="halt_thread"
            )
            for brake in self.brakes
        ]

        # Add default brakes
        brake_objs.append(
            Brake(
                constraint="Maximum execution time: 60 seconds",
                threshold=60.0,
                enforcement_method="timeout",
                violation_action="halt_thread",
            )
        )

        context = ComplianceContext(
            context_id=self.thread_id,
            purpose=purpose_obj,
            reasons=reason_objs,
            brakes=brake_objs,
            risk_level=self.risk_level,
        )

        self.compliance_context = context
        return context


@dataclass
class DecompositionResult:
    """Result from query decomposition phase"""

    threads: list[AtomicThread]
    dependency_graph: dict[str, list[str]]
    estimated_cost: float
    risk_assessment: dict[str, Any]
    compliance_validated: bool = False


class PNKLNAtomicOrchestrator:
    """
    Main orchestrator for atomic thread execution
    Integrates JR (Judgment Rule) + Cor (unified synthesis) + NS (execution)
    """

    def __init__(
        self,
        model_client: Any,  # Can be any LLM client (Anthropic, OpenAI, etc.)
        model_name: str = "claude-sonnet-4-20250514",
        max_concurrent_threads: int = 5,
        enable_compliance: bool = True,
    ):
        self.model_client = model_client
        self.model_name = model_name
        self.max_concurrent = max_concurrent_threads
        self.enable_compliance = enable_compliance

    async def decompose_query(
        self, query: str, max_threads: int = 10, risk_threshold: RiskLevel = RiskLevel.RA_3
    ) -> DecompositionResult:
        """
        JR (Judgment Rule) decomposition: Break query into atomic threads
        Each thread gets Purpose, Reasons, Brakes per AunCRM doctrine
        """

        decomposition_prompt = f"""You are a military-grade reasoning system (AunCRM Judge).
Decompose this query into atomic, parallelizable reasoning threads.

QUERY: {query}

For each thread, provide:
1. PURPOSE: What specific sub-problem does this thread solve?
2. REASONS: Why is this decomposition valid? What assumptions hold?
3. BRAKES: What constraints/limits must this thread respect?
4. RISK_LEVEL: RA-1 (routine), RA-2 (low), RA-3 (moderate), RA-4 (high)
5. DEPENDENCIES: Which other threads must complete first? (use thread_ids)

Return JSON array with max {max_threads} threads:
[
  {{
    "thread_id": "T001_market_analysis",
    "purpose": "Analyze target market size and competition",
    "reasons": ["Independent of tech stack decisions", "Can use public data sources"],
    "brakes": ["Must cite sources", "No speculation on private company data"],
    "risk_level": "RA-2",
    "agent_type": "analyst",
    "dependencies": [],
    "prompt": "Detailed prompt for this specific thread..."
  }}
]

CRITICAL: Threads must be truly independent (minimal dependencies) for parallel execution.
Each thread's prompt should be self-contained with all necessary context.
"""

        response = await self._call_model(decomposition_prompt)

        # Parse JSON response
        threads_data = self._extract_json(response)

        # Convert to AtomicThread objects
        threads = []
        for td in threads_data:
            thread = AtomicThread(
                thread_id=td["thread_id"],
                purpose=td["purpose"],
                reasons=td["reasons"],
                brakes=td["brakes"],
                risk_level=RiskLevel[td["risk_level"].replace("-", "_")],
                prompt=td["prompt"],
                agent_type=td["agent_type"],
                dependencies=td.get("dependencies", []),
            )

            # Create compliance context if enabled
            if self.enable_compliance:
                thread.create_compliance_context()

            threads.append(thread)

        # Build dependency graph
        dep_graph = {t.thread_id: t.dependencies for t in threads}

        # Risk assessment
        risk_counts = {}
        for t in threads:
            risk_counts[t.risk_level.value] = risk_counts.get(t.risk_level.value, 0) + 1

        # Estimate cost (conservative: 2000 tokens per thread)
        estimated_tokens_per_thread = 2000
        # Assuming $0.003/1K input + $0.015/1K output for Claude Sonnet
        estimated_cost = len(threads) * estimated_tokens_per_thread * (0.003 + 0.015) / 1000

        return DecompositionResult(
            threads=threads,
            dependency_graph=dep_graph,
            estimated_cost=estimated_cost,
            risk_assessment={
                "total_threads": len(threads),
                "risk_distribution": risk_counts,
                "has_high_risk": any(t.risk_level == RiskLevel.RA_4 for t in threads),
            },
            compliance_validated=self.enable_compliance,
        )

    async def execute_thread(self, thread: AtomicThread) -> AtomicThread:
        """
        Execute single atomic thread with error isolation
        Failures are contained and logged, not propagated
        """
        start_time = time.time()

        try:
            # Wrap prompt with AunCRM enforcement
            enforced_prompt = f"""[AunCRM CONSTRAINTS]
PURPOSE: {thread.purpose}
BRAKES: {", ".join(thread.brakes)}

[TASK]
{thread.prompt}

[ENFORCEMENT]
You MUST respect the brakes listed above. Violations will fail this thread.
Provide your response in structured format with clear reasoning.
"""

            # Execute with timeout
            response = await asyncio.wait_for(self._call_model(enforced_prompt), timeout=60.0)

            thread.result = {
                "content": response,
                "thread_id": thread.thread_id,
                "purpose": thread.purpose,
            }

            # Track token usage (simplified)
            thread.token_usage = {
                "estimated_tokens": len(enforced_prompt.split()) + len(response.split())
            }

        except TimeoutError:
            thread.error = Exception(f"Thread {thread.thread_id} exceeded 60s timeout")
        except Exception as e:
            thread.error = e
        finally:
            thread.execution_time = time.time() - start_time

        return thread

    async def execute_threads_concurrent(self, threads: list[AtomicThread]) -> list[AtomicThread]:
        """
        Execute threads concurrently respecting dependency graph
        Implements topological execution order
        """

        executed = set()
        results = []

        while len(executed) < len(threads):
            # Find threads ready to execute (dependencies met)
            ready = [
                t
                for t in threads
                if t.thread_id not in executed and all(dep in executed for dep in t.dependencies)
            ]

            if not ready:
                # Circular dependency or all remaining have errors
                break

            # Execute ready threads concurrently
            batch_results = await asyncio.gather(
                *[self.execute_thread(t) for t in ready], return_exceptions=True
            )

            for thread_result in batch_results:
                if isinstance(thread_result, Exception):
                    print(f"Thread execution failed: {thread_result}")
                else:
                    results.append(thread_result)
                    executed.add(thread_result.thread_id)

        return results

    async def stitch_results(
        self,
        original_query: str,
        threads: list[AtomicThread],
        output_format: str = "markdown_report",
    ) -> dict[str, Any]:
        """
        Cor (unified brain): Stitch thread results into coherent output
        Maintains audit trail for AunCRM compliance
        """

        # Separate successful and failed threads
        successful = [t for t in threads if t.error is None]
        failed = [t for t in threads if t.error is not None]

        # Build stitching context
        thread_results_text = "\n\n".join(
            [
                f"## Thread: {t.thread_id}\n**Purpose:** {t.purpose}\n**Result:**\n{t.result['content']}"
                for t in successful
            ]
        )

        stitching_prompt = f"""You are Cor, the unified execution brain of the PNKLN system.

ORIGINAL QUERY: {original_query}

You have received results from {len(successful)} atomic reasoning threads.
Your task is to synthesize these into a coherent, comprehensive response.

THREAD RESULTS:
{thread_results_text}

{"FAILED THREADS (handle gracefully):" if failed else ""}
{chr(10).join([f"- {t.thread_id}: {t.error}" for t in failed]) if failed else ""}

STITCHING REQUIREMENTS:
1. Maintain logical flow and coherence
2. Resolve any contradictions between threads
3. Highlight gaps from failed threads (if any)
4. Output format: {output_format}
5. Preserve key insights from each thread
6. Add executive summary at top

Generate the final synthesized response now.
"""

        final_output = await self._call_model(stitching_prompt)

        # Generate audit trail
        audit_trail = {
            "original_query": original_query,
            "total_threads": len(threads),
            "successful_threads": len(successful),
            "failed_threads": len(failed),
            "thread_details": [t.get_audit_trail() for t in threads],
            "total_execution_time": sum(t.execution_time for t in threads),
            "stitching_timestamp": datetime.utcnow().isoformat(),
        }

        return {
            "final_output": final_output,
            "audit_trail": audit_trail,
            "thread_results": [t.result for t in successful if t.result],
            "execution_summary": {
                "success_rate": len(successful) / len(threads) if threads else 0,
                "avg_execution_time": sum(t.execution_time for t in threads) / len(threads)
                if threads
                else 0,
                "risk_profile": {
                    level.value: len([t for t in threads if t.risk_level == level])
                    for level in RiskLevel
                },
            },
        }

    async def process_query(
        self, query: str, max_threads: int = 10, output_format: str = "markdown_report"
    ) -> dict[str, Any]:
        """
        Full AoT pipeline with AunCRM enforcement
        Decompose → Execute → Stitch
        """

        print("[JR] Decomposing query into atomic threads...")
        decomp_result = await self.decompose_query(query, max_threads)

        print(f"[JR] Decomposed into {len(decomp_result.threads)} threads")
        print(f"[JR] Risk Assessment: {decomp_result.risk_assessment}")
        print(f"[JR] Estimated Cost: ${decomp_result.estimated_cost:.4f}")

        # Gate check: Abort if cost too high
        if decomp_result.estimated_cost > 1.0:  # $1 threshold
            raise ValueError(
                f"Estimated cost ${decomp_result.estimated_cost:.2f} exceeds gate threshold"
            )

        print(f"\n[NS] Executing {len(decomp_result.threads)} threads concurrently...")
        executed_threads = await self.execute_threads_concurrent(decomp_result.threads)

        print(f"[NS] Completed {len(executed_threads)} threads")
        success_count = len([t for t in executed_threads if t.error is None])
        print(f"[NS] Success Rate: {success_count}/{len(executed_threads)}")

        print("\n[Cor] Stitching results into unified output...")
        final_result = await self.stitch_results(query, executed_threads, output_format)

        print(
            f"[Cor] Stitching complete. Total execution time: {final_result['audit_trail']['total_execution_time']:.2f}s"
        )

        return final_result

    # Helper methods

    async def _call_model(self, prompt: str) -> str:
        """
        Abstract model calling - override based on your LLM provider
        This is a placeholder that should be replaced with actual API calls
        """
        # This will be overridden by specific implementations
        raise NotImplementedError("Model client must implement _call_model method")

    def _extract_json(self, text: str) -> list[dict[str, Any]]:
        """Extract JSON from model response"""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        return json.loads(text.strip())
