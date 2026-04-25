# A2A Integration Architecture — CounselConduit

> **Protocol:** Google Agent-to-Agent (A2A) v1.0
> **Status:** Design Complete, Implementation Pending
> **Last Updated:** 2026-04-22

---

## 1. Multi-Agent Topology

```
                    ┌─────────────────────────────────────────┐
                    │         CounselConduit Orchestrator      │
                    │     (A2A Agent Card: coordinator.json)   │
                    └─────────┬───────────┬───────────┬───────┘
                              │           │           │
                    ┌─────────▼────┐ ┌────▼────┐ ┌───▼──────────┐
                    │   Oracle     │ │  Vent   │ │  Billing     │
                    │   Studio     │ │  Mode   │ │  Agent       │
                    │   Agent      │ │  Agent  │ │              │
                    │              │ │         │ │              │
                    │ 7-Stage      │ │ SSE     │ │ Stripe       │
                    │ Pipeline     │ │ Stream  │ │ Connect      │
                    └──────┬───────┘ └────┬────┘ └───┬──────────┘
                           │              │          │
                    ┌──────▼──────────────▼──────────▼──────────┐
                    │              MCP Tool Layer                │
                    │  (Firestore, Search, LiteLLM, Stripe)     │
                    └───────────────────────────────────────────┘
```

## 2. Agent Cards

### 2.1 Orchestrator Agent Card
```json
{
  "name": "CounselConduit Orchestrator",
  "description": "Routes legal AI queries to specialist agents. Manages session state and privilege attestation.",
  "url": "https://counselconduit-767252945109.us-central1.run.app",
  "version": "3.2.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "authentication": {
    "schemes": ["bearer"],
    "credentials": "Firebase Auth ID Token"
  },
  "skills": [
    {
      "id": "legal_research",
      "name": "Legal Research",
      "description": "Multi-model legal research with citation verification"
    },
    {
      "id": "client_intake",
      "name": "Client Intake",
      "description": "Structured intake with S.E.U. emotional architecture"
    },
    {
      "id": "billing_management",
      "name": "Billing Management",
      "description": "Stripe Connect subscription and payment management"
    }
  ]
}
```

### 2.2 Oracle Studio Agent Card
```json
{
  "name": "Oracle Studio",
  "description": "7-stage legal research pipeline: intake → extraction → research → analysis → citation → synthesis → attestation",
  "url": "https://counselconduit-767252945109.us-central1.run.app/agents/oracle",
  "version": "2.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {
      "id": "case_research",
      "name": "Case Law Research",
      "description": "Federal and state case law database search"
    },
    {
      "id": "statute_analysis",
      "name": "Statutory Analysis",
      "description": "Statute interpretation with jurisdiction awareness"
    },
    {
      "id": "citation_verification",
      "name": "Citation Verification",
      "description": "Validates all legal citations against authoritative sources"
    }
  ]
}
```

### 2.3 Vent Mode Agent Card
```json
{
  "name": "Vent Mode",
  "description": "Empathetic client-facing agent for emotional support during legal proceedings. S.E.U. architecture: Safety → Empathy → Utility.",
  "url": "https://counselconduit-767252945109.us-central1.run.app/agents/vent",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true
  },
  "skills": [
    {
      "id": "empathetic_response",
      "name": "Empathetic Response",
      "description": "Safety-first emotional support following S.E.U. ordering"
    }
  ]
}
```

## 3. A2A Task Lifecycle

```
Client → POST /agent/message
  → Orchestrator receives task (A2A Task object)
  → Orchestrator classifies intent
  → If legal_research:
      → Orchestrator sends A2A task to Oracle Studio agent
      → Oracle runs 7-stage pipeline (each stage = A2A subtask)
      → Oracle streams results back via A2A streaming (SSE)
      → Orchestrator wraps results in A2UI widgets
      → AG-UI SSE stream delivers to CopilotKit frontend
  → If emotional_support:
      → Orchestrator sends A2A task to Vent Mode agent
      → Vent Mode streams empathetic response
      → Dead-man's switch timeout: 45 min auto-disconnect
  → If billing:
      → Orchestrator sends A2A task to Billing agent
      → Billing agent calls Stripe MCP tools
```

