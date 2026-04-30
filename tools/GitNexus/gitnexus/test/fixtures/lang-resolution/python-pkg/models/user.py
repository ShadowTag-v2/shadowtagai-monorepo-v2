# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from .base import BaseModel


class User(BaseModel):
    def get_name(self):
        return self.name
