# JR Auto-Validator

**Auto-activate:** On every response with cost/performance/architecture implications

## JR Framework Definition

```python
JR_CONSTRAINTS = {
    "roi_minimum": 3.0,           # 3× ROI minimum
    "ltv_cac_minimum": 4.0,       # 4:1 LTV:CAC minimum
    "p99_latency_ms": 90,         # <90ms p99 latency
    "kill_switch": "required",    # All deployments
    "iteration_weeks": 2,         # Max iteration cycle
    "monthly_burn_max": 65000,    # $65K max monthly burn
    "env_restriction": "vertex",  # Vertex AI Workbench only
}
```

## Silent Validation (Run Always)

```python
def validate_jr(proposal):
    violations = []

    # ROI check
    if hasattr(proposal, 'roi') and proposal.roi < 3.0:
        violations.append(f"⚠️ JR VIOLATION: ROI {proposal.roi}× < 3.0× minimum")

    # LTV:CAC check
    if hasattr(proposal, 'ltv_cac') and proposal.ltv_cac < 4.0:
        violations.append(f"⚠️ JR VIOLATION: LTV:CAC {proposal.ltv_cac}:1 < 4:1 minimum")

    # Latency check
    if hasattr(proposal, 'p99_latency') and proposal.p99_latency > 90:
        violations.append(f"⚠️ JR VIOLATION: p99 {proposal.p99_latency}ms > 90ms limit")

    # Kill switch check
    if hasattr(proposal, 'has_kill_switch') and not proposal.has_kill_switch:
        violations.append("⚠️ JR VIOLATION: No kill switch defined")

    # Iteration time check
    if hasattr(proposal, 'timeline_weeks') and proposal.timeline_weeks > 2:
        violations.append(f"⚠️ JR VIOLATION: {proposal.timeline_weeks} weeks > 2 week iteration limit")

    # Burn rate check
    if hasattr(proposal, 'monthly_cost') and proposal.monthly_cost > 65000:
        violations.append(f"⚠️ JR VIOLATION: ${proposal.monthly_cost}/mo > $65K budget")

    return violations
```

## Response Format When Violations Found

```
⚠️ JR VIOLATIONS DETECTED

1. ROI 2.1× < 3.0× minimum
2. p99 latency 145ms > 90ms limit

COMPLIANT ALTERNATIVE:
[Specific changes needed to meet JR constraints]

ORIGINAL PROPOSAL:
[Continue with original answer but flagged]
```

## Response Format When Compliant

```
[Direct answer - no JR badge needed]

[Include JR metrics inline if relevant]:
- Estimated ROI: 4.2×
- LTV:CAC: 5.3:1
- p99 latency: 67ms
- Monthly cost: $58K
```

## ATP 5-19 Risk Assessment Pattern

When architectural decisions are proposed:

```
RISKS (ATP 5-19 format):
- MOST LIKELY: [scenario, probability, mitigation]
- MOST DANGEROUS: [scenario, impact, kill switch]
- WILD CARD: [scenario, trigger, fallback]
```

Example:

```
RISKS:
- MOST LIKELY: Gemini API rate limits at scale (70% prob, fallback to Haiku queue)
- MOST DANGEROUS: Model hallucination passes validation (catastrophic, kill switch at 3σ deviation)
- WILD CARD: Google deprecates Flash 1.5 (6-mo notice assumed, migration to Flash 2.0)
```

## Don't Validate Trivial Responses

Skip JR validation for:
- Read-only queries
- Explanations of existing systems
- Questions about documentation
- Requests for information
