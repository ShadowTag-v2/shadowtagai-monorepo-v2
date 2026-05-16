# Context Index Scaling Strategy - Elasticsearch Architecture

**Inspired by**: Apertus LLM Training Data Indexing (8.6T tokens, Elasticsearch 7.17 on Arm64)
**Target**: Scale Context Index to handle 600 agents × 100 contexts each = 60k+ OPORDs
**Platform**: GCP (Cloud Run, GCS, Elasticsearch on GKE)

## Problem Statement

Current `AtomicChatManager` uses SQLite for Context Index storage. This works for prototyping but won't scale to:

- **600 FlyingMonkeys agents** × 100 contexts each = 60,000+ OPORDs
- **Full-text search** across OPORD content (situation, mission, execution, etc.)
- **Multilingual support** (if expanding beyond English)
- **Audit trail queries** (e.g., "Find all security audits mentioning reentrancy")

## Apertus Paper Lessons

### What They Achieved

- **8.6 trillion tokens** indexed (58% of 15.2T training corpus)
- **Elasticsearch 7.17** on Arm64 NVIDIA GH200 nodes
- **~10,300 docs/sec** throughput (English FineWeb-Edu)
- **Index size ≈ 1.3× raw data** (with compression)
- **Practical query times** even for 300-word phrases

### Key Engineering Tricks

