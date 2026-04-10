import os
import random
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.autoresearch import AgentUnit, n-autoresearch/Kosmos/BioAgents
from pnkln.core.judge_six_pipeline import JudgeSix


class AntigravitySwarm(n-autoresearch/Kosmos/BioAgents):
    """
    Antigravity implementation of the n-autoresearch/Kosmos/BioAgents swarm.
    Parameters aligned with Antigravity's agentic makeup:
    - Purpose: ShadowTag-v2JR
    - Reason: Doctrine
    - Brakes: Judge6
    """

    def __init__(self):
        # Initialize parent
        super().__init__()

        # Initialize simulation state
        self.running = False
        self.governance_log = []
        self.thread = None

        # Override Judge #6 with Antigravity parameters
        self.judge = JudgeSix(
            caller=self,  # Use self as caller
            mission_statement="ShadowTag-v2JR Enforce Doctrine Optimize for Speed and Quality Maintain 160 IQ Baseline",
            audit_log_path="logs/antigravity_swarm_audit.log",
            purpose_threshold=0.3,  # Adjusted for keyword match demo
            reasons_threshold=0.8,  # Higher standard
            brakes_threshold=0.9,  # Strict safety
        )

        # Clear the default roster and initialize Antigravity roster
        self.units = []
        self._initialize_antigravity_roster()

    def _initialize_antigravity_roster(self):
        # Pillars (SOPs)
        pillars = [
            ("SOP-A", "Upload Triage"),
            ("SOP-B", "Change & Release"),
            ("SOP-C", "Decision Protocol"),
            ("SOP-D", "Code Review"),
        ]

        # Capabilities (Tech Stack & Research)
        capabilities = [
            ("TECH-01", "VertexAI Workbench"),
            ("TECH-02", "MCP Integration"),
            ("TECH-03", "Claude Code Bridge"),
            ("RES-01", "RoT Templates"),
            ("RES-02", "GAIN-RL"),
            ("RES-03", "RLAD Abstractions"),
            ("RES-04", "RLP Dense Rewards"),
            ("RES-05", "Set-RL Entropy"),
            ("RES-06", "ICoT Reasoning"),
        ]

        for pid, role in pillars:
            self.units.append(AgentUnit(id=pid, role=f"Pillar: {role}"))

        for cid, role in capabilities:
            self.units.append(AgentUnit(id=cid, role=f"Capability: {role}"))

    def start(self):
        """Start the swarm simulation loop."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        print("///▞ ANTIGRAVITY SWARM :: STARTED")

    def stop(self):
        """Stop the swarm simulation."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        print("///▞ ANTIGRAVITY SWARM :: STOPPED")

    def get_governance_status(self) -> Dict[str, Any]:
        """Get current status of the swarm governance."""
        active = len([u for u in self.units if u.status != "Idle"])
        approved = len([u for u in self.units if u.status == "Approved"])
        blocked = len([u for u in self.units if u.status == "Blocked"])

        avg_viability = 0
        if approved + blocked > 0:
            total_score = sum(u.viability_score for u in self.units if u.viability_score > 0)
            avg_viability = total_score / (approved + blocked)

        return {
            "active_agents": active,
            "approved_actions": approved,
            "blocked_actions": blocked,
            "avg_viability": round(avg_viability, 2),
            "recent_decisions": self.governance_log[-5:] if self.governance_log else [],
        }

    def _run_loop(self):
        """
        Override the run loop to simulate Antigravity's coding and optimization tasks
        instead of generic economic viability checks.
        """
        while self.running:
            for unit in self.units:
                if not self.running:
                    break

                # 1. Simulate Deep Work & Code Analysis
                unit.status = "Analyzing"
                unit.current_task = f"Executing {unit.role} protocols..."
                time.sleep(random.uniform(0.1, 0.3))  # Fast simulation (Antigravity speed)

                # 2. Generate Recommendation based on Antigravity Doctrine
                actions = ["Refactor", "Optimize", "Secure", "Document", "Test", "Deploy"]
                action = random.choice(actions)

                # Context specific to the role
                if "Pillar" in unit.role:
                    context = "SOP Compliance Check - Enforce Doctrine and Quality"
                else:
                    context = "Research Delta Application - Optimize Speed and Maintain IQ"

                unit.recommendation = f"{action} {unit.role} ({context})"

                # 3. Judge Validation (Doctrine Focus)
                fn_name = f"perform_{action.lower()}"
                fn_args = {
                    "domain": unit.role,
                    "complexity_score": random.randint(1, 10),
                    "doctrine_alignment": f"Aligned with {unit.role}",
                    "iq_score": 160,  # Baseline IQ
                }

                # Use Judge's internal validation logic
                try:
                    validation = self.judge._validate(fn_name, fn_args, context=context)

                    unit.judge_decision = str(validation.result).replace("ValidationResult.", "")
                    if unit.judge_decision == "APPROVED":
                        unit.viability_score = int(validation.purpose_score * 100)
                        unit.status = "Approved"
                    else:
                        unit.viability_score = int(validation.purpose_score * 100)
                        unit.status = "Blocked"

                    # Log decision
                    self.governance_log.append(
                        {
                            "timestamp": time.time(),
                            "agent": unit.role,
                            "proposal": unit.recommendation,
                            "decision": unit.judge_decision,
                            "score": unit.viability_score,
                            "context": context,
                        }
                    )

                except Exception:
                    # print(f"Judge Error: {e}")
                    unit.status = "Error"

            time.sleep(1.5)  # Wait before next cycle


if __name__ == "__main__":
    print("///▞ ANTIGRAVITY SWARM :: INITIALIZING")
    print("///▞ PARAMETERS :: Purpose=ShadowTag-v2JR • Reason=Doctrine • Brakes=Judge6")

    swarm = AntigravitySwarm()
    swarm.start()

    try:
        # Run for a few cycles to demonstrate
        for i in range(5):
            time.sleep(2)
            status = swarm.get_governance_status()
            print(f"\n///▞ STATUS CYCLE {i + 1}")
            print(f"Active Agents: {status['active_agents']}")
            print(f"Approved Actions: {status['approved_actions']}")
            print(f"Blocked Actions: {status['blocked_actions']}")
            print(f"Avg Viability: {status['avg_viability']}")

            if status["recent_decisions"]:
                last_decision = status["recent_decisions"][-1]
                print(
                    f"Latest Decision: {last_decision['agent']} -> {last_decision['decision']} ({last_decision['proposal']})"
                )

    except KeyboardInterrupt:
        print("\nStopping swarm...")
    finally:
        swarm.stop()
        print("///▞ ANTIGRAVITY SWARM :: TERMINATED")
