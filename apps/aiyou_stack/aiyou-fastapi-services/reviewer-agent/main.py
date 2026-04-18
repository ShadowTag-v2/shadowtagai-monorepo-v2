import os

import vertexai
import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vertexai.generative_models import GenerativeModel, Part

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = "us-central1"
MODEL_ID = "gemini-3.1-flash-lite-preview"

# --- Load Constitution ---
CONSTITUTION_TEXT = ""
try:
    with open("constitution.yaml") as f:
        constitution_data = yaml.safe_load(f)
        CONSTITUTION_TEXT = yaml.dump(constitution_data["principles"])
except FileNotFoundError:
    print("WARNING: constitution.yaml not found. Running without a constitution.")
except Exception as e:
    print(f"WARNING: Error loading constitution.yaml: {e}")

# --- Initialize Vertex AI and FastAPI ---
vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI(
    title="Constitutional Reviewer Agent",
    description="An AI agent that reviews code fixes based on a strict constitution.",
    version="1.1.0",
)


class ReviewRequest(BaseModel):
    original_code: str
    error_message: str
    proposed_fix: str


@app.post("/")
async def review_code_fix(request: ReviewRequest):
    """Receives a proposed code fix and uses Gemini to approve or reject it
    based on a predefined constitution.
    """
    try:
        model = GenerativeModel(MODEL_ID)

        prompt = f"""
        You are a senior software engineer acting as a meticulous code reviewer.
        Your task is to analyze the proposed fix based on the following constitution. Your judgment MUST adhere strictly to these principles.

        **Constitution:**
        ```yaml
        {CONSTITUTION_TEXT}
        ```

        In your response, you must only provide a valid JSON object with two keys: 'approved' (boolean) and 'reason' (string).
        If you reject the fix ('approved': false), the 'reason' MUST start with the ID of the principle that was violated (e.g., "MAINTAINABILITY: The proposed fix uses a complex regular expression that is hard to read...").

        **Original Code:**
        ```
        {request.original_code}
        ```

        **Error Message:**
        "{request.error_message}"

        **Proposed Fix:**
        ```
        {request.proposed_fix}
        ```
        """

        response = model.generate_content(
            [Part.from_text(prompt)],
            generation_config={"response_mime_type": "application/json"},
        )

        return response.text

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred in the Reviewer Agent: {e!s}",
        )
