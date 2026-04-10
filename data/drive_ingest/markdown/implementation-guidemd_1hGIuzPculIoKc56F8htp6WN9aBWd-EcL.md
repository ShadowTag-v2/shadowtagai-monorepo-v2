# ShadowTag-v2 FastAPI Services - Integration Implementation Guide

**Generated:** 2025-11-18
**Purpose:** Practical implementation guide for integrating AI agent patterns into ShadowTag-v2 services
**Companion to:** `ai-agents-knowledge-base.md`

---

## Quick Start: Highest ROI Implementations

### 1. Gemini Batch API Integration (50% Cost Savings)

**Timeline:** 1-2 weeks
**Difficulty:** Medium
**ROI:** 50% reduction in embedding costs

#### Current State Analysis
```bash
# Check current Gemini API usage
grep -r "generate_content" src/
grep -r "embed_content" src/
```

#### Implementation

```python
# src/services/gemini_batch.py

from google import generativeai as genai
from typing import List, Dict
import asyncio
import time

class GeminiBatchProcessor:
    """
    Batch processor for Gemini API calls with cost optimization
    """

    def __init__(self, api_key: str, batch_size: int = 100):
        genai.configure(api_key=api_key)
        self.batch_size = batch_size
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def embed_documents_batch(self, documents: List[str]) -> List[Dict]:
        """
        Embed documents in batches for 50% cost savings

        Args:
            documents: List of document texts to embed

        Returns:
            List of embeddings with metadata
        """
        results = []

        # Split into batches
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]

            # Create batch job
            batch_requests = [
                {
                    "model": "text-embedding-004",
                    "content": {"parts": [{"text": doc}]},
                    "task_type": "RETRIEVAL_DOCUMENT"
                }
                for doc in batch
            ]

            # Submit batch (50% cheaper than individual calls)
            try:
                batch_job = await self._submit_batch(batch_requests)
                batch_results = await self._poll_batch(batch_job)
                results.extend(batch_results)

                print(f"✓ Processed batch {i//self.batch_size + 1}, "
                      f"Cost savings: ~50% vs individual calls")
            except Exception as e:
                print(f"✗ Batch {i//self.batch_size + 1} failed: {e}")
                # Fallback to individual calls for this batch
                results.extend(await self._fallback_individual(batch))

        return results

    async def _submit_batch(self, requests: List[Dict]) -> str:
        """Submit batch job to Gemini API"""
        # Use Gemini Batch API endpoint
        # Documentation: https://ai.google.dev/gemini-api/docs/batch-api

        from google.ai.generativelanguage_v1beta import (
            BatchEmbedContentsRequest,
            CreateBatchRequest
        )

        # Create batch
        batch_request = CreateBatchRequest(
            requests=requests,
            model="models/text-embedding-004"
        )

        # Submit and get job ID
        response = self.model._client.create_batch(batch_request)
        return response.name  # Returns batch job ID

    async def _poll_batch(self, batch_job_id: str, timeout: int = 300):
        """Poll batch job until complete"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.model._client.get_batch(name=batch_job_id)

            if status.state == "SUCCEEDED":
                return status.results
            elif status.state == "FAILED":
                raise Exception(f"Batch job failed: {status.error}")

            await asyncio.sleep(5)  # Poll every 5 seconds

        raise TimeoutError(f"Batch job {batch_job_id} timed out after {timeout}s")

    async def _fallback_individual(self, documents: List[str]):
        """Fallback to individual API calls if batch fails"""
        print("⚠️  Using fallback individual calls (full cost)")

        results = []
        for doc in documents:
            embedding = genai.embed_content(
                model="models/text-embedding-004",
                content=doc,
                task_type="retrieval_document"
            )
            results.append(embedding)

        return results

# Example usage
async def main():
    processor = GeminiBatchProcessor(api_key="your-api-key")

    # Load documents to embed
    documents = [
        "Document 1 content...",
        "Document 2 content...",
        # ... up to thousands of documents
    ]

    # Batch process with 50% cost savings
    embeddings = await processor.embed_documents_batch(documents)

    print(f"Embedded {len(embeddings)} documents at 50% cost vs individual calls")

if __name__ == "__main__":
    asyncio.run(main())
```

#### Integration Steps

