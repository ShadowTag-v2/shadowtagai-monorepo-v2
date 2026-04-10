"""
Research Query Router

Routes research queries to appropriate sources based on keyword detection
and intent analysis. Determines which combination of Drive, Gmail, and Web
searches to execute.

Integration:
- Used by intent-classifier to detect RESEARCH mode
- Feeds source selection to research_pipeline
"""

from dataclasses import dataclass
from enum import Enum


class ResearchSourceType(Enum):
    """Available research source types."""

    DRIVE = "drive"
    GMAIL = "gmail"
    WEB = "web"
    MEMORY = "memory"
    CODEBASE = "codebase"


@dataclass
class ResearchIntent:
    """Detected research intent with source recommendations."""

    query: str
    recommended_sources: set[ResearchSourceType]
    confidence: float
    is_multi_source: bool
    intent_type: str  # "internal", "external", "comprehensive"
    extracted_topic: str


class ResearchQueryRouter:
    """
    Routes research queries to appropriate sources.

    Uses keyword detection and heuristics to determine:
    - Which sources to query (Drive, Gmail, Web, Memory, Codebase)
    - Whether to use concurrent or sequential execution
    - Priority order for sources

    Example:
        router = ResearchQueryRouter()
        intent = router.route("What do we know about competitor pricing?")
        # intent.recommended_sources = {DRIVE, GMAIL, WEB}
        # intent.intent_type = "comprehensive"
    """

    # Keywords suggesting INTERNAL sources needed
    INTERNAL_KEYWORDS = {
        "our",
        "we",
        "us",
        "internal",
        "company",
        "team",
        "decision",
        "decided",
        "agreed",
        "meeting",
        "discussion",
        "document",
        "doc",
        "email",
        "thread",
        "conversation",
        "proposal",
        "spec",
        "specification",
        "plan",
        "strategy",
    }

    # Keywords suggesting EXTERNAL sources needed
    EXTERNAL_KEYWORDS = {
        "competitor",
        "competition",
        "market",
        "industry",
        "trend",
        "public",
        "news",
        "article",
        "research",
        "paper",
        "study",
        "comparison",
        "benchmark",
        "best practice",
        "external",
        "current",
        "latest",
        "recent",
        "2024",
        "2025",
    }

    # Keywords that trigger EMAIL specifically
    EMAIL_KEYWORDS = {
        "email",
        "thread",
        "sent",
        "received",
        "mail",
        "from:",
        "to:",
        "subject:",
        "replied",
        "forwarded",
    }

    # Keywords that trigger DRIVE specifically
    DRIVE_KEYWORDS = {
        "document",
        "doc",
        "spreadsheet",
        "sheet",
        "presentation",
        "slide",
        "file",
        "gdoc",
        "gsheet",
        "folder",
    }

    # Keywords that trigger CODEBASE search
    CODEBASE_KEYWORDS = {
        "code",
        "implementation",
        "function",
        "class",
        "api",
        "endpoint",
        "module",
        "package",
        "repository",
        "repo",
    }

    # High-confidence research trigger keywords
    RESEARCH_TRIGGERS = {
        "research",
        "investigate",
        "deep dive",
        "analyze",
        "what do we know",
        "gather information",
        "look into",
        "compare",
        "evaluate",
        "prior art",
        "competitive analysis",
    }

    def route(self, query: str) -> ResearchIntent:
        """
        Determine which sources to query based on input.

        Args:
            query: User's research query

        Returns:
            ResearchIntent with recommended sources and metadata
        """
        query_lower = query.lower()
        sources: set[ResearchSourceType] = set()

        # Detect intent type
        has_internal = any(kw in query_lower for kw in self.INTERNAL_KEYWORDS)
        has_external = any(kw in query_lower for kw in self.EXTERNAL_KEYWORDS)

        # Specific source detection
        if any(kw in query_lower for kw in self.EMAIL_KEYWORDS):
            sources.add(ResearchSourceType.GMAIL)

        if any(kw in query_lower for kw in self.DRIVE_KEYWORDS):
            sources.add(ResearchSourceType.DRIVE)

        if any(kw in query_lower for kw in self.CODEBASE_KEYWORDS):
            sources.add(ResearchSourceType.CODEBASE)

        # General routing based on intent
        if has_internal and not sources:
            sources.add(ResearchSourceType.DRIVE)
            sources.add(ResearchSourceType.GMAIL)
            sources.add(ResearchSourceType.MEMORY)

        if has_external:
            sources.add(ResearchSourceType.WEB)

        # Default: comprehensive search if no specific signals
        if not sources:
            sources = {
                ResearchSourceType.DRIVE,
                ResearchSourceType.GMAIL,
                ResearchSourceType.WEB,
                ResearchSourceType.MEMORY,
            }

        # Determine intent type
        if has_internal and has_external:
            intent_type = "comprehensive"
        elif has_internal:
            intent_type = "internal"
        elif has_external:
            intent_type = "external"
        else:
            intent_type = "comprehensive"

        # Calculate confidence
        has_research_trigger = any(trigger in query_lower for trigger in self.RESEARCH_TRIGGERS)
        confidence = (
            0.95 if has_research_trigger else (0.85 if (has_internal or has_external) else 0.70)
        )

        # Extract topic (simple heuristic - remove trigger words)
        topic = self._extract_topic(query)

        return ResearchIntent(
            query=query,
            recommended_sources=sources,
            confidence=confidence,
            is_multi_source=len(sources) > 1,
            intent_type=intent_type,
            extracted_topic=topic,
        )

    def is_research_query(self, query: str) -> bool:
        """
        Quick check if query is likely a research query.

        Args:
            query: User input

        Returns:
            True if research intent detected
        """
        query_lower = query.lower()

        # Check for explicit research triggers
        if any(trigger in query_lower for trigger in self.RESEARCH_TRIGGERS):
            return True

        # Check for question patterns that suggest research
        question_patterns = [
            "what do we know",
            "what does",
            "how do we",
            "tell me about",
            "find out about",
            "looking for information",
            "need to understand",
        ]
        if any(pattern in query_lower for pattern in question_patterns):
            return True

        # Check for combination of internal + external keywords
        has_internal = any(kw in query_lower for kw in self.INTERNAL_KEYWORDS)
        has_external = any(kw in query_lower for kw in self.EXTERNAL_KEYWORDS)
        return bool(has_internal and has_external)

    def _extract_topic(self, query: str) -> str:
        """
        Extract the main topic from a research query.

        Simple heuristic: remove common trigger words and return remainder.
        """
        # Words to remove
        remove_words = {
            "research",
            "investigate",
            "analyze",
            "find",
            "look",
            "into",
            "about",
            "for",
            "the",
            "a",
            "an",
            "our",
            "we",
            "what",
            "do",
            "know",
            "gather",
            "information",
            "on",
            "can",
            "you",
            "please",
            "help",
            "me",
            "deep",
            "dive",
            "compare",
            "evaluate",
        }

        words = query.lower().split()
        topic_words = [w for w in words if w not in remove_words]

        return " ".join(topic_words) if topic_words else query

    def get_source_priority(self, sources: set[ResearchSourceType]) -> list[ResearchSourceType]:
        """
        Get sources in priority order for sequential fallback.

        Args:
            sources: Set of sources to query

        Returns:
            List in priority order (most important first)
        """
        priority_order = [
            ResearchSourceType.DRIVE,  # Internal docs first
            ResearchSourceType.GMAIL,  # Email decisions
            ResearchSourceType.MEMORY,  # Prior context
            ResearchSourceType.WEB,  # External info
            ResearchSourceType.CODEBASE,  # Code references
        ]

        return [s for s in priority_order if s in sources]


# Singleton instance for easy import
router = ResearchQueryRouter()


def detect_research_intent(query: str) -> ResearchIntent:
    """
    Convenience function to detect research intent.

    Args:
        query: User input

    Returns:
        ResearchIntent with source recommendations
    """
    return router.route(query)


def is_research_query(query: str) -> bool:
    """
    Convenience function to check if query is research-related.

    Args:
        query: User input

    Returns:
        True if research intent detected
    """
    return router.is_research_query(query)
