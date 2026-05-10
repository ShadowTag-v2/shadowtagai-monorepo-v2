# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from dataclasses import dataclass
from typing import Optional


@dataclass
class Token:
    """
    Base dataclass for a single generated token.
    """

    id: int
    text: str
    logprob: float
    from_draft: Optional[bool] = None