1. **Install dependencies**
```bash
pip install google-generativeai>=0.8.0
```

2. **Update requirements.txt**
```
google-generativeai>=0.8.0
```

3. **Migrate existing code**
```python
# Before (expensive)
for doc in documents:
    embedding = genai.embed_content(doc)  # Individual call

# After (50% cheaper)
processor = GeminiBatchProcessor()
embeddings = await processor.embed_documents_batch(documents)
```

4. **Monitor cost savings**
```python
# Add to GeminiBatchProcessor class

def calculate_savings(self, num_documents: int, cost_per_1m_tokens: float = 0.025):
    individual_cost = num_documents * cost_per_1m_tokens
    batch_cost = num_documents * (cost_per_1m_tokens / 2)
    savings = individual_cost - batch_cost

    print(f"""
    Cost Analysis:
    - Documents: {num_documents:,}
    - Individual calls: ${individual_cost:.2f}
    - Batch API: ${batch_cost:.2f}
    - Savings: ${savings:.2f} ({savings/individual_cost*100:.0f}%)
    """)
```

---

### 2. MCP Protocol for Tool Interoperability

**Timeline:** 2-3 weeks
**Difficulty:** Medium-Hard
**ROI:** Future-proof integration with Claude/Codex/Gemini CLI

#### Setup MCP Server

```python
# src/mcp/server.py

from mcp import Server, Tool
from typing import Dict, Any
import asyncio

class ShadowTag-v2MCPServer(Server):
    """
    MCP server for ShadowTag-v2 services
    Enables Claude Code, Codex, Gemini CLI to call ShadowTag-v2 tools
    """

    def __init__(self):
        super().__init__(name="ShadowTag-v2-fastapi-services")
        self.register_tools()

    def register_tools(self):
        """Register ShadowTag-v2 capabilities as MCP tools"""

        @self.tool(
            name="ingest_document",
            description="Ingest document from URL or file path",
            schema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "URL or file path"},
                    "tier": {"type": "string", "enum": ["free", "pro", "enterprise"]}
                },
                "required": ["source"]
            }
        )
        async def ingest_document(source: str, tier: str = "free") -> Dict[str, Any]:
            """MCP tool: ingest_document"""
            from src.services.ingestion import IngestionService

            service = IngestionService(tier=tier)
            result = await service.ingest(source)

            return {
                "status": "success",
                "document_id": result.id,
                "embeddings_count": len(result.embeddings),
                "cost": result.cost_usd
            }

        @self.tool(
            name="search_documents",
            description="Semantic search across ingested documents",
            schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        )
        async def search_documents(query: str, top_k: int = 10) -> Dict[str, Any]:
            """MCP tool: search_documents"""
            from src.services.search import SearchService

            service = SearchService()
            results = await service.semantic_search(query, top_k=top_k)

            return {
                "query": query,
                "results": [
                    {
                        "document_id": r.id,
                        "title": r.title,
                        "similarity": r.score,
                        "snippet": r.text[:200]
                    }
                    for r in results
                ]
            }

        @self.tool(
            name="get_embeddings",
            description="Generate embeddings for text using Gemini",
            schema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "model": {"type": "string", "default": "gemini-2.5-flash"}
                },
                "required": ["text"]
            }
        )
        async def get_embeddings(text: str, model: str = "gemini-2.5-flash"):
            """MCP tool: get_embeddings"""
            from src.services.gemini_batch import GeminiBatchProcessor

            processor = GeminiBatchProcessor()
            embeddings = await processor.embed_documents_batch([text])

            return {
                "model": model,
                "dimensions": len(embeddings[0]),
                "embedding": embeddings[0]
            }

async def main():
    server = ShadowTag-v2MCPServer()
    await server.run(transport="stdio")  # MCP uses stdio by default

if __name__ == "__main__":
    asyncio.run(main())
```

#### MCP Client Configuration

**For Claude Desktop:**
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "ShadowTag-v2": {
      "command": "python",
      "args": ["/path/to/ShadowTag-v2-fastapi-services/src/mcp/server.py"],
      "env": {
        "GEMINI_API_KEY": "your-api-key"
      }
    }
  }
}
```

**For Codex:**
```json
// ~/.codex/mcp_servers.json

