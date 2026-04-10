# PREFLIGHT CHECKLIST

## PNKLN Multi-Agent Deployment - ATP 5-19 Compliant

**Mission**: Deploy ShadowTag-v2JR-governed agents to Vertex AI Workbench for rust_scriptbots/Bevy integration

**Compliance Framework**: ATP 5-19 (Army Techniques Publication - Risk Management)

**Validation Gates**: PRB (Probability-Risk-Benefit) stratification with human approval for RA-4+ tasks

---

## Phase 0: Pre-Deployment Verification

### 0.1 Environment Setup

- [ ] **GCP Project ID confirmed**: `_________________`
- [ ] **gcloud CLI installed and authenticated**

  ```bash
  gcloud --version
  gcloud auth list
  ```

- [ ] **Project billing enabled**

  ```bash
  gcloud beta billing projects describe $GCP_PROJECT_ID
  ```

- [ ] **Required IAM permissions verified**
  - [ ] `roles/notebooks.admin` or equivalent
  - [ ] `roles/storage.admin` for GCS buckets
  - [ ] `roles/compute.admin` for Workbench instances

**Gate Criteria**: ALL items must be checked before proceeding

**Risk Level**: RA-1 (Routine Administrative)

---

## Phase 1: Infrastructure Deployment

### 1.1 API Enablement

- [ ] **Enable Vertex AI Notebooks API**
- [ ] **Enable Compute Engine API**
- [ ] **Enable Cloud Storage API**
- [ ] **Enable Cloud Build API**
- [ ] **Enable Vertex AI API**

**Automation**: `deploy_pnkln_agents.sh` handles this automatically

**Verification**:

```bash
gcloud services list --enabled --project=$GCP_PROJECT_ID | grep -E 'notebooks|compute|storage|cloudbuild|aiplatform'
```

**Risk Level**: RA-2 (Low Risk - Auto-approve with logging)

---

### 1.2 GCS Bucket Creation

