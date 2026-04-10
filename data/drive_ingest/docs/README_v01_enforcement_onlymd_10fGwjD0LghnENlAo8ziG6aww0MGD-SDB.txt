# ShadowTagAi Agent Platform

**Enforcement-First Agent Architecture for Regulated Verticals**

Build compliant AI agents with mandatory GDPR/CAN-SPAM/HIPAA enforcement, audit trails, and legal defensibility.

---

## Overview

Traditional agent frameworks use "start simple, add enforcement later" approach, creating liability in regulated verticals. ShadowTagAi provides **enforcement-first architecture** where every agent action is validated before execution and verified after completion.

### Key Components

```
┌─────────────────────────────────────────────────────┐
│                  ShadowTagAi Agent Pattern                 │
│                                                      │
│  1. Parse Intent → AgentTask                        │
│  2. JR Engine validates (Purpose/Reasons/Brakes)    │
│  3. If brake triggered → escalate to human          │
│  4. Execute with guardrails → raw result            │
│  5. Judge #6 verifies compliance → verification     │
│  6. If verification fails → rollback and log        │
│  7. Return result with watermark                     │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd aiyou-fastapi-services

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Example: Compliance SDR Agent

```python
from shadowtagai_agents import ComplianceSDRAgent

# Initialize agent
agent = ComplianceSDRAgent()

# Generate GDPR/CAN-SPAM compliant leads
result = agent.generate_leads(
    query="German fintech CTOs",
    target_count=100,
    customer_id="customer_123",
    context={
        'gdpr_consent': False,  # No GDPR consent yet
        'allow_personal_emails': False,  # Block personal emails
    }
)

# Check result
if result.status.name == 'COMPLETED':
    lead_result = result.output
    print(f"Approved: {len(lead_result.approved_leads)}")
    print(f"Blocked: {len(lead_result.blocked_leads)}")
    print(f"Cost: ${lead_result.total_cost_usd:.2f}")

    # Export audit trail
    audit_report = agent.export_audit_report(format='json')
```

---

## Architecture

### 1. JR Engine (Purpose/Reasons/Brakes Validator)

**Target Latency:** <500μs

Validates every agent action using ATP 5-19 risk assessment:

```python
from shadowtagai_agents import JREngine, Purpose, Reason

jr_engine = JREngine()

purpose = Purpose(
    intent="Generate B2B leads for customer",
    business_value="Lead generation for sales pipeline",
    customer_id="customer_123",
    cost_estimate_usd=10.0,
    expected_outcome="100 GDPR-compliant leads"
)

reasons = [
    Reason(
        justification="Automated lead generation with compliance enforcement",
        risk_probability=0.2,
        risk_severity=0.3,
        mitigation_strategy="Judge #6 GDPR/CAN-SPAM filtering"
    )
]

decision = jr_engine.validate(purpose, reasons, context={})

if decision.approved:
    print("✅ Approved for execution")
else:
    print("🚫 Brakes triggered:")
    for brake in decision.brakes:
        print(f"  - {brake.reason}")
```

**Risk Levels (ATP 5-19):**

| Risk Score | Level          | Action                       |
| ---------- | -------------- | ---------------------------- |
| ≥0.8       | Extremely High | Requires human approval      |
| ≥0.6       | High           | Requires mitigation strategy |
| ≥0.4       | Moderate       | Enhanced logging             |
| ≥0.2       | Low            | Standard execution           |
| <0.2       | Extremely Low  | Fast-path execution          |

### 2. Judge #6 Lite (Rule-Based Enforcement)

**Target Latency:** <90ms p99

Verifies agent outputs against compliance rules:

```python
from shadowtagai_agents import JudgeSixLite

judge = JudgeSixLite()

# Verify email content for CAN-SPAM compliance
email_content = {
    'subject': 'Special Offer',
    'content': 'Buy now! Unsubscribe: http://...',
    'email_body': '123 Main St, San Francisco, CA'
}

verification = judge.verify(
    email_content,
    context={'is_marketing_email': True}
)

if verification.passed:
    print("✅ Compliance verified")
else:
    print("🚫 Violations found:")
    for violation in verification.violations:
        print(f"  - {violation.description}")
```

**Built-in Rules:**

- **CAN-SPAM:** Unsubscribe link, physical address, non-deceptive subject
- **GDPR:** Consent validation, data minimization, personal email filtering
- **HIPAA:** PHI authorization (placeholder)
- **Budget:** Cost limit enforcement

### 3. Agent Pattern

All ShadowTagAi agents inherit from `ShadowTagAiAgent` base class:

```python
from shadowtagai_agents import ShadowTagAiAgent, AgentTask

class MyCustomAgent(ShadowTagAiAgent):
    def _execute_task(self, task: AgentTask, constraints: dict):
        # Your agent logic here
        return {"result": "task completed"}

    def _build_reasons(self, task: AgentTask):
        return [
            Reason(
                justification="Custom task execution",
                risk_probability=0.1,
                risk_severity=0.1,
                mitigation_strategy="Automated verification"
            )
        ]

# Use agent
agent = MyCustomAgent()
result = agent.execute(AgentTask(
    intent="Custom task",
    customer_id="customer_123",
    context={},
    cost_estimate_usd=1.0
))
```

---

## Configuration

### Bootstrap Constraints

```python
from shadowtagai_agents import DEFAULT_CONSTRAINTS

