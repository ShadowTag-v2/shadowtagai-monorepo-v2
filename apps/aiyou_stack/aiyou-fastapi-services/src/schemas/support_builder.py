"""
Pydantic schemas for Support Builder API request/response validation.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

# ===== FAQ Schemas =====


class FAQBase(BaseModel):
    """Base FAQ schema."""

    question: str = Field(..., min_length=5, max_length=500)
    answer: str = Field(..., min_length=10)
    category: str | None = Field(None, max_length=100)
    tags: list[str] = Field(default_factory=list)
    priority: int = Field(default=0, ge=0)


class FAQCreate(FAQBase):
    """Schema for creating a new FAQ."""

    pass


class FAQUpdate(BaseModel):
    """Schema for updating an FAQ."""

    question: str | None = Field(None, min_length=5, max_length=500)
    answer: str | None = Field(None, min_length=10)
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    priority: int | None = Field(None, ge=0)
    is_active: bool | None = None


class FAQResponse(FAQBase):
    """Schema for FAQ response."""

    id: int
    views: int
    helpful_count: int
    not_helpful_count: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Help Article Schemas =====


class HelpArticleBase(BaseModel):
    """Base help article schema."""

    title: str = Field(..., min_length=5, max_length=200)
    slug: str = Field(..., min_length=3, max_length=250)
    content: str = Field(..., min_length=50)
    excerpt: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=100)
    tags: list[str] = Field(default_factory=list)
    author: str | None = Field(None, max_length=100)
    related_faqs: list[int] = Field(default_factory=list)


class HelpArticleCreate(HelpArticleBase):
    """Schema for creating a help article."""

    pass


class HelpArticleUpdate(BaseModel):
    """Schema for updating a help article."""

    title: str | None = Field(None, min_length=5, max_length=200)
    content: str | None = Field(None, min_length=50)
    excerpt: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    author: str | None = Field(None, max_length=100)
    is_published: bool | None = None
    related_faqs: list[int] | None = None


class HelpArticleResponse(HelpArticleBase):
    """Schema for help article response."""

    id: int
    views: int
    helpful_count: int
    not_helpful_count: int
    is_published: bool
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Chat Widget Config Schemas =====


class ChatWidgetConfigBase(BaseModel):
    """Base chat widget configuration schema."""

    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    primary_color: str = Field(default="#007bff", pattern=r"^#[0-9A-Fa-f]{6}$")
    position: str = Field(default="bottom-right")
    greeting_message: str = Field(default="Hi! How can I help you today?", max_length=500)
    ai_system_prompt: str = Field(..., min_length=10)
    ai_model: str = Field(default="claude-3-sonnet-20240229")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    enable_faq_suggestions: bool = True
    enable_article_suggestions: bool = True
    enable_human_handoff: bool = True
    auto_suggest_after_messages: int = Field(default=3, ge=0)


class ChatWidgetConfigCreate(ChatWidgetConfigBase):
    """Schema for creating a chat widget configuration."""

    pass


class ChatWidgetConfigUpdate(BaseModel):
    """Schema for updating a chat widget configuration."""

    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    primary_color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    position: str | None = None
    greeting_message: str | None = Field(None, max_length=500)
    ai_system_prompt: str | None = Field(None, min_length=10)
    ai_model: str | None = None
    temperature: float | None = Field(None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, le=4096)
    enable_faq_suggestions: bool | None = None
    enable_article_suggestions: bool | None = None
    enable_human_handoff: bool | None = None
    auto_suggest_after_messages: int | None = Field(None, ge=0)
    is_active: bool | None = None


class ChatWidgetConfigResponse(ChatWidgetConfigBase):
    """Schema for chat widget configuration response."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===== Chat Session Schemas =====


class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session."""

    widget_config_id: int
    user_id: str | None = None
    user_email: EmailStr | None = None
    user_name: str | None = None


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""

    id: int
    session_id: str
    widget_config_id: int
    user_id: str | None = None
    user_email: str | None = None
    user_name: str | None = None
    resolved: bool
    escalated_to_human: bool
    satisfaction_rating: int | None = None
    message_count: int
    created_at: datetime
    ended_at: datetime | None = None

    model_config = {"from_attributes": True}


# ===== Chat Message Schemas =====


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""

    session_id: str
    content: str = Field(..., min_length=1, max_length=5000)


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""

    id: int
    role: str
    content: str
    suggested_faqs: list[int]
    suggested_articles: list[int]
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    """Schema for chat AI response."""

    message: str
    suggested_faqs: list[FAQResponse] = Field(default_factory=list)
    suggested_articles: list[HelpArticleResponse] = Field(default_factory=list)


# ===== Support Ticket Schemas =====


class SupportTicketBase(BaseModel):
    """Base support ticket schema."""

    subject: str = Field(..., min_length=5, max_length=200)
    description: str | None = None
    priority: str = Field(default="medium")
    category: str | None = Field(None, max_length=100)
    user_id: str | None = None
    user_email: EmailStr | None = None
    user_name: str | None = None


class SupportTicketCreate(SupportTicketBase):
    """Schema for creating a support ticket."""

    pass


class SupportTicketUpdate(BaseModel):
    """Schema for updating a support ticket."""

    subject: str | None = Field(None, min_length=5, max_length=200)
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    category: str | None = Field(None, max_length=100)
    resolved_by: str | None = None


class SupportTicketResponse(SupportTicketBase):
    """Schema for support ticket response."""

    id: int
    ticket_id: str
    status: str
    resolved_by: str | None = None
    resolution_time_minutes: int | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None

    model_config = {"from_attributes": True}


# ===== Analytics Schemas =====


class AnalyticsResponse(BaseModel):
    """Schema for analytics response."""

    id: int
    date: datetime
    total_tickets: int
    tickets_resolved_by_ai: int
    tickets_resolved_by_faq: int
    tickets_resolved_by_article: int
    tickets_escalated: int
    total_chat_sessions: int
    total_faq_views: int
    total_article_views: int
    average_session_length_minutes: float
    average_satisfaction_rating: float | None = None
    total_ratings: int
    ticket_reduction_percentage: float

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    """Schema for analytics summary."""

    total_tickets: int
    ai_resolved_count: int
    faq_resolved_count: int
    article_resolved_count: int
    escalated_count: int
    reduction_percentage: float
    average_resolution_time_minutes: float
    total_chat_sessions: int
    average_satisfaction: float | None = None


# ===== Search and Filter Schemas =====


class SearchRequest(BaseModel):
    """Schema for search requests."""

    query: str = Field(..., min_length=1, max_length=200)
    category: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


class FeedbackRequest(BaseModel):
    """Schema for feedback on FAQs/Articles."""

    item_id: int
    helpful: bool