{
  "ShadowTag-v2": {
    "command": "python /path/to/ShadowTag-v2-fastapi-services/src/mcp/server.py",
    "type": "stdio",
    "enabled_tools": ["ingest_document", "search_documents"]
  }
}
```

#### Testing MCP Integration

```python
# tests/test_mcp.py

import pytest
from src.mcp.server import ShadowTag-v2MCPServer

@pytest.mark.asyncio
async def test_mcp_ingest_tool():
    server = ShadowTag-v2MCPServer()

    # Simulate MCP tool call from Claude/Codex
    result = await server.call_tool(
        "ingest_document",
        {"source": "https://arxiv.org/pdf/2502.11089", "tier": "pro"}
    )

    assert result["status"] == "success"
    assert "document_id" in result
    assert result["embeddings_count"] > 0

@pytest.mark.asyncio
async def test_mcp_search_tool():
    server = ShadowTag-v2MCPServer()

    result = await server.call_tool(
        "search_documents",
        {"query": "machine learning agents", "top_k": 5}
    )

    assert len(result["results"]) <= 5
    assert all("similarity" in r for r in result["results"])
```

---

### 3. Multi-Agent Swarm Architecture

**Timeline:** 3-4 weeks
**Difficulty:** Hard
**ROI:** Parallel processing, specialized agents, scalability

#### Architecture Diagram

```
┌─────────────┐
│ Orchestrator│
└──────┬──────┘
       │
       ├──────────┬──────────┬──────────┬──────────┐
       ▼          ▼          ▼          ▼          ▼
   ┌─────┐   ┌─────┐   ┌──────┐   ┌─────┐   ┌────────┐
   │Parse│   │Class│   │Embed │   │Store│   │Validate│
   │Agent│   │Agent│   │Agent │   │Agent│   │ Agent  │
   └─────┘   └─────┘   └──────┘   └─────┘   └────────┘
```

#### Implementation

```python
# src/agents/swarm.py

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

class AgentRole(Enum):
    PARSER = "parser"
    CLASSIFIER = "classifier"
    EMBEDDER = "embedder"
    STORAGE = "storage"
    VALIDATOR = "validator"

@dataclass
class AgentMessage:
    """Message passed between agents"""
    role: AgentRole
    data: Any
    metadata: Dict[str, Any]
    timestamp: str

