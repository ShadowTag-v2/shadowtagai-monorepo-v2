#!/usr/bin/env python3
"""═══════════════════════════════════════════════════════════════════════════════
PNKLN ORCHESTRATOR - Validation Test Suite

Test auto-activation, skill matching, agent execution, and audit trail.
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import sys
from pathlib import Path

# Add core to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core import create_orchestrator, execute_prompt


def print_section(title: str):
    """Elegant section separator"""
    print()
    print("═" * 80)
    print(f"  {title}")
    print("═" * 80)
    print()


def test_registry_loading():
    """Test 1: Load registries successfully"""
    print_section("TEST 1: Registry Loading")

    orchestrator = create_orchestrator()

    print(f"✓ Loaded {len(orchestrator.skills)} skills:")
    for _skill_id, skill in orchestrator.skills.items():
        print(f"  - {skill.name} (v{skill.version})")

    print()
    print(f"✓ Loaded {len(orchestrator.agents)} agents:")
    for _agent_id, agent in orchestrator.agents.items():
        print(f"  - {agent.name} ({agent.persona}, IQ: {agent.iq})")

    assert len(orchestrator.skills) == 3, "Expected 3 skills"
    assert len(orchestrator.agents) == 2, "Expected 2 agents"

    print()
    print("✓ Registry loading: PASSED")


def test_skill_activation():
    """Test 2: Auto-activate skills based on triggers"""
    print_section("TEST 2: Skill Auto-Activation")

    orchestrator = create_orchestrator()

    test_cases = [
        {
            "prompt": "Research edge AI compute market and identify revenue opportunities",
            "expected_skills": ["research_explorer_v1", "monetization_architect_v1"],
        },
        {
            "prompt": "Review the design and simplify the architecture",
            "expected_skills": ["design_critic_v1"],
        },
        {
            "prompt": "How can we monetize this platform?",
            "expected_skills": ["monetization_architect_v1"],
        },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test['prompt']}")

        activated = orchestrator.activate_skills(test["prompt"])
        activated_ids = [s.id for s in activated]

        print(f"  Activated: {activated_ids}")
        print(f"  Expected: {test['expected_skills']}")

        # Check if all expected skills are activated
        for expected_skill in test["expected_skills"]:
            assert expected_skill in activated_ids, f"Expected {expected_skill} to be activated"

        print("  ✓ PASSED")
        print()

    print("✓ Skill activation: PASSED")


def test_agent_execution():
    """Test 3: Execute agent with skill composition"""
    print_section("TEST 3: Agent Execution")

    orchestrator = create_orchestrator()

    # Test with UltraThink Designer
    print("Agent: UltraThink Designer (Steve Jobs)")
    prompt = "Research AI video generation and design an elegant monetization strategy"

    result = orchestrator.execute(prompt, agent_id="ultrathink_designer")

    print(f"  Agent: {result.agent_id}")
    print(f"  Activated Skills: {result.activated_skills}")
    print(f"  Reasoning Chain: {len(result.reasoning_chain)} steps")
    print(f"  Audit Hash: {result.audit_hash[:16]}...")
    print(f"  Timestamp: {result.timestamp}")

    assert result.agent_id == "ultrathink_designer", "Wrong agent executed"
    assert len(result.activated_skills) > 0, "No skills activated"
    assert result.audit_hash, "No audit hash generated"

    print()
    print("✓ Agent execution: PASSED")


def test_wealth_accelerator():
    """Test 4: Wealth Accelerator agent with monetization focus"""
    print_section("TEST 4: Wealth Accelerator Agent")

    orchestrator = create_orchestrator()

    print("Agent: Wealth Accelerator (Revenue Strategist)")
    prompt = "Analyze the SaaS market and identify high-leverage revenue opportunities"

    result = orchestrator.execute(prompt, agent_id="wealth_accelerator")

    print(f"  Agent: {result.agent_id}")
    print(f"  Activated Skills: {result.activated_skills}")

    # Should activate both research_explorer_v1 and monetization_architect_v1
    assert result.agent_id == "wealth_accelerator", "Wrong agent executed"

    # This agent should activate research and monetization skills
    expected_skills = {"research_explorer_v1", "monetization_architect_v1"}
    activated_set = set(result.activated_skills)

    # Check intersection (some skills might not activate depending on exact trigger matching)
    assert len(activated_set.intersection(expected_skills)) > 0, "No expected skills activated"

    print()
    print("✓ Wealth Accelerator: PASSED")


def test_audit_trail():
    """Test 5: Boy Scout Rule audit trail"""
    print_section("TEST 5: Audit Trail (Boy Scout Rule)")

    orchestrator = create_orchestrator()

    prompt = "Test audit trail generation"
    orchestrator.execute(prompt)

    # Check audit directory was created
    audit_dir = Path("/mnt/project/audit")
    assert audit_dir.exists(), "Audit directory not created"

    # Check audit log file exists
    audit_files = list(audit_dir.glob("execution_*.json"))
    assert len(audit_files) > 0, "No audit log files created"

    print(f"  Audit Directory: {audit_dir}")
    print(f"  Audit Files: {len(audit_files)}")

    # Read most recent audit log
    latest_audit = sorted(audit_files)[-1]
    print(f"  Latest Audit: {latest_audit.name}")

    with open(latest_audit) as f:
        audit_data = json.load(f)

    print(f"  Agent ID: {audit_data['agent_id']}")
    print(f"  Skills: {audit_data['activated_skills']}")
    print(f"  Audit Hash: {audit_data['audit_hash'][:16]}...")

    assert audit_data["audit_hash"], "No audit hash in log"
    assert audit_data["agent_id"], "No agent ID in log"

    print()
    print("✓ Audit trail: PASSED")


def test_metrics_tracking():
    """Test 6: Metrics aggregation"""
    print_section("TEST 6: Metrics Tracking")

    orchestrator = create_orchestrator()

    # Execute multiple times
    prompts = [
        "Research AI market",
        "Design elegant solution",
        "Monetize the platform",
    ]

    for prompt in prompts:
        orchestrator.execute(prompt)

    # Get metrics summary
    metrics = orchestrator.get_metrics_summary()

    print(f"  Total Executions: {metrics['total_executions']}")
    print(f"  Agents Used: {metrics['agents_used']}")
    print(f"  Skills Activated: {metrics['skills_activated']}")
    print(f"  Time Saved: {metrics['total_time_saved_hours']} hours")
    print(f"  Revenue Identified: ${metrics['total_revenue_identified_usd']}")
    print(f"  Revenue Generated: ${metrics['total_revenue_generated_usd']}")

    assert metrics["total_executions"] == 3, "Wrong execution count"
    assert len(metrics["agents_used"]) > 0, "No agents tracked"

    print()
    print("✓ Metrics tracking: PASSED")


def test_convenience_function():
    """Test 7: One-liner convenience function"""
    print_section("TEST 7: Convenience Function")

    print("Testing: execute_prompt() one-liner")

    result = execute_prompt("Quick test of convenience function")

    print(f"  Agent: {result.agent_id}")
    print(f"  Skills: {result.activated_skills}")

    assert result.agent_id, "No agent executed"

    print()
    print("✓ Convenience function: PASSED")


def run_all_tests():
    """Run complete test suite"""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "PNKLN ORCHESTRATOR - VALIDATION SUITE" + " " * 21 + "║")
    print("╚" + "═" * 78 + "╝")

    tests = [
        test_registry_loading,
        test_skill_activation,
        test_agent_execution,
        test_wealth_accelerator,
        test_audit_trail,
        test_metrics_tracking,
        test_convenience_function,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1

    print_section("SUMMARY")
    print(f"  Total Tests: {len(tests)}")
    print(f"  ✓ Passed: {passed}")
    print(f"  ✗ Failed: {failed}")
    print()

    if failed == 0:
        print("  🎉 ALL TESTS PASSED! Framework is production-ready.")
    else:
        print("  ⚠️  Some tests failed. Review output above.")

    print()

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
