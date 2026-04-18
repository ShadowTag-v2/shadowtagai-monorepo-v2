# Contractual - Technical Architecture

## System Overview

Contractual is an AI-powered contract negotiation platform built on a microservices architecture using FastAPI, deployed on Google Kubernetes Engine (GKE), and integrated with Anthropic Claude for AI-powered conflict detection.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Contractual Platform                             │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────────┐   │
│  │  Mobile App      │  │  Web Application │  │  API Gateway    │   │
│  │  (React Native)  │  │  (Next.js)       │  │  (FastAPI)      │   │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬────────┘   │
│           │                     │                     │             │
│           └─────────────────────┴─────────────────────┘             │
│                                │                                    │
│                     ┌──────────▼──────────┐                         │
│                     │  Contractual API    │                         │
│                     │  (FastAPI)          │                         │
│                     └──────────┬──────────┘                         │
│                                │                                    │
│           ┌────────────────────┼────────────────────┐               │
│           │                    │                    │               │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐     │
│  │ Negotiation     │  │  Conflict       │  │  Document      │     │
│  │ Engine          │  │  Detection      │  │  Generation    │     │
│  └────────┬────────┘  └────────┬────────┘  └───────┬────────┘     │
│           │                    │                    │               │
│           └────────────────────┼────────────────────┘               │
│                                │                                    │
│                     ┌──────────▼──────────┐                         │
│                     │  AI Integration     │                         │
│                     │  (Anthropic Claude) │                         │
│                     └──────────┬──────────┘                         │
│                                │                                    │
│           ┌────────────────────┼────────────────────┐               │
│           │                    │                    │               │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐     │
│  │  PostgreSQL     │  │     Redis       │  │  Google Cloud  │     │
│  │  (Structured)   │  │     (Cache)     │  │  Storage (GCS) │     │
│  └─────────────────┘  └─────────────────┘  └────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend

**Web Application:**
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Real-time**: Socket.IO client
- **Forms**: React Hook Form + Zod validation
- **UI Components**: shadcn/ui

**Mobile Application:**
- **Framework**: React Native + Expo
- **Navigation**: React Navigation
- **State**: Zustand (shared with web)
- **Audio**: expo-av (recording)
- **Offline**: WatermelonDB (local-first)

### Backend

**API Layer:**
- **Framework**: FastAPI 0.104+ (Python 3.11)
- **Async**: asyncio + uvloop
- **Validation**: Pydantic v2
- **Auth**: Auth0 + JWT
- **API Docs**: OpenAPI 3.1 (auto-generated)

**Core Services:**
- **Negotiation Engine**: Python + FastAPI
- **Conflict Detection**: Python + Anthropic Claude API
- **Document Generation**: Jinja2 + WeasyPrint (PDF)
- **Transcription**: OpenAI Whisper API
- **E-Signature**: DocuSign API + native fallback

### AI/ML

**Primary AI Provider:**
- **Anthropic Claude 3.5 Sonnet** (via API)
- Use cases: Conflict detection, term extraction, legal analysis

**Secondary AI (Fallback/Comparison):**
- **OpenAI GPT-4 Turbo** (via API)
- Use cases: Transcription (Whisper), embeddings

**Custom ML (Phase 2):**
- Fine-tuned models on negotiation data
- Industry-specific classifiers
- Conflict prediction models

### Data Layer

**Primary Database:**
- **PostgreSQL 15**
- Schemas: Users, Negotiations, Contracts, Conflicts
- Extensions: pgvector (embeddings), pg_trgm (fuzzy search)

**Cache:**
- **Redis 7**
- Use cases: Session storage, rate limiting, real-time pub/sub

**Object Storage:**
- **Google Cloud Storage (GCS)**
- Use cases: Audio recordings, PDFs, backups

**Search:**
- **PostgreSQL Full-Text Search** (initial)
- **Elasticsearch** (Phase 2, if needed)

### Infrastructure

