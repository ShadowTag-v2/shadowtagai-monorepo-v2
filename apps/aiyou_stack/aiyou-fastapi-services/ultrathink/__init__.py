"""
Ultrathink Framework

An insanely elegant AI prompting and multi-agent framework.

"Simple can be harder than complex... but it's worth it,
because once you get there, you can move mountains." — Steve Jobs
"""

__version__ = "0.1.0"
__author__ = "ShadowTag-v4 Team"

from ultrathink.core.prompts import BAB, CARE, RISE, RTF, TAG
from ultrathink.core.reasoning import RCR, CoT, ToT

__all__ = [
    "RTF",
    "TAG",
    "BAB",
    "CARE",
    "RISE",
    "CoT",
    "ToT",
    "RCR",
]