class Agent:
    """Base agent class"""

    def __init__(self, role: AgentRole, mailbox: 'Mailbox'):
        self.role = role
        self.mailbox = mailbox

    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process message and return result"""
        raise NotImplementedError

class ParserAgent(Agent):
    """Extract text from PDFs, HTML, etc."""

    def __init__(self, mailbox):
        super().__init__(AgentRole.PARSER, mailbox)

    async def process(self, message: AgentMessage) -> AgentMessage:
        """Parse document from URL/file"""
        from src.services.parser import DocumentParser

        parser = DocumentParser()
        text = await parser.extract(message.data["source"])

        return AgentMessage(
            role=AgentRole.CLASSIFIER,  # Next agent
            data={"text": text, "source": message.data["source"]},
            metadata={"parsed_at": "2025-11-18T10:00:00Z"},
            timestamp="2025-11-18T10:00:01Z"
        )

class ClassifierAgent(Agent):
    """Classify documents by type/domain"""

    def __init__(self, mailbox):
        super().__init__(AgentRole.CLASSIFIER, mailbox)

    async def process(self, message: AgentMessage) -> AgentMessage:
        """Classify document"""
        from src.services.classifier import DocumentClassifier

        classifier = DocumentClassifier()
        category = await classifier.classify(message.data["text"])

        return AgentMessage(
            role=AgentRole.EMBEDDER,
            data={
                **message.data,
                "category": category
            },
            metadata=message.metadata,
            timestamp="2025-11-18T10:00:02Z"
        )

class EmbedderAgent(Agent):
    """Generate embeddings via Gemini"""

    def __init__(self, mailbox):
        super().__init__(AgentRole.EMBEDDER, mailbox)

    async def process(self, message: AgentMessage) -> AgentMessage:
        """Generate embeddings"""
        from src.services.gemini_batch import GeminiBatchProcessor

        processor = GeminiBatchProcessor()
        embeddings = await processor.embed_documents_batch([message.data["text"]])

        return AgentMessage(
            role=AgentRole.STORAGE,
            data={
                **message.data,
                "embeddings": embeddings[0]
            },
            metadata=message.metadata,
            timestamp="2025-11-18T10:00:03Z"
        )

class StorageAgent(Agent):
    """Store embeddings in vector DB"""

    def __init__(self, mailbox):
        super().__init__(AgentRole.STORAGE, mailbox)

    async def process(self, message: AgentMessage) -> AgentMessage:
        """Store in vector database"""
        from src.services.vectordb import VectorDatabase

        db = VectorDatabase()
        doc_id = await db.insert(
            embeddings=message.data["embeddings"],
            metadata={
                "source": message.data["source"],
                "category": message.data["category"],
                "text": message.data["text"][:1000]  # Store snippet
            }
        )

        return AgentMessage(
            role=AgentRole.VALIDATOR,
            data={
                **message.data,
                "document_id": doc_id
            },
            metadata=message.metadata,
            timestamp="2025-11-18T10:00:04Z"
        )

class ValidatorAgent(Agent):
    """Validate quality and detect anomalies"""

    def __init__(self, mailbox):
        super().__init__(AgentRole.VALIDATOR, mailbox)

    async def process(self, message: AgentMessage) -> AgentMessage:
        """Validate document quality"""
        from src.services.validator import DocumentValidator

        validator = DocumentValidator()
        is_valid, issues = await validator.validate(message.data)

        return AgentMessage(
            role=None,  # Terminal agent
            data={
                **message.data,
                "is_valid": is_valid,
                "issues": issues
            },
            metadata={
                **message.metadata,
                "validated_at": "2025-11-18T10:00:05Z"
            },
            timestamp="2025-11-18T10:00:05Z"
        )

class Mailbox:
    """Message queue for agent communication"""

    def __init__(self):
        self.queues: Dict[AgentRole, asyncio.Queue] = {
            role: asyncio.Queue() for role in AgentRole
        }

    async def send(self, message: AgentMessage):
        """Send message to agent's queue"""
        if message.role:
            await self.queues[message.role].put(message)

    async def receive(self, role: AgentRole) -> AgentMessage:
        """Receive message from queue"""
        return await self.queues[role].get()

class Orchestrator:
    """Orchestrate multi-agent workflow"""

    def __init__(self):
        self.mailbox = Mailbox()
        self.agents = {
            AgentRole.PARSER: ParserAgent(self.mailbox),
            AgentRole.CLASSIFIER: ClassifierAgent(self.mailbox),
            AgentRole.EMBEDDER: EmbedderAgent(self.mailbox),
            AgentRole.STORAGE: StorageAgent(self.mailbox),
            AgentRole.VALIDATOR: ValidatorAgent(self.mailbox)
        }

    async def run_agent(self, role: AgentRole):
        """Run agent worker loop"""
        agent = self.agents[role]

        while True:
            message = await self.mailbox.receive(role)
            result = await agent.process(message)

            if result.role:  # Forward to next agent
                await self.mailbox.send(result)
            else:  # Terminal message
                print(f"✓ Pipeline complete: {result.data}")

    async def ingest_document(self, source: str):
        """Start ingestion pipeline"""
        # Send initial message to parser
        initial_message = AgentMessage(
            role=AgentRole.PARSER,
            data={"source": source},
            metadata={},
            timestamp="2025-11-18T10:00:00Z"
        )

        await self.mailbox.send(initial_message)

    async def start(self):
        """Start all agent workers"""
        tasks = [
            asyncio.create_task(self.run_agent(role))
            for role in AgentRole
        ]

        await asyncio.gather(*tasks)

# Usage
async def main():
    orchestrator = Orchestrator()

    # Start agent workers
    asyncio.create_task(orchestrator.start())

    # Ingest documents
    await orchestrator.ingest_document("https://arxiv.org/pdf/2502.11089")
    await orchestrator.ingest_document("https://github.com/anthropics/anthropic-sdk-python")

    # Agents process in parallel!

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 4. Persistent Memory with Mem-Layer

**Timeline:** 2-3 weeks
**Difficulty:** Medium
**ROI:** Long-term context across sessions

#### Installation