## 4. A2A + MCP Bridge

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

class A2AToolBridge:
    """Bridge that exposes A2A agent discovery as an MCP tool."""

    def __init__(self, registry_url: str):
        self.registry_url = registry_url

    async def discover_agents(self, capability: str) -> list[dict]:
        """MCP tool that discovers A2A agents by capability."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.registry_url}/.well-known/agent.json"
            )
            card = response.json()
            matching = [
                s for s in card.get("skills", [])
                if capability.lower() in s["description"].lower()
            ]
            return matching

    async def delegate_to_agent(
        self, agent_url: str, skill_id: str, message: str
    ) -> dict:
        """MCP tool that delegates a task to an A2A agent."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{agent_url}/tasks",
                json={
                    "skill_id": skill_id,
                    "message": {"role": "user", "parts": [{"text": message}]},
                }
            )
            return response.json()
```

## 5. Security Architecture

### Authentication Flow
1. Client authenticates via Firebase Auth → ID token
2. ID token passed as Bearer token in A2A task request
3. Orchestrator validates token via Firebase Admin SDK
4. Per-agent authorization checks tenant membership
5. Kovel attestation receipt generated per privileged session

### A2A Security Checklist
- [ ] All agent endpoints require Bearer auth (Firebase ID token)
- [ ] Agent Cards served from `/.well-known/agent.json`
- [ ] No agent accepts unauthenticated tasks
- [ ] Tenant isolation enforced per-task (firm_id scoping)
- [ ] Rate limiting: 100 tasks/min per user, 1000/min per firm
- [ ] Input validation via Pydantic on all task payloads
- [ ] HMAC-SHA256 attestation on all privileged sessions
- [ ] No raw database objects in task responses
- [ ] Push notifications use Cloud Tasks (not direct callbacks)

## 6. ADK Session → Firestore Persistence

```python
from google.adk.sessions import InMemorySessionService
from google.cloud import firestore

class FirestoreSessionService(InMemorySessionService):
    """Persists ADK sessions to Firestore for cross-instance continuity."""

    def __init__(self, db: firestore.AsyncClient):
        super().__init__()
        self.db = db
        self.collection = "adk_sessions"

    async def save_session(self, session_id: str, data: dict):
        await self.db.collection(self.collection).document(session_id).set({
            **data,
            "updated_at": firestore.SERVER_TIMESTAMP,
            "ttl": datetime.utcnow() + timedelta(hours=24),
        })

    async def load_session(self, session_id: str) -> dict | None:
        doc = await self.db.collection(self.collection).document(session_id).get()
        return doc.to_dict() if doc.exists else None
```

## 7. Push Notifications for Long-Running Queries

```python
from google.cloud import tasks_v2

async def schedule_push_notification(
    task_id: str,
    user_id: str,
    callback_url: str,
    delay_seconds: int = 0,
):
    """Schedule a Cloud Tasks notification for when a long-running Oracle query completes."""
    client = tasks_v2.CloudTasksClient()
    parent = client.queue_path("shadowtag-omega-v4", "us-central1", "a2a-notifications")

    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=callback_url,
            headers={"Content-Type": "application/json"},
            body=json.dumps({
                "task_id": task_id,
                "user_id": user_id,
                "type": "oracle_query_complete",
            }).encode(),
        ),
        schedule_time=timestamp_pb2.Timestamp(
            seconds=int(time.time()) + delay_seconds,
        ),
    )

    client.create_task(parent=parent, task=task)
```

## 8. Manifest Integration

Added to `monorepo_manifest.yaml`:
- `product-pitch-site` as canonical app (Firebase Hosting source)
- `a2a_protocol_version: "1.0"`
- Skills fleet updated with 9 new protocol skills

## References

- [A2A Spec](https://github.com/google/a2a-spec)
- [ADK 2.0](https://adk.dev/2.0/)
- Agent Cards: `apps/counselconduit/.well-known/`
- Skills: `skills/a2a-agent-card-publisher/`, `skills/four-pillar-protocol-stack/`
