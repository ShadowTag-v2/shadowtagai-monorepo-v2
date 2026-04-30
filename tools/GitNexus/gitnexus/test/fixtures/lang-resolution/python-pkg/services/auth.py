# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from ..models.user import User


class AuthService:
    def authenticate(self, user: User):
        user.validate()
        return True