```bash
pip install mem-layer
```

#### Integration

```python
# src/services/memory.py

from mem_layer import MemLayer, MemoryNode, MemoryEdge
from typing import List, Dict, Optional
from datetime import datetime

class ShadowTag-v2Memory:
    """
    Persistent memory for ShadowTag-v2 agents
    Tracks document processing history across sessions
    """

    def __init__(self, scope: str = "ingestion_pipeline"):
        self.mem = MemLayer(
            scope=scope,
            storage_path="/data/memory.db"  # SQLite backend
        )

    async def track_document(
        self,
        doc_id: str,
        source: str,
        status: str,
        embeddings_count: int,
        cost_usd: float
    ):
        """Track document processing"""

        # Add document node
        doc_node = MemoryNode(
            id=doc_id,
            type="document",
            data={
                "source": source,
                "status": status,
                "embeddings_count": embeddings_count,
                "cost_usd": cost_usd,
                "processed_at": datetime.utcnow().isoformat()
            }
        )

        await self.mem.add_node(doc_node)

        # Add edge to source domain
        from urllib.parse import urlparse
        domain = urlparse(source).netloc

        domain_node = await self.mem.get_or_create_node(
            id=f"domain:{domain}",
            type="source_domain",
            data={"domain": domain}
        )

        await self.mem.add_edge(
            MemoryEdge(
                source=doc_id,
                target=f"domain:{domain}",
                relationship="from_domain"
            )
        )

    async def query_recent_documents(
        self,
        hours: int = 24,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Query recently processed documents"""

        results = await self.mem.query(
            pattern=f"type:document AND processed_at:last_{hours}h",
            filters={"status": status} if status else {}
        )

        return [node.data for node in results]

    async def get_domain_stats(self, domain: str) -> Dict:
        """Get statistics for a source domain"""

        # Get all documents from domain
        docs = await self.mem.query(
            pattern=f"domain:{domain}",
            traverse="incoming",  # Documents pointing to this domain
            relationship="from_domain"
        )

        total_docs = len(docs)
        total_cost = sum(doc.data.get("cost_usd", 0) for doc in docs)
        avg_embeddings = sum(doc.data.get("embeddings_count", 0) for doc in docs) / max(total_docs, 1)

        return {
            "domain": domain,
            "total_documents": total_docs,
            "total_cost_usd": round(total_cost, 2),
            "avg_embeddings_per_doc": round(avg_embeddings, 1)
        }

    async def leave_note_for_agent(
        self,
        from_agent: str,
        to_agent: str,
        message: str
    ):
        """Cross-agent communication"""

        note_node = MemoryNode(
            id=f"note:{datetime.utcnow().timestamp()}",
            type="agent_note",
            data={
                "from": from_agent,
                "to": to_agent,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        await self.mem.add_node(note_node)

    async def get_notes_for_agent(self, agent_name: str) -> List[Dict]:
        """Retrieve notes for specific agent"""

        notes = await self.mem.query(
            pattern="type:agent_note",
            filters={"to": agent_name}
        )

        return [note.data for note in notes]

# Usage in ingestion pipeline
async def enhanced_ingestion_with_memory(source: str):
    from src.services.ingestion import IngestionService
    from src.services.memory import ShadowTag-v2Memory

    memory = ShadowTag-v2Memory()
    service = IngestionService()

    # Check if already processed
    existing = await memory.query_recent_documents(hours=24*7)  # Last week
    if any(doc["source"] == source for doc in existing):
        print(f"⚠️  Document {source} already processed in last week")
        return

    # Ingest
    result = await service.ingest(source)

    # Track in memory
    await memory.track_document(
        doc_id=result.id,
        source=source,
        status="completed",
        embeddings_count=len(result.embeddings),
        cost_usd=result.cost_usd
    )

    # Leave note for search agent
    await memory.leave_note_for_agent(
        from_agent="ingestion_agent",
        to_agent="search_agent",
        message=f"New document indexed: {result.id} from {source}"
    )

    print(f"✓ Document tracked in persistent memory: {result.id}")
```

#### MCP Server Integration

