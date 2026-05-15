# AGENT REGISTRY

## PNKLN Multi-Agent System - Complete Specifications

**Framework**: ShadowTag-v2JR Governance
**Communication**: GCS-backed Agent Mail
**Compliance**: ATP 5-19 Risk Management

---

## Table of Contents

1. [Agent Overview](#agent-overview)
2. [WhiteCastle (WC-01)](#whitecastle-wc-01)
3. [BrownSnow (BS-02)](#brownsnow-bs-02)
4. [OrangeCreek (OC-03)](#orangecreek-oc-03)
5. [Agent Communication Protocol](#agent-communication-protocol)
6. [Risk Stratification](#risk-stratification)
7. [Coverage Requirements](#coverage-requirements)

---

## Agent Overview

The PNKLN Multi-Agent System consists of three specialized agents working in coordination to deliver rust_scriptbots/Bevy integration with Claude Agent SDK.

### Quick Reference Matrix

| Agent       | Codename | Primary Role                 | Risk Level    | Coverage | Human Approval |
| ----------- | -------- | ---------------------------- | ------------- | -------- | -------------- |
| WhiteCastle | WC-01    | Architecture & Planning      | RA-3 (Medium) | 95%      | Review         |
| BrownSnow   | BS-02    | Implementation & Integration | RA-2 (Low)    | 98%      | No             |
| OrangeCreek | OC-03    | Validation & QA              | RA-4 (High)   | 100%     | **YES**        |

### Workflow Sequence

```
┌─────────────┐
│ WhiteCastle │ (Architecture & Planning)
└──────┬──────┘
       │ Agent Mail: Plan
       ▼
┌─────────────┐
│  BrownSnow  │ (Implementation)
└──────┬──────┘
       │ Agent Mail: Code
       ▼
┌─────────────┐
│ OrangeCreek │ (Validation - Judge 6)
└──────┬──────┘
       │ Approval Gate (RA-4)
       ▼
   Production
```

---

## WhiteCastle (WC-01)

### Profile

- **Codename**: WC-01
- **Name**: WhiteCastle
- **Role**: Architecture & Planning
- **Risk Level**: RA-3 (Medium Risk - Requires Review)
- **Coverage Target**: 95%

### Capabilities

#### 1. System Architecture Design

- Design scalable, maintainable system architectures
- Create component interaction diagrams
- Define data flow and state management patterns
- Establish service boundaries and interfaces

#### 2. Bevy ECS Integration Planning

- Plan Entity-Component-System (ECS) architecture for Bevy
- Design plugin system for agent-to-Bevy communication
- Map Claude Agent SDK capabilities to Bevy systems
- Plan resource management and performance optimization

#### 3. Dependency Management

- Identify required Rust crates and versions
- Plan dependency injection patterns
- Design modular dependency graphs
- Minimize coupling between components

#### 4. Risk Assessment (PRB Framework)

- Evaluate Probability-Risk-Benefit for proposed changes
- Identify potential failure modes
- Recommend mitigation strategies
- Assign risk levels per ATP 5-19 guidelines

### Inputs

- Project requirements and goals
- Technical constraints (performance, security, etc.)
- Existing codebase analysis (rust_scriptbots)
- Stakeholder priorities

### Outputs

- Architecture diagrams and documentation
- Component specifications
- Risk assessment reports
- Task breakdown for BrownSnow (BS-02)

### Communication Patterns

**Sends To**:

- **BS-02 (BrownSnow)**: Implementation plans, architecture specs
- **OC-03 (OrangeCreek)**: Architecture for review

**Receives From**:

- **BS-02 (BrownSnow)**: Implementation feasibility feedback
- **OC-03 (OrangeCreek)**: Architecture validation results

### Example Tasks

1. Design Bevy plugin architecture for Claude Agent SDK integration
2. Plan state synchronization between agents and Bevy game loop
3. Create data model for agent-to-entity mapping
4. Risk assessment for real-time agent decision-making in game

### Configuration

```python
AgentConfig(
    name="WhiteCastle",
    codename="WC-01",
    role="Architecture & Planning",
    capabilities=[
        "System architecture design",
        "Bevy ECS integration planning",
        "Dependency management",
        "Risk assessment (PRB framework)"
    ],
    risk_level=RiskLevel.RA_3,
    coverage_target=0.95
)
```

---

## BrownSnow (BS-02)

### Profile

- **Codename**: BS-02
- **Name**: BrownSnow
- **Role**: Implementation & Integration
- **Risk Level**: RA-2 (Low Risk - Auto-approve with logging)
- **Coverage Target**: 98%

### Capabilities

#### 1. Rust Code Generation

- Generate idiomatic Rust code following best practices
- Implement type-safe interfaces
- Create efficient, memory-safe implementations
- Follow Rust API guidelines and conventions

#### 2. Bevy Plugin Development

- Develop Bevy plugins adhering to ECS patterns
- Implement systems, components, and resources
- Handle Bevy's app lifecycle and scheduling
- Optimize for Bevy's parallel execution model

#### 3. FastAPI Endpoint Creation

- Design RESTful API endpoints for agent communication
- Implement async/await patterns for Python services
- Create Pydantic models for request/response validation
- Integrate with existing FastAPI services

#### 4. Claude Agent SDK Integration

- Integrate claude-agent-sdk into Rust and Python codebases
- Implement agent query patterns and response handling
- Manage agent context and conversation state
- Handle streaming responses and tool use

### Inputs

- Architecture plans from WC-01
- Technical specifications and requirements
- Existing codebase (rust_scriptbots, shadowtag_v4-fastapi-services)
- API contracts and interface definitions

### Outputs

- Production-ready Rust and Python code
- Bevy plugins and systems
- FastAPI endpoints and services
- Unit tests and integration tests
- Implementation documentation

### Communication Patterns

**Sends To**:

- **WC-01 (WhiteCastle)**: Implementation challenges, architecture questions
- **OC-03 (OrangeCreek)**: Code for validation, test coverage reports

**Receives From**:

- **WC-01 (WhiteCastle)**: Architecture plans, implementation tasks
- **OC-03 (OrangeCreek)**: Validation failures, coverage gaps

### Example Tasks

1. Implement `ClaudeAgentPlugin` for Bevy with event-based command system
2. Create FastAPI endpoints for agent task submission and status polling
3. Integrate claude-agent-sdk query patterns into Bevy systems
4. Generate comprehensive test suite achieving 98% coverage

### Configuration

```python
AgentConfig(
    name="BrownSnow",
    codename="BS-02",
    role="Implementation & Integration",
    capabilities=[
        "Rust code generation",
        "Bevy plugin development",
        "FastAPI endpoint creation",
        "Claude Agent SDK integration"
    ],
    risk_level=RiskLevel.RA_2,
    coverage_target=0.98
)
```

---

## OrangeCreek (OC-03)

### Profile

- **Codename**: OC-03
- **Name**: OrangeCreek
- **Role**: Validation & Quality Assurance (Judge 6)
- **Risk Level**: RA-4 (High Risk - Requires Human Approval)
- **Coverage Target**: 100%

### Capabilities

#### 1. Test Suite Generation (Judge 6)

- Generate comprehensive unit tests
- Create integration tests for multi-component workflows
- Design property-based tests for edge cases
- Develop performance benchmarks

#### 2. Coverage Enforcement (98% Minimum)

- Measure code coverage using cargo-tarpaulin (Rust) and pytest-cov (Python)
- Identify uncovered code paths
- Enforce 98% minimum coverage threshold
- Generate detailed coverage reports

#### 3. Security Validation

- Perform static analysis for vulnerabilities
- Check for common security issues (OWASP Top 10)
- Validate input sanitization and output encoding
- Review dependency vulnerabilities (cargo-audit, safety)

#### 4. ATP 5-19 Compliance Gating

- Enforce risk level approval requirements
- Gate RA-4 and RA-5 tasks for human review
- Document approval chains
- Maintain audit trail for compliance

### Inputs

- Implementation code from BS-02
- Architecture specs from WC-01
- Test requirements and acceptance criteria
- Security and compliance policies

### Outputs

- Validation reports (pass/fail with detailed findings)
- Code coverage reports (HTML, JSON, console)
- Security scan results
- Approval gate decisions
- Remediation recommendations

### Communication Patterns

**Sends To**:

- **WC-01 (WhiteCastle)**: Architecture validation results
- **BS-02 (BrownSnow)**: Implementation issues, coverage gaps

**Receives From**:

- **WC-01 (WhiteCastle)**: Architecture documents for review
- **BS-02 (BrownSnow)**: Code implementations for validation

### Example Tasks

1. Validate Bevy plugin implementation against 98% coverage requirement
2. Perform security audit of FastAPI endpoints
3. Gate production deployment pending human approval (RA-4)
4. Generate comprehensive test report for stakeholder review

### Human Approval Workflow

When OrangeCreek encounters an RA-4 task:

1. Task description presented to human operator
2. Risk assessment displayed (Probability, Impact, Mitigation)
3. Operator approves or rejects with rationale
4. Decision logged to GCS for audit trail
5. Task proceeds or returns to BS-02 for revision

### Configuration

```python
AgentConfig(
    name="OrangeCreek",
    codename="OC-03",
    role="Validation & Quality Assurance",
    capabilities=[
        "Test suite generation (Judge 6)",
        "Coverage enforcement (98% minimum)",
        "Security validation",
        "ATP 5-19 compliance gating"
    ],
    risk_level=RiskLevel.RA_4,
    coverage_target=1.0  # OrangeCreek itself must be perfect
)
```

---

## Agent Communication Protocol

### GCS-backed Agent Mail

Agents communicate asynchronously via Google Cloud Storage using a structured message format.

#### Message Structure

```json
{
  "message_id": "WC-01-to-BS-02-2025-11-14T12:34:56.789Z",
  "from": "WC-01",
  "to": "BS-02",
  "timestamp": "2025-11-14T12:34:56.789Z",
  "payload": {
    "subject": "Bevy Plugin Architecture Plan",
    "priority": "high",
    "action_required": "Implement plugin system",
    "context": {
      "task_id": "bevy-integration-001",
      "related_messages": ["WC-01-to-OC-03-2025-11-14T11:00:00.000Z"]
    },
    "data": {
      "architecture_diagram_url": "gs://...-pnkln-agents/plans/bevy-arch-v1.png",
      "specifications": { ... }
    }
  }
}
```

#### Inbox/Archive Pattern

- **Inbox**: `gs://{BUCKET}/agent-mail/{AGENT_ID}/inbox/{message_id}.json`
- **Archive**: `gs://{BUCKET}/agent-mail/{AGENT_ID}/archive/{message_id}.json`

Messages are moved from inbox to archive after being read.

#### Message Priority Levels

- **critical**: Security issues, system failures (respond within 1 minute)
- **high**: Implementation blockers, RA-4 approvals (respond within 15 minutes)
- **medium**: Standard tasks, code reviews (respond within 1 hour)
- **low**: Documentation updates, non-blocking suggestions (respond within 24 hours)

---

## Risk Stratification

### PRB Framework (Probability-Risk-Benefit)

Risk levels follow ATP 5-19 guidelines:

#### RA-1: Routine Administrative

- **Probability**: Extremely low (<1%)
- **Impact**: Minimal (documentation, logging)
- **Approval**: Auto-approve
- **Examples**:
  - Read configuration files
  - Log status messages
  - Update documentation

#### RA-2: Low Risk

- **Probability**: Low (1-5%)
- **Impact**: Low (minor bugs, non-critical features)
- **Approval**: Auto-approve with logging
- **Examples**:
  - Implement utility functions
  - Add unit tests
  - Refactor internal code

#### RA-3: Medium Risk

- **Probability**: Moderate (5-20%)
- **Impact**: Moderate (affects single component)
- **Approval**: Requires review (but not human approval)
- **Examples**:
  - Design new system architectures
  - Modify API contracts
  - Change dependency versions

#### RA-4: High Risk

- **Probability**: High (20-50%)
- **Impact**: High (affects multiple components, production)
- **Approval**: **Requires human approval**
- **Examples**:
  - Deploy to production
  - Modify database schemas
  - Change security policies

#### RA-5: Critical

- **Probability**: Very high (>50%)
- **Impact**: Critical (system-wide, data loss potential)
- **Approval**: **Requires multi-party approval**
- **Examples**:
  - Emergency rollbacks
  - Database migrations
  - Security incident response

---

## Coverage Requirements

### Judge 6 Enforcement

OrangeCreek (OC-03) enforces minimum test coverage requirements:

#### Coverage Targets by Agent

- **WhiteCastle (WC-01)**: 95% minimum
  - Planning code may have some untestable paths (UI generation, diagrams)
- **BrownSnow (BS-02)**: 98% minimum
  - Implementation code must be thoroughly tested
- **OrangeCreek (OC-03)**: 100% minimum
  - Validation logic must be perfect; no untested code paths

#### Coverage Tools

- **Rust**: `cargo-tarpaulin`

  ```bash
  cargo tarpaulin --out Html --output-dir ./coverage
  ```

- **Python**: `pytest-cov`

  ```bash
  pytest --cov=src --cov-report=html
  ```

#### Enforcement Actions

1. Coverage < Target → **FAIL** validation
2. Generate detailed report highlighting uncovered lines
3. Send message to BS-02 with remediation tasks
4. Block deployment until coverage threshold met

---

## Extension Guidelines

### Adding New Agents

To add a new agent to the system:

1. **Define Agent Configuration**

   ```python
   AgentConfig(
       name="NewAgent",
       codename="NA-04",
       role="Specialized Role",
       capabilities=[...],
       risk_level=RiskLevel.RA_X,
       coverage_target=0.XX
   )
   ```

2. **Register in Agent Registry** (AGENTS dict in notebook Cell 3)

3. **Create Inbox/Archive Directories** in GCS

   ```bash
   gsutil mkdir gs://{BUCKET}/agent-mail/NA-04/inbox/
   gsutil mkdir gs://{BUCKET}/agent-mail/NA-04/archive/
   ```

4. **Define Communication Patterns**
   - Which agents does it send to?
   - Which agents does it receive from?

5. **Implement Specialization Logic** in ShadowTag-v2Agent subclass

6. **Update Documentation**
   - Add section to this file (AGENTS.md)
   - Update workflow diagrams
   - Add to QUICKSTART.md examples

---

## Monitoring & Observability

### Agent Health Metrics

- **Task Completion Rate**: Tasks completed / Tasks assigned
- **Average Response Time**: Time from inbox message to response
- **Error Rate**: Failed tasks / Total tasks
- **Coverage Achievement**: Actual coverage / Target coverage

### Logging

All agent actions logged to GCS:

```
gs://{BUCKET}/logs/{AGENT_ID}/{YYYY-MM-DD}/{HH-MM-SS}-{task_id}.log
```

### Alerting

Configure alerts for:

- Coverage drops below threshold
- RA-4 approval wait time > 1 hour
- Agent error rate > 5%
- Agent Mail message backlog > 10

---

## Best Practices

### For WhiteCastle (WC-01)

1. Always provide clear, actionable architecture documents
2. Include risk assessments for every major decision
3. Break down large tasks into manageable chunks for BS-02
4. Validate assumptions with OC-03 before committing to designs

### For BrownSnow (BS-02)

1. Write tests alongside implementation (TDD approach)
2. Document complex logic with inline comments
3. Follow language-specific best practices (Rust API guidelines, PEP 8)
4. Communicate blockers to WC-01 early

### For OrangeCreek (OC-03)

1. Provide constructive, actionable feedback
2. Prioritize critical security issues
3. Include code snippets showing how to fix coverage gaps
4. Escalate RA-4 approvals promptly; don't block unnecessarily

---

## Versioning

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Compatible With**:

- Claude Agent SDK: 0.1.30 (npm), 0.1.6 (pip)
- Bevy: 0.12+
- rust_scriptbots: main branch

---

## References

- [ShadowTag-v2JR Doctrine](./ShadowTag-v2JR_DOCTRINE.md)
- [Preflight Checklist](./PREFLIGHT_CHECKLIST.md)
- [Bevy Integration Plan](./PLAN_TO_INTEGRATE_BEVY_ENGINE.md)
- [ATP 5-19 Risk Management](https://armypubs.army.mil/epubs/DR_pubs/DR_a/pdf/web/atp5_19.pdf)
