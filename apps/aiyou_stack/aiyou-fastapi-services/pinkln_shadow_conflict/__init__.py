"""pinkln Agent Architecture System™
"Insanely Great AI Systems Through Elegant Orchestration"

A comprehensive framework for building Skills, Agents, Sub-Agents, Deep Agents,
and Multi-Agent systems inspired by the "Ultrathink like Steve Jobs" philosophy.

Core Philosophy:
- Question everything (start from zero)
- Obsess over details
- Plan like Da Vinci
- Craft, don't just code
- Iterate relentlessly
- Simplify ruthlessly
- Marry technology and liberal arts
- Activate the Reality Distortion Field
- Apply the Boy Scout Rule

Author: Erik Hancock (Founder, pinkln)
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Erik Hancock"

from .core.base_agent import BaseAgent
from .core.base_skill import BaseSkill
from .core.master_system import PnklnOS
from .core.validation import BoyScoutRule, ValidationLayer

# Export main components
__all__ = [
    "BaseAgent",
    "BaseSkill",
    "BoyScoutRule",
    "PnklnOS",
    "ValidationLayer",
]
