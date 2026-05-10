#!/usr/bin/env python3
"""
Colab Bootstrap: Initialize Colab Coop environment.
Sets up Cloud Code API, n-autoresearch/Kosmos/BioAgents connection, and account rotation.

Usage:
    python scripts/colab_bootstrap.py              # Start with 1 account
    python scripts/colab_bootstrap.py --accounts 3 # Start with 3 accounts
    python scripts/colab_bootstrap.py --test       # Run verification tests

Part of Cloud Code API + Colab automation stack.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.cloudcode_client import CloudCodeClient
from agents.colab_coop import ColabCoop
from agents.colab_notebook_runner import ColabNotebookRunner, ExecutionMode


class ColabBootstrap:
    """
    Initialize and verify Colab Coop environment.
    """

    def __init__(self, num_accounts: int = 1):
        """
        Initialize bootstrap with target account count.

        Args:
            num_accounts: Number of accounts to initialize (1-10)
        """
        self.num_accounts = min(num_accounts, 10)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "accounts_requested": self.num_accounts,
            "accounts_initialized": 0,
            "checks": {},
            "errors": [],
        }

        print("=" * 60)
        print("///▞ COLAB BOOTSTRAP :: Initializing Colab Coop Environment")
        print("=" * 60)

    def check_environment(self) -> dict[str, Any]:
        """Check environment variables and dependencies."""
        checks = {"api_keys": [], "dependencies": [], "n-autoresearch/Kosmos/BioAgents": False, "directories": []}

        # Check API keys
        print("\n[1/4] Checking API keys...")
        for i in range(1, self.num_accounts + 1):
            key_name = f"GEMINI_KEY_{i}"
            key = os.getenv(key_name)
            if key:
                checks["api_keys"].append(
                    {
                        "account": i,
                        "key_name": key_name,
                        "status": "found",
                        "prefix": key[:8] + "...",
                    }
                )
                print(f"  ✓ {key_name}: Found ({key[:8]}...)")
            else:
                # Fall back to GEMINI_API_KEY
                fallback = os.getenv("GEMINI_API_KEY")
                if fallback:
                    checks["api_keys"].append(
                        {
                            "account": i,
                            "key_name": "GEMINI_API_KEY (fallback)",
                            "status": "fallback",
                        }
                    )
                    print(f"  ~ {key_name}: Using GEMINI_API_KEY fallback")
                else:
                    checks["api_keys"].append(
                        {"account": i, "key_name": key_name, "status": "missing"}
                    )
                    print(f"  ✗ {key_name}: Missing")

        # Check dependencies
        print("\n[2/4] Checking dependencies...")
        dependencies = [
            ("google.generativeai", "google-generativeai"),
            ("aiohttp", "aiohttp"),
            ("requests", "requests"),
        ]

        for module_name, pip_name in dependencies:
            try:
                __import__(module_name)
                checks["dependencies"].append({"module": module_name, "status": "installed"})
                print(f"  ✓ {module_name}")
            except ImportError:
                checks["dependencies"].append(
                    {"module": module_name, "pip_name": pip_name, "status": "missing"}
                )
                print(f"  ✗ {module_name} (pip install {pip_name})")

        # Check optional dependencies
        optional_deps = [("playwright", "playwright"), ("e2b", "e2b")]
        for module_name, pip_name in optional_deps:
            try:
                __import__(module_name)
                print(f"  ✓ {module_name} (optional)")
            except ImportError:
                print(f"  ~ {module_name} not installed (optional)")

        # Check n-autoresearch/Kosmos/BioAgents
        print("\n[3/4] Checking n-autoresearch/Kosmos/BioAgents server...")
        n-autoresearch/Kosmos/BioAgents_url = os.getenv("n-autoresearch/Kosmos/BioAgents_URL", "http://localhost:8600")
        try:
            import requests

            response = requests.get(f"{n-autoresearch/Kosmos/BioAgents_url}/health", timeout=5)
            if response.status_code == 200:
                health = response.json()
                checks["n-autoresearch/Kosmos/BioAgents"] = True
                print(f"  ✓ n-autoresearch/Kosmos/BioAgents healthy at {n-autoresearch/Kosmos/BioAgents_url}")
                print(f"    Agents: {health.get('agents_available', 'unknown')}")
                print(f"    Uptime: {health.get('uptime_minutes', 0):.1f} min")
            else:
                print(f"  ✗ n-autoresearch/Kosmos/BioAgents returned {response.status_code}")
        except Exception as e:
            print(f"  ✗ n-autoresearch/Kosmos/BioAgents not reachable: {e}")

        # Check directories
        print("\n[4/4] Checking directories...")
        required_dirs = [
            Path(__file__).parent.parent / "agents",
            Path(__file__).parent.parent / "templates",
        ]

        for dir_path in required_dirs:
            if dir_path.exists():
                checks["directories"].append({"path": str(dir_path), "status": "exists"})
                print(f"  ✓ {dir_path}")
            else:
                checks["directories"].append({"path": str(dir_path), "status": "missing"})
                print(f"  ✗ {dir_path} (creating...)")
                dir_path.mkdir(parents=True, exist_ok=True)

        self.results["checks"] = checks
        return checks

    async def initialize_clients(self) -> list[CloudCodeClient]:
        """Initialize Cloud Code clients."""
        print("\n" + "=" * 60)
        print("///▞ Initializing Cloud Code Clients")
        print("=" * 60)

        clients = []
        for i in range(1, self.num_accounts + 1):
            try:
                client = CloudCodeClient(account_id=i)
                if client.api_key:
                    clients.append(client)
                    print(f"  ✓ Account {i}: Initialized")
                else:
                    print(f"  ✗ Account {i}: No API key")
            except Exception as e:
                print(f"  ✗ Account {i}: {e}")
                self.results["errors"].append(f"Account {i}: {str(e)}")

        self.results["accounts_initialized"] = len(clients)
        return clients

    async def run_verification(self) -> dict[str, Any]:
        """Run verification tests on the stack."""
        print("\n" + "=" * 60)
        print("///▞ Running Verification Tests")
        print("=" * 60)

        verification = {
            "cloud_code_test": None,
            "coop_test": None,
            "runner_test": None,
            "n-autoresearch/Kosmos/BioAgents_test": None,
        }

        # Test 1: Cloud Code API
        print("\n[Test 1] Cloud Code API...")
        try:
            client = CloudCodeClient(account_id=1)
            if client.model:
                result = await client.code_assist(
                    context="x = 1", instruction="What is the value of x?"
                )
                verification["cloud_code_test"] = {
                    "success": result.get("success", False),
                    "response_length": len(result.get("response", "")),
                    "account_id": result.get("account_id"),
                }
                print(
                    f"  ✓ Cloud Code API working (response: {len(result.get('response', ''))} chars)"
                )
            else:
                verification["cloud_code_test"] = {"success": False, "error": "No API key"}
                print("  ✗ Cloud Code API: No API key configured")
        except Exception as e:
            verification["cloud_code_test"] = {"success": False, "error": str(e)}
            print(f"  ✗ Cloud Code API: {e}")

        # Test 2: Colab Coop
        print("\n[Test 2] Colab Coop...")
        try:
            coop = ColabCoop(num_accounts=1)
            result = await coop.execute_cell("print('Hello from Coop!')")
            verification["coop_test"] = {
                "success": result.success,
                "account_id": result.account_id,
                "duration_ms": result.duration_ms,
            }
            print(f"  ✓ Colab Coop working (account: {result.account_id})")
        except Exception as e:
            verification["coop_test"] = {"success": False, "error": str(e)}
            print(f"  ✗ Colab Coop: {e}")

        # Test 3: Notebook Runner
        print("\n[Test 3] Notebook Runner...")
        try:
            runner = ColabNotebookRunner(mode=ExecutionMode.LOCAL)
            result = await runner.run("print('Hello from Runner!')")
            verification["runner_test"] = {
                "success": result.success,
                "mode": result.execution_mode.value,
                "duration": result.duration_seconds,
            }
            print(f"  ✓ Notebook Runner working (mode: {result.execution_mode.value})")
        except Exception as e:
            verification["runner_test"] = {"success": False, "error": str(e)}
            print(f"  ✗ Notebook Runner: {e}")

        # Test 4: n-autoresearch/Kosmos/BioAgents routing
        print("\n[Test 4] n-autoresearch/Kosmos/BioAgents routing...")
        try:
            client = CloudCodeClient(account_id=1)
            result = await client.route_to_n-autoresearch/Kosmos/BioAgents("test ping")
            verification["n-autoresearch/Kosmos/BioAgents_test"] = {
                "success": result.get("success", False),
                "source": result.get("source"),
            }
            if result.get("success"):
                print("  ✓ n-autoresearch/Kosmos/BioAgents routing working")
            else:
                print("  ~ n-autoresearch/Kosmos/BioAgents routing failed (server may be down)")
        except Exception as e:
            verification["n-autoresearch/Kosmos/BioAgents_test"] = {"success": False, "error": str(e)}
            print(f"  ✗ n-autoresearch/Kosmos/BioAgents routing: {e}")

        self.results["verification"] = verification
        return verification

    def generate_report(self) -> str:
        """Generate bootstrap report."""
        report = []
        report.append("\n" + "=" * 60)
        report.append("///▞ COLAB BOOTSTRAP REPORT")
        report.append("=" * 60)

        report.append(f"\nTimestamp: {self.results['timestamp']}")
        report.append(f"Accounts Requested: {self.results['accounts_requested']}")
        report.append(f"Accounts Initialized: {self.results['accounts_initialized']}")

        # API Keys summary
        checks = self.results.get("checks", {})
        api_keys = checks.get("api_keys", [])
        found = sum(1 for k in api_keys if k.get("status") in ["found", "fallback"])
        report.append(f"\nAPI Keys: {found}/{len(api_keys)}")

        # Dependencies summary
        deps = checks.get("dependencies", [])
        installed = sum(1 for d in deps if d.get("status") == "installed")
        report.append(f"Dependencies: {installed}/{len(deps)}")

        # n-autoresearch/Kosmos/BioAgents
        report.append(
            f"n-autoresearch/Kosmos/BioAgents: {'Connected' if checks.get('n-autoresearch/Kosmos/BioAgents') else 'Not available'}"
        )

        # Verification summary
        verification = self.results.get("verification", {})
        passed = sum(1 for v in verification.values() if v and v.get("success"))
        report.append(f"\nVerification Tests: {passed}/{len(verification)}")

        # Errors
        if self.results["errors"]:
            report.append(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                report.append(f"  - {error}")

        # Status
        all_good = (
            self.results["accounts_initialized"] > 0
            and passed >= 2  # At least cloud_code and runner should work
        )
        report.append("\n" + "=" * 60)
        if all_good:
            report.append("STATUS: READY")
            report.append("Colab Coop environment is ready for use.")
        else:
            report.append("STATUS: ISSUES FOUND")
            report.append("Review errors above and fix configuration.")
        report.append("=" * 60)

        return "\n".join(report)

    async def run(self, run_tests: bool = True) -> dict[str, Any]:
        """
        Run full bootstrap process.

        Args:
            run_tests: Whether to run verification tests

        Returns:
            Bootstrap results
        """
        # Check environment
        self.check_environment()

        # Initialize clients
        await self.initialize_clients()

        # Run verification if requested
        if run_tests:
            await self.run_verification()

        # Generate report
        report = self.generate_report()
        print(report)

        # Save results
        results_path = Path(__file__).parent.parent / "logs" / "bootstrap_results.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        with open(results_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nResults saved to: {results_path}")

        return self.results


def create_example_notebook() -> None:
    """Create example notebook template."""
    template_dir = Path(__file__).parent.parent / "templates"
    template_dir.mkdir(parents=True, exist_ok=True)

    example_notebook = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {"name": "Colab Coop Example"},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
        },
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Colab Coop Example Notebook\n", "Generated by colab_bootstrap.py"],
            },
            {
                "cell_type": "code",
                "source": [
                    "# Setup\n",
                    "import numpy as np\n",
                    "print('NumPy version:', np.__version__)",
                ],
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": [
                    "# Data processing\n",
                    "data = np.random.rand({{DATA_SIZE}})\n",
                    "print(f'Generated {len(data)} samples')",
                ],
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": [
                    "# Statistics\n",
                    "print(f'Mean: {data.mean():.4f}')\n",
                    "print(f'Std: {data.std():.4f}')",
                ],
                "outputs": [],
            },
        ],
    }

    template_path = template_dir / "example_notebook.ipynb"
    with open(template_path, "w") as f:
        json.dump(example_notebook, f, indent=2)
    print(f"Created example template: {template_path}")


async def main():
    parser = argparse.ArgumentParser(description="Initialize Colab Coop environment")
    parser.add_argument(
        "--accounts", "-a", type=int, default=1, help="Number of accounts to initialize (1-10)"
    )
    parser.add_argument("--test", "-t", action="store_true", help="Run verification tests")
    parser.add_argument("--skip-tests", action="store_true", help="Skip verification tests")
    parser.add_argument(
        "--create-template", action="store_true", help="Create example notebook template"
    )

    args = parser.parse_args()

    if args.create_template:
        create_example_notebook()
        return

    bootstrap = ColabBootstrap(num_accounts=args.accounts)
    await bootstrap.run(run_tests=not args.skip_tests)


if __name__ == "__main__":
    asyncio.run(main())