**Cloud Provider:**
- **Google Cloud Platform (GCP)** - Exclusive

**Compute:**
- **Google Kubernetes Engine (GKE)** - Production
- **Vertex AI Workbench** - Development/prototyping
- **Cloud Run** - Serverless functions (webhooks)

**Networking:**
- **Cloud Load Balancing** (HTTPS)
- **Cloud CDN** (static assets)
- **Cloud Armor** (DDoS protection)

**Security:**
- **Cloud KMS** (encryption keys)
- **Secret Manager** (API keys, credentials)
- **VPC** (network isolation)
- **Cloud IAM** (access control)

**Monitoring:**
- **Cloud Monitoring** (metrics)
- **Cloud Logging** (structured logs)
- **Cloud Trace** (distributed tracing)
- **Sentry** (error tracking)

---

## Core Components

### 1. Conversation Capture System

**Purpose**: Record and transcribe business negotiations

**Features:**
- Browser-based audio recording (WebRTC)
- Mobile app recording (expo-av)
- Speaker diarization (who said what)
- Real-time transcription (OpenAI Whisper)
- Multi-language support (Phase 2)

**Architecture:**
```python
# src/services/contractual/conversation.py

class ConversationCapture:
    async def start_recording(self, session_id: str) -> Recording:
        """Initiate audio recording for negotiation"""
        pass

    async def transcribe_audio(self, audio_file: bytes) -> Transcript:
        """Transcribe audio using Whisper API"""
        pass

    async def identify_speakers(self, transcript: Transcript) -> DiarizedTranscript:
        """Identify which party said what"""
        pass
```

**Data Model:**
```python
class Recording(BaseModel):
    id: UUID
    session_id: UUID
    audio_url: str  # GCS URL
    duration_seconds: int
    created_at: datetime

class Transcript(BaseModel):
    id: UUID
    recording_id: UUID
    text: str
    confidence: float
    segments: List[TranscriptSegment]

class TranscriptSegment(BaseModel):
    speaker: str  # "Party A" | "Party B"
    text: str
    start_time: float
    end_time: float
    confidence: float
```

### 2. Conflict Detection Engine

**Purpose**: Identify conflicting terms between parties using AI

**Features:**
- Legal subject classification (payment, scope, timeline, liability)
- Term extraction from natural language
- Conflict identification across 20+ categories
- Confidence scoring
- Explanation generation

**Architecture:**
```python
# src/services/contractual/conflict_detection.py

class ConflictDetector:
    def __init__(self, ai_client: AnthropicClient):
        self.ai_client = ai_client

    async def analyze_transcript(self, transcript: Transcript) -> List[DetectedConflict]:
        """Analyze transcript for conflicting terms"""
        # 1. Classify discussion topics (payment, scope, timeline, etc.)
        topics = await self.classify_topics(transcript)

        # 2. Extract terms proposed by each party
        party_a_terms = await self.extract_terms(transcript, party="A")
        party_b_terms = await self.extract_terms(transcript, party="B")

        # 3. Compare terms within each topic
        conflicts = []
        for topic in topics:
            a_proposal = party_a_terms.get(topic)
            b_proposal = party_b_terms.get(topic)

            if a_proposal != b_proposal:
                conflict = await self.create_conflict(
                    topic=topic,
                    party_a_proposal=a_proposal,
                    party_b_proposal=b_proposal
                )
                conflicts.append(conflict)

        return conflicts

    async def classify_topics(self, transcript: Transcript) -> List[LegalTopic]:
        """Use AI to classify legal topics being discussed"""
        prompt = f"""
        Analyze this business negotiation transcript and identify all legal topics being discussed.

        Legal topics include:
        - payment_terms: Amount, timing, method, penalties
        - scope_of_work: Deliverables, quality standards, change orders
        - timeline: Deadlines, milestones, delay consequences
        - liability: Warranties, indemnification, limitations
        - termination: Conditions, notice, consequences

        Transcript:
        {transcript.text}

        Return JSON array of topics with confidence scores.
        """

        response = await self.ai_client.analyze(prompt)
        return parse_topics(response)

    async def extract_terms(self, transcript: Transcript, party: str) -> Dict[str, Term]:
        """Extract specific terms proposed by each party"""
        party_segments = [
            seg for seg in transcript.segments
            if seg.speaker == f"Party {party}"
        ]

        prompt = f"""
        Extract specific terms proposed by Party {party} from their statements.

        Statements:
        {'\n'.join([seg.text for seg in party_segments])}

        For each legal topic, extract:
        - Specific amounts (money, time, quantity)
        - Conditions or requirements
        - Quality standards
        - Consequences or penalties

        Return structured JSON.
        """

        response = await self.ai_client.analyze(prompt)
        return parse_terms(response)
```

