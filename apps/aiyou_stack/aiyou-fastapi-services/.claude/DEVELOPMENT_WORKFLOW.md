# ShadowTag-v2JR FastAPI Development Workflow

## Overview

This document defines the complete development workflow for the ShadowTag-v2JR FastAPI services, incorporating SOPs, custom skills, and deployment to Vertex AI Workbench → GKE Native.

## Core Doctrine

**Purpose**: ShadowTag-v2JR mission advancement
**Reason**: Evidence-based engineering doctrine
**Brakes**: Army Risk Management (ATP 5-19)

**Operating Posture**: Strict mode (IQ baseline 160)

## Standard Operating Procedures (SOPs)

### SOP-A: Upload Triage (2× speed, −90% errors)

**Objective**: Rapid, accurate assessment of code changes before integration.

**Process:**


1. **Automated Checks** (run via session start hook):


   - Dependency scan (Safety, Pip-audit)


   - Type checking (mypy)


   - Linting (ruff)


   - Security scan (bandit)


   - Test suite (pytest)



2. **Manual Review Gates**:


   - Security impact assessment


   - Revenue impact analysis


   - Breaking change identification


   - Documentation completeness



3. **Triage Decision Matrix**:


   - **Green**: All checks pass → Fast-track to SOP-B


   - **Yellow**: Minor issues → Fix then fast-track


   - **Red**: Critical issues → Block until resolved

**Success Metrics**:


- Review time: <10 minutes


- False positive rate: <5%


- Critical issues caught: 100%

### SOP-B: Change & Release (2× cadence, clearer audits)

**Objective**: Safe, rapid deployment with full traceability.

**Process:**



1. **Pre-Deployment Checklist**:


   - [ ] All SOP-A checks passed


   - [ ] Database migrations tested (if applicable)


   - [ ] Environment variables documented


   - [ ] Rollback plan prepared


   - [ ] Monitoring/alerts configured


   - [ ] Performance benchmarks recorded



2. **Deployment Pipeline**:
   ```bash
   # Stage 1: Local validation
   pytest tests/ --cov=app --cov-report=term-missing
   mypy app/
   ruff check app/
   bandit -r app/

   # Stage 2: Staging (Vertex AI Workbench)
   gcloud compute ssh workbench-instance --command "cd /app && docker-compose up -d"
   ./scripts/run_integration_tests.sh staging

   # Stage 3: Production (GKE)
   kubectl apply -f k8s/deployment.yaml
   kubectl rollout status deployment/shadowtag_v4-api
   ./scripts/smoke_test.sh production

   # Stage 4: Verification
   ./scripts/verify_deployment.sh
   ```



3. **Audit Trail**:


   - Git commit SHA


   - Deployment timestamp


   - Who approved


   - What changed (semantic changelog)


   - Performance impact


   - Rollback commands



4. **Rollback Criteria**:


   - Error rate >1%


   - Response time p95 >500ms


   - Failed health checks


   - Security vulnerability discovered

**Success Metrics**:


- Deployment time: <15 minutes


- Rollback time: <5 minutes


- Deployment success rate: >99%

### SOP-C: Decision Protocol (2× faster, +1.8× robustness)

**Objective**: Fast, evidence-based decisions using Army Risk Management.

**Risk Assessment Framework**:

**Probability Scale**:


- **A**: >90% likely


- **B**: 70-90%


- **C**: 40-70%


- **D**: 10-40%


- **E**: <10%

**Severity Scale**:


- **I**: Catastrophic (data breach, service down, revenue loss >$10k)


- **II**: Critical (major feature broken, revenue loss $1k-$10k)


- **III**: Moderate (minor feature broken, user friction)


- **IV**: Minimal (cosmetic, no user impact)

**Risk Level Matrix**:

```

          Severity
          I    II   III  IV
Prob  A   EH   H    M    L
      B   EH   H    M    L
      C   H    M    M    L
      D   M    M    L    L
      E   M    L    L    L

```

**Decision Rules**:


- **EH (Extremely High)**: Stop work, escalate, mitigate immediately


- **H (High)**: Mitigate before proceeding, document plan


- **M (Moderate)**: Accept with monitoring


- **L (Low)**: Accept

**Decision Template**:

```markdown

## Decision: [Title]

**Context**: What are we deciding?

**Options**:


1. Option A: [Description]


   - Pros: ...


   - Cons: ...


   - Risk: [Probability + Severity] = [Level]


   - Cost: Time/Money



2. Option B: [Description]


   - Pros: ...


   - Cons: ...


   - Risk: [Probability + Severity] = [Level]


   - Cost: Time/Money

**Evidence**:


- Data point 1


- Data point 2


- Reference doc

**Recommendation**: Option [X]
**Rationale**: [Evidence-based reasoning]
**Risk Mitigation**: [If H or EH]

**Approval**: [Name] on [Date]

```

