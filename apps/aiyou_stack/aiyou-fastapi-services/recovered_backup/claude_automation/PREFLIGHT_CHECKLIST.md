# PNKLN Multi-Agent Deployment - Pre-Flight Checklist

**Target:** Vertex AI Workbench (rust_scriptbots/Bevy integration)  
**Execution:** Bootstrap from $0K with zero manual drift

---

## Phase 1: GCP Prerequisites

- [ ] **GCP Project exists**
  - Project ID: `_________________`
  - Billing enabled: Yes / No
  - Owner/Editor access confirmed: Yes / No

- [ ] **gcloud CLI authenticated**
  ```bash
  gcloud auth login
  gcloud config set project <PROJECT_ID>
  ```

- [ ] **Required APIs enabled** (auto-enabled by script, verify manually if errors)
  - Compute Engine API
  - Notebooks API (Vertex AI Workbench)
  - Vertex AI API
  - Cloud Storage API
  - IAM API

- [ ] **Quota check** (prevent provisioning failures)
  ```bash
  gcloud compute regions describe us-central1 --format="table(quotas.metric,quotas.limit,quotas.usage)"
  ```
  - Verify: `CPUS` ≥ 8, `IN_USE_ADDRESSES` has room

---

## Phase 2: Git Repository

- [ ] **rust_scriptbots repository accessible**
  - Clone URL: `_________________`
  - Authentication method:
    - [ ] Public repo (no auth needed)
    - [ ] Private repo - SSH key configured
    - [ ] Private repo - PAT token ready
  
- [ ] **Test clone locally** (optional but recommended)
  ```bash
  git clone <REPO_URL> /tmp/test_clone
  cd /tmp/test_clone && cargo check
  rm -rf /tmp/test_clone
  ```

---

## Phase 3: Deployment Execution

- [ ] **Run deployment script**
  ```bash
  # Set environment variables
  export GCP_PROJECT_ID="<YOUR_PROJECT_ID>"
  export RUST_SCRIPTBOTS_REPO="<YOUR_REPO_URL>"  # Optional
  
  # Make executable
  chmod +x deploy_pnkln_agents.sh
  
  # Execute
  ./deploy_pnkln_agents.sh
  ```

- [ ] **Monitor deployment logs**
  - No errors in GCS bucket creation
  - Service account created successfully
  - Workbench instance reaches `ACTIVE` state (~5-10 min)

- [ ] **Verify GCS buckets created**
  ```bash
  gsutil ls -b gs://pnkln-agent-mail
  gsutil ls -b gs://pnkln-ShadowTag-v2jr-logs
  gsutil ls -b gs://pnkln-task-artifacts
  ```

- [ ] **Verify supporting docs uploaded**
  ```bash
  gsutil ls gs://pnkln-task-artifacts/docs/
  # Should show: AGENTS.md, ShadowTag-v2JR_DOCTRINE.md, PLAN_TO_INTEGRATE_BEVY_ENGINE.md
  ```

---

## Phase 4: Workbench Instance Setup

- [ ] **Access JupyterLab**
  - Navigate to: https://console.cloud.google.com/vertex-ai/workbench/list/instances
  - Click `OPEN JUPYTERLAB` on `pnkln-multi-agent`

- [ ] **Verify Rust toolchain**
  - Open Terminal in JupyterLab
  ```bash
  rustc --version  # Should show 1.75+
  cargo --version
  sccache --version
  ```

- [ ] **Clone rust_scriptbots** (if not auto-cloned)
  ```bash
  cd /home/jupyter
  git clone <REPO_URL> rust_scriptbots
  cd rust_scriptbots
  cargo check  # Verify build works
  ```

- [ ] **Download supporting docs to instance**
  ```bash
  cd /home/jupyter
  gsutil -m cp gs://pnkln-task-artifacts/docs/*.md ./
  ls -la *.md  # Verify AGENTS.md, ShadowTag-v2JR_DOCTRINE.md, PLAN_TO_INTEGRATE_BEVY_ENGINE.md
  ```

- [ ] **Upload COR_MULTI_AGENT_TEMPLATE.ipynb**
  - Option A: Upload via JupyterLab UI (drag-drop)
  - Option B: Command line
  ```bash
  cd /home/jupyter/notebooks
  gsutil cp gs://pnkln-task-artifacts/notebooks/COR_MULTI_AGENT_TEMPLATE.ipynb ./
  ```

---

## Phase 5: Notebook Configuration

- [ ] **Open COR_MULTI_AGENT_TEMPLATE.ipynb**

- [ ] **Edit Cell 2: Project Configuration**
  ```python
  PROJECT_ID = "<YOUR_PROJECT_ID>"  # ← CHANGE THIS
  LOCATION = "us-central1"
  AGENT_MAIL_BUCKET = "pnkln-agent-mail"
  GOVERNANCE_BUCKET = "pnkln-ShadowTag-v2jr-logs"
  ARTIFACTS_BUCKET = "pnkln-task-artifacts"
  ```

- [ ] **Edit Cell 7: Agent Configuration (Optional)**
  - Review WhiteCastle, BrownSnow, OrangeCreek configs
  - Adjust brakes/reasons if needed for your specific workflow

