"""Boy Scout Rule Metadata Bridge

Integrates the pnkln/scout registry with the existing AuditTrailPersistence system.
Provides tracking, validation, and reporting for agent cleanup actions.

Philosophy: Leave everything cleaner than you found it - and prove it.
"""

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .audit import AuditTrailPersistence, create_audit_trail


@dataclass
class BoyScoutMetadata:
    """Tracks cleanup actions for a single agent execution.

    Attributes:
        agent_name: Name of the agent performing work
        files_touched: List of file paths modified
        cleanup_actions: List of cleanup descriptions
        cleaner_than_found: Whether state improved (must be True)
        baseline_state: Hash/snapshot of initial state
        new_state: Hash/snapshot of final state
        timestamp: When the execution occurred
        execution_id: Unique ID for this execution

    """

    agent_name: str
    files_touched: list[str] = field(default_factory=list)
    cleanup_actions: list[str] = field(default_factory=list)
    cleaner_than_found: bool = True
    baseline_state: str = ""
    new_state: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_id: str = ""

    def __post_init__(self):
        if not self.execution_id:
            self.execution_id = self._generate_id()

    def _generate_id(self) -> str:
        """Generate unique execution ID"""
        content = f"{self.agent_name}:{self.timestamp}:{len(self.files_touched)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def validate(self) -> bool:
        """Validate that Boy Scout Rule is satisfied"""
        if not self.cleaner_than_found:
            return False
        if self.baseline_state and self.new_state:
            # If states are tracked, they should differ (improvement made)
            return self.baseline_state != self.new_state or len(self.cleanup_actions) > 0
        return True


class ScoutMetadataTracker:
    """Tracks Boy Scout Rule metadata across agent executions.

    Integrates with AuditTrailPersistence for persistent storage
    and provides validation that cleanup standards are met.
    """

    def __init__(
        self, audit_trail: AuditTrailPersistence | None = None, registry_path: Path | None = None,
    ):
        self.audit_trail = audit_trail or create_audit_trail()
        self.registry_path = (
            registry_path or Path(__file__).parent.parent.parent / "pnkln/scout/registry.json"
        )
        self._active_sessions: dict[str, BoyScoutMetadata] = {}
        self._registry_cache: dict | None = None

    def load_registry(self) -> dict[str, Any]:
        """Load the scout registry"""
        if self._registry_cache is not None:
            return self._registry_cache

        if not self.registry_path.exists():
            return {"skills": [], "agents": []}

        with open(self.registry_path) as f:
            self._registry_cache = json.load(f)
        return self._registry_cache

    def get_agent_template(self, agent_name: str) -> dict | None:
        """Get metadata template for an agent"""
        registry = self.load_registry()
        for agent in registry.get("agents", []):
            if agent["name"] == agent_name:
                return deepcopy(agent.get("metadataTemplate", {}))
        return None

    def start_session(self, agent_name: str, baseline_state: str = "") -> str:
        """Start a new tracking session for an agent execution.

        Args:
            agent_name: Name of the agent starting work
            baseline_state: Hash or description of initial state

        Returns:
            Execution ID for this session

        """
        metadata = BoyScoutMetadata(agent_name=agent_name, baseline_state=baseline_state)
        self._active_sessions[metadata.execution_id] = metadata
        return metadata.execution_id

    def record_file_touch(self, execution_id: str, file_path: str) -> None:
        """Record that a file was modified"""
        if execution_id in self._active_sessions:
            session = self._active_sessions[execution_id]
            if file_path not in session.files_touched:
                session.files_touched.append(file_path)

    def record_cleanup_action(self, execution_id: str, action: str) -> None:
        """Record a cleanup action taken"""
        if execution_id in self._active_sessions:
            self._active_sessions[execution_id].cleanup_actions.append(action)

    def end_session(
        self,
        execution_id: str,
        new_state: str = "",
        cleaner_than_found: bool = True,
        metrics: dict | None = None,
    ) -> BoyScoutMetadata:
        """End a tracking session and persist to audit trail.

        Args:
            execution_id: ID from start_session()
            new_state: Hash or description of final state
            cleaner_than_found: Whether improvement was made
            metrics: Optional monetization metrics

        Returns:
            Completed BoyScoutMetadata

        Raises:
            ValueError: If Boy Scout Rule validation fails

        """
        if execution_id not in self._active_sessions:
            raise ValueError(f"No active session: {execution_id}")

        session = self._active_sessions[execution_id]
        session.new_state = new_state
        session.cleaner_than_found = cleaner_than_found

        # Validate Boy Scout Rule
        if not session.validate():
            raise ValueError(
                f"Boy Scout Rule violation: Agent {session.agent_name} "
                f"did not leave system cleaner. Actions: {session.cleanup_actions}",
            )

        # Persist to audit trail
        audit_entry = {
            "type": "boy_scout_execution",
            "agent_name": session.agent_name,
            "execution_id": session.execution_id,
            "files_touched": session.files_touched,
            "cleanup_actions": session.cleanup_actions,
            "cleaner_than_found": session.cleaner_than_found,
            "baseline_state": session.baseline_state,
            "new_state": session.new_state,
            "timestamp": session.timestamp,
            "metrics": metrics or {},
        }
        self.audit_trail.append(audit_entry)

        # Clean up
        del self._active_sessions[execution_id]
        return session

    def get_cleanup_report(self, agent_name: str | None = None, limit: int = 100) -> dict[str, Any]:
        """Generate cleanup report for agents.

        Args:
            agent_name: Filter by specific agent (optional)
            limit: Maximum entries to include

        Returns:
            Report with cleanup statistics

        """
        entries = self.audit_trail.read_all()

        # Filter to boy scout executions
        scout_entries = [e for e in entries if e.get("type") == "boy_scout_execution"]

        # Filter by agent if specified
        if agent_name:
            scout_entries = [e for e in scout_entries if e.get("agent_name") == agent_name]

        # Take most recent
        scout_entries = scout_entries[-limit:]

        # Aggregate stats
        total_files = 0
        total_actions = 0
        violations = 0
        agent_stats: dict[str, dict] = {}

        for entry in scout_entries:
            agent = entry.get("agent_name", "unknown")
            files = len(entry.get("files_touched", []))
            actions = len(entry.get("cleanup_actions", []))

            total_files += files
            total_actions += actions

            if not entry.get("cleaner_than_found", True):
                violations += 1

            if agent not in agent_stats:
                agent_stats[agent] = {
                    "executions": 0,
                    "files_touched": 0,
                    "cleanup_actions": 0,
                    "violations": 0,
                }

            agent_stats[agent]["executions"] += 1
            agent_stats[agent]["files_touched"] += files
            agent_stats[agent]["cleanup_actions"] += actions
            if not entry.get("cleaner_than_found", True):
                agent_stats[agent]["violations"] += 1

        return {
            "total_executions": len(scout_entries),
            "total_files_touched": total_files,
            "total_cleanup_actions": total_actions,
            "total_violations": violations,
            "compliance_rate": (
                (len(scout_entries) - violations) / len(scout_entries) * 100
                if scout_entries
                else 100.0
            ),
            "agent_breakdown": agent_stats,
            "recent_cleanups": [
                {
                    "agent": e.get("agent_name"),
                    "actions": e.get("cleanup_actions", []),
                    "timestamp": e.get("timestamp"),
                }
                for e in scout_entries[-10:]
            ],
        }


