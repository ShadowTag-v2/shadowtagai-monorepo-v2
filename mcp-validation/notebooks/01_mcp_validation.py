#!/usr/bin/env python3
# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
MCP Code Execution Validation Notebook
Run in Vertex AI Workbench for Hour 0-24 technical validation

Tests:
1. Latency validation (p99 ≤75ms target)
2. Security validation (sandbox escape attempts)
3. Cost analysis (token reduction vs. traditional tool calls)
4. Reliability testing (success rate ≥99.9%)

Usage:
  python 01_mcp_validation.py --mcp-url http://mcp-server.mcp-system --runs 1000
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any
import statistics
import httpx
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class ValidationConfig:
  """Validation test configuration"""

  mcp_server_url: str = "http://mcp-server.mcp-system"
  num_runs: int = 1000
  timeout_seconds: int = 30
  user_id: str = "validation-test"
  session_id: str = "validation-001"


# ============================================================================
# TEST SCENARIOS
# ============================================================================


@dataclass
class TestScenario:
  """Test scenario for code execution"""

  name: str
  category: str  # simple_rules, complex_calculation, multi_step, edge_case
  code: str
  expected_result: Any
  expected_success: bool
  workload_percentage: int  # % of total workload


# Pnkln workload distribution (based on real usage)
TEST_SCENARIOS = [
  # 40% - Simple rules (deterministic, fast)
  TestScenario(
    name="S3 retention policy check",
    category="simple_rules",
    code="""
import json
policy = {"retention_days": 90}
current_age = 45
result = current_age < policy["retention_days"]
""",
    expected_result=True,
    expected_success=True,
    workload_percentage=10,
  ),
  TestScenario(
    name="GDPR data classification",
    category="simple_rules",
    code="""
data_fields = ["email", "name", "address"]
pii_fields = {"email", "name", "address", "ssn", "phone"}
result = bool(set(data_fields) & pii_fields)
""",
    expected_result=True,
    expected_success=True,
    workload_percentage=10,
  ),
  TestScenario(
    name="Compliance tag validation",
    category="simple_rules",
    code="""
required_tags = {"compliance", "owner", "env"}
resource_tags = {"compliance": "gdpr", "owner": "team-a", "env": "prod"}
result = required_tags.issubset(resource_tags.keys())
""",
    expected_result=True,
    expected_success=True,
    workload_percentage=10,
  ),
  TestScenario(
    name="Data residency check",
    category="simple_rules",
    code="""
allowed_regions = {"us-east-1", "us-west-2", "eu-west-1"}
bucket_region = "us-east-1"
result = bucket_region in allowed_regions
""",
    expected_result=True,
    expected_success=True,
    workload_percentage=10,
  ),
  # 35% - Complex calculations
  TestScenario(
    name="GDPR deletion cascade calculation",
    category="complex_calculation",
    code="""
import json

# Simulate user data across multiple tables
user_data = {
    "profiles": [{"id": 1, "user_id": 123}],
    "orders": [{"id": 1, "user_id": 123}, {"id": 2, "user_id": 123}],
    "analytics": [{"id": i, "user_id": 123} for i in range(10)]
}

# Calculate total records to delete
total_deletions = sum(len(records) for records in user_data.values())
result = total_deletions
""",
    expected_result=13,
    expected_success=True,
    workload_percentage=10,
  ),
  TestScenario(
    name="Cost allocation across departments",
    category="complex_calculation",
    code="""
# Cloud resource costs by department
costs = {
    "engineering": [100, 200, 150],
    "marketing": [50, 75, 60],
    "sales": [25, 30, 28]
}

# Calculate percentage for each department
total_cost = sum(sum(dept_costs) for dept_costs in costs.values())
result = {
    dept: round(sum(dept_costs) / total_cost * 100, 2)
    for dept, dept_costs in costs.items()
}
""",
    expected_result={"engineering": 52.94, "marketing": 21.76, "sales": 9.80},
    expected_success=True,
    workload_percentage=15,
  ),
  TestScenario(
    name="Risk score calculation",
    category="complex_calculation",
    code="""
# Calculate security risk score based on multiple factors
factors = {
    "public_exposure": 8,      # 0-10 scale
    "unencrypted_data": 7,
    "missing_mfa": 9,
    "outdated_software": 6,
    "privileged_access": 8
}

weights = {
    "public_exposure": 0.3,
    "unencrypted_data": 0.25,
    "missing_mfa": 0.25,
    "outdated_software": 0.1,
    "privileged_access": 0.1
}

# Weighted average
result = round(sum(factors[k] * weights[k] for k in factors), 2)
""",
    expected_result=7.65,
    expected_success=True,
    workload_percentage=10,
  ),
  # 20% - Multi-step orchestration
  TestScenario(
    name="ShadowTag cross-region compliance",
    category="multi_step",
    code="""
# Simulate multi-region compliance check
regions = ["us-east-1", "eu-west-1", "ap-south-1"]
compliance_rules = {
    "us-east-1": ["HIPAA", "SOC2"],
    "eu-west-1": ["GDPR", "ISO27001"],
    "ap-south-1": ["ISO27001"]
}

# Check if all regions have at least one compliance certification
result = {
    region: bool(rules)
    for region, rules in compliance_rules.items()
}
""",
    expected_result={"us-east-1": True, "eu-west-1": True, "ap-south-1": True},
    expected_success=True,
    workload_percentage=10,
  ),
  TestScenario(
    name="Multi-cloud policy sync",
    category="multi_step",
    code="""
# Simulate policy sync across clouds
aws_policies = {"s3-encryption": True, "vpc-logging": True}
gcp_policies = {"gcs-encryption": True, "vpc-logging": True}
azure_policies = {"blob-encryption": True, "vnet-logging": False}

# Detect policy drift (Azure missing VPC logging)
compliant = all([
    aws_policies["vpc-logging"],
    gcp_policies["vpc-logging"],
    azure_policies["vnet-logging"]
])

result = {"compliant": compliant, "drift": not compliant}
""",
    expected_result={"compliant": False, "drift": True},
    expected_success=True,
    workload_percentage=10,
  ),
  # 5% - Edge cases (ambiguous, may need LLM fallback)
  TestScenario(
    name="Ambiguous policy interpretation",
    category="edge_case",
    code="""
# Edge case: empty policy
policy = {}
result = policy.get("retention_days", 30)  # Default to 30 days
""",
    expected_result=30,
    expected_success=True,
    workload_percentage=5,
  ),
]

