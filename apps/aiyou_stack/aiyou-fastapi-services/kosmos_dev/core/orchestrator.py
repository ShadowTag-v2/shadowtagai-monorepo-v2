"""
ReAct Orchestrator: Reason → Act → Observe cycle for Shadowtag swarm.

Implements Kosmos patterns:
- 200+ agent rollouts per run
- Iterative cycles with linear scaling
- Consensus mechanism with Monte Carlo weighting
- Full traceability of all decisions
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from shadowtag.core.swarm import AgentPersona, SwarmAgent, SwarmManager
from shadowtag.core.whiteboard import (
    ConsensusState,
    Finding,
    Whiteboard,
)


class OrchestratorState(Enum):
    """State of the orchestrator."""

    IDLE = "idle"
    SCANNING = "scanning"
    ANALYZING = "analyzing"
    VOTING = "voting"
    SYNTHESIZING = "synthesizing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class CycleResult:
    """Result of a single ReAct cycle."""

    cycle_number: int
    findings_discovered: int
    votes_cast: int
    consensus_reached: int
    contested_findings: int
    duration_seconds: float
    agent_rollouts: int


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""

    max_cycles: int = 20  # Kosmos default
    max_iterations_per_cycle: int = 50
    consensus_threshold: float = 0.70
    min_votes_for_consensus: int = 3
    timeout_seconds: int = 43200  # 12 hours (Kosmos max)
    target_accuracy: float = 0.794  # Kosmos 79.4% target


class ReActOrchestrator:
    """
    Orchestrates the Shadowtag agent swarm using ReAct pattern.

    Cycle flow:
    1. SCAN: Connectors find files to analyze
    2. REASON: Agents analyze findings on whiteboard
    3. ACT: Agents post new findings, cast votes
    4. OBSERVE: Check consensus, identify contested findings
    5. REPEAT: Until consensus or max cycles

    Implements Kosmos linear scaling: more cycles = more discoveries.
    """

    def __init__(
        self,
        whiteboard: Whiteboard,
        swarm: SwarmManager,
        config: OrchestratorConfig | None = None,
    ):
        self.whiteboard = whiteboard
        self.swarm = swarm
        self.config = config or OrchestratorConfig()

        self.state = OrchestratorState.IDLE
        self.current_cycle = 0
        self.start_time: datetime | None = None
        self.cycle_results: list[CycleResult] = []

        # Callbacks
        self._on_cycle_complete: list[Callable[[CycleResult], None]] = []
        self._on_consensus: list[Callable[[Finding], None]] = []
        self._on_contest: list[Callable[[Finding], None]] = []

    def on_cycle_complete(self, callback: Callable[[CycleResult], None]) -> None:
        """Register callback for cycle completion."""
        self._on_cycle_complete.append(callback)

    def on_consensus(self, callback: Callable[[Finding], None]) -> None:
        """Register callback for consensus reached."""
        self._on_consensus.append(callback)

    def on_contest(self, callback: Callable[[Finding], None]) -> None:
        """Register callback for contested finding."""
        self._on_contest.append(callback)

    async def run(
        self,
        scan_targets: list[str],
        scan_type: str = "memory",  # or "drive"
    ) -> dict[str, Any]:
        """
        Run the full orchestration cycle.

        Args:
            scan_targets: List of paths or folder IDs to scan
            scan_type: "memory" for local files, "drive" for Google Drive

        Returns:
            Final results with all findings and consensus status
        """
        self.state = OrchestratorState.SCANNING
        self.start_time = datetime.utcnow()
        self.current_cycle = 0

        try:
            # Initialize swarm
            agents = self.swarm.spawn_swarm(
                include_board=True,
                include_detectives=True,
            )

            # Run cycles until max or all consensus reached
            while self.current_cycle < self.config.max_cycles:
                self.current_cycle += 1
                self.swarm.increment_cycle()

                cycle_start = datetime.utcnow()

                # Execute cycle
                result = await self._execute_cycle(
                    agents=agents,
                    scan_targets=scan_targets,
                    scan_type=scan_type,
                )

                # Record result
                result.duration_seconds = (datetime.utcnow() - cycle_start).total_seconds()
                self.cycle_results.append(result)

                # Notify callbacks
                for callback in self._on_cycle_complete:
                    await self._safe_callback(callback, result)

                # Check if we can stop early
                pending = self.whiteboard.get_pending_findings()
                contested = self.whiteboard.get_contested_findings()

                if not pending and not contested:
                    # All findings resolved
                    break

                # Check timeout
                elapsed = (datetime.utcnow() - self.start_time).total_seconds()
                if elapsed > self.config.timeout_seconds:
                    break

            self.state = OrchestratorState.COMPLETE

            return self._generate_final_report()

        except Exception as e:
            self.state = OrchestratorState.ERROR
            return {
                "status": "error",
                "error": str(e),
                "cycles_completed": self.current_cycle,
            }

    async def _execute_cycle(
        self,
        agents: list[SwarmAgent],
        scan_targets: list[str],
        scan_type: str,
    ) -> CycleResult:
        """Execute a single ReAct cycle."""

        findings_start = self.whiteboard.total_findings
        votes_start = self.whiteboard.total_votes

        # REASON: Agents analyze current whiteboard state
        self.state = OrchestratorState.ANALYZING

        # Get pending and contested findings for analysis
        to_analyze = (
            self.whiteboard.get_pending_findings() + self.whiteboard.get_contested_findings()
        )

        # ACT: Agents cast votes and post new findings
        self.state = OrchestratorState.VOTING

        vote_tasks = []
        for finding in to_analyze:
            for agent in agents:
                # Skip if agent already voted
                existing_vote = any(v.agent_id == agent.id for v in finding.votes)
                if existing_vote:
                    continue

                # Each agent votes based on their persona
                task = self._agent_vote(agent, finding)
                vote_tasks.append(task)

        # Run votes in parallel (swarm pattern)
        if vote_tasks:
            await asyncio.gather(*vote_tasks, return_exceptions=True)

        # OBSERVE: Check consensus states
        self.state = OrchestratorState.SYNTHESIZING

        # Track consensus changes
        consensus_count = 0
        contest_count = 0

        for finding in self.whiteboard.get_all_findings():
            if finding.consensus == ConsensusState.AGREED:
                consensus_count += 1
                for callback in self._on_consensus:
                    await self._safe_callback(callback, finding)
            elif finding.consensus == ConsensusState.CONTESTED:
                contest_count += 1
                for callback in self._on_contest:
                    await self._safe_callback(callback, finding)

        return CycleResult(
            cycle_number=self.current_cycle,
            findings_discovered=self.whiteboard.total_findings - findings_start,
            votes_cast=self.whiteboard.total_votes - votes_start,
            consensus_reached=consensus_count,
            contested_findings=contest_count,
            duration_seconds=0,  # Set by caller
            agent_rollouts=len(agents),
        )

    async def _agent_vote(
        self,
        agent: SwarmAgent,
        finding: Finding,
    ) -> None:
        """Have an agent vote on a finding."""
        # Simulate agent reasoning (in production, call LLM)
        # For now, use persona-based heuristics

        agrees = True
        confidence = 0.7
        reasoning = f"Analysis from {agent.config.persona.value} perspective"

        # Persona-specific voting logic
        if agent.config.persona == AgentPersona.GENERAL_COUNSEL:
            # Legal is more cautious
            confidence = 0.6
            reasoning = "Legal review: checking compliance implications"

        elif agent.config.persona == AgentPersona.CTO:
            # CTO focuses on technical accuracy
            confidence = 0.8
            reasoning = "Technical verification of detection methodology"

        elif agent.config.persona == AgentPersona.CFO:
            # CFO considers business impact
            confidence = 0.65
            reasoning = "Risk quantification and liability assessment"

        await agent.vote_on_finding(
            finding_id=finding.id,
            agrees=agrees,
            confidence=confidence,
            reasoning=reasoning,
        )

    async def _safe_callback(
        self,
        callback: Callable,
        *args,
    ) -> None:
        """Safely execute a callback."""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception:
            pass  # Don't let callbacks break orchestration

    def _generate_final_report(self) -> dict[str, Any]:
        """Generate final report with all findings and metrics."""
        findings = self.whiteboard.get_all_findings()

        # Categorize findings
        agreed = [f for f in findings if f.consensus == ConsensusState.AGREED]
        contested = [f for f in findings if f.consensus == ConsensusState.CONTESTED]
        pending = [f for f in findings if f.consensus == ConsensusState.PENDING]

        # Calculate accuracy estimate
        avg_confidence = sum(f.weighted_confidence for f in agreed) / len(agreed) if agreed else 0

        # Total duration
        duration = (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0

        return {
            "status": "complete",
            "session_id": self.whiteboard.session_id,
            "summary": {
                "total_cycles": self.current_cycle,
                "total_findings": len(findings),
                "agreed_findings": len(agreed),
                "contested_findings": len(contested),
                "pending_findings": len(pending),
                "total_votes": self.whiteboard.total_votes,
                "avg_confidence": round(avg_confidence, 3),
                "duration_seconds": round(duration, 1),
                "meets_accuracy_target": avg_confidence >= self.config.target_accuracy,
            },
            "findings": {
                "agreed": [f.to_dict() for f in agreed],
                "contested": [f.to_dict() for f in contested],
                "pending": [f.to_dict() for f in pending],
            },
            "cycle_history": [
                {
                    "cycle": r.cycle_number,
                    "findings": r.findings_discovered,
                    "votes": r.votes_cast,
                    "consensus": r.consensus_reached,
                    "contested": r.contested_findings,
                    "duration_s": round(r.duration_seconds, 2),
                    "rollouts": r.agent_rollouts,
                }
                for r in self.cycle_results
            ],
            "swarm_metrics": self.swarm.get_metrics(),
            "whiteboard_summary": self.whiteboard.get_summary(),
        }

    def get_progress(self) -> dict[str, Any]:
        """Get current progress status."""
        return {
            "state": self.state.value,
            "current_cycle": self.current_cycle,
            "max_cycles": self.config.max_cycles,
            "total_findings": self.whiteboard.total_findings,
            "consensus_reached": self.whiteboard.consensus_reached,
            "contested": len(self.whiteboard.get_contested_findings()),
            "pending": len(self.whiteboard.get_pending_findings()),
        }
