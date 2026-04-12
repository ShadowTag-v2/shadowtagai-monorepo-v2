# 03_main.py
# Save in src/brain/

import glob
import os
import uuid

from fastapi import FastAPI
from google.cloud import firestore
from pydantic import BaseModel

app = FastAPI()
db = firestore.Client()


# --- MEMORY SYSTEM (Beads) ---
def get_static_memory():
    mem = "\n--- 📿 STATIC MEMORY ---\n"
    # Reads Markdown files from the container
    for f in sorted(glob.glob(".beads/*.md")):
        with open(f) as file:
            mem += f"[{os.path.basename(f)}]\n{file.read()}\n"
    return mem


# --- INTERFACE (A2UI) ---
class ChatRequest(BaseModel):
    query: str


@app.post("/chat")
def chat(r: ChatRequest):
    # 1. Access Memory
    get_static_memory()

    # 2. Heuristic: Do we need the browser?
    needs_browsing = "browse" in r.query.lower() or "check" in r.query.lower()
    task_id = str(uuid.uuid4())[:8]

    if needs_browsing:
        # 3. DISPATCH TO HANDS (Firestore Queue)
        db.collection("agent_queue").document(task_id).set(
            {"status": "queued", "goal": r.query, "created_at": firestore.SERVER_TIMESTAMP}
        )

        # 4. RETURN OPTIMISTIC UI
        return {
            "type": "a2ui_render",
            "payload": {
                "component": "Panel",
                "title": "ShadowTag Activated",
                "children": [
                    {
                        "component": "StatusBadge",
                        "status": "processing",
                        "label": f"Task {task_id} sent to Workstation",
                    },
                    {"component": "Markdown", "content": "I am browsing the web now."},
                ],
            },
        }

    return {"type": "text", "payload": "I can answer this directly using my static memory beads."}
