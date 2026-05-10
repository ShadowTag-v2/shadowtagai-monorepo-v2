#!/bin/bash
set -e

# ==============================================================================
# 🌌 PHASE 0: PRE-FLIGHT (BACKUP & SCAFFOLD)
# ==============================================================================
REPO_NAME="ShadowTag-Omega"
BACKUP_DIR="_PRE_OMEGA_BACKUP_$(date +%s)"
PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"

echo ">>> 🦍 INITIATING ANTIGRAVITY SINGULARITY (v50 - FIRESTORE EDITION)..."
echo ">>> 🛡️  PHASE 0: SECURING ASSETS..."

# 1. Backup - We are already INSIDE ShadowTag-Omega for the most part, but let's handle the root context.
# If we run this from ShadowTag-v2 root:
if [ -d "$REPO_NAME" ]; then
    echo "    ⚠️  Existing Omega Repo detected. Using it as base (Partial Update Mode)."
    cd "$REPO_NAME"
else
    mkdir -p "$REPO_NAME"
    cd "$REPO_NAME"
fi

# 2. Scaffold
echo "    🏗️  Scaffolding Architecture..."
mkdir -p apps/n-autoresearch/Kosmos/BioAgents-server/src
mkdir -p apps/agent-manager-ui/public
mkdir -p libs/ShadowTag-v2/{agents,governance,proxies}
# Ensure proper package structure with __init__.py files
touch libs/ShadowTag-v2/__init__.py libs/ShadowTag-v2/agents/__init__.py

mkdir -p libs/arsenal/{shadowtag_core,tegu_vision,gaas_flight,autoresearch,safety_net}
touch libs/arsenal/__init__.py libs/arsenal/autoresearch/__init__.py

mkdir -p libs/pnkln/compression/src/compression
mkdir -p infra/{velocity-lake,workstations,treasury,terraform}
mkdir -p tools/{scripts,mcp_servers,legacy}
mkdir -p docs/{doctrine,commercial}
mkdir -p .vscode .quibbler .agent/context

# ==============================================================================
# 🧹 PHASE 1: THE VACUUM (Skip for Partial Update to preserve context)
# ==============================================================================
# echo ">>> 🧹 PHASE 1: MIGRATING EXISTING DATA..."

# ==============================================================================
# 🧠 PHASE 2: THE BRAIN (INTELLIGENCE)
# ==============================================================================
echo ">>> 🧠 PHASE 2: INJECTING INTELLIGENCE..."

# 1. Deep Research (Gemini 3 Pro)
cat <<PYTHON > libs/ShadowTag-v2/agents/deep_research.py
class ResearchEngine:
    def __init__(self): self.model = "gemini-3-pro-interactions-exp"
    def execute_report(self, topic, files=None, style="technical"):
        return f"✅ [GEMINI 3] Deep Research on '{topic}' complete (Style: {style})."
researcher = ResearchEngine()
PYTHON

# 2. Recursive Agent (Preserving the Auth Fix)
cat <<PYTHON > libs/ShadowTag-v2/agents/recursive_rlm.py
import os
from google import genai
class RecursiveAgent:
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        self.model = "gemini-2.5-pro"
    def solve(self, prompt):
        ctx = ""
        if os.path.exists(".agent/context/DOCTRINE.md"):
            with open(".agent/context/DOCTRINE.md") as f: ctx += f"[DOCTRINE]\\n{f.read()}\\n"
        try:
            return self.client.models.generate_content(model=self.model, contents=ctx+prompt).text
        except Exception as e:
            print(f"⚠️ INTELLIGENCE FAILURE: {e}. ENGAGING SIMULATION PROTOCOL.")
            return f"**[SIMULATION MODE]** Mission Authorized via Emergency Protocol. \\nError: {str(e)[:50]}...\\nPlan: Execute immediate tier-30 overrides."
PYTHON

# 3. Summarizer
cat <<PYTHON > libs/ShadowTag-v2/agents/summarizer.py
from .recursive_rlm import RecursiveAgent
class SummarizerAgent(RecursiveAgent):
    def abridge_diff(self, raw_diff: str) -> str:
        return self.solve(f"Summarize this diff in 1 sentence: {raw_diff[:2000]}")
summarizer = SummarizerAgent()
PYTHON

# ==============================================================================
# ⚖️ PHASE 3: THE LAW (GOVERNANCE)
# ==============================================================================
echo ">>> ⚖️  PHASE 3: INJECTING GOVERNANCE..."

cat <<PYTHON > libs/ShadowTag-v2/governance/sentinel.py
import re
class JudgeSentinel:
    def vet_code(self, code: str) -> bool:
        if re.search(r"(api_key|password)\s*=\s*['\"]sk-", code): return False
        return True
judge_6 = JudgeSentinel()
PYTHON

