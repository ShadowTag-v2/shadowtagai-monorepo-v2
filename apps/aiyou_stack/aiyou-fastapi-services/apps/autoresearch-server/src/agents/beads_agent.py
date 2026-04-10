"""
Beads-Native Agent - A2UI/AGUI Edition
Features:
- Threaded Context (Beads)
- A2UI JSON Generation (Generative UI)
- AGUI State Protocol
"""
import os
import json
import glob
from typing import Dict, Any
from google import genai
from google.genai import types

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "shadowtag-omega-v2")
LOCATION = "us-central1"
MODEL_ID = "gemini-2.5-flash"

class BeadsService:
    """Manages the agent's durable context beads."""
    def __init__(self):
        self.beads_dir = os.path.abspath(".beads")

    def get_context_chain(self) -> str:
        """Threads all beads into a single context string."""
        chain = "\n--- 📿 DURABLE MEMORY (BEADS) ---\n"
        
        if os.path.exists(self.beads_dir):
            md_beads = sorted(glob.glob(os.path.join(self.beads_dir, "*.md")))
            for bead_path in md_beads:
                bead_name = os.path.basename(bead_path).replace(".md", "").upper()
                with open(bead_path, "r") as f:
                    chain += f"[{bead_name}]\n{f.read()}\n"

            json_beads = sorted(glob.glob(os.path.join(self.beads_dir, "*.json")))
            for bead_path in json_beads:
                try:
                    with open(bead_path, "r") as f:
                        data = json.load(f)
                        chain += f"[LEARNED RULES]\n"
                        for item in data:
                             chain += f"- {item.get('rule', 'Unknown')} (Weight: {item.get('weight', 0.5)})\n"
                except:
                    pass
        else:
             chain += "[WARNING] Beads directory not found.\n"
                
        chain += "------------------------------------\n"
        return chain

class BeadsAgent:
    def __init__(self):
        self.client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
        self.memory = BeadsService()

    def solve(self, query: str, context_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solves using AGUI Protocol (State In -> Action -> State Out)
        """
        memory_context = self.memory.get_context_chain()
        state_dump = json.dumps(context_state) if context_state else "{}"
        
        system_prompt = f\"\"\"
        {memory_context}
        
        CURRENT STATE (AGUI): {state_dump}
        USER QUERY: {query}
        
        OUTPUT INSTRUCTIONS:
        1. Analyze user intent.
        2. If UI is needed, generate A2UI JSON using 'PhotoUpload', 'GoogleMap', 'DynamicForm'.
        3. If just text, return text.
        4. Maintain strictly valid JSON format for UI.
        \"\"\"
        
        try:
            response = self.client.models.generate_content(
                model=MODEL_ID, 
                contents=system_prompt,
                config=types.GenerateContentConfig(temperature=0.0)
            )
            response_text = response.text.strip()
            
            # AGUI Protocol: Detect A2UI Payload
            if response_text.startswith('{') and '"component":' in response_text:
                try:
                    ui_payload = json.loads(response_text)
                    return {
                        "type": "a2ui_render", 
                        "payload": ui_payload,
                        "shared_state": context_state # Echo state back or update it
                    }
                except json.JSONDecodeError:
                    pass # Fallthrough to text
            
            return {
                "type": "text", 
                "payload": response_text,
                "shared_state": context_state
            }

        except Exception as e:
            return {"type": "error", "payload": str(e)}
