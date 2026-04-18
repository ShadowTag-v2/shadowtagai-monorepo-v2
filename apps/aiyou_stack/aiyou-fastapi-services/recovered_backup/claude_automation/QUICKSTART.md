# PNKLN Multi-Agent Quick Start

**Target:** Cursor → Vertex AI Workbench migration (rust_scriptbots/Bevy)
**Time to First Execution:** < 30 minutes
**Bootstrap Capital:** $0K

---

## TL;DR - Three Commands to Production

```bash
# 1. Deploy infrastructure
export GCP_PROJECT_ID="your-project-id"
export RUST_SCRIPTBOTS_REPO="redacted@shadowtag-v4.local:your-org/rust_scriptbots.git"  # Optional
chmod +x deploy_pnkln_agents.sh && ./deploy_pnkln_agents.sh

# 2. Open Workbench (after deployment completes)
# → https://console.cloud.google.com/vertex-ai/workbench/list/instances
# → Click "OPEN JUPYTERLAB" on pnkln-multi-agent

# 3. Execute in JupyterLab Terminal
cd /home/jupyter
git clone $RUST_SCRIPTBOTS_REPO rust_scriptbots  # If not auto-cloned
gsutil cp gs://pnkln-task-artifacts/notebooks/COR_MULTI_AGENT_TEMPLATE.ipynb notebooks/
# → Open notebooks/COR_MULTI_AGENT_TEMPLATE.ipynb
# → Edit Cell 2: Set PROJECT_ID
# → Run All Cells
```

---

## File Inventory

From this deployment, you have:

### 1. `deploy_pnkln_agents.sh`
**Purpose:** One-command infrastructure provisioning
**What it does:**
- Creates 3 GCS buckets (Agent Mail, Governance Logs, Artifacts)
- Provisions Vertex AI Workbench instance (n1-standard-8, 200GB SSD)
- Sets up service account with IAM roles
- Uploads supporting docs (AGENTS.md, ShadowTag-v2JR_DOCTRINE.md, PLAN.md)
- Configures Rust toolchain on instance
- Installs Python dependencies (AutoGen, Vertex AI SDK)

**Prerequisites:**
- gcloud CLI authenticated
- GCP project with billing enabled
- jq installed (`apt-get install jq` / `brew install jq`)

**Execution:**
```bash
./deploy_pnkln_agents.sh
```

