#!/bin/bash
set -e

# --- CONFIGURATION ---
PROJECT_ID="acquired-jet-478701-b3"
REGION="us-central1"
SERVICE_NAME="beads-agent-server"
TARGET_MODEL="gemini-2.5-flash" 

echo ">>> 📿 INITIATING BEADS MEGA-IMPLANT (Active State + A2UI)..."

# ------------------------------------------------------------------
# 1. SETUP BEADS STORAGE (The Durable Context)
# ------------------------------------------------------------------
echo ">>> 📂 Creating Beads Structure..."
mkdir -p .beads

# BEAD 00: ARCHITECTURE (The "Hard Constraints")
cat <<MARKDOWN > .beads/00_architecture.md
# SYSTEM ARCHITECTURE
- **Compute:** Cloud Run (Stateless, Ephemeral).
- **Memory:** Repo-backed (.beads folder).
- **Lang:** Python 3.13+ with strict typing.
- **Port:** Listen on env var \$PORT.
MARKDOWN

# BEAD 01: CONVENTIONS (The "Style Guide")
cat <<MARKDOWN > .beads/01_conventions.md
# CODING CONVENTIONS
- **Imports:** Group standard libs, then 3rd party, then local.
- **Logging:** Use structured JSON logging only.
- **Error Handling:** Fail fast, no silent catches.
MARKDOWN

