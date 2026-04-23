from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .service import GroundedGenerationService

router = APIRouter(prefix="/grounded-generation", tags=["grounded-generation"])


# Dependency to get service instance
def get_service():
    return GroundedGenerationService()


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The user prompt to generate content for.")
    model_id: str = Field("gemini-3.1-flash-lite-preview", description="The model ID to use.")


class Citation(BaseModel):
    search_entry_point: str | None = None


class GenerateResponse(BaseModel):
    text: str
    citations: list[Citation]
    raw_response: str | None = None


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    service: GroundedGenerationService = Depends(get_service),
):
    """Generate content grounded in Google Search."""
    try:
        result = await service.generate(request.prompt, request.model_id)
        return GenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
