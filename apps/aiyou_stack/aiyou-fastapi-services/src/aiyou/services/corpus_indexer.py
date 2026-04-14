#!/usr/bin/env python3
"""Corpus Indexer for Elasticsearch
Indexes documents for Flying minion searchable corpus.
Apertus-style 8.6T token indexing pattern.
"""

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from elasticsearch import Elasticsearch
except ImportError:
    Elasticsearch = None


@dataclass
class Document:
    """Indexed document structure."""

    doc_id: str
    title: str
    content: str
    source_path: str
    doc_type: str  # code, paper, doc, config
    language: str | None
    tokens: int
    indexed_at: str
    metadata: dict[str, Any]


class CorpusIndexer:
    """Elasticsearch indexer for Flying minion corpus.

    Pipeline:
    GitHub Discovery Agent → Safety Scanner → Corpus Indexer → Judge #6
    """

    INDEX_NAME = "minions-corpus"

    def __init__(self, es_host: str = None):
        self.es_host = es_host or os.getenv("ELASTICSEARCH_HOST", "localhost:9200")

        if Elasticsearch:
            self.es = Elasticsearch([self.es_host])
        else:
            self.es = None
            print("WARNING: elasticsearch not installed, running in mock mode")

        self._ensure_index()

    def _ensure_index(self):
        """Create index with mappings if not exists."""
        if not self.es:
            return

        if not self.es.indices.exists(index=self.INDEX_NAME):
            mappings = {
                "mappings": {
                    "properties": {
                        "doc_id": {"type": "keyword"},
                        "title": {"type": "text", "analyzer": "standard"},
                        "content": {"type": "text", "analyzer": "standard"},
                        "source_path": {"type": "keyword"},
                        "doc_type": {"type": "keyword"},
                        "language": {"type": "keyword"},
                        "tokens": {"type": "integer"},
                        "indexed_at": {"type": "date"},
                        "metadata": {"type": "object", "enabled": False},
                    },
                },
                "settings": {"number_of_shards": 1, "number_of_replicas": 0},
            }
            self.es.indices.create(index=self.INDEX_NAME, body=mappings)
            print(f"///▞ Created index: {self.INDEX_NAME}")

    def _generate_doc_id(self, content: str, source_path: str) -> str:
        """Generate unique document ID."""
        hash_input = f"{source_path}:{content[:1000]}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def _estimate_tokens(self, content: str) -> int:
        """Rough token estimate (4 chars per token)."""
        return len(content) // 4

    def index_document(
        self,
        content: str,
        source_path: str,
        title: str = None,
        doc_type: str = "doc",
        language: str = None,
        metadata: dict = None,
    ) -> str:
        """Index a single document.

        Args:
            content: Document text
            source_path: File path or URL
            title: Document title (defaults to filename)
            doc_type: code, paper, doc, config
            language: Programming language if code
            metadata: Additional metadata

        Returns:
            Document ID

        """
        doc_id = self._generate_doc_id(content, source_path)

        doc = Document(
            doc_id=doc_id,
            title=title or Path(source_path).name,
            content=content,
            source_path=source_path,
            doc_type=doc_type,
            language=language,
            tokens=self._estimate_tokens(content),
            indexed_at=datetime.utcnow().isoformat(),
            metadata=metadata or {},
        )

        if self.es:
            self.es.index(index=self.INDEX_NAME, id=doc_id, body=asdict(doc))

        print(f"///▞ Indexed: {doc_id} ({doc.tokens} tokens) {source_path}")
        return doc_id

    def index_code_file(self, file_path: str, metadata: dict = None) -> str:
        """Index a code file with language detection."""
        path = Path(file_path)

        # Language detection by extension
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".sh": "bash",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".rb": "ruby",
            ".sql": "sql",
        }

        language = lang_map.get(path.suffix, "unknown")

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        return self.index_document(
            content=content,
            source_path=file_path,
            doc_type="code",
            language=language,
            metadata=metadata,
        )

    def index_from_discovery(self, discovery_json: dict) -> list[str]:
        """Index scripts from GitHub Discovery Agent output.

        Args:
            discovery_json: Output from github_discovery_agent.py

        Returns:
            List of indexed document IDs

        """
        indexed = []

        for script in discovery_json.get("scripts", []):
            if script.get("sensitive"):
                print(f"///▞ SKIP (sensitive): {script['path']}")
                continue

            try:
                doc_id = self.index_code_file(
                    script["path"],
                    metadata={
                        "category": script.get("category"),
                        "status": script.get("status"),
                        "dependencies": script.get("dependencies"),
                        "issues": script.get("issues"),
                    },
                )
                indexed.append(doc_id)
            except Exception as e:
                print(f"///▞ ERROR indexing {script['path']}: {e}")

        return indexed

    def search(
        self, query: str, doc_type: str = None, language: str = None, limit: int = 10,
    ) -> list[dict]:
        """Search the corpus.

        Args:
            query: Search query
            doc_type: Filter by type
            language: Filter by language
            limit: Max results

        Returns:
            List of matching documents

        """
        if not self.es:
            return []

        must = [{"match": {"content": query}}]

        if doc_type:
            must.append({"term": {"doc_type": doc_type}})
        if language:
            must.append({"term": {"language": language}})

        body = {
            "query": {"bool": {"must": must}},
            "size": limit,
            "_source": ["doc_id", "title", "source_path", "doc_type", "language", "tokens"],
        }

        result = self.es.search(index=self.INDEX_NAME, body=body)

        return [{**hit["_source"], "score": hit["_score"]} for hit in result["hits"]["hits"]]

    def get_stats(self) -> dict:
        """Get corpus statistics."""
        if not self.es:
            return {"status": "mock_mode"}

        count = self.es.count(index=self.INDEX_NAME)

        # Aggregate by type
        agg_body = {
            "size": 0,
            "aggs": {
                "by_type": {"terms": {"field": "doc_type"}},
                "by_language": {"terms": {"field": "language"}},
                "total_tokens": {"sum": {"field": "tokens"}},
            },
        }

        aggs = self.es.search(index=self.INDEX_NAME, body=agg_body)

        return {
            "total_documents": count["count"],
            "by_type": {
                b["key"]: b["doc_count"] for b in aggs["aggregations"]["by_type"]["buckets"]
            },
            "by_language": {
                b["key"]: b["doc_count"] for b in aggs["aggregations"]["by_language"]["buckets"]
            },
            "total_tokens": int(aggs["aggregations"]["total_tokens"]["value"]),
        }


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Corpus Indexer")
    subparsers = parser.add_subparsers(dest="command")

    # Index file
    index_parser = subparsers.add_parser("index", help="Index a file")
    index_parser.add_argument("file", help="File to index")

    # Index from discovery
    discovery_parser = subparsers.add_parser("discovery", help="Index from discovery JSON")
    discovery_parser.add_argument("json_file", help="Discovery JSON file")

    # Search
    search_parser = subparsers.add_parser("search", help="Search corpus")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", help="Filter by doc type")
    search_parser.add_argument("--lang", help="Filter by language")

    # Stats
    subparsers.add_parser("stats", help="Show corpus stats")

    args = parser.parse_args()
    indexer = CorpusIndexer()

    if args.command == "index":
        indexer.index_code_file(args.file)
    elif args.command == "discovery":
        with open(args.json_file) as f:
            discovery = json.load(f)
        indexed = indexer.index_from_discovery(discovery)
        print(f"Indexed {len(indexed)} documents")
    elif args.command == "search":
        results = indexer.search(args.query, doc_type=args.type, language=args.lang)
        for r in results:
            print(f"{r['score']:.2f} {r['doc_id']} {r['source_path']}")
    elif args.command == "stats":
        stats = indexer.get_stats()
        print(json.dumps(stats, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
