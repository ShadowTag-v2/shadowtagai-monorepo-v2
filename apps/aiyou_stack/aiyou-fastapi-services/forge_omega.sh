#!/bin/bash
set -e
# ==============================================================================
#  SHADOWTAG OMEGA v2: THE SOVEREIGN FOUNDRY
# ==============================================================================
# "Simplicity is the ultimate sophistication."
#
# CONTAINS:
# [1] INFRASTRUCTURE (Terraform/WIF)
# [2] ARSENAL (Tegu, Jetski, GodMode)
# [3] GOVERNANCE (Judge 6, Rules, CI)
# [4] INTERFACE (A2UI Rich Renderer)
# [5] NERVOUS SYSTEM (FastAPI, Gemini CLI)
# ==============================================================================

PROJECT_ID=$(gcloud config get-value project)
REPO_ROOT="shadowtag_omega_v2"
REGION="us-central1"

echo ">>> 🦍 INITIATING OMEGA PROTOCOL..."
echo ">>> 🎨 DESIGNING ARCHITECTURE..."

mkdir -p "$REPO_ROOT"
cd "$REPO_ROOT"

# ==============================================================================
# [1] INFRASTRUCTURE: THE FOUNDATION
# ==============================================================================
echo ">>> [1/5] POURING CONCRETE (INFRASTRUCTURE)..."
mkdir -p infra/terraform

# BLOCK 1.1: Workstation Cluster (The Cockpit)
cat <<TF > infra/terraform/main.tf
provider "google" { project = "$PROJECT_ID"; region = "$REGION" }

resource "google_compute_network" "omega_net" { name = "omega-vpc"; auto_create_subnetworks = false }
resource "google_compute_subnetwork" "omega_sub" { name = "omega-sub"; ip_cidr_range = "10.0.0.0/24"; region = "$REGION"; network = google_compute_network.omega_net.id }

resource "google_workstations_workstation_cluster" "cluster" {
  workstation_cluster_id = "omega-cluster"
  network = google_compute_network.omega_net.id
  subnetwork = google_compute_subnetwork.omega_sub.id
  location = "$REGION"
}

resource "google_workstations_workstation_config" "god_mode" {
  workstation_config_id = "god-mode-config"
  workstation_cluster_id = google_workstations_workstation_cluster.cluster.workstation_cluster_id
  location = "$REGION"
  host { gce_instance { machine_type = "e2-standard-8"; boot_disk_size_gb = 100 } }
  container {
    image = "us-central1-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest"
    env { name = "OMEGA_MODE"; value = "TRUE" }
  }
}

resource "google_workstations_workstation" "cockpit" {
  workstation_id = "omega-cockpit"
  workstation_config_id = google_workstations_workstation_config.god_mode.workstation_config_id
  workstation_cluster_id = google_workstations_workstation_cluster.cluster.workstation_cluster_id
  location = "$REGION"
}
TF

# ==============================================================================
# [2] ARSENAL: THE MUSCLE
# ==============================================================================
echo ">>> [2/5] FORGING WEAPONS (ARSENAL)..."
mkdir -p libs/arsenal/{vision,browser,godmode}

# BLOCK 2.1: TEGU VISION (Visual Anchoring Engine)
# Distinction: Uses Gemini 2.0 to "Reason" about layout, not just OCR.
cat <<PYTHON > libs/arsenal/vision/engine.py
import json
from google import genai
from google.genai import types

