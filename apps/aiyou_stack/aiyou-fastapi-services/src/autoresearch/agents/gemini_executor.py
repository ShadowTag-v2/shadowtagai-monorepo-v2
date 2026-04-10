"""
Gemini Vehicle Executor for minion
==========================================
Real Gemini API calls per vehicle crew with consensus voting.
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

# Try to import google-generativeai
try:
    import google.generativeai as genai

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed. Using simulation mode.")


class VoteResult(StrEnum):
    """Vote options"""

    APPROVE = "APPROVE"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


@dataclass
class AgentResponse:
    """Response from a single agent"""

    agent_id: str
    response_text: str
    vote: VoteResult
    confidence: float
    reasoning: str
    latency_ms: float
    model: str
    error: str | None = None


@dataclass
class VehicleExecutionResult:
    """Result from executing a vehicle crew"""

    vehicle_id: str
    callsign: str
    decision: VoteResult
    agent_responses: list[AgentResponse]
    unanimous: bool
    approve_count: int
    reject_count: int
    abstain_count: int
    total_latency_ms: float
    model: str
    cost_estimate_usd: float = 0.0


@dataclass
class SquadronExecutionResult:
    """Result from executing entire squadron"""

    opord_id: str
    mission: str
    vehicle_results: list[VehicleExecutionResult]
    squadron_decision: VoteResult
    consensus_achieved: bool
    vehicles_approve: int
    vehicles_reject: int
    vehicles_abstain: int
    total_agents: int
    total_latency_ms: float
    total_cost_usd: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class GeminiVehicleExecutor:
    """
    Execute Gemini API calls per vehicle crew.

    Each agent in a vehicle crew gets the same prompt and task,
    votes independently, and vehicle consensus is determined.
    """

    MODELS = {
        "pro": "gemini-2.5-pro-preview-06-05",
        "flash": "gemini-2.5-flash-preview-05-20",
        "fallback": "gemini-2.0-flash",
    }

    # Cost estimates per 1K tokens (input/output)
    COST_PER_1K = {
        "pro": {"input": 0.00125, "output": 0.005},
        "flash": {"input": 0.000075, "output": 0.0003},
        "fallback": {"input": 0.00001, "output": 0.00004},
    }

    def __init__(self, api_key: str = None):
        self.api_key = (
            api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        )

        if GENAI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Gemini executor running in simulation mode")

        self._rate_limited: dict[str, datetime] = {}

    async def execute_vehicle(
        self,
        vehicle_id: str,
        callsign: str,
        agent_ids: list[str],
        prompt: str,
        task: str,
        tier: str = "flash",
        timeout_per_agent: float = 30.0,
    ) -> VehicleExecutionResult:
        """
        Execute task for all agents in a vehicle, return consensus.

        Args:
            vehicle_id: Vehicle identifier
            callsign: Vehicle callsign (e.g., "IRON-03")
            agent_ids: List of agent IDs in the vehicle
            prompt: Base prompt (from antigravity_system)
            task: User's task
            tier: "pro" or "flash"
            timeout_per_agent: Timeout per agent call

        Returns:
            VehicleExecutionResult with consensus decision
        """
        start_time = datetime.utcnow()
        model = self.MODELS.get(tier, self.MODELS["flash"])

        # Execute all agents in parallel
        agent_tasks = [
            self._execute_agent(agent_id, prompt, task, model, timeout_per_agent)
            for agent_id in agent_ids
        ]

        responses = await asyncio.gather(*agent_tasks, return_exceptions=True)

        # Process responses
        agent_responses = []
        for agent_id, response in zip(agent_ids, responses, strict=False):
            if isinstance(response, Exception):
                agent_responses.append(
                    AgentResponse(
                        agent_id=agent_id,
                        response_text="",
                        vote=VoteResult.ABSTAIN,
                        confidence=0.0,
                        reasoning=f"Error: {str(response)}",
                        latency_ms=0.0,
                        model=model,
                        error=str(response),
                    )
                )
            else:
                agent_responses.append(response)

        # Calculate consensus
        approve_count = sum(1 for r in agent_responses if r.vote == VoteResult.APPROVE)
        reject_count = sum(1 for r in agent_responses if r.vote == VoteResult.REJECT)
        abstain_count = sum(1 for r in agent_responses if r.vote == VoteResult.ABSTAIN)

        # Unanimous = all approve (0% error rate per Kosmos paper)
        unanimous = approve_count == len(agent_responses)
        decision = VoteResult.APPROVE if unanimous else VoteResult.REJECT

        total_latency = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Estimate cost
        cost = self._estimate_cost(
            tier, len(agent_ids), 500, 200
        )  # ~500 input, ~200 output per agent

        return VehicleExecutionResult(
            vehicle_id=vehicle_id,
            callsign=callsign,
            decision=decision,
            agent_responses=agent_responses,
            unanimous=unanimous,
            approve_count=approve_count,
            reject_count=reject_count,
            abstain_count=abstain_count,
            total_latency_ms=total_latency,
            model=model,
            cost_estimate_usd=cost,
        )

    async def _execute_agent(
        self,
        agent_id: str,
        prompt: str,
        task: str,
        model: str,
        timeout: float,
    ) -> AgentResponse:
        """Execute single agent with Gemini API"""
        start_time = datetime.utcnow()

        full_prompt = f"{prompt}\n\nTASK: {task}\n\nAgent {agent_id} analysis and vote:"

        if self.enabled:
            try:
                response_text = await asyncio.wait_for(
                    self._call_gemini(model, full_prompt), timeout=timeout
                )
            except TimeoutError:
                response_text = "ABSTAIN - Timeout exceeded"
            except Exception as e:
                logger.error(f"Gemini call failed for {agent_id}: {e}")
                response_text = f"ABSTAIN - Error: {str(e)}"
        else:
            # Simulation mode
            response_text = await self._simulate_response(agent_id, task)

        latency = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Parse vote from response
        vote, confidence, reasoning = self._parse_response(response_text)

        return AgentResponse(
            agent_id=agent_id,
            response_text=response_text,
            vote=vote,
            confidence=confidence,
            reasoning=reasoning,
            latency_ms=latency,
            model=model,
        )

    async def _call_gemini(self, model: str, prompt: str) -> str:
        """Make actual Gemini API call"""
        try:
            gen_model = genai.GenerativeModel(model)
            response = await asyncio.to_thread(gen_model.generate_content, prompt)
            return response.text
        except Exception:
            # Try fallback model
            if model != self.MODELS["fallback"]:
                logger.warning(f"Falling back from {model} to {self.MODELS['fallback']}")
                return await self._call_gemini(self.MODELS["fallback"], prompt)
            raise

    async def _simulate_response(self, agent_id: str, task: str) -> str:
        """Simulate a response for testing without API calls"""
        await asyncio.sleep(0.01)  # Simulate latency

        # Deterministic but varied responses based on agent ID
        agent_hash = hash(agent_id + task) % 100

        if agent_hash < 70:  # 70% approve
            vote = "APPROVE"
            reasoning = "Task appears well-defined and achievable."
        elif agent_hash < 90:  # 20% reject
            vote = "REJECT"
            reasoning = "Potential issues identified that need clarification."
        else:  # 10% abstain
            vote = "ABSTAIN"
            reasoning = "Insufficient information to make determination."

        return f"""
