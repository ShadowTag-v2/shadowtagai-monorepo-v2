"""
Training Data Safety Indexer
Based on: Apertus LLM Training Data Indexing Research (arxiv:2510.09471v1)

PURPOSE:
Full-text index over training/inference data for safety auditing:
- Toxicity detection (Weaponized Words, LDNOOBW)
- Chemical/weapons content detection
- PII exposure scanning
- Multilingual safety coverage

ARCHITECTURE:
- Elasticsearch 7.17+ backend (Arm64 compatible)
- Parquet streaming for large corpora
- Custom web_content_analyzer (HTML strip, tokenize, lowercase, ASCII-fold)
- match_phrase queries with configurable slop

PERFORMANCE TARGETS (from paper):
- ~10k docs/sec (English, educational)
- ~600 docs/sec (multilingual)
- Index overhead: 1.1-1.3x raw data
- Query: practical even for 300-word phrases

INTEGRATION:
- ShadowTag provenance verification
- Judge #6 content classification
- Kernel Chain audit trails
"""

import json
import hashlib
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Set, AsyncIterator
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SafetyCategory(Enum):
    """Safety categories from Apertus research"""

    WEAPONIZED_WORDS = "weaponized_words"  # Multilingual slurs/toxic terms
    LDNOOBW = "ldnoobw"  # Dirty/naughty/obscene words (28 languages)
    CHEMICAL_WEAPONS = "chemical_weapons"  # Ledgard's agents list
    PII = "pii"  # Personal identifiable information
    COPYRIGHTED = "copyrighted"  # Known copyrighted content
    CSAM = "csam"  # Child safety (immediate escalation)
    DISINFORMATION = "disinformation"  # Known false claims


@dataclass
class SafetyHit:
    """A single safety match in content"""

    category: SafetyCategory
    term: str
    context: str  # 50 chars before/after
    position: int
    language: str
    severity: float  # 0.0-1.0
    requires_review: bool = False


@dataclass
class SafetyScanResult:
    """Result of scanning a document"""

    doc_id: str
    doc_hash: str  # SHA-256
    scanned_at: datetime
    hits: List[SafetyHit] = field(default_factory=list)
    total_tokens: int = 0
    languages_detected: Set[str] = field(default_factory=set)

    @property
    def is_clean(self) -> bool:
        return len(self.hits) == 0

    @property
    def max_severity(self) -> float:
        if not self.hits:
            return 0.0
        return max(h.severity for h in self.hits)

    @property
    def requires_immediate_review(self) -> bool:
        return any(h.category == SafetyCategory.CSAM for h in self.hits)


class SafetyLexicon:
    """
    Multilingual safety term lexicons.

    Based on:
    - Weaponized Words (restricted, multilingual)
    - LDNOOBW (28 languages)
    - Ledgard's Laboratory History (chemical weapons)
    """

    def __init__(self):
        self._lexicons: Dict[SafetyCategory, Dict[str, Set[str]]] = {}
        self._load_lexicons()

    def _load_lexicons(self):
        """Load lexicon files (stub - would load from secure storage)"""
        # Chemical weapons terms from paper
        self._lexicons[SafetyCategory.CHEMICAL_WEAPONS] = {
            "en": {
                "phosgene",
                "sulfur mustard",
                "nitrogen mustard",
                "sarin",
                "tabun",
                "vx",
                "novichok",
                "hydrogen cyanide",
                "cyanogen chloride",
                "chloropicrin",
                "bromopicrin",
                "adamsite",
                "lewisite",
                "ricin",
                "abrin",
            },
            "de": {"senfgas", "phosgen", "blausäure"},
            "fr": {"gaz moutarde", "phosgène", "acide cyanhydrique"},
        }

        # Placeholder for other lexicons (would be loaded securely)
        self._lexicons[SafetyCategory.WEAPONIZED_WORDS] = {"en": set()}
        self._lexicons[SafetyCategory.LDNOOBW] = {"en": set()}
        self._lexicons[SafetyCategory.PII] = {"en": set()}

    def get_terms(self, category: SafetyCategory, language: str = "en") -> Set[str]:
        """Get terms for a category and language"""
        return self._lexicons.get(category, {}).get(language, set())

    def all_languages(self, category: SafetyCategory) -> Set[str]:
        """Get all languages available for a category"""
        return set(self._lexicons.get(category, {}).keys())


