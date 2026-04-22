"""Compliance SDR Agent Demo

Demonstrates enforcement-first lead generation with GDPR/CAN-SPAM compliance.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pnkln_agents import (
    DEFAULT_CONSTRAINTS,
    DEFAULT_REVENUE_MODEL,
    ComplianceSDRAgent,
    JREngine,
    JudgeSixLite,
    PricingTier,
)


def print_separator(title=""):
    """Print section separator"""
    if title:
        print(f"\n{'=' * 60}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")
    else:
        print(f"{'=' * 60}\n")


def demo_jr_engine():
    """Demonstrate JR Engine validation"""
    print_separator("JR Engine: Purpose/Reasons/Brakes Validation")

    from shadowtagai_agents import Purpose, Reason

    jr_engine = JREngine(
        config={
            "max_budget_per_action": 100.0,
            "require_human_approval_above": 1000.0,
        },
    )

    # Example 1: Approved action
    purpose = Purpose(
        intent="Generate 50 B2B leads for customer outreach",
        business_value="Lead generation for sales pipeline",
        customer_id="customer_123",
        cost_estimate_usd=5.0,
        expected_outcome="50 GDPR-compliant leads",
    )

    reasons = [
        Reason(
            justification="Automated lead generation with compliance enforcement",
            risk_probability=0.2,
            risk_severity=0.3,
            mitigation_strategy="Judge 6 GDPR/CAN-SPAM filtering",
        ),
    ]

    decision = jr_engine.validate(
        purpose,
        reasons,
        context={
            "eu_customer": False,
            "involves_pii": True,
        },
    )

    print(f"Status: {'✅ APPROVED' if decision.approved else '🚫 BLOCKED'}")
    print(f"Validation time: {decision.validation_time_ms:.2f}ms")

    if decision.brakes:
        print("\nBrakes triggered:")
        for brake in decision.brakes:
            print(f"  - {brake.reason}")
            print(f"    Required action: {brake.required_action}")
    else:
        print("\nConstraints applied:")
        for key, value in decision.constraints.items():
            print(f"  - {key}: {value}")

    # Example 2: Budget exceeded
    print("\n" + "-" * 60 + "\n")

    high_cost_purpose = Purpose(
        intent="Generate 10,000 leads",
        business_value="Mass lead generation",
        customer_id="customer_456",
        cost_estimate_usd=1500.0,  # Exceeds limit
        expected_outcome="10,000 leads",
    )

    decision2 = jr_engine.validate(high_cost_purpose, reasons, context={})

    print(f"Status: {'✅ APPROVED' if decision2.approved else '🚫 BLOCKED'}")
    print(f"Validation time: {decision2.validation_time_ms:.2f}ms")

    if decision2.brakes:
        print("\nBrakes triggered:")
        for brake in decision2.brakes:
            print(f"  - {brake.brake_type.value}: {brake.reason}")


def demo_judge_six():
    """Demonstrate Judge 6 Lite verification"""
    print_separator("Judge 6 Lite: Rule-Based Enforcement")

    judge = JudgeSixLite()

    # Example 1: CAN-SPAM compliant email
    email_compliant = {
        "subject": "Special Offer on Our Services",
        "content": """
Hello,

We have a special offer for you.

If you'd like to unsubscribe, click here: https://example.com/unsubscribe

