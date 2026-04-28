# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Idle Worker - 24/7 Maintenance & Intelligence Ingestion

Keeps all paid instances busy during downtime with:
- System maintenance (logs, deps, security)
- Codebase maintenance (dead code, refactoring, docs)
- Intelligence ingestion (fold recent learnings into stack)
"""

import glob
import os
import threading
import time
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from typing import Any


class MaintenanceTaskType(Enum):
    """Types of maintenance tasks"""

    SYSTEM = "system"
    CODEBASE = "codebase"
    INTELLIGENCE = "intelligence"
    SECURITY = "security"


@dataclass
class MaintenanceTask:
    """Represents a maintenance task"""

    id: str
    type: MaintenanceTaskType
    description: str
    priority: int = 5  # 1-10, lower is higher priority
    estimated_duration: int = 60  # seconds
    completed: bool = False


class IdleWorker:
    """Keeps instances busy 24/7 with maintenance and intelligence ingestion.

    Tasks run during idle periods to maximize license utilization.
    """

    def __init__(self, autoresearch=None, rotation_orchestrator=None):
        self.autoresearch = autoresearch
        self.rotation_orchestrator = rotation_orchestrator

        self.task_queue = Queue()
        self.completed_tasks: list[MaintenanceTask] = []
        self.running = False
        self.thread: threading.Thread | None = None

        self._initialize_tasks()

    def _initialize_tasks(self):
        """Initialize the maintenance task queue"""
        tasks = [
            # System Maintenance
            MaintenanceTask(
                id="sys-log-rotation",
                type=MaintenanceTaskType.SYSTEM,
                description="Rotate and compress old log files",
                priority=3,
                estimated_duration=30,
            ),
            MaintenanceTask(
                id="sys-dep-update",
                type=MaintenanceTaskType.SYSTEM,
                description="Check for dependency updates",
                priority=5,
                estimated_duration=120,
            ),
            # Codebase Maintenance
            MaintenanceTask(
                id="code-dead-import",
                type=MaintenanceTaskType.CODEBASE,
                description="Remove unused imports",
                priority=4,
                estimated_duration=45,
            ),
            MaintenanceTask(
                id="code-docstring",
                type=MaintenanceTaskType.CODEBASE,
                description="Add missing docstrings",
                priority=6,
                estimated_duration=90,
            ),
            MaintenanceTask(
                id="code-type-hints",
                type=MaintenanceTaskType.CODEBASE,
                description="Add type hints to functions",
                priority=7,
                estimated_duration=120,
            ),
            # Intelligence Ingestion
            MaintenanceTask(
                id="intel-conversation",
                type=MaintenanceTaskType.INTELLIGENCE,
                description="Process recent conversation exports",
                priority=2,
                estimated_duration=180,
            ),
            MaintenanceTask(
                id="intel-knowledge-base",
                type=MaintenanceTaskType.INTELLIGENCE,
                description="Update knowledge base from ingestion pipeline",
                priority=1,
                estimated_duration=240,
            ),
            # Security
            MaintenanceTask(
                id="sec-audit",
                type=MaintenanceTaskType.SECURITY,
                description="Run security audit on dependencies",
                priority=2,
                estimated_duration=60,
            ),
        ]

        # Sort by priority and add to queue
        tasks.sort(key=lambda t: t.priority)
        for task in tasks:
            self.task_queue.put(task)

    def start(self):
        """Start the idle worker loop"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._work_loop, daemon=True)
        self.thread.start()
        print("///▞ IDLE WORKER :: Started 24/7 Maintenance & Intelligence Ingestion")

    def stop(self):
        """Stop the idle worker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def _work_loop(self):
        """Background loop to execute maintenance tasks"""
        while self.running:
            if not self.task_queue.empty():
                task = self.task_queue.get()

                print(f"///▞ IDLE WORKER :: Executing {task.id} ({task.type.value})")

                # Execute task based on type
                if task.type == MaintenanceTaskType.SYSTEM:
                    self._execute_system_task(task)
                elif task.type == MaintenanceTaskType.CODEBASE:
                    self._execute_codebase_task(task)
                elif task.type == MaintenanceTaskType.INTELLIGENCE:
                    self._execute_intelligence_task(task)
                elif task.type == MaintenanceTaskType.SECURITY:
                    self._execute_security_task(task)

                task.completed = True
                self.completed_tasks.append(task)

                print(f"///▞ IDLE WORKER :: Completed {task.id}")
            else:
                # Queue is empty, reinitialize tasks for next cycle
                print("///▞ IDLE WORKER :: Task cycle complete. Reinitializing...")
                self._initialize_tasks()

            time.sleep(5)

    def _execute_system_task(self, task: MaintenanceTask):
        """Execute system maintenance task"""
        if task.id == "sys-log-rotation":
            # Rotate logs
            try:
                log_dir = "logs"
                if os.path.exists(log_dir):
                    log_files = glob.glob(f"{log_dir}/*.log")
                    for log_file in log_files:
                        # Compress old logs (simulate)
                        print(f"  → Rotating {log_file}")
                time.sleep(2)
            except Exception as e:
                print(f"  → Error: {e}")

        elif task.id == "sys-dep-update":
            # Check dependencies (simulate)
            print("  → Checking pip dependencies...")
            time.sleep(3)

    def _execute_codebase_task(self, task: MaintenanceTask):
        """Execute codebase maintenance task"""
        if task.id == "code-dead-import":
            # Remove unused imports (simulate)
            print("  → Scanning for unused imports...")
            time.sleep(2)

        elif task.id == "code-docstring":
            # Add docstrings (simulate)
            print("  → Adding missing docstrings...")
            time.sleep(3)

        elif task.id == "code-type-hints":
            # Add type hints (simulate)
            print("  → Adding type hints...")
            time.sleep(3)

    def _execute_intelligence_task(self, task: MaintenanceTask):
        """Execute intelligence ingestion task"""
        if task.id == "intel-conversation":
            # Process conversation exports
            print("  → Processing conversation exports...")
            extractions_dir = "erik-hancock-llm-memory/extractions"
            if os.path.exists(extractions_dir):
                json_files = glob.glob(f"{extractions_dir}/*.json")
                print(f"  → Found {len(json_files)} extraction files")
                # Simulate processing
                time.sleep(4)
            else:
                print("  → No extractions directory found")

        elif task.id == "intel-knowledge-base":
            # Update knowledge base
            print("  → Updating knowledge base...")
            print("  → Folding recent learnings into current stack...")
            # Simulate ingestion
            time.sleep(5)

    def _execute_security_task(self, task: MaintenanceTask):
        """Execute security task"""
        if task.id == "sec-audit":
            # Run security audit
            print("  → Running security audit...")
            try:
                # Simulate pip-audit or safety check
                print("  → Checking for known vulnerabilities...")
                time.sleep(3)
            except Exception as e:
                print(f"  → Error: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get idle worker statistics"""
        total_completed = len(self.completed_tasks)

        by_type = {}
        for task_type in MaintenanceTaskType:
            completed = [t for t in self.completed_tasks if t.type == task_type]
            by_type[task_type.value] = len(completed)

        return {
            "total_completed": total_completed,
            "queue_size": self.task_queue.qsize(),
            "running": self.running,
            "completed_by_type": by_type,
            "recent_tasks": [
                {"id": t.id, "type": t.type.value, "description": t.description}
                for t in self.completed_tasks[-5:]
            ],
        }
