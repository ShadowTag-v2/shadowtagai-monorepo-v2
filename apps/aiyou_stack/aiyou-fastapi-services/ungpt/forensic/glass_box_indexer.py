# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Glass Box Indexer - Full-Text Compliance Search

Based on ArXiv 2510.09471 (Apertus Methodology):
- Parquet streaming for efficient ingestion
- Elasticsearch with phrase search (slop)
- ~10k docs/sec throughput target

This enables queries like:
"Show me every time the AI blocked a transaction because it suspected 'chemical weapon' precursors"
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime

from .es_config import get_es_config
from .pii_scrubber import PIIScrubber, scrub_document

logger = logging.getLogger(__name__)


@dataclass
class IndexStats:
    """Statistics for an indexing run"""

    documents_indexed: int = 0
    documents_failed: int = 0
    pii_scrubbed: int = 0
    total_bytes: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None

    @property
    def duration_seconds(self) -> float:
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()

    @property
    def docs_per_second(self) -> float:
        if self.duration_seconds == 0:
            return 0
        return self.documents_indexed / self.duration_seconds


class GlassBoxIndexer:
    """Full-text indexer for governance decision chains.

    Implements the Apertus methodology for large-scale
    reasoning chain indexing with compliance search.
    """

    def __init__(
        self,
        es_host: str = "localhost",
        es_port: int = 9200,
        index_name: str = "ungpt_forensic",
        scrub_pii: bool = True,
    ):
        self.es_host = es_host
        self.es_port = es_port
        self.index_name = index_name
        self.scrub_pii = scrub_pii
        self._es_client = None
        self.pii_scrubber = PIIScrubber() if scrub_pii else None

        # Bulk indexing config (from Apertus Table 4)
        self.bulk_config = {
            "chunk_size": 500,
            "max_chunk_bytes": 100 * 1024 * 1024,  # 100MB
            "thread_count": 4,
            "queue_size": 4,
        }

    async def connect(self):
        """Connect to Elasticsearch"""
        try:
            from elasticsearch import AsyncElasticsearch

            self._es_client = AsyncElasticsearch(
                [f"http://{self.es_host}:{self.es_port}"],
                http_compress=True,
                retry_on_timeout=True,
                max_retries=3,
            )

            # Test connection
            info = await self._es_client.info()
            logger.info(f"Connected to Elasticsearch {info['version']['number']}")

        except ImportError:
            logger.warning("elasticsearch-py not installed, using mock mode")
            self._es_client = None
        except Exception as e:
            logger.error(f"Failed to connect to ES: {e}")
            self._es_client = None

    async def create_index(self):
        """Create the forensic index with optimized mappings"""
        if not self._es_client:
            logger.warning("ES not connected, skipping index creation")
            return

        config = get_es_config(self.index_name)

        try:
            await self._es_client.indices.create(
                index=self.index_name,
                body=config,
                ignore=400,  # Ignore if exists
            )
            logger.info(f"Index {self.index_name} ready")
        except Exception as e:
            logger.error(f"Index creation failed: {e}")

    async def index_document(self, doc: dict) -> bool:
        """Index a single governance decision document.

        Args:
            doc: Document with fields:
                - trace_id: Unique identifier
                - component: judge_6, shadowtag, etc.
                - verdict: ALLOW, BLOCK, etc.
                - full_prompt: Complete input
                - reasoning_chain: CoT output
                - final_output: Final response

        Returns:
            Success boolean

        """
        # Scrub PII if enabled
        if self.scrub_pii and self.pii_scrubber:
            doc, pii_report = scrub_document(doc)
            if pii_report["total_matches"] > 0:
                logger.debug(f"Scrubbed {pii_report['total_matches']} PII items")

        # Add metadata
        doc["indexed_at"] = datetime.utcnow().isoformat()
        doc["retention_days"] = doc.get("retention_days", 2555)  # 7 years default

        if not self._es_client:
            logger.debug(f"Mock index: {doc.get('trace_id', 'unknown')}")
            return True

        try:
            await self._es_client.index(index=self.index_name, id=doc.get("trace_id"), body=doc)
            return True
        except Exception as e:
            logger.error(f"Index failed: {e}")
            return False

    async def bulk_index(
        self,
        documents: AsyncIterator[dict],
        progress_callback=None,
    ) -> IndexStats:
        """Bulk index documents with Apertus-style parallel processing.

        Args:
            documents: Async iterator of documents
            progress_callback: Optional callback(stats) for progress

        Returns:
            IndexStats with results

        """
        stats = IndexStats()
        batch = []

        async for doc in documents:
            # Scrub PII
            if self.scrub_pii and self.pii_scrubber:
                doc, pii_report = scrub_document(doc)
                if pii_report["total_matches"] > 0:
                    stats.pii_scrubbed += 1

            # Add to batch
            batch.append({"_index": self.index_name, "_id": doc.get("trace_id"), "_source": doc})

            stats.total_bytes += len(json.dumps(doc))

            # Flush batch
            if len(batch) >= self.bulk_config["chunk_size"]:
                success, failed = await self._flush_batch(batch)
                stats.documents_indexed += success
                stats.documents_failed += failed
                batch = []

                if progress_callback:
                    progress_callback(stats)

        # Final flush
        if batch:
            success, failed = await self._flush_batch(batch)
            stats.documents_indexed += success
            stats.documents_failed += failed

        stats.end_time = datetime.now()
        return stats

    async def _flush_batch(self, batch: list[dict]) -> tuple:
        """Flush a batch to Elasticsearch"""
        if not self._es_client:
            return len(batch), 0

        try:
            from elasticsearch.helpers import async_bulk

            success, errors = await async_bulk(
                self._es_client,
                batch,
                chunk_size=self.bulk_config["chunk_size"],
                raise_on_error=False,
            )
            return success, len(errors)
        except Exception as e:
            logger.error(f"Bulk index failed: {e}")
            return 0, len(batch)

    async def search_phrase(
        self,
        phrase: str,
        field: str = "reasoning_chain",
        slop: int = 5,
        limit: int = 100,
        filters: dict | None = None,
    ) -> list[dict]:
        """Search for a phrase with configurable slop.

        Slop allows words to be out of order or have
        words between them. slop=5 means up to 5 words
        can appear between terms.

        Args:
            phrase: Search phrase
            field: Field to search (reasoning_chain, full_prompt, etc.)
            slop: Word distance allowed
            limit: Max results
            filters: Optional filters (component, verdict, etc.)

        Returns:
            List of matching documents

        """
        if not self._es_client:
            logger.warning("ES not connected, returning empty results")
            return []

        # Build query
        must = [{"match_phrase": {field: {"query": phrase, "slop": slop}}}]

        # Add filters
        if filters:
            for key, value in filters.items():
                must.append({"term": {key: value}})

        query = {
            "query": {"bool": {"must": must}},
            "size": limit,
            "sort": [{"timestamp": "desc"}],
            "_source": True,
        }

        try:
            result = await self._es_client.search(index=self.index_name, body=query)
            return [hit["_source"] for hit in result["hits"]["hits"]]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def search_verdict(
        self,
        verdict: str,
        component: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Search by verdict (ALLOW, BLOCK, etc.)

        Args:
            verdict: Verdict to search for
            component: Optional component filter
            limit: Max results

        Returns:
            List of matching documents

        """
        filters = {"verdict": verdict}
        if component:
            filters["component"] = component

        return await self.search_phrase(phrase="", filters=filters, limit=limit)

    async def get_stats(self) -> dict:
        """Get index statistics"""
        if not self._es_client:
            return {"status": "disconnected"}

        try:
            stats = await self._es_client.indices.stats(index=self.index_name)
            return {
                "documents": stats["indices"][self.index_name]["total"]["docs"]["count"],
                "size_bytes": stats["indices"][self.index_name]["total"]["store"]["size_in_bytes"],
                "pii_scrubber": self.pii_scrubber.get_stats() if self.pii_scrubber else None,
            }
        except Exception as e:
            return {"error": str(e)}


# CLI entry point for testing
async def main():
    """CLI for testing Glass Box indexer"""
    import argparse

    parser = argparse.ArgumentParser(description="Glass Box Forensic Indexer")
    parser.add_argument("command", choices=["index", "search", "stats"])
    parser.add_argument("--phrase", "-p", help="Search phrase")
    parser.add_argument("--field", "-f", default="reasoning_chain")
    parser.add_argument("--slop", "-s", type=int, default=5)

    args = parser.parse_args()

    indexer = GlassBoxIndexer()
    await indexer.connect()

    if args.command == "stats":
        stats = await indexer.get_stats()
        print(json.dumps(stats, indent=2))

    elif args.command == "search":
        if not args.phrase:
            print("Error: --phrase required for search")
            return

        results = await indexer.search_phrase(args.phrase, field=args.field, slop=args.slop)
        print(f"Found {len(results)} results:")
        for r in results[:5]:
            print(f"  - {r.get('trace_id')}: {r.get('verdict')}")


if __name__ == "__main__":
    asyncio.run(main())
