#!/bin/bash
set -e

# --- CONFIGURATION ---
PROJECT_ID="shadowtag-omega-v2"
REPO="pikeymickey/ShadowTag-v2"
POOL_NAME="github-pool"
REGION="us-central1"

echo ">>> 🦍 INITIALIZING ANTIGRAVITY GOD MODE..."

# ------------------------------------------------------------------
# 1. INSTALL DEPENDENCIES (GenAI Toolbox & SDKs)
# ------------------------------------------------------------------
echo ">>> 📦 Installing GenAI Toolbox & Google Cloud SDKs..."
uv pip install toolbox-core toolbox-langchain google-genai google-cloud-aiplatform || \
pip install toolbox-core toolbox-langchain google-genai google-cloud-aiplatform

# ------------------------------------------------------------------
# 2. IMPLANT RLM AGENT (Recursive Language Model)
# ------------------------------------------------------------------
echo ">>> 🧬 Injecting Recursive Agent Code..."
mkdir -p src/libs/aiyou/agents
cat <<PYTHON > src/libs/aiyou/agents/recursive_rlm.py
"""
Recursive Language Model (RLM) Agent
Navigates documents as environments without vector search.
"""
import os
from typing import List
from google import genai
from google.genai import types

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "$PROJECT_ID")
LOCATION = "$REGION"
MODEL_ID = "gemini-1.5-flash-002"

class TextEnvironment:
    def __init__(self, file_path: str, chunk_size: int = 2000):
        self.file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.full_text = f.read()
        except FileNotFoundError:
            self.full_text = "ERROR: File not found."
        self.total_length = len(self.full_text)
        self.chunk_size = chunk_size

    def read(self, start_index: int) -> str:
        start_index = max(0, min(start_index, self.total_length))
        end_index = min(start_index + self.chunk_size, self.total_length)
        return self.full_text[start_index:end_index]

class RecursiveAgent:
    def __init__(self):
        self.client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        self.max_depth = 3

    def _call_gemini(self, prompt: str, context_chunk: str) -> str:
        full_prompt = f"{prompt}\n\n--- CHUNK ---\n{context_chunk}\n----------------"
        try:
            response = self.client.models.generate_content(
                model=MODEL_ID, contents=full_prompt,
                config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=50)
            )
            return response.text.strip()
        except Exception as e:
            return f"ANSWER Error: {str(e)}"

    def construct_system_prompt(self, query: str, current_pos: int, total_len: int, history: List[str]) -> str:
        return f"""
        GOAL: Answer "{query}"
        STATUS: Doc Size: {total_len}, Pos: {current_pos}, History: {history[-3:]}
        COMMANDS:
        1. READ_NEXT
        2. JUMP <int>
        3. RECURSE <query>
        4. ANSWER <text>
        OUTPUT ONLY COMMAND.
        """

    def solve(self, query: str, env: TextEnvironment, start_index: int = 0, depth: int = 0) -> str:
        current_pos = start_index
        history = []
        steps = 0

        while steps < 10:
            chunk = env.read(current_pos)
            prompt = self.construct_system_prompt(query, current_pos, env.total_length, history)
            decision = self._call_gemini(prompt, chunk)
            history.append(decision)

            if decision.startswith("ANSWER"): return decision.replace("ANSWER ", "")
            elif decision.startswith("JUMP"):
                try: current_pos = int(decision.split()[1])
                except: current_pos += env.chunk_size
            elif decision.startswith("READ_NEXT"): current_pos += env.chunk_size
            elif decision.startswith("RECURSE"):
                if depth < self.max_depth:
                    sub_res = self.solve(decision.replace("RECURSE ", ""), env, current_pos, depth + 1)
                    if "could not find" not in sub_res: return sub_res
            else: current_pos += env.chunk_size

            steps += 1
            if current_pos >= env.total_length: return "End of document."
        return "Not found."
PYTHON

# ------------------------------------------------------------------
# 3. CONFIGURE MEMORY & FLOW STATE
# ------------------------------------------------------------------
echo ">>> 🧠 Implanting Memory & Style Guide..."
mkdir -p .gemini
cat <<YAML > .gemini/config.yaml
version: 1
memory_config:
  disabled: false