### 2. `COR_MULTI_AGENT_TEMPLATE.ipynb`
**Purpose:** Jupyter notebook for multi-agent orchestration
**Architecture:**
- **Cell 1-2**: Environment + GCS connection
- **Cell 3**: ShadowTag-v2JR governance (Judge #6, ATP 5-19)
- **Cell 4**: Agent Mail (NS - Nervous System)
- **Cell 5-6**: Task coordination + context management
- **Cell 7**: Agent configuration (WhiteCastle, BrownSnow, OrangeCreek)
- **Cell 8-9**: AutoGen agent instantiation + Cor orchestrator
- **Cell 10**: Coordination phase initiation
- **Cell 11**: Agent Mail monitoring
- **Cell 12**: Execution report generation

**Key Configuration Points:**
- Cell 2: `PROJECT_ID` (required)
- Cell 7: Agent configs (optional - defaults work for Bevy integration)
- Cell 10: Coordination prompt (optional - customize task/project name)

### 3. `PREFLIGHT_CHECKLIST.md`
**Purpose:** Gate-based validation (ATP 5-19 compliance)
**Use case:** Run through checklist before executing deployment
**Key phases:**
- Phase 1: GCP prerequisites
- Phase 2: Git repository access
- Phase 3: Deployment execution
- Phase 4: Workbench instance setup
- Phase 5: Notebook configuration
- Phase 6: Execution validation
- Phase 7: Operational validation
- Phase 8: Integration with rust_scriptbots

### 4. Supporting Docs (Auto-Generated)
- **AGENTS.md**: Agent registry (WhiteCastle, BrownSnow, OrangeCreek)
- **ShadowTag-v2JR_DOCTRINE.md**: Governance framework (PRB + ATP 5-19)
- **PLAN_TO_INTEGRATE_BEVY_ENGINE.md**: Task breakdown with checkpoints

---

## Execution Sequence (Detailed)

### Step 1: Pre-Deployment Validation
```bash
# Verify gcloud authentication
gcloud auth list
gcloud config get-value project

# Check quota (prevent provisioning failures)
gcloud compute regions describe us-central1 --format="table(quotas.metric,quotas.limit,quotas.usage)"
# Ensure: CPUS ≥ 8, IN_USE_ADDRESSES has capacity

# Test jq installation
echo '{"test": "value"}' | jq '.test'
# Should output: "value"
```

### Step 2: Deploy Infrastructure
```bash
# Set required environment variables
export GCP_PROJECT_ID="your-gcp-project-id"

# Optional: Set if you want auto-clone (otherwise clone manually later)
export RUST_SCRIPTBOTS_REPO="redacted@shadowtag-v4.local:your-org/rust_scriptbots.git"

# Optional: Customize region/zone/machine
export GCP_REGION="us-central1"
export GCP_ZONE="us-central1-a"

# Execute deployment
chmod +x deploy_pnkln_agents.sh
./deploy_pnkln_agents.sh

# Expected output:
# [✓] All prerequisites installed
# [✓] Project validated: your-gcp-project-id
# [✓] APIs enabled
# [✓] GCS buckets created
# [✓] Service account created
# [✓] IAM roles configured
# [✓] Supporting documents uploaded
# [✓] Startup script generated
# [✓] Instance is ACTIVE
```

**Duration:** 5-10 minutes (mostly waiting for instance provisioning)

### Step 3: Access Workbench
```bash
# Open in browser (or use gcloud command)
open "https://console.cloud.google.com/vertex-ai/workbench/list/instances?project=$GCP_PROJECT_ID"

# Or via gcloud (prints JupyterLab URL)
gcloud notebooks instances describe pnkln-multi-agent \
  --location=us-central1-a \
  --project=$GCP_PROJECT_ID \
  --format="value(proxyUri)"
```

Click **"OPEN JUPYTERLAB"** button next to `pnkln-multi-agent`

### Step 4: Instance Setup (JupyterLab Terminal)
```bash
# Verify Rust installation
rustc --version  # Should show 1.75+
cargo --version
sccache --version

# Clone rust_scriptbots (if not auto-cloned)
cd /home/jupyter
git clone redacted@shadowtag-v4.local:your-org/rust_scriptbots.git rust_scriptbots
cd rust_scriptbots
cargo check  # Verify build works

# Verify supporting docs downloaded
cd /home/jupyter
ls -la *.md
# Should show: AGENTS.md, ShadowTag-v2JR_DOCTRINE.md, PLAN_TO_INTEGRATE_BEVY_ENGINE.md

# Download notebook template
mkdir -p notebooks
cd notebooks
gsutil cp gs://pnkln-task-artifacts/notebooks/COR_MULTI_AGENT_TEMPLATE.ipynb ./
```

### Step 5: Configure Notebook
Open `notebooks/COR_MULTI_AGENT_TEMPLATE.ipynb` in JupyterLab

**Required Edit (Cell 2):**
```python
PROJECT_ID = "your-gcp-project-id"  # ← CHANGE THIS
```

**Optional Edits:**

Cell 7 (Agent Configuration):
```python
agent_configs = [
    {
        "name": "WhiteCastle",
        "role": "Backend/API Development",
        # Adjust brakes if you want different constraints
        "brakes": [
            "No unsafe blocks without RA-3 approval + justification",
            "Test coverage >= 98% before task completion",
            # Add/remove as needed
        ]
    },
    # ... BrownSnow, OrangeCreek
]
```

Cell 10 (Coordination Prompt):
```python
initial_coordination_prompt = """
...
3. DOCUMENT REVIEW:
   - Read: /home/jupyter/AGENTS.md
   - Read: /home/jupyter/ShadowTag-v2JR_DOCTRINE.md
   - Read: /home/jupyter/PLAN_TO_INTEGRATE_BEVY_ENGINE.md  # ← Update path if needed
...
"""
```

### Step 6: Execute Multi-Agent Coordination
**In the notebook:**

1. **Run Cells 1-6** (Environment Setup)
   - Installs dependencies
   - Connects to GCS
   - Initializes ShadowTag-v2JR governance

2. **Run Cells 7-9** (Agent Initialization)
   - Creates WhiteCastle, BrownSnow, OrangeCreek
   - Each agent gets Purpose/Reasons/Brakes
   - Cor orchestrator initialized

3. **Run Cell 10** (Start Coordination)
   - Agents send introductions via Agent Mail
   - Risk assessment on PLAN.md tasks
   - Work distribution negotiation
   - Consensus-based task claiming

4. **Monitor with Cell 11**
   ```python
   # Check all Agent Mail
   review_agent_mail()

   # Check specific agent inbox
   review_agent_mail("WhiteCastle")

   # Review governance logs
   review_governance_logs("risk")  # Risk assessments
   review_governance_logs("validations")  # Judge #6 results
   review_governance_logs("brakes")  # Brake violations (should be empty)
   ```

5. **Generate Report (Cell 12)**
   ```python
   report = generate_execution_report()
   # Shows: agent message counts, risk assessments, validations, brake activations
   ```

---

## Verification Checkpoints

### ✅ Infrastructure Deployed
```bash
# Check GCS buckets exist
gsutil ls -b | grep pnkln
# Expected:
# gs://pnkln-agent-mail/
# gs://pnkln-ShadowTag-v2jr-logs/
# gs://pnkln-task-artifacts/

# Check service account
gcloud iam service-accounts list | grep pnkln-agent-orchestrator

# Check Workbench instance running
gcloud notebooks instances list --location=us-central1-a | grep pnkln-multi-agent
# Expected: STATE = ACTIVE
```

### ✅ Agents Operational
```bash
# From instance terminal, check Agent Mail
gsutil ls gs://pnkln-agent-mail/inbox/WhiteCastle/
# Should show message files (*.json)

# Check governance logs
gsutil ls gs://pnkln-ShadowTag-v2jr-logs/risk_assessments/
# Should show risk assessment logs
```

### ✅ Bevy Integration Started
```bash
# Check PLAN.md updates
cd /home/jupyter
cat PLAN_TO_INTEGRATE_BEVY_ENGINE.md | grep "Status:"
# Should show agents claiming tasks

# Verify Cargo.toml updated (if WhiteCastle claimed that task)
cd /home/jupyter/rust_scriptbots
grep "bevy" Cargo.toml
```

---

## Operational Patterns

### Pattern 1: Queue New Tasks
**Edit PLAN.md**, add new task block:
```markdown
### RA-2: New Feature X
**Owner**: Not Assigned
**Status**: Not Started
**Progress**: 0%

Tasks:
- [ ] Implement feature X
- [ ] Write tests (98% coverage)
- [ ] Judge #6 validation

**Checkpoints**:
- 25%: Design approved
- 50%: Implementation complete
- 75%: Tests pass
- 100%: Validated
```

**Send Agent Mail** to trigger re-coordination:
```python
from google.cloud import storage
import json
from datetime import datetime

mail = AgentMail("cor_orchestrator")
mail.send(
    to="*all*",  # Broadcast
    subject="New Task: Feature X",
    body="PLAN.md updated with new RA-2 task. Review and claim if within specialization."
)
```

### Pattern 2: Monitor Progress
```python
# Real-time Agent Mail monitoring (run periodically)
review_agent_mail(limit=50)

# Check task progress in GCS
!gsutil ls gs://pnkln-task-artifacts/progress/
```

### Pattern 3: Brake Enforcement
If agent violates brake (e.g., RA-4 task without approval):
```python
# Agent automatically logs brake violation
governance.enforce_brake(
    agent_name="WhiteCastle",
    brake_condition="Attempted RA-4 task without human gate",
    context={"task_id": "deploy_production", "risk_level": "RA-4"}
)

# Check brake logs
review_governance_logs("brakes")
```

**Human intervention required:**
```python
# Review brake, decide to approve or reject
mail = AgentMail("human_approver")
mail.send(
    to="WhiteCastle",
    subject="RE: RA-4 Task Approval",
    body="Approved. Proceed with production deployment after peer review."
)
```

### Pattern 4: Context Consolidation
Agents automatically consolidate at 80% context:
```python
# Agent detects context limit
if context_mgr.needs_consolidation():
    summary = "Completed tasks 1-5. Remaining: 6-10. No brake violations."
    context_mgr.consolidate(agent_mail, summary)
    # Summary saved to gs://pnkln-task-artifacts/consolidations/
    # Agent Mail sent to cor_orchestrator
    # Context reset, work resumes
```

---

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Workbench Instance (n1-standard-8) | ~$0.38/hr | ~$274/mo if left running 24/7 |
| Persistent Disk (200GB SSD) | ~$34/mo | Storage for Rust builds + cargo cache |
| GCS Buckets | ~$0.02/GB/mo | Agent Mail ~1GB, Logs ~0.5GB |
| Vertex AI API (Gemini) | ~$0.25/1K requests | Judge #6 validations |
| **Total (assuming 8hr/day usage)** | ~$100/mo | Stop instance when not in use |

**Stop instance to save costs:**
```bash
gcloud notebooks instances stop pnkln-multi-agent --location=us-central1-a
```

**Resume when needed:**
```bash
gcloud notebooks instances start pnkln-multi-agent --location=us-central1-a
```

---

## Troubleshooting

### Issue: "Permission denied" when cloning private repo
**Solution:** Add SSH key to instance
```bash
# On instance terminal
ssh-keygen -t ed25519 -C "pnkln-vertex"
cat ~/.ssh/id_ed25519.pub
# Copy output, add to GitHub/GitLab SSH keys
```

### Issue: Agents not sending messages
**Solution:** Check service account permissions
```bash
gsutil iam get gs://pnkln-agent-mail | grep pnkln-agent-orchestrator
# Should show "objectAdmin" role
```

### Issue: Judge #6 validation fails (Gemini API error)
**Solution:** Verify Vertex AI API enabled + quota
```bash
gcloud services list --enabled | grep aiplatform
gcloud alpha services quota list --service=aiplatform.googleapis.com
```

### Issue: Rust compilation fails (out of memory)
**Solution:** Increase sccache capacity or upgrade machine type
```bash
# Increase sccache size (default: 10GB)
export SCCACHE_CACHE_SIZE="20G"

# Or upgrade instance
gcloud notebooks instances stop pnkln-multi-agent --location=us-central1-a
# Manually change machine type in Console to n1-standard-16
gcloud notebooks instances start pnkln-multi-agent --location=us-central1-a
```

---

## Next Steps After First Successful Run

1. **Scale to More Agents**: Add specialized agents in Cell 7
2. **Custom Brakes**: Define domain-specific constraints per vertical
3. **Integration Tests**: Add Judge #6 validation for E2E workflows
4. **CI/CD**: Trigger Vertex notebooks from GitHub Actions
5. **Multi-Project**: Replicate pattern across PNKLN's 30 verticals

---

## Cleanup (Kill Switch)

**⚠️ ATP 5-19 RA-4 Warning:** Requires human approval (Erik).

```bash
# Stop instance (preserves data)
gcloud notebooks instances stop pnkln-multi-agent --location=us-central1-a

# Delete instance (keeps GCS buckets)
gcloud notebooks instances delete pnkln-multi-agent --location=us-central1-a --quiet

# Delete everything (IRREVERSIBLE)
gsutil -m rm -r gs://pnkln-agent-mail
gsutil -m rm -r gs://pnkln-ShadowTag-v2jr-logs
gsutil -m rm -r gs://pnkln-task-artifacts
gcloud iam service-accounts delete pnkln-agent-orchestrator@$GCP_PROJECT_ID.iam.gserviceaccount.com --quiet
```

---

**PNKLN Core Stack™**
*Bootstrap from $0K → Multi-Agent Coordination → $1.33T valuation by Year 30*
*Military-grade execution. Zero compromise on governance.*
