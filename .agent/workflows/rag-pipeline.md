---
description: Build retrieval-augmented generation pipelines
---

# RAG Pipeline

I will help you build a retrieval-augmented generation (RAG) pipeline.

## Guardrails
- Start simple, optimize later
- Measure retrieval quality before optimizing generation
- Handle empty results gracefully
- Consider cost and latency
- Prefer LanceDB for local/sovereign deployments (per monorepo doctrine)
- Use the `lancedb-rag-automator` skill for automated ingestion

## Steps

### 1. Understand Requirements
Ask clarifying questions:
- What data sources need indexing?
- What types of queries will users make?
- Real-time or batch processing?
- Any existing vector store setup?
- Local-only (Apple Silicon) or cloud (Vertex AI)?

### 2. Design Pipeline
Components to set up:
- **Document Loader**: Ingest sources (files, URLs, APIs)
- **Text Splitter**: Chunk documents (respect token limits)
- **Embeddings**: Generate vectors (choose model: text-embedding-004, local MLX, etc.)
- **Vector Store**: Store and query (LanceDB local or AlloyDB cloud)
- **Retriever**: Find relevant chunks (configure k, threshold)
- **Generator**: Create responses (Gemini, Claude, local Gemma)

### 3. Set Up Components
Configure each piece:
- Choose embedding model (consider cost vs quality: `text-embedding-004` for cloud, `all-MiniLM-L6-v2` for local)
- Select vector database (LanceDB for sovereign, Pinecone/Chroma for managed)
- Set chunk size (512-1024 tokens) and overlap (10-20%)
- Configure retrieval parameters (top-k, MMR diversity)

### 4. Implement Pipeline
Build the flow:
- Load and process documents
- Generate embeddings
- Store in vector database
- Create retrieval chain
- Connect to LLM for generation
- Add source grounding (citation with character offsets if using langextract pattern)

### 5. Optimize
Improve quality:
- Tune chunk size (smaller = more precise, larger = more context)
- Adjust retrieval k (start with 5, increase if coverage is poor)
- Add reranking (cross-encoder or Gemini-based)
- Implement hybrid search (keyword + semantic)
- Add caching for repeated queries (hash-based cache pattern from langextract)

### 6. Verify
// turbo
- Test with sample queries
- Check retrieval relevance (precision@k, recall@k)
- Verify generated responses cite sources accurately
- Measure latency and cost per query

## Principles
- Quality of retrieval = quality of output
- Start with small dataset, iterate
- Monitor and measure continuously
- Citation-grade grounding is the gold standard
