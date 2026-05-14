# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from pydantic import BaseModel


class MediaAsset(BaseModel):
    uri: str
    error: str | None = None
