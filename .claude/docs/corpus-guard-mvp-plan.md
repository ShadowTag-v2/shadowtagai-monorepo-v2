# Corpus Guard MVP Implementation Plan

## Executive Summary
**Objective**: Deploy Apertus-style full-text searchable index over all PNKLN training data, logs, and governance decisions.

**Timeline**: 14-21 days
**Tech Stack**: Meilisearch (GCP Cloud Run) + Python ingestor + React UI
**Revenue Tier**: "Governance Replay" ($2-10k MRR per customer)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  DATA SOURCES                                               │
├─────────────────────────────────────────────────────────────┤
│  • Claude async job logs (JSONL via claude_async.sh)       │
│  • Judge#6 reasoning traces (ATP 5-19 decisions)           │
│  • ShadowTag DCT analysis outputs                          │
│  • Kernel Chain decision batches                           │
│  • Customer fine-tune datasets (future)                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  INGESTION PIPELINE (Cloud Run)                             │
├─────────────────────────────────────────────────────────────┤
│  • Triggered on GCS object finalize (Cloud Function)       │
│  • Strips XML tags, normalizes text                        │
│  • Extracts metadata: job_id, owner, timestamp, task_type  │
│  • Flags: toxicity, PII patterns, chemical weapon terms    │
│  • Indexes to Meilisearch with custom analyzer             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  MEILISEARCH CLUSTER (Cloud Run)                            │
├─────────────────────────────────────────────────────────────┤
│  • Single-node deployment (scales to 100TB)                │
│  • Custom analyzer: tokenization + stemming                │
│  • Indexes: full_text, metadata, flags                     │
│  • Search API: phrase queries with slop tolerance          │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  SEARCH UI (Next.js + IAP)                                  │
├─────────────────────────────────────────────────────────────┤
│  • React frontend with phrase search                       │
│  • Filters: date range, task type, owner, flags            │
│  • Results: highlighted snippets + full document view      │
│  • Export: CSV/JSON for compliance audits                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Week-by-Week Plan

### Week 1: Infrastructure Setup
**Owner**: DevOps + Backend

**Deliverables**:
1. Meilisearch Cloud Run deployment
   - Docker image: `getmeili/meilisearch:v1.5`
   - Resources: 2 vCPU, 4GB RAM (scales to 8 vCPU)
   - Persistent disk: 100GB SSD (for index storage)
   - IAM: Service account with Secret Manager access

2. GCS buckets for data sources
   - `pnkln-corpus-guard-raw` (raw logs/traces)
   - `pnkln-corpus-guard-processed` (normalized JSONL)
   - Lifecycle: 90-day retention on raw, indefinite on processed

3. Cloud Function trigger
   - Event: `google.storage.object.finalize`
   - Trigger bucket: `pnkln-corpus-guard-raw`
   - Action: Invoke Cloud Run ingestor

**Acceptance Criteria**:
- Meilisearch accessible via internal VPC
- GCS buckets created with correct IAM bindings
- Cloud Function deploys successfully

---

### Week 2: Ingestion Pipeline
**Owner**: Backend

**Deliverables**:
1. Python ingestor (Cloud Run service)
   ```python
   # src/corpus_guard/ingestor.py

   import re
   from meilisearch import Client
   from google.cloud import storage

   def normalize_text(raw_text: str) -> str:
       """Strip XML tags, normalize whitespace."""
       text = re.sub(r'<[^>]+>', '', raw_text)
       text = re.sub(r'\s+', ' ', text)
       return text.strip()

   def extract_metadata(filename: str) -> dict:
       """Parse job_id, timestamp from filename."""
       # Example: Cor.Claude_Code_6_00143_2025-11-22T15:30:00.jsonl
       parts = filename.split('_')
       return {
           'task_type': parts[0],
           'job_id': parts[1],
           'timestamp': parts[2].replace('.jsonl', '')
       }

   def flag_content(text: str) -> dict:
       """Detect toxicity, PII, sensitive terms."""
       flags = {
           'toxicity': detect_toxicity(text),
           'pii': detect_pii(text),
           'chemical_weapons': 'chemical weapon' in text.lower()
       }
       return flags

   def ingest_document(gcs_uri: str):
       """Main ingestion flow."""
       client = Client('http://meilisearch:7700', 'MASTER_KEY')
       storage_client = storage.Client()

       # Download from GCS
       blob = storage_client.get_bucket('pnkln-corpus-guard-raw').blob(gcs_uri)
       raw_text = blob.download_as_text()

       # Normalize
       normalized = normalize_text(raw_text)
       metadata = extract_metadata(blob.name)
       flags = flag_content(normalized)

       # Index
       document = {
           'id': f"{metadata['task_type']}_{metadata['job_id']}",
           'full_text': normalized,
           'metadata': metadata,
           'flags': flags
       }

       client.index('corpus_guard').add_documents([document])
   ```

