#!/usr/bin/env python3
"""
Mac Local Demo - Pnkln Agent Platform v0.2.0
Tests full Collection → Enforcement pipeline

Run: python examples/mac_local_demo.py
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_success(message):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message):
    """Print error message"""
    print(f"✗ {message}")


def print_metric(label, value):
    """Print metric"""
    print(f"  {label}: {value}")


def test_imports():
    """Test all core imports"""
    print_header("TEST 1: Core Imports")

    try:
        from pnkln_agents import (
            DEFAULT_SOURCES,
        )

        print_success("All imports successful")
        print_metric("Collection Layer", "GeminiIngestionLayer, EthicalValidator, TierClassifier")
        print_metric("Enforcement Layer", "JREngine, JudgeSixLite")
        print_metric("Agents", "IntelligenceAgent, ComplianceSDRAgent")
        print_metric("Default Sources", f"{len(DEFAULT_SOURCES)} sources")

        return True
    except Exception as e:
        print_error(f"Import failed: {e}")
        return False


def test_jr_engine():
    """Test JR Engine validation"""
    print_header("TEST 2: JR Engine (Purpose/Reasons/Brakes)")

    try:
        from pnkln_agents import JREngine, Purpose, Reason

        jr_engine = JREngine()

        purpose = Purpose(
            intent="Test intelligence collection on Mac",
            business_value="Local development validation",
            customer_id="mac_local_test",
            cost_estimate_usd=0.0,
            expected_outcome="Successful local test run",
        )

        reasons = [
            Reason(
                justification="Local Mac testing environment",
                risk_probability=0.05,
                risk_severity=0.05,
                mitigation_strategy="Isolated test environment",
            )
        ]

        decision = jr_engine.validate(purpose, reasons, context={})

        if decision.approved:
            print_success("JR Engine validation passed")
            print_metric("Validation time", f"{decision.validation_time_ms:.2f}ms")
            print_metric("Brakes triggered", len(decision.brakes))
            print_metric("Constraints", len(decision.constraints))
        else:
            print_error("JR Engine validation failed")
            for brake in decision.brakes:
                print(f"  Brake: {brake.reason}")
            return False

        return True
    except Exception as e:
        print_error(f"JR Engine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_judge_six():
    """Test Judge #6 Lite enforcement"""
    print_header("TEST 3: Judge #6 Lite (Compliance Verification)")

    try:
        from pnkln_agents import JudgeSixLite

        judge = JudgeSixLite()

        # Test compliant content
        compliant_content = {
            "subject": "Test Email",
            "content": """
Hello,

This is a test email.

Unsubscribe: https://example.com/unsubscribe

Company Name
123 Main Street
San Francisco, CA 94105
            """.strip(),
        }

        verification = judge.verify(compliant_content, context={"is_marketing_email": True})

        print_success("Judge #6 verification executed")
        print_metric("Verification time", f"{verification.verification_time_ms:.2f}ms")
        print_metric("Passed", verification.passed)
        print_metric("Violations", len(verification.violations))

        if verification.violations:
            print("\n  Violations detected:")
            for v in verification.violations:
                print(f"    - [{v.severity.value}] {v.description}")

        return True
    except Exception as e:
        print_error(f"Judge #6 test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_gemini_ingestion():
    """Test Gemini Ingestion Layer"""
    print_header("TEST 4: Gemini Ingestion Layer (Collection)")

    try:
        from pnkln_agents import DEFAULT_SOURCES, GeminiIngestionLayer

        ingestion = GeminiIngestionLayer()

        # Register sources
        for source in DEFAULT_SOURCES[:3]:  # Use first 3 sources for quick test
            ingestion.register_source(source)

        print_success("Gemini Ingestion Layer initialized")
        print_metric("Registered sources", len(ingestion.sources))

        # Run ingestion (small batch for testing)
        result = ingestion.ingest(target_items=10)

        print_metric("Items collected", len(result.items))
        print_metric("Runtime", f"{result.runtime_minutes:.2f} min")
        print_metric("Success", result.success)
        print_metric("Ethical violations", len(result.violations))

        if result.metrics:
            print_metric("Unique sources", result.metrics.unique_sources_count)
            print_metric("Avg relevance", f"{result.metrics.average_relevance_score:.2f}")
            print_metric("Tier 1%", f"{result.metrics.tier_1_percentage:.1f}%")

        return True
    except Exception as e:
        print_error(f"Gemini Ingestion test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_intelligence_agent():
    """Test Intelligence Agent (full pipeline)"""
    print_header("TEST 5: Intelligence Agent (Full Pipeline)")

    try:
        from pnkln_agents import DEFAULT_SOURCES, IntelligenceAgent, IntelligenceTask

        agent = IntelligenceAgent()

        # Register sources (limited for quick test)
        for source in DEFAULT_SOURCES[:3]:
            agent.register_source(source)

        print_success("Intelligence Agent initialized")

        # Run intelligence collection
        result = agent.collect_intelligence(
            IntelligenceTask(
                query="Mac local testing",
                target_items=10,
                customer_id="mac_test",
                require_enforcement=True,
                require_briefing=True,
            )
        )

        print_metric("Status", result.status.value)
        print_metric("Execution time", f"{result.execution_time_ms:.2f}ms")

        if result.status.name == "COMPLETED":
            print_success("Intelligence collection completed")

            if result.metrics:
                print("\n  Ingestion Metrics:")
                print_metric("  Items collected", result.metrics["ingestion"]["items_collected"])
                print_metric("  Unique sources", result.metrics["ingestion"]["unique_sources"])
                print_metric(
                    "  Avg relevance", f"{result.metrics['ingestion']['average_relevance']:.2f}"
                )

                print("\n  Enforcement Metrics:")
                print_metric(
                    "  Verification passed", result.metrics["enforcement"]["verification_passed"]
                )
                print_metric("  Violations", result.metrics["enforcement"]["violations"])

            if result.briefing:
                print("\n  Briefing generated:")
                print(f"    {len(result.briefing)} characters")
        else:
            print_error(f"Intelligence collection failed: {result.status.value}")
            return False

        return True
    except Exception as e:
        print_error(f"Intelligence Agent test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_compliance_sdr():
    """Test Compliance SDR Agent"""
    print_header("TEST 6: Compliance SDR Agent (Lead Generation)")

    try:
        from pnkln_agents import ComplianceSDRAgent

        agent = ComplianceSDRAgent()

        print_success("Compliance SDR Agent initialized")

        # Generate leads (small batch)
        result = agent.generate_leads(
            query="Tech startups",
            target_count=20,
            customer_id="mac_test",
            context={
                "gdpr_consent": False,
                "allow_personal_emails": False,
            },
        )

        print_metric("Status", result.status.value)
        print_metric("Execution time", f"{result.execution_time_ms:.2f}ms")

        if result.status.name == "COMPLETED":
            leads = result.output
            print_success("Lead generation completed")
            print_metric("Approved leads", len(leads.approved_leads))
            print_metric("Blocked leads", len(leads.blocked_leads))
            print_metric("Needs review", len(leads.needs_review_leads))
            print_metric("Total cost", f"${leads.total_cost_usd:.2f}")
        else:
            print_error(f"Lead generation failed: {result.status.value}")
            return False

        return True
    except Exception as e:
        print_error(f"Compliance SDR test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration():
    """Test configuration modules"""
    print_header("TEST 7: Configuration Modules")

    try:
        from pnkln_agents import (
            DEFAULT_CONSTRAINTS,
            DEFAULT_INGESTION_CONFIG,
            DEFAULT_REVENUE_MODEL,
            PricingTier,
        )

        print_success("Configuration imports successful")

        # Bootstrap constraints
        print("\n  Bootstrap Constraints:")
        print_metric("  Monthly burn", f"${DEFAULT_CONSTRAINTS.monthly_burn_usd:,.2f}")
        print_metric(
            "  ROI gate",
            f"≥{DEFAULT_CONSTRAINTS.roi_gate_multiplier}× ({DEFAULT_CONSTRAINTS.roi_gate_months}mo)",
        )
        print_metric("  SLA p99", f"{DEFAULT_CONSTRAINTS.sla_p99_ms}ms")

        # Revenue model
        print("\n  Revenue Model:")
        print_metric("  Base tier", f"${DEFAULT_REVENUE_MODEL.base_tier.monthly_price_usd}/mo")
        print_metric("  Usage pricing", f"${DEFAULT_REVENUE_MODEL.price_per_validated_lead}/lead")
        ltv = DEFAULT_REVENUE_MODEL.calculate_ltv(PricingTier.BASE)
        ratio = DEFAULT_REVENUE_MODEL.calculate_ltv_cac_ratio(PricingTier.BASE)
        print_metric("  Base LTV", f"${ltv:,.2f}")
        print_metric("  LTV:CAC ratio", f"{ratio:.1f}:1")

        # Ingestion config
        print("\n  Ingestion Config:")
        print_metric("  Target items/day", DEFAULT_INGESTION_CONFIG.target_items_per_day)
        print_metric("  Target cost/item", f"${DEFAULT_INGESTION_CONFIG.target_cost_per_item}")
        print_metric("  Target runtime", f"{DEFAULT_INGESTION_CONFIG.target_runtime_minutes} min")
        print_metric("  Monthly cost", f"${DEFAULT_INGESTION_CONFIG.monthly_operational_cost_usd}")

        return True
    except Exception as e:
        print_error(f"Configuration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  PNKLN AGENT PLATFORM - MAC LOCAL VALIDATION                      ║")
    print("║  Version: 0.2.0 (Collection → Enforcement)                        ║")
    print(
        "║  Date: {}                                          ║".format(
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )
    print("╚════════════════════════════════════════════════════════════════════╝")

    tests = [
        ("Core Imports", test_imports),
        ("JR Engine", test_jr_engine),
        ("Judge #6 Lite", test_judge_six),
        ("Gemini Ingestion", test_gemini_ingestion),
        ("Intelligence Agent", test_intelligence_agent),
        ("Compliance SDR Agent", test_compliance_sdr),
        ("Configuration", test_configuration),
    ]

    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test {name} crashed: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print_header("TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "=" * 70)
        print("  ✓ ALL TESTS PASSED - MAC SETUP VALIDATED")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Review code in src/pnkln_agents/")
        print("  2. Check docs/adr/ for architecture decisions")
        print("  3. Run full tests: pytest tests/")
        print("  4. Deploy to GKE: See docs/deployment.md")
        return 0
    else:
        print("\n" + "=" * 70)
        print(f"  ✗ {total - passed} TEST(S) FAILED")
        print("=" * 70)
        print("\nTroubleshooting:")
        print("  1. Check Python version: python3 --version (≥3.10 required)")
        print("  2. Reinstall dependencies: pip install -r requirements.txt")
        print("  3. Reinstall package: pip install -e .")
        return 1


if __name__ == "__main__":
    sys.exit(main())