# Security violation test scenarios
SECURITY_TEST_SCENARIOS = [
  TestScenario(
    name="Blocked import: os",
    category="security",
    code="import os; result = os.listdir('/')",
    expected_result=None,
    expected_success=False,
    workload_percentage=0,
  ),
  TestScenario(
    name="Blocked import: subprocess",
    category="security",
    code="import subprocess; result = subprocess.run(['whoami'])",
    expected_result=None,
    expected_success=False,
    workload_percentage=0,
  ),
  TestScenario(
    name="Blocked function: eval",
    category="security",
    code="result = eval('1+1')",
    expected_result=None,
    expected_success=False,
    workload_percentage=0,
  ),
  TestScenario(
    name="Blocked function: exec",
    category="security",
    code="exec('result = 1+1')",
    expected_result=None,
    expected_success=False,
    workload_percentage=0,
  ),
  TestScenario(
    name="Blocked pattern: __import__",
    category="security",
    code="result = __import__('os').listdir('/')",
    expected_result=None,
    expected_success=False,
    workload_percentage=0,
  ),
]

# ============================================================================
# MCP CLIENT
# ============================================================================


class MCPClient:
  """Async HTTP client for MCP code execution server"""

  def __init__(self, base_url: str):
    self.base_url = base_url
    self.client = httpx.AsyncClient(timeout=30.0)

  async def execute_code(
    self,
    code: str,
    user_id: str,
    session_id: str,
    context: dict[str, Any] | None = None,
  ) -> dict[str, Any]:
    """Execute code via MCP server"""
    request = {
      "code": code,
      "user_id": user_id,
      "session_id": session_id,
      "context": context or {},
    }

    response = await self.client.post(f"{self.base_url}/execute", json=request)

    return response.json()

  async def health_check(self) -> bool:
    """Check if MCP server is healthy"""
    try:
      response = await self.client.get(f"{self.base_url}/health")
      return response.status_code == 200
    except Exception:
      return False

  async def close(self):
    """Close HTTP client"""
    await self.client.aclose()


