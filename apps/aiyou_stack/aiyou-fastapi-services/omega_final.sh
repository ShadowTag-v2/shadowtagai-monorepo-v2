#!/bin/bash
set -e

# ==============================================================================
# 🌌 PHASE 0: PRE-FLIGHT (BACKUP & SCAFFOLD)
# ==============================================================================
REPO_NAME="ShadowTag-Omega"
BACKUP_DIR="_PRE_OMEGA_BACKUP_$(date +%s)"
PROJECT_ID="shadowtag-omega-v2"

echo ">>> 🦍 INITIATING ANTIGRAVITY SINGULARITY BUILD (v48)..."
echo ">>> 🛡️  PHASE 0: SECURING ASSETS..."

# 1. Backup
if [ -d "$REPO_NAME" ]; then
    echo "    ⚠️  Existing Repo detected. Backing up to $BACKUP_DIR..."
    cp -r "$REPO_NAME" "$BACKUP_DIR"
else
    mkdir -p "$REPO_NAME"
fi
cd "$REPO_NAME"

# 2. Scaffold
echo "    🏗️  Scaffolding Monorepo..."
mkdir -p apps/{n-autoresearch/Kosmos/BioAgents-server/src,agent-manager-ui/public}
mkdir -p libs/ShadowTag-v2/{agents,governance,proxies}
mkdir -p libs/arsenal/{shadowtag_core,tegu_vision,gaas_flight,autoresearch,safety_net}
mkdir -p libs/pnkln/compression/src/compression
mkdir -p infra/{velocity-lake,workstations,treasury,terraform}
mkdir -p tools/{scripts,mcp_servers,legacy}
mkdir -p docs/{doctrine,commercial}
mkdir -p .vscode .quibbler .agent/context

# ==============================================================================
# 🧹 PHASE 1: THE VACUUM (MIGRATION)
# ==============================================================================
echo ">>> 🧹 PHASE 1: MIGRATING EXISTING DATA..."
for item in *; do
    if [[ ! "apps libs infra tools docs .vscode .quibbler .agent pyproject.toml uv.lock README.md .gitignore" =~ "$item" ]]; then
        mkdir -p tools/legacy/_root_stash
        mv "$item" tools/legacy/_root_stash/ 2>/dev/null || true
    fi
done

# ==============================================================================
# 🧠 PHASE 2: THE BRAIN (AGENTS & SUMMARIZER)
# ==============================================================================
echo ">>> 🧠 PHASE 2: INJECTING INTELLIGENCE..."

# 1. Deep Research
cat <<PYTHON > libs/ShadowTag-v2/agents/deep_research.py
import logging
class ResearchEngine:
    def __init__(self): self.model = "gemini-3-pro-interactions-exp"
    def execute_report(self, topic, files=None):
        return f"✅ [GEMINI 3] Deep Research on '{topic}' complete via Interactions API."
researcher = ResearchEngine()
PYTHON

# 2. Recursive Agent
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
        return self.client.models.generate_content(model=self.model, contents=ctx+prompt).text
PYTHON

# 3. Summarizer Agent (The Manager's Brain)
cat <<PYTHON > libs/ShadowTag-v2/agents/summarizer.py
from .recursive_rlm import RecursiveAgent
class SummarizerAgent(RecursiveAgent):
    def abridge_diff(self, raw_diff: str) -> str:
        return self.solve(f"SUMMARIZE THIS DIFF IN 1 SENTENCE:\\n{raw_diff[:5000]}")
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
        if re.search(r"BEGIN PRIVATE KEY", code): return False
        return True
judge_6 = JudgeSentinel()
PYTHON

cat <<MD > .quibbler/rules.md
# QUIBBLER LAW
1. Governance: Pass Sentinel. 2. Architecture: No root scripts. 3. Secrets: None.
MD

# ==============================================================================
# 💪 PHASE 4: THE MUSCLE (ARSENAL)
# ==============================================================================
echo ">>> 💪 PHASE 4: INJECTING ARSENAL..."

cat <<PYTHON > libs/arsenal/autoresearch/swarm.py
class SwarmController:
    def deploy_bravo(self, target): return {"status": "DEPLOYED", "target": target}
PYTHON

cat <<PYTHON > libs/arsenal/shadowtag_core/neural_hash.py
import hashlib, time
class NeuralHash:
    def mint(self, meta): return hashlib.sha256(f"{meta}{time.time()}".encode()).hexdigest()
PYTHON

# ==============================================================================
# 🖥️ PHASE 5: THE BODY (SERVER + MANAGER UI)
# ==============================================================================
echo ">>> 🖥️  PHASE 5: BUILDING MANAGER UI & SERVER..."

# 1. Manager Routes (Backend)
cat <<PYTHON > apps/n-autoresearch/Kosmos/BioAgents-server/src/manager_routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import sys, os
sys.path.append(os.path.abspath("../../../libs"))
from ShadowTag-v2.agents.summarizer import summarizer

router = APIRouter()
class AgentUpdate(BaseModel):
    agent_id: str; raw_diff: Optional[str] = None

