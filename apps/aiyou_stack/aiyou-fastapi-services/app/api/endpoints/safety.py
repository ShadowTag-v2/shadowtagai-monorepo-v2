"""Safety & Compliance API endpoints"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class ModerateContentRequest(BaseModel):
    content: str
    content_type: str = "text"
    check_pii: bool = True
    check_toxicity: bool = True


class ModerateMediaRequest(BaseModel):
    media_url: str
    media_type: str = "image"


@router.post("/moderate/content")
async def moderate_content(request: ModerateContentRequest, req: Request):
    """Moderate content for safety and compliance"""
    safety = req.app.state.safety

    if not safety:
        raise HTTPException(status_code=503, detail="Safety service not initialized")

    result = await safety.moderate_content(
        content=request.content,
        content_type=request.content_type,
        check_pii=request.check_pii,
        check_toxicity=request.check_toxicity,
    )

    return result


@router.post("/moderate/media")
async def moderate_media(request: ModerateMediaRequest, req: Request):
    """Moderate media content"""
    safety = req.app.state.safety

    if not safety:
        raise HTTPException(status_code=503, detail="Safety service not initialized")

    result = await safety.moderate_media(media_url=request.media_url, media_type=request.media_type)

    return result


@router.get("/stats")
async def get_moderation_stats(req: Request):
    """Get moderation statistics"""
    safety = req.app.state.safety

    if not safety:
        raise HTTPException(status_code=503, detail="Safety service not initialized")

    stats = await safety.get_moderation_stats()
    return stats
