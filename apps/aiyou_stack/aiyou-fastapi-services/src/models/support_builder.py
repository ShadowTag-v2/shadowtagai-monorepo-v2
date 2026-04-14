"""Database models for Support Builder feature.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database import Base


class FAQ(Base):
    """FAQ model for frequently asked questions."""

    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(500), nullable=False, index=True)
    answer = Column(Text, nullable=False)
    category = Column(String(100), index=True)
    tags = Column(JSON, default=list)  # List of tags for better searchability
    priority = Column(Integer, default=0)  # Higher priority = shown first
    views = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FAQ(id={self.id}, question='{self.question[:50]}...')>"


class HelpArticle(Base):
    """Help article/documentation model."""

    __tablename__ = "help_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(250), unique=True, nullable=False, index=True)
    content = Column(Text, nullable=False)
    excerpt = Column(String(500))
    category = Column(String(100), index=True)
    tags = Column(JSON, default=list)
    author = Column(String(100))
    views = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Related FAQs
    related_faqs = Column(JSON, default=list)  # List of FAQ IDs

    def __repr__(self):
        return f"<HelpArticle(id={self.id}, title='{self.title}')>"


class ChatWidgetConfig(Base):
    """Chat widget configuration model."""

    __tablename__ = "chat_widget_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))

    # Widget appearance
    primary_color = Column(String(7), default="#007bff")  # Hex color
    position = Column(String(20), default="bottom-right")  # bottom-right, bottom-left, etc.
    greeting_message = Column(String(500), default="Hi! How can I help you today?")

    # AI Agent configuration
    ai_system_prompt = Column(Text, nullable=False)
    ai_model = Column(String(50), default="claude-3-sonnet-20240229")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1024)

    # Behavior settings
    enable_faq_suggestions = Column(Boolean, default=True)
    enable_article_suggestions = Column(Boolean, default=True)
    enable_human_handoff = Column(Boolean, default=True)
    auto_suggest_after_messages = Column(Integer, default=3)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chat_sessions = relationship("ChatSession", back_populates="widget_config")

    def __repr__(self):
        return f"<ChatWidgetConfig(id={self.id}, name='{self.name}')>"


class ChatSession(Base):
    """Chat session model for tracking conversations."""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    widget_config_id = Column(Integer, ForeignKey("chat_widget_configs.id"))

    # User information (optional)
    user_id = Column(String(100), index=True)
    user_email = Column(String(100))
    user_name = Column(String(100))

    # Session metadata
    resolved = Column(Boolean, default=False)
    escalated_to_human = Column(Boolean, default=False)
    satisfaction_rating = Column(Integer)  # 1-5 rating

    # Analytics
    message_count = Column(Integer, default=0)
    faq_suggestions_shown = Column(Integer, default=0)
    article_suggestions_shown = Column(Integer, default=0)
    faq_resolved = Column(Boolean, default=False)  # Resolved by FAQ
    article_resolved = Column(Boolean, default=False)  # Resolved by article

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime)

    # Relationships
    widget_config = relationship("ChatWidgetConfig", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id={self.id}, session_id='{self.session_id}')>"


class ChatMessage(Base):
    """Individual chat message model."""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)

    # Message data
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)

    # AI metadata
    model_used = Column(String(50))
    tokens_used = Column(Integer)

    # Suggestions provided with this message
    suggested_faqs = Column(JSON, default=list)  # List of FAQ IDs
    suggested_articles = Column(JSON, default=list)  # List of article IDs

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}')>"


class SupportTicket(Base):
    """Support ticket model for tracking ticket reduction."""

    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(100), unique=True, nullable=False, index=True)

    # Ticket data
    subject = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="open")  # open, resolved, closed
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    category = Column(String(100), index=True)

    # User information
    user_id = Column(String(100), index=True)
    user_email = Column(String(100))
    user_name = Column(String(100))

    # Resolution tracking
    resolved_by = Column(String(50))  # 'ai', 'faq', 'article', 'human'
    resolution_time_minutes = Column(Integer)

    # Associated resources
    related_chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    related_faq_id = Column(Integer, ForeignKey("faqs.id"))
    related_article_id = Column(Integer, ForeignKey("help_articles.id"))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)

    def __repr__(self):
        return (
            f"<SupportTicket(id={self.id}, ticket_id='{self.ticket_id}', status='{self.status}')>"
        )


class Analytics(Base):
    """Analytics model for tracking support metrics."""

    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)

    # Ticket metrics
    total_tickets = Column(Integer, default=0)
    tickets_resolved_by_ai = Column(Integer, default=0)
    tickets_resolved_by_faq = Column(Integer, default=0)
    tickets_resolved_by_article = Column(Integer, default=0)
    tickets_escalated = Column(Integer, default=0)

    # Engagement metrics
    total_chat_sessions = Column(Integer, default=0)
    total_faq_views = Column(Integer, default=0)
    total_article_views = Column(Integer, default=0)
    average_session_length_minutes = Column(Float, default=0.0)

    # Satisfaction metrics
    average_satisfaction_rating = Column(Float)
    total_ratings = Column(Integer, default=0)

    # Reduction metrics
    ticket_reduction_percentage = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Analytics(id={self.id}, date='{self.date}', reduction={self.ticket_reduction_percentage}%)>"
