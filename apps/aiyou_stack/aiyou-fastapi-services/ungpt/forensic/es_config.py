# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Elasticsearch Configuration for Glass Box

Based on Apertus paper constraints:
- mmap disabled for HPC/container compatibility
- Custom analyzer for reasoning chains
- Optimized for phrase search with slop
"""


def get_es_config(index_name: str = "ungpt_forensic", shards: int = 1, replicas: int = 0) -> dict:
    """Get Elasticsearch index configuration.

    Settings based on Apertus paper Section 3:
    - Disabled memory mapping (vm.max_map_count workaround)
    - Custom analyzer for reasoning text
    - Position index for phrase search

    Args:
        index_name: Name of the index
        shards: Number of shards
        replicas: Number of replicas

    Returns:
        Elasticsearch index settings dict

    """
    return {
        "settings": {
            "number_of_shards": shards,
            "number_of_replicas": replicas,
            # Apertus HPC compatibility
            "index.store.type": "niofs",  # Avoid mmap
            # Analysis
            "analysis": {
                "analyzer": {
                    "reasoning_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "asciifolding", "english_stop", "english_stemmer"],
                    },
                    "code_analyzer": {
                        "type": "custom",
                        "tokenizer": "whitespace",
                        "filter": ["lowercase"],
                    },
                },
                "filter": {
                    "english_stop": {"type": "stop", "stopwords": "_english_"},
                    "english_stemmer": {"type": "stemmer", "language": "english"},
                },
            },
        },
        "mappings": {
            "properties": {
                # Identifiers
                "trace_id": {"type": "keyword"},
                "query_id": {"type": "keyword"},
                "timestamp": {"type": "date"},
                # Governance fields
                "component": {"type": "keyword"},
                "verdict": {"type": "keyword"},
                "crm_score": {"type": "float"},
                # Full-text searchable fields
                "full_prompt": {
                    "type": "text",
                    "analyzer": "reasoning_analyzer",
                    "index_options": "positions",  # Enable phrase search
                },
                "reasoning_chain": {
                    "type": "text",
                    "analyzer": "reasoning_analyzer",
                    "index_options": "positions",
                },
                "final_output": {"type": "text", "analyzer": "reasoning_analyzer"},
                # Code-specific field
                "code_blocks": {"type": "text", "analyzer": "code_analyzer"},
                # Metadata
                "model": {"type": "keyword"},
                "layer": {"type": "keyword"},
                "cost": {"type": "float"},
                "tokens_in": {"type": "integer"},
                "tokens_out": {"type": "integer"},
                # Compliance
                "pii_scrubbed": {"type": "boolean"},
                "retention_days": {"type": "integer"},
            },
        },
    }


# Node settings for container/HPC deployment
NODE_SETTINGS = {
    # Disable mmap to avoid vm.max_map_count requirement
    "bootstrap.memory_lock": False,
    "node.store.allow_mmap": False,
    # Network settings for container
    "network.host": "0.0.0.0",
    "http.port": 9200,
    # Disable discovery for single-node
    "discovery.type": "single-node",
    # JVM heap (adjust based on container limits)
    "ES_JAVA_OPTS": "-Xms1g -Xmx1g",
}