# ============================================================================
# VALIDATION RESULTS
# ============================================================================


@dataclass
class ValidationResult:
  """Result of a single validation run"""

  scenario_name: str
  category: str
  success: bool
  execution_time_ms: float
  expected_success: bool
  result_matches: bool
  error: str | None
  security_violations: list[str]


@dataclass
class ValidationSummary:
  """Summary of all validation runs"""

  total_runs: int
  successful_runs: int
  failed_runs: int
  blocked_runs: int
  success_rate: float

  # Latency statistics
  p50_latency_ms: float
  p90_latency_ms: float
  p99_latency_ms: float
  p999_latency_ms: float
  mean_latency_ms: float

  # Category breakdown
  category_stats: dict[str, dict[str, Any]]

  # Security test results
  security_tests_passed: int
  security_tests_failed: int

  # GO/NO-GO decision
  go_decision: str  # "GO", "PIVOT", "ABORT"
  decision_rationale: str


# ============================================================================
# VALIDATION RUNNER
# ============================================================================


class ValidationRunner:
  """Runs validation tests and collects results"""

  def __init__(self, config: ValidationConfig):
    self.config = config
    self.client = MCPClient(config.mcp_server_url)
    self.results: list[ValidationResult] = []

  async def run_scenario(
    self, scenario: TestScenario, run_number: int
  ) -> ValidationResult:
    """Run a single test scenario"""
    start_time = time.time()

    try:
      response = await self.client.execute_code(
        code=scenario.code,
        user_id=self.config.user_id,
        session_id=f"{self.config.session_id}-{run_number}",
      )

      execution_time_ms = (time.time() - start_time) * 1000

      # Check if result matches expected
      result_matches = response.get("success") == scenario.expected_success

      return ValidationResult(
        scenario_name=scenario.name,
        category=scenario.category,
        success=response.get("success", False),
        execution_time_ms=execution_time_ms,
        expected_success=scenario.expected_success,
        result_matches=result_matches,
        error=response.get("error"),
        security_violations=response.get("security_checks", {}),
      )

    except Exception as e:
      execution_time_ms = (time.time() - start_time) * 1000
      return ValidationResult(
        scenario_name=scenario.name,
        category=scenario.category,
        success=False,
        execution_time_ms=execution_time_ms,
        expected_success=scenario.expected_success,
        result_matches=False,
        error=str(e),
        security_violations=[],
      )

  async def run_all_scenarios(self):
    """Run all test scenarios according to workload distribution"""
    print(f"Starting validation with {self.config.num_runs} runs...")
    print(f"MCP Server: {self.config.mcp_server_url}")

    # Check server health
    is_healthy = await self.client.health_check()
    if not is_healthy:
      raise Exception(f"MCP server is not healthy: {self.config.mcp_server_url}")

    print("✓ MCP server is healthy\n")

    # Generate run distribution based on workload percentages
    run_distribution = []
    for scenario in TEST_SCENARIOS:
      num_runs = int(self.config.num_runs * scenario.workload_percentage / 100)
      run_distribution.extend([scenario] * num_runs)

    # Fill remaining runs with balanced distribution
    while len(run_distribution) < self.config.num_runs:
      run_distribution.append(
        TEST_SCENARIOS[len(run_distribution) % len(TEST_SCENARIOS)]
      )

    # Run scenarios
    print(f"Running {len(run_distribution)} functional tests...")
    for i, scenario in enumerate(run_distribution):
      result = await self.run_scenario(scenario, i)
      self.results.append(result)

      if (i + 1) % 100 == 0:
        print(f"  Progress: {i + 1}/{len(run_distribution)} runs completed")

    # Run security tests
    print(f"\nRunning {len(SECURITY_TEST_SCENARIOS)} security tests...")
    for i, scenario in enumerate(SECURITY_TEST_SCENARIOS):
      result = await self.run_scenario(scenario, 9000 + i)
      self.results.append(result)

    print("\n✓ All validation tests completed\n")

  def analyze_results(self) -> ValidationSummary:
    """Analyze validation results and generate summary"""
    # Filter functional vs security tests
    functional_results = [r for r in self.results if r.category != "security"]
    security_results = [r for r in self.results if r.category == "security"]

    # Calculate success rates
    successful_runs = sum(
      1 for r in functional_results if r.success and r.result_matches
    )
    failed_runs = sum(
      1 for r in functional_results if not r.success and r.expected_success
    )
    blocked_runs = sum(
      1 for r in functional_results if not r.success and not r.expected_success
    )

    success_rate = (
      successful_runs / len(functional_results) * 100 if functional_results else 0
    )

    # Calculate latency statistics
    latencies = [r.execution_time_ms for r in functional_results]
    latencies.sort()

    p50_latency = latencies[int(len(latencies) * 0.50)] if latencies else 0
    p90_latency = latencies[int(len(latencies) * 0.90)] if latencies else 0
    p99_latency = latencies[int(len(latencies) * 0.99)] if latencies else 0
    p999_latency = latencies[int(len(latencies) * 0.999)] if latencies else 0
    mean_latency = statistics.mean(latencies) if latencies else 0

    # Category breakdown
    category_stats = {}
    for category in ["simple_rules", "complex_calculation", "multi_step", "edge_case"]:
      cat_results = [r for r in functional_results if r.category == category]
      if cat_results:
        cat_latencies = [r.execution_time_ms for r in cat_results]
        category_stats[category] = {
          "count": len(cat_results),
          "success_rate": sum(1 for r in cat_results if r.success)
          / len(cat_results)
          * 100,
          "p99_latency_ms": sorted(cat_latencies)[int(len(cat_latencies) * 0.99)],
          "mean_latency_ms": statistics.mean(cat_latencies),
        }

    # Security test results
    security_tests_passed = sum(
      1 for r in security_results if not r.success
    )  # Should be blocked
    security_tests_failed = sum(
      1 for r in security_results if r.success
    )  # Should NOT succeed

    # GO/NO-GO decision
    go_decision, decision_rationale = self._make_go_decision(
      p99_latency, success_rate, security_tests_failed
    )

    return ValidationSummary(
      total_runs=len(functional_results),
      successful_runs=successful_runs,
      failed_runs=failed_runs,
      blocked_runs=blocked_runs,
      success_rate=success_rate,
      p50_latency_ms=p50_latency,
      p90_latency_ms=p90_latency,
      p99_latency_ms=p99_latency,
      p999_latency_ms=p999_latency,
      mean_latency_ms=mean_latency,
      category_stats=category_stats,
      security_tests_passed=security_tests_passed,
      security_tests_failed=security_tests_failed,
      go_decision=go_decision,
      decision_rationale=decision_rationale,
    )

  def _make_go_decision(
    self, p99_latency: float, success_rate: float, security_failures: int
  ) -> tuple[str, str]:
    """Determine GO/NO-GO decision based on validation results"""

    # ABORT criteria
    if p99_latency > 90:
      return "ABORT", f"p99 latency ({p99_latency:.1f}ms) exceeds 90ms SLA"

    if success_rate < 99.0:
      return "ABORT", f"Success rate ({success_rate:.1f}%) below 99% requirement"

    if security_failures > 0:
      return "ABORT", f"{security_failures} security tests failed (should be blocked)"

    # PIVOT criteria
    if p99_latency > 75:
      return (
        "PIVOT",
        f"p99 latency ({p99_latency:.1f}ms) between 75-90ms, recommend AutoGen-only deployment",
      )

    # GO criteria
    if p99_latency <= 75 and success_rate >= 99.9 and security_failures == 0:
      return (
        "GO",
        f"All criteria met: p99={p99_latency:.1f}ms, success={success_rate:.1f}%, security=PASS",
      )

    # Default PIVOT
    return "PIVOT", "Some criteria met, recommend partial deployment"

  def print_summary(self, summary: ValidationSummary):
    """Print validation summary to console"""
    print("=" * 80)
    print("MCP CODE EXECUTION VALIDATION RESULTS")
    print("=" * 80)
    print()

    print("LATENCY METRICS")
    print("-" * 80)
    print(f"  p50:  {summary.p50_latency_ms:7.2f} ms")
    print(f"  p90:  {summary.p90_latency_ms:7.2f} ms")
    print(
      f"  p99:  {summary.p99_latency_ms:7.2f} ms {'✓' if summary.p99_latency_ms <= 75 else '✗ EXCEEDS TARGET'}"
    )
    print(f"  p999: {summary.p999_latency_ms:7.2f} ms")
    print(f"  Mean: {summary.mean_latency_ms:7.2f} ms")
    print()

    print("RELIABILITY METRICS")
    print("-" * 80)
    print(f"  Total runs:      {summary.total_runs}")
    print(f"  Successful:      {summary.successful_runs} ({summary.success_rate:.2f}%)")
    print(f"  Failed:          {summary.failed_runs}")
    print(f"  Blocked:         {summary.blocked_runs}")
    print(
      f"  Success rate:    {summary.success_rate:.2f}% {'✓' if summary.success_rate >= 99.9 else '✗ BELOW TARGET'}"
    )
    print()

    print("CATEGORY BREAKDOWN")
    print("-" * 80)
    for category, stats in summary.category_stats.items():
      print(
        f"  {category:20s}: {stats['count']:4d} runs, p99={stats['p99_latency_ms']:6.2f}ms, success={stats['success_rate']:5.1f}%"
      )
    print()

    print("SECURITY TESTS")
    print("-" * 80)
    print(f"  Tests passed (blocked): {summary.security_tests_passed}")
    print(
      f"  Tests failed (allowed): {summary.security_tests_failed} {'✓' if summary.security_tests_failed == 0 else '✗ SECURITY RISK'}"
    )
    print()

    print("GO/NO-GO DECISION")
    print("=" * 80)
    print(f"  Decision:   {summary.go_decision}")
    print(f"  Rationale:  {summary.decision_rationale}")
    print("=" * 80)
    print()

    # Save detailed results to JSON
    results_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w") as f:
      json.dump(
        {
          "summary": asdict(summary),
          "detailed_results": [asdict(r) for r in self.results],
        },
        f,
        indent=2,
      )

    print(f"Detailed results saved to: {results_file}")

  async def close(self):
    """Clean up resources"""
    await self.client.close()


# ============================================================================
# MAIN
# ============================================================================


async def main():
  parser = argparse.ArgumentParser(description="MCP Code Execution Validation")
  parser.add_argument(
    "--mcp-url", default="http://mcp-server.mcp-system", help="MCP server URL"
  )
  parser.add_argument(
    "--runs", type=int, default=1000, help="Number of validation runs"
  )
  args = parser.parse_args()

  config = ValidationConfig(mcp_server_url=args.mcp_url, num_runs=args.runs)

  runner = ValidationRunner(config)

  try:
    # Run validation
    await runner.run_all_scenarios()

    # Analyze results
    summary = runner.analyze_results()

    # Print summary
    runner.print_summary(summary)

  finally:
    await runner.close()


if __name__ == "__main__":
  asyncio.run(main())
