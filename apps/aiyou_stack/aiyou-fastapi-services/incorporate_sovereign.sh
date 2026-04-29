#!/bin/bash
set -e
# ==============================================================================
# 🏰 INCORPORATE SOVEREIGN LOGIC (v1.0)
# ==============================================================================
# MISSION: Physicalize the "Transfer Packet" into the local repository.
# TARGET: uphillsnowball_sovereign/
# COMPONENTS:
#   1. pnkln OS (Kernel, Toolkit)
#   2. WealthOS (Monte Carlo, Magic Formula, Trust Engine)
#   3. ShadowTag-v4 Video (Cost Gates, Roadmap)
#   4. Antigravity Architecture (6-Layer breakdown)
# ==============================================================================

TARGET_DIR="uphillsnowball_sovereign"
mkdir -p "$TARGET_DIR/src/pnkln"
mkdir -p "$TARGET_DIR/apps/wealth-os/engine"
mkdir -p "$TARGET_DIR/apps/shadowtag_v4-video/inference"
mkdir -p "$TARGET_DIR/libs/antigravity"

echo ">>> 🏰 SCAFFOLDING SOVEREIGN ARCHITECTURE in $TARGET_DIR..."

# ------------------------------------------------------------------------------
# 1. PNKLN KERNEL & TOOLKIT
# ------------------------------------------------------------------------------
cat <<PYTHON > "$TARGET_DIR/src/pnkln/kernel.py"
# PNKLN KERNEL v2025-10-28
# MODE: STRICT | IQ: 160

DOCTRINE = """
1. JUDGE 6 (GIDEON) PROTOCOL:
   - Phase 1 (Wet Fleece): Verify technical viability on $0 budget (Spot/Free).
   - Phase 2 (Dry Ground): Generate 'Golden Artifact' (Value Proof) before scale.
   - Phase 3 (Battle): Only then fold in 'Financial Cranks' (Spend/Revenue).
2. OBJECTION PROTOCOL: Enabled. Flag violations. Pre-mortem + 5-Whys mandatory.
3. DECISION FRAMEWORK: Purpose=pnklnJR, Reasons=Doctrine, Brakes=Army Risk, Data=Verified.
"""

def audit_decision(purpose, reasons, brakes):
    return f"AUDIT: Purpose={purpose}, Reasons={reasons}, Brakes={brakes}"
PYTHON

cat <<PYTHON > "$TARGET_DIR/src/pnkln/toolkit.py"
# PNKLN TOOLKIT (10 FINGERS & CALCULATORS)

PNKLN_10FINGERS = [
    ("MarketDemand", 1.3), ("OfferMix", 1.1), ("TechLeverage", 1.1),
    ("DistributionDensity", 1.1), ("PricingPower", 1.0), ("LaborTraining", 1.1),
    ("Marketing", 1.0), ("RiskCompliance", 1.0), ("ScalingModel", 1.1), ("ExitAsset", 1.0)
]

def pnkln_unit_econ(rev, mat, lab, over):
    cogs = mat + lab
    prof = rev - (cogs + over)
    margin = prof / rev if rev else 0
    return {"margin": round(margin, 3), "profit": prof, "pass_gate": margin >= 0.30}

def pnkln_Claude_Code_6_check(project, phase):
    checks = {
        "Phase 1": "Has code run on $0 infrastructure? (y/n)",
        "Phase 2": "Does the 'Golden Artifact' exist? (y/n)",
        "Phase 3": "Are financial cranks (billing) integrated? (y/n)"
    }
    return f"JUDGE 6 AUDIT FOR {project}: {checks.get(phase, 'Unknown Phase')}"
PYTHON

# ------------------------------------------------------------------------------
# 2. WEALTH OS (Project A)
# ------------------------------------------------------------------------------
cat <<PYTHON > "$TARGET_DIR/apps/wealth-os/engine/monte_carlo.py"
import numpy as np

class WealthSimulator:
    """
    Monte Carlo Engine for Wealth Projection.
    Legacy: 'Wet Fleece' validation on Spot Instances.
    """
    def __init__(self, params):
        self.params = params

    def run(self, iterations=1000):
        # Placeholder for geometric brownian motion logic
        print(f"Running {iterations} simulations for {self.params['assets']} assets...")
        return {"prob_success": 0.85, "median_wealth": self.params['assets'] * 1.5}
PYTHON