# BEAD 05: UI SPECS (The "Face" - A2UI)
cat <<MARKDOWN > .beads/05_ui_specs.md
# A2UI CAPABILITIES
The agent can output JSON to render UI components on the client.
- **\`Panel\`**: Container for layout.
- **\`Form\`**: Input fields (text, upload, select).
- **\`Chart\`**: Visual data summary (bar, line, pie).
- **\`Map\`**: Google Map integration for location data.

## Output Format (JSON)
\`\`\`json
{
  "component": "Panel",
  "children": [
    { "component": "Chart", "data": {...} },
    { "component": "Form", "fields": [...] }
  ]
}
\`\`\`
MARKDOWN

# BEAD 50: ACTIVE WORK (The "Issue Tracker")
cat <<JSON > .beads/50_active_work.json
{
  "project_status": "active",
  "current_sprint": "Sprint 4: Visual Polish",
  "issues": [
    {
      "id": "Y-444",
      "title": "Fix Map Rendering Flicker",
      "status": "in_progress",
      "priority": "P0",
      "context": "Map flickers when player moves west. Screenshot 'error_flicker.png' confirms.",
      "dependencies": []
    }
  ],
  "session_history": []
}
JSON

# BEAD 99: DYNAMIC STATE (The "Learned Memory")
cat <<JSON > .beads/99_learned.json
[
  {
    "rule": "Do not line-wrap import statements.",
    "source": "CodeReview-102",
    "weight": 1.0
  },
  {
    "rule": "Always use A2UI 'Panel' summary when landing the plane.",
    "source": "User-Preference",
    "weight": 2.0
  }
]
JSON

# ------------------------------------------------------------------
# 2. UPGRADE AGENT BRAIN (Beads-Aware + A2UI + Land Plane)
# ------------------------------------------------------------------
echo ">>> 🧬 Rewriting Agent to Thread Beads..."
mkdir -p src/libs/ShadowTag-v2/agents

cat <<PYTHON > src/libs/ShadowTag-v2/agents/beads_agent.py
"""
Beads-Native Agent - Cloud Run Edition
Features:
- Dynamically threads context from .beads/ directory
- Separates Architecture, Style, Active State, and Learned Memory
- Supports 'Land the Plane' protocol and A2UI Rendering
"""
import os
import json
import glob
from typing import List, Union, Dict
from google import genai
from google.genai import types

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "$PROJECT_ID")
LOCATION = "$REGION"
MODEL_ID = "$TARGET_MODEL"

class BeadsService:
    """Manages the agent's durable context beads."""
    def __init__(self):
        self.beads_dir = ".beads"

    def get_context_chain(self) -> str:
        """Threads all beads into a single context string."""
        chain = "\\n--- 📿 DURABLE MEMORY (BEADS) ---\\n"
        
        # 1. Thread Markdown Beads (Static Context)
        md_beads = sorted(glob.glob(os.path.join(self.beads_dir, "*.md")))
        for bead_path in md_beads:
            bead_name = os.path.basename(bead_path).replace(".md", "").upper()
            with open(bead_path, "r") as f:
                chain += f"[{bead_name}]\\n{f.read()}\\n"

        # 2. Thread JSON Beads (Active Work + Learned)
        json_beads = sorted(glob.glob(os.path.join(self.beads_dir, "*.json")))
        for bead_path in json_beads:
            bead_name = os.path.basename(bead_path).replace(".json", "").upper()
            try:
                with open(bead_path, "r") as f:
                    data = json.load(f)
                    chain += f"[{bead_name}]\\n{json.dumps(data, indent=2)}\\n"
            except:
                pass
                
        chain += "------------------------------------\\n"
        return chain

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

class BeadsAgent:
    def __init__(self):
        self.client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        self.memory = BeadsService()

    def land_the_plane(self, issue_id: str, summary: str, status: str = "closed"):
        """
        The Agent calls this to finish a session.
        It updates the .beads/50_active_work.json file and commits it.
        """
        bead_path = ".beads/50_active_work.json"
        
        # 1. Load the Active Bead
        if not os.path.exists(bead_path):
             return "Error: Active Bead not found."

        with open(bead_path, "r") as f:
            data = json.load(f)
            
        # 2. Update the Issue
        found = False
        for issue in data.get("issues", []):
            if issue["id"] == issue_id:
                issue["status"] = status
                issue["resolution_summary"] = summary
                found = True
                break
        
        if not found:
            return f"Error: Issue {issue_id} not found in Beads."

        # 3. Add Session Log
        data.setdefault("session_history", []).append({
            "timestamp": "Now", # In real code, use datetime
            "action": "landed_plane",
            "summary": summary
        })

        # 4. Save and Commit (The "Memory Implant")
        with open(bead_path, "w") as f:
            json.dump(data, f, indent=2)
            
        # 5. Git Commit (Simulated for Demo)
        # os.system(f'git add {bead_path} && git commit -m "agent: Landed plane for {issue_id}"')
        
        return "Plane Landed. Memory Updated."

    def solve(self, query: str, env: TextEnvironment) -> Union[str, Dict]:
        memory_context = self.memory.get_context_chain()
        doc_chunk = env.read(0) 
        
        system_prompt = f\"\"\"
        {memory_context}
        GOAL: {query}
        
        OUTPUT RULES:
        1. If you fixed an issue, Output "LAND_THE_PLANE: <issue_id> <summary>"
        2. If the user asks for data visualization, output A2UI JSON.
        3. If the user asks for action, use the 'Form' component.
        4. Otherwise, answer in text.
        
        --- DOC CHUNK ---\\n{doc_chunk}\\n----------------
        \"\"\"
        
        try:
            response = self.client.models.generate_content(
                model=MODEL_ID, 
                contents=system_prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            response_text = response.text.strip()
            
            # Logic: Land the Plane
            if response_text.startswith("LAND_THE_PLANE"):
                parts = response_text.split(" ", 2)
                if len(parts) >= 3:
                     issue_id = parts[1]
                     summary = parts[2]
                     result = self.land_the_plane(issue_id, summary)
                     # Return A2UI Summary
                     return {
                        "type": "a2ui_render",
                        "payload": {
                            "component": "Panel",
                            "title": f"Plane Landed: {issue_id}",
                            "children": [
                                {"component": "Chart", "title": "Status", "data": {"status": "closed"}},
                                {"component": "Form", "fields": [{"label": "Summary", "value": summary, "readonly": True}]}
                            ]
                        }
                     }

            # A2UI Detection
            if response_text.startswith('{') and '"component":' in response_text:
                try:
                    return {
                        "type": "a2ui_render", 
                        "payload": json.loads(response_text)
                    }
                except json.JSONDecodeError:
                    pass
            
            return {"type": "text", "payload": response_text}

        except Exception as e:
            return {"type": "error", "payload": str(e)}
PYTHON

# ------------------------------------------------------------------
# 3. CLOUD RUN SERVER (Updated for A2UI)
# ------------------------------------------------------------------
echo ">>> 🏗️  Structuring Server..."
cat <<PYTHON > src/libs/ShadowTag-v2/main.py
import os
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union, Dict
from libs.ShadowTag-v2.agents.beads_agent import BeadsAgent, TextEnvironment

app = FastAPI()
agent = BeadsAgent()

class QueryRequest(BaseModel):
    query: str
    doc_content: str = "Demo content..."

@app.post("/chat")
def chat(request: QueryRequest):
    temp_path = "/tmp/request_doc.txt"
    with open(temp_path, "w") as f:
        f.write(request.doc_content)
    
    env = TextEnvironment(temp_path)
    # Result is now a Dict (A2UI) or String
    answer = agent.solve(request.query, env)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
PYTHON

echo ">>> ✅ MEGA-IMPLANT COMPLETE."
