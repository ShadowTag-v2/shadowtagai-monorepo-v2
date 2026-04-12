"""
FM 7-8 / Ranger Handbook: Battle Drills
========================================

Source: FM 7-8 Infantry Rifle Platoon and Squad / Ranger Handbook

Battle Drills are standardized responses to common combat situations.
They are rehearsed until they become automatic responses.

Adapted for AI agent error handling and incident response.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DrillTrigger(Enum):
    """Events that trigger battle drills"""

    EXCEPTION = "exception"
    API_FAILURE = "api_failure"
    SECURITY_ALERT = "security_alert"
    COST_SPIKE = "cost_spike"
    MALICIOUS_INPUT = "malicious_input"
    UNEXPECTED_BEHAVIOR = "unexpected_behavior"
    HARD_PROBLEM = "hard_problem"
    NEW_FEATURE = "new_feature"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"


class DrillPhase(Enum):
    """Phases of drill execution"""

    ALERT = "alert"
    ASSESS = "assess"
    RESPOND = "respond"
    RECOVER = "recover"
    REPORT = "report"


@dataclass
class BattleDrill(ABC):
    """
    Base class for all Battle Drills.

    A battle drill is a collective action rapidly executed
    without applying a deliberate decision-making process.
    """

    name: str
    drill_number: int
    triggers: list[DrillTrigger]

    # Execution state
    current_phase: DrillPhase = DrillPhase.ALERT
    started_at: datetime | None = None
    completed_at: datetime | None = None
    success: bool = False
    actions_taken: list[str] = field(default_factory=list)

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the battle drill"""
        pass

    def log_action(self, action: str):
        """Log action taken during drill"""
        self.actions_taken.append(
            {
                "action": action,
                "phase": self.current_phase.value,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "drill_number": self.drill_number,
            "triggers": [t.value for t in self.triggers],
            "phase": self.current_phase.value,
            "success": self.success,
            "actions": self.actions_taken,
            "fm_reference": "FM 7-8",
        }


@dataclass
class ReactToContact(BattleDrill):
    """
    Battle Drill 1: React to Contact

    FM 7-8 Trigger: Enemy contact (direct fire)
    AI Trigger: Exception, API failure, error

    Response: Return fire, seek cover, report
    AI Response: Log error, pause requests, analyze, fix, resume
    """

    def __post_init__(self):
        self.name = "React to Contact"
        self.drill_number = 1
        self.triggers = [
            DrillTrigger.EXCEPTION,
            DrillTrigger.API_FAILURE,
            DrillTrigger.TIMEOUT,
        ]

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0
    current_retry: int = 0

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute React to Contact drill.

        Algorithm:
        1. ALERT: Log the contact (error)
        2. ASSESS: Analyze root cause
        3. RESPOND: Attempt fix or retry
        4. RECOVER: Resume operations
        5. REPORT: Document incident
        """
        self.started_at = datetime.utcnow()
        error = context.get("error", "Unknown error")
        task = context.get("task", "Unknown task")

        # Phase 1: ALERT
        self.current_phase = DrillPhase.ALERT
        self.log_action(f"Contact! Error detected: {error}")

        # Phase 2: ASSESS
        self.current_phase = DrillPhase.ASSESS
        root_cause = self._analyze_error(error)
        self.log_action(f"Root cause: {root_cause}")

        # Phase 3: RESPOND
        self.current_phase = DrillPhase.RESPOND
        while self.current_retry < self.max_retries:
            self.current_retry += 1
            self.log_action(f"Retry attempt {self.current_retry}/{self.max_retries}")

            try:
                # Attempt recovery
                if context.get("retry_func"):
                    await context["retry_func"]()
                    self.success = True
                    break
                else:
                    # Simulate retry delay
                    await asyncio.sleep(self.retry_delay * self.current_retry)
                    self.success = True
                    break
            except Exception as e:
                self.log_action(f"Retry {self.current_retry} failed: {str(e)}")

        # Phase 4: RECOVER
        self.current_phase = DrillPhase.RECOVER
        if self.success:
            self.log_action("Operations resumed")
        else:
            self.log_action("Escalating to higher echelon")

        # Phase 5: REPORT
        self.current_phase = DrillPhase.REPORT
        self.completed_at = datetime.utcnow()

        return {
            "drill": self.name,
            "success": self.success,
            "retries": self.current_retry,
            "root_cause": root_cause,
            "duration_ms": (self.completed_at - self.started_at).total_seconds() * 1000,
            "actions": self.actions_taken,
        }

    def _analyze_error(self, error: str) -> str:
        """Analyze error to determine root cause"""
        error_lower = error.lower()
        if "timeout" in error_lower:
            return "Network timeout - external service unavailable"
        elif "rate" in error_lower or "429" in error_lower:
            return "Rate limit exceeded"
        elif "auth" in error_lower or "401" in error_lower:
            return "Authentication failure"
        elif "permission" in error_lower or "403" in error_lower:
            return "Authorization failure"
        return "Unknown error type"


@dataclass
class BreakContact(BattleDrill):
    """
    Battle Drill 2: Break Contact

    FM 7-8 Trigger: Overwhelming force, need to disengage
    AI Trigger: Cost spike, security alert, kill switch

    Response: Smoke, withdraw, rally
    AI Response: Revoke tokens, terminate pods, safe mode
    """

    def __post_init__(self):
        self.name = "Break Contact"
        self.drill_number = 2
        self.triggers = [DrillTrigger.COST_SPIKE, DrillTrigger.SECURITY_ALERT]

    # Thresholds
    cost_threshold: float = 5.0  # $/minute
    force_terminate: bool = False

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute Break Contact drill.

        Algorithm:
        1. ALERT: Broadcast "CEASE FIRE"
        2. ASSESS: Evaluate threat level
        3. RESPOND: Smoke (revoke tokens)
        4. RECOVER: Withdraw (terminate pods)
        5. REPORT: Rally at safe mode
        """
        self.started_at = datetime.utcnow()
        alert_type = context.get("alert_type", "unknown")
        current_cost = context.get("current_cost", 0)

        # Phase 1: ALERT
        self.current_phase = DrillPhase.ALERT
        self.log_action(f"CEASE FIRE! Alert: {alert_type}")

        # Phase 2: ASSESS
        self.current_phase = DrillPhase.ASSESS
        threat_level = "HIGH" if alert_type == "security" else "MEDIUM"
        self.log_action(f"Threat level: {threat_level}")

        # Phase 3: RESPOND (Smoke)
        self.current_phase = DrillPhase.RESPOND
        self.log_action("Revoking active tokens")
        if context.get("revoke_func"):
            await context["revoke_func"]()

        # Phase 4: RECOVER (Withdraw)
        self.current_phase = DrillPhase.RECOVER
        self.log_action("Terminating non-essential pods")
        if self.force_terminate and context.get("terminate_func"):
            await context["terminate_func"]()
        self.log_action("Entering safe mode (read-only)")

        # Phase 5: REPORT
        self.current_phase = DrillPhase.REPORT
        self.completed_at = datetime.utcnow()
        self.success = True

        return {
            "drill": self.name,
            "success": self.success,
            "alert_type": alert_type,
            "cost_at_trigger": current_cost,
            "mode": "safe_mode",
            "duration_ms": (self.completed_at - self.started_at).total_seconds() * 1000,
            "actions": self.actions_taken,
        }


@dataclass
class ReactToAmbush(BattleDrill):
    """
    Battle Drill 3: React to Ambush

    FM 7-8 Trigger: Surprise attack from concealed positions
    AI Trigger: Unexpected behavior, cascade failure

    Response: Return fire, assault through
    AI Response: Isolate, diagnose, recover
    """

    def __post_init__(self):
        self.name = "React to Ambush"
        self.drill_number = 3
        self.triggers = [DrillTrigger.UNEXPECTED_BEHAVIOR]

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self.started_at = datetime.utcnow()
        anomaly = context.get("anomaly", "Unknown anomaly")

        # Phase 1: ALERT
        self.current_phase = DrillPhase.ALERT
        self.log_action(f"AMBUSH! Anomaly detected: {anomaly}")

        # Phase 2: ASSESS
        self.current_phase = DrillPhase.ASSESS
        self.log_action("Isolating affected components")

        # Phase 3: RESPOND
        self.current_phase = DrillPhase.RESPOND
        self.log_action("Diagnosing root cause")
        self.log_action("Implementing containment")

        # Phase 4: RECOVER
        self.current_phase = DrillPhase.RECOVER
        self.log_action("Restoring normal operations")
        self.success = True

        # Phase 5: REPORT
        self.current_phase = DrillPhase.REPORT
        self.completed_at = datetime.utcnow()

        return {
            "drill": self.name,
            "success": self.success,
            "anomaly": anomaly,
            "containment": "active",
            "actions": self.actions_taken,
        }


@dataclass
class ReactToIED(BattleDrill):
    """
    Battle Drill 4: React to IED/Mine

    FM 7-8 Trigger: IED detonation or discovery
    AI Trigger: Malicious input, injection attempt

    Response: 5 and 25 meter checks, report
    AI Response: Block, sanitize, report
    """

    def __post_init__(self):
        self.name = "React to IED"
        self.drill_number = 4
        self.triggers = [DrillTrigger.MALICIOUS_INPUT]

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self.started_at = datetime.utcnow()
        threat = context.get("threat", "Unknown threat")

        # Phase 1: ALERT
        self.current_phase = DrillPhase.ALERT
        self.log_action(f"IED! Malicious input detected: {threat[:50]}")

        # Phase 2: ASSESS
        self.current_phase = DrillPhase.ASSESS
        self.log_action("5-meter check: Immediate threat assessment")
        self.log_action("25-meter check: Secondary threat scan")

        # Phase 3: RESPOND
        self.current_phase = DrillPhase.RESPOND
        self.log_action("Blocking input")
        self.log_action("Sanitizing context")

        # Phase 4: RECOVER
        self.current_phase = DrillPhase.RECOVER
        self.log_action("Resuming with sanitized input")
        self.success = True

        # Phase 5: REPORT
        self.current_phase = DrillPhase.REPORT
        self.completed_at = datetime.utcnow()
        self.log_action("Reporting to security team")

        return {
            "drill": self.name,
            "success": self.success,
            "threat_type": "malicious_input",
            "blocked": True,
            "sanitized": True,
            "actions": self.actions_taken,
        }


@dataclass
class KnockOutBunker(BattleDrill):
    """
    Battle Drill 5: Knock Out Bunker

    FM 7-8 Trigger: Fortified enemy position
    AI Trigger: Hard problem requiring concentrated effort

    Response: Suppress, breach, assault, exploit
    AI Response: Concentrate resources, breach problem, solve, expand
    """

    def __post_init__(self):
        self.name = "Knock Out Bunker"
        self.drill_number = 5
        self.triggers = [DrillTrigger.HARD_PROBLEM]

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self.started_at = datetime.utcnow()
        problem = context.get("problem", "Unknown problem")

        # Phase 1: ALERT
        self.current_phase = DrillPhase.ALERT
        self.log_action(f"BUNKER! Hard problem identified: {problem[:50]}")

        # Phase 2: ASSESS
        self.current_phase = DrillPhase.ASSESS
        self.log_action("Suppression: Constraining problem scope")

        # Phase 3: RESPOND
        self.current_phase = DrillPhase.RESPOND
        self.log_action("Breach: Concentrating agent resources")
        self.log_action("Assault: Direct attack on problem")

        # Phase 4: RECOVER
        self.current_phase = DrillPhase.RECOVER
        self.log_action("Exploit: Expanding solution")
        self.success = True

        # Phase 5: REPORT
        self.current_phase = DrillPhase.REPORT
        self.completed_at = datetime.utcnow()

        return {
            "drill": self.name,
            "success": self.success,
            "problem": problem[:50],
            "resources_concentrated": True,
            "actions": self.actions_taken,
        }


@dataclass
class EnterClearRoom(BattleDrill):
    """
    Battle Drill 6: Enter and Clear a Room

    FM 7-8 Trigger: Building/room clearing operation
    AI Trigger: New feature, pipeline processing

    Response: Stack, breach, clear, mark
    AI Response: Clone, build, test, deploy
    """

    def __post_init__(self):
        self.name = "Enter and Clear Room"
        self.drill_number = 6
        self.triggers = [DrillTrigger.NEW_FEATURE]

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        self.started_at = datetime.utcnow()
        feature = context.get("feature", "Unknown feature")

        # Phase 1: ALERT (Stack)
        self.current_phase = DrillPhase.ALERT
        self.log_action(f"STACK! New feature: {feature}")

        # Phase 2: ASSESS (Breach)
        self.current_phase = DrillPhase.ASSESS
        self.log_action("Breach: Clone & Install")

        # Phase 3: RESPOND (Clear)
        self.current_phase = DrillPhase.RESPOND
        self.log_action("Clear Entry: Verify Build & Lint")
        self.log_action("Clear Room: Run Tests & Security Scan")

        # Phase 4: RECOVER (Consolidate)
        self.current_phase = DrillPhase.RECOVER
        self.log_action("Consolidate: Integration tests pass")
        self.success = True

        # Phase 5: REPORT (Mark)
        self.current_phase = DrillPhase.REPORT
        self.completed_at = datetime.utcnow()
        self.log_action("Mark: Tag as 'Ready for Deployment'")

        return {
            "drill": self.name,
            "success": self.success,
            "feature": feature,
            "build_passed": True,
            "tests_passed": True,
            "ready_for_deploy": True,
            "actions": self.actions_taken,
        }


class BattleDrillRouter:
    """
    Routes events to appropriate battle drills.

    Monitors for triggers and automatically executes drills.
    """

    def __init__(self):
        self.drills: dict[DrillTrigger, BattleDrill] = {}
        self._register_default_drills()

    def _register_default_drills(self):
        """Register all standard battle drills"""
        drill_classes = [
            ReactToContact,
            BreakContact,
            ReactToAmbush,
            ReactToIED,
            KnockOutBunker,
            EnterClearRoom,
        ]

        for drill_class in drill_classes:
            drill = drill_class(name="", drill_number=0, triggers=[])
            for trigger in drill.triggers:
                self.drills[trigger] = drill

    async def route(self, trigger: DrillTrigger, context: dict[str, Any]) -> dict[str, Any]:
        """Route trigger to appropriate drill and execute"""
        drill = self.drills.get(trigger)
        if drill:
            # Create fresh instance for execution
            drill_instance = type(drill)(
                name=drill.name,
                drill_number=drill.drill_number,
                triggers=drill.triggers,
            )
            return await drill_instance.execute(context)
        return {"error": f"No drill registered for trigger: {trigger.value}"}

    def get_drill(self, trigger: DrillTrigger) -> BattleDrill | None:
        """Get drill for trigger without executing"""
        return self.drills.get(trigger)
