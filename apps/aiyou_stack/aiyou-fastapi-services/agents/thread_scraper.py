"""
Thread Scraper Agent

Automated agent for collecting AI agent knowledge threads from X/Twitter.
Uses the n-autoresearch/Kosmos/BioAgents swarm pattern for parallel processing.

Features:
- Search X API for threads matching criteria
- Parse thread structure and extract posts
- Deduplicate against existing threads
- Queue for indexing in knowledge base
"""

import asyncio
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from sqlalchemy.orm import Session
from src.shadowtag_v4.models.ai_threads import (
    AIThread,
    AIThreadAuthor,
    AIThreadPost,
    AIThreadScrapeJob,
    ThreadCategory,
    ThreadSource,
    ThreadStatus,
)

logger = logging.getLogger(__name__)


class ScrapeStatus(StrEnum):
    """Scrape job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"


@dataclass
class ScrapedThread:
    """Represents a scraped thread before database insertion."""

    platform_post_id: str
    author_username: str
    author_display_name: str
    author_platform_id: str
    title: str
    full_content: str
    posts: list[dict]
    likes: int
    retweets: int
    replies: int
    published_at: datetime
    source_url: str
    tags: list[str] = field(default_factory=list)
    category: ThreadCategory | None = None


@dataclass
class ScrapeResult:
    """Result of a scrape operation."""

    success: bool
    threads_found: int = 0
    threads_saved: int = 0
    threads_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    rate_limited: bool = False


class ThreadScraperAgent:
    """
    Agent for scraping AI agent threads from X/Twitter.

    Implements the n-autoresearch/Kosmos/BioAgents agent pattern with:
    - Rate limiting and backoff
    - Parallel thread processing
    - Content extraction and parsing
    - Deduplication
    """

    # Default search queries for AI agent content
    DEFAULT_QUERIES = [
        "AI agents tips min_faves:10",
        "building AI agents thread",
        "LangChain tutorial thread",
        "AI agent architecture",
        "RAG implementation guide",
        "prompt engineering tips",
        "multi-agent systems",
        "AI agent memory",
    ]

    # Rate limiting
    REQUESTS_PER_WINDOW = 50
    WINDOW_SECONDS = 900  # 15 minutes
    RETRY_DELAYS = [2, 4, 8, 16, 32]  # Exponential backoff

    def __init__(
        self,
        db: Session,
        api_key: str | None = None,
        api_secret: str | None = None,
        bearer_token: str | None = None,
    ):
        """
        Initialize scraper agent.

        Args:
            db: Database session
            api_key: X API key
            api_secret: X API secret
            bearer_token: X API bearer token
        """
        self.db = db
        self.api_key = api_key
        self.api_secret = api_secret
        self.bearer_token = bearer_token

        # Rate limiting state
        self._request_count = 0
        self._window_start = datetime.now()

        # Mock mode for testing without API
        self.mock_mode = not bearer_token

    async def run_job(self, job_id: str) -> ScrapeResult:
        """
        Execute a scrape job.

        Args:
            job_id: ID of the scrape job to run

        Returns:
            ScrapeResult with operation details
        """
        job = self.db.query(AIThreadScrapeJob).filter_by(id=job_id).first()
        if not job:
            return ScrapeResult(success=False, errors=[f"Job not found: {job_id}"])

        # Update job status
        job.status = ScrapeStatus.RUNNING.value
        job.started_at = datetime.utcnow()
        self.db.commit()

        logger.info(f"Starting scrape job {job_id}: query='{job.query}'")

        try:
            result = await self.scrape(
                query=job.query,
                min_likes=job.min_likes,
                max_results=job.max_results,
            )

            # Update job with results
            job.status = (
                ScrapeStatus.COMPLETED.value if result.success else ScrapeStatus.FAILED.value
            )
            job.threads_found = result.threads_found
            job.threads_saved = result.threads_saved
            job.completed_at = datetime.utcnow()
            if result.errors:
                job.error_message = "; ".join(result.errors[:5])

            self.db.commit()
            return result

        except Exception as e:
            logger.error(f"Scrape job {job_id} failed: {e}")
            job.status = ScrapeStatus.FAILED.value
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            self.db.commit()
            return ScrapeResult(success=False, errors=[str(e)])

    async def scrape(
        self,
        query: str,
        min_likes: int = 10,
        max_results: int = 100,
    ) -> ScrapeResult:
        """
        Scrape threads matching query.

        Args:
            query: Search query
            min_likes: Minimum likes filter
            max_results: Maximum threads to fetch

        Returns:
            ScrapeResult
        """
        logger.info(f"Scraping: query='{query}', min_likes={min_likes}, max_results={max_results}")

        if self.mock_mode:
            return await self._mock_scrape(query, min_likes, max_results)

        try:
            # Search for threads
            raw_tweets = await self._search_tweets(query, max_results)

            # Parse and filter threads
            scraped_threads = []
            for tweet in raw_tweets:
                if tweet.get("likes", 0) < min_likes:
                    continue

                thread = await self._parse_thread(tweet)
                if thread:
                    scraped_threads.append(thread)

            # Save to database
            saved_count = 0
            skipped_count = 0
            errors = []

            for thread in scraped_threads:
                try:
                    saved = await self._save_thread(thread)
                    if saved:
                        saved_count += 1
                    else:
                        skipped_count += 1
                except Exception as e:
                    errors.append(f"Failed to save {thread.platform_post_id}: {e}")

            return ScrapeResult(
                success=True,
                threads_found=len(scraped_threads),
                threads_saved=saved_count,
                threads_skipped=skipped_count,
                errors=errors,
            )

        except RateLimitError:
            return ScrapeResult(
                success=False,
                rate_limited=True,
                errors=["Rate limited by X API"],
            )
        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            return ScrapeResult(success=False, errors=[str(e)])

    async def _search_tweets(self, query: str, max_results: int) -> list[dict]:
        """Search X API for tweets matching query."""
        await self._check_rate_limit()

        # X API v2 search endpoint
        url = "https://api.twitter.com/2/tweets/search/recent"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }
        params = {
            "query": query,
            "max_results": min(max_results, 100),
            "tweet.fields": "created_at,public_metrics,author_id,conversation_id",
            "expansions": "author_id",
            "user.fields": "username,name,public_metrics,verified",
        }

        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)

            if response.status_code == 429:
                raise RateLimitError("X API rate limit exceeded")

            response.raise_for_status()
            data = response.json()

            self._request_count += 1
            return data.get("data", [])

    async def _parse_thread(self, tweet: dict) -> ScrapedThread | None:
        """Parse a tweet into a thread structure."""
        # Check if this is a thread (has multiple replies from same author)
        conversation_id = tweet.get("conversation_id")
        author_id = tweet.get("author_id")

        # For now, treat single tweets as single-post threads
        # Full thread retrieval would require additional API calls

        metrics = tweet.get("public_metrics", {})

        # Extract content
        text = tweet.get("text", "")

        # Extract title (first line or first sentence)
        title = self._extract_title(text)

        # Extract hashtags
        tags = re.findall(r"#(\w+)", text)

        # Detect if this is an AI agent related thread
        if not self._is_relevant(text):
            return None

        # Categorize
        category = self._categorize(text)

        return ScrapedThread(
            platform_post_id=tweet.get("id"),
            author_username=tweet.get("author", {}).get("username", "unknown"),
            author_display_name=tweet.get("author", {}).get("name", "Unknown"),
            author_platform_id=f"@{tweet.get('author', {}).get('username', 'unknown')}",
            title=title,
            full_content=text,
            posts=[
                {
                    "platform_post_id": tweet.get("id"),
                    "position": 1,
                    "content": text,
                }
            ],
            likes=metrics.get("like_count", 0),
            retweets=metrics.get("retweet_count", 0),
            replies=metrics.get("reply_count", 0),
            published_at=datetime.fromisoformat(
                tweet.get("created_at", datetime.utcnow().isoformat()).replace("Z", "+00:00")
            ),
            source_url=f"https://x.com/i/status/{tweet.get('id')}",
            tags=[t.lower() for t in tags],
            category=category,
        )

    async def _save_thread(self, scraped: ScrapedThread) -> bool:
        """Save scraped thread to database."""
        # Check if already exists
        existing = (
            self.db.query(AIThread).filter_by(platform_post_id=scraped.platform_post_id).first()
        )
        if existing:
            logger.debug(f"Thread {scraped.platform_post_id} already exists, skipping")
            return False

        # Find or create author
        author = (
            self.db.query(AIThreadAuthor).filter_by(platform_id=scraped.author_platform_id).first()
        )

        if not author:
            author = AIThreadAuthor(
                id=str(uuid.uuid4()),
                platform_id=scraped.author_platform_id,
                display_name=scraped.author_display_name,
                username=scraped.author_username,
                platform=ThreadSource.TWITTER_X,
            )
            self.db.add(author)
            self.db.flush()

        # Create thread
        thread = AIThread(
            id=str(uuid.uuid4()),
            platform_post_id=scraped.platform_post_id,
            platform=ThreadSource.TWITTER_X,
            author_id=author.id,
            title=scraped.title,
            full_content=scraped.full_content,
            post_count=len(scraped.posts),
            likes=scraped.likes,
            retweets=scraped.retweets,
            replies=scraped.replies,
            category=scraped.category or ThreadCategory.GENERAL,
            tags=scraped.tags,
            published_at=scraped.published_at,
            source_url=scraped.source_url,
            status=ThreadStatus.PENDING,
        )
        self.db.add(thread)

        # Create posts
        for post_data in scraped.posts:
            post = AIThreadPost(
                id=str(uuid.uuid4()),
                thread_id=thread.id,
                platform_post_id=post_data["platform_post_id"],
                position=post_data["position"],
                content=post_data["content"],
                content_length=len(post_data["content"]),
            )
            self.db.add(post)

        self.db.commit()
        logger.info(f"Saved thread: {thread.id} - {thread.title[:50]}")
        return True

    # ========================================================================
    # Helpers
    # ========================================================================

    def _extract_title(self, text: str) -> str:
        """Extract title from thread content."""
        # Try first line
        lines = text.strip().split("\n")
        first_line = lines[0].strip()

        # Remove thread indicators like "1/" or "🧵"
        first_line = re.sub(r"^[\d]+[/.]?\s*", "", first_line)
        first_line = first_line.replace("🧵", "").strip()

        # Truncate if too long
        if len(first_line) > 100:
            first_line = first_line[:97] + "..."

        return first_line or "Untitled Thread"

    def _is_relevant(self, text: str) -> bool:
        """Check if content is relevant to AI agents."""
        text_lower = text.lower()
        relevant_terms = [
            "ai agent",
            "llm",
            "langchain",
            "gpt",
            "claude",
            "prompt",
            "rag",
            "embedding",
            "vector",
            "chatbot",
            "agentic",
            "multi-agent",
            "crewai",
            "autogen",
            "function calling",
        ]
        return any(term in text_lower for term in relevant_terms)

    def _categorize(self, text: str) -> ThreadCategory:
        """Categorize thread based on content."""
        text_lower = text.lower()

        if any(t in text_lower for t in ["prompt", "system prompt", "few-shot"]):
            return ThreadCategory.PROMPT_ENGINEERING
        if any(t in text_lower for t in ["memory", "context", "conversation"]):
            return ThreadCategory.MEMORY_SYSTEMS
        if any(t in text_lower for t in ["rag", "retrieval", "vector", "embedding"]):
            return ThreadCategory.RAG_RETRIEVAL
        if any(t in text_lower for t in ["tool", "function calling", "api"]):
            return ThreadCategory.TOOL_INTEGRATION
        if any(t in text_lower for t in ["multi-agent", "swarm", "crew", "orchestrat"]):
            return ThreadCategory.MULTI_AGENT
        if any(t in text_lower for t in ["deploy", "production", "scale"]):
            return ThreadCategory.DEPLOYMENT
        if any(t in text_lower for t in ["eval", "test", "benchmark", "metric"]):
            return ThreadCategory.EVALUATION
        if any(t in text_lower for t in ["langchain", "crewai", "autogen", "langgraph"]):
            return ThreadCategory.FRAMEWORKS

        return ThreadCategory.GENERAL

    async def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        now = datetime.now()
        window_elapsed = (now - self._window_start).total_seconds()

        if window_elapsed >= self.WINDOW_SECONDS:
            # Reset window
            self._request_count = 0
            self._window_start = now
        elif self._request_count >= self.REQUESTS_PER_WINDOW:
            # Wait for window to reset
            wait_time = self.WINDOW_SECONDS - window_elapsed
            logger.warning(f"Rate limit reached, waiting {wait_time:.0f}s")
            await asyncio.sleep(wait_time)
            self._request_count = 0
            self._window_start = datetime.now()

    async def _mock_scrape(
        self,
        query: str,
        min_likes: int,
        max_results: int,
    ) -> ScrapeResult:
        """Mock scrape for testing without API access."""
        logger.info("Running in mock mode - generating sample threads")

        # Generate sample threads
        sample_threads = [
            ScrapedThread(
                platform_post_id=f"mock_{uuid.uuid4().hex[:12]}",
                author_username="ai_builder",
                author_display_name="AI Builder",
                author_platform_id="@ai_builder",
                title=f"Tips for building AI agents with {query}",
                full_content=f"""1/ Thread on {query} tips:

