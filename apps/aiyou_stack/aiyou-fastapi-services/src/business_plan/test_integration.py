#!/usr/bin/env python3
"""Integration tests for business plan module
Validates all components work together correctly
"""

import json

from . import BUSINESS_METRICS, CONTEXT_RESTORATION, TECH_STACK, UNIT_ECONOMICS, KillSwitches
from .decision_framework import RiskAssessment
from .verticals import get_current_focus, get_total_mrr


def test_metrics_validation():
    """Test business metrics pass validation"""
    assert BUSINESS_METRICS.validate(), "Business metrics failed validation"
    print("✅ Business metrics validation passed")


def test_unit_economics():
    """Test unit economics meet bootstrap constraints"""
    ltv = UNIT_ECONOMICS.lifetime_value
    cac = UNIT_ECONOMICS.customer_acquisition_cost
    ratio = ltv / cac
    assert ratio >= 4.0, f"LTV:CAC ratio {ratio:.2f} below minimum 4.0"
    print(f"✅ Unit economics passed (LTV:CAC = {ratio:.2f}:1)")


def test_verticals_totals():
    """Test vertical revenue totals"""
    total = get_total_mrr()
    assert total > 0, "Total MRR is zero"
    print(f"✅ Total MRR: ${total:,}")


def test_current_focus():
    """Test priority 1 vertical is Sales Automation"""
    focus = get_current_focus()
    assert focus.name == "Sales Automation Agent", "Wrong priority 1 vertical"
    assert focus.priority == 1, "Priority mismatch"
    print(f"✅ Current focus: {focus.name} (Priority {focus.priority})")


def test_kill_switches():
    """Test kill-switch logic"""
    # Should pass
    should_kill, _ = KillSwitches.evaluate(month=3, mrr=12_000, pilots=5)
    assert not should_kill, "Month 3 gate failed incorrectly"

    # Should fail
    should_kill, reason = KillSwitches.evaluate(month=3, mrr=8_000, pilots=3)
    assert should_kill, "Month 3 gate passed incorrectly"
    print(f"✅ Kill-switch logic working (failed correctly: {reason})")


def test_risk_assessment():
    """Test ATP 5-19 risk matrix"""
    risk_assessor = RiskAssessment()

    # High risk scenario
    risk = risk_assessor.assess("A", "I")  # Frequent + Catastrophic
    action = risk_assessor.get_action_gate(risk)
    assert "BLOCK" in action, "EH risk not blocked"

    # Low risk scenario
    risk = risk_assessor.assess("E", "IV")  # Unlikely + Negligible
    action = risk_assessor.get_action_gate(risk)
    assert action == "ALLOW", "Low risk not allowed"

    print("✅ Risk assessment matrix working")


def test_tech_stack():
    """Test tech stack configuration"""
    assert TECH_STACK.core_language == "Python 3.11+"
    assert "LangGraph" in TECH_STACK.orchestration
    assert TECH_STACK.cloud_provider == "Google Cloud Platform (exclusive)"
    print("✅ Tech stack configured correctly")


def test_context_restoration():
    """Test context can be exported"""
    prompt = CONTEXT_RESTORATION.generate_restart_prompt()
    assert len(prompt) > 1000, "Restart prompt too short"
    assert "Week 1" in prompt, "Missing Week 1 context"
    assert "$120K MRR" in prompt or "120_000" in prompt, "Missing MRR target"
    print(f"✅ Context restoration ready ({len(prompt)} chars)")


def test_json_export():
    """Test full export works"""
    from .cli import export_all

    data = export_all()

    assert "metadata" in data
    assert "business_metrics" in data
    assert "verticals" in data
    assert data["total_mrr"] > 0

    # Validate JSON serializable
    json_str = json.dumps(data, indent=2)
    assert len(json_str) > 0

    print(f"✅ JSON export working ({len(json_str)} bytes)")


def run_all_tests():
    """Execute all integration tests"""
    print("=" * 70)
    print("BUSINESS PLAN MODULE - INTEGRATION TESTS")
    print("=" * 70)
    print()

    tests = [
        test_metrics_validation,
        test_unit_economics,
        test_verticals_totals,
        test_current_focus,
        test_kill_switches,
        test_risk_assessment,
        test_tech_stack,
        test_context_restoration,
        test_json_export,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            failed += 1

    print()
    print("=" * 70)
    if failed == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {failed}/{len(tests)} TESTS FAILED")
    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    import sys

    success = run_all_tests()
    sys.exit(0 if success else 1)
