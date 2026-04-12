#!/bin/bash
set -e

# --- CONFIGURATION ---
PROJECT_ID="shadowtag-omega-v2"
REGION="us-central1"
SERVICE_NAME="n-autoresearch/Kosmos/BioAgents-server"
TARGET_MODEL="gemini-2.5-flash"  

echo ">>> 🧠 INITIATING MEMORY IMPLANT (Cloud Run Native)..."

# ------------------------------------------------------------------
# 1. SETUP MEMORY STORAGE (Repo-Based Source of Truth)
# ------------------------------------------------------------------
echo ">>> 📂 Creating Memory Structures..."
mkdir -p .gemini

# A. MANUAL MEMORY (The Style Guide)
# As per the blog: "Static, universal guidelines."
cat <<MARKDOWN > .gemini/styleguide.md
# Antigravity Coding Standards
## General
- **Tone:** Concise, professional, no fluff.
- **Language:** Python 3.13+ (Strict typing required).
- **Format:** Use 'ruff' for linting.

## Cloud Run Native
- **State:** Never store state locally. Use GCS or DB.
- **Port:** Always listen on 'PORT' env var (default 8080).
- **Logs:** Json-structured logging only (for Cloud Logging).

## Security
- **Auth:** Workload Identity Federation ONLY. No JSON keys.
MARKDOWN

# B. AUTOMATED MEMORY (The Learned Rules)
# As per the blog: "Dynamic, evolving memory... derived from interactions."
cat <<JSON > .gemini/learned_memory.json
[
  {
    "rule": "Do not line-wrap import statements in Python.",
    "source": "PR-Review-102",
    "weight": 1.0
  },
  {
    "rule": "Always use 'uv' instead of 'pip' for package management.",
    "source": "PR-Review-105",
    "weight": 0.9
  }
]
JSON

# ------------------------------------------------------------------
# 2. UPGRADE AGENT BRAIN (Recursive + Memory Aware)
# ------------------------------------------------------------------
echo ">>> 🧬 Rewriting Agent Code to use Memory..."
mkdir -p src/libs/ShadowTag-v2/agents

cat <<PYTHON > src/libs/ShadowTag-v2/agents/recursive_rlm.py
"""
Recursive Language Model (RLM) Agent - Cloud Run Native Memory Edition
Features:
- Gemini 2.5 Flash Brain
- Dual-Layer Memory (Manual + Learned)
- Stateless Execution
"""
import os
import json
from typing import List, Dict
from google import genai
from google.genai import types

# Cloud Run Native Config
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "$PROJECT_ID")
LOCATION = "$REGION"
MODEL_ID = "$TARGET_MODEL"

class MemoryService:
    """Manages the agent's context and learned rules."""
    def __init__(self):
        self.styleguide_path = ".gemini/styleguide.md"
        self.learned_path = ".gemini/learned_memory.json"

    def get_context_block(self) -> str:
        """Retrieves and formats all memory for the prompt."""
        memory_block = "\\n--- 🧠 MEMORY & STANDARDS ---\\n"
        
        # 1. Load Manual Styleguide
        if os.path.exists(self.styleguide_path):
            with open(self.styleguide_path, "r") as f:
                memory_block += f"[MANUAL RULES]\\n{f.read()}\\n"
        
        # 2. Load Learned Memory
        if os.path.exists(self.learned_path):
            try:
                with open(self.learned_path, "r") as f:
                    rules = json.load(f)
                    memory_block += "[LEARNED RULES]\\n"
                    for r in rules:
                        memory_block += f"- {r['rule']} (Confidence: {r.get('weight', 0.5)})\\n"
            except:
                pass
                
        memory_block += "------------------------------\\n"
        return memory_block

class TextEnvironment:
    def __init__(self, file_path: str, chunk_size: int = 50000):
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
        self.memory = MemoryService()
        self.max_depth = 3

    def _call_gemini(self, prompt: str, context_chunk: str) -> str:
        # Inject Memory into every call
        memory_context = self.memory.get_context_block()
        full_prompt = f"{memory_context}\\n{prompt}\\n\\n--- DOC CHUNK ---\\n{context_chunk}\\n----------------"
        
        try:
            response = self.client.models.generate_content(
                model=MODEL_ID, 
                contents=full_prompt,
                config=types.GenerateContentConfig(temperature=0.0, max_output_tokens=100)
            )
            return response.text.strip()
        except Exception as e:
            return f"ANSWER Error: {str(e)}"

    def construct_system_prompt(self, query: str, current_pos: int, total_len: int, history: List[str]) -> str:
        return f"""
        GOAL: Answer "{query}"
        STATUS: Doc Size: {total_len}, Pos: {current_pos}
        HISTORY: {history[-3:]}
        
        INSTRUCTIONS:
        Use the MEMORY RULES above to guide your decision.
        
        COMMANDS:
        1. READ_NEXT
        2. JUMP <int>
        3. RECURSE <query>
        4. ANSWER <text>
        
        OUTPUT ONLY THE COMMAND.
        """

    def solve(self, query: str, env: TextEnvironment, start_index: int = 0, depth: int = 0) -> str:
        current_pos = start_index
        history = []
        steps = 0
        
        print(f"  ➤ [Depth {depth}] Agent with Memory active. Searching...")

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
# 3. CLOUD RUN NATIVE WEB SERVER (The Body)
# ------------------------------------------------------------------
echo ">>> 🏗️  Structuring Cloud Run Entrypoint..."
# Ensure we have a web server wrapper for the agent (FastAPI)
cat <<PYTHON > src/libs/ShadowTag-v2/main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from libs.ShadowTag-v2.agents.recursive_rlm import RecursiveAgent, TextEnvironment

app = FastAPI()
agent = RecursiveAgent()

class QueryRequest(BaseModel):
    query: str
    doc_content: str = "Dummy content for stateless demo..."

@app.get("/")
def health_check():
    return {"status": "ok", "model": "$TARGET_MODEL", "memory": "active"}

@app.post("/chat")
def chat(request: QueryRequest):
    # In a real Cloud Run Native app, doc_content would come from GCS or a DB
    # We save it temporarily to disk for the TextEnvironment to read (ephemeral)
    temp_path = "/tmp/request_doc.txt"
    with open(temp_path, "w") as f:
        f.write(request.doc_content)
    
    env = TextEnvironment(temp_path)
    answer = agent.solve(request.query, env)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
PYTHON

# ------------------------------------------------------------------
# 4. DEPLOYMENT (GitOps + Cloud Run)
# ------------------------------------------------------------------
echo ">>> 🚀 DEPLOYING CLOUD RUN NATIVE SERVICE..."

# A. Commit Memory & Code
git add .
git commit -m "feat: Cloud Run Native Memory Implant ($TARGET_MODEL)" || echo "Changes already staged."
git push origin main

# B. Force Deploy (Stateless)
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --allow-unauthenticated \
  --clear-base-image \
  --quiet

echo ">>> ✅ MEMORY IMPLANT COMPLETE."
echo ">>> Your agent now follows rules in .gemini/styleguide.md"