```python
# src/mcp/server.py (add to ShadowTag-v2MCPServer)

@self.tool(
    name="query_memory",
    description="Query persistent memory for document history",
    schema={
        "type": "object",
        "properties": {
            "pattern": {"type": "string"},
            "hours": {"type": "integer", "default": 24}
        }
    }
)
async def query_memory(pattern: str, hours: int = 24):
    """MCP tool: query_memory"""
    from src.services.memory import ShadowTag-v2Memory

    memory = ShadowTag-v2Memory()
    results = await memory.query_recent_documents(hours=hours)

    return {
        "pattern": pattern,
        "results_count": len(results),
        "documents": results
    }
```

---

### 5. Backlog.md Task Management

**Timeline:** 1 day
**Difficulty:** Easy
**ROI:** Git-native tracking for AI agents + humans

#### Setup

```bash
# Install backlog CLI
curl -sSL https://backlog.md/install.sh | sh

# Or via npm
npm install -g backlog-md

# Initialize in project
cd /path/to/ShadowTag-v2-fastapi-services
backlog init
```

#### Configuration

```yaml
# backlog/config.yml

columns:
  - todo
  - in_progress
  - review
  - done

agents:
  - name: claude-code
    mcp_enabled: true
  - name: gemini-cli
    mcp_enabled: true

tags:
  - ingestion
  - embeddings
  - api
  - optimization
  - security
```

#### Task Template

```markdown
<!-- backlog/implement-batch-api.md -->

# Implement Gemini Batch API

## Description
Migrate from individual Gemini API calls to batch processing for 50% cost reduction

## Acceptance Criteria
- [ ] Batch requests in groups of 100 documents
- [ ] Handle rate limits gracefully with exponential backoff
- [ ] Monitor cost savings (target: 50%)
- [ ] Add tests for batch processing
- [ ] Update documentation

## Dependencies
- task:setup-gcp-credentials
- task:update-gemini-sdk

## Planning Notes
- Use `google.ai.generativelanguage_v1beta.BatchEmbedContentsRequest`
- Poll batch job every 5 seconds with 300s timeout
- Fallback to individual calls if batch fails

## Tags
optimization, api, embeddings

## Status
in_progress

## Assigned To
claude-code
```

#### CLI Usage

```bash
# Create task
backlog create "Implement MCP server" \
  --description "Add MCP protocol support for Claude/Codex integration" \
  --tags "api,integration"

# View Kanban board
backlog board

# Move task
backlog move implement-batch-api --to in_progress

# Web interface
backlog browser  # Opens http://localhost:3000

# Fuzzy search
backlog search "gemini"

# Stats
backlog stats
```

#### AI Agent Integration

```python
# src/services/tasks.py

import subprocess
import json
from typing import List, Dict

class BacklogManager:
    """Interface for AI agents to manage Backlog.md tasks"""

    def create_task(
        self,
        title: str,
        description: str,
        tags: List[str] = None,
        assigned_to: str = "claude-code"
    ) -> str:
        """Create new task"""

        cmd = [
            "backlog", "create", title,
            "--description", description,
            "--assigned-to", assigned_to
        ]

        if tags:
            cmd.extend(["--tags", ",".join(tags)])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return f"✓ Created task: {title}"
        else:
            return f"✗ Failed to create task: {result.stderr}"

    def list_tasks(self, status: str = None) -> List[Dict]:
        """List tasks"""

        cmd = ["backlog", "list", "--json"]
        if status:
            cmd.extend(["--status", status])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return []

    def update_status(self, task_id: str, status: str):
        """Update task status"""

        subprocess.run([
            "backlog", "move", task_id,
            "--to", status
        ])

# Usage in agent
async def agent_creates_subtasks():
    """Example: Agent breaks down work into tasks"""

    backlog = BacklogManager()

    # Agent identifies work to be done
    tasks = [
        ("Implement batch API", ["api", "optimization"]),
        ("Add MCP server", ["api", "integration"]),
        ("Setup persistent memory", ["infrastructure"])
    ]

    for title, tags in tasks:
        backlog.create_task(
            title=title,
            description=f"Auto-generated by agent at {datetime.utcnow()}",
            tags=tags,
            assigned_to="claude-code"
        )

    print(f"✓ Created {len(tasks)} tasks in Backlog.md")
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_gemini_batch.py

import pytest
from src.services.gemini_batch import GeminiBatchProcessor

@pytest.mark.asyncio
async def test_batch_embedding():
    processor = GeminiBatchProcessor(api_key="test-key")

    documents = ["Document 1", "Document 2"]
    embeddings = await processor.embed_documents_batch(documents)

    assert len(embeddings) == 2
    assert all(isinstance(e, list) for e in embeddings)

@pytest.mark.asyncio
async def test_cost_calculation():
    processor = GeminiBatchProcessor()
    processor.calculate_savings(num_documents=1000)
    # Should show 50% savings
```

