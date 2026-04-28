# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import StrEnum

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SuperpowerCategory(StrEnum):
    """Superpower categories"""

    AI_TUTOR = "ai_tutor"
    PRODUCTIVITY = "productivity"
    ANALYSIS = "analysis"
    AUTOMATION = "automation"
    CREATIVITY = "creativity"
    RESEARCH = "research"
    COMMUNICATION = "communication"
    DATA = "data"
    HEALTH = "health"
    OTHER = "other"
