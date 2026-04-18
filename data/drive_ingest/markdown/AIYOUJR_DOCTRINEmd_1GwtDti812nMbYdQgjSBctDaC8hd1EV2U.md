# ShadowTag-v2JR DOCTRINE

## Governance Framework for Multi-Agent Systems

**Framework Name**: ShadowTag-v2JR (AI-Driven, Youth-Oriented, Justified Risk)
**Foundation**: ATP 5-19 Risk Management + PRB Stratification
**Purpose**: Ensure safe, auditable, and effective multi-agent coordination

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [PRB Framework](#prb-framework)
3. [Risk Stratification](#risk-stratification)
4. [Approval Gates](#approval-gates)
5. [Audit Trail](#audit-trail)
6. [Judge #6 Protocol](#judge-6-protocol)
7. [Incident Response](#incident-response)

---

## Core Principles

### 1. Justified Risk (JR)

**Principle**: Every action must have a clear, documented justification balancing probability, risk, and benefit.

**Implementation**:

- All agent tasks include risk assessment metadata
- Benefits are quantified and compared against risks
- Decisions are traceable to specific requirements

**Example**:

```python
task = {
    "description": "Deploy Bevy plugin to production",
    "justification": {
        "probability": 0.15,  # 15% chance of issues
        "risk": "Medium (single component failure, rollback available)",
        "benefit": "Enables real-time agent-game integration for 1000+ users",
        "verdict": "Benefit outweighs risk - APPROVED"
    }
}
```

### 2. Youth-Oriented (YO)

**Principle**: Design for accessibility, education, and long-term maintainability by next-generation developers.

**Implementation**:

- Comprehensive inline documentation
- Clear, descriptive variable and function names
- Educational comments explaining "why" not just "what"
- Onboarding guides for new contributors

**Example**:

```rust
/// Spawns a Bevy entity controlled by an AI agent.
///
/// # Why This Exists
/// Agents need to interact with the Bevy game world. This function
/// bridges the Claude Agent SDK (Python/TypeScript) with Bevy's ECS (Rust).
///
/// # Educational Note
/// Bevy uses an Entity-Component-System (ECS) architecture. Entities are
/// just IDs; components store data; systems process logic. This pattern
/// scales well for game engines.
pub fn spawn_agent_entity(agent_id: &str, commands: &mut Commands) { ... }
```

### 3. AI-Driven (AI)

**Principle**: Leverage AI for automation, but maintain human oversight for critical decisions.

**Implementation**:

- RA-1, RA-2, RA-3 tasks automated
- RA-4, RA-5 tasks require human approval
- AI generates options; humans make final calls on high-risk items

**Human-AI Collaboration Model**:

```
RA-1, RA-2 → AI decides → Logs action
RA-3 → AI decides → Human reviews logs periodically
RA-4 → AI proposes → Human approves/rejects in real-time
RA-5 → AI proposes → Multi-party approval required
```

---

## PRB Framework

**PRB** = **P**robability × **R**isk × **B**enefit Analysis

### Formula

```
Decision Score = (Benefit / (Probability × Impact)) × Mitigation Factor

If Decision Score > Threshold → APPROVE
If Decision Score ≤ Threshold → REJECT or REQUEST MITIGATION
```

### Components

#### Probability (P)

**Scale**: 0.0 - 1.0 (0% - 100% likelihood of issue occurring)

- **0.0 - 0.01**: Extremely unlikely (RA-1)
- **0.01 - 0.05**: Unlikely (RA-2)
- **0.05 - 0.20**: Possible (RA-3)
- **0.20 - 0.50**: Likely (RA-4)
- **0.50 - 1.0**: Highly likely or certain (RA-5)

#### Risk/Impact (R)

**Scale**: 1 - 5 (severity of impact if issue occurs)

1. **Trivial**: Documentation typo, log message formatting
2. **Low**: Minor bug affecting single user, non-critical feature
3. **Moderate**: Bug affecting multiple users, partial feature degradation
4. **High**: Service outage, data corruption (recoverable), security vulnerability
5. **Critical**: Irreversible data loss, security breach, legal/compliance violation

#### Benefit (B)

**Scale**: 1 - 5 (value delivered by the action)

1. **Trivial**: Minor cosmetic improvement
2. **Low**: Small quality-of-life enhancement
3. **Moderate**: Notable feature addition, performance improvement
4. **High**: Major feature enabling new use cases
5. **Critical**: Mission-critical capability, significant revenue/user impact

#### Mitigation Factor (M)

**Scale**: 0.5 - 2.0 (adjusts based on available safeguards)

- **2.0**: Strong mitigation (rollback available, extensive testing, canary deployment)
- **1.0**: Standard mitigation (basic testing, monitoring)
- **0.5**: Weak mitigation (no rollback, limited testing)

### Example Calculations

#### Example 1: Deploy Bevy Plugin to Production

```
Probability: 0.15 (15% chance of issues)
Impact: 3 (Moderate - single component may fail)
Benefit: 4 (High - enables key feature for users)
Mitigation: 1.8 (Rollback available, tested in staging)

Decision Score = (4 / (0.15 × 3)) × 1.8 = (4 / 0.45) × 1.8 = 16.0

Threshold for RA-4: 10.0
Result: 16.0 > 10.0 → APPROVE (pending human review)
```

#### Example 2: Update Dependency to Untested Version

```
Probability: 0.60 (60% chance of breaking changes)
Impact: 4 (High - multiple systems depend on this)
Benefit: 2 (Low - minor performance improvement)
Mitigation: 0.8 (No rollback, limited testing)

Decision Score = (2 / (0.60 × 4)) × 0.8 = (2 / 2.4) × 0.8 = 0.67

Threshold for RA-5: 5.0
Result: 0.67 < 5.0 → REJECT
```

---

## Risk Stratification

### RA-1: Routine Administrative

**Characteristics**:

- Probability: <1%
- Impact: Trivial (1)
- Examples: Read config, update docs, log messages

**Approval**: Auto-approve
**Logging**: Optional (can be disabled for performance)
**Agent**: Any agent can execute

**Governance**:

```python
if task.risk_level == RiskLevel.RA_1:
    execute_immediately()
    # No approval required
```

---

### RA-2: Low Risk

**Characteristics**:

- Probability: 1-5%
- Impact: Low (2)
- Examples: Add unit tests, refactor internal code, implement utilities

**Approval**: Auto-approve with logging
**Logging**: Required (all RA-2+ actions must be logged)
**Agent**: BrownSnow (BS-02) typically executes

**Governance**:

```python
if task.risk_level == RiskLevel.RA_2:
    log_action(task)
    execute()
    log_result(task)
```

---

### RA-3: Medium Risk

**Characteristics**:

- Probability: 5-20%
- Impact: Moderate (3)
- Examples: Design architectures, modify APIs, change dependency versions

**Approval**: Requires review (human reviews logs periodically, but not real-time)
**Logging**: Required + detailed (include PRB calculation)
**Agent**: WhiteCastle (WC-01) typically executes

**Governance**:

```python
if task.risk_level == RiskLevel.RA_3:
    prb_score = calculate_prb(task)
    log_action_with_prb(task, prb_score)
    execute()
    log_result(task)
    # Human reviews daily log digest
```

---

### RA-4: High Risk

**Characteristics**:

- Probability: 20-50%
- Impact: High (4)
- Examples: Production deployment, database schema changes, security policy updates

**Approval**: **Requires human approval in real-time**
**Logging**: Required + detailed + archived for audit
**Agent**: OrangeCreek (OC-03) gates these actions

**Governance**:

```python
if task.risk_level == RiskLevel.RA_4:
    prb_score = calculate_prb(task)
    log_action_with_prb(task, prb_score)

    # BLOCK until human approves
    approval = request_human_approval(task, prb_score)

    if approval.status == "approved":
        execute()
        log_result(task, approval.rationale)
        archive_approval(approval)
    else:
        log_rejection(task, approval.rationale)
        notify_requestor(approval.rationale)
```

---

### RA-5: Critical

**Characteristics**:

- Probability: >50%
- Impact: Critical (5)
- Examples: Emergency rollbacks, database migrations, security incident response

**Approval**: **Requires multi-party approval**
**Logging**: Required + detailed + archived + reported to stakeholders
**Agent**: All agents coordinate; OC-03 gates

**Governance**:

```python
if task.risk_level == RiskLevel.RA_5:
    prb_score = calculate_prb(task)
    log_action_with_prb(task, prb_score)

    # BLOCK until multiple humans approve
    approvals = request_multi_party_approval(task, prb_score, required_approvers=3)

    if len(approvals.approved) >= 3:
        execute_with_safeguards()
        log_result(task, approvals)
        archive_approvals(approvals)
        notify_stakeholders(task, "EXECUTED")
    else:
        log_rejection(task, approvals)
        notify_stakeholders(task, "REJECTED")
```

---

## Approval Gates

### Human Approval Interface

When OrangeCreek (OC-03) encounters an RA-4 or RA-5 task, it presents:

```
========================================
APPROVAL REQUIRED
========================================
Risk Level: RA-4 (High Risk)
Agent: OC-03 (OrangeCreek)
Task ID: bevy-deploy-001

Description:
  Deploy Bevy plugin v1.0 to production

PRB Analysis:
  Probability: 15% (Possible)
  Impact: Moderate (partial feature failure, rollback available)
  Benefit: High (enables real-time agent control for 1000+ users)
  Mitigation: Strong (tested in staging, rollback script ready)

  Decision Score: 16.0 / 10.0 (APPROVE recommended)

Risks:
  - Plugin may conflict with existing Bevy systems
  - Performance impact unknown in production scale
  - Users may experience temporary lag during initialization

Mitigations:
  - Canary deployment to 10% of users first
  - Rollback script tested and ready (< 2 minute recovery)
  - Monitoring dashboards configured with alerts

Approve this task? (yes/no/defer):
```

**Response Options**:

- `yes` + rationale → Task proceeds, logged to audit trail
- `no` + rationale → Task rejected, sent back to requesting agent
- `defer` + reason → Task moved to pending queue for later review

---

## Audit Trail

### Logging Structure

All actions logged to GCS:

```
gs://{BUCKET}/audit-logs/{YYYY}/{MM}/{DD}/{agent_id}-{task_id}.json
```

**Log Entry Format**:

```json
{
  "timestamp": "2025-11-14T12:34:56.789Z",
  "agent_id": "OC-03",
  "task_id": "bevy-deploy-001",
  "risk_level": "RA-4",
  "action": "deploy_bevy_plugin",
  "prb_analysis": {
    "probability": 0.15,
    "impact": 3,
    "benefit": 4,
    "mitigation_factor": 1.8,
    "decision_score": 16.0,
    "threshold": 10.0
  },
  "approval": {
    "required": true,
    "approver": "human_operator_01",
    "status": "approved",
    "rationale": "Staging tests passed, rollback ready, low user impact window",
    "timestamp": "2025-11-14T12:40:23.456Z"
  },
  "execution": {
    "status": "success",
    "duration_seconds": 45.2,
    "output": "Plugin deployed successfully to production"
  }
}
```

### Audit Retention

- **RA-1, RA-2**: 30 days
- **RA-3**: 90 days
- **RA-4**: 1 year
- **RA-5**: 7 years (compliance requirement)

### Audit Access

- **Developers**: Read access to own agent logs
- **Team Leads**: Read access to all agent logs
- **Compliance**: Full access including deleted items

---

## Judge #6 Protocol

**Judge #6** is OrangeCreek's (OC-03) enforcement mechanism for test coverage.

### Coverage Requirements

- **Minimum**: 98% line coverage
- **Measurement**: cargo-tarpaulin (Rust), pytest-cov (Python)
- **Exclusions**: Generated code, test files themselves, example/demo code

### Enforcement Actions

#### Coverage ≥ 98%: PASS

```
✅ PASS - Coverage: 98.5%
   Lines covered: 985 / 1000

   Proceed to deployment gate.
```

#### Coverage < 98%: FAIL

```
❌ FAIL - Coverage: 94.2%
   Lines covered: 942 / 1000
   Missing coverage: 58 lines

   Uncovered code paths:
   - src/plugins/claude_agent.rs:145-152 (error handling)
   - src/systems/agent_sync.rs:78-82 (edge case: empty entity list)

   Required actions:
   1. Add test case for error handling in claude_agent.rs
   2. Add test case for empty entity list in agent_sync.rs
   3. Re-run: cargo tarpaulin --out Html
   4. Resubmit to OrangeCreek for validation

   Deployment BLOCKED until coverage ≥ 98%.
```

### Coverage Exemptions

Exemptions require **RA-4 approval** with rationale:

```
Exemption Request:
  File: src/experimental/new_feature.rs
  Current Coverage: 85%
  Reason: Feature still in development, will reach 98% before GA release

  Approve exemption? (yes/no):
```

---

## Incident Response

### Incident Classification

#### P0: Critical (RA-5)

- Production outage affecting all users
- Security breach with data exposure
- Irreversible data loss

**Response**: Immediate escalation, multi-party approval for fixes

#### P1: High (RA-4)

- Production outage affecting >10% of users
- Performance degradation >50%
- Security vulnerability discovered (not yet exploited)

**Response**: Within 1 hour, human approval for fixes

#### P2: Medium (RA-3)

- Production outage affecting <10% of users
- Performance degradation 20-50%
- Non-critical bug in new feature

**Response**: Within 4 hours, reviewed approval for fixes

#### P3: Low (RA-2)

- Minor bugs affecting few users
- Cosmetic issues
- Non-blocking feature requests

**Response**: Within 1 business day, auto-approved fixes

---

### Incident Workflow

1. **Detection**: Agent or human identifies issue
2. **Classification**: Assign priority (P0-P3) and risk level (RA-1 to RA-5)
3. **Notification**: Alert appropriate stakeholders based on priority
4. **Triage**: WhiteCastle (WC-01) analyzes root cause and proposes fix
5. **Implementation**: BrownSnow (BS-02) implements fix
6. **Validation**: OrangeCreek (OC-03) validates fix with tests
7. **Approval**: Human approves deployment (RA-4+) or auto-deployed (RA-3-)
8. **Deployment**: Fix deployed with rollback plan ready
9. **Post-Mortem**: Document incident, root cause, fix, and prevention

---

## Best Practices

### For Developers

1. **Always document PRB reasoning** in code comments for RA-3+ changes
2. **Test before submitting** to OrangeCreek to avoid rejection loops
3. **Provide clear rollback plans** for RA-4+ deployments
4. **Review audit logs weekly** to catch patterns and improve processes

### For Operators

1. **Respond to RA-4 approvals within 1 hour** (set up alerts)
2. **Defer if uncertain**; better to investigate than approve blindly
3. **Document approval rationale** clearly for future audit review
4. **Escalate RA-5 items** to team lead immediately

### For Compliance

1. **Audit RA-4+ logs monthly** for anomalies
2. **Verify coverage reports** match actual test execution
3. **Review exemption requests** quarterly to ensure they haven't become permanent
4. **Maintain ATP 5-19 compliance documentation** up to date

---

## Configuration

### Thresholds (Adjustable per Environment)

```python
# Production
PRB_THRESHOLDS = {
    RiskLevel.RA_1: 0.0,   # Always approve
    RiskLevel.RA_2: 0.0,   # Always approve (with logging)
    RiskLevel.RA_3: 5.0,   # Must have PRB score > 5.0
    RiskLevel.RA_4: 10.0,  # Must have PRB score > 10.0 + human approval
    RiskLevel.RA_5: 20.0,  # Must have PRB score > 20.0 + multi-party approval
}

# Staging (more lenient)
PRB_THRESHOLDS_STAGING = {
    RiskLevel.RA_1: 0.0,
    RiskLevel.RA_2: 0.0,
    RiskLevel.RA_3: 2.0,  # Lower threshold
    RiskLevel.RA_4: 5.0,  # Lower threshold
    RiskLevel.RA_5: 10.0,
}

# Development (minimal gates)
PRB_THRESHOLDS_DEV = {
    RiskLevel.RA_1: 0.0,
    RiskLevel.RA_2: 0.0,
    RiskLevel.RA_3: 0.0,  # Auto-approve
    RiskLevel.RA_4: 0.0,  # Auto-approve (log only)
    RiskLevel.RA_5: 5.0,
}
```

---

## Versioning

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Based On**: ATP 5-19 (Army Techniques Publication 5-19, Risk Management, April 2014)

---

## References

- [ATP 5-19 Risk Management](https://armypubs.army.mil/epubs/DR_pubs/DR_a/pdf/web/atp5_19.pdf)
- [AGENTS.md](./AGENTS.md) - Agent registry and capabilities
- [PREFLIGHT_CHECKLIST.md](./PREFLIGHT_CHECKLIST.md) - Deployment checklist
- [Judge #6 Coverage Protocol](./AGENTS.md#judge-6-protocol)