**Success Metrics**:


- Decision time: <1 hour for routine, <1 day for strategic


- Evidence-backed: 100%


- Post-decision regret: <10%

### SOP-D: Code Review (+2× defect capture)

**Objective**: Catch defects before production using systematic review.

**Review Checklist**:

**1. Security (Non-Negotiable)**:


- [ ] Input validation on all endpoints


- [ ] Authentication/authorization enforced


- [ ] SQL injection prevention (use ORM)


- [ ] XSS prevention (Pydantic validation)


- [ ] Secrets in Secret Manager (not code)


- [ ] Rate limiting implemented


- [ ] Security scan clean (Bandit)

**2. Architecture**:


- [ ] Boy Scout Rule: cleaner than found


- [ ] Single Responsibility Principle


- [ ] Functions ≤20 lines


- [ ] Clear abstractions, minimal coupling


- [ ] No premature optimization

**3. Testing**:


- [ ] Test coverage ≥80%


- [ ] Tests follow AAA (Arrange-Act-Assert)


- [ ] Edge cases covered


- [ ] Error paths tested


- [ ] Integration tests for API endpoints

**4. Revenue**:


- [ ] Monetization strategy documented


- [ ] Usage tracking implemented (if applicable)


- [ ] Tier gates configured


- [ ] Conversion prompts added

**5. Documentation**:


- [ ] API contract documented


- [ ] Docstrings explain WHY (not what)


- [ ] README updated (if applicable)


- [ ] CHANGELOG updated

**6. Performance**:


- [ ] No N+1 queries


- [ ] Appropriate indexes


- [ ] Response time <200ms (p95)


- [ ] Resource usage reasonable

**Review SLA**:


- Small PRs (<200 lines): <2 hours


- Medium PRs (200-500 lines): <4 hours


- Large PRs (>500 lines): Break down or <8 hours

**Success Metrics**:


- Defects caught in review: >90%


- Defects escaped to production: <1 per month


- Review time within SLA: >95%

## Skills Integration

**Custom skills automatically activate based on context:**



1. **fastapi-endpoint-development**: When creating/modifying API endpoints


2. **api-security-validation**: When reviewing security, auth, or validation


3. **revenue-optimization**: When adding features or analyzing monetization

**To manually invoke a skill:**

```

/skill:fastapi-endpoint-development

```

## Development Lifecycle

### 1. Feature Planning

**Inputs**:


- User story or requirement


- Revenue target (if applicable)


- Security requirements

**Process**:


1. Use SOP-C Decision Protocol


2. Create decision document


3. Assess risk (Probability × Severity)


4. Get approval if H or EH risk

**Outputs**:


- Approved decision document


- Feature specification


- Risk mitigation plan

### 2. Implementation

**Process**:


1. **Activate skill**: fastapi-endpoint-development


2. **Follow TDD cycle**:


   - Write tests (happy path, edge cases, errors)


   - Implement to pass tests


   - Refactor (Boy Scout Rule)


3. **Security review**: Use api-security-validation skill


4. **Revenue integration**: Use revenue-optimization skill


5. **Documentation**: Update API docs

**Outputs**:


- Working code with tests


- Security validation complete


- Revenue tracking implemented

### 3. Code Review

**Process**:


1. Create PR with template


2. Run SOP-A automated checks


3. Request review from team member


4. Address feedback using SOP-D checklist


5. Get approval

**Outputs**:


- Approved PR


- All checks passed


- Review comments addressed

### 4. Deployment

**Process**:


1. Follow SOP-B Change & Release


2. Deploy to staging (Vertex AI Workbench)


3. Run integration tests


4. Deploy to production (GKE)


5. Monitor for issues

**Outputs**:


- Live feature in production


- Monitoring alerts configured


- Rollback plan ready

### 5. Monitoring & Iteration

**Process**:


1. Track key metrics:


   - Error rate


   - Response time (p50, p95, p99)


   - Usage (API calls, active users)


   - Revenue (if applicable)


2. Identify issues or optimization opportunities


3. Create new feature/fix cycle

**Outputs**:


- Performance data


- User feedback


- Optimization backlog

## Tool Stack

### Development



- **Language**: Python 3.11+


- **Framework**: FastAPI


- **ORM**: SQLAlchemy


- **Validation**: Pydantic


- **Testing**: pytest, pytest-cov


- **Type Checking**: mypy


- **Linting**: ruff


- **Security**: bandit, safety

### Infrastructure



- **Cloud**: Google Cloud Platform (GCP) exclusive


- **Development**: Vertex AI Workbench


- **Production**: GKE Native


- **Secrets**: Google Secret Manager


- **Monitoring**: Cloud Monitoring, Cloud Logging


- **Database**: Cloud SQL (PostgreSQL)


