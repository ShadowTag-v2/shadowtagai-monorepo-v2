# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def managers():
    return {"status": "active"}
