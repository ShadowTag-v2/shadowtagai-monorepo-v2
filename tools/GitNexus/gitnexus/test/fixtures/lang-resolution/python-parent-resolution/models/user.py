# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from .base import BaseModel


class User(BaseModel):
    def serialize(self) -> str:
        return ""
