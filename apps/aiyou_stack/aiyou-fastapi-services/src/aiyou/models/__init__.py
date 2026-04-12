"""
Database models for all ShadowTag-v4 services.

This package contains SQLAlchemy ORM models for:
- User authentication and profiles
- CineVerse streaming content
- GamePort sessions and integrations
- Commerce products and orders
- ShadowTag verification records
- Infrastructure node management
- Revenue tracking and analytics
"""

from .ai_threads import (
    AIThread,
    AIThreadAuthor,
    AIThreadEmbedding,
    AIThreadPost,
    AIThreadScrapeJob,
    ThreadCategory,
    ThreadSource,
    ThreadStatus,
)
from .analytics import PerformanceMetric, RevenueEvent, UserEvent
from .cineverse import Content, ContentType, Creator, Stream, Subscription
from .commerce import Cart, Order, OrderItem, Payment, Product
from .gameport import Game, GamePublisher, GameSession
from .infrastructure import EdgePop, Node, NodeStatus, NodeType
from .shadowtag import VerificationChain, VerificationRecord
from .user import User, UserRole, UserSession

__all__ = [
    # AI Thread models
    "AIThread",
    "AIThreadAuthor",
    "AIThreadPost",
    "AIThreadEmbedding",
    "AIThreadScrapeJob",
    "ThreadSource",
    "ThreadStatus",
    "ThreadCategory",
    # User models
    "User",
    "UserRole",
    "UserSession",
    # CineVerse models
    "Content",
    "ContentType",
    "Stream",
    "Creator",
    "Subscription",
    # GamePort models
    "Game",
    "GameSession",
    "GamePublisher",
    # Commerce models
    "Product",
    "Order",
    "OrderItem",
    "Cart",
    "Payment",
    # ShadowTag models
    "VerificationRecord",
    "VerificationChain",
    # Infrastructure models
    "Node",
    "NodeType",
    "NodeStatus",
    "EdgePop",
    # Analytics models
    "RevenueEvent",
    "UserEvent",
    "PerformanceMetric",
]
