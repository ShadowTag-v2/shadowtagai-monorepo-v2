# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Business logic layer for Support Builder feature.

Handles database operations, AI integration, and core functionality.
"""

import uuid
from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai_agents.support_builder_agent import support_agent
from src.models.support_builder import (
    FAQ,
    ChatMessage,
    ChatSession,
    ChatWidgetConfig,
    HelpArticle,
    SupportTicket,
)
from src.schemas.support_builder import (
    AnalyticsSummary,
    ChatSessionCreate,
    ChatWidgetConfigCreate,
    FAQCreate,
    FAQUpdate,
    HelpArticleCreate,
    HelpArticleUpdate,
    SupportTicketCreate,
)


class SupportBuilderService:
    """Service class for Support Builder operations."""

    # ===== FAQ Operations =====

    @staticmethod
    async def create_faq(db: AsyncSession, faq_data: FAQCreate) -> FAQ:
        """Create a new FAQ."""
        faq = FAQ(**faq_data.model_dump())
        db.add(faq)
        await db.commit()
        await db.refresh(faq)
        return faq

    @staticmethod
    async def get_faq(db: AsyncSession, faq_id: int) -> FAQ | None:
        """Get FAQ by ID."""
        result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_faqs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        active_only: bool = True,
    ) -> list[FAQ]:
        """Get list of FAQs with optional filtering."""
        query = select(FAQ)

        if active_only:
            query = query.where(FAQ.is_active)

        if category:
            query = query.where(FAQ.category == category)

        query = query.order_by(FAQ.priority.desc(), FAQ.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_faq(db: AsyncSession, faq_id: int, faq_data: FAQUpdate) -> FAQ | None:
        """Update an FAQ."""
        faq = await SupportBuilderService.get_faq(db, faq_id)
        if not faq:
            return None

        update_data = faq_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(faq, field, value)

        faq.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(faq)
        return faq

    @staticmethod
    async def delete_faq(db: AsyncSession, faq_id: int) -> bool:
        """Delete an FAQ."""
        faq = await SupportBuilderService.get_faq(db, faq_id)
        if not faq:
            return False

        await db.delete(faq)
        await db.commit()
        return True

    @staticmethod
    async def search_faqs(db: AsyncSession, query: str, limit: int = 10) -> list[FAQ]:
        """Search FAQs by question or answer content."""
        search_pattern = f"%{query}%"
        stmt = (
            select(FAQ)
            .where(
                and_(
                    FAQ.is_active,
                    or_(
                        FAQ.question.ilike(search_pattern),
                        FAQ.answer.ilike(search_pattern),
                    ),
                ),
            )
            .order_by(FAQ.priority.desc(), FAQ.helpful_count.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def record_faq_feedback(db: AsyncSession, faq_id: int, helpful: bool) -> FAQ | None:
        """Record user feedback on FAQ."""
        faq = await SupportBuilderService.get_faq(db, faq_id)
        if not faq:
            return None

        if helpful:
            faq.helpful_count += 1
        else:
            faq.not_helpful_count += 1

        await db.commit()
        await db.refresh(faq)
        return faq

    # ===== Help Article Operations =====

    @staticmethod
    async def create_article(db: AsyncSession, article_data: HelpArticleCreate) -> HelpArticle:
        """Create a new help article."""
        article = HelpArticle(**article_data.model_dump())
        db.add(article)
        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    async def get_article(db: AsyncSession, article_id: int) -> HelpArticle | None:
        """Get help article by ID."""
        result = await db.execute(select(HelpArticle).where(HelpArticle.id == article_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_article_by_slug(db: AsyncSession, slug: str) -> HelpArticle | None:
        """Get help article by slug."""
        result = await db.execute(select(HelpArticle).where(HelpArticle.slug == slug))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_articles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        category: str | None = None,
        published_only: bool = True,
    ) -> list[HelpArticle]:
        """Get list of help articles with optional filtering."""
        query = select(HelpArticle)

        if published_only:
            query = query.where(HelpArticle.is_published)

        if category:
            query = query.where(HelpArticle.category == category)

        query = query.order_by(HelpArticle.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update_article(
        db: AsyncSession,
        article_id: int,
        article_data: HelpArticleUpdate,
    ) -> HelpArticle | None:
        """Update a help article."""
        article = await SupportBuilderService.get_article(db, article_id)
        if not article:
            return None

        update_data = article_data.model_dump(exclude_unset=True)

        # Handle publication
        if (
            "is_published" in update_data
            and update_data["is_published"]
            and not article.is_published
        ):
            update_data["published_at"] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(article, field, value)

        article.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(article)
        return article

    @staticmethod
    async def search_articles(db: AsyncSession, query: str, limit: int = 10) -> list[HelpArticle]:
        """Search articles by title or content."""
        search_pattern = f"%{query}%"
        stmt = (
            select(HelpArticle)
            .where(
                and_(
                    HelpArticle.is_published,
                    or_(
                        HelpArticle.title.ilike(search_pattern),
                        HelpArticle.content.ilike(search_pattern),
                    ),
                ),
            )
            .order_by(HelpArticle.helpful_count.desc(), HelpArticle.views.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ===== Chat Widget Configuration =====

    @staticmethod
    async def create_widget_config(
        db: AsyncSession,
        config_data: ChatWidgetConfigCreate,
    ) -> ChatWidgetConfig:
        """Create a new chat widget configuration."""
        config = ChatWidgetConfig(**config_data.model_dump())
        db.add(config)
        await db.commit()
        await db.refresh(config)
        return config

    @staticmethod
    async def get_widget_config(db: AsyncSession, config_id: int) -> ChatWidgetConfig | None:
        """Get chat widget configuration by ID."""
        result = await db.execute(select(ChatWidgetConfig).where(ChatWidgetConfig.id == config_id))
        return result.scalar_one_or_none()

    # ===== Chat Session Operations =====

    @staticmethod
    async def create_chat_session(db: AsyncSession, session_data: ChatSessionCreate) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            session_id=str(uuid.uuid4()),
            **session_data.model_dump(),
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @staticmethod
    async def get_chat_session(db: AsyncSession, session_id: str) -> ChatSession | None:
        """Get chat session by session_id."""
        result = await db.execute(select(ChatSession).where(ChatSession.session_id == session_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def process_chat_message(
        db: AsyncSession,
        session_id: str,
        user_message: str,
    ) -> dict:
        """Process a chat message and generate AI response with suggestions.

        Returns a dictionary with the AI response and suggested FAQs/articles.
        """
        # Get session
        session = await SupportBuilderService.get_chat_session(db, session_id)
        if not session:
            raise ValueError("Chat session not found")

        # Get widget configuration
        widget_config = await SupportBuilderService.get_widget_config(db, session.widget_config_id)
        if not widget_config:
            raise ValueError("Widget configuration not found")

        # Get conversation history
        conversation_history = await SupportBuilderService.get_conversation_history(db, session.id)

        # Generate AI response
        ai_response = await support_agent.generate_response(
            user_message=user_message,
            conversation_history=conversation_history,
            system_prompt=widget_config.ai_system_prompt,
            model=widget_config.ai_model,
            temperature=widget_config.temperature,
            max_tokens=widget_config.max_tokens,
        )

        # Save user message
        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=user_message,
        )
        db.add(user_msg)

        # Find relevant FAQs and articles if enabled
        suggested_faqs = []
        suggested_articles = []

        if widget_config.enable_faq_suggestions:
            # Generate keywords for search
            keywords = await support_agent.generate_faq_suggestion_keywords(user_message)
            search_query = " ".join(keywords)
            suggested_faqs = await SupportBuilderService.search_faqs(db, search_query, limit=3)

        if widget_config.enable_article_suggestions:
            # Search articles
            keywords = await support_agent.generate_faq_suggestion_keywords(user_message)
            search_query = " ".join(keywords)
            suggested_articles = await SupportBuilderService.search_articles(
                db,
                search_query,
                limit=3,
            )

        # Save AI response message
        ai_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response,
            model_used=widget_config.ai_model,
            suggested_faqs=[faq.id for faq in suggested_faqs],
            suggested_articles=[article.id for article in suggested_articles],
        )
        db.add(ai_msg)

        # Update session stats
        session.message_count += 2  # User + assistant
        session.faq_suggestions_shown += len(suggested_faqs)
        session.article_suggestions_shown += len(suggested_articles)
        session.updated_at = datetime.utcnow()

        await db.commit()

        return {
            "message": ai_response,
            "suggested_faqs": suggested_faqs,
            "suggested_articles": suggested_articles,
        }

    @staticmethod
    async def get_conversation_history(
        db: AsyncSession,
        session_db_id: int,
    ) -> list[dict[str, str]]:
        """Get conversation history for a session."""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_db_id)
            .order_by(ChatMessage.created_at),
        )
        messages = result.scalars().all()

        return [{"role": msg.role, "content": msg.content} for msg in messages]

    # ===== Support Ticket Operations =====

    @staticmethod
    async def create_ticket(db: AsyncSession, ticket_data: SupportTicketCreate) -> SupportTicket:
        """Create a new support ticket."""
        ticket = SupportTicket(
            ticket_id=f"TICKET-{uuid.uuid4().hex[:8].upper()}",
            **ticket_data.model_dump(),
        )
        db.add(ticket)
        await db.commit()
        await db.refresh(ticket)
        return ticket

    # ===== Analytics Operations =====

    @staticmethod
    async def get_analytics_summary(
        db: AsyncSession,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> AnalyticsSummary:
        """Get analytics summary for a date range."""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # Query tickets
        ticket_query = select(SupportTicket).where(
            and_(
                SupportTicket.created_at >= start_date,
                SupportTicket.created_at <= end_date,
            ),
        )
        result = await db.execute(ticket_query)
        tickets = list(result.scalars().all())

        total_tickets = len(tickets)
        ai_resolved = len([t for t in tickets if t.resolved_by == "ai"])
        faq_resolved = len([t for t in tickets if t.resolved_by == "faq"])
        article_resolved = len([t for t in tickets if t.resolved_by == "article"])
        escalated = len([t for t in tickets if t.resolved_by == "human"])

        # Calculate reduction percentage
        self_service_resolved = ai_resolved + faq_resolved + article_resolved
        reduction_pct = (self_service_resolved / total_tickets * 100) if total_tickets > 0 else 0

        # Average resolution time
        resolved_tickets = [t for t in tickets if t.resolution_time_minutes is not None]
        avg_resolution = (
            sum(t.resolution_time_minutes for t in resolved_tickets) / len(resolved_tickets)
            if resolved_tickets
            else 0
        )

        # Chat sessions count
        session_query = select(func.count(ChatSession.id)).where(
            and_(
                ChatSession.created_at >= start_date,
                ChatSession.created_at <= end_date,
            ),
        )
        result = await db.execute(session_query)
        total_sessions = result.scalar() or 0

        # Average satisfaction
        satisfaction_query = select(func.avg(ChatSession.satisfaction_rating)).where(
            and_(
                ChatSession.created_at >= start_date,
                ChatSession.created_at <= end_date,
                ChatSession.satisfaction_rating.isnot(None),
            ),
        )
        result = await db.execute(satisfaction_query)
        avg_satisfaction = result.scalar()

        return AnalyticsSummary(
            total_tickets=total_tickets,
            ai_resolved_count=ai_resolved,
            faq_resolved_count=faq_resolved,
            article_resolved_count=article_resolved,
            escalated_count=escalated,
            reduction_percentage=round(reduction_pct, 2),
            average_resolution_time_minutes=round(avg_resolution, 2),
            total_chat_sessions=total_sessions,
            average_satisfaction=round(avg_satisfaction, 2) if avg_satisfaction else None,
        )