# Factory function
def create_scout_tracker(audit_trail: AuditTrailPersistence | None = None) -> ScoutMetadataTracker:
    """Create a ScoutMetadataTracker with default configuration"""
    return ScoutMetadataTracker(audit_trail=audit_trail)


# Context manager for tracking sessions
class ScoutSession:
    """Context manager for Boy Scout Rule tracking.

    Usage:
        tracker = create_scout_tracker()
        with ScoutSession(tracker, "ResearchAgent", baseline="v1.0") as session:
            session.touch_file("/path/to/file.py")
            session.cleanup("Removed unused import")
            # ... do work ...
        # Session automatically validated and persisted on exit
    """

    def __init__(self, tracker: ScoutMetadataTracker, agent_name: str, baseline: str = ""):
        self.tracker = tracker
        self.agent_name = agent_name
        self.baseline = baseline
        self.execution_id: str = ""
        self._new_state: str = ""
        self._metrics: dict = {}

    def __enter__(self) -> "ScoutSession":
        self.execution_id = self.tracker.start_session(
            self.agent_name, baseline_state=self.baseline,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self.tracker.end_session(
                self.execution_id,
                new_state=self._new_state,
                cleaner_than_found=True,
                metrics=self._metrics,
            )
        return False

    def touch_file(self, file_path: str) -> None:
        """Record file modification"""
        self.tracker.record_file_touch(self.execution_id, file_path)

    def cleanup(self, action: str) -> None:
        """Record cleanup action"""
        self.tracker.record_cleanup_action(self.execution_id, action)

    def set_new_state(self, state: str) -> None:
        """Set final state for comparison"""
        self._new_state = state

    def set_metrics(self, metrics: dict) -> None:
        """Set monetization metrics"""
        self._metrics = metrics


if __name__ == "__main__":
    # Self-test
    tracker = create_scout_tracker()

    # Test context manager usage
    with ScoutSession(tracker, "ResearchAgent", baseline="initial") as session:
        session.touch_file("/path/to/research.py")
        session.cleanup("Removed duplicate research queries")
        session.cleanup("Consolidated data sources")
        session.set_new_state("improved")
        session.set_metrics({"time_saved_hours": 1.5, "revenue_identified_usd": 25000})

    # Generate report
    report = tracker.get_cleanup_report()
    print(json.dumps(report, indent=2))
