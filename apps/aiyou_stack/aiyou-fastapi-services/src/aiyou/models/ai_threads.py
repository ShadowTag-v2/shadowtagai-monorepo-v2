"""
AI Thread models for storing and managing curated AI agent knowledge threads.

Handles storage for threads scraped from X/Twitter, including:
- Thread metadata (author, date, likes, tags)
- Individual posts within threads
- Vector embeddings for semantic search
"""

import uuid
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class ThreadSource(StrEnum):
    """Source platform for threads."""

    TWITTER_X = "twitter_x"
    LINKEDIN = "linkedin"
    MANUAL = "manual"
    IMPORT = "import"


class ThreadStatus(StrEnum):
    """Processing status for threads."""

    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class ThreadCategory(StrEnum):
    """Categories for AI agent threads."""

    AGENT_BASICS = "agent_basics"
    PROMPT_ENGINEERING = "prompt_engineering"
    MEMORY_SYSTEMS = "memory_systems"
    TOOL_INTEGRATION = "tool_integration"
    MULTI_AGENT = "multi_agent"
    RAG_RETRIEVAL = "rag_retrieval"
    DEPLOYMENT = "deployment"
    EVALUATION = "evaluation"
    FRAMEWORKS = "frameworks"
    GENERAL = "general"


class AIThreadAuthor(Base):
    """
    Author model for thread creators.

    Tracks authors across multiple threads for attribution and filtering.
    """

    __tablename__ = "ai_thread_authors"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Author identity
    platform_id = Column(String(100), unique=True, index=True, nullable=False)  # e.g., @username
    display_name = Column(String(200), nullable=False)
    username = Column(String(100), index=True, nullable=False)
    platform = Column(SQLEnum(ThreadSource), default=ThreadSource.TWITTER_X, nullable=False)

    # Profile data
    profile_url = Column(String(500))
    avatar_url = Column(String(500))
    bio = Column(Text)
    follower_count = Column(Integer, default=0)
    verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    threads = relationship("AIThread", back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AIThreadAuthor(id={self.id}, username=@{self.username})>"


class AIThread(Base):
    """
    Main thread model representing a complete AI agent knowledge thread.

    A thread contains multiple posts and metadata for search/filtering.
    """

    __tablename__ = "ai_threads"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Platform reference
    platform_post_id = Column(String(100), unique=True, index=True, nullable=False)
    platform = Column(SQLEnum(ThreadSource), default=ThreadSource.TWITTER_X, nullable=False)

    # Foreign keys
    author_id = Column(
        String(36),
        ForeignKey("ai_thread_authors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Thread content
    title = Column(String(500), nullable=False)  # First line or derived title
    full_content = Column(Text, nullable=False)  # Concatenated thread content
    post_count = Column(Integer, default=1)

    # Engagement metrics
    likes = Column(Integer, default=0, index=True)
    retweets = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    views = Column(Integer, default=0)

    # Classification
    category = Column(SQLEnum(ThreadCategory), default=ThreadCategory.GENERAL, index=True)
    tags = Column(ARRAY(String(50)), default=list)

    # Dates
    published_at = Column(DateTime(timezone=True), nullable=False, index=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Processing status
    status = Column(SQLEnum(ThreadStatus), default=ThreadStatus.PENDING, index=True)
    embedding_id = Column(String(100), index=True)  # Reference to vector store

    # Quality metrics
    quality_score = Column(Float)  # AI-assessed quality 0-1
    relevance_score = Column(Float)  # Relevance to AI agents 0-1

    # Metadata
    source_url = Column(String(500))
    metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    author = relationship("AIThreadAuthor", back_populates="threads")
    posts = relationship(
        "AIThreadPost",
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="AIThreadPost.position",
    )
    embeddings = relationship(
        "AIThreadEmbedding", back_populates="thread", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AIThread(id={self.id}, title={self.title[:50]}..., likes={self.likes})>"


class AIThreadPost(Base):
    """
    Individual post within a thread.

    Represents a single tweet/post in the thread sequence.
    """

    __tablename__ = "ai_thread_posts"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    thread_id = Column(
        String(36), ForeignKey("ai_threads.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Platform reference
    platform_post_id = Column(String(100), unique=True, index=True, nullable=False)

    # Position in thread
    position = Column(Integer, nullable=False)  # 1-indexed position

    # Content
    content = Column(Text, nullable=False)
    content_length = Column(Integer)

    # Media
    has_media = Column(Boolean, default=False)
    media_urls = Column(ARRAY(String(500)), default=list)
    media_descriptions = Column(ARRAY(Text), default=list)  # Alt text or AI descriptions

    # Code blocks
    has_code = Column(Boolean, default=False)
    code_language = Column(String(50))  # Detected language

    # Engagement (individual post level)
    likes = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    thread = relationship("AIThread", back_populates="posts")

    def __repr__(self):
        return f"<AIThreadPost(id={self.id}, thread_id={self.thread_id}, position={self.position})>"


class AIThreadEmbedding(Base):
    """
    Vector embeddings for semantic search.

    Stores embeddings at thread and post level for granular retrieval.
    """

    __tablename__ = "ai_thread_embeddings"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign keys
    thread_id = Column(
        String(36), ForeignKey("ai_threads.id", ondelete="CASCADE"), nullable=False, index=True
    )
    post_id = Column(
        String(36), ForeignKey("ai_thread_posts.id", ondelete="SET NULL"), index=True
    )  # Null = full thread embedding

    # Embedding metadata
    embedding_model = Column(String(100), nullable=False)  # e.g., text-embedding-3-large
    embedding_dimensions = Column(Integer, nullable=False)  # e.g., 1536
    embedding_type = Column(String(50), nullable=False)  # "full_thread" or "post"

    # Vector store references
    vector_store = Column(String(50), nullable=False)  # "vertex_ai", "pinecone", "faiss"
    vector_id = Column(String(200), index=True)  # ID in the vector store
    index_name = Column(String(100))  # Index/collection name

    # Content hash for deduplication
    content_hash = Column(String(64), index=True)  # SHA-256 of content

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    thread = relationship("AIThread", back_populates="embeddings")

    def __repr__(self):
        return f"<AIThreadEmbedding(id={self.id}, thread_id={self.thread_id}, type={self.embedding_type})>"


class AIThreadScrapeJob(Base):
    """
    Scrape job tracking for thread collection.

    Manages scheduled and on-demand scraping operations.
    """

    __tablename__ = "ai_thread_scrape_jobs"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Job configuration
    query = Column(String(500), nullable=False)  # Search query
    min_likes = Column(Integer, default=10)
    max_results = Column(Integer, default=100)

    # Status
    status = Column(
        String(50), default="pending", index=True
    )  # pending, running, completed, failed
    threads_found = Column(Integer, default=0)
    threads_saved = Column(Integer, default=0)
    error_message = Column(Text)

    # Timing
    scheduled_at = Column(DateTime(timezone=True))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return (
            f"<AIThreadScrapeJob(id={self.id}, query={self.query[:30]}..., status={self.status})>"
        )
