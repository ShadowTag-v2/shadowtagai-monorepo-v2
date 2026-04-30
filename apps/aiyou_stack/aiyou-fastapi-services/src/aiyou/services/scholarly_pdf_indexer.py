"""Scholarly PDF Indexer - Elasticsearch-based Academic Paper Search

Indexes scholarly PDFs for full-text search, enabling "Sauron's Panorama"
knowledge base where agents can research academic papers as part of OPORD execution.

Inspired by Apertus paper: 8.6T tokens indexed with Elasticsearch 7.17
"""

import hashlib
import logging
from datetime import datetime
from io import BytesIO
from typing import Any

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None  # Will raise error at runtime if used

logger = logging.getLogger(__name__)


class ScholarlyPDFIndexer:
    """Indexes scholarly PDFs for full-text search.

    Architecture (inspired by Apertus):
    - Extract text from PDFs (PyPDF2 or pdfplumber)
    - Index in Elasticsearch with custom analyzer
    - Store metadata: title, authors, year, topics
    - Enable full-text search across all papers

    This creates a searchable knowledge base for agents to reference
    during OPORD execution, similar to how Apertus indexed 8.6T tokens.
    """

    def __init__(self, es_client=None):
        """Initialize PDF indexer.

        Args:
            es_client: Elasticsearch client (optional, uses mock if None)

        """
        self.es = es_client  # TODO: Connect to actual Elasticsearch
        self.index_name = "scholarly_pdfs"

    def index_pdf(
        self,
        pdf_content: bytes,
        title: str,
        authors: list[str],
        year: int,
        topics: list[str] | None = None,
        abstract: str | None = None,
    ) -> dict[str, Any]:
        """Index a scholarly PDF for search.

        Args:
            pdf_content: Raw PDF bytes
            title: Paper title
            authors: List of author names
            year: Publication year
            topics: Tags/keywords
            abstract: Paper abstract

        Returns:
            Indexing result with doc_id, page_count, index_size

        """
        if PdfReader is None:
            raise ImportError("PyPDF2 not installed. Run: pip install PyPDF2")

        # Extract text from PDF
        pages = self._extract_text_from_pdf(pdf_content)

        # Generate document ID (SHA-256 of content)
        doc_id = hashlib.sha256(pdf_content).hexdigest()[:16]

        # Prepare document for indexing
        doc = {
            "doc_id": doc_id,
            "title": title,
            "authors": authors,
            "year": year,
            "topics": topics or [],
            "abstract": abstract or "",
            "page_count": len(pages),
            "indexed_at": datetime.utcnow().isoformat(),
            # Full text for search (all pages concatenated)
            "full_text": "\n\n".join([p["text"] for p in pages]),
            # Pages stored separately for excerpt extraction
            "pages": pages,
        }

        # Index in Elasticsearch (or mock)
        if self.es:
            self.es.index(index=self.index_name, id=doc_id, body=doc)
            logger.info(f"Indexed PDF '{title}' ({len(pages)} pages) to Elasticsearch")
        else:
            # Mock mode: just log
            logger.info(f"Mock indexed PDF '{title}' ({len(pages)} pages)")

        return {
            "doc_id": doc_id,
            "title": title,
            "pages": len(pages),
            "index_size_bytes": len(pdf_content),
        }

    def search_pdfs(
        self,
        query: str,
        authors: list[str] | None = None,
        year_range: tuple | None = None,
        topics: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search indexed PDFs with full-text and filters.

        Uses Elasticsearch match_phrase queries with configurable slop
        (similar to Apertus implementation).

        Args:
            query: Full-text search query
            authors: Filter by authors
            year_range: Filter by year range (start, end)
            topics: Filter by topics
            limit: Max results

        Returns:
            List of matching papers with excerpts and scores

        """
        if self.es:
            # Build Elasticsearch query
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "match_phrase": {
                                    "full_text": {
                                        "query": query,
                                        "slop": 2,  # Allow 2-word gaps (Apertus pattern)
                                    },
                                },
                            },
                        ],
                        "filter": [],
                    },
                },
                "highlight": {
                    "fields": {"full_text": {"fragment_size": 150, "number_of_fragments": 3}},
                },
                "size": limit,
            }

            # Add filters
            if authors:
                es_query["query"]["bool"]["filter"].append({"terms": {"authors": authors}})

            if year_range:
                es_query["query"]["bool"]["filter"].append(
                    {"range": {"year": {"gte": year_range[0], "lte": year_range[1]}}},
                )

            if topics:
                es_query["query"]["bool"]["filter"].append({"terms": {"topics": topics}})

            # Execute search
            results = self.es.search(index=self.index_name, body=es_query)

            # Parse results
            papers = []
            for hit in results["hits"]["hits"]:
                source = hit["_source"]
                papers.append(
                    {
                        "doc_id": source["doc_id"],
                        "title": source["title"],
                        "authors": source["authors"],
                        "year": source["year"],
                        "topics": source["topics"],
                        "score": hit["_score"],
                        "excerpts": hit.get("highlight", {}).get("full_text", []),
                        "page_count": source["page_count"],
                    },
                )

            logger.info(f"Search for '{query}' returned {len(papers)} papers")
            return papers

        # Mock mode: return example
        logger.info(f"Mock search for '{query}'")
        return [
            {
                "doc_id": "mock_0001",
                "title": "Apertus LLM Training Data Indexing (Mock)",
                "authors": ["Researcher A", "Researcher B"],
                "year": 2024,
                "topics": ["elasticsearch", "llm", "indexing"],
                "score": 10.5,
                "excerpts": [
                    f"...{query} appears in the context of large-scale indexing...",
                    f"...performance tuning for {query} workloads...",
                ],
                "page_count": 15,
            },
        ]

    def _extract_text_from_pdf(self, pdf_content: bytes) -> list[dict[str, str]]:
        """Extract text from PDF using PyPDF2.

        Returns list of pages with text and page number.

        Uses custom analyzer (similar to Apertus web_content_analyzer):
        - Strip formatting
        - Tokenize
        - Lowercase
        - ASCII fold
        """
        try:
            pdf_file = BytesIO(pdf_content)
            reader = PdfReader(pdf_file)

            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text()

                # Clean text (basic normalization)
                text = self._normalize_text(text)

                pages.append({"page_number": i + 1, "text": text})

            return pages

        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            return []

    def _normalize_text(self, text: str) -> str:
        """Normalize text for indexing.

        Applies transformations similar to Apertus web_content_analyzer:
        - Remove excess whitespace
        - Lowercase (for case-insensitive search)
        - ASCII folding (é → e, ñ → n, etc.)
        """
        # Remove excess whitespace
        text = " ".join(text.split())

        # Lowercase
        text = text.lower()

        # ASCII folding (basic - full implementation would use unidecode)
        # For now, just handle common cases
        replacements = {
            "é": "e",
            "è": "e",
            "ê": "e",
            "ë": "e",
            "á": "a",
            "à": "a",
            "â": "a",
            "ä": "a",
            "ñ": "n",
            "ü": "u",
            "ù": "u",
            "ú": "u",
            "ö": "o",
            "ò": "o",
            "ó": "o",
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    def create_index_mapping(self) -> dict:
        """Create Elasticsearch index mapping.

        Defines custom analyzer similar to Apertus:
        - Tokenization
        - Lowercase filter
        - ASCII folding filter
        - Stop words filter
        """
        return {
            "mappings": {
                "properties": {
                    "doc_id": {"type": "keyword"},
                    "title": {"type": "text", "analyzer": "scholarly_analyzer"},
                    "authors": {"type": "keyword"},
                    "year": {"type": "integer"},
                    "topics": {"type": "keyword"},
                    "abstract": {"type": "text", "analyzer": "scholarly_analyzer"},
                    "full_text": {"type": "text", "analyzer": "scholarly_analyzer"},
                    "page_count": {"type": "integer"},
                    "indexed_at": {"type": "date"},
                    # Pages stored as nested objects
                    "pages": {
                        "type": "nested",
                        "properties": {
                            "page_number": {"type": "integer"},
                            "text": {"type": "text", "analyzer": "scholarly_analyzer"},
                        },
                    },
                },
            },
            "settings": {
                "analysis": {
                    "analyzer": {
                        "scholarly_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding", "stop"],
                        },
                    },
                },
            },
        }


# ==================== How This Enables Scholarly PDF Search ====================

"""
CONNECTING THE DOTS: Elasticsearch → Scholarly PDF Search

The Apertus paper showed us that Elasticsearch can index 8.6 TRILLION tokens
with ~10k docs/sec throughput and <100ms p99 query latency.

Our ScholarlyPDFIndexer uses the SAME ARCHITECTURE:

1. PDF Upload → Text Extraction (PyPDF2)
2. Normalization (lowercase, ASCII folding, tokenization)
3. Elasticsearch Indexing (custom analyzer)
4. Full-Text Search (match_phrase with slop=2)

AGENT WORKFLOW INTEGRATION:

When an agent receives an OPORD like:

  OPORD 00042 - Research ERC-8004 Reputation Standards

  MISSION:
    - WHO: agent_123 (PhD Computer Science)
    - WHAT: Survey academic papers on decentralized reputation systems
    - WHERE: Context Index + Scholarly PDF database
    - WHY: Inform ERC-8004 implementation design

The agent can now:

1. Search indexed PDFs:
   POST /api/v1/atomic-chat/scholarly-pdfs/search
   {
     "query": "decentralized reputation blockchain",
     "topics": ["blockchain", "reputation"],
     "year_range": [2020, 2025]
   }

2. Get relevant excerpts with highlights:
   Returns papers ranked by relevance, with excerpt highlighting
   showing exactly where the query terms appear.

3. Use findings in OPORD execution:
   Agent incorporates academic knowledge into implementation,
   logs references to Context Index for audit trail.

REVENUE OPPORTUNITY:

This creates "Sauron's Panorama" - a searchable knowledge base that:
- Indexes internal documentation (OPORDs, code, decisions)
- Indexes external knowledge (academic papers, technical specs)
- Enables AI agents to research autonomously

Pricing tier: "Enterprise Knowledge Base"
- Basic: 100 PDFs indexed
- Standard: 1,000 PDFs (+$200/month)
- Enterprise: Unlimited PDFs + custom taxonomies (+$1,000/month)

Target customers: Research teams, law firms, compliance departments
that need AI agents to autonomously research complex topics.
"""