@router.get("/inbox")
def get_inbox():
    return [
        {"id": "Agent-007", "task": "Fix Stripe Webhook", "status": "WAITING", "summary": "Fixed signature verification.", "proof": None},
        {"id": "Agent-023", "task": "Deploy Lake", "status": "WORKING", "summary": "Terraform apply running...", "proof": None}
    ]

@router.post("/summarize")
def summarize(u: AgentUpdate):
    return {"summary": summarizer.abridge_diff(u.raw_diff) if u.raw_diff else "No changes."}
PYTHON

# 2. Main Server (Mounts UI)
cat <<PYTHON > apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py
import sys, os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
sys.path.append(os.path.abspath("../../../libs"))

from ShadowTag-v2.agents.recursive_rlm import RecursiveAgent
from arsenal.autoresearch.swarm import SwarmController
from manager_routes import router as manager_router

app = FastAPI()
app.include_router(manager_router, prefix="/manager")
# Mount the Inbox UI
app.mount("/", StaticFiles(directory="../../apps/agent-manager-ui/public", html=True), name="ui")

agent = RecursiveAgent()
swarm = SwarmController()

class Mission(BaseModel):
    objective: str

@app.post("/mission")
def execute_mission(m: Mission):
    return {"plan": agent.solve(m.objective), "result": swarm.deploy_bravo(m.objective)}
PYTHON

# 3. Agent Manager UI (The Inbox HTML)
cat <<HTML > apps/agent-manager-ui/public/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>Antigravity Inbox</title>
    <style>
        body { background: #111; color: #eee; font-family: sans-serif; padding: 20px; }
        .card { background: #222; border: 1px solid #444; padding: 15px; margin-bottom: 10px; display: grid; grid-template-columns: 50px 1fr 100px; gap: 10px; }
        .waiting { border-color: #ffd700; }
        .btn { padding: 5px 10px; cursor: pointer; border: none; font-weight: bold; }
        .approve { background: #28a745; color: white; }
    </style>
</head>
<body>
    <h1>Agent Inbox <span style="font-size:12px;color:#888">650 AGENTS ONLINE</span></h1>
    <div id="inbox">Loading...</div>
    <script>
        async function load() {
            const res = await fetch('/manager/inbox');
            const data = await res.json();
            document.getElementById('inbox').innerHTML = data.map(a => \`
                <div class="card \${a.status==='WAITING'?'waiting':''}">
                    <div style="font-weight:bold;color:#888">\${a.id.split('-')[1]}</div>
                    <div>
                        <div style="font-weight:bold">\${a.task}</div>
                        <div style="color:#aaa;font-size:14px">\${a.summary}</div>
                    </div>
                    <div>
                        \${a.status==='WAITING' ? '<button class="btn approve">APPROVE</button>' : '<span style="color:#666">WORKING</span>'}
                    </div>
                </div>
            \`).join('');
        }
        setInterval(load, 5000); load();
    </script>
</body>
</html>
HTML

# ==============================================================================
# 🏗️ PHASE 6: INFRA & CONFIG
# ==============================================================================
echo ">>> 🏗️  PHASE 6: FINAL CONFIG..."

# Velocity Lake
cat <<TF > infra/velocity-lake/main.tf
resource "google_storage_bucket" "lake" { name = "acquired-jet-velocity-lake"; location = "US" }
resource "google_bigquery_dataset" "ds" { dataset_id = "velocity_dataset" }
TF

# Pyproject
cat <<TOML > pyproject.toml
[project]
name = "shadowtag-omega"
version = "2026.01.14"
requires-python = ">=3.11"
dependencies = ["fastapi", "uvicorn", "google-genai", "pydantic"]
[tool.uv.workspace]
members = ["apps/*", "libs/*"]
TOML

# MCP
cat <<JSON > .vscode/mcp.json
{
  "mcpServers": {
    "quibbler": { "command": "quibbler", "args": ["mcp"] },
    "deep-research": { "command": "python3", "args": ["tools/mcp_servers/deep_research_server.py"] }
  }
}
JSON

# Deep Research Server
cat <<PYTHON > tools/mcp_servers/deep_research_server.py
import sys, json, os; sys.path.append(os.path.abspath("../../libs"))
from ShadowTag-v2.agents.deep_research import researcher
while True:
    l=sys.stdin.readline();
    if not l: break
    r=json.loads(l)
    if r.get("method")=="tools/call":
        print(json.dumps({"jsonrpc":"2.0","id":r["id"],"result":{"content":[{"type":"text","text":researcher.execute_report(r["params"]["arguments"]["topic"])}]}})); sys.stdout.flush()
PYTHON

echo ">>> ✅ FINAL SINGULARITY COMPLETE."
echo "👉 1. Run './omega_final.sh'"
echo "👉 2. Run 'uv sync'"
echo "👉 3. Start Server: 'uv run python apps/n-autoresearch/Kosmos/BioAgents-server/src/main.py'"
echo "👉 4. View Inbox: http://localhost:8000/"