Analysis: The task "{task[:50]}..." has been reviewed.
Key findings: Standard implementation approach applicable.
VOTE: {vote}
Reason: {reasoning}
"""

    def _parse_response(self, response: str) -> tuple[VoteResult, float, str]:
        """Parse vote from response text"""
        response_upper = response.upper()

        # Find vote
        if "VOTE: APPROVE" in response_upper or "VOTE:APPROVE" in response_upper:
            vote = VoteResult.APPROVE
        elif "VOTE: REJECT" in response_upper or "VOTE:REJECT" in response_upper:
            vote = VoteResult.REJECT
        elif "APPROVE" in response_upper and "REJECT" not in response_upper:
            vote = VoteResult.APPROVE
        elif "REJECT" in response_upper:
            vote = VoteResult.REJECT
        else:
            vote = VoteResult.ABSTAIN

        # Extract reasoning (simple extraction)
        reasoning = ""
        if "REASON:" in response_upper:
            idx = response_upper.find("REASON:")
            reasoning = response[idx + 7 : idx + 200].strip()
        elif "REASONING:" in response_upper:
            idx = response_upper.find("REASONING:")
            reasoning = response[idx + 10 : idx + 200].strip()

        # Confidence based on clarity
        confidence = 0.9 if vote != VoteResult.ABSTAIN else 0.5

        return vote, confidence, reasoning

    def _estimate_cost(
        self, tier: str, num_agents: int, input_tokens: int, output_tokens: int
    ) -> float:
        """Estimate cost for a set of agent calls"""
        costs = self.COST_PER_1K.get(tier, self.COST_PER_1K["flash"])
        input_cost = (input_tokens / 1000) * costs["input"] * num_agents
        output_cost = (output_tokens / 1000) * costs["output"] * num_agents
        return input_cost + output_cost


class SquadronExecutor:
    """
    Execute missions across entire squadron.
    Coordinates vehicle execution and aggregates results.
    """

    def __init__(self, api_key: str = None):
        self.vehicle_executor = GeminiVehicleExecutor(api_key)

    async def execute_mission(
        self,
        opord_id: str,
        mission: str,
        vehicles: list[dict[str, Any]],
        prompts: dict[str, str],
        task: str,
        max_concurrent: int = 20,
    ) -> SquadronExecutionResult:
        """
        Execute mission across all vehicles.

        Args:
            opord_id: OPORD identifier
            mission: Mission statement
            vehicles: List of vehicle dicts with id, callsign, agent_ids, tier
            prompts: Dict of prompts per vehicle (keyed by vehicle_id)
            task: User's task
            max_concurrent: Max concurrent vehicle executions

        Returns:
            SquadronExecutionResult with full results
        """
        start_time = datetime.utcnow()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def execute_with_limit(vehicle: dict) -> VehicleExecutionResult:
            async with semaphore:
                return await self.vehicle_executor.execute_vehicle(
                    vehicle_id=vehicle["vehicle_id"],
                    callsign=vehicle["callsign"],
                    agent_ids=vehicle["agent_ids"],
                    prompt=prompts.get(vehicle["vehicle_id"], prompts.get("default", "")),
                    task=task,
                    tier=vehicle.get("tier", "flash"),
                )

        # Execute all vehicles
        vehicle_results = await asyncio.gather(*[execute_with_limit(v) for v in vehicles])

        # Aggregate results
        vehicles_approve = sum(1 for r in vehicle_results if r.decision == VoteResult.APPROVE)
        vehicles_reject = sum(1 for r in vehicle_results if r.decision == VoteResult.REJECT)
        vehicles_abstain = sum(1 for r in vehicle_results if r.decision == VoteResult.ABSTAIN)

        total_agents = sum(len(r.agent_responses) for r in vehicle_results)
        total_cost = sum(r.cost_estimate_usd for r in vehicle_results)
        total_latency = (datetime.utcnow() - start_time).total_seconds() * 1000

        # Squadron decision: unanimous vehicles required
        consensus_achieved = vehicles_approve == len(vehicle_results)
        squadron_decision = VoteResult.APPROVE if consensus_achieved else VoteResult.REJECT

        return SquadronExecutionResult(
            opord_id=opord_id,
            mission=mission,
            vehicle_results=vehicle_results,
            squadron_decision=squadron_decision,
            consensus_achieved=consensus_achieved,
            vehicles_approve=vehicles_approve,
            vehicles_reject=vehicles_reject,
            vehicles_abstain=vehicles_abstain,
            total_agents=total_agents,
            total_latency_ms=total_latency,
            total_cost_usd=total_cost,
        )
