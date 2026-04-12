#!/usr/bin/env python3
"""
Hybrid Orchestrator: Routes tasks to appropriate execution layer
Combines: rtrvr.ai (web) + E2B (sandbox) + CI pipeline + n-autoresearch/Kosmos/BioAgents

Part of 4-Module Agent Stack
"""

import asyncio
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import requests


class ExecutionLayer(Enum):
    """Available execution layers."""

    n-autoresearch/Kosmos/BioAgents = "n-autoresearch/Kosmos/BioAgents"  # General agent swarm
    E2B = "e2b"  # Code sandbox
    RTRVR = "rtrvr"  # Web automation
    CI = "ci"  # Dual-model CI pipeline
    LOOP = "loop"  # ADK loop agent
    LOCAL = "local"  # Local execution


@dataclass
class TaskResult:
    """Result from task execution."""

    layer: ExecutionLayer
    success: bool
    output: Any
    cost: float = 0.0
    duration_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class HybridOrchestrator:
    """
    Routes tasks to the most appropriate execution layer.

    Layers:
    - n-autoresearch/Kosmos/BioAgents: 600 agent swarm for general tasks
    - E2B: Sandboxed code execution (Firecracker VMs)
    - rtrvr.ai: Web automation and data extraction
    - CI Pipeline: Dual-model code review
    - Loop Agent: Architect/Critic/Refiner iterations
    """

    n-autoresearch/Kosmos/BioAgents_URL = os.environ.get("n-autoresearch/Kosmos/BioAgents_URL", "http://localhost:8600")
    E2B_API_KEY = os.environ.get("E2B_API_KEY", "")

    # Task type to layer mapping
    LAYER_ROUTING = {
        # Web tasks → rtrvr.ai
        "browse": ExecutionLayer.RTRVR,
        "extract": ExecutionLayer.RTRVR,
        "scrape": ExecutionLayer.RTRVR,
        "web": ExecutionLayer.RTRVR,
        "navigate": ExecutionLayer.RTRVR,
        # Code execution → E2B sandbox
        "execute": ExecutionLayer.E2B,
        "run_code": ExecutionLayer.E2B,
        "sandbox": ExecutionLayer.E2B,
        "test": ExecutionLayer.E2B,
        # Code review → CI pipeline
        "review": ExecutionLayer.CI,
        "analyze": ExecutionLayer.CI,
        "validate": ExecutionLayer.CI,
        "lint": ExecutionLayer.CI,
        # Architecture → Loop agent
        "design": ExecutionLayer.LOOP,
        "architect": ExecutionLayer.LOOP,
        "plan": ExecutionLayer.LOOP,
        # Default → n-autoresearch/Kosmos/BioAgents
        "default": ExecutionLayer.n-autoresearch/Kosmos/BioAgents,
    }

    def __init__(self):
        """Initialize orchestrator with available backends."""
        self.stats = {
            "tasks_routed": 0,
            "by_layer": {layer.value: 0 for layer in ExecutionLayer},
            "total_cost": 0.0,
        }

    def route_task(self, task: dict[str, Any]) -> ExecutionLayer:
        """Determine which execution layer to use."""
        task_type = task.get("type", "").lower()

        # Check explicit type mapping
        if task_type in self.LAYER_ROUTING:
            return self.LAYER_ROUTING[task_type]

        # Keyword-based routing from prompt
        prompt = task.get("prompt", "").lower()

        if any(kw in prompt for kw in ["browse", "website", "url", "scrape"]):
            return ExecutionLayer.RTRVR
        elif any(kw in prompt for kw in ["execute", "run", "code", "python", "sandbox"]):
            return ExecutionLayer.E2B
        elif any(kw in prompt for kw in ["review", "pr", "diff", "analyze"]):
            return ExecutionLayer.CI
        elif any(kw in prompt for kw in ["design", "architect", "infrastructure"]):
            return ExecutionLayer.LOOP

        return ExecutionLayer.n-autoresearch/Kosmos/BioAgents

    async def execute_n-autoresearch/Kosmos/BioAgents(self, task: dict[str, Any]) -> TaskResult:
        """Execute via n-autoresearch/Kosmos/BioAgents agent swarm."""
        try:
            endpoint = task.get("endpoint", "task")
            response = requests.post(
                f"{self.n-autoresearch/Kosmos/BioAgents_URL}/{endpoint}",
                json={"prompt": task.get("prompt", "")},
                timeout=120,
            )
            response.raise_for_status()
            result = response.json()

            return TaskResult(
                layer=ExecutionLayer.n-autoresearch/Kosmos/BioAgents,
                success=True,
                output=result.get("response", result),
                cost=0.001,  # Flash tier default
                metadata={"endpoint": endpoint},
            )
        except Exception as e:
            return TaskResult(layer=ExecutionLayer.n-autoresearch/Kosmos/BioAgents, success=False, output=str(e))

    async def execute_e2b(self, task: dict[str, Any]) -> TaskResult:
        """Execute code in E2B sandbox."""
        if not self.E2B_API_KEY:
            return TaskResult(
                layer=ExecutionLayer.E2B, success=False, output="E2B_API_KEY not configured"
            )

        try:
            # E2B SDK integration
            # Note: Requires `pip install e2b`
            import e2b

            sandbox = e2b.Sandbox(api_key=self.E2B_API_KEY)

            code = task.get("code", task.get("prompt", ""))
            language = task.get("language", "python")

            if language == "python":
                result = sandbox.process.start(f"python3 -c '{code}'").wait()
            else:
                result = sandbox.process.start(code).wait()

            return TaskResult(
                layer=ExecutionLayer.E2B,
                success=result.exit_code == 0,
                output=result.stdout or result.stderr,
                cost=0.01,  # E2B per-execution cost
                metadata={"exit_code": result.exit_code},
            )
        except ImportError:
            # Fallback to local execution with warning
            return await self.execute_local(task)
        except Exception as e:
            return TaskResult(layer=ExecutionLayer.E2B, success=False, output=str(e))

    async def execute_rtrvr(self, task: dict[str, Any]) -> TaskResult:
        """Execute web automation via rtrvr.ai or browser MCP."""
        try:
            # rtrvr.ai integration via MCP
            # Uses browser-as-MCP for web navigation
            url = task.get("url", "")
            action = task.get("action", "fetch")

            if action == "fetch":
                # Simple URL fetch
                response = requests.get(url, timeout=30)
                return TaskResult(
                    layer=ExecutionLayer.RTRVR,
                    success=True,
                    output=response.text[:10000],
                    cost=0.0,
                    metadata={"status_code": response.status_code},
                )
            else:
                # Complex browser automation would use MCP
                # Placeholder for full rtrvr.ai integration
                return TaskResult(
                    layer=ExecutionLayer.RTRVR,
                    success=False,
                    output="Complex browser automation requires MCP server",
                )
        except Exception as e:
            return TaskResult(layer=ExecutionLayer.RTRVR, success=False, output=str(e))

    async def execute_ci(self, task: dict[str, Any]) -> TaskResult:
        """Execute via Dual-Model CI pipeline."""
        import subprocess
        import tempfile

        try:
            diff = task.get("diff", "")
            diff_range = task.get("diff_range", "origin/main...HEAD")

            # Write diff to temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                if diff:
                    f.write(diff)
                else:
                    # Get diff from git
                    result = subprocess.run(
                        ["git", "diff", diff_range], capture_output=True, text=True
                    )
                    f.write(result.stdout)
                diff_file = f.name

            # Run implementer
            impl_result = subprocess.run(
                ["python3", "scripts/implementer.py", diff_file],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Write plan
            plan_file = diff_file.replace(".txt", "_plan.json")
            with open(plan_file, "w") as f:
                f.write(impl_result.stdout)

            # Run critic
            critic_result = subprocess.run(
                ["python3", "scripts/critic.py", diff_file, plan_file],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Read critic issues if generated
            issues = ""
            if os.path.exists("critic_issues.md"):
                with open("critic_issues.md") as f:
                    issues = f.read()

            return TaskResult(
                layer=ExecutionLayer.CI,
                success=critic_result.returncode == 0,
                output={
                    "implementer": impl_result.stdout,
                    "critic": critic_result.stdout,
                    "issues": issues,
                },
                cost=0.011,  # ~$0.001 implementer + $0.01 critic
                metadata={"verdict": "APPROVED" if critic_result.returncode == 0 else "BLOCKED"},
            )
        except Exception as e:
            return TaskResult(layer=ExecutionLayer.CI, success=False, output=str(e))

    async def execute_loop(self, task: dict[str, Any]) -> TaskResult:
        """Execute via Loop Agent (ADK pattern)."""
        try:
            from agents.loop_agent import LoopAgent

            requirement = task.get("requirement", task.get("prompt", ""))
            max_iterations = task.get("max_iterations", 5)

            agent = LoopAgent(max_iterations=max_iterations)
            result = agent.run(requirement)

            return TaskResult(
                layer=ExecutionLayer.LOOP,
                success=result.get("approved", False),
                output=result,
                cost=result.get("iterations", 1) * 0.02,  # ~$0.02/iteration
                metadata={"iterations": result.get("iterations"), "status": result.get("status")},
            )
        except Exception as e:
            return TaskResult(layer=ExecutionLayer.LOOP, success=False, output=str(e))

    async def execute_local(self, task: dict[str, Any]) -> TaskResult:
        """Execute locally (fallback)."""
        import subprocess

        try:
            code = task.get("code", task.get("prompt", ""))

            result = subprocess.run(
                ["python3", "-c", code], capture_output=True, text=True, timeout=30
            )

            return TaskResult(
                layer=ExecutionLayer.LOCAL,
                success=result.returncode == 0,
                output=result.stdout or result.stderr,
                cost=0.0,
                metadata={"exit_code": result.returncode},
            )
        except Exception as e:
            return TaskResult(layer=ExecutionLayer.LOCAL, success=False, output=str(e))

    async def execute(self, task: dict[str, Any]) -> TaskResult:
        """
        Execute task on appropriate layer.

        Routing logic:
        1. Check explicit layer override
        2. Route based on task type
        3. Route based on prompt keywords
        4. Default to n-autoresearch/Kosmos/BioAgents
        """
        # Allow explicit layer override
        if "layer" in task:
            layer = ExecutionLayer(task["layer"])
        else:
            layer = self.route_task(task)

        print(f"///▞ HYBRID :: Routing to {layer.value}")

        # Execute on appropriate layer
        if layer == ExecutionLayer.n-autoresearch/Kosmos/BioAgents:
            result = await self.execute_n-autoresearch/Kosmos/BioAgents(task)
        elif layer == ExecutionLayer.E2B:
            result = await self.execute_e2b(task)
        elif layer == ExecutionLayer.RTRVR:
            result = await self.execute_rtrvr(task)
        elif layer == ExecutionLayer.CI:
            result = await self.execute_ci(task)
        elif layer == ExecutionLayer.LOOP:
            result = await self.execute_loop(task)
        else:
            result = await self.execute_local(task)

        # Update stats
        self.stats["tasks_routed"] += 1
        self.stats["by_layer"][layer.value] += 1
        self.stats["total_cost"] += result.cost

        return result

    async def execute_batch(self, tasks: list[dict[str, Any]]) -> list[TaskResult]:
        """Execute multiple tasks in parallel where possible."""
        # Group tasks by layer for efficient batching
        results = await asyncio.gather(*[self.execute(task) for task in tasks])
        return list(results)

    def get_stats(self) -> dict[str, Any]:
        """Return routing statistics."""
        return self.stats


# Standalone execution
if __name__ == "__main__":
    import sys

    async def main():
        orchestrator = HybridOrchestrator()

        # Example tasks for each layer
        test_tasks = [
            {"type": "default", "prompt": "What is the capital of France?"},
            {"type": "review", "diff_range": "HEAD~1...HEAD"},
            {"type": "design", "prompt": "Design a serverless API"},
        ]

        if len(sys.argv) > 1:
            # Single task from command line
            task = {"prompt": " ".join(sys.argv[1:])}
            result = await orchestrator.execute(task)
            print(f"Layer: {result.layer.value}")
            print(f"Success: {result.success}")
            print(f"Output: {result.output}")
        else:
            # Run example tasks
            for task in test_tasks:
                print(f"\n{'=' * 60}")
                print(f"Task: {task}")
                result = await orchestrator.execute(task)
                print(f"Layer: {result.layer.value}")
                print(f"Success: {result.success}")
                print(f"Cost: ${result.cost:.4f}")

            print(f"\n{'=' * 60}")
            print("Stats:", json.dumps(orchestrator.get_stats(), indent=2))

    asyncio.run(main())
