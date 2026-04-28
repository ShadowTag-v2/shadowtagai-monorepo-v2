# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import asyncio
import os
import sys

import httpx


async def verify_infrastructure():
    print("///▞ VERIFYING PHASE 1: INFRASTRUCTURE & HEALTH CHECKS")

    # 1. Test /health
    async with httpx.AsyncClient():
        try:
            print("\n1. Testing /health...")
            # We assume the server is NOT running, so we'll test the logic by mocking the app and calling it
            # But wait, I can just use TestClient from fastapi if I want to be thorough
            from fastapi.testclient import TestClient
            from src.shadowtag_v4.main import app

            with TestClient(app) as test_client:
                response = test_client.get("/health")
                print(f"Health Response: {response.status_code} - {response.json()}")
                assert response.status_code == 200
                assert response.json()["status"] == "healthy"

                print("\n2. Testing /status (Detailed Health)...")
                response = test_client.get("/status")
                data = response.json()
                print(f"Status Response: {json.dumps(data, indent=2)}")
                assert "components" in data
                assert "database" in data["components"]
                assert "cache" in data["components"]

                print("\n3. Testing COR Orchestrator Async Execution...")
                from src.orchestrator.deploy_03_cor_orchestrator import (
                    COROrchestrator,
                    OrchestrationPlan,
                )

                orchestrator = COROrchestrator(project_id="test-project")
                plan = OrchestrationPlan(
                    steps=[
                        {"action": "validate", "condition": "p99 < 50ms"},
                        {"action": "aggregate", "sources": ["s1", "s2"], "strategy": "consensus"},
                    ],
                    validation_rules=[],
                    estimated_duration_seconds=5,
                    resource_requirements={},
                )

                results = await orchestrator.execute_plan_async(plan)
                print(f"Orchestrator Success: {results['success']}")
                assert results["success"] is True
                assert len(results["results"]) == 2

            print("\n✅ PHASE 1 VERIFIED: Infrastructure & Core Services operational.")
            return True
        except Exception as e:
            print(f"\n❌ VERIFICATION FAILED: {e!s}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    import json

    # Ensure PYTHONPATH is correct
    sys.path.append(os.getcwd())
    success = asyncio.run(verify_infrastructure())
    sys.exit(0 if success else 1)
