#!/usr/bin/env python3
"""
Antigravity System Status Dashboard
====================================

Comprehensive status check for all Antigravity components:
- n-autoresearch/Kosmos/BioAgents 650-agent swarm
- Gemini API failover system
- Git repository status
- LLM memory integration
- Service health checks

Usage:
    python3 antigravity_status.py
    python3 antigravity_status.py --json
    python3 antigravity_status.py --watch  # Live monitoring
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any

import requests


class AntigravityStatus:
    """Comprehensive system status checker"""

    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.status = {"timestamp": datetime.now().isoformat(), "components": {}}

    def check_n-autoresearch/Kosmos/BioAgents(self) -> dict[str, Any]:
        """Check n-autoresearch/Kosmos/BioAgents server status"""
        try:
            response = requests.get("http://localhost:8888/health", timeout=5)
            health = response.json()

            # Get detailed status
            try:
                root_response = requests.get("http://localhost:8888/", timeout=5)
                root_data = root_response.json()
            except:
                root_data = {}

            return {
                "status": "✅ OPERATIONAL",
                "port": 8888,
                "health": health,
                "api_key_configured": health.get("api_key_set", False),
                "endpoints": root_data.get("endpoints", []),
                "docs_url": "http://localhost:8888/docs",
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "❌ OFFLINE",
                "port": 8888,
                "message": "Server not running. Start with: ./run_n-autoresearch/Kosmos/BioAgents_api.sh",
            }
        except Exception as e:
            return {"status": "⚠️  ERROR", "error": str(e)}

    def check_gemini_failover(self) -> dict[str, Any]:
        """Check Gemini API failover configuration"""
        try:
            # Check environment variables
            api_keys_str = os.getenv("GEMINI_API_KEYS", "")
            api_keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
            single_key = os.getenv("GEMINI_API_KEY")
            project_id = os.getenv("GCP_PROJECT_ID")

            total_keys = len(api_keys) if api_keys else (1 if single_key else 0)

            # Try to import and check the failover client
            try:
                sys.path.insert(0, os.path.join(self.base_dir, "src"))
                from shadowtag_v4.services.gemini_failover import get_failover_client

                client = get_failover_client()
                metrics = client.get_metrics()
                health = client.health_check()

                return {
                    "status": f"✅ {health['status'].upper()}",
                    "total_api_keys": total_keys,
                    "available_keys": metrics["available_keys"],
                    "vertex_ai_fallback": metrics["vertex_ai_available"],
                    "project_id": project_id or "Not configured",
                    "health": health["status"],
                    "metrics": metrics,
                }
            except ImportError:
                return {
                    "status": "⚠️  MODULE NOT LOADED",
                    "total_api_keys": total_keys,
                    "vertex_ai_configured": bool(project_id),
                    "project_id": project_id or "Not configured",
                    "note": "Failover client not initialized yet",
                }
        except Exception as e:
            return {"status": "❌ ERROR", "error": str(e)}

    def check_git_status(self) -> dict[str, Any]:
        """Check Git repository status"""
        try:
            # Get current branch
            branch = (
                subprocess.check_output(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=self.base_dir,
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )

            # Get commit info
            commit = (
                subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=self.base_dir,
                    stderr=subprocess.DEVNULL,
                )
                .decode()
                .strip()
            )

            # Check for uncommitted changes
            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=self.base_dir, stderr=subprocess.DEVNULL
            ).decode()

            uncommitted = len(status_output.strip().split("\n")) if status_output.strip() else 0

            # Check remote status
            try:
                subprocess.check_output(
                    ["git", "fetch", "--dry-run"],
                    cwd=self.base_dir,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
                remote_status = "✅ Connected"
            except:
                remote_status = "⚠️  Unable to reach remote"

            return {
                "status": "✅ TRACKED" if uncommitted == 0 else "⚠️  UNCOMMITTED CHANGES",
                "branch": branch,
                "commit": commit,
                "uncommitted_files": uncommitted,
                "remote": remote_status,
            }
        except subprocess.CalledProcessError:
            return {"status": "❌ NOT A GIT REPO", "message": "Directory is not a Git repository"}
        except Exception as e:
            return {"status": "❌ ERROR", "error": str(e)}

    def check_llm_memory(self) -> dict[str, Any]:
        """Check LLM memory integration status"""
        try:
            memory_dir = os.path.join(self.base_dir, "erik-hancock-llm-memory")

            if not os.path.exists(memory_dir):
                return {
                    "status": "❌ NOT FOUND",
                    "message": "erik-hancock-llm-memory directory not found",
                }

            # Check for current.json
            current_json = os.path.join(memory_dir, "current.json")
            if os.path.exists(current_json):
                with open(current_json) as f:
                    memory_data = json.load(f)

                total_conversations = len(memory_data.get("conversations", []))
                architectures = len(memory_data.get("architectures", {}))

                return {
                    "status": "✅ INTEGRATED",
                    "total_conversations": total_conversations,
                    "architectures": architectures,
                    "last_updated": memory_data.get("metadata", {}).get("last_updated", "Unknown"),
                    "location": memory_dir,
                }
            else:
                return {
                    "status": "⚠️  NO DATA",
                    "message": "current.json not found. Run: python3 scripts/extract_and_commit.py",
                    "location": memory_dir,
                }
        except Exception as e:
            return {"status": "❌ ERROR", "error": str(e)}

    def check_services(self) -> dict[str, Any]:
        """Check additional services"""
        services = {}

        # Check Redis
        try:
            import redis

            r = redis.Redis(host="localhost", port=6379, decode_responses=True)
            r.ping()
            services["redis"] = {"status": "✅ RUNNING", "port": 6379}
        except:
            services["redis"] = {"status": "❌ OFFLINE", "port": 6379}

        # Check PostgreSQL
        try:
            result = subprocess.run(
                ["pg_isready", "-h", "localhost", "-p", "5432"], capture_output=True, timeout=2
            )
            if result.returncode == 0:
                services["postgresql"] = {"status": "✅ RUNNING", "port": 5432}
            else:
                services["postgresql"] = {"status": "❌ OFFLINE", "port": 5432}
        except:
            services["postgresql"] = {"status": "⚠️  UNKNOWN", "port": 5432}

        return services

    def run_full_check(self) -> dict[str, Any]:
        """Run comprehensive status check"""
        print("🔍 Antigravity System Status Check")
        print("=" * 70)
        print()

        # n-autoresearch/Kosmos/BioAgents
        print("🐵 n-autoresearch/Kosmos/BioAgents 650-Agent Swarm")
        print("-" * 70)
        fm_status = self.check_n-autoresearch/Kosmos/BioAgents()
        self.status["components"]["n-autoresearch/Kosmos/BioAgents"] = fm_status
        self._print_component(fm_status)
        print()

        # Gemini Failover
        print("🔄 Gemini API Failover System")
        print("-" * 70)
        gemini_status = self.check_gemini_failover()
        self.status["components"]["gemini_failover"] = gemini_status
        self._print_component(gemini_status)
        print()

        # Git Status
        print("📦 Git Repository")
        print("-" * 70)
        git_status = self.check_git_status()
        self.status["components"]["git"] = git_status
        self._print_component(git_status)
        print()

        # LLM Memory
        print("🧠 LLM Memory Integration")
        print("-" * 70)
        memory_status = self.check_llm_memory()
        self.status["components"]["llm_memory"] = memory_status
        self._print_component(memory_status)
        print()

        # Additional Services
        print("🔧 Additional Services")
        print("-" * 70)
        services_status = self.check_services()
        self.status["components"]["services"] = services_status
        for service_name, service_data in services_status.items():
            print(f"  {service_name.upper()}: {service_data['status']}")
        print()

        # Overall Status
        print("=" * 70)
        self._print_overall_status()

        return self.status

    def _print_component(self, component: dict[str, Any]):
        """Pretty print component status"""
        for key, value in component.items():
            if key == "status":
                print(f"  Status: {value}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            elif isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")

    def _print_overall_status(self):
        """Print overall system status"""
        components = self.status["components"]

        # Count operational components
        operational = 0
        total = 0

        for comp_name, comp_data in components.items():
            if comp_name == "services":
                for service_data in comp_data.values():
                    total += 1
                    if "✅" in service_data.get("status", ""):
                        operational += 1
            else:
                total += 1
                if "✅" in comp_data.get("status", ""):
                    operational += 1

        health_pct = (operational / total * 100) if total > 0 else 0

        if health_pct == 100:
            overall = "✅ ALL SYSTEMS OPERATIONAL"
        elif health_pct >= 75:
            overall = "⚠️  DEGRADED - SOME COMPONENTS OFFLINE"
        else:
            overall = "❌ CRITICAL - MULTIPLE FAILURES"

        print(f"Overall Status: {overall}")
        print(f"Health: {operational}/{total} components operational ({health_pct:.0f}%)")
        print()
        print(f"Timestamp: {self.status['timestamp']}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Antigravity System Status Dashboard")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--watch", action="store_true", help="Watch mode (refresh every 5s)")
    args = parser.parse_args()

    checker = AntigravityStatus()

    if args.watch:
        try:
            while True:
                os.system("clear" if os.name == "posix" else "cls")
                checker.run_full_check()
                print("\n[Press Ctrl+C to exit]")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n👋 Exiting watch mode...")
            sys.exit(0)
    else:
        status = checker.run_full_check()

        if args.json:
            print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