**Data Model:**
```python
class LegalTopic(str, Enum):
    PAYMENT_TERMS = "payment_terms"
    SCOPE_OF_WORK = "scope_of_work"
    TIMELINE = "timeline"
    LIABILITY = "liability"
    TERMINATION = "termination"
    WARRANTY = "warranty"
    CHANGE_ORDERS = "change_orders"

class DetectedConflict(BaseModel):
    id: UUID
    session_id: UUID
    topic: LegalTopic
    party_a_proposal: Term
    party_b_proposal: Term
    confidence: float  # 0.0 - 1.0
    explanation: str
    severity: str  # "high" | "medium" | "low"
    created_at: datetime

class Term(BaseModel):
    topic: LegalTopic
    value: str  # Raw value (e.g., "$500", "Net 30", "7 days")
    normalized: Any  # Normalized value (e.g., 500, 30, 7)
    context: str  # Surrounding context from transcript
    confidence: float
```

### 3. Conflict Resolution Interface

**Purpose**: Display conflicts to both parties and facilitate resolution

**Features:**
- Side-by-side comparison UI
- "Choose A", "Choose B", "Negotiate New" options
- AI-suggested compromises
- Real-time negotiation chat
- Agreement locking

**Architecture:**
```python
# src/services/contractual/resolution.py

class ConflictResolver:
    async def present_conflict(self, conflict: DetectedConflict) -> ResolutionInterface:
        """Create resolution interface for conflict"""
        # Generate suggested compromise
        compromise = await self.suggest_compromise(conflict)

        return ResolutionInterface(
            conflict=conflict,
            party_a_option=conflict.party_a_proposal,
            party_b_option=conflict.party_b_proposal,
            suggested_compromise=compromise
        )

    async def suggest_compromise(self, conflict: DetectedConflict) -> Term:
        """Use AI to suggest middle-ground compromise"""
        prompt = f"""
        Suggest a fair compromise between these two proposals:

        Party A proposes: {conflict.party_a_proposal.value}
        Context: {conflict.party_a_proposal.context}

        Party B proposes: {conflict.party_b_proposal.value}
        Context: {conflict.party_b_proposal.context}

        Topic: {conflict.topic}

        Suggest a compromise that:
        1. Splits the difference fairly
        2. Is acceptable to both parties
        3. Is legally clear and enforceable

        Return JSON with suggested term and rationale.
        """

        response = await self.ai_client.analyze(prompt)
        return parse_compromise(response)

    async def resolve_conflict(
        self,
        conflict_id: UUID,
        resolution: ConflictResolution
    ) -> ResolvedConflict:
        """Lock in agreed resolution"""
        # Require both parties to digitally sign resolution
        if not (resolution.party_a_signed and resolution.party_b_signed):
            raise ValueError("Both parties must sign resolution")

        return ResolvedConflict(
            conflict_id=conflict_id,
            chosen_term=resolution.chosen_term,
            resolution_method=resolution.method,  # "choose_a" | "choose_b" | "compromise" | "custom"
            signed_by_a_at=resolution.party_a_signed_at,
            signed_by_b_at=resolution.party_b_signed_at,
            is_final=True
        )
```

