import os

import vertexai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview import generative_models

# Initialize FastAPI
app = FastAPI(title="ShadowTag Vision Refinery (Native)")

# Initialize Vertex AI
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    # Using Gemini 1.5 Flash for high speed/low cost
    model = GenerativeModel("gemini-3.1-flash-lite-preview-001")
else:
    print("⚠️ PROJECT_ID not set. Vertex AI init skipped (Mock Mode).")
    model = None


class DocumentRequest(BaseModel):
    gcs_uri: str
    prompt: str = "Extract all text and structured data from this document."


@app.post("/parse")
async def parse_document(request: DocumentRequest):
    if not model:
        return {"status": "mock", "text": "Mock Result: Vertex AI not initialized."}

    try:
        # Load Image from GCS
        image_part = Part.from_uri(request.gcs_uri, mime_type="image/jpeg")

        # Generate Content
        responses = model.generate_content(
            [image_part, request.prompt],
            generation_config=generative_models.GenerationConfig(
                max_output_tokens=2048,
                temperature=0.2,
                top_p=1.0,
                top_k=32,
            ),
            stream=False,
        )

        return {"status": "success", "text": responses.text, "usage": str(responses.usage_metadata)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "alive", "engine": "Vertex AI (Gemini 1.5 Flash)"}
