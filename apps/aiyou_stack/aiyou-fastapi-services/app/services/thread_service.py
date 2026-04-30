"""Thread Service for AI agent knowledge threads.

Business logic for:
- Thread CRUD operations
- Compilation parsing and import
- Export to various formats
- Analytics and statistics
"""

import logging
import re
import uuid
from datetime import datetime

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, joinedload
from src.shadowtag_v4.models.ai_threads import (
    AIThread,
    AIThreadAuthor,
    AIThreadPost,
    ThreadCategory,
    ThreadSource,
    ThreadStatus,
)

from app.api.schemas.ai_threads import (
    BulkImportRequest,
    BulkImportResult,
    ExportFormat,
    ExportRequest,
    SortOrder,
    ThreadAnalytics,
    ThreadCreate,
    ThreadListRequest,
    ThreadListResponse,
    ThreadSummary,
    ThreadUpdate,
)

logger = logging.getLogger(__name__)


class ThreadService:
    """Service for managing AI agent knowledge threads."""

    def __init__(self, db: Session):
        self.db = db

    # ========================================================================
    # CRUD Operations
    # ========================================================================

    async def create_thread(self, data: ThreadCreate) -> AIThread:
        """Create a new thread with author and posts."""
        # Handle author - find existing or create new
        author = None
        if data.author_id:
            author = self.db.query(AIThreadAuthor).filter_by(id=data.author_id).first()
            if not author:
                raise ValueError(f"Author not found: {data.author_id}")
        elif data.author:
            # Check if author exists by platform_id
            author = (
                self.db.query(AIThreadAuthor).filter_by(platform_id=data.author.platform_id).first()
            )
            if not author:
                author = AIThreadAuthor(
                    id=str(uuid.uuid4()),
                    platform_id=data.author.platform_id,
                    display_name=data.author.display_name,
                    username=data.author.username,
                    platform=data.author.platform,
                    profile_url=data.author.profile_url,
                    avatar_url=data.author.avatar_url,
                    bio=data.author.bio,
                    follower_count=data.author.follower_count,
                    verified=data.author.verified,
                )
                self.db.add(author)
                self.db.flush()
        else:
            raise ValueError("Either author_id or author must be provided")

        # Create thread
        thread = AIThread(
            id=str(uuid.uuid4()),
            platform_post_id=data.platform_post_id,
            platform=data.platform,
            author_id=author.id,
            title=data.title,
            full_content=data.full_content,
            post_count=len(data.posts) if data.posts else 1,
            likes=data.likes,
            retweets=data.retweets,
            replies=data.replies,
            views=data.views,
            category=data.category,
            tags=data.tags,
            published_at=data.published_at,
            source_url=data.source_url,
            metadata=data.metadata,
            status=ThreadStatus.PENDING,
        )
        self.db.add(thread)
        self.db.flush()

        # Create posts
        for post_data in data.posts:
            post = AIThreadPost(
                id=str(uuid.uuid4()),
                thread_id=thread.id,
                platform_post_id=post_data.platform_post_id,
                position=post_data.position,
                content=post_data.content,
                content_length=len(post_data.content),
                has_media=post_data.has_media,
                media_urls=post_data.media_urls,
                media_descriptions=post_data.media_descriptions,
                has_code=post_data.has_code,
                code_language=post_data.code_language,
                likes=post_data.likes,
            )
            self.db.add(post)

        self.db.commit()
        self.db.refresh(thread)
        return thread

    async def get_thread(self, thread_id: str) -> AIThread | None:
        """Get a thread by ID with all relationships."""
        return (
            self.db.query(AIThread)
            .options(
                joinedload(AIThread.author),
                joinedload(AIThread.posts),
            )
            .filter_by(id=thread_id)
            .first()
        )

    async def get_thread_by_platform_id(self, platform_post_id: str) -> AIThread | None:
        """Get a thread by platform post ID."""
        return self.db.query(AIThread).filter_by(platform_post_id=platform_post_id).first()

    async def update_thread(self, thread_id: str, data: ThreadUpdate) -> AIThread | None:
        """Update thread fields."""
        thread = self.db.query(AIThread).filter_by(id=thread_id).first()
        if not thread:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(thread, key, value)

        self.db.commit()
        self.db.refresh(thread)
        return thread

    async def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all related data."""
        thread = self.db.query(AIThread).filter_by(id=thread_id).first()
        if not thread:
            return False

        self.db.delete(thread)
        self.db.commit()
        return True

    async def list_threads(self, request: ThreadListRequest) -> ThreadListResponse:
        """List threads with pagination and filters."""
        query = self.db.query(AIThread).options(joinedload(AIThread.author))

        # Apply filters
        if request.category:
            query = query.filter(AIThread.category == request.category)
        if request.status:
            query = query.filter(AIThread.status == request.status)
        if request.min_likes:
            query = query.filter(AIThread.likes >= request.min_likes)
        if request.author_username:
            query = query.join(AIThreadAuthor).filter(
                AIThreadAuthor.username.ilike(f"%{request.author_username}%"),
            )
        if request.tags:
            # Filter threads that have any of the specified tags
            for tag in request.tags:
                query = query.filter(AIThread.tags.contains([tag]))

        # Apply sorting
        sort_map = {
            SortOrder.LIKES_DESC: desc(AIThread.likes),
            SortOrder.LIKES_ASC: asc(AIThread.likes),
            SortOrder.DATE_DESC: desc(AIThread.published_at),
            SortOrder.DATE_ASC: asc(AIThread.published_at),
            SortOrder.RELEVANCE: desc(AIThread.quality_score),
        }
        query = query.order_by(sort_map.get(request.sort, desc(AIThread.likes)))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (request.page - 1) * request.page_size
        threads = query.offset(offset).limit(request.page_size).all()

        # Build summaries
        summaries = [
            ThreadSummary(
                id=t.id,
                title=t.title,
                author_username=t.author.username,
                author_display_name=t.author.display_name,
                category=t.category,
                tags=t.tags or [],
                likes=t.likes,
                post_count=t.post_count,
                published_at=t.published_at,
                status=t.status,
            )
            for t in threads
        ]

        total_pages = (total + request.page_size - 1) // request.page_size

        return ThreadListResponse(
            threads=summaries,
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
            has_next=request.page < total_pages,
            has_prev=request.page > 1,
        )

    # ========================================================================
    # Import Operations
    # ========================================================================

    async def import_compilation(self, request: BulkImportRequest) -> list[BulkImportResult]:
        """Parse and import threads from raw compilation text."""
        results = []
        threads_data = self._parse_compilation(request.content)

        for thread_data in threads_data:
            try:
                # Check if already exists
                existing = await self.get_thread_by_platform_id(thread_data["platform_post_id"])
                if existing:
                    results.append(
                        BulkImportResult(
                            platform_post_id=thread_data["platform_post_id"],
                            success=False,
                            error="Thread already exists",
                        ),
                    )
                    continue

                # Auto-categorize if requested
                if request.auto_categorize:
                    thread_data["category"] = self._categorize_thread(thread_data["full_content"])

                # Create thread
                thread_create = ThreadCreate(**thread_data)
                thread = await self.create_thread(thread_create)

                results.append(
                    BulkImportResult(
                        platform_post_id=thread_data["platform_post_id"],
                        success=True,
                        thread_id=thread.id,
                    ),
                )

            except Exception as e:
                logger.error(f"Failed to import thread: {e}")
                results.append(
                    BulkImportResult(
                        platform_post_id=thread_data.get("platform_post_id", "unknown"),
                        success=False,
                        error=str(e),
                    ),
                )

        return results

    def _parse_compilation(self, content: str) -> list[dict]:
        """Parse raw thread compilation into structured data."""
        threads = []

        # Pattern to match thread headers
        # Format: **Thread N: Author (@handle) - "Title" - Post ID: XXX - Date: XXX - Likes: N**
        header_pattern = re.compile(
            r"\*\*Thread\s+\d+:\s*"
            r"([^(]+)\s*"
            r"\(@(\w+)\)\s*-\s*"
            r'"([^"]+)"\s*-\s*'
            r"Post ID:\s*(\d+)\s*-\s*"
            r"Date:\s*([^-]+)\s*-\s*"
            r"Likes:\s*([\d,]+)\*\*",
            re.IGNORECASE,
        )

        # Split by thread headers
        sections = re.split(r"---\n+", content)

        for section in sections:
            header_match = header_pattern.search(section)
            if not header_match:
                continue

            display_name = header_match.group(1).strip()
            username = header_match.group(2).strip()
            title = header_match.group(3).strip()
            post_id = header_match.group(4).strip()
            date_str = header_match.group(5).strip()
            likes = int(header_match.group(6).replace(",", ""))

            # Parse date
            try:
                published_at = datetime.strptime(date_str, "%B %d, %Y")
            except ValueError:
                published_at = datetime.now()

            # Extract content after header
            content_start = header_match.end()
            thread_content = section[content_start:].strip()

            # Remove surrounding quotes if present
            if thread_content.startswith('"') and thread_content.endswith('"'):
                thread_content = thread_content[1:-1]

            # Parse individual posts (numbered like "1/", "2/", etc.)
            posts = self._parse_posts(thread_content, post_id)

            # Extract tags from content
            tags = self._extract_tags(thread_content)

            threads.append(
                {
                    "platform_post_id": post_id,
                    "platform": ThreadSource.IMPORT,
                    "title": title,
                    "full_content": thread_content,
                    "published_at": published_at,
                    "likes": likes,
                    "tags": tags,
                    "author": {
                        "platform_id": f"@{username}",
                        "display_name": display_name,
                        "username": username,
                        "platform": ThreadSource.TWITTER_X,
                    },
                    "posts": posts,
                },
            )

        return threads

    def _parse_posts(self, content: str, base_post_id: str) -> list[dict]:
        """Parse numbered posts from thread content."""
        posts = []

        # Match patterns like "1/", "1/3:", "1.", etc.
        post_pattern = re.compile(r"(\d+)[/.](?:\d+)?[:\s]")

        matches = list(post_pattern.finditer(content))
        if not matches:
            # Single post thread
            return [
                {
                    "platform_post_id": base_post_id,
                    "position": 1,
                    "content": content.strip(),
                    "has_code": self._has_code(content),
                    "code_language": self._detect_code_language(content),
                },
            ]

        for i, match in enumerate(matches):
            position = int(match.group(1))
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            post_content = content[start:end].strip()

            posts.append(
                {
                    "platform_post_id": f"{base_post_id}_{position}",
                    "position": position,
                    "content": post_content,
                    "has_code": self._has_code(post_content),
                    "code_language": self._detect_code_language(post_content),
                },
            )

        return posts

    def _extract_tags(self, content: str) -> list[str]:
        """Extract hashtags from content."""
        hashtags = re.findall(r"#(\w+)", content)
        return list(set(tag.lower() for tag in hashtags))

    def _has_code(self, content: str) -> bool:
        """Check if content contains code blocks."""
        return "```" in content or "def " in content or "class " in content or "import " in content

    def _detect_code_language(self, content: str) -> str | None:
        """Detect programming language from code blocks."""
        if "python" in content.lower() or "def " in content or "import " in content:
            return "python"
        if "javascript" in content.lower() or "const " in content or "let " in content:
            return "javascript"
        if "typescript" in content.lower():
            return "typescript"
        return None

    def _categorize_thread(self, content: str) -> ThreadCategory:
        """Auto-categorize thread based on content."""
        content_lower = content.lower()

        category_keywords = {
            ThreadCategory.PROMPT_ENGINEERING: [
                "prompt",
                "system prompt",
                "few-shot",
                "cot",
                "chain of thought",
            ],
            ThreadCategory.MEMORY_SYSTEMS: [
                "memory",
                "vector",
                "embedding",
                "rag",
                "retrieval",
                "pinecone",
                "chroma",
            ],
            ThreadCategory.TOOL_INTEGRATION: ["tool", "function calling", "api", "integration"],
            ThreadCategory.MULTI_AGENT: [
                "multi-agent",
                "swarm",
                "crew",
                "orchestrat",
                "collaborate",
            ],
            ThreadCategory.RAG_RETRIEVAL: ["rag", "retrieval", "knowledge base", "semantic search"],
            ThreadCategory.DEPLOYMENT: ["deploy", "production", "scale", "kubernetes", "docker"],
            ThreadCategory.EVALUATION: ["eval", "metric", "benchmark", "test", "accuracy"],
            ThreadCategory.FRAMEWORKS: ["langchain", "crewai", "autogen", "langgraph", "framework"],
            ThreadCategory.AGENT_BASICS: ["agent", "getting started", "beginner", "basic", "first"],
        }

        scores = dict.fromkeys(ThreadCategory, 0)
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    scores[category] += 1

        best_category = max(scores, key=scores.get)
        if scores[best_category] > 0:
            return best_category
        return ThreadCategory.GENERAL

    # ========================================================================
    # Export Operations
    # ========================================================================

    async def export_threads(self, request: ExportRequest) -> tuple[str, int]:
        """Export threads to specified format."""
        # Build query
        query = self.db.query(AIThread).options(
            joinedload(AIThread.author),
            joinedload(AIThread.posts) if request.include_posts else joinedload(AIThread.author),
        )

        if request.thread_ids:
            query = query.filter(AIThread.id.in_(request.thread_ids))
        if request.category:
            query = query.filter(AIThread.category == request.category)
        if request.min_likes:
            query = query.filter(AIThread.likes >= request.min_likes)

        threads = query.all()

        if request.format == ExportFormat.JSON:
            content = self._export_json(threads, request)
        elif request.format == ExportFormat.MARKDOWN:
            content = self._export_markdown(threads, request)
        elif request.format == ExportFormat.TXT:
            content = self._export_txt(threads, request)
        else:
            content = self._export_json(threads, request)

        return content, len(threads)

    def _export_json(self, threads: list[AIThread], request: ExportRequest) -> str:
        """Export threads as JSON."""
        import json

        data = []
        for thread in threads:
            thread_data = {
                "id": thread.id,
                "title": thread.title,
                "author": {
                    "username": thread.author.username,
                    "display_name": thread.author.display_name,
                },
                "category": thread.category.value if thread.category else None,
                "tags": thread.tags,
                "likes": thread.likes,
                "published_at": thread.published_at.isoformat() if thread.published_at else None,
                "content": thread.full_content,
            }

            if request.include_posts:
                thread_data["posts"] = [
                    {
                        "position": p.position,
                        "content": p.content,
                        "has_code": p.has_code,
                    }
                    for p in sorted(thread.posts, key=lambda x: x.position)
                ]

            if request.include_metadata:
                thread_data["metadata"] = thread.metadata

            data.append(thread_data)

        return json.dumps(data, indent=2, default=str)

    def _export_markdown(self, threads: list[AIThread], request: ExportRequest) -> str:
        """Export threads as Markdown."""
        lines = ["# AI Agent Threads Export\n"]
        lines.append(f"*Generated on {datetime.now().strftime('%B %d, %Y')}*\n")
        lines.append(f"*Total threads: {len(threads)}*\n\n---\n")

        for i, thread in enumerate(threads, 1):
            lines.append(f"\n## Thread {i}: {thread.title}\n")
            lines.append(f"**Author:** {thread.author.display_name} (@{thread.author.username})\n")
            lines.append(
                f"**Likes:** {thread.likes:,} | **Category:** {thread.category.value if thread.category else 'N/A'}\n",
            )
            lines.append(
                f"**Published:** {thread.published_at.strftime('%B %d, %Y') if thread.published_at else 'N/A'}\n",
            )

            if thread.tags:
                lines.append(f"**Tags:** {', '.join(thread.tags)}\n")

            lines.append("\n### Content\n")

            if request.include_posts and thread.posts:
                for post in sorted(thread.posts, key=lambda x: x.position):
                    lines.append(f"\n**{post.position}/{len(thread.posts)}:**\n")
                    lines.append(f"{post.content}\n")
            else:
                lines.append(f"{thread.full_content}\n")

            lines.append("\n---\n")

        return "".join(lines)

    def _export_txt(self, threads: list[AIThread], request: ExportRequest) -> str:
        """Export threads as plain text."""
        lines = ["AI AGENT THREADS EXPORT\n"]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n")
        lines.append(f"Total threads: {len(threads)}\n")
        lines.append("=" * 60 + "\n")

        for i, thread in enumerate(threads, 1):
            lines.append(f"\n[{i}] {thread.title}\n")
            lines.append(f"By: {thread.author.display_name} (@{thread.author.username})\n")
            lines.append(f"Likes: {thread.likes:,}\n")
            lines.append("-" * 40 + "\n")
            lines.append(f"{thread.full_content}\n")
            lines.append("=" * 60 + "\n")

        return "".join(lines)

    # ========================================================================
    # Analytics
    # ========================================================================

    async def get_analytics(self) -> ThreadAnalytics:
        """Get analytics for the thread collection."""
        total_threads = self.db.query(func.count(AIThread.id)).scalar()
        total_posts = self.db.query(func.count(AIThreadPost.id)).scalar()
        total_authors = self.db.query(func.count(AIThreadAuthor.id)).scalar()

        indexed_threads = (
            self.db.query(func.count(AIThread.id))
            .filter(AIThread.status == ThreadStatus.INDEXED)
            .scalar()
        )

        pending_threads = (
            self.db.query(func.count(AIThread.id))
            .filter(AIThread.status == ThreadStatus.PENDING)
            .scalar()
        )

        # Category distribution
        category_counts = (
            self.db.query(AIThread.category, func.count(AIThread.id))
            .group_by(AIThread.category)
            .all()
        )
        category_distribution = {
            cat.value if cat else "none": count for cat, count in category_counts
        }

        # Average metrics
        avg_likes = self.db.query(func.avg(AIThread.likes)).scalar() or 0
        avg_posts = self.db.query(func.avg(AIThread.post_count)).scalar() or 0

        # Date range
        min_date = self.db.query(func.min(AIThread.published_at)).scalar()
        max_date = self.db.query(func.max(AIThread.published_at)).scalar()

        return ThreadAnalytics(
            total_threads=total_threads,
            total_posts=total_posts,
            total_authors=total_authors,
            indexed_threads=indexed_threads,
            pending_threads=pending_threads,
            category_distribution=category_distribution,
            top_tags=[],  # TODO: Implement tag aggregation
            avg_likes=float(avg_likes),
            avg_posts_per_thread=float(avg_posts),
            date_range={"min": min_date, "max": max_date},
        )

    # ========================================================================
    # Embedding Status
    # ========================================================================

    async def mark_thread_indexed(self, thread_id: str, embedding_id: str) -> bool:
        """Mark thread as indexed with embedding reference."""
        thread = self.db.query(AIThread).filter_by(id=thread_id).first()
        if not thread:
            return False

        thread.status = ThreadStatus.INDEXED
        thread.embedding_id = embedding_id
        self.db.commit()
        return True

    async def get_unindexed_threads(self, limit: int = 100) -> list[AIThread]:
        """Get threads pending indexing."""
        return (
            self.db.query(AIThread)
            .filter(AIThread.status == ThreadStatus.PENDING)
            .limit(limit)
            .all()
        )
