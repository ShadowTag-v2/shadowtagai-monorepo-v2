#!/bin/bash
set -e

# --- CONFIGURATION ---
PROJECT_ID="acquired-jet-478701-b3"
REGION="us-central1"
SERVICE_NAME="n-autoresearch/Kosmos/BioAgents-rlm"
# We use Pro for the "compression" intelligence, Flash for serving
COMPILER_MODEL="gemini-1.5-pro"
SERVING_MODEL="gemini-2.5-flash"

echo ">>> 🧠 INITIATING RECURSIVE FOLD PROTOCOL..."
echo ">>> ⚠️  WARNING: Upgrading Memory Architecture to RLM."
sleep 2

# ==============================================================================
# PHASE 1: STRUCTURE (The Container)
# ==============================================================================
# (Standard Monorepo Setup)
echo ">>> [1/5] 🏗️  Ensuring Monorepo Structure..."
mkdir -p apps/n-autoresearch/Kosmos/BioAgents-server libs/ShadowTag-v2/agents .gemini

cat <<TOML > pyproject.toml
[project]
name = "shadowtag-rlm"
version = "2.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi", "uvicorn", "google-genai", "pydantic"
]
[tool.uv.workspace]
members = ["apps/*", "libs/*"]
TOML

# ==============================================================================
# PHASE 2: THE RECURSIVE DEFINITION (The "Fold" Logic)
# ==============================================================================
echo ">>> [2/5] 🌀 Defining Recursive Prompts..."

# This is the "Prompt that updates the Prompt"
cat <<MARKDOWN > .gemini/compressor_prompt.md
You are the Cortex. Your job is not to answer, but to **FOLD**.
You will receive:
1. The Current Mental State (a compressed summary of all knowledge).
2. New Information (a user query or document).

**GOAL:** Output a NEW Mental State that perfectly integrates the new information into the old state.
- Discard fluff.
- Keep facts, rules, and intent.
- Resolution: High.
MARKDOWN

# ==============================================================================
# PHASE 3: THE CODE (Recursive Agent)
# ==============================================================================
echo ">>> [3/5] 🧬 Injecting RLM Engine..."

cat <<PYTHON > libs/ShadowTag-v2/agents/recursive_rlm.py
import os
from google import genai
from google.genai import types

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "$PROJECT_ID")
LOCATION = "$REGION"

class RecursiveMemory:
    """
    The RLM Engine.
    Instead of RAG (lookup), we use Recursion (update).
    """
    def __init__(self):
        self.client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        # In a real RLM, this state persists in a fast KV store (Redis/Firestore).
        # For this demo, we initialize it empty.
        self.mental_state = "System initialized. No user data yet."

    def fold(self, new_input: str):
        """
        The Singularity Step: Compressing input into the persistent state.
        """
        with open(".gemini/compressor_prompt.md", "r") as f:
            sys_prompt = f.read()

        prompt = f"CURRENT STATE:\\n{self.mental_state}\\n\\nNEW INPUT:\\n{new_input}"

        # We use the smarter model (Pro) to perform the compression
        response = self.client.models.generate_content(
            model="$COMPILER_MODEL",
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=sys_prompt)
        )
        self.mental_state = response.text
        return self.mental_state

    def answer(self, query: str):
        """
        Answering based ONLY on the compressed Mental State.
        """
        prompt = f"CONTEXT:\\n{self.mental_state}\\n\\nUSER QUERY:\\n{query}"

        # We use the fast model (Flash) to serve the answer
        response = self.client.models.generate_content(
            model="$SERVING_MODEL",
            contents=prompt
        )
        return response.text

PYTHON

# ==============================================================================
# PHASE 4: THE INTERFACE (API)
# ==============================================================================
echo ">>> [4/5] 🔌 Wiring the Server..."

cat <<PYTHON > apps/n-autoresearch/Kosmos/BioAgents-server/main.py
import sys, os
# Path injection for Monorepo
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../libs')))

from fastapi import FastAPI
from pydantic import BaseModel
from ShadowTag-v2.agents.recursive_rlm import RecursiveMemory

app = FastAPI()
# Initialize the Singularity
brain = RecursiveMemory()

class InputPayload(BaseModel):
    text: str

@app.post("/fold")
def fold_memory(payload: InputPayload):
    """Feeds the model new data to memorize."""
    new_state = brain.fold(payload.text)
    return {"status": "folded", "current_mental_state": new_state}

@app.post("/ask")
def ask_agent(payload: InputPayload):
    """Asks the model based on its compressed memory."""
    answer = brain.answer(payload.text)
    return {"answer": answer, "source_state": brain.mental_state}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
PYTHON

cat <<TOML > apps/n-autoresearch/Kosmos/BioAgents-server/pyproject.toml
[project]
name = "n-autoresearch/Kosmos/BioAgents-server"
version = "2.0.0"
dependencies = ["fastapi", "uvicorn", "google-genai"]
TOML

# ==============================================================================
# PHASE 5: DEPLOY
# ==============================================================================
echo ">>> [5/5] 🚀 Deploying RLM to Cloud Run..."

# Deploy command
cat <<SCRIPT > deploy_rlm.sh
#!/bin/bash
gcloud run deploy $SERVICE_NAME \\
  --source . \\
  --command python3 \\
  --args apps/n-autoresearch/Kosmos/BioAgents-server/main.py \\
  --region $REGION \\
  --allow-unauthenticated \\
  --clear-base-image \\
  --quiet
SCRIPT
chmod +x deploy_rlm.sh

echo ">>> ✅ RECURSIVE PROTOCOL READY."
echo ">>> Run './deploy_rlm.sh' to push the singularity."
