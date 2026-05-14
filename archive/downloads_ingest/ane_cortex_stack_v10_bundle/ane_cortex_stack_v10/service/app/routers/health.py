# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from fastapi import APIRouter
router = APIRouter()

@router.get("/health")
def health():
    return {"ok": True, "service": "ane-cortex-stack-v3"}