class TrainingDataIndexer:
    """
    Full-text indexer for training data safety auditing.

    Elasticsearch configuration (from Apertus paper):
    - Custom analyzer: web_content_analyzer
    - HTML stripping, tokenization, lowercasing, ASCII-folding
    - match_phrase with configurable slop for fuzzy matching
    - Parallel bulk indexing with tuned parameters

    Performance tuning:
    - Thread count <= CPU cores
    - Chunk size balanced for memory/timeout
    - Queue size for throughput smoothing
    - ~50 µs/doc storage latency = ~10k docs/sec theoretical max
    """

    def __init__(
        self,
        es_host: str = "localhost",
        es_port: int = 9200,
        index_name: str = "pnkln_training_safety",
    ):
        self.es_host = es_host
        self.es_port = es_port
        self.index_name = index_name
        self.lexicon = SafetyLexicon()
        self._es_client = None

        # Performance config (from paper Table 4)
        self.bulk_config = {
            "thread_count": 4,  # <= CPU cores
            "chunk_size": 500,
            "max_chunk_bytes": 100 * 1024 * 1024,  # 100MB
            "queue_size": 4,
        }

    async def connect(self):
        """Connect to Elasticsearch"""
        try:
            from elasticsearch import AsyncElasticsearch

            self._es_client = AsyncElasticsearch(
                [f"http://{self.es_host}:{self.es_port}"],
                # Arm64/HPC compatibility settings
                http_compress=True,
                retry_on_timeout=True,
            )
            logger.info(f"Connected to Elasticsearch at {self.es_host}:{self.es_port}")
        except ImportError:
            logger.warning("Elasticsearch not installed, using mock mode")
            self._es_client = None

    async def create_index(self):
        """Create index with safety-optimized mappings"""
        mappings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "web_content_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding", "stop"],
                            "char_filter": ["html_strip"],
                        }
                    }
                },
            },
            "mappings": {
                "properties": {
                    "content": {"type": "text", "analyzer": "web_content_analyzer"},
                    "doc_hash": {"type": "keyword"},
                    "source": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "indexed_at": {"type": "date"},
                    "token_count": {"type": "integer"},
                    "safety_flags": {"type": "keyword"},
                }
            },
        }

        if self._es_client:
            await self._es_client.indices.create(
                index=self.index_name,
                body=mappings,
                ignore=400,  # Ignore if exists
            )
            logger.info(f"Index {self.index_name} ready")

    def compute_hash(self, content: str) -> str:
        """SHA-256 hash for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()

    async def scan_document(
        self,
        content: str,
        doc_id: str,
        language: str = "en",
        categories: Optional[List[SafetyCategory]] = None,
    ) -> SafetyScanResult:
        """
        Scan a document for safety issues.

        From paper: "many harmful strings are actually general terms needed
        for important discussions... you can't just blanket-remove everything;
        you need context-aware filtering."
        """
        if categories is None:
            categories = list(SafetyCategory)

        result = SafetyScanResult(
            doc_id=doc_id,
            doc_hash=self.compute_hash(content),
            scanned_at=datetime.utcnow(),
            total_tokens=len(content.split()),
            languages_detected={language},
        )

        content_lower = content.lower()

        for category in categories:
            terms = self.lexicon.get_terms(category, language)

            for term in terms:
                term_lower = term.lower()
                pos = content_lower.find(term_lower)

                while pos != -1:
                    # Extract context (50 chars before/after)
                    start = max(0, pos - 50)
                    end = min(len(content), pos + len(term) + 50)
                    context = content[start:end]

                    # Calculate severity based on category
                    severity = self._calculate_severity(category, term, context)

                    hit = SafetyHit(
                        category=category,
                        term=term,
                        context=context,
                        position=pos,
                        language=language,
                        severity=severity,
                        requires_review=(severity > 0.7),
                    )
                    result.hits.append(hit)

                    # Find next occurrence
                    pos = content_lower.find(term_lower, pos + 1)

        return result

    def _calculate_severity(self, category: SafetyCategory, term: str, context: str) -> float:
        """
        Context-aware severity calculation.

        From paper: Despite lots of toxic words in training data,
        Apertus still performs well on toxicity benchmarks because
        context matters.
        """
        base_severity = {
            SafetyCategory.CSAM: 1.0,  # Always maximum
            SafetyCategory.CHEMICAL_WEAPONS: 0.8,
            SafetyCategory.WEAPONIZED_WORDS: 0.6,
            SafetyCategory.LDNOOBW: 0.4,
            SafetyCategory.PII: 0.5,
            SafetyCategory.COPYRIGHTED: 0.3,
            SafetyCategory.DISINFORMATION: 0.5,
        }.get(category, 0.5)

        # Reduce severity for educational/research context
        educational_markers = [
            "research",
            "study",
            "analysis",
            "history",
            "definition",
            "example",
            "warning",
            "avoid",
        ]
        context_lower = context.lower()

        for marker in educational_markers:
            if marker in context_lower:
                base_severity *= 0.7
                break

        return min(1.0, base_severity)

    async def search_phrase(self, phrase: str, slop: int = 0, limit: int = 100) -> List[Dict]:
        """
        Search for a phrase with configurable slop.

        From paper: match_phrase queries with slop for fuzzy matching.
        Response times practical even for 300-word phrases.
        """
        if not self._es_client:
            logger.warning("ES not connected, returning empty results")
            return []

        query = {
            "query": {"match_phrase": {"content": {"query": phrase, "slop": slop}}},
            "size": limit,
        }

        result = await self._es_client.search(index=self.index_name, body=query)

        return [hit["_source"] for hit in result["hits"]["hits"]]

    async def bulk_index(self, documents: AsyncIterator[Dict], progress_callback=None) -> Dict:
        """
        Bulk index documents with parallel processing.

        From paper Table 4:
        - FineWeb-Edu: ~10,300 docs/sec
        - Multilingual: ~600 docs/sec
        - Index size: 1.1-1.3x raw data
        """
        stats = {
            "indexed": 0,
            "failed": 0,
            "duplicates": 0,
            "safety_flagged": 0,
            "start_time": datetime.utcnow().isoformat(),
        }

        seen_hashes = set()
        batch = []

        async for doc in documents:
            doc_hash = self.compute_hash(doc.get("content", ""))

            # Dedup check
            if doc_hash in seen_hashes:
                stats["duplicates"] += 1
                continue
            seen_hashes.add(doc_hash)

            # Safety scan
            scan_result = await self.scan_document(
                doc.get("content", ""), doc.get("id", doc_hash), doc.get("language", "en")
            )

            # Prepare for indexing
            index_doc = {
                "_index": self.index_name,
                "_id": doc_hash,
                "_source": {
                    "content": doc.get("content", ""),
                    "doc_hash": doc_hash,
                    "source": doc.get("source", "unknown"),
                    "language": doc.get("language", "en"),
                    "indexed_at": datetime.utcnow().isoformat(),
                    "token_count": scan_result.total_tokens,
                    "safety_flags": [h.category.value for h in scan_result.hits],
                    "max_severity": scan_result.max_severity,
                },
            }

            batch.append(index_doc)

            if not scan_result.is_clean:
                stats["safety_flagged"] += 1

            # Bulk insert when batch is full
            if len(batch) >= self.bulk_config["chunk_size"]:
                if self._es_client:
                    from elasticsearch.helpers import async_bulk

                    success, failed = await async_bulk(
                        self._es_client,
                        batch,
                        chunk_size=self.bulk_config["chunk_size"],
                    )
                    stats["indexed"] += success
                    stats["failed"] += len(failed)
                else:
                    stats["indexed"] += len(batch)

                if progress_callback:
                    progress_callback(stats)

                batch = []

        # Index remaining
        if batch:
            if self._es_client:
                from elasticsearch.helpers import async_bulk

                success, failed = await async_bulk(self._es_client, batch)
                stats["indexed"] += success
                stats["failed"] += len(failed)
            else:
                stats["indexed"] += len(batch)

        stats["end_time"] = datetime.utcnow().isoformat()
        return stats

    async def generate_safety_report(self, languages: Optional[List[str]] = None) -> Dict:
        """
        Generate safety report similar to Apertus Table 5.

        Reports counts of documents with harmful terms by:
        - Category (Weaponized Words, LDNOOBW, Chemical)
        - Language
        """
        if languages is None:
            languages = ["en", "de", "fr", "it", "es"]

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "index": self.index_name,
            "by_category": {},
            "by_language": {},
        }

        for category in SafetyCategory:
            if not self._es_client:
                continue

            query = {
                "query": {"term": {"safety_flags": category.value}},
                "size": 0,
                "aggs": {"by_language": {"terms": {"field": "language"}}},
            }

            result = await self._es_client.search(index=self.index_name, body=query)

            total = result["hits"]["total"]["value"]
            report["by_category"][category.value] = {
                "total": total,
                "by_language": {
                    b["key"]: b["doc_count"]
                    for b in result["aggregations"]["by_language"]["buckets"]
                },
            }

        return report


# =============================================================================
# INTEGRATION WITH JUDGE #6
# =============================================================================


class SafetyGate:
    """
    Safety gate for Judge #6 pipeline.

    Blocks content that exceeds severity thresholds before
    it reaches governance evaluation.
    """

    def __init__(
        self,
        indexer: TrainingDataIndexer,
        max_severity: float = 0.7,
        auto_block_categories: Optional[List[SafetyCategory]] = None,
    ):
        self.indexer = indexer
        self.max_severity = max_severity
        self.auto_block_categories = auto_block_categories or [
            SafetyCategory.CSAM,
            SafetyCategory.CHEMICAL_WEAPONS,
        ]

    async def evaluate(self, content: str, doc_id: str, language: str = "en") -> Dict:
        """
        Evaluate content through safety gate.

        Returns:
            {
                "passed": bool,
                "blocked_reason": str or None,
                "severity": float,
                "hits": List[SafetyHit],
                "requires_review": bool
            }
        """
        scan_result = await self.indexer.scan_document(content, doc_id, language)

        # Auto-block for critical categories
        for hit in scan_result.hits:
            if hit.category in self.auto_block_categories:
                return {
                    "passed": False,
                    "blocked_reason": f"Auto-blocked: {hit.category.value}",
                    "severity": hit.severity,
                    "hits": scan_result.hits,
                    "requires_review": True,
                }

        # Check severity threshold
        if scan_result.max_severity > self.max_severity:
            return {
                "passed": False,
                "blocked_reason": f"Severity {scan_result.max_severity:.2f} exceeds threshold {self.max_severity}",
                "severity": scan_result.max_severity,
                "hits": scan_result.hits,
                "requires_review": True,
            }

        return {
            "passed": True,
            "blocked_reason": None,
            "severity": scan_result.max_severity,
            "hits": scan_result.hits,
            "requires_review": scan_result.requires_immediate_review,
        }


# =============================================================================
# CLI ENTRY POINT
# =============================================================================


async def main():
    """CLI entry point for training data safety operations"""
    import argparse

    parser = argparse.ArgumentParser(description="Training Data Safety Indexer")
    parser.add_argument(
        "command", choices=["scan", "search", "report", "index"], help="Command to run"
    )
    parser.add_argument("--file", "-f", help="File to scan")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--language", "-l", default="en", help="Language code")

    args = parser.parse_args()

    indexer = TrainingDataIndexer()
    await indexer.connect()

    if args.command == "scan":
        if not args.file:
            print("Error: --file required for scan")
            return

        content = Path(args.file).read_text()
        result = await indexer.scan_document(content, args.file, args.language)
        print(
            json.dumps(
                {
                    "doc_id": result.doc_id,
                    "is_clean": result.is_clean,
                    "max_severity": result.max_severity,
                    "hit_count": len(result.hits),
                    "hits": [
                        {
                            "category": h.category.value,
                            "term": h.term,
                            "severity": h.severity,
                        }
                        for h in result.hits[:10]  # Limit output
                    ],
                },
                indent=2,
            )
        )

    elif args.command == "search":
        if not args.query:
            print("Error: --query required for search")
            return

        results = await indexer.search_phrase(args.query)
        print(json.dumps({"count": len(results), "results": results[:5]}, indent=2))

    elif args.command == "report":
        report = await indexer.generate_safety_report()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
