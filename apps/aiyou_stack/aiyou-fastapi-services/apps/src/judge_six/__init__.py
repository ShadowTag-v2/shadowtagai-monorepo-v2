"""
Judge #6 - ATP 5-19 Compliance & Enforcement Engine
PNKLN Core Stack™ - Enforcement Layer

This module implements the Purpose/Reasons/Brakes (JR Engine) validation framework
for automated policy enforcement and compliance checking.
"""

__version__ = "1.0.0"
__author__ = "PNKLN Core Team"

from .jr_engine import JREngine, JRVerdict
from .validators import BrakesValidator, PurposeValidator, ReasonsValidator

__all__ = [
    "JREngine",
    "JRVerdict",
    "PurposeValidator",
    "ReasonsValidator",
    "BrakesValidator",
]
