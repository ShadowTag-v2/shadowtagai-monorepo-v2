# ShadowTag v2 - Operational Procedures

**pnkln Bourne/160 STRICT Mode**

## Quality Gates Checklist

### Pre-Deployment Checklist

- [ ] All tests passing with ≥98% coverage
- [ ] Static analysis (ruff, mypy) passing
- [ ] Security scan (bandit) clean
- [ ] Pre-commit hooks passing
- [ ] Two green CI runs completed
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] GCP secrets configured
- [ ] Blockchain credentials tested (if enabled)

### Security Checklist

- [ ] No hardcoded secrets in code
- [ ] All secrets in GCP Secret Manager
- [ ] TLS enforced for all network operations
- [ ] Input validation on all user-provided data
- [ ] File upload size limits enforced
- [ ] CORS configured appropriately
- [ ] Authentication/authorization implemented (if required)
- [ ] Rate limiting configured (if required)
- [ ] Logging sanitized (no secrets in logs)
- [ ] Error messages don't leak sensitive info

### Testing Checklist

- [ ] Unit tests for all modules
- [ ] Integration tests for API endpoints
- [ ] Property-based tests (hypothesis)
- [ ] Mock blockchain transactions in tests
- [ ] Test file cleanup in fixtures
- [ ] Edge cases covered
- [ ] Error handling tested
- [ ] Performance benchmarks run

### Deployment Checklist

- [ ] Environment variables set
- [ ] GCP project configured
- [ ] Secret Manager secrets created
- [ ] Service account permissions granted
- [ ] Vertex AI APIs enabled (if applicable)
- [ ] Blockchain RPC endpoints accessible
- [ ] Storage buckets configured
- [ ] Monitoring/alerting configured
- [ ] Backup procedures documented
- [ ] Rollback plan documented

## ROI Gate Monitoring

### Metrics to Track

1. **Usage Metrics**
   - Watermarks embedded per day
   - Verification requests per day
   - API response times
   - Error rates

2. **Business Metrics**
   - Customer acquisition cost
   - Monthly recurring revenue
   - Customer lifetime value
   - Churn rate

3. **ROI Calculation**
   - Target: ≥3× return in 18 months
   - Kill-switch if ROI < 3× at 12 months
   - Monthly ROI review

### Kill-Switch Triggers

Activate kill-switch if:
- ROI projection < 3× at 12-month review
- Security breach detected
- Legal/compliance violation
- Critical infrastructure failure without recovery path

## Incident Response

### Severity Levels

**P0 - Critical**
- System down
- Data breach
- Security vulnerability exploited

**P1 - High**
- Degraded performance (>50% slower)
- Blockchain integration failure
- High error rate (>5%)

**P2 - Medium**
- Minor performance degradation
- Non-critical feature failure
- Elevated error rate (1-5%)

**P3 - Low**
- Cosmetic issues
- Documentation gaps
- Enhancement requests

### Response Procedures

1. **Detection**
   - Monitor logs and metrics
   - Alert on anomalies
   - Health check failures

2. **Triage**
   - Assess severity
   - Assign owner
   - Notify stakeholders

3. **Resolution**
   - Isolate issue
   - Apply fix
   - Test thoroughly
   - Deploy with rollback plan

4. **Post-Mortem**
   - Document incident
   - Root cause analysis
   - Preventive measures
   - Update runbooks

## Maintenance Procedures

### Daily

- [ ] Check CI/CD pipeline status
- [ ] Review error logs
- [ ] Monitor API response times
- [ ] Check GCP quota usage

### Weekly

- [ ] Review test coverage trends
- [ ] Dependency security scan
- [ ] Performance benchmark review
- [ ] Backup verification

### Monthly

- [ ] ROI metrics review
- [ ] Security audit
- [ ] Dependency updates
- [ ] Capacity planning review
- [ ] Documentation audit

### Quarterly

- [ ] Comprehensive security assessment
- [ ] Architecture review
- [ ] Disaster recovery drill
- [ ] Competitive analysis
- [ ] Patent/IP review

## Compliance & Legal

### Export Control

- ShadowTag v2 uses steganography (dual-use technology)
- Export classification: 'Content Authenticity System'
- LEO/GOV/ITAR: "LEO/GOV/ITAR in effect" (details gated)

### Data Privacy

- No PII stored without consent
- GDPR compliance (if applicable)
- Data retention policies enforced
- Right to deletion supported

### Intellectual Property

- Patent provisional filed for dual-layer technique
- Regular IP audits
- Trademark protection for pnkln brand
- Open source license compliance

## Scaling Procedures

### Vertical Scaling

1. Monitor resource usage
2. Identify bottlenecks
3. Increase instance size
4. Test under load
5. Monitor post-scaling

### Horizontal Scaling

1. Load balancer configuration
2. Stateless API design
3. Shared storage for files
4. Database connection pooling
5. Cache layer implementation

### Performance Optimization

- Profile watermarking operations
- Optimize DCT/FFT computations
- Parallel processing where applicable
- Caching prompt hashes
- Database query optimization

## Backup & Recovery

### Backup Strategy

- **Code**: Git repository (GitHub)
- **Secrets**: GCP Secret Manager (versioned)
- **Data**: Regular snapshots
- **Blockchain**: On-chain receipts (immutable)

### Recovery Procedures

1. **Code Recovery**
   - Restore from Git
   - Deploy to new environment
   - Run smoke tests

2. **Secret Recovery**
   - Access GCP Secret Manager
   - Rotate if compromised
   - Update services

3. **Data Recovery**
   - Restore from snapshot
   - Verify integrity
   - Replay transactions if needed

## Monitoring & Alerting

### Key Metrics

- API latency (p50, p95, p99)
- Error rate (5xx, 4xx)
- Watermark embedding success rate
- Verification accuracy
- Blockchain transaction success rate

### Alerts

- **Critical**: System down, error rate >10%
- **Warning**: Latency >2s, error rate >5%
- **Info**: Deployment completed, scaling event

### Dashboards

- Real-time API metrics
- Test coverage trends
- ROI tracking
- Security scan results

---

**Version**: 2.0.0
**Last Updated**: 2025-11-15
**Owner**: pnkln Operations Team