- **Cache**: Memorystore (Redis)

### CI/CD



- **VCS**: Git + GitHub


- **CI**: GitHub Actions


- **CD**: Cloud Build → GKE


- **Container**: Docker

## Quality Gates

**No exceptions. These must pass:**



1. **Security**: No critical/high vulnerabilities


2. **Tests**: Coverage ≥80%, all passing


3. **Types**: mypy strict mode clean


4. **Linting**: ruff clean


5. **Performance**: Response time p95 <200ms


6. **Documentation**: API contract complete

**If any gate fails**: Block deployment, fix immediately.

## Bootstrap Discipline

**Financial Constraints** (non-negotiable):


- ROI ≥3× within 18 months


- LTV:CAC ≥4:1 within 12 months


- Kill-switch on features not meeting targets

**Evidence-Only Decisions**:


- No opinions, only data


- Document assumptions


- Test hypotheses


- Measure outcomes

## Common Workflows

### Creating a New Endpoint

```bash

# 1. Plan (SOP-C)

# Create decision doc, assess risk

# 2. Activate skill

/skill:fastapi-endpoint-development

# 3. Write tests first

cat > tests/test_api_resource.py <<EOF

# Test code here...

EOF

pytest tests/test_api_resource.py  # Should fail (no implementation yet)

# 4. Implement

cat > app/api/v1/endpoints/resource.py <<EOF

# Implementation here...

EOF

pytest tests/test_api_resource.py  # Should pass

# 5. Security review

/skill:api-security-validation

# 6. Revenue integration (if applicable)

/skill:revenue-optimization

# 7. Create PR

git add .
git commit -m "Add resource endpoint with TDD, security, and revenue tracking"
git push origin feature/resource-endpoint

# 8. Code review (SOP-D)

# Request review via GitHub

# 9. Deploy (SOP-B)

# Merge → CI/CD pipeline → GKE

```

### Fixing a Security Issue

```bash

# 1. Assess severity (SOP-C)

# I = Catastrophic? II = Critical?

# 2. If critical, activate incident response

# Stop deployment pipeline

# 3. Activate security skill

/skill:api-security-validation

# 4. Write test reproducing vulnerability

pytest tests/test_security_issue.py  # Should fail

# 5. Fix and verify

# Implement fix

pytest tests/test_security_issue.py  # Should pass

# 6. Run full security scan

bandit -r app/
safety check

# 7. Fast-track review (SOP-D)

# Get immediate review from security-cleared team member

# 8. Deploy ASAP (SOP-B)

# Production hotfix process

```

### Analyzing Revenue Opportunity

```bash

# 1. Activate revenue skill

/skill:revenue-optimization

# 2. Gather usage data

# Query analytics for feature usage, tier distribution

# 3. Identify opportunities

# Features frequently blocked by tier?

# Users near quota limits?

# High engagement but low tier?

# 4. Plan monetization (SOP-C)

# Decision doc with revenue projections

# 5. Implement

# Add tier gates, usage tracking, upgrade prompts

# 6. Deploy and measure

# A/B test pricing, track conversions

```

## Emergency Procedures

### Security Breach



1. **Contain**: Disable affected endpoints


2. **Assess**: Determine scope of breach


3. **Mitigate**: Patch vulnerability


4. **Notify**: Inform affected users (if PII exposed)


5. **Post-mortem**: Document lessons learned

### Service Outage



1. **Detect**: Monitoring alerts


2. **Triage**: Severity assessment


3. **Rollback**: Use SOP-B rollback procedure


4. **Root Cause**: Use systematic debugging skill


5. **Fix**: Implement and deploy


6. **Post-mortem**: Update runbooks

### Performance Degradation



1. **Identify**: Slow query? High CPU? Network?


2. **Profile**: Use APM tools


3. **Optimize**: Fix bottleneck


4. **Verify**: Load test


5. **Deploy**: Gradual rollout

## Success Metrics

**Velocity**:


- Feature idea → production: <1 week


- Bug report → fix deployed: <1 day (critical), <1 week (normal)

**Quality**:


- Production defects: <1 per month


- Security incidents: 0


- Test coverage: ≥80%

**Revenue**:


- ROI: ≥3× in 18 months


- LTV:CAC: ≥4:1 in 12 months


- Feature monetization rate: >50%

**Operations**:


- Uptime: >99.9%


- Response time p95: <200ms


- Deployment success rate: >99%

## Resources



- **SOPs**: This document


- **Skills**: `.claude/skills/`


- **Templates**: `.claude/templates/`


- **Runbooks**: `docs/runbooks/`


- **Architecture**: `docs/architecture/`

---

**Ultrathink Mode**: Obsess over details like masterpiece studies. Question assumptions. Re-examine from zero. Iterate to insanely great. Simplify to elegance (nothing left to remove).
