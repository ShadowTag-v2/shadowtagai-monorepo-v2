# Gemini File Search Grounding for PNKLN

## Overview

Gemini's file search (grounding) feature provides a managed alternative to building custom RAG systems. Instead of manually creating embeddings and managing vector databases, you upload files directly to Gemini and query them with natural language.

**Key Features:**
- 🚀 Automatic chunking and embedding
- 📄 Multi-format support (PDF, DOCX, PPTX, images, text)
- 🎯 Built-in grounding (reduces hallucinations)
- 💰 No separate embedding costs
- 🔄 Simple file management

## When to Use Gemini Grounding

### ✅ Best For:
- **Quick prototyping** - Test legal Q&A without infrastructure setup
- **Multi-format documents** - PDFs, Word docs, presentations
- **Ad-hoc analysis** - One-off contract reviews, policy checks
- **Exploratory queries** - Research and discovery
- **Low-maintenance** - Don't want to manage vector databases

### ⚠️ Trade-offs:
- Less control over chunking strategy
- Vendor lock-in to Google
- Cannot run offline
- Limited customization of ranking

## Custom RAG vs Gemini Grounding

| Aspect | Custom RAG (pnkln.rag) | Gemini Grounding |
|--------|------------------------|------------------|
| **Setup** | Complex (embeddings, vectors, storage) | Simple (upload files) |
| **Chunking** | Manual control | Automatic |
| **Cost** | Pay per embedding + storage | Included in generation |
| **File Types** | Text only | PDF, DOCX, images, etc. |
| **Control** | Full (chunking, scoring, filters) | Limited |
| **Portability** | High (open-source compatible) | Google-locked |
| **Scale** | Optimizable for production | Managed by Google |
| **Best Use** | Production semantic search | Rapid prototyping |

## Hybrid Strategy for PNKLN

**Recommended approach**: Use **both** systems for different purposes:

```
┌─────────────────────────────────────────────────────┐
│                  PNKLN Stack                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Ingestion Layer                                    │
│  ├─── Gemini Grounding ──→ Quick classification    │
│  └─── Custom RAG build ──→ Production indexes      │
│                                                     │
│  Query Layer                                        │
│  ├─── Gemini Grounding ──→ Ad-hoc Q&A             │
│  └─── Custom RAG ────────→ Production search       │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Use Gemini Grounding for:**
1. Ingestion tier classification (quick AI assessment)
2. Contract review Q&A (user-uploaded docs)
3. Policy compliance checks
4. Exploratory legal research

**Use Custom RAG for:**
1. Production semantic search (optimized)
2. Large-scale document retrieval
3. Fine-tuned legal text chunking
4. Offline/air-gapped deployments

## Quick Start

### 1. Set API Key

```bash
export GOOGLE_API_KEY="your-api-key"
```

Or add to `.env`:
```
GOOGLE_API_KEY=your-api-key
```

### 2. Direct Python Usage

```python
from app.pnkln.gemini_grounding import GeminiFileSearchRAG

# Initialize
rag = GeminiFileSearchRAG()

# Upload documents
rag.upload_file("contract.pdf")
rag.upload_text("Policy text here...", "company_policy.txt")

# Query with grounding
result = rag.query_with_grounding(
    query="What are the payment terms?",
    temperature=0.1  # Lower = more factual
)

print(result['answer'])
```

### 3. API Usage

Start the server:
```bash
python -m app.main
```

Upload a file:
```bash
curl -X POST http://localhost:8000/api/v1/grounding/upload/file \
  -F "file=@contract.pdf"
```

Upload text:
```bash
curl -X POST http://localhost:8000/api/v1/grounding/upload/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Contract payment terms: Net 30 days",
    "name": "contract_snippet.txt"
  }'
```

Query:
```bash
curl -X POST http://localhost:8000/api/v1/grounding/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the payment terms?",
    "temperature": 0.1
  }'
```

List files:
```bash
curl http://localhost:8000/api/v1/grounding/files
```

## API Endpoints

All endpoints are prefixed with `/api/v1/grounding`

### Upload File
**POST** `/upload/file`

Upload a file for grounding.

**Supported formats:**
- Documents: PDF, TXT, MD, HTML, DOCX, PPTX, XLSX
- Images: PNG, JPG, JPEG, GIF, WEBP

**Request:**
```
multipart/form-data
file: <file>
```

**Response:**
```json
{
  "status": "uploaded",
  "file_name": "files/abc123",
  "display_name": "contract.pdf",
  "mime_type": "application/pdf",
  "uri": "https://generativelanguage.googleapis.com/..."
}
```

### Upload Text
**POST** `/upload/text`

Upload raw text as a document.

**Request:**
```json
{
  "text": "Document content here...",
  "name": "my_document.txt"
}
```

**Response:**
```json
{
  "status": "uploaded",
  "file_name": "files/xyz789",
  "display_name": "my_document.txt"
}
```

### Query with Grounding
**POST** `/query`

Query uploaded files with natural language.

**Request:**
```json
{
  "query": "What are the termination clauses?",
  "file_names": ["contract.pdf"],  // Optional: specific files
  "temperature": 0.1  // Lower = more factual
}
```

**Response:**
```json
{
  "answer": "The termination clause allows either party...",
  "grounding_metadata": {
    "files_used": ["contract.pdf"],
    "file_count": 1
  }
}
```

### List Files
**GET** `/files`

List all uploaded files.

**Response:**
```json
{
  "files": [
    {
      "name": "files/abc123",
      "display_name": "contract.pdf",
      "mime_type": "application/pdf",
      "uri": "https://..."
    }
  ],
  "count": 1
}
```

### Delete File
**DELETE** `/files/{file_name}`

Delete a specific file.

**Response:**
```json
{
  "status": "deleted",
  "file_name": "files/abc123"
}
```

### Clear All Files
**DELETE** `/files`

Delete all uploaded files.

**Response:**
```json
{
  "status": "cleared",
  "files_deleted": 3
}
```

## Use Cases

### 1. Contract Review Q&A

```python
rag = GeminiFileSearchRAG()

