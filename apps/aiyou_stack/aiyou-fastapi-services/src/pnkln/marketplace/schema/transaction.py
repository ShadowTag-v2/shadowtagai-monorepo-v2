from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .transactionstatus import TransactionStatus

Base = declarative_base()


class Transaction(Base):
    """Marketplace transaction (purchase/subscription)

    Platform fee: 20-30% of transaction amount
    Developer receives: 70-80% of transaction amount
    """

    __tablename__ = "marketplace_transactions"
    id = Column(String(50), primary_key=True)
    buyer_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    developer_id = Column(String(50), ForeignKey("marketplace_developers.id"), nullable=False)
    superpower_id = Column(String(50), ForeignKey("marketplace_superpowers.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    total_amount = Column(Numeric(10, 2), nullable=False)
    platform_fee = Column(Numeric(10, 2), nullable=False)
    developer_share = Column(Numeric(10, 2), nullable=False)
    platform_fee_pct = Column(Float, default=25.0)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50))
    payment_intent_id = Column(String(200))
    paid_at = Column(DateTime)
    subscription_id = Column(String(50))
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    refunded_at = Column(DateTime)
    refund_amount = Column(Numeric(10, 2))
    refund_reason = Column(Text)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    superpower = relationship("Superpower", back_populates="transactions")
    __table_args__ = (
        Index("idx_marketplace_transactions_buyer", "buyer_id"),
        Index("idx_marketplace_transactions_developer", "developer_id"),
        Index("idx_marketplace_transactions_superpower", "superpower_id"),
        Index("idx_marketplace_transactions_status", "status"),
        Index("idx_marketplace_transactions_created", "created_at"),
    )