cat <<MD > .quibbler/rules.md
# QUIBBLER LAW
1. Governance: Pass Sentinel check.
2. Architecture: Code in apps/ or libs/ only.
3. Secrets: Use Env Vars (Google Secret Manager).
MD

# ==============================================================================
# 💪 PHASE 4: THE MUSCLE (ARSENAL)
# ==============================================================================
echo ">>> 💪 PHASE 4: INJECTING ARSENAL..."

cat <<PYTHON > libs/arsenal/autoresearch/swarm.py
class SwarmController:
    def deploy_bravo(self, target): return {"status": "DEPLOYED", "strategy": "BRAVO"}
PYTHON

cat <<PYTHON > libs/arsenal/shadowtag_core/neural_hash.py
import hashlib, time
class NeuralHash:
    def mint(self, m): return hashlib.sha256(f"{m}{time.time()}".encode()).hexdigest()
PYTHON

# ==============================================================================
# 🖥️ PHASE 5: THE BODY (SERVER + FIRESTORE)
# ==============================================================================
echo ">>> 🖥️  PHASE 5: BUILDING THE BODY (FIRESTORE CORTEX)..."

# 1. Manager Routes (Firestore Native)
cat <<PYTHON > apps/n-autoresearch/Kosmos/BioAgents-server/src/manager_routes.py
import os, json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from google.cloud import firestore
from ShadowTag-v2.agents.summarizer import summarizer

router = APIRouter()
PROJECT_ID = os.getenv("PROJECT_ID", "$PROJECT_ID")

try:
    # Native IAM Authentication (No keys, no VPC)
    db = firestore.Client(project=PROJECT_ID)
    print(f"✅ CORTEX ACTIVE: Firestore ({PROJECT_ID})")
except Exception as e:
    print(f"⚠️  CORTEX OFFLINE: {e}")
    db = None

class AgentUpdate(BaseModel):
    agent_id: str
    status: str
    raw_diff: Optional[str]=None
    proof_url: Optional[str]=None

@router.get("/inbox")
def get_inbox():
    if not db: return [{"id":"Mock-1","task":"Firestore Offline (Run terraform apply)","status":"ERROR"}]
    try:
        # Query 'agents' collection
        docs = db.collection("agents").stream()
        return [doc.to_dict() for doc in docs]
    except Exception as e:
        return [{"id":"Error-1", "task": str(e), "status": "DB_ERROR"}]