print(DEFAULT_CONSTRAINTS.to_dict())
# {
#   'monthly_burn_usd': 65000.0,
#   'roi_gate': '≥3× (18mo)',
#   'ltv_cac_gate': '≥4:1 (12mo)',
#   'sla_p99_ms': 90,
#   'sla_p50_ms': 50,
#   'security_gate': '100%',
#   'operational_cost_range': (1000.0, 1600.0)
# }

# Calculate break-even
min_customers, max_customers = DEFAULT_CONSTRAINTS.calculate_break_even_customers(297.0)
print(f"Break-even: {min_customers}-{max_customers} customers @ $297/mo")
```

### Revenue Model

```python
from shadowtagai_agents import DEFAULT_REVENUE_MODEL, PricingTier

print(DEFAULT_REVENUE_MODEL.to_dict())

# Calculate LTV for base tier
ltv = DEFAULT_REVENUE_MODEL.calculate_ltv(PricingTier.BASE)
print(f"Base tier LTV: ${ltv:.2f}")  # $5,346

# Calculate LTV:CAC ratio
ratio = DEFAULT_REVENUE_MODEL.calculate_ltv_cac_ratio(PricingTier.BASE)
print(f"LTV:CAC ratio: {ratio:.1f}:1")  # 5.3:1
```

**Pricing Tiers:**

| Tier            | Price/mo   | Target Customer           | LTV (18mo) |
| --------------- | ---------- | ------------------------- | ---------- |
| **Base**        | $297       | SaaS with EU customers    | $5,346     |
| **White-glove** | $997       | US healthcare (HIPAA)     | $17,946    |
| **Enterprise**  | $9,970     | Financial services (SOC2) | $179,460   |
| **Usage**       | $0.10/lead | Pay-per-validated-lead    | N/A        |

---

## Compliance SDR Agent

**Job:** Generate B2B leads without GDPR/CAN-SPAM violations

**Workflow:**

1. User query: "Find 100 German fintech CTOs"
2. JR Engine validates budget/purpose
3. Agent scrapes LinkedIn/Apollo/Clearbit
4. Judge #6 filters personal emails, flags EU contacts
5. Output: N approved + M blocked + audit PDF

**Features:**

- ✅ EU personal email filtering (GDPR risk)
- ✅ GDPR consent validation
- ✅ Personal vs corporate email classification
- ✅ Per-lead pricing ($0.10/approved)
- ✅ Audit trail generation
- ✅ Exportable compliance report

**Example:**

```python
from shadowtagai_agents import ComplianceSDRAgent

agent = ComplianceSDRAgent()

result = agent.generate_leads(
    query="German fintech CTOs",
    target_count=100,
    customer_id="customer_123"
)

if result.status.name == 'COMPLETED':
    leads = result.output
    print(f"✅ Approved: {len(leads.approved_leads)}")
    print(f"🚫 Blocked: {len(leads.blocked_leads)}")
    print(f"⚠️  Needs review: {len(leads.needs_review_leads)}")
    print(f"💰 Cost: ${leads.total_cost_usd:.2f}")
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/shadowtagai_agents --cov-report=html

# Run specific test
pytest tests/unit/test_jr_engine.py
```

---

## Deployment

See [docs/deployment.md](docs/deployment.md) for deployment guide.

**Quick Deploy:**

```bash
# Build Docker image
docker build -t shadowtagai-agents .

# Run container
docker run -p 8000:8000 shadowtagai-agents

# Or deploy to CloudFlare Workers (edge compute)
# See deployment guide for details
```

---

## Architecture Decision Records

See [docs/adr/001-enforcement-first-architecture.md](docs/adr/001-enforcement-first-architecture.md) for detailed architecture decisions.

**Key Decisions:**

- Enforcement-first pattern (validation before execution)
- JR Engine for Purpose/Reasons/Brakes validation
- Judge #6 Lite for rule-based compliance
- Target SLA: <90ms p99 for verification
- Revenue model: $297-$9,970/mo + usage pricing

---

## Roadmap

### Immediate (7-day MVP)

- [x] Implement JR Engine
- [x] Implement Judge #6 Lite
- [x] Implement Agent Pattern
- [x] Implement Compliance SDR Agent
- [ ] Write tests (unit + integration)
- [ ] Set up CI/CD
- [ ] Deploy MVP
- [ ] Launch to first customer

### Short-term (30 days)

- [ ] Integrate real lead sources (LinkedIn Sales Navigator, Apollo.io)
- [ ] Build PDF audit export
- [ ] Add multi-tenancy support
- [ ] Build customer dashboard
- [ ] Measure LTV/CAC
- [ ] Iterate on pricing

### Medium-term (90 days)

- [ ] Implement ML training for Judge #6
- [ ] Add LangGraph integration
- [ ] Scale to 10+ customers
- [ ] Validate revenue model
- [ ] Add more agent types (support, moderation)

---

## License

Proprietary - ShadowTagAi Engineering

---

## Support

- Issues: [GitHub Issues](https://github.com/ehanc69/aiyou-fastapi-services/issues)
- Email: support@shadowtagai.ai
- Documentation: [docs/](docs/)

---

## Credits

**Architecture:** ShadowTagAi Engineering Team

**Based on:**

- ATP 5-19 (US Army risk assessment methodology)
- GDPR (EU General Data Protection Regulation)
- CAN-SPAM Act (US email marketing law)
- HIPAA (US healthcare data protection)

**Built with:**

- Python 3.10+
- FastAPI
- Pydantic
- (Future: LangGraph, Gemini Flash, ChromaDB)

---

**Status:** ✅ MVP Implementation Complete

**Last Updated:** 2025-11-15

**Version:** 0.1.0
