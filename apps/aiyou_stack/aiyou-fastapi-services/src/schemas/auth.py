# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class AuthUserCreate(BaseModel):
    email: EmailStr
    password: str


class AuthUserResponse(BaseModel):
    id: UUID | Any
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