class TeguVision:
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="$REGION")
        self.model = "gemini-2.0-flash-exp"

    def analyze(self, file_path: str, intent: str):
        with open(file_path, "rb") as f: img = f.read()
        prompt = f"""
        TASK: {intent}
        METHODOLOGY:
        1. **Anchor**: Locate visual landmarks (headers, labels).
        2. **Region**: Define bounding boxes relative to anchors.
        3. **Extract**: Read data from regions.
        Return JSON.
        """
        res = self.client.models.generate_content(
            model=self.model, contents=[types.Part.from_bytes(img, "image/jpeg"), prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(res.text)
tegu = TeguVision()
PYTHON

# BLOCK 2.2: JETSKI (Brave Browser Agent)
# Distinction: Uses Brave if available, Vision-based navigation.
cat <<PYTHON > libs/arsenal/browser/agent.py
import asyncio, os, shutil, json, base64
from playwright.async_api import async_playwright
from google import genai
from google.genai import types

class Jetski:
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="$REGION")
        self.model = "gemini-2.0-flash-exp"

    async def surf(self, task: str, url: str):
        brave = os.getenv("BRAVE_BIN") or shutil.which("brave-browser")
        args = {"headless": True, "executable_path": brave} if brave else {"headless": True}

        async with async_playwright() as p:
            browser = await p.chromium.launch(**args)
            page = await browser.new_page()
            await page.goto(url)

            # Vision Loop (One-Shot)
            shot = await page.screenshot(format="jpeg")
            prompt = f"TASK: {task}. Analyze screen. Return JSON {{'action': 'click', 'selector': '...'}}"
            res = await self.client.models.generate_content_async(
                model=self.model, contents=[types.Part.from_bytes(shot, "image/jpeg"), prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            decision = json.loads(res.text)

            # Execute (Simplified)
            if decision.get("action") == "click":
                try: await page.click(decision["selector"])
                except: pass

            await browser.close()
            return decision
jetski = Jetski()
PYTHON

# BLOCK 2.3: GOD MODE (Direct Write)
# Distinction: The "Writer" that listens to the "Judge".
cat <<PYTHON > libs/arsenal/godmode/writer.py
import os
class GodWriter:
    def write(self, path: str, content: str):
        # Safety Check (Judge 6 Logic Inline)
        if "sk-" in content or "PRIVATE KEY" in content:
            return {"status": "BLOCKED", "reason": "Secret Detected"}

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f: f.write(content)
        return {"status": "SUCCESS", "path": path}
writer = GodWriter()
PYTHON

# ==============================================================================
# [3] GOVERNANCE: THE CONSCIENCE
# ==============================================================================
echo ">>> [3/5] CODIFYING LAW (JUDGE 6)..."
mkdir -p libs/governance/{policies,gatekeeper}

# BLOCK 3.1: The Constitution
cat <<MD > libs/governance/policies/constitution.md
# OMEGA CONSTITUTION
1. **Sovereignty**: No external dependencies that cannot be mirrored.
2. **Visual Truth**: Trust the pixels (Tegu), not the text stream.
3. **Safety**: Judge 6 must audit all 'GodMode' writes.
MD

# BLOCK 3.2: CI Gatekeeper (The Review Agent)
cat <<BASH > libs/governance/gatekeeper/audit.sh
#!/bin/bash
# JUDGE 6 AUDITOR
if ! command -v gemini &> /dev/null; then npm install -g @google/gemini-cli; fi
gemini --yolo <<EOF
You are Judge 6. Audit '.' against 'libs/governance/policies/constitution.md'.
Output 'APPROVED' or 'BLOCKED'.
EOF
BASH
chmod +x libs/governance/gatekeeper/audit.sh

# ==============================================================================
# [4] INTERFACE: THE SKIN
# ==============================================================================
echo ">>> [4/5] POLISHING GLASS (A2UI)..."
mkdir -p apps/dashboard/public

# BLOCK 4.1: Rich Renderer (Maps, Charts, Forms)
cat <<JS > apps/dashboard/public/renderer.js
class A2UIRenderer {
    constructor(t) { this.t = t; }
    render(json) {
        this.t.innerHTML = '';
        const build = (c) => {
            const el = document.createElement('div');
            el.className = \`comp-\${c.type.toLowerCase()}\`;

            if(c.type === 'Text') { el.innerText = c.props.text; if(c.props.size==='h1') el.style.fontSize='2em'; }
            if(c.type === 'Button') {
                const b = document.createElement('button');
                b.innerText = c.props.label; b.className = c.props.variant;
                el.appendChild(b);
            }
            if(c.type === 'Map') {
                el.style.height = '300px'; el.style.background = '#e0e0e0';
                el.innerText = \`🗺️ MAP [Lat: \${c.props.lat}, Lng: \${c.props.lng}]\`;
                el.style.display = 'flex'; el.style.alignItems='center'; el.style.justifyContent='center';
            }

            if(c.children) c.children.forEach(k => el.appendChild(build(k)));
            return el;
        };
        if(json.root) this.t.appendChild(build(json.root));
    }
}
JS

# BLOCK 4.2: The Dashboard
cat <<HTML > apps/dashboard/public/index.html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #111; color: #fff; font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 40px; }
        .comp-card { border: 1px solid #333; border-radius: 12px; padding: 24px; background: #1a1a1a; margin-bottom: 20px; }
        button { padding: 12px 24px; border-radius: 8px; border: none; cursor: pointer; font-weight: 600; }
        .primary { background: #2979ff; color: white; }
        .danger { background: #ff1744; color: white; }
    </style>
</head>
<body>
    <h1>SHADOWTAG OMEGA</h1>
    <input id="q" placeholder="Command the Sovereign..." style="width: 100%; padding: 16px; border-radius: 8px; border: 1px solid #333; background: #000; color: #fff; font-size: 16px;">
    <div id="ui" style="margin-top: 40px;"></div>
    <script src="renderer.js"></script>
    <script>
        document.getElementById('q').addEventListener('keypress', async (e) => {
            if(e.key === 'Enter') {
                const res = await fetch(\`/api/command?q=\${encodeURIComponent(e.target.value)}\`);
                new A2UIRenderer(document.getElementById('ui')).render(await res.json());
            }
        });
    </script>
</body>
</html>
HTML

# ==============================================================================
# [5] NERVOUS SYSTEM: THE WIRE
# ==============================================================================
echo ">>> [5/5] WIRING SYNAPSES..."
mkdir -p src config

# BLOCK 5.1: Gemini CLI Settings (The Hands)
cat <<JSON > config/cli_settings.json
{
  "coreTools": ["LSTool", "ReadFileTool", "WriteFileTool", "GrepTool"],
  "contextFiles": ["GEMINI.md"],
  "fileFiltering": { "ignorePatterns": [".git", "__pycache__"] }
}
JSON

# BLOCK 5.2: The Context Anchor
cat <<MD > GEMINI.md
# SHADOWTAG OMEGA v2
**You are the Sovereign Operator.**
- **Vision:** Use \`libs/arsenal/vision\` for documents.
- **Browser:** Use \`libs/arsenal/browser\` for web.
- **Write:** Use \`libs/arsenal/godmode\` to edit code (subject to Judge 6).
MD

# BLOCK 5.3: The Server (FastAPI)
cat <<PYTHON > src/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from libs.arsenal.vision.engine import tegu
from libs.arsenal.godmode.writer import writer

app = FastAPI()
app.mount("/", StaticFiles(directory="apps/dashboard/public", html=True), name="ui")

@app.get("/api/command")
def command(q: str):
    # SIMULATED AGENTIC ROUTER (In Prod: Gemini 2.0 Router)
    if "scan" in q:
        return {
            "root": {
                "type": "Card",
                "children": [
                    {"type": "Text", "props": {"text": "Tegu Vision Active", "size": "h1"}},
                    {"type": "Text", "props": {"text": "Drop file to analyze layout."}}
                ]
            }
        }
    return {
        "root": {
            "type": "Card",
            "children": [
                {"type": "Text", "props": {"text": f"Executed: {q}", "size": "h1"}},
                {"type": "Map", "props": {"lat": 37.7749, "lng": -122.4194}}
            ]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
PYTHON

# BLOCK 5.4: Dependencies
cat <<TXT > requirements.txt
fastapi
uvicorn
google-genai
playwright
pydantic
TXT

# BLOCK 5.5: Git Ignore
cat <<GIT > .gitignore
__pycache__
venv
.DS_Store
*.tfstate
GIT

echo ">>> 🏁 OMEGA v2 GENERATED."
echo ">>> LOCATION: ./$REPO_ROOT"
echo ">>> NEXT: 'uv sync' -> 'playwright install chromium' -> 'python src/main.py'"
