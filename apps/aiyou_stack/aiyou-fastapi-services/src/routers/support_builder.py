"""API routes for Support Builder feature.

Provides REST endpoints for FAQs, help articles, chat widgets,
and analytics.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.support_builder import (
    # Analytics
    AnalyticsSummary,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatResponse,
    # Chat Session
    ChatSessionCreate,
    ChatSessionResponse,
    # Chat Widget
    ChatWidgetConfigCreate,
    ChatWidgetConfigResponse,
    FAQCreate,
    FAQResponse,
    FAQUpdate,
    FeedbackRequest,
    # Articles
    HelpArticleCreate,
    HelpArticleResponse,
    HelpArticleUpdate,
    # Common
    SearchRequest,
    # Tickets
    SupportTicketCreate,
    SupportTicketResponse,
)
from src.services.support_builder_service import SupportBuilderService

router = APIRouter(prefix="/api/support-builder", tags=["Support Builder"])


# ===== FAQ Endpoints =====


@router.post("/faqs", response_model=FAQResponse, status_code=201)
async def create_faq(
    faq: FAQCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new FAQ."""
    return await SupportBuilderService.create_faq(db, faq)


@router.get("/faqs", response_model=list[FAQResponse])
async def get_faqs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str | None = None,
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get list of FAQs with optional filtering."""
    return await SupportBuilderService.get_faqs(
        db,
        skip=skip,
        limit=limit,
        category=category,
        active_only=active_only,
    )


@router.get("/faqs/{faq_id}", response_model=FAQResponse)
async def get_faq(
    faq_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific FAQ by ID."""
    faq = await SupportBuilderService.get_faq(db, faq_id)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@router.put("/faqs/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: int,
    faq_update: FAQUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an FAQ."""
    faq = await SupportBuilderService.update_faq(db, faq_id, faq_update)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


@router.delete("/faqs/{faq_id}", status_code=204)
async def delete_faq(
    faq_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an FAQ."""
    success = await SupportBuilderService.delete_faq(db, faq_id)
    if not success:
        raise HTTPException(status_code=404, detail="FAQ not found")


@router.post("/faqs/search", response_model=list[FAQResponse])
async def search_faqs(
    search: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search FAQs by question or answer."""
    return await SupportBuilderService.search_faqs(db, search.query, search.limit)


@router.post("/faqs/{faq_id}/feedback", response_model=FAQResponse)
async def faq_feedback(
    faq_id: int,
    feedback: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """Record user feedback on an FAQ."""
    faq = await SupportBuilderService.record_faq_feedback(db, faq_id, feedback.helpful)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq


# ===== Help Article Endpoints =====


@router.post("/articles", response_model=HelpArticleResponse, status_code=201)
async def create_article(
    article: HelpArticleCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new help article."""
    return await SupportBuilderService.create_article(db, article)


@router.get("/articles", response_model=list[HelpArticleResponse])
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str | None = None,
    published_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """Get list of help articles."""
    return await SupportBuilderService.get_articles(
        db,
        skip=skip,
        limit=limit,
        category=category,
        published_only=published_only,
    )


@router.get("/articles/{article_id}", response_model=HelpArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific help article by ID."""
    article = await SupportBuilderService.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/articles/slug/{slug}", response_model=HelpArticleResponse)
async def get_article_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a help article by slug."""
    article = await SupportBuilderService.get_article_by_slug(db, slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.put("/articles/{article_id}", response_model=HelpArticleResponse)
async def update_article(
    article_id: int,
    article_update: HelpArticleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a help article."""
    article = await SupportBuilderService.update_article(db, article_id, article_update)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/articles/search", response_model=list[HelpArticleResponse])
async def search_articles(
    search: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search help articles."""
    return await SupportBuilderService.search_articles(db, search.query, search.limit)


# ===== Chat Widget Configuration Endpoints =====


@router.post("/widget-configs", response_model=ChatWidgetConfigResponse, status_code=201)
async def create_widget_config(
    config: ChatWidgetConfigCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat widget configuration."""
    return await SupportBuilderService.create_widget_config(db, config)


@router.get("/widget-configs/{config_id}", response_model=ChatWidgetConfigResponse)
async def get_widget_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get chat widget configuration."""
    config = await SupportBuilderService.get_widget_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Widget configuration not found")
    return config


# ===== Chat Session Endpoints =====


@router.post("/chat/sessions", response_model=ChatSessionResponse, status_code=201)
async def create_chat_session(
    session: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    return await SupportBuilderService.create_chat_session(db, session)


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get chat session details."""
    session = await SupportBuilderService.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.post("/chat/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_chat_message(
    session_id: str,
    message: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Send a message in a chat session and get AI response with suggestions.

    This endpoint:
    1. Processes the user message
    2. Generates an AI response using Claude
    3. Suggests relevant FAQs and help articles
    4. Stores the conversation
    """
    try:
        result = await SupportBuilderService.process_chat_message(db, session_id, message.content)
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {e!s}") from e


@router.get("/chat/sessions/{session_id}/history", response_model=list[ChatMessageResponse])
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get conversation history for a chat session."""
    session = await SupportBuilderService.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # Get messages
    from sqlalchemy import select

    from src.models.support_builder import ChatMessage

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at),
    )
    messages = result.scalars().all()
    return messages


# ===== Support Ticket Endpoints =====


@router.post("/tickets", response_model=SupportTicketResponse, status_code=201)
async def create_ticket(
    ticket: SupportTicketCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new support ticket."""
    return await SupportBuilderService.create_ticket(db, ticket)


# ===== Analytics Endpoints =====


@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get analytics summary showing ticket reduction and support metrics.

    This endpoint provides insights into:
    - Total tickets and resolution methods
    - Ticket reduction percentage (target: 80%)
    - Average resolution times
    - Chat session statistics
    - Customer satisfaction ratings
    """
    return await SupportBuilderService.get_analytics_summary(db, start_date, end_date)


# ===== Health Check =====


@router.get("/health")
async def health_check():
    """Health check endpoint for Support Builder service."""
    return {
        "status": "healthy",
        "service": "Support Builder",
        "timestamp": datetime.utcnow().isoformat(),
    }