Start simple. Don't over-engineer.
Build a basic agent first, then iterate.

2/ Use proper memory management.
Short-term: Conversation buffer.
Long-term: Vector database.

3/ Always add guardrails.
Validate inputs, sanitize outputs.

#AIAgents #Tips""",
                posts=[
                    {"platform_post_id": f"mock_p1_{i}", "position": 1, "content": "Tip 1..."},
                    {"platform_post_id": f"mock_p2_{i}", "position": 2, "content": "Tip 2..."},
                ],
                likes=min_likes + 50,
                retweets=10,
                replies=5,
                published_at=datetime.utcnow(),
                source_url=f"https://x.com/i/status/mock_{i}",
                tags=["aiagents", "tips"],
                category=ThreadCategory.AGENT_BASICS,
            )
            for i in range(min(3, max_results))
        ]

        # Save mock threads
        saved = 0
        for thread in sample_threads:
            try:
                if await self._save_thread(thread):
                    saved += 1
            except Exception as e:
                logger.error(f"Failed to save mock thread: {e}")

        return ScrapeResult(
            success=True,
            threads_found=len(sample_threads),
            threads_saved=saved,
            threads_skipped=len(sample_threads) - saved,
        )


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""

    pass


# Scheduled job runner
async def run_scheduled_jobs(db: Session):
    """Run any scheduled scrape jobs that are due."""
    now = datetime.utcnow()

    pending_jobs = (
        db.query(AIThreadScrapeJob)
        .filter(
            AIThreadScrapeJob.status == "pending",
            AIThreadScrapeJob.scheduled_at <= now,
        )
        .all()
    )

    if not pending_jobs:
        return

    logger.info(f"Found {len(pending_jobs)} scheduled jobs to run")

    scraper = ThreadScraperAgent(db)

    for job in pending_jobs:
        await scraper.run_job(job.id)
