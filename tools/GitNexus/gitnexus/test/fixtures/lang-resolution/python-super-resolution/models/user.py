# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from .base import BaseModel


class User(BaseModel):
    def save(self) -> bool:
        super().save()
        return True