YAML
cat <<MD > .gemini/styleguide.md
# Antigravity Coding Standards
- **Auth:** Workload Identity Federation (Keyless).
- **AI:** Use 'google-genai' SDK and RLM Agents.
- **Deploy:** GitHub Actions -> Cloud Run.
MD

# ------------------------------------------------------------------
# 4. REPAIR MCP SERVERS
# ------------------------------------------------------------------
echo ">>> 🔌 Wiring MCP Servers..."
mkdir -p ~/.gemini
cat <<JSON > ~/.gemini/mcp.json
{
  "ide": { "hasSeenNudge": true },
  "mcpServers": {
    "github": {
      "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "\${env:GITHUB_TOKEN}" }
    },
    "flyingmonkeys": {
      "command": "$PWD/.venv/bin/python3",
      "args": ["-m", "libs.aiyou.main"],
      "cwd": "$PWD",
      "env": { "PYTHONPATH": "$PWD/src", "PORT": "8080", "GOOGLE_CLOUD_PROJECT": "$PROJECT_ID" }
    },
    "bigquery": {
      "command": "npx", "args": ["-y", "mcp-bigquery-server"],
      "env": { "BIGQUERY_PROJECT": "$PROJECT_ID" }
    }
  }
}
JSON

# ------------------------------------------------------------------
# 5. SETUP WORKLOAD IDENTITY (Keyless)
# ------------------------------------------------------------------
echo ">>> 🛡️  Configuring Keyless Auth..."
if ! gcloud iam workload-identity-pools describe "$POOL_NAME" --project="$PROJECT_ID" --location="global" >/dev/null 2>&1; then
    gcloud iam workload-identity-pools create "$POOL_NAME" --project="$PROJECT_ID" --location="global" --display-name="GitHub Pool"
    gcloud iam workload-identity-pools providers create-oidc "github-provider" \
      --project="$PROJECT_ID" --location="global" --workload-identity-pool="$POOL_NAME" \
      --display-name="GitHub Provider" --issuer-uri="https://token.actions.githubusercontent.com" \
      --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository"
fi
PROJECT_NUM=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
PROVIDER_PATH="projects/$PROJECT_NUM/locations/global/workloadIdentityPools/$POOL_NAME/providers/github-provider"

# ------------------------------------------------------------------
# 6. GENERATE CI/CD PIPELINE
# ------------------------------------------------------------------
echo ">>> 🚀 Generating Deployment Workflow..."
mkdir -p .github/workflows
cat <<YAML > .github/workflows/deploy.yml
name: Antigravity Deploy
on: { push: { branches: ["main"] } }
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions: { contents: 'read', id-token: 'write' }
    steps:
    - uses: 'actions/checkout@v4'
    - id: 'auth'
      uses: 'google-github-actions/auth@v2'
      with:
        workload_identity_provider: '$PROVIDER_PATH'
        service_account: 'flyingmonkeys-sa@$PROJECT_ID.iam.gserviceaccount.com'
    - uses: 'google-github-actions/deploy-cloudrun@v2'
      with: { service: 'flyingmonkeys-server', region: '$REGION', source: '.' }
YAML

# ------------------------------------------------------------------
# 7. SCAN ISSUES
# ------------------------------------------------------------------
echo ">>> 🔍 Compiling Issues..."
echo "# OUTSTANDING ISSUES" > CURRENT_ISSUES.md
echo "## 1. Syntax" >> CURRENT_ISSUES.md
find . -name "*.py" -not -path "*/.*" -exec python3 -m py_compile {} \; 2>> CURRENT_ISSUES.md || true

# ------------------------------------------------------------------
# 8. SETUP GEMINI CLI COMMANDS
# ------------------------------------------------------------------
echo ">>> 💬 Configuring Gemini Slash Commands..."
chmod +x tools/setup_gemini_commands.sh
./tools/setup_gemini_commands.sh

echo ">>> ✅ GOD MODE INSTALLED. Run the prompt below."
