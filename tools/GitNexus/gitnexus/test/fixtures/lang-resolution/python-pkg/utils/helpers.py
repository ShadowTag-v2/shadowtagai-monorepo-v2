# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from ..models.base import BaseModel


def process_model(model: BaseModel):
    model.validate()
    model.save()