- [ ] **Agent Mail bucket created**: `gs://${GCP_PROJECT_ID}-pnkln-agents`
- [ ] **Directory structure initialized**:
  - [ ] `/agent-mail/` (inter-agent communication)
  - [ ] `/checkpoints/` (state persistence)
  - [ ] `/coverage-reports/` (Judge #6 outputs)

**Verification**:

```bash
gsutil ls -p $GCP_PROJECT_ID
gsutil ls gs://${GCP_PROJECT_ID}-pnkln-agents/
```

**Risk Level**: RA-2 (Low Risk - Auto-approve with logging)

---

### 1.3 Workbench Instance Deployment

- [ ] **Instance name**: `pnkln-agents-workbench` (or custom)
- [ ] **Region**: `us-central1` (or custom)
- [ ] **Machine type**: `n1-standard-4` (4 vCPU, 15GB RAM minimum)
- [ ] **Boot disk**: 100GB minimum
- [ ] **Startup script execution**: Rust + Bevy dependencies installed

**Verification**:

```bash
gcloud notebooks instances describe pnkln-agents-workbench \
  --location=us-central1 \
  --project=$GCP_PROJECT_ID
```

**Risk Level**: RA-3 (Medium Risk - Requires review)

**ATP 5-19 Gate**: Confirm resource quotas and cost estimates before creation

---

## Phase 2: Artifact Deployment

### 2.1 Upload Deployment Artifacts

- [ ] **COR_MULTI_AGENT_TEMPLATE.ipynb** uploaded to GCS
- [ ] **PREFLIGHT_CHECKLIST.md** (this file) uploaded
- [ ] **QUICKSTART.md** uploaded
- [ ] **AGENTS.md** uploaded
- [ ] **ShadowTag-v2JR_DOCTRINE.md** uploaded
- [ ] **PLAN_TO_INTEGRATE_BEVY_ENGINE.md** uploaded

**Verification**:

```bash
gsutil ls gs://${GCP_PROJECT_ID}-pnkln-agents/setup/
```

**Risk Level**: RA-1 (Routine Administrative)

---

## Phase 3: Agent Configuration

### 3.1 Agent Registry Validation

- [ ] **WhiteCastle (WC-01)** configured
  - Role: Architecture & Planning
  - Risk Level: RA-3
  - Coverage Target: 95%
- [ ] **BrownSnow (BS-02)** configured
  - Role: Implementation & Integration
  - Risk Level: RA-2
  - Coverage Target: 98%
- [ ] **OrangeCreek (OC-03)** configured
  - Role: Validation & QA (Judge #6)
  - Risk Level: RA-4 (Requires human approval)
  - Coverage Target: 100%

**Verification**: Review `AGENTS.md` for complete specifications

**Risk Level**: RA-3 (Medium Risk - Requires review)

---

### 3.2 API Key Configuration

- [ ] **ANTHROPIC_API_KEY environment variable set**

  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  ```

- [ ] **API key validated**

  ```python
  import anthropic
  client = anthropic.Anthropic()
  # Test connection
  ```

**Risk Level**: RA-4 (High Risk - Requires human approval)

**ATP 5-19 Gate**: CRITICAL - Secure key storage required. Never commit keys to version control.

---

## Phase 4: Workbench Initialization

### 4.1 Access Workbench

- [ ] **JupyterLab URL obtained**

  ```bash
  gcloud notebooks instances describe pnkln-agents-workbench \
    --location=us-central1 \
    --format='value(proxyUri)'
  ```

- [ ] **Successfully logged into JupyterLab**
- [ ] **Startup script completed** (check `/tmp/startup-complete.txt`)

**Risk Level**: RA-1 (Routine Administrative)

---

### 4.2 Clone rust_scriptbots Repository

- [ ] **Repository cloned to Workbench**

  ```bash
  git clone https://github.com/YOUR_ORG/rust_scriptbots.git
  cd rust_scriptbots
  ```

- [ ] **Bevy dependencies verified**

  ```bash
  cargo check
  ```

**Risk Level**: RA-2 (Low Risk - Auto-approve with logging)

---

### 4.3 Download Deployment Artifacts

- [ ] **Artifacts downloaded from GCS**

  ```bash
  gsutil -m cp -r gs://${GCP_PROJECT_ID}-pnkln-agents/setup/ ~/workbench-setup/
  ```

- [ ] **COR_MULTI_AGENT_TEMPLATE.ipynb** opened in JupyterLab

**Risk Level**: RA-1 (Routine Administrative)

---

## Phase 5: Agent Activation

### 5.1 Notebook Configuration

- [ ] **Cell 2 edited**: Set `PROJECT_ID` to actual GCP project ID
- [ ] **Cell 3 executed**: Dependencies installed successfully
- [ ] **No import errors** when running initialization cells

**Risk Level**: RA-2 (Low Risk - Auto-approve with logging)

---

### 5.2 Agent Initialization

- [ ] **All 3 agents initialized** (WhiteCastle, BrownSnow, OrangeCreek)
- [ ] **Agent Mail system connected** to GCS bucket
- [ ] **No authentication errors**

**Verification**: Run agent registry cell, should see:

```
✅ 3 agents initialized
   - WC-01: WhiteCastle
   - BS-02: BrownSnow
   - OC-03: OrangeCreek
```

**Risk Level**: RA-3 (Medium Risk - Requires review)

---

### 5.3 Test Workflow Execution

- [ ] **Run example Bevy integration workflow** (Cell in section 4)
- [ ] **WhiteCastle generates architecture plan**
- [ ] **BrownSnow receives plan via Agent Mail**
- [ ] **OrangeCreek validation triggered**
- [ ] **Human approval prompt displayed** (for RA-4 task)

**Risk Level**: RA-4 (High Risk - Requires human approval)

**ATP 5-19 Gate**: CRITICAL - Review all OrangeCreek validation tasks manually

---

## Phase 6: Judge #6 Validation

### 6.1 Coverage Enforcement

- [ ] **98% coverage requirement configured**
- [ ] **Sample validation executed successfully**
- [ ] **Coverage report generated**

**Expected Output**:

```
======================================================================
JUDGE #6 COVERAGE REPORT
======================================================================
Minimum Required: 98.00%

✅ Test 1: 98.00% coverage
======================================================================
```

**Risk Level**: RA-3 (Medium Risk - Requires review)

---

### 6.2 Integration Test

- [ ] **Bevy plugin template generated** by BrownSnow
- [ ] **Rust code compiles** without errors
- [ ] **Tests pass** with >98% coverage
- [ ] **OrangeCreek approval** received

**Verification**:

```bash
cd rust_scriptbots
cargo test
cargo tarpaulin --out Stdout  # Check coverage
```

**Risk Level**: RA-4 (High Risk - Requires human approval)

**ATP 5-19 Gate**: FINAL CHECKPOINT - All tests must pass before production deployment

---

## Phase 7: Production Readiness

### 7.1 Documentation Review

- [ ] **All generated documentation present**:
  - [ ] AGENTS.md
  - [ ] ShadowTag-v2JR_DOCTRINE.md
  - [ ] PLAN_TO_INTEGRATE_BEVY_ENGINE.md
- [ ] **Architecture diagrams reviewed** (if generated)
- [ ] **Risk assessment completed** per ShadowTag-v2JR framework

**Risk Level**: RA-2 (Low Risk - Auto-approve with logging)

---

### 7.2 Security Validation

- [ ] **No secrets in version control**
- [ ] **IAM permissions follow least privilege**
- [ ] **GCS bucket access properly scoped**
- [ ] **API keys stored in Secret Manager** (recommended)

**Risk Level**: RA-4 (High Risk - Requires human approval)

**ATP 5-19 Gate**: SECURITY CRITICAL - Manual security review required

---

### 7.3 Operational Readiness

- [ ] **Monitoring configured** for agent tasks
- [ ] **Cost alerts set** for GCP resources
- [ ] **Backup strategy defined** for agent state
- [ ] **Incident response plan** documented

**Risk Level**: RA-3 (Medium Risk - Requires review)

---

## Final Sign-Off

### Deployment Approval

**Deployment Lead**: _______________________  Date: __________

**Security Review**: _______________________  Date: __________

**Operations Review**: _____________________  Date: __________

---

### ATP 5-19 Risk Assessment Summary

| Phase | Risk Level | Human Approval Required | Status |
|-------|------------|------------------------|--------|
| Phase 0 | RA-1 | No | ⬜ |
| Phase 1.1-1.2 | RA-2 | No | ⬜ |
| Phase 1.3 | RA-3 | Review | ⬜ |
| Phase 2 | RA-1 | No | ⬜ |
| Phase 3.1 | RA-3 | Review | ⬜ |
| Phase 3.2 | RA-4 | **YES** | ⬜ |
| Phase 4 | RA-1/RA-2 | No | ⬜ |
| Phase 5.1-5.2 | RA-2/RA-3 | Review | ⬜ |
| Phase 5.3 | RA-4 | **YES** | ⬜ |
| Phase 6.1 | RA-3 | Review | ⬜ |
| Phase 6.2 | RA-4 | **YES** | ⬜ |
| Phase 7.1 | RA-2 | No | ⬜ |
| Phase 7.2 | RA-4 | **YES** | ⬜ |
| Phase 7.3 | RA-3 | Review | ⬜ |

**Total RA-4 Gates**: 4 (API Keys, Test Workflow, Integration Test, Security Validation)

**Estimated Time to Complete**: 30-45 minutes (excluding approvals)

---

## Troubleshooting

### Common Issues

**Issue**: Workbench instance creation fails

- **Solution**: Check resource quotas: `gcloud compute project-info describe --project=$GCP_PROJECT_ID`

**Issue**: Agent Mail communication fails

- **Solution**: Verify GCS bucket permissions: `gsutil iam get gs://${GCP_PROJECT_ID}-pnkln-agents`

**Issue**: Judge #6 coverage validation fails

- **Solution**: Review generated tests in rust_scriptbots, add coverage for untested paths

**Issue**: OrangeCreek approval loop

- **Solution**: Set `RA_4_AUTO_APPROVE=true` environment variable (NOT recommended for production)

---

## Resources

- [Deployment Script](./deploy_pnkln_agents.sh)
- [Quick Start Guide](./QUICKSTART.md)
- [Agent Registry](./AGENTS.md)
- [ShadowTag-v2JR Doctrine](./ShadowTag-v2JR_DOCTRINE.md)
- [Bevy Integration Plan](./PLAN_TO_INTEGRATE_BEVY_ENGINE.md)
- [ATP 5-19 Reference](https://armypubs.army.mil/epubs/DR_pubs/DR_a/pdf/web/atp5_19.pdf)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Maintained By**: PNKLN Multi-Agent Team
