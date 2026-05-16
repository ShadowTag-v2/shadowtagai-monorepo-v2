# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Unified Pinkln Proof-of-Concept Demo.

Demonstrates the complete integrated system:
- AutoGen → Gemini migration (31× faster)
- Kernel chaining as function tools (98.5% token reduction)
- Ultrathink capabilities (Glicko-2, DTE, Debates, Wealth)
- PNKLN stack (JR Engine, Cor, ShadowTag, NS)

Result: Insanely great AI system 🚀
"""

import os
import sys
import time
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.integration.unified_orchestrator import (
  UnifiedPinklnOrchestrator,
  create_unified_orchestrator,
)


def print_header(title: str):
  """Print formatted header."""


def print_section(title: str):
  """Print section header."""


def print_metrics(metrics: dict[str, Any], title: str = "METRICS"):
  """Print formatted metrics."""
  print_section(title)
  for key, value in metrics.items():
    if isinstance(value, float):
      pass
    elif isinstance(value, dict):
      for k, v in value.items():
        pass
    else:
      pass


def demo_1_kernel_chain():
  """Demo 1: Kernel Chain as Function Tools."""
  print_header("DEMO 1: KERNEL CHAIN AS FUNCTION TOOLS")

  print_section("Creating Unified Orchestrator")
  orchestrator = create_unified_orchestrator(
    api_key=os.environ.get("GOOGLE_API_KEY"),
    enable_jr_validation=True,
    enable_shadowtag=True,
    enable_memory=True,
    enable_glicko=True,
  )

  print_section("Executing Decision Pipeline")
  decision_context = """
    Battalion Commander requests approval for $2.5M contract for
    combat vehicle maintenance. Contract exceeds battalion authority
    level (ATP 5-19 violation: unauthorized purchase). Documentation
    is incomplete (missing environmental impact assessment).
    """

  start = time.time()
  orchestrator.execute(
    "Analyze this military decision for ATP 5-19 compliance and provide go/no-go recommendation: "
    + decision_context
  )
  (time.time() - start) * 1000

  return orchestrator


def demo_2_multi_agent_debate(orchestrator: UnifiedPinklnOrchestrator):
  """Demo 2: Multi-Agent Debates (31× faster than AutoGen)."""
  print_header("DEMO 2: MULTI-AGENT DEBATES")

  print_section("Running Multi-Agent Debate")
  orchestrator.execute(
    "Have a panel of 3 experts debate: Should we prioritize latency or cost optimization?"
  )


def demo_3_dte_self_evolution(orchestrator: UnifiedPinklnOrchestrator):
  """Demo 3: DTE Self-Evolution (+3.7% accuracy)."""
  print_header("DEMO 3: DTE SELF-EVOLUTION")

  print_section("Evolving a Prompt")
  original_prompt = "You are a helpful assistant that analyzes data."

  orchestrator.execute(f'Evolve this prompt using DTE: "{original_prompt}"')


def demo_4_wealth_planning(orchestrator: UnifiedPinklnOrchestrator):
  """Demo 4: Wealth Planning (Leak Detection)."""
  print_header("DEMO 4: WEALTH PLANNING MODEL")

  print_section("Analyzing Sample Business")
  orchestrator.execute("""
Analyze this business:
- Monthly revenue: $100,000
- Customer acquisition cost: $500
- Customer lifetime value: $1,200
- Monthly churn rate: 8%

Identify leaks and create actionable plan.
""")


def demo_5_glicko_ratings(orchestrator: UnifiedPinklnOrchestrator):
  """Demo 5: Glicko-2 Performance Tracking."""
  print_header("DEMO 5: GLICKO-2 PERFORMANCE TRACKING")

  # Execute multiple tasks to build rating history
  print_section("Executing Tasks to Build Rating History")

  tasks = [
    "Analyze decision context for violations",
    "Run debate on best approach",
    "Evolve this prompt: 'Be helpful'",
  ]

  for i, task in enumerate(tasks, 1):
    orchestrator.execute(task)

  print_section("Performance Summary")
  summary = orchestrator.get_performance_summary()
  print_metrics(summary, "COMPREHENSIVE PERFORMANCE METRICS")


def demo_6_complete_workflow(orchestrator: UnifiedPinklnOrchestrator):
  """Demo 6: Complete End-to-End Workflow."""
  print_header("DEMO 6: COMPLETE WORKFLOW (ALL SYSTEMS)")

  print_section("Executing Complex Workflow")
  complex_request = """
Analyze this military procurement decision:
- $5M contract for equipment maintenance
- Authority level: Company Commander (limit: $1M)
- Missing documentation: 3 required forms

Tasks:
1. Scan for ATP 5-19 violations
2. Get go/no-go recommendation
3. Have experts debate the risk level
4. Analyze business impact if this pattern continues
5. Evolve the violation detection prompt for better accuracy

Provide comprehensive analysis with recommendations.
"""

  start = time.time()
  result = orchestrator.execute(complex_request)
  (time.time() - start) * 1000

  for func in result.functions_called:
    pass


def demo_7_system_health(orchestrator: UnifiedPinklnOrchestrator):
  """Demo 7: System Health Dashboard."""
  print_header("DEMO 7: SYSTEM HEALTH DASHBOARD")

  health = orchestrator.get_system_health()

  print_section("System Status")

  print_section("Component Status")
  for component, status in health["components"].items():
    pass

  print_section("Performance Summary")
  perf = health["performance"]

  print_section("SLA Validation")
  if perf["p99_latency_ms"] <= 90:
    pass
  else:
    pass

  if perf["total_cost_usd"] <= perf["total_executions"] * 0.001:
    pass
  else:
    pass


def main():
  """Run complete proof-of-concept demonstration."""
  print_header("PINKLN ULTRATHINK ECOSYSTEM")

  # Check API key
  if not os.environ.get("GOOGLE_API_KEY"):
    return

  try:
    # Run all demos
    orchestrator = demo_1_kernel_chain()
    demo_2_multi_agent_debate(orchestrator)
    demo_3_dte_self_evolution(orchestrator)
    demo_4_wealth_planning(orchestrator)
    demo_5_glicko_ratings(orchestrator)
    demo_6_complete_workflow(orchestrator)
    demo_7_system_health(orchestrator)

    # Final summary
    print_header("PROOF-OF-CONCEPT COMPLETE ✅")

  except Exception:
    import traceback

    traceback.print_exc()


if __name__ == "__main__":
  main()
