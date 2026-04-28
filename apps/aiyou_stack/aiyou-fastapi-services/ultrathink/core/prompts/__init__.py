# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prompting primitives: RTF, TAG, BAB, CARE, RISE.

These are the building blocks of structured AI prompting.
Each technique serves a specific purpose and composes beautifully.
"""

from ultrathink.core.prompts.bab import BAB
from ultrathink.core.prompts.base import BasePrompt
from ultrathink.core.prompts.care import CARE
from ultrathink.core.prompts.rise import RISE
from ultrathink.core.prompts.rtf import RTF
from ultrathink.core.prompts.tag import TAG

__all__ = ["BAB", "CARE", "RISE", "RTF", "TAG", "BasePrompt"]
