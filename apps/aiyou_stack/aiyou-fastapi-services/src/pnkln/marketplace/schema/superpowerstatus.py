from enum import StrEnum

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SuperpowerStatus(StrEnum):
    """Superpower lifecycle status"""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    SUSPENDED = "suspended"
    DEPRECATED = "deprecated"