### 4. Document Generation

**Purpose**: Generate legally binding contracts from resolved terms

**Features:**
- Dynamic template system
- Industry-specific templates
- PDF generation with signatures
- Legal compliance verification (state-by-state)
- Version control

**Architecture:**
```python
# src/services/contractual/document_generation.py

class DocumentGenerator:
    async def generate_contract(
        self,
        session: NegotiationSession,
        resolved_conflicts: List[ResolvedConflict]
    ) -> Contract:
        """Generate final contract from negotiation"""

        # 1. Select appropriate template
        template = await self.select_template(session.industry, session.contract_type)

        # 2. Populate template with resolved terms
        contract_data = await self.build_contract_data(resolved_conflicts)

        # 3. Generate HTML contract
        html_contract = await self.render_template(template, contract_data)

        # 4. Convert to PDF
        pdf_contract = await self.generate_pdf(html_contract)

        # 5. Store contract
        contract_url = await self.upload_to_gcs(pdf_contract)

        return Contract(
            id=uuid4(),
            session_id=session.id,
            template_id=template.id,
            html_url=contract_url.replace('.pdf', '.html'),
            pdf_url=contract_url,
            status="pending_signatures",
            created_at=datetime.now()
        )

    async def add_signatures(
        self,
        contract: Contract,
        signatures: List[Signature]
    ) -> SignedContract:
        """Add e-signatures to contract"""
        # Use DocuSign API or native e-signature
        if settings.USE_DOCUSIGN:
            signed_url = await self.docusign_client.sign(contract, signatures)
        else:
            signed_url = await self.native_sign(contract, signatures)

        return SignedContract(
            contract_id=contract.id,
            signed_pdf_url=signed_url,
            signatures=signatures,
            signed_at=datetime.now(),
            is_legally_binding=True
        )
```

---

## API Endpoints

### Base URL: `/contractual`

### Negotiation Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sessions` | Create new negotiation session |
| `GET` | `/sessions/{id}` | Get session details |
| `PATCH` | `/sessions/{id}` | Update session metadata |
| `DELETE` | `/sessions/{id}` | Cancel session |

### Conversation Capture

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sessions/{id}/recording/start` | Start audio recording |
| `POST` | `/sessions/{id}/recording/stop` | Stop recording, trigger transcription |
| `GET` | `/sessions/{id}/transcript` | Get transcript |
| `POST` | `/sessions/{id}/transcript/manual` | Manually input text (no audio) |

### Conflict Detection

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sessions/{id}/analyze` | Trigger AI conflict detection |
| `GET` | `/sessions/{id}/conflicts` | List detected conflicts |
| `GET` | `/conflicts/{id}` | Get conflict details |

### Conflict Resolution

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/conflicts/{id}/resolve` | Submit resolution choice |
| `POST` | `/conflicts/{id}/negotiate` | Open negotiation chat |
| `GET` | `/conflicts/{id}/suggestions` | Get AI compromise suggestions |
| `POST` | `/conflicts/{id}/sign` | Digitally sign resolution |

### Document Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/sessions/{id}/generate-contract` | Generate contract from resolved conflicts |
| `GET` | `/contracts/{id}` | Get contract details |
| `POST` | `/contracts/{id}/sign` | Add e-signature |
| `GET` | `/contracts/{id}/download` | Download signed PDF |

### Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/templates` | List available templates |
| `GET` | `/templates/{id}` | Get template details |
| `POST` | `/templates` | Create custom template (business/enterprise) |

---

## Data Models

### Core Entities

