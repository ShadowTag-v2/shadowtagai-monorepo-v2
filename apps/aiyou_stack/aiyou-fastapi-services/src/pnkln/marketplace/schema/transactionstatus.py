# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

from enum import StrEnum

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TransactionStatus(StrEnum):
    """Transaction lifecycle"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    DISPUTED = "disputed"
