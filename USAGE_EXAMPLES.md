# Usage Examples

This document provides comprehensive examples of using the Claude Memory & Search API.

## Table of Contents
- [Basic Workflow](#basic-workflow)
- [Python Examples](#python-examples)
- [JavaScript Examples](#javascript-examples)
- [cURL Examples](#curl-examples)
- [Advanced Use Cases](#advanced-use-cases)

## Basic Workflow

### 1. Create a Project
Projects provide memory isolation - each project has its own memory space.

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/projects/",
        json={
            "name": "Personal Assistant",
            "description": "My personal AI assistant",
            "memory_enabled": True
        }
    )
    project = response.json()
    print(f"Project ID: {project['id']}")
```

### 2. Start a Conversation
Create a conversation within a project. Set `is_incognito: true` for private chats.

```python
response = await client.post(
    "http://localhost:8000/api/v1/conversations/",
    json={
        "project_id": project['id'],
        "is_incognito": False  # Memory will be saved
    }
)
conversation = response.json()
```

### 3. Add Messages
Messages are automatically embedded for semantic search.

```python
# User message
await client.post(
    f"http://localhost:8000/api/v1/conversations/{conversation['id']}/messages",
    json={
        "conversation_id": conversation['id'],
        "role": "user",
        "content": "I'm learning Python and FastAPI"
    }
)

# Assistant response
await client.post(
    f"http://localhost:8000/api/v1/conversations/{conversation['id']}/messages",
    json={
        "conversation_id": conversation['id'],
        "role": "assistant",
        "content": "That's great! FastAPI is an excellent framework..."
    }
)
```

### 4. Search Conversations
Use semantic search to find relevant conversations.

```python
response = await client.post(
    "http://localhost:8000/api/v1/search/",
    json={
        "query": "Python frameworks",
        "project_id": project['id'],
        "top_k": 5,
        "min_relevance": 0.5
    }
)
results = response.json()

for result in results['conversation_results']:
    print(f"Relevance: {result['relevance_score']:.2f}")
    print(f"Message: {result['message_content']}")
```

### 5. Create Memories
Store important information as memories.

```python
response = await client.post(
    "http://localhost:8000/api/v1/memories/",
    json={
        "title": "User Tech Stack",
        "content": "User is learning Python, FastAPI, and async programming",
        "memory_type": "fact",
        "project_id": project['id'],
        "confidence_score": 1.0
    }
)
```

### 6. Get Memory Synthesis
Get a synthesis of all memories for context.

```python
response = await client.get(
    f"http://localhost:8000/api/v1/memories/synthesis?project_id={project['id']}"
)
synthesis = response.json()
print(synthesis['synthesis'])
```

## Python Examples

### Complete Chatbot Integration

```python
import asyncio
import httpx
from typing import List, Dict

class ClaudeMemoryClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.current_conversation_id = None
        self.project_id = None

    async def initialize(self, project_name: str):
        """Initialize with a project."""
        response = await self.client.post(
            f"{self.base_url}/projects/",
            json={"name": project_name, "memory_enabled": True}
        )
        self.project_id = response.json()['id']

        # Start conversation
        response = await self.client.post(
            f"{self.base_url}/conversations/",
            json={"project_id": self.project_id}
        )
        self.current_conversation_id = response.json()['id']

    async def send_message(self, content: str, role: str = "user"):
        """Send a message in the current conversation."""
        response = await self.client.post(
            f"{self.base_url}/conversations/{self.current_conversation_id}/messages",
            json={
                "conversation_id": self.current_conversation_id,
                "role": role,
                "content": content
            }
        )
        return response.json()

    async def search(self, query: str, top_k: int = 5) -> Dict:
        """Search conversations and memories."""
        response = await self.client.post(
            f"{self.base_url}/search/",
            json={
                "query": query,
                "project_id": self.project_id,
                "top_k": top_k,
                "search_conversations": True,
                "search_memories": True
            }
        )
        return response.json()

    async def create_memory(self, title: str, content: str, memory_type: str = "fact"):
        """Create a new memory."""
        response = await self.client.post(
            f"{self.base_url}/memories/",
            json={
                "title": title,
                "content": content,
                "memory_type": memory_type,
                "project_id": self.project_id
            }
        )
        return response.json()

    async def get_context(self) -> str:
        """Get memory synthesis for context."""
        response = await self.client.get(
            f"{self.base_url}/memories/synthesis",
            params={"project_id": self.project_id}
        )
        return response.json()['synthesis']

    async def close(self):
        """Close the client."""
        await self.client.aclose()


# Usage example
async def main():
    client = ClaudeMemoryClient()

    # Initialize
    await client.initialize("Personal Assistant")

    # Send messages
    await client.send_message("I'm working on a FastAPI project")
    await client.send_message(
        "Great! What features are you building?",
        role="assistant"
    )

    # Create memory
    await client.create_memory(
        title="Current Project",
        content="User is building a FastAPI application",
        memory_type="context"
    )

    # Search
    results = await client.search("FastAPI features")
    print(f"Found {results['total_results']} results")

    # Get context
    context = await client.get_context()
    print(f"Memory Context:\n{context}")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## JavaScript Examples

### Basic Node.js Client

```javascript
const fetch = require('node-fetch');

class ClaudeMemoryClient {
  constructor(baseUrl = 'http://localhost:8000/api/v1') {
    this.baseUrl = baseUrl;
    this.projectId = null;
    this.conversationId = null;
  }

  async initialize(projectName) {
    // Create project
    const projectRes = await fetch(`${this.baseUrl}/projects/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: projectName,
        memory_enabled: true
      })
    });
    const project = await projectRes.json();
    this.projectId = project.id;

    // Create conversation
    const convRes = await fetch(`${this.baseUrl}/conversations/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        project_id: this.projectId
      })
    });
    const conversation = await convRes.json();
    this.conversationId = conversation.id;
  }

  async sendMessage(content, role = 'user') {
    const response = await fetch(
      `${this.baseUrl}/conversations/${this.conversationId}/messages`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: this.conversationId,
          role,
          content
        })
      }
    );
    return response.json();
  }

  async search(query, topK = 5) {
    const response = await fetch(`${this.baseUrl}/search/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        project_id: this.projectId,
        top_k: topK
      })
    });
    return response.json();
  }

  async createMemory(title, content, memoryType = 'fact') {
    const response = await fetch(`${this.baseUrl}/memories/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title,
        content,
        memory_type: memoryType,
        project_id: this.projectId
      })
    });
    return response.json();
  }

  async getRecentChats(limit = 20) {
    const response = await fetch(
      `${this.baseUrl}/conversations/recent?limit=${limit}&project_id=${this.projectId}`
    );
    return response.json();
  }
}

// Usage
(async () => {
  const client = new ClaudeMemoryClient();
  await client.initialize('Work Assistant');

  await client.sendMessage('Schedule meeting for tomorrow');
  await client.createMemory(
    'Meeting Request',
    'User wants to schedule a meeting for tomorrow',
    'context'
  );

  const results = await client.search('meeting');
  console.log('Search results:', results);
})();
```

## Advanced Use Cases

### Automatic Memory Extraction

```python
async def process_conversation_with_memory_extraction(
    client: ClaudeMemoryClient,
    conversation_id: int
):
    """Process a conversation and extract memories."""
    # Extract memories from conversation
    response = await client.client.post(
        f"{client.base_url}/memories/extract/{conversation_id}"
    )
    extracted_memories = response.json()

    print(f"Extracted {len(extracted_memories)} memories:")
    for memory in extracted_memories:
        print(f"- [{memory['memory_type']}] {memory['title']}")
```

### Multi-Project Management

```python
async def manage_multiple_projects():
    """Manage conversations across multiple projects."""
    client = ClaudeMemoryClient()

    # Create multiple projects
    projects = {}
    for project_name in ["Work", "Personal", "Learning"]:
        response = await client.client.post(
            f"{client.base_url}/projects/",
            json={"name": project_name, "memory_enabled": True}
        )
        projects[project_name] = response.json()['id']

    # Search across specific project
    work_results = await client.client.post(
        f"{client.base_url}/search/",
        json={
            "query": "project deadline",
            "project_id": projects["Work"]
        }
    )

    # Get stats for each project
    for name, project_id in projects.items():
        response = await client.client.get(
            f"{client.base_url}/projects/{project_id}/stats"
        )
        stats = response.json()
        print(f"{name}: {stats['conversation_count']} conversations, "
              f"{stats['memory_count']} memories")
```

### Incognito Conversations

```python
async def private_conversation():
    """Create a conversation that won't be saved to memory."""
    async with httpx.AsyncClient() as client:
        # Create incognito conversation
        response = await client.post(
            "http://localhost:8000/api/v1/conversations/",
            json={
                "project_id": 1,
                "is_incognito": True  # Won't save to memory or history
            }
        )
        conversation = response.json()

        # Messages in this conversation won't appear in search
        await client.post(
            f"http://localhost:8000/api/v1/conversations/{conversation['id']}/messages",
            json={
                "conversation_id": conversation['id'],
                "role": "user",
                "content": "This is a private message"
            }
        )
```

### Memory Management

```python
async def manage_memories(client: ClaudeMemoryClient):
    """View, edit, and delete memories."""
    # Get all memories
    response = await client.client.get(
        f"{client.base_url}/memories/",
        params={"project_id": client.project_id}
    )
    memories = response.json()

    # Edit a memory
    memory_id = memories[0]['id']
    response = await client.client.patch(
        f"{client.base_url}/memories/{memory_id}",
        json={
            "content": "Updated memory content",
            "title": "Updated Title"
        }
    )

    # Delete a memory
    response = await client.client.delete(
        f"{client.base_url}/memories/{memory_id}"
    )

    # Get memories by type
    response = await client.client.get(
        f"{client.base_url}/memories/",
        params={
            "project_id": client.project_id,
            "memory_type": "preference"
        }
    )
    preferences = response.json()
```

## Best Practices

1. **Project Organization**: Use separate projects for different contexts
2. **Memory Types**: Use appropriate types (fact, preference, context, insight)
3. **Incognito Mode**: Use for sensitive or temporary conversations
4. **Regular Synthesis**: Check memory synthesis to understand saved context
5. **Search Relevance**: Adjust `min_relevance` based on your needs (0.5-0.8 works well)
6. **Memory Cleanup**: Periodically review and delete outdated memories

## Error Handling

```python
async def robust_search(client: ClaudeMemoryClient, query: str):
    """Search with error handling."""
    try:
        results = await client.search(query)
        if results['total_results'] == 0:
            print("No results found")
            return None
        return results
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
```
