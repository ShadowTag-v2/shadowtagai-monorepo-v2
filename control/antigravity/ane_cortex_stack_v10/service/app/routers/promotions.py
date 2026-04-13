from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any
from ..config import load_settings
from ..adapters.authority_promotions import propose_promotion, approve_and_apply

router = APIRouter(prefix="/api")


class PromotionRequest(BaseModel):
    promotion_kind: str
    subject: str
    payload: dict[str, Any]
    proposed_by: str = "assistant"


@router.post("/promotions/propose")
def propose(req: PromotionRequest):
    s = load_settings()
    pid = propose_promotion(
        s.postgres_dsn, s.repo_id, req.promotion_kind, req.subject, req.payload, req.proposed_by
    )
    return {"promotion_id": pid, "status": "proposed"}


class PromotionApplyRequest(BaseModel):
    promotion_id: str


@router.post("/promotions/apply")
def apply(req: PromotionApplyRequest):
    s = load_settings()
    return approve_and_apply(s.postgres_dsn, s.repo_id, req.promotion_id, s.authority_state_path)
