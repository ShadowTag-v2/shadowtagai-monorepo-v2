"""Antigravity Swarm - Judge 6 Governed Agent Orchestration

Purpose: ShadowTag-v2JR doctrine enforcement
Reason: SOP compliance + research delta application
Brakes: Judge 6 validation (p99 ≤90ms target)
"""

from __future__ import annotations

import logging
import random
import sys
import threading
import time
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Final

# Proper package resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.autoresearch import AgentUnit, minion  # noqa: E402
from pnkln.core.judge_six_pipeline import JudgeSix  # noqa: E402

if TYPE_CHECKING:
    from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────


class Threshold:
    """Judge 6 validation thresholds."""

    PURPOSE: Final[float] = 0.3  # Keyword match baseline
    REASONS: Final[float] = 0.8  # Doctrine alignment
    BRAKES: Final[float] = 0.9  # Safety gate (strict)


class Timing:
    """Cycle timing parameters (seconds)."""

    TASK_MIN: Final[float] = 0.1
    TASK_MAX: Final[float] = 0.3
    CYCLE_INTERVAL: Final[float] = 1.5
    DEMO_INTERVAL: Final[float] = 2.0


IQ_BASELINE: Final[int] = 160
AUDIT_LOG_PATH: Final[str] = "logs/antigravity_swarm_audit.log"
MISSION: Final[str] = "ShadowTag-v2JR Enforce Doctrine Optimize for Speed and Quality"


class Action(Enum):
    """Valid swarm actions."""

    REFACTOR = auto()
    OPTIMIZE = auto()
    SECURE = auto()
    DOCUMENT = auto()
    TEST = auto()
    DEPLOY = auto()


@dataclass(frozen=True)
class SwarmConfig:
    """Immutable swarm configuration."""

    purpose_threshold: float = Threshold.PURPOSE
    reasons_threshold: float = Threshold.REASONS
    brakes_threshold: float = Threshold.BRAKES
    audit_log_path: str = AUDIT_LOG_PATH
    mission: str = MISSION


# ─────────────────────────────────────────────────────────────────────────────
# Roster Definitions
# ─────────────────────────────────────────────────────────────────────────────

PILLARS: Final[tuple[tuple[str, str], ...]] = (
    ("SOP-A", "Upload Triage"),
    ("SOP-B", "Change & Release"),
    ("SOP-C", "Decision Protocol"),
    ("SOP-D", "Code Review"),
)

CAPABILITIES: Final[tuple[tuple[str, str], ...]] = (
    ("TECH-01", "VertexAI Workbench"),
    ("TECH-02", "MCP Integration"),
    ("TECH-03", "Claude Code Bridge"),
    ("RES-01", "RoT Templates"),
    ("RES-02", "GAIN-RL"),
    ("RES-03", "RLAD Abstractions"),
    ("RES-04", "RLP Dense Rewards"),
    ("RES-05", "Set-RL Entropy"),
    ("RES-06", "ICoT Reasoning"),
)


# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Swarm Implementation
# ─────────────────────────────────────────────────────────────────────────────


