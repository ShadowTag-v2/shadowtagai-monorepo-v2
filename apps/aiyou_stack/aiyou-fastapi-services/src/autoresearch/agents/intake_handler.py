"""
Intake Handler - Sonnet 4.5 Interface

Receives tasks from the standalone Sonnet 4.5 instance and routes them
to the Flying minion for processing via the Antigravity Gemini pool.
"""

import json
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from queue import PriorityQueue
from typing import Any


class TaskPriority(Enum):
    """Task priority levels"""

    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    MAINTENANCE = 5


@dataclass
class IncomingTask:
    """Represents a task from Sonnet 4.5"""

    id: str
    content: str
    priority: TaskPriority
    source: str = "sonnet-4.5"
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __lt__(self, other):
        """For priority queue sorting"""
        return self.priority.value < other.priority.value


class IntakeHandler:
    """
    Handles intake from Sonnet 4.5 and routes to Flying minion.

    Pipeline: Sonnet 4.5 → IntakeHandler → minion → FinalBoss → Git
    """

    def __init__(self, autoresearch=None):
        self.autoresearch = autoresearch
        self.task_queue = PriorityQueue()
        self.processed_tasks: list[IncomingTask] = []
        self.running = False
        self.thread: threading.Thread | None = None

        # Stats
        self.total_received = 0
        self.total_processed = 0
        self.total_rejected = 0

    def start(self):
        """Start the intake processing loop"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        print("///▞ INTAKE HANDLER :: Started Sonnet 4.5 Interface")

    def stop(self):
        """Stop the intake handler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def receive_task(self, task: IncomingTask):
        """
        Receive a task from Sonnet 4.5.

        Args:
            task: IncomingTask object
        """
        self.total_received += 1
        self.task_queue.put(task)
        print(f"///▞ INTAKE :: Received task {task.id} (Priority: {task.priority.name})")

    def receive_from_json(self, json_path: str):
        """
        Receive tasks from a JSON file (for batch processing).

        Args:
            json_path: Path to JSON file with tasks
        """
        try:
            with open(json_path) as f:
                data = json.load(f)

            tasks = data.get("tasks", [])
            for task_data in tasks:
                task = IncomingTask(
                    id=task_data.get("id", f"task-{time.time()}"),
                    content=task_data.get("content", ""),
                    priority=TaskPriority[task_data.get("priority", "NORMAL")],
                    metadata=task_data.get("metadata", {}),
                )
                self.receive_task(task)

            print(f"///▞ INTAKE :: Loaded {len(tasks)} tasks from {json_path}")
        except Exception as e:
            print(f"///▞ INTAKE :: Error loading tasks: {e}")

    def _process_loop(self):
        """Background loop to process incoming tasks"""
        while self.running:
            if not self.task_queue.empty():
                task = self.task_queue.get()

                # Triage and categorize
                categorized_task = self._triage(task)

                # Route to Flying minion if available
                if self.autoresearch:
                    self._route_to_autoresearch(categorized_task)
                    self.total_processed += 1
                else:
                    # Queue for later processing
                    self.processed_tasks.append(categorized_task)

            time.sleep(0.1)

    def _triage(self, task: IncomingTask) -> IncomingTask:
        """
        Triage and categorize the task.

        Args:
            task: Incoming task

        Returns:
            Categorized task with metadata
        """
        # Add categorization metadata
        task.metadata["category"] = self._categorize_content(task.content)
        task.metadata["estimated_complexity"] = self._estimate_complexity(task.content)

        return task

    def _categorize_content(self, content: str) -> str:
        """Categorize task content"""
        content_lower = content.lower()

        if any(kw in content_lower for kw in ["bug", "fix", "error", "crash"]):
            return "bug_fix"
        elif any(kw in content_lower for kw in ["feature", "implement", "add"]):
            return "feature"
        elif any(kw in content_lower for kw in ["refactor", "cleanup", "optimize"]):
            return "refactor"
        elif any(kw in content_lower for kw in ["test", "verify", "validate"]):
            return "testing"
        else:
            return "general"

    def _estimate_complexity(self, content: str) -> str:
        """Estimate task complexity"""
        word_count = len(content.split())

        if word_count > 200:
            return "high"
        elif word_count > 50:
            return "medium"
        else:
            return "low"

    def _route_to_autoresearch(self, task: IncomingTask):
        """
        Route the task to Flying minion for deep analysis.

        Args:
            task: Categorized task
        """
        # In a real implementation, this would integrate with the Flying minion
        # For now, we log the routing
        print(
            f"///▞ INTAKE :: Routing {task.id} to Flying minion ({task.metadata.get('category')})"
        )

    def get_stats(self) -> dict[str, Any]:
        """Get intake handler statistics"""
        return {
            "total_received": self.total_received,
            "total_processed": self.total_processed,
            "total_rejected": self.total_rejected,
            "queue_size": self.task_queue.qsize(),
            "running": self.running,
        }