- [ ] **Edit Cell 10: Coordination Prompt**
  - Update file paths if PLAN.md is in different location
  - Customize project name/thread names

---

## Phase 6: Execution Validation

- [ ] **Run Cells 1-6** (Environment + Governance Setup)
  - No errors in dependency installation
  - GCS buckets connect successfully
  - ShadowTag-v2JR governance layer initialized

- [ ] **Run Cells 7-9** (Agent Initialization)
  - All 3 agents initialized without errors
  - Group chat created with Cor orchestrator

- [ ] **Run Cell 10** (Initiate Coordination)
  - Agents send introduction messages
  - Agent Mail thread "Bevy Integration Coordination" starts
  - Tasks assessed for risk levels (RA-1, RA-2)
  - Work distribution proposed

- [ ] **Monitor with Cell 11** (Agent Mail Review)
  ```python
  review_agent_mail()  # Check all coordination messages
  review_governance_logs("risk")  # Verify ATP 5-19 assessments
  ```

---

## Phase 7: Operational Validation

- [ ] **Verify Agent Mail system**
  - Messages appear in GCS bucket inbox/outbox folders
  ```bash
  gsutil ls gs://pnkln-agent-mail/inbox/WhiteCastle/
  gsutil ls gs://pnkln-agent-mail/outbox/WhiteCastle/
  ```

- [ ] **Verify governance logging**
  ```bash
  gsutil ls gs://pnkln-ShadowTag-v2jr-logs/risk_assessments/
  gsutil ls gs://pnkln-ShadowTag-v2jr-logs/validations/
  ```

- [ ] **Test brake enforcement** (optional but recommended)
  - Manually trigger a brake violation (e.g., claim RA-4 task without approval)
  - Verify brake log appears:
  ```bash
  gsutil ls gs://pnkln-ShadowTag-v2jr-logs/brakes/
  ```

- [ ] **Run first task execution**
  - Let agents complete one small RA-1 task
  - Verify progress updates in PLAN.md
  - Confirm Judge #6 validation runs
  - Check 98% coverage enforcement

- [ ] **Generate execution report** (Cell 12)
  ```python
  report = generate_execution_report()
  ```
  - Review agent message counts
  - Check for any brake activations
  - Verify risk assessments logged

---

## Phase 8: Integration with rust_scriptbots

- [ ] **Update Cargo.toml** (if Bevy not already added)
  ```bash
  cd /home/jupyter/rust_scriptbots
  # Let WhiteCastle agent handle this via Agent Mail
  ```

- [ ] **Run cargo test** (baseline coverage)
  ```bash
  cargo tarpaulin --out Xml --output-dir coverage/
  # Compare against 98% threshold
  ```

- [ ] **Verify Bevy dependencies compile**
  ```bash
  cargo build --features bevy
  # GPU driver validation
  ```

---

## Troubleshooting

### Issue: Workbench instance stuck in PROVISIONING
**Fix:** Check quota limits. Increase CPU/disk quota if needed.
```bash
gcloud compute project-info describe --project=<PROJECT_ID>
```

### Issue: Permission denied on GCS buckets
**Fix:** Verify service account IAM roles
```bash
gsutil iam get gs://pnkln-agent-mail | grep pnkln-agent-orchestrator
```

### Issue: Rust toolchain not found
**Fix:** Manually install via Terminal
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env
```

### Issue: Git clone fails (private repo)
**Fix:** Set up SSH key or PAT
```bash
# SSH key
ssh-keygen -t ed25519 -C "pnkln@vertex"
cat ~/.ssh/id_ed25519.pub  # Add to GitHub/GitLab

# Or use HTTPS with PAT
git config --global credential.helper store
git clone https://<PAT>@github.com/user/rust_scriptbots.git
```

### Issue: Agent Mail messages not appearing
**Fix:** Check service account permissions on bucket
```bash
gsutil iam ch serviceAccount:<SA_EMAIL>:objectAdmin gs://pnkln-agent-mail
```

---

## Success Criteria

✅ All phases complete without errors  
✅ Agents coordinate via Agent Mail  
✅ Governance logs appear in GCS  
✅ First task executes with Judge #6 validation  
✅ rust_scriptbots compiles on instance  
✅ Bevy integration tasks claimed and in progress  

**Time to Production:** < 1 hour (assuming no quota/auth issues)  
**Bootstrap Cost:** ~$0.50/hr for n1-standard-8 + ~$0.10/day for GCS  

---

## Kill Switch Protocol

If deployment fails or needs rollback:

```bash
# Delete Workbench instance
gcloud notebooks instances delete pnkln-multi-agent \
  --location=us-central1-a \
  --project=<PROJECT_ID>

# Delete GCS buckets (WARNING: Irreversible)
gsutil -m rm -r gs://pnkln-agent-mail
gsutil -m rm -r gs://pnkln-ShadowTag-v2jr-logs
gsutil -m rm -r gs://pnkln-task-artifacts

# Delete service account
gcloud iam service-accounts delete pnkln-agent-orchestrator@<PROJECT_ID>.iam.gserviceaccount.com
```

**ATP 5-19 RA-4 Warning:** Only execute kill switch after human approval (Erik).

---

**PNKLN Core Stack™** - Military-grade execution. Zero compromise on governance.