1. **Custom Analyzer** - `web_content_analyzer` with HTML stripping, tokenization, lowercasing, ASCII-folding
2. **Parallel Bulk Indexing** - Tuned thread count, chunk size, queue size
3. **Memory Mapping Disabled** - Worked around HPC constraints (we don't have this issue on GKE)
4. **Dedup via SHA-256** - 68% duplicates found, but dedup didn't speed indexing (ES handles internally)
5. **Match Phrase Queries** - Configurable slop for fuzzy phrase search

### Performance Bounds

- **Storage latency**: ~50 µs/doc → theoretical max ~10k docs/sec per node
- **Multilingual penalty**: Throughput drops to ~600 docs/sec for complex char sets
- **Code corpus**: Higher memory usage (unique identifiers, less redundancy)

## Proposed Architecture for ShadowTagAI

### Phase 1: Elasticsearch on GKE (Current Scale)

**Target**: 60k OPORDs, full-text search, <100ms p99 query latency

```
┌─────────────────────────────────────────────────┐
│          AtomicChatManager (Python)             │
│  - Creates OPORDs                               │
│  - Writes to SQLite (local cache)              │
│  - Async pushes to Elasticsearch               │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│     Elasticsearch 8.x on GKE Autopilot          │
│  - 3-node cluster (primary + 2 replicas)        │
│  - Index: opord_contexts                        │
│  - Shards: 3 (20k docs each)                    │
│  - Replicas: 1 (for HA)                         │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          GCS Backup (Daily Snapshots)           │
│  - Retention: 30 days                           │
│  - Cost: ~$0.02/GB/month                        │
└─────────────────────────────────────────────────┘
```

**Index Mapping** (Elasticsearch):

```json
{
  "mappings": {
    "properties": {
      "opord_number": {"type": "integer"},
      "task_title": {"type": "text", "analyzer": "opord_analyzer"},
      "agent_id": {"type": "keyword"},
      "shift_number": {"type": "integer"},

      "situation": {
        "properties": {
          "enemy_forces": {"type": "text", "analyzer": "opord_analyzer"},
          "friendly_forces": {"type": "text", "analyzer": "opord_analyzer"},
          "attachments": {"type": "text"},
          "civil_considerations": {"type": "text"}
        }
      },

      "mission": {
        "properties": {
          "who": {"type": "text"},
          "what": {"type": "text", "analyzer": "opord_analyzer"},
          "when": {"type": "text"},
          "where": {"type": "text"},
          "why": {"type": "text", "analyzer": "opord_analyzer"}
        }
      },

      "execution": {
        "properties": {
          "commanders_intent": {"type": "text", "analyzer": "opord_analyzer"},
          "concept_of_operations": {"type": "text", "analyzer": "opord_analyzer"},
          "tasks_to_subordinates": {"type": "object", "enabled": false},
          "coordinating_instructions": {"type": "object", "enabled": false}
        }
      },

      "tags": {"type": "keyword"},
      "created_at": {"type": "date"},
      "status": {"type": "keyword"}
    }
  },
  "settings": {
    "analysis": {
      "analyzer": {
        "opord_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding", "stop"]
        }
      }
    }
  }
}
```

**Cost Estimate** (GKE Autopilot):

- **3 nodes** × e2-standard-4 (4 vCPU, 16 GB RAM) = ~$150/month
- **Persistent disks** (100 GB SSD each) = ~$50/month
- **GCS backups** (30 days × 10 GB) = ~$6/month
- **Total**: ~$206/month for 60k OPORDs

### Phase 2: Hybrid SQLite + Elasticsearch (Optimization)

**Goal**: Reduce costs by keeping SQLite for fast local queries, ES for full-text search only

```python
class HybridContextIndex:
    """
    SQLite for structured queries (agent_id, shift, status)
    Elasticsearch for full-text search (keywords, phrases)
    """

    def __init__(self):
        self.sqlite = sqlite3.connect("data/context_index.db")
        self.es = Elasticsearch(["https://es.shadowtagai.com"])

    def create_opord(self, **kwargs) -> int:
        # Write to SQLite (fast, local)
        opord_num = self._insert_sqlite(**kwargs)

        # Async push to Elasticsearch (for search)
        self._index_es_async(opord_num, **kwargs)

        return opord_num

    def search_opords(self, query: str, filters: Dict) -> List[Dict]:
        # Full-text search via ES
        es_results = self.es.search(
            index="opord_contexts",
            body={
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"mission.what": query}}
                        ],
                        "filter": [
                            {"term": {"status": filters.get("status", "active")}}
                        ]
                    }
                }
            }
        )

        # Enrich with SQLite data if needed
        opord_nums = [hit["_source"]["opord_number"] for hit in es_results["hits"]["hits"]]
        return self._fetch_sqlite_by_opord_nums(opord_nums)
```

**Cost Savings**: ~50% by using smaller ES cluster (1-2 nodes) since SQLite handles most queries

### Phase 3: Multi-Tenant Scaling (Future)

**Target**: 10,000+ agents across multiple customers

```
┌─────────────────────────────────────────────────┐
│       Elasticsearch 8.x (Multi-Tenant)          │
│  - Index per customer: opord_contexts_<org_id>  │
│  - Sharding: 1 shard per 50k docs               │
│  - Replicas: 2 (for HA + read scaling)          │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│      GCS Tiered Storage (Hot/Cold)              │
│  - Hot: Last 30 days (GCS Standard)             │
│  - Cold: 30-365 days (GCS Nearline)             │
│  - Archive: >365 days (GCS Archive)             │
└─────────────────────────────────────────────────┘
```

**Revenue Opportunity**: Charge for audit trail retention

- **Basic**: 30 days (included)
- **Standard**: 90 days (+$100/month)
- **Enterprise**: Unlimited (+$500/month with replay viewer)

## Safety & Governance Indexing (Apertus-Inspired)

### Harmful Content Detection

Apertus indexed for:
- **Weaponized Words** (multilingual slurs/toxic terms)
- **LDNOOBW** (dirty/naughty/obscene words, 28 languages)
- **Chemical weapons** (specific agents like phosgene, sulfur mustard)

**ShadowTagAI Application**:

```python
# Index OPORD content for governance violations
GOVERNANCE_LEXICONS = {
    "pii_patterns": ["ssn", "credit card", "passport"],
    "security_violations": ["hardcoded password", "api key", "private key"],
    "compliance_flags": ["gdpr", "hipaa", "sox", "pci-dss"]
}

def scan_opord_for_violations(opord_content: str) -> List[str]:
    """
    Scan OPORD for governance violations using ES match_phrase.
    """
    violations = []

    for category, terms in GOVERNANCE_LEXICONS.items():
        for term in terms:
            results = es.search(
                index="opord_contexts",
                body={
                    "query": {
                        "match_phrase": {
                            "_all": {
                                "query": term,
                                "slop": 2  # Allow 2-word gaps
                            }
                        }
                    }
                }
            )

            if results["hits"]["total"]["value"] > 0:
                violations.append(f"{category}: {term}")

    return violations
```

### Judge#6 Integration

```python
# Log governance decisions to ES for audit trail
def log_judge6_decision(decision: Dict):
    """
    Log Judge#6 governance decision to Elasticsearch.
    """
    es.index(
        index="judge6_decisions",
        body={
            "decision_id": decision["id"],
            "opord_number": decision["opord_num"],
            "policy_violated": decision["policy"],
            "severity": decision["severity"],
            "action_taken": decision["action"],
            "timestamp": datetime.utcnow().isoformat(),
            "reasoning": decision["reasoning"]
        }
    )
```

## Implementation Roadmap

### Week 1: Elasticsearch Setup

- [ ] Deploy ES 8.x on GKE Autopilot (3-node cluster)
- [ ] Create `opord_contexts` index with custom analyzer
- [ ] Test bulk indexing with 1k sample OPORDs
- [ ] Validate query performance (<100ms p99)

### Week 2: Hybrid Integration

- [ ] Update `AtomicChatManager` to write to both SQLite + ES
- [ ] Implement async ES indexing (avoid blocking OPORD creation)
- [ ] Add full-text search API endpoint
- [ ] Test with 10k OPORDs

### Week 3: Safety Scanning

- [ ] Implement governance lexicon scanning
- [ ] Integrate with Judge#6 decision logging
- [ ] Create audit trail viewer (Cloud Run web app)
- [ ] Test with real governance scenarios

### Week 4: Production Hardening

- [ ] Set up GCS snapshots (daily backups)
- [ ] Configure alerts (query latency, index size, errors)
- [ ] Load test with 60k OPORDs
- [ ] Document runbooks for incidents

## Success Metrics

- **Indexing Speed**: ≥1k OPORDs/sec (10× faster than Apertus multilingual)
- **Query Latency**: <100ms p99 for full-text search
- **Storage Efficiency**: Index size ≤ 1.5× raw OPORD data
- **Availability**: 99.9% uptime (GKE HA + replicas)
- **Cost**: <$250/month for 60k OPORDs

## References

- Apertus Paper: [arXiv:2510.09471v1](https://arxiv.org/pdf/2510.09471v1)
- Elasticsearch on GKE: [GCP Docs](https://cloud.google.com/kubernetes-engine/docs/tutorials/elasticsearch)
- ES Performance Tuning: [Elastic Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/tune-for-indexing-speed.html)