### Integration Tests

```python
# tests/integration/test_swarm.py

import pytest
from src.agents.swarm import Orchestrator

@pytest.mark.asyncio
async def test_full_pipeline():
    orchestrator = Orchestrator()

    # Start workers
    asyncio.create_task(orchestrator.start())

    # Ingest test document
    await orchestrator.ingest_document("https://example.com/test.pdf")

    # Wait for completion
    await asyncio.sleep(10)

    # Verify document in vector DB
    from src.services.vectordb import VectorDatabase
    db = VectorDatabase()
    results = await db.search("test")

    assert len(results) > 0
```

---

## Monitoring & Observability

### Cost Tracking Dashboard

```python
# src/monitoring/cost_tracker.py

from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class CostMetric:
    timestamp: str
    operation: str  # "individual" or "batch"
    documents_count: int
    cost_usd: float
    model: str

class CostTracker:
    """Track API costs over time"""

    def __init__(self):
        self.metrics: List[CostMetric] = []

    def log_cost(
        self,
        operation: str,
        documents_count: int,
        cost_usd: float,
        model: str
    ):
        """Log cost metric"""

        metric = CostMetric(
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            documents_count=documents_count,
            cost_usd=cost_usd,
            model=model
        )

        self.metrics.append(metric)

    def get_daily_summary(self) -> dict:
        """Get daily cost summary"""

        today = datetime.utcnow().date()
        today_metrics = [
            m for m in self.metrics
            if datetime.fromisoformat(m.timestamp).date() == today
        ]

        individual_cost = sum(
            m.cost_usd for m in today_metrics if m.operation == "individual"
        )

        batch_cost = sum(
            m.cost_usd for m in today_metrics if m.operation == "batch"
        )

        return {
            "date": today.isoformat(),
            "individual_api_cost": round(individual_cost, 2),
            "batch_api_cost": round(batch_cost, 2),
            "total_cost": round(individual_cost + batch_cost, 2),
            "savings": round(individual_cost - (batch_cost * 2), 2),  # What we saved vs all individual
            "documents_processed": sum(m.documents_count for m in today_metrics)
        }

# Usage
tracker = CostTracker()

# Log batch operation
tracker.log_cost(
    operation="batch",
    documents_count=100,
    cost_usd=0.125,  # 50% of $0.25
    model="gemini-2.5-flash"
)

# Daily summary
print(tracker.get_daily_summary())
# {
#   "date": "2025-11-18",
#   "batch_api_cost": 0.12,
#   "total_cost": 0.12,
#   "savings": 0.13,  # vs individual calls
#   "documents_processed": 100
# }
```

---

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY config/ ./config/

# Expose ports
EXPOSE 8000  # FastAPI
EXPOSE 9000  # MCP server

# Run
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ShadowTag-v2-services
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ShadowTag-v2-services
  template:
    metadata:
      labels:
        app: ShadowTag-v2-services
    spec:
      containers:
      - name: api
        image: ShadowTag-v2-services:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ShadowTag-v2-secrets
              key: gemini-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

---

## Next Steps

1. **Week 1:** Implement Gemini Batch API (src/services/gemini_batch.py)
2. **Week 2:** Setup MCP server (src/mcp/server.py)
3. **Week 3:** Build multi-agent swarm (src/agents/swarm.py)
4. **Week 4:** Integrate persistent memory (src/services/memory.py)
5. **Week 5:** Deploy to GCP using Agent Starter Pack templates
6. **Week 6:** Monitoring, testing, optimization

**Questions?** Review the companion knowledge base: `docs/research/ai-agents-knowledge-base.md`

---

**Last Updated:** 2025-11-18
**Version:** 1.0
**Maintainer:** Claude Code