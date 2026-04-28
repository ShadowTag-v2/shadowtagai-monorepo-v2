# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import StrEnum

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PricingModel(StrEnum):
    """Pricing models"""

    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    FREEMIUM = "freemium"