class AntigravitySwarm(minion):
    """Judge 6 governed agent swarm.

    Extends minion with Antigravity doctrine:
    - Purpose: ShadowTag-v2JR mission alignment
    - Reason: SOP + research delta compliance
    - Brakes: Strict safety validation
    """

    def __init__(self, config: SwarmConfig | None = None) -> None:
        super().__init__()
        self.config = config or SwarmConfig()
        self._lock = threading.RLock()

        self.judge = JudgeSix(
            caller=self.orchestrator,
            mission_statement=self.config.mission,
            audit_log_path=self.config.audit_log_path,
            purpose_threshold=self.config.purpose_threshold,
            reasons_threshold=self.config.reasons_threshold,
            brakes_threshold=self.config.brakes_threshold,
        )

        self.units: list[AgentUnit] = []
        self._init_roster()

    def _init_roster(self) -> None:
        """Initialize agent roster from pillars and capabilities."""
        for unit_id, role in PILLARS:
            self.units.append(AgentUnit(id=unit_id, role=f"Pillar: {role}"))

        for unit_id, role in CAPABILITIES:
            self.units.append(AgentUnit(id=unit_id, role=f"Capability: {role}"))

        logger.info("Roster initialized: %d agents", len(self.units))

    def _get_context(self, unit: AgentUnit) -> str:
        """Generate context string for validation."""
        if "Pillar" in unit.role:
            return "SOP Compliance Check - Enforce Doctrine and Quality"
        return "Research Delta Application - Optimize Speed and Maintain IQ"

    def _process_unit(self, unit: AgentUnit) -> None:
        """Execute single unit processing cycle."""
        # Phase 1: Analysis
        unit.status = "Analyzing"
        unit.current_task = f"Executing {unit.role} protocols..."
        time.sleep(random.uniform(Timing.TASK_MIN, Timing.TASK_MAX))

        # Phase 2: Action selection
        action = random.choice(list(Action))
        context = self._get_context(unit)
        unit.recommendation = f"{action.name.title()} {unit.role} ({context})"

        # Phase 3: Judge validation
        fn_name = f"perform_{action.name.lower()}"
        fn_args = {
            "domain": unit.role,
            "complexity_score": random.randint(1, 10),
            "doctrine_alignment": f"Aligned with {unit.role}",
            "iq_score": IQ_BASELINE,
        }

        self._validate_and_log(unit, fn_name, fn_args, context)

    def _validate_and_log(
        self,
        unit: AgentUnit,
        fn_name: str,
        fn_args: dict[str, Any],
        context: str,
    ) -> None:
        """Run Judge 6 validation and record decision."""
        try:
            # Try public API first, fallback to private if needed
            if hasattr(self.judge, "validate"):
                validation = self.judge.validate(fn_name, fn_args, context=context)
            else:
                validation = self.judge._validate(fn_name, fn_args, context=context)

            decision = (
                validation.result.name
                if hasattr(validation.result, "name")
                else str(validation.result).replace("ValidationResult.", "")
            )
            score = int(validation.purpose_score * 100)

            unit.judge_decision = decision
            unit.viability_score = score
            unit.status = "Approved" if decision == "APPROVED" else "Blocked"

            with self._lock:
                self.governance_log.append(
                    {
                        "timestamp": time.time(),
                        "agent": unit.role,
                        "proposal": unit.recommendation,
                        "decision": decision,
                        "score": score,
                        "context": context,
                    },
                )

        except AttributeError as e:
            logger.error("Judge interface mismatch: %s", e)
            unit.status = "Error"
        except (ValueError, TypeError) as e:
            logger.error("Validation input error for %s: %s", unit.id, e)
            unit.status = "Error"

    def _run_loop(self) -> None:
        """Main execution loop - processes all units per cycle."""
        while self.running:
            for unit in self.units:
                if not self.running:
                    return
                self._process_unit(unit)
            time.sleep(Timing.CYCLE_INTERVAL)


# ─────────────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────────────


def main(cycles: int = 5) -> None:
    """Run swarm demonstration."""
    logger.info("///▞ ANTIGRAVITY SWARM :: INITIALIZING")
    logger.info("///▞ Purpose=ShadowTag-v2JR • Reason=Doctrine • Brakes=Judge6")

    swarm = AntigravitySwarm()
    swarm.start()

    try:
        for i in range(1, cycles + 1):
            time.sleep(Timing.DEMO_INTERVAL)
            status = swarm.get_governance_status()

            logger.info("─" * 50)
            logger.info("CYCLE %d/%d", i, cycles)
            logger.info(
                "  Active: %d | Approved: %d | Blocked: %d | Avg: %.1f%%",
                status["active_agents"],
                status["approved_actions"],
                status["blocked_actions"],
                status["avg_viability"],
            )

            if status["recent_decisions"]:
                last = status["recent_decisions"][-1]
                logger.info("  Latest: %s → %s", last["agent"], last["decision"])

    except KeyboardInterrupt:
        logger.info("Interrupt received")
    finally:
        swarm.stop()
        logger.info("///▞ ANTIGRAVITY SWARM :: TERMINATED")


if __name__ == "__main__":
    main()
