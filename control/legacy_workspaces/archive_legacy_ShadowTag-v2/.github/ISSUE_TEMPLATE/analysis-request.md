---
name: Analysis Request
about: Request a structured analysis of a system component
title: '[ANALYSIS] '
labels: analysis
assignees: ''
---

## Context

### Component/System
[What component or system needs analysis?]

### Current State
[Brief description of the current situation]

### Driving Force
[Why is this analysis needed now?]
- [ ] Performance concerns
- [ ] Cost optimization
- [ ] Architecture review
- [ ] Security audit
- [ ] Pre-production validation
- [ ] Other: [specify]

---

## Scope

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item 1]
- [Item 2]

### Data Sources Available
- [ ] Architecture specs/documentation
- [ ] Performance metrics/logs
- [ ] Cost data
- [ ] User feedback
- [ ] Code access
- [ ] Other: [specify]

---

## Analysis Requirements

### Key Questions to Answer
1. [Question 1]
2. [Question 2]
3. [Question 3]

### Metrics to Evaluate
- [ ] Performance (latency, throughput, runtime)
- [ ] Cost ($/item, $/month, ROI)
- [ ] Quality (coverage, error rates, scores)
- [ ] Security (vulnerabilities, compliance)
- [ ] Other: [specify]

### Expected Deliverable
- [ ] Full analysis report (use system-analysis-report.md template)
- [ ] Brief summary only
- [ ] Specific recommendations only
- [ ] ADR for decision needed

---

## Constraints

### Timeline
[When is this analysis needed by?]

### Confidence Target
- [ ] ≥60% (pre-prod, specs-only)
- [ ] ≥70% (production, with telemetry)

### Bootstrap Gates
This analysis should help validate:
- [ ] ROI ≥3× (18mo)
- [ ] LTV:CAC ≥4:1 (12mo)
- [ ] Security 100%

---

## Additional Context
[Any other relevant information, links to related issues/PRs, etc.]
