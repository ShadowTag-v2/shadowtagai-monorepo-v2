# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from policy_engine.objection.service import ObjectionEngine
from shared.types import PolicyDecision

router = APIRouter(prefix="/objection", tags=["Gate1_Semantic_Objection"])
engine = ObjectionEngine()


class EvalRequest(BaseModel):
    pr_title: str
    diff_text: str
    changed_files: list[str]


@router.post("/evaluate", response_model=PolicyDecision)
async def evaluate_diff_endpoint(req: EvalRequest):
    try:
        decision = engine.evaluate_diff(req.pr_title, req.diff_text, req.changed_files)
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
