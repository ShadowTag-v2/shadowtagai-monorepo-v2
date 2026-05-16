# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from pydantic import BaseModel, Field


class SupportedAsyncMethods(BaseModel):
    read: bool = Field(default=False)
    write: bool = Field(default=False)


class ProviderAsyncMethods(BaseModel):
    online: SupportedAsyncMethods = Field(default_factory=SupportedAsyncMethods)