Company Name
123 Main Street
San Francisco, CA 94105
        """.strip(),
    }

    verification1 = judge.verify(email_compliant, context={"is_marketing_email": True})

    print("Email Content (CAN-SPAM Compliant):")
    print(f"Status: {'✅ PASSED' if verification1.passed else '🚫 FAILED'}")
    print(f"Verification time: {verification1.verification_time_ms:.2f}ms")
    print(f"Violations: {len(verification1.violations)}")

    # Example 2: CAN-SPAM non-compliant email
    print("\n" + "-" * 60 + "\n")

    email_noncompliant = {
        "subject": "Re: Your Account",  # Deceptive subject
        "content": "Buy now! Limited time offer!",  # No unsubscribe, no address
    }

    verification2 = judge.verify(email_noncompliant, context={"is_marketing_email": True})

    print("Email Content (CAN-SPAM Non-Compliant):")
    print(f"Status: {'✅ PASSED' if verification2.passed else '🚫 FAILED'}")
    print(f"Verification time: {verification2.verification_time_ms:.2f}ms")
    print(f"Violations: {len(verification2.violations)}")

    if verification2.violations:
        print("\nViolations found:")
        for v in verification2.violations:
            print(f"  - [{v.severity.value}] {v.violation_type.value}: {v.description}")
            if v.remediation:
                print(f"    Remediation: {v.remediation}")


def demo_compliance_sdr_agent():
    """Demonstrate Compliance SDR Agent"""
    print_separator("Compliance SDR Agent: GDPR/CAN-SPAM Lead Generation")

    agent = ComplianceSDRAgent()

    # Example 1: German leads (GDPR risk)
    print("Query: 'German fintech CTOs' (EU customers, GDPR risk)\n")

    result1 = agent.generate_leads(
        query="German fintech CTOs",
        target_count=50,
        customer_id="customer_789",
        context={
            "gdpr_consent": False,  # No GDPR consent
            "allow_personal_emails": False,  # Block personal emails
        },
    )

    print(f"Status: {result1.status.value}")
    print(f"Execution time: {result1.execution_time_ms:.2f}ms")

    if result1.status.name == "COMPLETED":
        leads = result1.output
        print(f"\n✅ Approved leads: {len(leads.approved_leads)}")
        print(f"🚫 Blocked leads: {len(leads.blocked_leads)}")
        print(f"⚠️  Needs review: {len(leads.needs_review_leads)}")
        print(f"💰 Total cost: ${leads.total_cost_usd:.2f}")

        if leads.blocked_leads:
            print("\nSample blocked lead:")
            blocked = leads.blocked_leads[0]
            print(f"  - {blocked.name} ({blocked.email})")
            print(f"    Reason: {blocked.block_reason}")

        if leads.needs_review_leads:
            print("\nSample needs-review lead:")
            review = leads.needs_review_leads[0]
            print(f"  - {review.name} ({review.email})")
            print(f"    Reason: {review.block_reason}")

    elif result1.status.name == "ESCALATED":
        print(f"\n🚫 Escalated: {result1.metadata.get('escalation_reason')}")

    # Example 2: US leads (lower GDPR risk)
    print("\n" + "-" * 60 + "\n")
    print("Query: 'US SaaS founders' (non-EU, lower risk)\n")

    result2 = agent.generate_leads(
        query="US SaaS founders",
        target_count=50,
        customer_id="customer_790",
        context={
            "gdpr_consent": False,
            "allow_personal_emails": False,
        },
    )

    if result2.status.name == "COMPLETED":
        leads2 = result2.output
        print(f"✅ Approved leads: {len(leads2.approved_leads)}")
        print(f"🚫 Blocked leads: {len(leads2.blocked_leads)}")
        print(f"⚠️  Needs review: {len(leads2.needs_review_leads)}")
        print(f"💰 Total cost: ${leads2.total_cost_usd:.2f}")


def demo_revenue_model():
    """Demonstrate revenue model calculations"""
    print_separator("Revenue Model & Bootstrap Constraints")

    # Revenue model
    print("Pricing Tiers:")
    print(f"  Base tier: ${DEFAULT_REVENUE_MODEL.base_tier.monthly_price_usd}/mo")
    print(f"  White-glove: ${DEFAULT_REVENUE_MODEL.white_glove_tier.monthly_price_usd}/mo")
    print(f"  Enterprise: ${DEFAULT_REVENUE_MODEL.enterprise_tier.monthly_price_usd}/mo")
    print(f"  Usage: ${DEFAULT_REVENUE_MODEL.price_per_validated_lead}/lead")

    print("\nLTV Calculations (18mo average lifetime):")
    for tier in [PricingTier.BASE, PricingTier.WHITE_GLOVE, PricingTier.ENTERPRISE]:
        ltv = DEFAULT_REVENUE_MODEL.calculate_ltv(tier)
        ratio = DEFAULT_REVENUE_MODEL.calculate_ltv_cac_ratio(tier)
        print(f"  {tier.value}: LTV=${ltv:,.2f}, LTV:CAC={ratio:.1f}:1")

    # Bootstrap constraints
    print("\nBootstrap Constraints:")
    constraints_dict = DEFAULT_CONSTRAINTS.to_dict()
    print(f"  Monthly burn: ${constraints_dict['monthly_burn_usd']:,.2f}")
    print(f"  ROI gate: {constraints_dict['roi_gate']}")
    print(f"  LTV:CAC gate: {constraints_dict['ltv_cac_gate']}")
    print(f"  SLA p99: {constraints_dict['sla_p99_ms']}ms")
    print(
        f"  Operational cost: ${constraints_dict['operational_cost_range'][0]:,.2f}-${constraints_dict['operational_cost_range'][1]:,.2f}/mo",
    )

    # Break-even analysis
    print("\nBreak-even Analysis:")
    min_customers, max_customers = DEFAULT_CONSTRAINTS.calculate_break_even_customers(
        DEFAULT_REVENUE_MODEL.base_tier.monthly_price_usd,
    )
    print(f"  Base tier ($297/mo): {min_customers}-{max_customers} customers")

    min_leads, max_leads = DEFAULT_CONSTRAINTS.calculate_break_even_leads(
        DEFAULT_REVENUE_MODEL.price_per_validated_lead,
    )
    print(f"  Usage tier ($0.10/lead): {min_leads:,}-{max_leads:,} leads/mo")


def main():
    """Run all demos"""
    print_separator("SHADOWTAGAI AGENT PLATFORM DEMO")
    print("Enforcement-First Agent Architecture")
    print("Version: 0.1.0")

    try:
        demo_jr_engine()
        demo_judge_six()
        demo_compliance_sdr_agent()
        demo_revenue_model()

        print_separator("DEMO COMPLETE")
        print("✅ All demonstrations completed successfully!")
        print("\nNext steps:")
        print("  1. Review code in src/shadowtagai_agents/")
        print("  2. Check docs/adr/001-enforcement-first-architecture.md")
        print("  3. Run tests: pytest")
        print("  4. Deploy: See docs/deployment.md")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
