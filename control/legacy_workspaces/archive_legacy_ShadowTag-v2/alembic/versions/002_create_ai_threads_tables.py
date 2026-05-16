# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Create AI threads tables for storing curated AI agent knowledge

Revision ID: 002
Revises: 001
Create Date: 2025-11-29

Tables created:
- ai_thread_authors: Thread creators/authors
- ai_threads: Main thread records
- ai_thread_posts: Individual posts within threads
- ai_thread_embeddings: Vector embeddings for semantic search
- ai_thread_scrape_jobs: Scrape job tracking
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY, JSON

# revision identifiers
revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
  """Create all tables for AI thread management"""

  # AI thread authors table
  op.create_table(
    "ai_thread_authors",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("platform_id", sa.String(100), unique=True, nullable=False),
    sa.Column("display_name", sa.String(200), nullable=False),
    sa.Column("username", sa.String(100), nullable=False),
    sa.Column("platform", sa.String(20), default="twitter_x", nullable=False),
    sa.Column("profile_url", sa.String(500), nullable=True),
    sa.Column("avatar_url", sa.String(500), nullable=True),
    sa.Column("bio", sa.Text, nullable=True),
    sa.Column("follower_count", sa.Integer, default=0),
    sa.Column("verified", sa.Boolean, default=False),
    sa.Column(
      "created_at",
      sa.DateTime(timezone=True),
      server_default=sa.func.now(),
      nullable=False,
    ),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
  )
  op.create_index("idx_author_platform_id", "ai_thread_authors", ["platform_id"])
  op.create_index("idx_author_username", "ai_thread_authors", ["username"])

  # AI threads table
  op.create_table(
    "ai_threads",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("platform_post_id", sa.String(100), unique=True, nullable=False),
    sa.Column("platform", sa.String(20), default="twitter_x", nullable=False),
    sa.Column(
      "author_id",
      sa.String(36),
      sa.ForeignKey("ai_thread_authors.id", ondelete="CASCADE"),
      nullable=False,
    ),
    sa.Column("title", sa.String(500), nullable=False),
    sa.Column("full_content", sa.Text, nullable=False),
    sa.Column("post_count", sa.Integer, default=1),
    sa.Column("likes", sa.Integer, default=0),
    sa.Column("retweets", sa.Integer, default=0),
    sa.Column("replies", sa.Integer, default=0),
    sa.Column("views", sa.Integer, default=0),
    sa.Column("category", sa.String(50), default="general"),
    sa.Column("tags", ARRAY(sa.String(50)), default=[]),
    sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
    sa.Column("scraped_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("status", sa.String(20), default="pending"),
    sa.Column("embedding_id", sa.String(100), nullable=True),
    sa.Column("quality_score", sa.Float, nullable=True),
    sa.Column("relevance_score", sa.Float, nullable=True),
    sa.Column("source_url", sa.String(500), nullable=True),
    sa.Column("metadata", JSON, nullable=True),
    sa.Column(
      "created_at",
      sa.DateTime(timezone=True),
      server_default=sa.func.now(),
      nullable=False,
    ),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
  )
  op.create_index("idx_thread_platform_post_id", "ai_threads", ["platform_post_id"])
  op.create_index("idx_thread_author_id", "ai_threads", ["author_id"])
  op.create_index("idx_thread_likes", "ai_threads", ["likes"])
  op.create_index("idx_thread_category", "ai_threads", ["category"])
  op.create_index("idx_thread_published_at", "ai_threads", ["published_at"])
  op.create_index("idx_thread_status", "ai_threads", ["status"])
  op.create_index("idx_thread_embedding_id", "ai_threads", ["embedding_id"])

  # AI thread posts table
  op.create_table(
    "ai_thread_posts",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column(
      "thread_id",
      sa.String(36),
      sa.ForeignKey("ai_threads.id", ondelete="CASCADE"),
      nullable=False,
    ),
    sa.Column("platform_post_id", sa.String(100), unique=True, nullable=False),
    sa.Column("position", sa.Integer, nullable=False),
    sa.Column("content", sa.Text, nullable=False),
    sa.Column("content_length", sa.Integer, nullable=True),
    sa.Column("has_media", sa.Boolean, default=False),
    sa.Column("media_urls", ARRAY(sa.String(500)), default=[]),
    sa.Column("media_descriptions", ARRAY(sa.Text), default=[]),
    sa.Column("has_code", sa.Boolean, default=False),
    sa.Column("code_language", sa.String(50), nullable=True),
    sa.Column("likes", sa.Integer, default=0),
    sa.Column(
      "created_at",
      sa.DateTime(timezone=True),
      server_default=sa.func.now(),
      nullable=False,
    ),
  )
  op.create_index("idx_post_thread_id", "ai_thread_posts", ["thread_id"])
  op.create_index("idx_post_platform_post_id", "ai_thread_posts", ["platform_post_id"])
  op.create_index("idx_post_position", "ai_thread_posts", ["position"])

  # AI thread embeddings table
  op.create_table(
    "ai_thread_embeddings",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column(
      "thread_id",
      sa.String(36),
      sa.ForeignKey("ai_threads.id", ondelete="CASCADE"),
      nullable=False,
    ),
    sa.Column(
      "post_id",
      sa.String(36),
      sa.ForeignKey("ai_thread_posts.id", ondelete="SET NULL"),
      nullable=True,
    ),
    sa.Column("embedding_model", sa.String(100), nullable=False),
    sa.Column("embedding_dimensions", sa.Integer, nullable=False),
    sa.Column("embedding_type", sa.String(50), nullable=False),
    sa.Column("vector_store", sa.String(50), nullable=False),
    sa.Column("vector_id", sa.String(200), nullable=True),
    sa.Column("index_name", sa.String(100), nullable=True),
    sa.Column("content_hash", sa.String(64), nullable=True),
    sa.Column(
      "created_at",
      sa.DateTime(timezone=True),
      server_default=sa.func.now(),
      nullable=False,
    ),
    sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
  )
  op.create_index("idx_embedding_thread_id", "ai_thread_embeddings", ["thread_id"])
  op.create_index("idx_embedding_post_id", "ai_thread_embeddings", ["post_id"])
  op.create_index("idx_embedding_vector_id", "ai_thread_embeddings", ["vector_id"])
  op.create_index(
    "idx_embedding_content_hash", "ai_thread_embeddings", ["content_hash"]
  )

  # AI thread scrape jobs table
  op.create_table(
    "ai_thread_scrape_jobs",
    sa.Column("id", sa.String(36), primary_key=True),
    sa.Column("query", sa.String(500), nullable=False),
    sa.Column("min_likes", sa.Integer, default=10),
    sa.Column("max_results", sa.Integer, default=100),
    sa.Column("status", sa.String(50), default="pending"),
    sa.Column("threads_found", sa.Integer, default=0),
    sa.Column("threads_saved", sa.Integer, default=0),
    sa.Column("error_message", sa.Text, nullable=True),
    sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column(
      "created_at",
      sa.DateTime(timezone=True),
      server_default=sa.func.now(),
      nullable=False,
    ),
  )
  op.create_index("idx_scrape_job_status", "ai_thread_scrape_jobs", ["status"])


def downgrade():
  """Drop all AI thread tables"""
  op.drop_table("ai_thread_scrape_jobs")
  op.drop_table("ai_thread_embeddings")
  op.drop_table("ai_thread_posts")
  op.drop_table("ai_threads")
  op.drop_table("ai_thread_authors")
