import os

import vertexai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from vertexai.generative_models import GenerativeModel, Part

# --- Configuration ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
LOCATION = "us-central1"
MODEL_ID = "gemini-1.5-pro-001"

# --- Initialize Vertex AI and FastAPI ---
vertexai.init(project=PROJECT_ID, location=LOCATION)

app = FastAPI(
    title="Fixer Agent",
    description="An AI agent that generates code fixes based on an error message.",
    version="1.0.0",
)


class FixRequest(BaseModel):
    original_code: str
    error_message: str
    rejection_reason: str | None = Field(
        None, description="Feedback from the Reviewer on a previous failed attempt.",
    )


class FixResponse(BaseModel):
    proposed_fix: str


@app.post("/", response_model=FixResponse)
async def create_code_fix(request: FixRequest):
    """Receives a code problem and uses Gemini to generate a fix.
    If a rejection_reason is provided, it incorporates the feedback.
    """
    try:
        model = GenerativeModel(MODEL_ID)

        # Build the prompt dynamically based on whether this is a retry
        retry_context = ""
        if request.rejection_reason:
            retry_context = f"""
            Your previous attempt was rejected by the code reviewer for the following reason: '{request.rejection_reason}'.
            You MUST generate a new, improved fix that directly addresses this feedback.
            """

        prompt = f"""
        You are an expert software engineer. Your task is to fix the bug in the provided code.
        Respond ONLY with the complete, corrected code block. Do not add any explanation, comments, or surrounding text.
        {retry_context}

        **Error Message:**
        "{request.error_message}"

        **Original Code:**
        ```
        {request.original_code}
        ```
        """

        response = model.generate_content([Part.from_text(prompt)])

        # Clean up the response to ensure it's just the code block
        proposed_fix_text = response.text.strip().replace("```", "").strip()

        return FixResponse(proposed_fix=proposed_fix_text)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred in the Fixer Agent: {e!s}",
        )
