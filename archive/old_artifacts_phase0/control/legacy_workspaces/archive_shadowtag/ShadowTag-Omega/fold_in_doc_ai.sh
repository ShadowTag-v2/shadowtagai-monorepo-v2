#!/bin/bash
set -e
# ==============================================================================
# 👁️ TEGU VISION v2: AGENTIC DOCUMENT EXTRACTION
# ==============================================================================
# Methodology: DeepLearning.AI "Document AI" (Layout -> Anchors -> Extraction)
# REPLACES: libs/arsenal/tegu_vision/
# UPDATES: GEMINI.md (New /scan protocols)
# ==============================================================================
echo ">>> 👁️ FOLDING IN 'DOCUMENT AI' METHODOLOGY..."

# ==============================================================================
# 1. THE VISUAL PROMPTS (The "Course Wisdom")
# ==============================================================================
mkdir -p libs/arsenal/tegu_vision
cat <<PYTHON > libs/arsenal/tegu_vision/prompts.py
"""
TEGU VISION PROTOCOLS
Derived from 'Agentic Doc Extraction' Principles.
"""

LAYOUT_ANALYSIS_PROMPT = \"\"\"
PHASE 1: VISUAL SCOUTING
Do not extract data yet. Analyze the document structure:
1. **Layout**: Is it a column-based form? A grid? A mixed layout?
2. **Anchors**: Identify the key visual anchors (e.g., "TOTAL", "INVOICE #", "SHIPPING ADDRESS").
3. **Regions**: Define the bounding box logic for where the values likely reside relative to the anchors.

Output your reasoning briefly.
\"\"\"

EXTRACTION_PROMPT = \"\"\"
PHASE 2: SURGICAL EXTRACTION
Based on the layout analysis, extract the target data.
- If a Table is present, maintain row alignment.
- If data is handwritten, flag it as 'confidence: low'.
- Return strictly valid JSON.
\"\"\"
PYTHON

# ==============================================================================
# 2. THE AGENT (Block 13: The Reasoner)
# ==============================================================================
cat <<PYTHON > libs/arsenal/tegu_vision/agent.py
import json
from google import genai
from google.genai import types
from .prompts import LAYOUT_ANALYSIS_PROMPT, EXTRACTION_PROMPT

class AgenticDocExtractor:
    """
    Implements the 'OCR to Agentic' pipeline.
    Uses Gemini 2.0/3.0 to 'Reason' about layout before 'Reading' text.
    """
    def __init__(self):
        self.client = genai.Client(vertexai=True, location="us-central1")
        # Flash is sufficient for Layout Analysis; Pro for dense extraction
        self.model = "gemini-2.0-flash-exp"

    def scan(self, file_path: str, user_intent: str):
        print(f"👁️  TEGU: Loading Visual Context from {file_path}...")

        # 1. Ingest Visual Data (Multimodal)
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        doc_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

        # 2. The Agentic Chain (Reasoning + Extraction)
        full_prompt = f"""
        USER GOAL: {user_intent}

        {LAYOUT_ANALYSIS_PROMPT}

        {EXTRACTION_PROMPT}
        """

        print("🧠 TEGU: Reasoning about Layout & Anchors...")
        response = self.client.models.generate_content(
            model=self.model,
            contents=[doc_part, full_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2 # Low temp for precision
            )
        )

        return json.loads(response.text)

vision_agent = AgenticDocExtractor()
PYTHON

# ==============================================================================
# 3. THE CONTEXT (Block 1: Gemini CLI Upgrade)
# ==============================================================================
cat <<MARKDOWN > GEMINI.md
# PROJECT: SHADOWTAG OMEGA (AGENTIC VISION)

## 🛡️ MISSION
You are the Sovereign Operator.
1. **Safety:** Adhere to 6-Gate Risk Protocol.
2. **Visual:** Use Agentic Vision for documents. Do not use simple OCR.

## 👁️ VISUAL PROTOCOLS (TEGU)
When the user provides a document (PDF/Image):
1. **Do not** just read the text.
2. **Reason** about the layout (Tables, Forms, Signatures).
3. **Trigger** \`/scan\` to use the `tegu_vision` library.

## ⚡ SLASH COMMANDS
- \`/risk [code]\`: Assess code safety.
- \`/ui [intent]\`: Generate A2UI interface.
- \`/scan [file] [intent]\`: Run Agentic Extraction.
  * *Example:* \`/scan invoice.pdf "Extract the table items and the final total"\`
MARKDOWN

# ==============================================================================
# 4. THE INTERFACE (Block 15: DropZone Connection)
# ==============================================================================
cat <<PYTHON > src/agents/a2ui_agent.py
from libs.arsenal.tegu_vision.agent import vision_agent

class A2UIAgent:
    def generate(self, intent):
        # VISUAL INTENT DETECTED
        if any(w in intent.lower() for w in ["scan", "extract", "invoice", "receipt"]):
            return {
                "root_id": "vision_dash",
                "components": [
                    {"id": "vision_dash", "type": "Column", "children": ["header", "drop_zone", "instruction"]},
                    {"id": "header", "type": "Text", "props": {"text": "Agentic Document Extraction", "size": "h2"}},
                    {"id": "instruction", "type": "Text", "props": {"text": "Upload document to analyze Layout & Extract Data."}},
                    {"id": "drop_zone", "type": "DropZone", "props": {"action": "/scan", "label": "Drop PDF/Image Here"}}
                ]
            }

        # FALLBACK: Standard Dashboard
        return {
            "root_id": "main",
            "components": [
                {"id": "main", "type": "Column", "children": ["header", "btn"]},
                {"id": "header", "type": "Text", "props": {"text": f"Ready: {intent}", "size": "h1"}},
                {"id": "btn", "type": "Button", "props": {"label": "EXECUTE", "action": "run"}}
            ]
        }
PYTHON

echo ">>> ✅ TEGU VISION UPGRADED: AGENTIC EXTRACTION ENABLED."
echo ">>> Theory: Layout Analysis -> Visual Anchoring -> Structured JSON."
