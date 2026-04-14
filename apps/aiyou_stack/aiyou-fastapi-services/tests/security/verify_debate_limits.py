import sys
from unittest.mock import MagicMock

# Aggressive Mocking of dependencies missing in environment
sys.modules["prometheus_client"] = MagicMock()
sys.modules["prometheus_client.make_asgi_app"] = MagicMock()
sys.modules["torch"] = MagicMock()

# Mock internal app modules that might import heavy stuff
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class EvolutionStrategy(StrEnum):
    RCR_MAD = "RCR_MAD"
    GRPO = "GRPO"
    BENCHMARK = "BENCHMARK"


class ValidationResult(BaseModel):
    passed: bool = True
    approved_kernels: list[str] = []
    dict: Any = dict


class DecisionContext(BaseModel):
    trace_id: str = "test"
    decision: str = "test"


class DecisionResult(BaseModel):
    trace_id: str = "test"
    decision: str = "test"
    confidence: float = 1.0
    risk_tier: str = "low"
    violations: list[str] = []
    total_latency_ms: float = 0
    total_cost_usd: float = 0


# Create module mocks
sys.modules["app.kernels"] = MagicMock()
sys.modules["app.kernels.base"] = MagicMock()
sys.modules["app.orchestration"] = MagicMock()

# app.validation needs JREngine class
mock_validation = MagicMock()
mock_validation.JREngine.return_value.validate_kernel_chain.return_value = ValidationResult()
sys.modules["app.validation"] = mock_validation

sys.modules["app.monitoring"] = MagicMock()
sys.modules["app.ratings"] = MagicMock()
sys.modules["app.training"] = MagicMock()
sys.modules["app.agents"] = MagicMock()
sys.modules["app.prompts"] = MagicMock()

# app.evolution needs EvolutionStrategy
mock_evolution = MagicMock()
mock_evolution.EvolutionStrategy = EvolutionStrategy
sys.modules["app.evolution"] = mock_evolution

sys.modules["app.wealth"] = MagicMock()

# Mock models.decision
mock_models_decision = MagicMock()
mock_models_decision.DecisionContext = DecisionContext
mock_models_decision.DecisionResult = DecisionResult
sys.modules["app.models"] = MagicMock()
sys.modules["app.models.decision"] = mock_models_decision

# Mock app.config
mock_config = MagicMock()
mock_config.settings.enable_metrics = False
mock_config.settings.service_name = "TestService"
mock_config.settings.max_latency_p99_ms = 1000
mock_config.settings.max_cost_per_decision = 1.0
mock_config.settings.log_level = "INFO"
sys.modules["app.config"] = mock_config

from fastapi.testclient import TestClient

from app.main_ecosystem import app

client = TestClient(app)

print("Verifying debate limits...")

# 1. Valid parameters
try:
    response = client.post("/debate", params={"question": "test", "num_agents": 3, "max_rounds": 3})
    # We accept 200 or 500 (if internal logic fails), just NOT 422
    if response.status_code == 422:
        print("FAIL: Valid request rejected with 422")
        print(response.json())
        sys.exit(1)
    print("PASS: Valid request passed validation")
except Exception as e:
    print(f"WARN: Execution error on valid request: {e}")

# 2. Invalid Agents (>10)
response = client.post("/debate", params={"question": "test", "num_agents": 100, "max_rounds": 3})
if response.status_code != 422:
    print(f"FAIL: Invalid agents accepted with code {response.status_code}")
    sys.exit(1)
print("PASS: Invalid agents rejected")

# 3. Invalid Rounds (>20)
response = client.post("/debate", params={"question": "test", "num_agents": 3, "max_rounds": 100})
if response.status_code != 422:
    print(f"FAIL: Invalid rounds accepted with code {response.status_code}")
    sys.exit(1)
print("PASS: Invalid rounds rejected")

print("ALL TESTS PASSED")