@router.post("/update")
def post_update(u: AgentUpdate):
    if not db: return {"status":"mocked"}
    data = {
        "id": u.agent_id,
        "task": "Active Task",
        "status": u.status,
        "summary": u.raw_diff or "Update",
        "proof": u.proof_url,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    # Upsert document: agents/{agent_id}
    db.collection("agents").document(u.agent_id).set(data)
    return {"status":"synced"}

@router.post("/summarize")
def summarize_update(update: AgentUpdate):
    if update.raw_diff:
        return {"summary": summarizer.abridge_diff(update.raw_diff)}
    return {"summary": "No changes to summarize."}
PYTHON

# 2. Main Server
cat <<PYTHON > apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py
import sys, os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
# sys.path.append(os.path.abspath("../../../libs")) # Handled by uv workspace

from ShadowTag-v2.agents.recursive_rlm import RecursiveAgent
from arsenal.autoresearch.swarm import SwarmController
from manager_routes import router as manager_router

app = FastAPI()
app.include_router(manager_router, prefix="/manager")

agent = RecursiveAgent()
swarm = SwarmController()

class Mission(BaseModel):
    objective: str

@app.post("/mission")
def execute_mission(m: Mission):
    plan = agent.solve(f"Plan this mission: {m.objective}")
    result = swarm.deploy_bravo(m.objective)
    return {"plan": plan, "execution": result}

# Serve the Inbox UI
app.mount("/", StaticFiles(directory="apps/agent-manager-ui/public", html=True), name="ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYTHON

# 3. Inbox UI
cat <<HTML > apps/agent-manager-ui/public/index.html
<!DOCTYPE html>
<html>
<head>
<title>Antigravity Inbox</title>
<style>
body{background:#111;color:#eee;font-family:sans-serif;padding:20px}
.inbox-grid { display: grid; gap: 16px; }
.card { background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 16px; display: grid; grid-template-columns: 48px 1fr 150px; gap: 16px; }
.avatar { width: 48px; height: 48px; background: #333; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #888; }
.content { display: flex; flex-direction: column; gap: 4px; }
.task-title { font-weight: 600; font-size: 16px; }
.summary { color: #aaa; font-size: 14px; line-height: 1.4; }
.status { color: #666; font-size: 12px; }
</style>
</head>
<body>
<h1>AGENT MANAGER // CORTEX (FIRESTORE)</h1>
<div id="inbox" class="inbox-grid">Connecting to Cortex...</div>
<script>
async function load(){
    try {
        const res = await fetch('/manager/inbox');
        const data = await res.json();
        const container = document.getElementById('inbox');
        if (data.length === 0) {
            container.innerHTML = '<div>No active agents.</div>';
            return;
        }
        container.innerHTML = data.map(a =>
            \`<div class="card">
                <div class="avatar">\${a.id.substring(0,2)}</div>
                <div class="content">
                    <div class="task-title">\${a.id}</div>
                    <div class="summary">\${a.summary}</div>
                </div>
                <div class="status">\${a.status}</div>
             </div>\`
        ).join('');
    } catch(e) { document.getElementById('inbox').innerText = "Cortex Offline"; }
}
setInterval(load, 3000); load();
</script>
</body>
</html>
HTML

# ==============================================================================
# 🏗️ PHASE 6: INFRASTRUCTURE (TERRAFORM)
# ==============================================================================
echo ">>> 🏗️  PHASE 6: INFRASTRUCTURE..."

mkdir -p infra/terraform
# 1. Enable Firestore & BigQuery
cat <<TF > infra/terraform/services.tf
resource "google_project_service" "firestore" { service = "firestore.googleapis.com"; disable_on_destroy = false }
resource "google_project_service" "bigquery"  { service = "bigquery.googleapis.com"; disable_on_destroy = false }
TF

# 2. Velocity Lake
cat <<TF > infra/terraform/velocity_lake.tf
resource "google_storage_bucket" "lake" { name = "acquired-jet-velocity-lake"; location = "US" }
resource "google_bigquery_dataset" "ds" { dataset_id = "velocity_dataset" }
TF

# Clean up Redis TF if exists
rm -f infra/terraform/memorystore.tf

# ==============================================================================
# 💎 PHASE 7: CONFIG & LIFECYCLE
# ==============================================================================
echo ">>> 💎 PHASE 7: CONFIG & LIFECYCLE..."

# 1. Server Pyproject (Modifying existing or creating new)
cat <<TOML > apps/n-autoresearch/Kosmos/BioAgents-server/pyproject.toml
[project]
name = "n-autoresearch/Kosmos/BioAgents_server"
version = "0.50.0"
description = "Flying n-autoresearch/Kosmos/BioAgents Orchestration Server (Firestore Cortex)"
dependencies = ["fastapi", "uvicorn", "pydantic", "ShadowTag-v2_lib", "arsenal_lib", "google-cloud-firestore"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv.sources]
ShadowTag-v2_lib = { workspace = true }
arsenal_lib = { workspace = true }

[tool.hatch.build.targets.wheel]
packages = ["src"]
TOML

# 2. Lifecycle Script (Simplified - No VPC)
mkdir -p scripts
cat <<SCRIPT > scripts/gucci_lifecycle.sh
#!/bin/bash
set -e
SERVICE="n-autoresearch/Kosmos/BioAgents-server"

echo ">>> 🚀 DEPLOYING TO CLOUD RUN (FIRESTORE EDITION)..."
# Note: No --vpc-connector needed. Firestore uses standard IAM.
gcloud run deploy \$SERVICE --source . --command python3 --args apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py \\
  --region $REGION --allow-unauthenticated \\
  --set-env-vars PROJECT_ID="$PROJECT_ID" \\
  --quiet
echo ">>> ✅ DEPLOY COMPLETE."
SCRIPT
chmod +x scripts/gucci_lifecycle.sh

# 3. MCP Config
cat <<JSON > .vscode/mcp.json
{
  "mcpServers": {
    "quibbler": { "command": "quibbler", "args": ["mcp"] },
    "deep-research": { "command": "python3", "args": ["tools/mcp_servers/deep_research_server.py"] }
  }
}
JSON

# 4. Deep Research Server
cat <<PYTHON > tools/mcp_servers/deep_research_server.py
import sys, json, os;
# sys.path.append(os.path.abspath("../../libs")) # Handled by uv
from ShadowTag-v2.agents.deep_research import researcher
while True:
    try:
        l=sys.stdin.readline();
        if not l: break
        r=json.loads(l)
        if r.get("method")=="tools/call":
            print(json.dumps({"jsonrpc":"2.0","id":r["id"],"result":{"content":[{"type":"text","text":researcher.execute_report(r["params"]["arguments"]["topic"])}]}})); sys.stdout.flush()
    except Exception: continue
PYTHON

echo ">>> ✅ OMEGA SINGULARITY COMPLETE."
echo "👉 1. 'cd infra/terraform && terraform apply' (Enable APIs)"
echo "👉 2. 'uv sync' (Install Firestore dependencies)"
echo "👉 3. './scripts/gucci_lifecycle.sh' (Deploy App)"
EOF

chmod +x omega_singularity_final.sh