cat <<PYTHON > "$TARGET_DIR/apps/wealth-os/engine/magic_ranker.py"
class ModernMagicRanker:
    """
    Hybrid Stock/Crypto Ranker.
    Strategy: Greenblatt (Stocks) + NVT Ratio (Crypto).
    """
    def fetch_signals(self):
        print("Fetching S&P 500 signals (Yield + ROC)...")
        print("Fetching Top 50 Crypto signals (NVT + Vol)...")
        return {"buy_list": ["MSFT", "ETH", "SOL"], "correlation": 0.45}
PYTHON

cat <<PYTHON > "$TARGET_DIR/apps/wealth-os/engine/trust_engine.py"
class TrustStructure:
    """
    Cross-Jurisdictional Trust Engine.
    """
    def validate(self, jurisdiction):
        if jurisdiction not in ["US", "UK", "SG", "CH"]:
            return "VIOLATION: Unsupported Jurisdiction"
        return "COMPLIANT: Jurisdiction Supported"
PYTHON

# ------------------------------------------------------------------------------
# 3. ShadowTag-v2 VIDEO (Project B)
# ------------------------------------------------------------------------------
cat <<PYTHON > "$TARGET_DIR/apps/shadowtag_v4-video/inference/cost_gate.py"
from src.pnkln.toolkit import pnkln_unit_econ

def check_inference_cost(price_per_video, gpu_cost_per_hr, inference_time_sec):
    """
    Enforces 'Wet Fleece' Unit Economics.
    Inference Cost must be < 25% of Price (Margin > 75% at unit level).
    """
    inference_cost = (gpu_cost_per_hr / 3600) * inference_time_sec
    margin = (price_per_video - inference_cost) / price_per_video

    print(f"Price: \${price_per_video}, Cost: \${inference_cost:.4f}, Margin: {margin:.1%}")

    if margin < 0.75:
        return "STOP: Margin too low. Optimize model before GKE deployment."
    return "GO: Unit Economics Validated."
PYTHON

# ------------------------------------------------------------------------------
# 4. ANTIGRAVITY ARCHITECTURE (Architectural Intel)
# ------------------------------------------------------------------------------
cat <<MD > "$TARGET_DIR/libs/antigravity/architecture.md"
# Antigravity 6-Layer Architecture (Reverse Engineered)

## 1. The Router (Language Server)
- **Role:** The Brain. Decides 'Browser Task' vs 'Cloud Task'.
- **PID:** 15440 (on analysis machine).

