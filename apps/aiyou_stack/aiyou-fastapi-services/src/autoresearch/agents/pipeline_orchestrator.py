"""PipelineOrchestrator - Routes tasks to Flying minion, chains Jura evaluations.
Aggregates results from 600 PhD/JD agents for group Jeopardy-style answers.
"""

import json
from dataclasses import dataclass, field
from typing import Any

import redis
from agents.autoresearch import minion

from agents.jura_protocol import JuraProtocol


@dataclass
class TaskResult:
    """Result from a single agent task."""

    agent_id: str
    specialization: str
    result: Any
    confidence: float
    reasoning: str
    passed_jura: bool


@dataclass
class PipelineTask:
    """Task to be distributed to agents."""

    task_id: str
    query: str
    required_specializations: list[str] = field(default_factory=list)
    min_agents: int = 3
    consensus_threshold: float = 0.7  # 70% agreement for group answer
    jura_gate: bool = True  # Require Jura approval


class PipelineOrchestrator:
    """Orchestrates Flying minion swarm for distributed task execution.
    Implements "Call of the Question" methodology - tests first, then execute.
    """

    def __init__(self, redis_host: str = "10.85.19.187", redis_port: int = 6379):
        self.swarm = minion()
        self.jura = JuraProtocol(redis_host=redis_host, redis_port=redis_port)

        # Redis for task queuing
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis.ping()
            self._redis_available = True
        except:
            self.redis = None
            self._redis_available = False

        # Load cursor rules into Jura
        self._load_cursor_stack()

    def _load_cursor_stack(self):
        """Load .cursorrules and activate default commands."""
        self.jura.activate_command("jura")
        self.jura.activate_command("musk-filter")
        self.jura.activate_command("bootstrap")

    def select_agents(self, task: PipelineTask) -> list[str]:
        """Select appropriate agents for task based on specializations."""
        selected = []

        if task.required_specializations:
            # Get agents with matching specializations
            for spec in task.required_specializations:
                spec_agents = self.swarm.get_agents_by_specialization(spec)
                selected.extend([a.agent_id for a in spec_agents[: task.min_agents]])
        else:
            # Default: get top-level strategists
            strategists = self.swarm.get_agents_by_tier("strategy")
            selected = [a.agent_id for a in strategists[: task.min_agents]]

        return selected[: task.min_agents * len(task.required_specializations or [1])]

    def execute_task(self, task: PipelineTask) -> dict[str, Any]:
        """Execute task using selected agents.
        Returns aggregated result with consensus.
        """
        print(f"///▞ PIPELINE :: Task {task.task_id} starting")

        # Step 1: Jura pre-gate (if enabled)
        if task.jura_gate:
            pre_eval = self.jura.inject_context(
                "system",
                "Pre-evaluate this task for safety and feasibility",
            ).evaluate_with_context(task.query)

            if pre_eval.get("verdict") == "DENY":
                return {"status": "blocked", "reason": "Jura pre-gate denied", "details": pre_eval}

        # Step 2: Select agents
        agent_ids = self.select_agents(task)
        if not agent_ids:
            return {"status": "error", "reason": "No agents available"}

        print(f"///▞ PIPELINE :: Selected {len(agent_ids)} agents")

        # Step 3: Distribute to agents (simulated - would be async in production)
        results: list[TaskResult] = []

        for agent_id in agent_ids:
            agent = self.swarm.get_agent(agent_id)
            if not agent:
                continue

            # Simulate agent processing (in production, this would call the LLM)
            result = TaskResult(
                agent_id=agent_id,
                specialization=agent.specialization.value,
                result=f"Agent {agent_id} response to: {task.query[:50]}...",
                confidence=0.85,
                reasoning="Based on doctorate-level analysis",
                passed_jura=True,
            )
            results.append(result)

        # Step 4: Aggregate and find consensus
        consensus = self._find_consensus(results, task.consensus_threshold)

        # Step 5: Jura post-gate (validate consensus)
        if task.jura_gate and consensus:
            post_eval = (
                self.jura.clear_injected()
                .inject_context("system", "Validate this consensus result from agent swarm")
                .evaluate_with_context(json.dumps(consensus))
            )

            consensus["jura_validation"] = post_eval

        # Cache result
        if self._redis_available:
            self.redis.setex(
                f"pipeline:result:{task.task_id}",
                3600,  # 1 hour TTL
                json.dumps(consensus, default=str),
            )

        print(f"///▞ PIPELINE :: Task {task.task_id} complete")
        return consensus

    def _find_consensus(self, results: list[TaskResult], threshold: float) -> dict[str, Any]:
        """Find consensus among agent results."""
        if not results:
            return {"status": "no_results"}

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in results) / len(results)

        # Count passing agents
        passing = [r for r in results if r.passed_jura]
        pass_rate = len(passing) / len(results)

        return {
            "status": "consensus" if pass_rate >= threshold else "no_consensus",
            "agents_queried": len(results),
            "agents_passing": len(passing),
            "pass_rate": round(pass_rate, 2),
            "avg_confidence": round(avg_confidence, 2),
            "results": [
                {
                    "agent_id": r.agent_id,
                    "specialization": r.specialization,
                    "confidence": r.confidence,
                    "passed": r.passed_jura,
                }
                for r in results
            ],
        }

    def chain_tasks(self, tasks: list[PipelineTask]) -> list[dict[str, Any]]:
        """Execute tasks in sequence, passing context between them."""
        results = []

        for i, task in enumerate(tasks):
            # Inject previous result as context
            if i > 0 and results:
                self.jura.inject_context(
                    "assistant",
                    f"Previous task result: {json.dumps(results[-1], default=str)}",
                )

            result = self.execute_task(task)
            results.append(result)

            # Stop on failure if strict mode
            if result.get("status") == "blocked":
                break

        return results

    def parallel_tasks(self, tasks: list[PipelineTask]) -> list[dict[str, Any]]:
        """Execute tasks in parallel (simulated - would use asyncio in production)."""
        return [self.execute_task(task) for task in tasks]

    # === CONVENIENCE METHODS ===

    def ask_swarm(
        self,
        query: str,
        specializations: list[str] = None,
        min_agents: int = 5,
    ) -> dict[str, Any]:
        """Quick method to ask the swarm a question."""
        task = PipelineTask(
            task_id=f"quick_{hash(query) % 10000}",
            query=query,
            required_specializations=specializations or [],
            min_agents=min_agents,
        )
        return self.execute_task(task)

    def code_review(self, code: str) -> dict[str, Any]:
        """Review code using security and testing specialists."""
        return self.ask_swarm(
            f"Review this code for security, correctness, and best practices:\n\n{code}",
            specializations=["SECURITY", "TESTING", "PYTHON"],
            min_agents=3,
        )

    def legal_analysis(self, question: str) -> dict[str, Any]:
        """Legal analysis using agents with JD credentials."""
        task = PipelineTask(
            task_id=f"legal_{hash(question) % 10000}",
            query=f"Provide legal analysis using IRAC methodology:\n\n{question}",
            required_specializations=["SECURITY"],  # Security agents have legal training
            min_agents=5,
            consensus_threshold=0.8,  # Higher bar for legal
        )
        return self.execute_task(task)


if __name__ == "__main__":
    # Test the orchestrator
    orchestrator = PipelineOrchestrator()

    result = orchestrator.ask_swarm(
        "What are the security implications of storing API keys in environment variables?",
        specializations=["SECURITY", "DEVOPS"],
        min_agents=3,
    )

    print(json.dumps(result, indent=2))
