# ShadowTag-v4 Memory System Architecture

## Overview

FastAPI service implementing persistent memory and conversation management using Claude Agent SDK, similar to Claude.ai's memory features.

## Core Components

### 1. API Layer (FastAPI)

- **Conversation endpoints**: Create, read, update conversations
- **Memory endpoints**: View, edit, search memory
- **Search endpoints**: RAG-based conversation search
- **Health/status endpoints**: System monitoring

### 2. Data Storage

#### Relational Database (SQLite/PostgreSQL)

```
conversations
  - id (uuid)
  - project_id (uuid, nullable)
  - created_at, updated_at
  - title
  - metadata (json)

messages
  - id (uuid)
  - conversation_id (fk)
  - role (user/assistant/system)
  - content (text)
  - timestamp
  - metadata (json)

memory_entries
  - id (uuid)
  - project_id (uuid, nullable)
  - category (preferences/facts/decisions/patterns)
  - content (text)
  - confidence (0.0-1.0)
  - source_conversation_ids (json array)
  - created_at, updated_at
  - active (boolean)
```

#### Vector Database (ChromaDB)

- Embedded message content for semantic search
- Embedded memory entries for context retrieval
- Collections: `conversations`, `memory`

### 3. Memory Synthesis Engine

**Periodic Processing** (configurable interval, default: 24hr):

```python
async def synthesize_memory():
    # 1. Fetch recent conversations (since last synthesis)
    # 2. Use Claude to extract:
    #    - User preferences/patterns
    #    - Technical decisions
    #    - Project-specific facts
    #    - Communication style
    # 3. Merge with existing memory (deduplication)
    # 4. Store in memory_entries table
    # 5. Update vector embeddings
```

**Memory Categories**:

- `preferences`: User preferences, working style
- `facts`: Project facts, technical stack, constraints
- `decisions`: Technical decisions, architectural choices
- `patterns`: Communication patterns, recurring themes

### 4. Search & Retrieval (RAG)

**Semantic Search Flow**:

```
User query → Embed query → Vector search → Retrieve top-k
→ Rerank by relevance → Return with metadata
```

**Context Assembly**:

```
Active memory + Relevant past conversations → Claude context
```

### 5. Claude Agent SDK Integration

**Query with Memory**:

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Assemble context from memory system
memory_context = await get_active_memory(project_id)
relevant_convos = await search_conversations(user_query)

# Build enhanced system prompt
enhanced_prompt = f"""
{base_system_prompt}

## Persistent Memory
{memory_context}

## Relevant Past Context
{relevant_convos}
"""

# Execute query with context
async for message in query(
    prompt=user_query,
    options=ClaudeAgentOptions(
        system_prompt=enhanced_prompt,
        model="claude-sonnet-4-5-20250929"
    )
):
    yield message
```

## API Endpoints

### Conversations

- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}` - Get conversation
- `GET /api/conversations` - List conversations (paginated)
- `POST /api/conversations/{id}/messages` - Add message
- `DELETE /api/conversations/{id}` - Delete conversation

### Memory

- `GET /api/memory` - Get active memory (optionally filtered by project)
- `PUT /api/memory/{id}` - Edit memory entry
- `DELETE /api/memory/{id}` - Delete memory entry
- `POST /api/memory/synthesize` - Trigger synthesis manually
- `POST /api/memory` - Add manual memory entry

### Search

- `POST /api/search/conversations` - Semantic search across conversations
- `POST /api/search/messages` - Search specific messages
- `GET /api/search/suggestions` - Get related conversation suggestions

### Agent

- `POST /api/agent/query` - Query Claude with memory context
- `POST /api/agent/stream` - Streaming query with memory

## Technology Stack

- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: SQLite (development), PostgreSQL (production)
- **Vector DB**: ChromaDB
- **Embeddings**: Claude API embeddings or OpenAI embeddings
- **AI**: Claude Agent SDK
- **Task Queue**: APScheduler (for periodic synthesis)
- **Validation**: Pydantic v2

## Configuration

Environment variables:

```bash
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./shadowtag_v4.db
VECTOR_DB_PATH=./chroma_db
MEMORY_SYNTHESIS_INTERVAL_HOURS=24
ENABLE_MEMORY_SYNTHESIS=true
ENABLE_CONVERSATION_SEARCH=true
```

## Project Structure

```
shadowtag_v4-fastapi-services/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry
│   ├── config.py               # Configuration
│   ├── database.py             # DB setup
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── memory.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── memory.py
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── conversations.py
│   │   ├── memory.py
│   │   ├── search.py
│   │   └── agent.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── conversation_service.py
│   │   ├── memory_service.py
│   │   ├── search_service.py
│   │   └── synthesis_service.py
│   └── core/                   # Core utilities
│       ├── __init__.py
│       ├── vector_db.py        # ChromaDB wrapper
│       └── claude_client.py    # Claude SDK wrapper
├── tests/
│   └── __init__.py
├── requirements.txt
├── .env.example
├── README.md
└── ARCHITECTURE.md
```

## Memory Privacy Model

- **Project Isolation**: Memory is scoped to projects (optional `project_id`)
- **Incognito Mode**: Conversations with `incognito=true` bypass memory synthesis
- **Manual Control**: Users can view/edit/delete any memory entry
- **Confidence Scoring**: Memory entries have confidence scores, low-confidence entries can be flagged

## Implementation Phases

### Phase 1: Core Infrastructure

- FastAPI setup
- Database models and migrations
- Basic CRUD endpoints for conversations

### Phase 2: Memory Foundation

- Memory models and storage
- Manual memory management endpoints
- Vector database integration

### Phase 3: Search & Retrieval

- Semantic search implementation
- Conversation search endpoints
- RAG context assembly

### Phase 4: Memory Synthesis

- Synthesis engine using Claude
- Periodic task scheduling
- Deduplication and merging logic

### Phase 5: Agent Integration

- Query endpoints with memory context
- Streaming responses
- Context optimization

## Performance Considerations

- **Vector search**: Index optimization, top-k tuning
- **Memory synthesis**: Batch processing, incremental updates
- **API responses**: Pagination, lazy loading
- **Database**: Proper indexing on frequently queried fields

## Future Enhancements

- Multi-user support with user-scoped memory
- Memory sharing between users/projects
- Advanced deduplication with semantic similarity
- Memory importance scoring and auto-pruning
- Analytics and memory insights dashboard
