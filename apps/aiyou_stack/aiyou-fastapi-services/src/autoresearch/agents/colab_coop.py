#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Colab Coop: Cooperative notebook execution orchestrator.
Distributes workloads across Gemini accounts via Cloud Code API.

Architecture:
  Antigravity IDE → CloudCodePool → Colab Coop → minions
                                  ↓
                    [Account 1] [Account 2] ... [Account 10]

Part of Cloud Code API + Colab automation stack.
"""

import asyncio
import json
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agents.cloudcode_client import CloudCodeClient, CloudCodePool


class CoopStrategy(Enum):
    """Distribution strategies for cooperative execution."""

    ROUND_ROBIN = "round_robin"  # Simple rotation
    LOAD_BALANCED = "load_balanced"  # Based on account stats
    SHARDED = "sharded"  # Data partitioning
    REPLICATED = "replicated"  # Same task, multiple accounts
    GPU_PRIORITY = "gpu_priority"  # GPU-heavy tasks get priority


@dataclass
class CoopTask:
    """Task for cooperative execution."""

    task_id: str
    notebook_code: str
    data_shard: Any | None = None
    requires_gpu: bool = False
    priority: int = 5
    timeout_seconds: int = 120
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CoopResult:
    """Result from cooperative execution."""

    task_id: str
    account_id: int
    success: bool
    output: Any
    duration_ms: int = 0
    tokens_used: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ColabCoop:
    """Cooperative Colab notebook orchestrator.

    Distributes notebook execution across multiple Gemini accounts
    via Cloud Code API, with minions routing for complex tasks.

    Scaling: Start with 1 account → scale to 10.
    """

    def __init__(self, num_accounts: int = 1, strategy: CoopStrategy = CoopStrategy.ROUND_ROBIN):
        """Initialize cooperative orchestrator.

        Args:
            num_accounts: Number of accounts to use (1-10)
            strategy: Task distribution strategy

        """
        self.num_accounts = min(num_accounts, 10)
        self.strategy = strategy
        self.pool = CloudCodePool(num_accounts=self.num_accounts)
        self.current_index = 0

        # Stats tracking
        self.stats = {
            "tasks_distributed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_tokens": 0,
            "by_account": dict.fromkeys(range(1, self.num_accounts + 1), 0),
            "start_time": datetime.now(),
        }

        # minions endpoint for complex routing
        self.minions_url = os.getenv("minionS_URL", "http://localhost:8600")  # noqa: SIM112

        print(f"///▞ COLAB COOP :: Initialized with {len(self.pool.clients)} accounts")
        print(f"///▞ COLAB COOP :: Strategy: {strategy.value}")

    def _get_next_account(self, task: CoopTask | None = None) -> CloudCodeClient:
        """Get next account based on strategy."""
        if not self.pool.clients:
            raise RuntimeError("No accounts available in pool")

        if self.strategy == CoopStrategy.ROUND_ROBIN:
            client = self.pool.clients[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.pool.clients)
            return client

        if self.strategy == CoopStrategy.LOAD_BALANCED:
            # Select account with lowest request count
            return min(self.pool.clients, key=lambda c: c.stats.requests)

        if self.strategy == CoopStrategy.GPU_PRIORITY:
            # GPU tasks go to accounts with lower error rates
            if task and task.requires_gpu:
                return min(self.pool.clients, key=lambda c: c.stats.errors)
            return self.pool.get_next_client()

        return self.pool.get_next_client()

    async def execute_cell(self, code: str, context: str | None = None) -> CoopResult:
        """Execute a single notebook cell.

        Args:
            code: Python code to execute
            context: Previous cell context (variables, outputs)

        Returns:
            CoopResult with execution details

        """
        task = CoopTask(task_id=f"cell_{datetime.now().timestamp()}", notebook_code=code)

        client = self._get_next_account(task)
        start_time = datetime.now()

        try:
            result = await client.execute_notebook_cell(code, context)

            self.stats["tasks_completed"] += 1
            self.stats["by_account"][client.account_id] = (
                self.stats["by_account"].get(client.account_id, 0) + 1
            )

            return CoopResult(
                task_id=task.task_id,
                account_id=client.account_id,
                success=result.get("safe_to_execute", True),
                output=result,
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                metadata={"dependencies": result.get("dependencies", [])},
            )
        except Exception as e:
            self.stats["tasks_failed"] += 1
            return CoopResult(
                task_id=task.task_id,
                account_id=client.account_id,
                success=False,
                output=str(e),
            )
        finally:
            self.stats["tasks_distributed"] += 1

    async def execute_notebook(self, cells: list[str], sequential: bool = True) -> list[CoopResult]:
        """Execute a complete notebook.

        Args:
            cells: List of code cells
            sequential: If True, execute in order with context passing

        Returns:
            List of results for each cell

        """
        results = []
        context = ""

        if sequential:
            for i, cell in enumerate(cells):
                result = await self.execute_cell(cell, context)
                results.append(result)

                # Build context from successful executions
                if result.success and isinstance(result.output, dict):
                    modified = result.output.get("modified_code", cell)
                    context += f"\n# Cell {i}:\n{modified}\n"
        else:
            # Parallel execution across accounts
            tasks = [self.execute_cell(cell) for cell in cells]
            results = await asyncio.gather(*tasks)

        return results

    async def distribute_sharded(
        self,
        notebook_template: str,
        data_shards: list[Any],
        aggregator: Callable | None = None,
    ) -> dict[str, Any]:
        """Execute notebook with sharded data across accounts.

        Args:
            notebook_template: Notebook code with {SHARD_DATA} placeholder
            data_shards: List of data shards to distribute
            aggregator: Function to aggregate results

        Returns:
            Aggregated results from all shards

        """
        tasks = []

        for i, shard in enumerate(data_shards):
            # Inject shard data into template
            code = notebook_template.replace("{SHARD_DATA}", json.dumps(shard))
            code = code.replace("{SHARD_INDEX}", str(i))
            code = code.replace("{TOTAL_SHARDS}", str(len(data_shards)))

            task = CoopTask(task_id=f"shard_{i}", notebook_code=code, data_shard=shard)
            tasks.append(task)

        # Execute all shards in parallel
        async def execute_shard(task: CoopTask) -> CoopResult:
            client = self._get_next_account(task)
            result = await client.execute_notebook_cell(task.notebook_code)
            return CoopResult(
                task_id=task.task_id,
                account_id=client.account_id,
                success=result.get("safe_to_execute", True),
                output=result,
                metadata={"shard": task.data_shard},
            )

        results = await asyncio.gather(*[execute_shard(t) for t in tasks])

        # Aggregate results
        if aggregator:
            aggregated = aggregator([r.output for r in results])
        else:
            aggregated = {
                "shards_processed": len(results),
                "successful": sum(1 for r in results if r.success),
                "results": [r.output for r in results],
            }

        return {
            "strategy": "sharded",
            "num_shards": len(data_shards),
            "aggregated": aggregated,
            "individual_results": [
                {"task_id": r.task_id, "account_id": r.account_id, "success": r.success}
                for r in results
            ],
        }

    async def execute_replicated(
        self,
        notebook_code: str,
        num_replicas: int | None = None,
    ) -> dict[str, Any]:
        """Execute same notebook on multiple accounts for redundancy/comparison.

        Args:
            notebook_code: Code to execute
            num_replicas: Number of replicas (default: all accounts)

        Returns:
            Results from all replicas with consensus analysis

        """
        n = num_replicas or len(self.pool.clients)
        n = min(n, len(self.pool.clients))

        async def execute_replica(client: CloudCodeClient) -> CoopResult:
            result = await client.execute_notebook_cell(notebook_code)
            return CoopResult(
                task_id=f"replica_{client.account_id}",
                account_id=client.account_id,
                success=result.get("safe_to_execute", True),
                output=result,
            )

        results = await asyncio.gather(*[execute_replica(self.pool.clients[i]) for i in range(n)])

        # Analyze consensus
        successful = [r for r in results if r.success]

        return {
            "strategy": "replicated",
            "num_replicas": n,
            "successful_replicas": len(successful),
            "consensus": len(successful) > n // 2,
            "results": [
                {"account_id": r.account_id, "success": r.success, "output": r.output}
                for r in results
            ],
        }

    async def route_to_minions(self, prompt: str, tier: str = "task") -> dict[str, Any]:
        """Route complex tasks to minions swarm.

        Args:
            prompt: Task description
            tier: "task" (Flash) or "governance" (Pro)

        Returns:
            minions response

        """
        # Use first available client for routing
        if self.pool.clients:
            return await self.pool.clients[0].route_to_minions(prompt, tier)
        return {"error": "No clients available", "success": False}

    async def generate_notebook(self, description: str) -> dict[str, Any]:
        """Generate a complete notebook from description.

        Args:
            description: What the notebook should do

        Returns:
            Generated notebook cells

        """
        client = self._get_next_account()

        prompt = f"""Generate a Jupyter/Colab notebook for:

{description}

Return a JSON array of cells, where each cell is:
{{
  "cell_type": "code" or "markdown",
  "source": "cell content"
}}

Requirements:
- Include setup/import cell
- Include documentation cells
- Include execution cells
- Include results visualization if applicable
"""

        result = await client.code_assist("", prompt)

        if result.get("success"):
            # Parse notebook cells from response
            response_text = result.get("response", "")
            try:
                # Extract JSON from response
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0]
                else:
                    json_str = response_text

                cells = json.loads(json_str)
                return {"success": True, "cells": cells}
            except json.JSONDecodeError:
                return {"success": True, "raw_response": response_text}

        return result

    def scale_accounts(self, new_count: int) -> None:
        """Scale the number of active accounts.

        Args:
            new_count: New account count (1-10)

        """
        new_count = max(1, min(new_count, 10))

        if new_count != self.num_accounts:
            old_count = self.num_accounts
            self.num_accounts = new_count
            self.pool = CloudCodePool(num_accounts=new_count)
            print(f"///▞ COLAB COOP :: Scaled {old_count} → {new_count} accounts")

    def get_stats(self) -> dict[str, Any]:
        """Get cooperative execution statistics."""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()

        return {
            "accounts_active": len(self.pool.clients),
            "strategy": self.strategy.value,
            "tasks_distributed": self.stats["tasks_distributed"],
            "tasks_completed": self.stats["tasks_completed"],
            "tasks_failed": self.stats["tasks_failed"],
            "success_rate": (
                self.stats["tasks_completed"] / max(self.stats["tasks_distributed"], 1)
            ),
            "by_account": self.stats["by_account"],
            "uptime_seconds": uptime,
            "pool_stats": self.pool.get_pool_stats(),
        }


# Convenience function for quick coop setup
def create_coop(num_accounts: int = 1, strategy: str = "round_robin") -> ColabCoop:
    """Create a ColabCoop instance with specified configuration."""
    strategy_enum = CoopStrategy(strategy)
    return ColabCoop(num_accounts=num_accounts, strategy=strategy_enum)


# Standalone test
if __name__ == "__main__":

    async def main():
        # Start with single account
        coop = ColabCoop(num_accounts=1)

        # Test single cell execution
        result = await coop.execute_cell("""
import numpy as np
data = np.random.rand(100)
print(f"Mean: {data.mean():.4f}")
""")
        print("Single cell:", result)

        # Test notebook generation
        notebook = await coop.generate_notebook(
            "Create a notebook that loads a CSV file and generates basic statistics",
        )
        print("Generated notebook:", notebook)

        # Test minions routing
        fm_result = await coop.route_to_minions("Analyze this data pattern")
        print("minions:", fm_result)

        # Print stats
        print("\nStats:", json.dumps(coop.get_stats(), indent=2, default=str))

        # Scale up demo
        print("\n--- Scaling to 3 accounts ---")
        coop.scale_accounts(3)
        print("Stats after scale:", json.dumps(coop.get_stats(), indent=2, default=str))

    asyncio.run(main())