```python
# src/models/contractual.py

from enum import Enum
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class NegotiationSession(BaseModel):
    id: UUID
    user_a_id: UUID  # Initiator
    user_b_id: UUID | None  # Recipient (invited)
    industry: str  # "auto_repair", "contracting", "consulting"
    contract_type: str  # "service", "sale", "lease"
    status: str  # "recording", "analyzing", "resolving", "completed", "cancelled"
    created_at: datetime
    updated_at: datetime

class Recording(BaseModel):
    id: UUID
    session_id: UUID
    audio_url: str  # GCS URL
    duration_seconds: int
    format: str  # "webm", "m4a"
    created_at: datetime

class Transcript(BaseModel):
    id: UUID
    recording_id: UUID
    text: str
    segments: List[TranscriptSegment]
    language: str  # "en", "es"
    confidence: float
    created_at: datetime

class TranscriptSegment(BaseModel):
    speaker: str  # "Party A" | "Party B"
    text: str
    start_time: float
    end_time: float
    confidence: float

class DetectedConflict(BaseModel):
    id: UUID
    session_id: UUID
    topic: str  # LegalTopic enum
    party_a_proposal: Term
    party_b_proposal: Term
    confidence: float
    explanation: str
    severity: str  # "high" | "medium" | "low"
    status: str  # "detected" | "resolving" | "resolved"
    created_at: datetime

class Term(BaseModel):
    topic: str
    value: str
    normalized: Any
    context: str
    confidence: float

class ResolvedConflict(BaseModel):
    id: UUID
    conflict_id: UUID
    chosen_term: Term
    resolution_method: str  # "choose_a" | "choose_b" | "compromise" | "custom"
    party_a_signed_at: datetime
    party_b_signed_at: datetime
    is_final: bool

class Contract(BaseModel):
    id: UUID
    session_id: UUID
    template_id: UUID
    html_url: str
    pdf_url: str
    status: str  # "pending_signatures" | "signed" | "expired"
    created_at: datetime

class Signature(BaseModel):
    id: UUID
    contract_id: UUID
    user_id: UUID
    signature_data: str  # Base64 image or DocuSign envelope ID
    signed_at: datetime
    ip_address: str
    is_valid: bool
```

---

## Security Architecture

### Authentication & Authorization

**Auth0 Integration:**
- OAuth 2.0 + OpenID Connect
- JWT tokens (access + refresh)
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)

**Roles:**
- `user` - Can create sessions, negotiate
- `business` - Multi-user accounts, custom templates
- `enterprise` - White-label, API access, dedicated support
- `admin` - Platform administration

### Data Encryption

**At Rest:**
- GCS: Server-side encryption with Google-managed keys
- PostgreSQL: Transparent Data Encryption (TDE)
- Secrets: Cloud Secret Manager with automatic rotation

**In Transit:**
- TLS 1.3 for all API traffic
- WebSocket Secure (WSS) for real-time
- Certificate management via Google-managed certificates

### Privacy & Compliance

**Data Handling:**
- End-to-end encryption for audio recordings
- Automatic PII scrubbing from transcripts
- Anonymization for AI training data
- Right to erasure (GDPR Article 17)

**Compliance:**
- SOC 2 Type II (target: Month 12)
- GDPR compliance (EU users)
- CCPA compliance (California users)
- HIPAA compliance (healthcare industry, Phase 2)

---

## Scalability & Performance

### Target SLAs

| Metric | Target |
|--------|--------|
| API Response Time (p95) | <200ms |
| API Response Time (p99) | <500ms |
| Conflict Detection Time | <5 seconds |
| Contract Generation Time | <10 seconds |
| System Uptime | 99.9% |
| Concurrent Users | 10,000+ |

### Scaling Strategy

**Horizontal Scaling:**
- GKE autoscaling (HPA + VPA)
- Load balancing across pods
- Database read replicas (PostgreSQL)
- Redis cluster mode

**Caching:**
- Redis for session data, rate limiting
- CDN for static assets (Cloud CDN)
- API response caching (conditional)

**Database Optimization:**
- Connection pooling (pgbouncer)
- Query optimization (EXPLAIN ANALYZE)
- Indexing strategy (B-tree, GIN for full-text)
- Partitioning for large tables (Phase 2)

---

## Monitoring & Observability

### Metrics (Prometheus + Cloud Monitoring)

