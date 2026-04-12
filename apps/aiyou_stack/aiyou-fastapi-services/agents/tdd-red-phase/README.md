# TDD Red-Phase Agent (Embedded Guard Validation)

## Overview

**One agent. Two phases internally. Zero coordination overhead.**

This agent eliminates the 3-agent circular dependency problem by embedding guard validation directly into the TDD red-phase. No separate tdd-guard agent needed.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         TDD-Red-Phase Agent (Unified)                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Phase 1: Test Generation                                │
│  ├─ Parse requirements                                   │
│  ├─ Generate integration tests (80%)                     │
│  ├─ Generate unit tests (20%)                            │
│  └─ Output: TestSuite + metadata                         │
│                                                           │
│  Phase 2: Self-Verification (Embedded Guard)             │
│  ├─ Validate against 10 compliance rules                 │
│  ├─ Calculate weighted compliance score                  │
│  ├─ If < 95%: Self-correct (max 3 iterations)            │
│  ├─ Generate audit trail                                 │
│  └─ Output: ComplianceReport + validated tests           │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Old Architecture (3-agent circular dependency)

```
tdd-guard → instructs → tdd-red-phase → modifies → tdd-guard verifies
    ↑                                                         │
    └─────────────────────────────────────────────────────────┘
```

### New Architecture (single agent, internal phases)

```
tdd-red-phase:
  - Write tests
  - SELF-VERIFY against rules (embedded)
  - Self-correct violations
  - Output: tests + compliance_report
```

## Compliance Rules (95% Threshold)

| ID  | Rule                      | Weight | Severity | Enforcement |
| --- | ------------------------- | ------ | -------- | ----------- |
| R1  | Coverage Completeness     | 15%    | Critical | Mandatory   |
| R2  | Test Independence         | 10%    | Critical | Mandatory   |
| R3  | Naming Convention         | 8%     | High     | Recommended |
| R4  | Assertion Presence        | 12%    | Critical | Mandatory   |
| R5  | Resource Cleanup          | 9%     | High     | Mandatory   |
| R6  | Dependency Mocking        | 10%    | High     | Mandatory   |
| R7  | Edge Case Coverage        | 12%    | Critical | Mandatory   |
| R8  | Performance Constraints   | 7%     | Medium   | Recommended |
| R9  | Test Documentation        | 7%     | Medium   | Recommended |
| R10 | Integration Ratio (80/20) | 10%    | High     | Mandatory   |

**Total:** 100% weighted compliance

## Kill Switch & Constraints

```typescript
MAX_ITERATIONS = 3           // Self-correction attempts
TIMEOUT = 90s                // p99 ≤90ms doctrine (Judge #6)
FAIL_FAST = 10 violations    // Don't analyze 100+ violations
COMPLIANCE_THRESHOLD = 95%   // Pass/fail gate
```

## Escalation Paths

If any condition triggers:

- `iterations_exceeded` - Max 3 attempts reached
- `timeout_reached` - 90s SLA breached
- `compliance_impossible` - Cannot achieve 95%

Action: Generate audit log → Manual review

## Audit Trail

Every execution generates:

```json
{
  "timestamp": "2025-11-14T...",
  "total_iterations": 2,
  "final_compliance_score": 0.97,
  "passed": true,
  "violations_found": [...],
  "corrections_applied": [...],
  "execution_time_ms": 4523,
  "escalation_triggered": false,
  "judge6_integration": {
    "coverage_target": 0.98,
    "latency_p99_ms": 90
  }
}
```

Saved to: `/logs/tdd-guard-{timestamp}.json`

## Usage

### TypeScript

```typescript
import TDDRedPhaseAgent from './agents/tdd-red-phase/tdd-red-phase-agent';

const agent = new TDDRedPhaseAgent();

const requirements = `
Module: PaymentProcessor
- Process credit card payments
- Validate card numbers
- Handle declined transactions
- Integrate with Stripe API
`;

const result = await agent.execute(requirements);

if (result.success) {
  console.log('✓ Tests generated and validated');
  console.log(`Compliance: ${(result.compliance_report.compliance_score * 100).toFixed(1)}%`);
  console.log(`Tests: ${result.test_suite?.metadata.total_tests}`);
  console.log(
    `Integration ratio: ${(result.test_suite?.metadata.integration_ratio * 100).toFixed(1)}%`
  );
} else {
  console.log('✗ Compliance failed');
  console.log(`Score: ${(result.compliance_report.compliance_score * 100).toFixed(1)}%`);
  console.log(`Violations: ${result.compliance_report.violations_found.length}`);

  if (result.compliance_report.escalation_triggered) {
    console.log(`Escalation: ${result.compliance_report.escalation_reason}`);
  }
}
```

### Result Object

```typescript
interface AgentResult {
  success: boolean; // Passed 95% threshold?
  test_suite: TestSuite | null; // Generated tests
  compliance_report: ComplianceReport; // Validation details
  audit_file_path?: string; // Audit trail location
}
```

## Integration with Judge #6

The agent aligns with Judge #6 enforcement doctrine:

- **Coverage Target:** 98% (enforced via R1)
- **Latency SLA:** p99 ≤90ms (timeout constraint)
- **Quality Gate:** 95%+ compliance before Green phase
- **Integration First:** 80/20 rule (R10) for bootstrap ROI

## Boy Scout Rule

This agent **leaves code cleaner than found** by:

1. Enforcing naming conventions
2. Adding missing edge case tests
3. Ensuring proper cleanup/teardown
4. Validating assertion presence
5. Maintaining 80/20 integration ratio

## Bootstrap ROI Justification

**Old complexity:** 3 agents, circular coordination
**New elegance:** 1 agent, internal phases
**ROI:** Eliminates coordination latency, reduces failure modes, simpler debugging

**Does 1-agent simplicity justify quality?** YES.

- Same 95% compliance gate
- Same 10 validation rules
- Faster execution (no inter-agent communication)
- Clearer audit trail
- Judge #6 integration maintained

**Ship TODAY. Perfect tomorrow.**

---

## Configuration

Edit `/src/config/tdd-compliance-rules.json` to customize:

- Rule weights
- Thresholds
- Timeout values
- Audit settings
- Judge #6 integration params

## Logs

Audit trails stored in `/logs/` directory:

- Retention: 90 days (configurable)
- Format: JSON
- Includes: violations, corrections, scores, timing

---

_"Real artists ship. With 95% compliance attached."_ 🚀
