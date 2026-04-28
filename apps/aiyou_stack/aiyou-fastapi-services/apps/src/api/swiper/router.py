# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def swiper_root():
    return {
        "platform": "Swiper (Craigslist Challenger)",
        "status": "Isolated from Amazon Challenger",
    }