- `contractual_sessions_total{status}` - Session count by status
- `contractual_conflicts_detected_total{topic}` - Conflicts by topic
- `contractual_api_latency_seconds` - API latency histogram
- `contractual_ai_api_calls_total{provider}` - AI API usage
- `contractual_ai_cost_usd` - AI cost tracking

### Logging (Cloud Logging)

- Structured JSON logs
- Request tracing (correlation IDs)
- Error tracking (Sentry integration)
- Audit logs (all contract signatures, resolutions)

### Alerting

- PagerDuty for critical incidents
- Slack for warnings
- Email for non-urgent notifications

---

## Deployment Architecture

### Kubernetes (GKE)

```yaml
# k8s/contractual-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: contractual-api
  namespace: contractual
spec:
  replicas: 3
  selector:
    matchLabels:
      app: contractual-api
  template:
    metadata:
      labels:
        app: contractual-api
    spec:
      containers:
      - name: api
        image: gcr.io/pnkln/contractual-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: contractual-secrets
              key: database_url
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: contractual-secrets
              key: anthropic_api_key
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
```

### CI/CD Pipeline

**GitHub Actions:**
1. Run tests (pytest + coverage)
2. Lint code (black, isort, mypy, flake8)
3. Build Docker image
4. Push to Google Container Registry (GCR)
5. Deploy to GKE (rolling update)

---

## Cost Projections

### Infrastructure Costs (Monthly)

| Service | Usage | Cost |
|---------|-------|------|
| GKE (3 nodes) | n1-standard-2 | $150 |
| PostgreSQL (Cloud SQL) | db-n1-standard-2 | $100 |
| Redis (Memorystore) | 1GB Standard | $40 |
| Cloud Storage (GCS) | 100GB + 10K ops | $5 |
| Cloud Load Balancing | 100GB egress | $20 |
| Cloud Monitoring | Standard tier | $10 |
| **Subtotal** | | **$325** |

### AI API Costs (Monthly)

| Provider | Usage | Cost per Unit | Monthly Cost |
|----------|-------|---------------|--------------|
| Anthropic Claude | 10M tokens | $0.03/1K tokens | $300 |
| OpenAI Whisper | 1000 hours | $0.006/min | $360 |
| DocuSign API | 500 envelopes | $0.50/envelope | $250 |
| **Subtotal** | | | **$910** |

**Total Monthly Cost (100 active users)**: ~$1,235
**Cost per Active User**: ~$12.35
**Target Revenue per User**: $50-150/month
**Gross Margin**: 75-90%

---

## Development Roadmap

### Phase 1: MVP (Months 1-6)
- ✅ Conversation capture (audio recording + transcription)
- ✅ Basic conflict detection (payment, timeline, scope)
- ✅ Side-by-side comparison UI
- ✅ Simple resolution workflow
- ✅ Document generation (PDF)
- ✅ E-signature (DocuSign integration)

### Phase 2: Enhancement (Months 7-12)
- Advanced conflict detection (all legal categories)
- Industry-specific templates (10+ industries)
- AI learning from user resolutions
- Mobile app (iOS + Android)
- Real-time collaboration features
- Analytics dashboard

### Phase 3: Scale (Year 2)
- Custom fine-tuned AI models
- White-label solution for enterprises
- API for third-party integrations
- Marketplace for templates and services
- Multi-language support
- Advanced compliance features (HIPAA)

---

## Testing Strategy

### Unit Tests
- Pytest for all services
- 80%+ code coverage target
- Mock AI API calls (avoid costs)

### Integration Tests
- Test database interactions
- Test AI API integrations
- Test e-signature flows

### End-to-End Tests
- Playwright for UI testing
- Full user journeys (record → detect → resolve → sign)
- Cross-browser testing

### Load Tests
- k6 for load testing
- Target: 1,000 concurrent users
- Simulate realistic negotiation workflows

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Author**: PNKLN Core Stack / ShadowTag-v2 FastAPI Services
**Status**: Technical Planning Phase
