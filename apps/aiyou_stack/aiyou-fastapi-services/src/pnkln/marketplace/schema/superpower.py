from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Superpower(Base):
    """
    AI superpower listing

    A superpower is a packaged AI capability that users can purchase/subscribe to.
    Examples:
    - Advanced Math Tutor (AI tutor for calculus/algebra)
    - Focus Agent (workplace productivity enhancement)
    - Research Assistant (intelligence gathering and summarization)
    - Health Monitor (medical reminders and tracking)
    """

    __tablename__ = "marketplace_superpowers"
    id = Column(String(50), primary_key=True)
    developer_id = Column(String(50), ForeignKey("marketplace_developers.id"), nullable=False)
    name = Column(String(200), nullable=False)
    tagline = Column(String(500))
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(SuperpowerCategory), nullable=False)
    tags = Column(JSON, default=list)
    status = Column(SQLEnum(SuperpowerStatus), default=SuperpowerStatus.DRAFT)
    published_at = Column(DateTime)
    pricing_model = Column(SQLEnum(PricingModel), nullable=False)
    price = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")
    subscription_period = Column(String(20))
    usage_unit = Column(String(50))
    usage_price = Column(Numeric(10, 6))
    has_free_trial = Column(Boolean, default=False)
    trial_days = Column(Integer, default=7)
    free_tier_limit = Column(Integer)
    kernel_chain_id = Column(String(50))
    api_endpoint = Column(String(500))
    config = Column(JSON, default=dict)
    requires_api_key = Column(Boolean, default=False)
    min_credits = Column(Integer, default=0)
    icon_url = Column(String(500))
    screenshot_urls = Column(JSON, default=list)
    demo_video_url = Column(String(500))
    total_installs = Column(Integer, default=0)
    active_installs = Column(Integer, default=0)
    total_revenue = Column(Numeric(10, 2), default=0)
    avg_rating = Column(Float, default=0)
    total_ratings = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    featured_until = Column(DateTime)
    featured_fee_paid = Column(Numeric(10, 2))
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    developer = relationship("Developer", back_populates="superpowers")
    transactions = relationship("Transaction", back_populates="superpower")
    __table_args__ = (
        Index("idx_marketplace_superpowers_developer", "developer_id"),
        Index("idx_marketplace_superpowers_status", "status"),
        Index("idx_marketplace_superpowers_category", "category"),
        Index("idx_marketplace_superpowers_featured", "is_featured"),
        Index("idx_marketplace_superpowers_published", "published_at"),
    )
