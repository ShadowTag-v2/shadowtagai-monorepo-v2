import json
import os

import vertexai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vertexai.generative_models import GenerationConfig, GenerativeModel

app = FastAPI()

# Initialize Vertex AI
PROJECT_ID = os.environ.get("PROJECT_ID")
vertexai.init(project=PROJECT_ID, location="us-central1")


class ReviewRequest(BaseModel):
    original_code: str
    error_log: str
    proposed_fix: str


@app.post("/review")
async def review_fix(request: ReviewRequest):
    model = GenerativeModel("gemini-1.5-pro-001")

    prompt = f"""
    You are a Senior Principal Software Engineer. Review this code fix.

    ORIGINAL CODE:
    {request.original_code}

    ERROR ENCOUNTERED:
    {request.error_log}

    PROPOSED FIX:
    {request.proposed_fix}

    Analyze the fix for:
    1. Correctness (Does it actually fix the error?)
    2. Safety (Does it introduce security risks?)
    3. Style (Does it follow best practices?)

    Return JSON only: {{ "approved": boolean, "reason": "string" }}
    """

    try:
        response = model.generate_content(
            prompt, generation_config=GenerationConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