2. Custom Meilisearch analyzer
   ```json
   {
     "filterableAttributes": ["metadata.task_type", "metadata.timestamp", "flags.*"],
     "sortableAttributes": ["metadata.timestamp"],
     "searchableAttributes": ["full_text"],
     "rankingRules": [
       "words",
       "typo",
       "proximity",
       "attribute",
       "sort",
       "exactness"
     ]
   }
   ```

**Acceptance Criteria**:
- Ingestor processes JSONL files from GCS
- Documents indexed with correct metadata + flags
- Search API returns results for phrase queries

---

### Week 3: Search UI
**Owner**: Frontend

**Deliverables**:
1. Next.js app with Meilisearch integration
   ```typescript
   // app/search/page.tsx

   'use client';

   import { useState } from 'react';
   import { MeiliSearch } from 'meilisearch';

   export default function SearchPage() {
     const [query, setQuery] = useState('');
     const [results, setResults] = useState([]);

     const client = new MeiliSearch({
       host: 'https://meilisearch.pnkln.internal',
       apiKey: process.env.NEXT_PUBLIC_MEILI_KEY
     });

     const handleSearch = async () => {
       const res = await client.index('corpus_guard').search(query, {
         attributesToHighlight: ['full_text'],
         highlightPreTag: '<mark>',
         highlightPostTag: '</mark>'
       });
       setResults(res.hits);
     };

     return (
       <div>
         <input
           type="text"
           value={query}
           onChange={(e) => setQuery(e.target.value)}
           placeholder="Search governance history..."
         />
         <button onClick={handleSearch}>Search</button>

         {results.map((hit) => (
           <div key={hit.id}>
             <h3>{hit.metadata.task_type} - {hit.metadata.job_id}</h3>
             <p dangerouslySetInnerHTML={{ __html: hit._formatted.full_text }} />
           </div>
         ))}
       </div>
     );
   }
   ```

2. IAP configuration
   - Enable Identity-Aware Proxy on Cloud Run service
   - Restrict access to `@pnkln.ai` email domain
   - OAuth consent screen setup

**Acceptance Criteria**:
- UI accessible via IAP (authenticated users only)
- Phrase search works with highlighted results
- Filters functional (date, task type, flags)

---

## Pre-Load Strategy

**First 100 Judge#6 Runs**:
1. Export existing Judge#6 decisions from Context Index
2. Convert to JSONL format
3. Upload to `pnkln-corpus-guard-raw`
4. Trigger ingestion via Cloud Function

**ShadowTag Logs**:
1. Query BigQuery for all ShadowTag DCT analyses
2. Export as JSONL (one document per analysis)
3. Upload to GCS bucket
4. Verify indexing via search UI

---

## Revenue Model Integration

**Governance Replay Tier** ($2-10k MRR):
- Customer gets dedicated Corpus Guard instance
- Pre-loaded with their training data + decision history
- Full-text search across all model interactions
- Export capability for compliance audits

**Data Passport Product** ($5-20k one-time):
- Signed manifest of every token that touched customer model
- Searchable index (perpetual license)
- Provenance chain (blockchain-backed)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Ingestion latency | <30s per document | Cloud Monitoring |
| Search latency | <500ms p99 | Meilisearch metrics |
| Index size | <10TB (MVP) | GCS bucket size |
| Customer demos | 3 by end of month | Sales pipeline |

---

## Risk Mitigation

**Risk**: Meilisearch can't handle scale
**Mitigation**: Benchmark with 1M documents before customer launch

**Risk**: PII leakage in search results
**Mitigation**: Redaction layer before indexing (regex + NER model)

**Risk**: High GCP costs
**Mitigation**: Start with single-node, scale only after revenue validation

---

## Next Actions

1. **Today**: Provision Meilisearch Cloud Run service
2. **This week**: Build Python ingestor + Cloud Function trigger
3. **Next week**: Deploy search UI behind IAP
4. **End of month**: Dogfood internally + first customer demo
