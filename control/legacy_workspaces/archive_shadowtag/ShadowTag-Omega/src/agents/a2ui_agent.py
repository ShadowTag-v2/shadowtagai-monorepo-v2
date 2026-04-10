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