# Upload contracts
rag.upload_file("service_agreement.pdf")
rag.upload_file("msa.pdf")
rag.upload_file("sow.pdf")

# Ask questions
questions = [
    "What are the payment terms across all contracts?",
    "Are there any liability caps?",
    "What are the termination provisions?",
    "Do these contracts have arbitration clauses?"
]

for q in questions:
    result = rag.query_with_grounding(query=q)
    print(f"Q: {q}")
    print(f"A: {result['answer']}\n")
```

### 2. Policy Compliance Check

```python
# Upload company policy
rag.upload_text(company_policy, "legal_policy.txt")

# Upload contract to review
rag.upload_file("vendor_contract.pdf")

# Check compliance
result = rag.query_with_grounding(
    query="""Does the vendor contract comply with our legal policy?
    List any non-compliant items."""
)

print(result['answer'])
```

### 3. Multi-Contract Analysis

```python
# Batch upload
contracts = [
    "q1_contracts/contract_1.pdf",
    "q1_contracts/contract_2.pdf",
    "q1_contracts/contract_3.pdf",
]
rag.batch_upload_legal_docs(contracts)

# Comparative analysis
result = rag.query_with_grounding(
    query="Compare payment terms across all Q1 contracts. Which has the shortest payment period?"
)
```

### 4. Due Diligence Research

```python
# Upload target company docs
rag.upload_file("financials.pdf")
rag.upload_file("material_contracts.pdf")
rag.upload_file("ip_assignments.pdf")

# Research queries
rag.query_with_grounding("What are the key IP assets?")
rag.query_with_grounding("Are there any pending litigation mentions?")
rag.query_with_grounding("What are the largest contract obligations?")
```

## Integration with Ingestion Layer

Add grounding to the nightly ingestion pipeline:

```python
# In scripts/run_ingestion.py

from app.pnkln.gemini_grounding import GeminiFileSearchRAG

rag_grounding = GeminiFileSearchRAG()

# During ingestion
for source in sources:
    content = fetch_content(source)

    # Option 1: Use grounding for classification
    rag_grounding.upload_text(content, f"{source.id}.txt")
    classification = rag_grounding.query_with_grounding(
        query="Is this legal content Tier 1 (authoritative), Tier 2 (semi-authoritative), or Tier 3 (general)? Explain."
    )

    # Option 2: Build both grounding AND custom RAG
    # Grounding for ad-hoc queries, RAG for production
```

## Cost Considerations

**Gemini Grounding Pricing** (as of 2025):
- File storage: Included in API quota
- Queries: Standard Gemini API rates
- No separate embedding costs (vs custom RAG)

**Cost Comparison Example:**

Custom RAG (1000 documents, 1000 queries/day):
- Embeddings: ~$X/day
- Storage: GCS costs
- Queries: Gemini generation costs
- **Total**: ~$Y/month

Gemini Grounding (same workload):
- Embeddings: Included
- Storage: Included (up to quota)
- Queries: Gemini generation costs
- **Total**: ~$Z/month (potentially lower for small-medium scale)

## Limitations

1. **File Size Limits**: Check current API quotas
2. **File Count Limits**: Per-account quotas apply
3. **No Offline Mode**: Requires internet connection
4. **Limited Chunking Control**: Can't customize chunking strategy
5. **Vendor Lock-in**: Google-specific (not portable to other LLMs)

## Best Practices

1. **Organize by Project**: Use separate RAG instances per project/client
2. **Clear Unused Files**: Delete files when done to save quota
3. **Temperature Control**: Use 0.1-0.3 for factual legal queries
4. **Specific Queries**: More specific questions = better grounding
5. **Hybrid Approach**: Combine with custom RAG for production use

## Troubleshooting

**Error: API key not configured**
```bash
export GOOGLE_API_KEY="your-key"
```

**Error: File upload failed**
- Check file format (PDF, DOCX, TXT supported)
- Verify file size is within limits
- Ensure file is not corrupted

**Error: Quota exceeded**
- Delete unused files
- Check API quota in Google Cloud Console
- Consider upgrading quota if needed

**Poor quality answers**
- Make queries more specific
- Ensure uploaded files are relevant
- Try lower temperature (0.1-0.2)
- Check that files uploaded successfully

## Migration from Custom RAG

If migrating from custom RAG:

```python
# Old (custom RAG)
from app.pnkln.rag import rag_build, rag_query

items = [{"k": "1", "t": "text1"}, {"k": "2", "t": "text2"}]
rag_build(items, "index.npy", "index.json")
answer = rag_query("query", "index.npy", "index.json")

# New (Gemini grounding)
from app.pnkln.gemini_grounding import GeminiFileSearchRAG

rag = GeminiFileSearchRAG()
rag.upload_text("text1", "doc1.txt")
rag.upload_text("text2", "doc2.txt")
result = rag.query_with_grounding("query")
answer = result['answer']
```

**Keep both!** Use Gemini for prototyping, custom RAG for production.

## See Also

- [Custom RAG Documentation](README.md#rag-semantic-search)
- [Ingestion Layer](INGESTION.md)
- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Example Demo](examples/gemini_grounding_demo.py)