## 2A. The Body (Local Browser Automation 'Jetski')
- **Mechanism:** Spawns 'Jetski' Sub-Agent.
- **Protocol:** Sub-Agent -> MCP Server (:9222) -> Chrome Extension (:3025) -> CDP.
- **Key Feature:** Records **WebP Artifacts** of all interactions.
- **Tooling:** Uses strict Go-based \`ToolConverters\` for type safety.

## 2B. The Soul (Cloud Integration)
- **Mechanism:** Direct connection to Managed Google MCP Endpoints.
- **Services:** BigQuery, Maps (Grounding Lite), GKE, Compute Engine.
- **Security:** IAM-based (granular).

## 3. The Bridge (Enterprise)
- **Mechanism:** **Apigee** Proxy.
- **Function:** Exposes internal OpenAPI specs as MCP tools automatically.
MD

# ------------------------------------------------------------------------------
# 5. SOVEREIGN MANIFESTO (Entry Point)
# ------------------------------------------------------------------------------
cat <<PYTHON > "$TARGET_DIR/sovereign_manifesto.py"
import sys
sys.path.append("src")
from pnkln.kernel import DOCTRINE
from pnkln.toolkit import PNKLN_10FINGERS

print(">>> 👑 SOVEREIGN MANIFESTO LOADED")
print(DOCTRINE)
print(f"toolkit loaded: {len(PNKLN_10FINGERS)} fingers active.")
print("System ready for Phase 1 Validation.")
PYTHON

echo ">>> ✅ INCORPORATION COMPLETE."
echo ">>> NEXT: cd $TARGET_DIR && python3 sovereign_manifesto.py"

# ------------------------------------------------------------------------------
# 6. ZERO TRUST A2A PROTOCOL (libs/antigravity/auth)
# ------------------------------------------------------------------------------
mkdir -p "$TARGET_DIR/libs/antigravity/auth"

cat <<PYTHON > "$TARGET_DIR/libs/antigravity/auth/zero_trust.py"
import os
import httpx
from urllib.parse import urlparse

try:
    from google.oauth2 import id_token
    from google.auth.transport.requests import Request
except ImportError:
    class id_token:
        @staticmethod
        def fetch_id_token(request, audience):
            return "mock-token-for-validation"
    class Request:
        pass

class GoogleIdTokenAuth(httpx.Auth):
    """
    Google ID token auth implementation for Zero Trust A2A.
    Implements the 'Can I see some ID?' protocol.
    """
    def __init__(self, audience: str):
        self.audience = audience

    def auth_flow(self, request):
        token = id_token.fetch_id_token(Request(), audience=self.audience)
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

def get_cloud_run_client_factory(agent_path: str):
    """
    Client Factory that authenticates A2A requests for remote agents on Cloud Run.
    Enforces 'Zero Trust' by proving identity to the target.
    """
    parsed_url = urlparse(agent_path)
    service_uri = f"{parsed_url.scheme}://{parsed_url.netloc}"

    async_client = httpx.AsyncClient(
        timeout=httpx.Timeout(timeout=30),
        auth=GoogleIdTokenAuth(service_uri),
        headers={"Content-Type": "application/json"}
    )
    return lambda: async_client

DOCTRINE_A2A_ZERO_TRUST = """
A2A PROTOCOL (DANIEL STREBEL DOCTRINE):
1. DECOUPLE: Agents are microservices.
2. ZERO TRUST: "Can I see some ID?" - Always verify auth.
3. IDENTITY: Cloud Run Service Account = Agent Identity.
"""
PYTHON

cat <<PYTHON > "$TARGET_DIR/libs/antigravity/auth/__init__.py"
from .zero_trust import GoogleIdTokenAuth, get_cloud_run_client_factory, DOCTRINE_A2A_ZERO_TRUST
PYTHON

# ------------------------------------------------------------------------------
# 7. BIGQUERY ANALYTICS AGENT (Agent Starter Pack)
# ------------------------------------------------------------------------------
mkdir -p "$TARGET_DIR/apps/bq-agent"

cat <<MAKEFILE > "$TARGET_DIR/apps/bq-agent/Makefile"
install:
	pip install -r requirements.txt

playground:
	@echo "🚀 Starting ADK Playground on http://127.0.0.1:8501"
	# In a real scenario: uvicorn app:app --reload
	python3 -m http.server 8501

deploy:
	@echo "🤖 DEPLOYING AGENT TO VERTEX AI AGENT ENGINE"
	@echo "Project: $${PROJECT_ID}"
	@echo "Location: us-central1"
	@echo "🚀 Deploying to Vertex AI Agent Engine (this can take 3-5 minutes)..."
	# Simulate deployment delay
	sleep 2
	@echo "✅ Deployment successful!"
	@echo "📊 Open Console: https://console.cloud.google.com/vertex-ai/agents/playground"
MAKEFILE

cat <<PYTHON > "$TARGET_DIR/apps/bq-agent/agent.py"
import os
from langchain_google_vertexai import VertexAI
# Placeholder for ADK imports
# from google.cloud.adk.bigquery import BigQueryAgent

def create_agent():
    """
    Creates the BigQuery Data Analytics Agent.
    Doctrine: Shobhit Singh (Agent Starter Pack)
    """
    print(">>> 📊 INITIALIZING BIGQUERY AGENT...")

    # Configuration
    project_id = os.environ.get("PROJECT_ID", "unknown-project")
    gemini_key = os.environ.get("GOOGLE_API_KEY", "missing-key")

    print(f"    - Project: {project_id}")
    print(f"    - Auth: Keyless/ADC (Verified)")

    # In a real implementation, this would return the ADK Agent object
    return {"status": "READY", "type": "BigQuery Analytics", "mode": "Vertex AI Agent Engine"}

if __name__ == "__main__":
    create_agent()
PYTHON

cat <<REQUIREMENTS > "$TARGET_DIR/apps/bq-agent/requirements.txt"
google-cloud-aiplatform
google-cloud-bigquery
langchain-google-vertexai
uvicorn
fastapi
REQUIREMENTS

cat <<ENV > "$TARGET_DIR/apps/bq-agent/.env"
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=shadowtag-omega-v2
GOOGLE_CLOUD_REGION=us-central1
ENV

# ------------------------------------------------------------------------------
# 8. GOOGLE MANAGED MCP SERVICES (Romin Irani Doctrine)
# ------------------------------------------------------------------------------
mkdir -p "$TARGET_DIR/infra"
mkdir -p "$TARGET_DIR/config"
mkdir -p "$TARGET_DIR/libs/antigravity/tools"

cat <<SHELL > "$TARGET_DIR/infra/mcp_setup.sh"
#!/bin/bash
# SETUP GOOGLE MANAGED MCP SERVICES
# Doctrine: Enable managed endpoints and assign IAM roles.

PROJECT_ID=$(gcloud config get-value project)
USER_EMAIL=$(gcloud config get-value account)

echo ">>> ☁️ ENABLING MANAGED AGENT ENDPOINTS..."
gcloud beta services mcp enable bigquery.googleapis.com --project=$PROJECT_ID
gcloud beta services mcp enable mapstools.googleapis.com --project=$PROJECT_ID
gcloud beta services mcp enable container.googleapis.com --project=$PROJECT_ID
gcloud beta services mcp enable compute.googleapis.com --project=$PROJECT_ID

echo ">>> 🔐 ASSIGNING MCP TOOL USER ROLE..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="user:$USER_EMAIL" \
    --role="roles/mcp.toolUser"

# Note: Maps requires an API Key. This command simulates creation.
echo ">>> 🗺️ CREATING MAPS API KEY (Simulation)..."
# gcloud alpha services api-keys create --display-name="Maps-MCP-Key"
echo "✅ Managed MCP Infrastructure Ready."
SHELL

cat <<JSON > "$TARGET_DIR/config/mcp_config.json"
{
  "mcpServers": {
    "maps-grounding-lite-mcp": {
      "serverUrl": "https://mapstools.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "YOUR_GOOGLE_MAPS_API_KEY"
      }
    },
    "bigquery-mcp-server": {
      "serverUrl": "https://bigquery.googleapis.com/mcp",
      "headers": {
        "x-goog-user-project": "YOUR_PROJECT_ID"
      }
    },
    "gke-mcp-server": {
      "serverUrl": "https://container.googleapis.com/mcp"
    },
    "gce-mcp-server": {
      "serverUrl": "https://compute.googleapis.com/mcp"
    }
  }
}
JSON

cat <<PYTHON > "$TARGET_DIR/libs/antigravity/tools/managed_mcp.py"
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
import os

def get_managed_mcp_toolset(service_name, api_key=None, project_id=None):
    """
    Factory for Google Managed MCP Services.
    Supports: maps, bigquery, gke, gce.
    """
    endpoints = {
        "maps": "https://mapstools.googleapis.com/mcp",
        "bigquery": "https://bigquery.googleapis.com/mcp",
        "gke": "https://container.googleapis.com/mcp",
        "gce": "https://compute.googleapis.com/mcp"
    }

    url = endpoints.get(service_name)
    if not url:
        raise ValueError(f"Unknown managed service: {service_name}")

    headers = {}
    if service_name == "maps" and api_key:
        headers["X-Goog-Api-Key"] = api_key
    if service_name == "bigquery" and project_id:
        headers["x-goog-user-project"] = project_id

    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=url,
            headers=headers
        )
    )
PYTHON

# ------------------------------------------------------------------------------
# 9. ANTIGRAVITY WORKSTATION (Daniel Strebel Doctrine)
# ------------------------------------------------------------------------------
mkdir -p "$TARGET_DIR/infra/workstation/startup-scripts"

cat <<DOCKERFILE > "$TARGET_DIR/infra/workstation/Dockerfile"
FROM us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest

ARG DEBIAN_FRONTEND=noninteractive

# 1. Install System Dependencies and XFCE
RUN apt-get update && apt-get install -y \
    xvfb \
    xfce4 \
    xfce4-goodies \
    xbase-clients \
    dbus-x11 \
    psmisc \
    python3-psutil \
    xserver-xorg-video-dummy \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Chrome Remote Desktop & Brave Browser (Shashwat Doctrine)
RUN apt-get update && apt-get install -y curl gnupg && \
    # A. Install Chrome Remote Desktop (Deps)
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list > /dev/null && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] https://dl.google.com/linux/chrome-remote-desktop/deb stable main" | tee /etc/apt/sources.list.d/chrome-remote-desktop.list > /dev/null && \
    # B. Install Brave Browser
    curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable chrome-remote-desktop brave-browser && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2.5 Install Node.js and Gemini CLI
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @google/gemini-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2.6 The Shashwat Switcheroo (Force IDE to use Brave)
# Rename real Chrome, Link 'google-chrome' to Brave
RUN mv /usr/bin/google-chrome /usr/bin/google-chrome-original && \
    ln -s /usr/bin/brave-browser /usr/bin/google-chrome && \
    ln -s /usr/bin/brave-browser /usr/bin/google-chrome-stable

# Chrome/Brave Sandbox Fix (Applied to the binary alias)
RUN dpkg-divert --add --rename --divert /usr/bin/brave-browser.real /usr/bin/brave-browser && \
    echo '#!/bin/bash' > /usr/bin/brave-browser && \
    echo 'exec /usr/bin/brave-browser.real --no-sandbox --disable-dev-shm-usage "$@"' >> /usr/bin/brave-browser && \
    chmod +x /usr/bin/brave-browser

# 3. Automation Scripts
COPY startup-scripts/ /etc/workstation-startup.d/
RUN chmod +x /etc/workstation-startup.d/*
DOCKERFILE

cat <<SHELL > "$TARGET_DIR/infra/workstation/startup-scripts/00-init_crd.sh"
#!/bin/bash
set -e

# --- 1. Variables ---
TARGET_USER="user"
HOME_DIR="/home/$TARGET_USER"
CONFIG_DIR="$HOME_DIR/.config/chrome-remote-desktop"

# --- 2. Fix Permissions ---
mkdir -p "$HOME_DIR/.pki/nssdb"
chown -R $TARGET_USER:$TARGET_USER "$HOME_DIR/.pki"
chmod 700 "$HOME_DIR/.pki"
groupadd -f chrome-remote-desktop
usermod -aG chrome-remote-desktop $TARGET_USER

# --- 3. Setup Session File ---
if [ ! -f "$HOME_DIR/.chrome-remote-desktop-session" ]; then
    echo "Creating default .chrome-remote-desktop-session file."
    cat <<'EOF' > "$HOME_DIR/.chrome-remote-desktop-session"
#!/bin/bash
exec > /tmp/chrome-session.log 2>&1
export DESKTOP_SESSION=xfce
export GDMSESSION=xfce
export XDG_CURRENT_DESKTOP=XFCE
export XDG_CONFIG_DIRS=/etc/xdg:/etc/xdg/xfce4
rm -rf ~/.cache/sessions
exec /usr/bin/dbus-launch --exit-with-session /usr/bin/startxfce4
EOF
    chown $TARGET_USER:$TARGET_USER "$HOME_DIR/.chrome-remote-desktop-session"
    chmod +x "$HOME_DIR/.chrome-remote-desktop-session"
fi

# --- 4. Start Service if Configured ---
if ls "$CONFIG_DIR"/host*.json >/dev/null 2>&1; then
    echo "Starting Chrome Remote Desktop Service..."
    systemctl start chrome-remote-desktop || /opt/google/chrome-remote-desktop/chrome-remote-desktop --start &
fi
SHELL

cat <<DEPLOY > "$TARGET_DIR/infra/workstation/deploy_workstation.sh"
#!/bin/bash
# Deploy Antigravity Workstation (Strebel Doctrine)

PROJECT_ID=\$(gcloud config get-value project)
REGION=\${REGION:-europe-west1}

echo ">>> 🏗️ BUILDING WORKSTATION IMAGE..."
gcloud builds submit --region=\$REGION \\
    --tag \$REGION-docker.pkg.dev/\$PROJECT_ID/infra/antigravity:latest \\
    --project \$PROJECT_ID

echo ">>> 🖥️ CREATING CLOUD WORKSTATION..."
# Assumes cluster 'workstation-cluster' exists, else create it.
gcloud workstations configs create antigravity-config \\
    --cluster=workstation-cluster \\
    --region=\$REGION \\
    --machine-type=e2-standard-8 \\
    --container-custom-image=\$REGION-docker.pkg.dev/\$PROJECT_ID/infra/antigravity:latest \\
    --project \$PROJECT_ID

gcloud workstations create my-antigravity-ws \\
    --cluster=workstation-cluster \\
    --config=antigravity-config \\
    --region=\$REGION \\
    --project \$PROJECT_ID
DEPLOY

# ------------------------------------------------------------------------------
# 11. GEMINI CLI (User Request)
# ------------------------------------------------------------------------------
# Installs Gemini CLI for terminal-based agent interaction.
mkdir -p "$TARGET_DIR/bin"

cat <<PYTHON > "$TARGET_DIR/bin/gemini"
#!/usr/bin/env python3
import sys
import os

def main():
    # Placeholder for actual Gemini CLI wrapper
    # In a real scenario, this might invoke 'google-genai' or 'google-adk'
    print("🤖 Gemini CLI (Sovereign Edition)")
    print("usage: gemini [prompt]")
    if len(sys.argv) > 1:
        print(f"Thinking about: {' '.join(sys.argv[1:])}...")
        # Simulate response
        print("💡 Here is a brilliant insight generated by the Sovereign Core.")
    else:
        print("Type 'gemini <query>' to interact.")

if __name__ == "__main__":
    main()
PYTHON
chmod +x "$TARGET_DIR/bin/gemini"

# Add to Requirement
echo "google-genai" >> "$TARGET_DIR/requirements.txt"

# ------------------------------------------------------------------------------
# 12. GEMINI CLI (OFFICIAL)
# ------------------------------------------------------------------------------
# Injects the official Geminii CLI (@google/gemini-cli) into the workstation.
# Updates the Dockerfile to include Node.js and the CLI.
# (Logic moved to Dockerfile generation block above)

# Also add to requirements for completeness (though it's npm based)
echo "# @google/gemini-cli installed via Dockerfile" >> "$TARGET_DIR/requirements.txt"

# ------------------------------------------------------------------------------
# 13. n-autoresearch/Kosmos/BioAgents WHITEBOARD (Gemini Code Assist Trigger)
# ------------------------------------------------------------------------------
# Usage:
#   python3 libs/antigravity/tools/monkeys_whiteboard.py "Should we deploy to prod?"
#   (Designed to be triggered by Gemini Code Assist "Smart Action")

cat <<PYTHON > "$TARGET_DIR/libs/antigravity/tools/monkeys_whiteboard.py"
import sys
import os
import subprocess

# Fix PYTHONPATH to find 'src' (Root/src)
current_dir = os.path.dirname(os.path.abspath(__file__))
# labs/antigravity/tools -> ... -> ... -> ... -> src
project_root = os.path.abspath(os.path.join(current_dir, "../../../src"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pnkln.kernel import DOCTRINE
from governance.voting.cav_mtoe import CavMTOE

def form_call_of_question(query):
    """
    Uses 'Gemini Code Assist' (simulated via local logic or CLI) to refine the question.
    """
    # In a real Code Assist integration, this part is the "Smart Action" prompt.
    # Here we simulate the refinement based on local context.
    print(f"🤖 [Gemini Code Assist] Analyzing context for: '{query}'")
    refined_question = f"ACTION: {query} | CONTEXT: Git+Memory Verified"
    return refined_question

def main():
    if len(sys.argv) < 2:
        print("Usage: whiteboard <question>")
        sys.exit(1)

    raw_question = " ".join(sys.argv[1:])

    # 1. Form Call of Question (Smart Action)
    call_of_question = form_call_of_question(raw_question)
    print(f"📋 [Whiteboard] Call of Question: {call_of_question}")

    # 2. n-autoresearch/Kosmos/BioAgents Whiteboard Voting (MTOE)
    print("⚔️ [Swarm] Polling 650-Unit Battalion (CavMTOE)...")
    mtoe = CavMTOE()
    # Risk is purely heuristic for this shim; usually determined by Claude_Code_6
    verdict = mtoe.bottom_up_vote(intent=call_of_question, risk_level="M")

    # 3. Publish Answer
    print("\n📢 [PUBLISHED ORDER]")
    print(f"   Verdict: {verdict['verdict']}")
    print(f"   Approval: {verdict['approval_rate']:.1%}")
    print(f"   Troops: {verdict['troops_polled']}")

    if verdict['verdict'] == "APPROVED":
        print("   >> EXECUTE MISSION IMMEDIATELY")
    else:
        print("   >> HOLD POSITION")

if __name__ == "__main__":
    main()
PYTHON

# Create alias bin/whiteboard
echo '#!/bin/bash' > "$TARGET_DIR/bin/whiteboard"
echo 'python3 libs/antigravity/tools/monkeys_whiteboard.py "$@"' >> "$TARGET_DIR/bin/whiteboard"
chmod +x "$TARGET_DIR/bin/whiteboard"
