# Pull Request

## Description
<!-- Provide a clear and concise description of what this PR does -->

## Type of Change
<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactoring (no functional changes)
- [ ] Documentation update
- [ ] Security fix
- [ ] Performance improvement

## Related Issue
<!-- Link to related issue(s) -->
Fixes #(issue number)

## SOP-C: Decision Assessment

**Business Value:**
<!-- What problem does this solve? What value does it provide? -->

**Risk Assessment:**
- **Probability**: [A/B/C/D/E] <!-- A: >90%, B: 70-90%, C: 40-70%, D: 10-40%, E: <10% -->
- **Severity**: [I/II/III/IV] <!-- I: Catastrophic, II: Critical, III: Moderate, IV: Minimal -->
- **Risk Level**: [EH/H/M/L] <!-- Extremely High, High, Moderate, Low -->

**Mitigation Strategy** (if H or EH):
<!-- How are you mitigating the risk? -->

## Revenue Impact
<!-- Required: How does this affect revenue? -->

- [ ] Direct monetization (new paid feature)
- [ ] Indirect revenue (retention, growth driver)
- [ ] No revenue impact
- [ ] Cost reduction

**ROI Projection**: <!-- Expected ROI (target ≥3× in 18 months) -->

**Monetization Strategy**:
<!-- How is this feature monetized? Freemium tier? Usage-based? Add-on? -->

## SOP-D: Code Review Checklist

### Security (Non-Negotiable)
- [ ] Input validation on all endpoints
- [ ] Authentication/authorization enforced
- [ ] SQL injection prevention (using ORM/parameterized queries)
- [ ] XSS prevention (Pydantic validation)
- [ ] Secrets in Secret Manager (not in code)
- [ ] Rate limiting implemented
- [ ] Security scan passed (Bandit clean)

### Architecture
- [ ] Boy Scout Rule: code cleaner than found
- [ ] Single Responsibility Principle followed
- [ ] Functions ≤20 lines
- [ ] Clear abstractions, minimal coupling
- [ ] No premature optimization

### Testing
- [ ] Test coverage ≥80%
- [ ] Tests follow AAA (Arrange-Act-Assert)
- [ ] Edge cases covered
- [ ] Error paths tested
- [ ] Integration tests for API endpoints

### Documentation
- [ ] API contract documented (docstrings)
- [ ] README updated (if applicable)
- [ ] CHANGELOG updated
- [ ] Inline comments explain WHY (not what)

### Performance
- [ ] No N+1 queries
- [ ] Appropriate database indexes
- [ ] Response time <200ms (p95)
- [ ] Resource usage reasonable

## Testing Evidence

**Test Results:**
```bash
# Paste pytest output
pytest tests/ --cov=app --cov-report=term-missing
```

**Coverage:**
<!-- Current test coverage percentage -->
- Coverage: ___%

**Security Scan:**
```bash
# Paste bandit output
bandit -r app/
```

**Type Checking:**
```bash
# Paste mypy output
mypy app/
```

## Deployment Plan

**Staging Verification:**
- [ ] Deployed to staging (Vertex AI Workbench)
- [ ] Integration tests passed
- [ ] Manual testing completed

**Production Deployment:**
- [ ] Database migrations prepared (if applicable)
- [ ] Environment variables documented
- [ ] Monitoring/alerts configured
- [ ] Rollback plan documented

**Rollback Commands:**
```bash
# How to rollback if things go wrong
kubectl rollout undo deployment/shadowtag-omega-v4-api
```

## Screenshots / Videos
<!-- If applicable, add screenshots or videos to demonstrate the changes -->

## Checklist Before Merge

- [ ] All automated checks passed (SOP-A)
- [ ] Code review completed (SOP-D)
- [ ] Security review approved
- [ ] Revenue impact documented
- [ ] Tests passing with ≥80% coverage
- [ ] Documentation updated
- [ ] Ready for deployment (SOP-B)

## Additional Notes
<!-- Any additional information reviewers should know -->

---

**Remember**: Security is non-negotiable. Revenue awareness is mandatory. Tests come first.
