# Transcript-to-Contract System Architecture

## AI-Powered Contract Generation Platform

---

## 1. System Overview

### 1.1 Vision

Transform spoken negotiations into legally-binding, attorney-reviewed contracts that enable laypersons to prove breach of contract in small claims court.

### 1.2 Core Architecture

```

┌─────────────────────────────────────────────────────────────────────────┐
│                      TRANSCRIPT-TO-CONTRACT PLATFORM                    │
│                         (Google Cloud Platform)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   CUSTOMER    │          │   ATTORNEY    │          │     ADMIN     │
│   WEB/MOBILE  │          │   DASHBOARD   │          │   PORTAL      │
│     APP       │          │  (Uber Law)   │          │               │
└───────┬───────┘          └───────┬───────┘          └───────┬───────┘
        │                          │                          │
        └──────────────────┬───────┴───────┬──────────────────┘
                          │               │
                          ▼               ▼
                  ┌─────────────────────────────┐
                  │      API GATEWAY            │
                  │   (Cloud Load Balancer)     │
                  │   - Auth (Identity Platform)│
                  │   - Rate Limiting           │
                  │   - TLS Termination         │
                  └─────────────┬───────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌────────────────┐      ┌──────────────┐
│  INGESTION    │      │  CONTRACT      │      │   REVIEW     │
│  SERVICE      │      │  GENERATION    │      │   SERVICE    │
│  (FastAPI)    │      │  SERVICE       │      │  (FastAPI)   │
│               │      │  (FastAPI)     │      │              │
│ • Upload      │      │ • LLM calls    │      │ • Attorney   │
│   Audio       │      │ • Clause lib   │      │   matching   │
│ • Consent     │      │ • Jurisdiction │      │ • Approval   │
│   Validation  │      │   rules        │      │   workflow   │
└───────┬───────┘      └────────┬───────┘      └──────┬───────┘
        │                       │                      │
        └───────────────┬───────┴───────┬──────────────┘
                        │               │
                        ▼               ▼
            ┌───────────────────────────────────┐
            │       TRANSCRIPTION SERVICE       │
            │     (Google Speech-to-Text API)   │
            │   OR AssemblyAI (speaker diarize) │
            └───────────────┬───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│   STORAGE     │   │   DATABASE   │   │   SEARCH     │
│   (GCS)       │   │ (PostgreSQL) │   │ (Vertex AI)  │
│               │   │              │   │              │
│ • Audio files │   │ • Contracts  │   │ • Semantic   │
│ • Transcripts │   │ • Users      │   │   search     │
│ • Evidence    │   │ • Attorneys  │   │ • Clause lib │
│   photos      │   │ • Metrics    │   │              │
└───────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                    ▼               ▼
        ┌────────────────┐  ┌──────────────┐
        │  E-SIGNATURE   │  │  PAYMENT     │
        │  (DocuSign API)│  │  (Stripe)    │
        └────────────────┘  └──────────────┘

```

---

## 2. Service Breakdown

### 2.1 Ingestion Service

**Responsibility**: Accept customer uploads, validate consent, trigger transcription

**Tech Stack**:

- **Framework**: FastAPI (Python 3.11+)

- **Deployment**: Cloud Run (serverless, auto-scaling)

- **Storage**: GCS (audio files, consent forms)

- **Queue**: Pub/Sub (asynchronous transcription)

**API Endpoints**:

```python
POST   /api/v1/ingestion/upload          # Upload audio + consent form
GET    /api/v1/ingestion/status/{job_id} # Check transcription status
POST   /api/v1/ingestion/validate-consent # Verify consent signatures
DELETE /api/v1/ingestion/{job_id}        # GDPR right to erasure

```

**Key Features**:

1. **Multi-Format Support**: MP3, WAV, M4A, FLAC (auto-conversion to 16kHz mono)

2. **Consent Validation**:

   - Detect customer location (GPS)

   - Require all-party consent in 2-party states (CA, FL, IL, PA, etc.)

   - Generate consent form PDF (DocuSign for signature)

3. **Audio Quality Check**:

   - Min duration: 30 seconds

   - Max duration: 4 hours

   - SNR threshold: >10dB (reject if too noisy)

4. **Security**:

   - End-to-end encryption (TLS 1.3)

   - Signed URLs (1-hour expiry)

   - Virus scanning (ClamAV)

**Data Flow**:

```

Customer Upload → GCS Bucket → Pub/Sub Message → Transcription Service
                                     ↓
                              PostgreSQL (job metadata)

```

---

### 2.2 Transcription Service

**Responsibility**: Convert audio to text with speaker diarization

**Tech Stack**:

- **Primary**: Google Speech-to-Text V2 (chirp model)

- **Fallback**: AssemblyAI (if Google fails or for advanced features)

- **Deployment**: Cloud Run (triggered by Pub/Sub)

**Features**:

1. **Speaker Diarization**: Identify "Customer" vs. "Shop Owner"

2. **Legal Vocabulary**: Custom vocabulary (e.g., "indemnify", "warranty", "jurisdiction")

3. **Timestamp Precision**: Word-level timestamps (for contract term sourcing)

4. **Confidence Scoring**: Flag low-confidence segments for attorney review

**Output Format** (JSON):

```json
{
  "job_id": "abc123",
  "duration_seconds": 2220,
  "speakers": [
    {"id": "speaker_0", "label": "Customer"},
    {"id": "speaker_1", "label": "Shop Owner"}
  ],
  "segments": [
    {
      "speaker": "speaker_0",
      "start_time": 0.0,
      "end_time": 5.2,
      "text": "I need the head gasket replaced on my F-150.",
      "confidence": 0.97
    },
    {
      "speaker": "speaker_1",
      "start_time": 5.5,
      "end_time": 12.1,
      "text": "Okay, we can do that. I'll use OEM parts. Should take about five business days.",
      "confidence": 0.95
    }
  ],
  "low_confidence_segments": [23, 47, 89]  // Segment indices
}

```

**Cost Optimization**:

- **Google Pricing**: $0.016/min (standard model) → $2.37 for 37-min negotiation

- **AssemblyAI**: $0.00025/sec → $0.56 for same

- **Strategy**: Use AssemblyAI by default (75% cheaper), Google for high-stakes contracts

---

### 2.3 Contract Generation Service

**Responsibility**: Generate legally-compliant contract draft from transcript

**Tech Stack**:

- **LLM**: Claude 3.5 Sonnet (primary), GPT-4 Turbo (fallback)

- **Framework**: FastAPI + LangChain

- **Deployment**: GKE (for GPU inference) OR Vertex AI (managed)

- **Clause Library**: PostgreSQL + Vertex AI Vector Search (semantic retrieval)

**Architecture**:

```

Transcript → Term Extraction → Clause Retrieval → Draft Assembly → Validation
                 (LLM)          (Vector Search)      (LLM)         (Rules Engine)

```

**Key Components**:

#### 2.3.1 Term Extraction

**Prompt** (Claude 3.5 Sonnet):

```

You are a legal contract analyst. Extract key terms from this negotiation transcript.

TRANSCRIPT:
{transcript_text}

JURISDICTION: {state}
CONTRACT TYPE: {type}  # e.g., "Auto Repair Service Agreement"

OUTPUT FORMAT (JSON):
{
  "parties": {
    "customer": {"name": "...", "contact": "..."},
    "service_provider": {"name": "...", "contact": "..."}
  },
  "services": [
    {"description": "...", "timestamp_ref": "..."}
  ],
  "payment": {
    "total": 2300.00,
    "currency": "USD",
    "terms": "Due upon completion",
    "timestamp_ref": "14:32"
  },
  "timeline": {
    "start_date": "2025-11-18",
    "completion_date": "2025-11-25",
    "timestamp_ref": "22:18"
  },
  "warranties": [
    {"description": "12 months / 12,000 miles", "timestamp_ref": "31:45"}
  ],
  "ambiguities": [
    {"issue": "Customer said 'done right' (vague)", "segment_id": 67}
  ]
}

```

**Validation**:

- Require at least: parties, services, payment, timeline

- Flag missing elements for attorney review

#### 2.3.2 Clause Retrieval

**Clause Library Schema**:

```sql
CREATE TABLE contract_clauses (
  id UUID PRIMARY KEY,
  clause_type VARCHAR(50),  -- e.g., "warranty", "limitation_of_liability", "dispute_resolution"
  jurisdiction VARCHAR(10),  -- e.g., "TX", "CA", "ALL"
  contract_type VARCHAR(50), -- e.g., "auto_repair", "contractor", "real_estate"
  template_text TEXT,
  required BOOLEAN,          -- Must include in contract?
  embedding VECTOR(768)      -- Vertex AI embedding for semantic search
);

```

**Example Clauses** (Texas Auto Repair):

```sql
INSERT INTO contract_clauses VALUES (
  gen_random_uuid(),
  'warranty',
  'TX',
  'auto_repair',
  'Shop warrants all parts and labor for {warranty_period}. If defects arise during warranty period, Shop will re-perform work at no charge. Warranty void if Customer modifies vehicle or uses aftermarket parts.',
  TRUE,
  vertex_ai_embed('warranty coverage for auto repairs')
);

```

**Retrieval Logic**:

1. Embed extracted terms (Vertex AI)

2. Vector search for top 5 relevant clauses per term

3. Filter by jurisdiction + contract type

4. Rank by relevance score

#### 2.3.3 Draft Assembly

**Prompt** (Claude 3.5 Sonnet):

```

You are a contract drafting attorney licensed in {state}. Generate a legally-binding contract.

EXTRACTED TERMS:
{terms_json}

RETRIEVED CLAUSES:
{clauses_json}

REQUIREMENTS:

1. Use plain language (8th-grade reading level)

2. Include all required clauses for {jurisdiction}

3. Resolve ambiguities (note your reasoning)

4. Add timestamp references (link each term to transcript segment)

5. Optimize for layperson to prove breach in small claims court

OUTPUT FORMAT (Markdown):

# {CONTRACT_TITLE}

## Parties

...

## Services

...

## Payment Terms

...

[etc.]

## AI Reasoning Appendix

For each clause, explain:

- Why included (legal requirement? party agreement? best practice?)

- Transcript reference (timestamp)

- Ambiguities resolved

```

**Output Example**:

```markdown

# AUTO REPAIR SERVICE AGREEMENT

**Effective Date**: November 18, 2025

## 1. Parties

This agreement is between:

- **Customer**: John Doe, 123 Main St, Austin, TX 78701, (512) 555-1234

- **Shop**: ABC Auto Repair LLC, 456 Elm St, Austin, TX 78702, (512) 555-5678

## 2. Services

Shop agrees to perform the following services on Customer's vehicle (2015 Ford F-150, VIN: 1FTFW1ET5FKE12345):


- **Replace head gasket** using OEM Ford parts (Part No. FL3Z-6051-A)

  - *Source*: Transcript 2:15 - "I need the head gasket replaced" / 8:42 - "I'll use OEM parts"

## 3. Payment


- **Total Cost**: $2,300.00 USD

  - Labor: $1,500 (12 hours @ $125/hour)

  - Parts: $800

- **Payment Due**: Upon completion of services

- **Payment Method**: Cash, check, or credit card

- *Source*: Transcript 14:32 - "So $2,300 total?"

## 4. Timeline


- **Start Date**: November 18, 2025 (vehicle drop-off)

- **Completion Date**: November 25, 2025 (5 business days)

- **Late Penalty**: $50/day if not completed by deadline (max $500)

- *Source*: Transcript 22:18 - "Should take about five business days"

## 5. Warranty

Shop warrants all parts and labor for **12 months OR 12,000 miles** (whichever occurs first), starting from completion date. If defects arise during warranty period, Shop will re-perform work at no charge.

**Warranty Void If**:

- Customer modifies vehicle

- Customer uses aftermarket parts for related systems

- Damage caused by accident or misuse

*Source*: Transcript 31:45 - "We do a 12-month, 12,000-mile warranty"

## 6. Limitation of Liability

Shop's total liability for any damages (including negligence) shall not exceed **$5,000**. Shop is NOT liable for:

- Consequential damages (e.g., lost wages, rental car costs)

- Pre-existing vehicle conditions not disclosed by Customer

*AI Note*: Added to comply with Texas law (caps on service provider liability)

## 7. Photographic Evidence


- Customer photographed vehicle on November 18, 2025 at 9:15 AM (before drop-off)

- Customer will photograph vehicle upon completion (before payment)

- Photos are part of this contract

*AI Note*: Added to enable small claims court evidence submission

## 8. Dispute Resolution

Any disputes under this contract shall be resolved in **Small Claims Court, Travis County, Texas**. Parties waive right to jury trial.

*AI Note*: Required for small claims court jurisdiction

## 9. Entire Agreement

This contract represents the entire agreement between parties. Any modifications must be in writing and signed by both parties.

## 10. Signatures

By signing below, parties agree to all terms.

**Attorney Certification**: This contract has been reviewed by [Attorney Name], State Bar of Texas No. [XXXXX], on [Date].

---
**Customer Signature**: _______________________  **Date**: ___________

**Shop Signature**: _______________________  **Date**: ___________

---

# AI REASONING APPENDIX

## Why Each Clause Was Included

### Services (§2)


- **Legal Basis**: Texas requires clear description of services (Tex. Bus. & Com. Code § 17.46)

- **Ambiguity Resolved**: Customer said "done right" (vague) → AI added "using OEM Ford parts" based on Shop's statement at 8:42

- **Transcript References**: 2:15, 8:42, 19:33

### Payment (§3)


- **Legal Basis**: Meeting of the minds on price (essential contract element)

- **Ambiguity Resolved**: None (parties clearly agreed on $2,300)

- **Transcript References**: 14:32

### Timeline (§4)


- **Legal Basis**: Certainty of performance (Texas common law)

- **Ambiguity Resolved**: "About five business days" → AI set firm deadline (Nov 25) + late penalty

- **Transcript References**: 22:18

- **Late Penalty Rationale**: Incentivizes timely performance; enforceable in TX small claims

### Warranty (§5)


- **Legal Basis**: Texas Deceptive Trade Practices Act (DTPA) encourages written warranties

- **Ambiguity Resolved**: None (parties clearly agreed on 12mo/12K miles)

- **Transcript References**: 31:45

### Limitation of Liability (§6)


- **Legal Basis**: Texas allows contractual liability caps (not unconscionable if reasonable)

- **AI Addition**: Not discussed in transcript, but standard for service agreements

- **Attorney Review Required**: Ensure $5K cap is reasonable given $2.3K service cost

### Photographic Evidence (§7)


- **Legal Basis**: Texas Rules of Evidence (photos are admissible)

- **AI Addition**: Not discussed, but critical for small claims court proof

- **Rationale**: Prevents "he said, she said" disputes over pre-existing damage

### Dispute Resolution (§8)


- **Legal Basis**: Texas allows contractual forum selection (small claims)

- **AI Addition**: Required for small claims court jurisdiction (max $20K in TX)

- **Rationale**: Enables layperson to sue without lawyer

### Entire Agreement (§9)


- **Legal Basis**: Parol Evidence Rule (Texas common law)

- **Rationale**: Prevents Shop from claiming "we agreed to something else verbally"

---

**Draft Generation Time**: 8.3 seconds
**LLM Used**: Claude 3.5 Sonnet (2025-11-17)
**Clause Library Version**: 2.1.4
**Jurisdiction Rules Version**: TX-2025-Q4

```

#### 2.3.4 Validation Rules Engine

**Checks** (before sending to attorney):

1. **Completeness**: All required clauses present (by jurisdiction)

2. **Consistency**: Payment amount matches transcript

3. **Legal Compliance**: Complies with state-specific rules (e.g., TX DTPA)

4. **Readability**: Flesch-Kincaid grade level ≤10

5. **Timestamp Coverage**: ≥80% of terms have transcript references

**If Validation Fails**: Flag for attorney with specific issues

---

### 2.4 Review Service (Uber Law Platform)

**Responsibility**: Connect customers with licensed attorneys for contract review

**Tech Stack**:

- **Framework**: FastAPI

- **Deployment**: GKE (persistent connections for WebSocket notifications)

- **Queue**: Cloud Tasks (attorney assignment)

- **Notifications**: SendGrid (email), Twilio (SMS)

**API Endpoints**:

```python
POST   /api/v1/review/request            # Customer requests review
GET    /api/v1/review/available-attorneys # Attorney queries available contracts
POST   /api/v1/review/{contract_id}/claim # Attorney claims contract for review
PUT    /api/v1/review/{contract_id}/submit # Attorney submits reviewed contract
POST   /api/v1/review/{contract_id}/approve # Customer approves attorney changes

```

**Attorney Matching Algorithm**:

```python
def match_attorney(contract):
    # Step 1: Filter by jurisdiction
    attorneys = Attorney.query.filter(
        Attorney.licenses.contains(contract.jurisdiction),
        Attorney.active == True,
        Attorney.malpractice_insurance_valid == True
    )

    # Step 2: Prioritize by experience in contract type
    attorneys = attorneys.order_by(
        Attorney.contract_types[contract.type].desc(),  # e.g., "auto_repair"
        Attorney.avg_review_time.asc(),
        Attorney.rating.desc()
    )

    # Step 3: Round-robin assignment (fairness)
    return attorneys.first()

```

**Attorney Dashboard** (React SPA):

```

┌────────────────────────────────────────────────────────────┐
│  UBER LAW - ATTORNEY DASHBOARD                             │
├────────────────────────────────────────────────────────────┤
│  Available Contracts (5)                    [Sort ▼ Fee]   │
├────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🚗 Auto Repair - Austin, TX         $100  [Claim]  │   │
│  │ Customer: John D.                                    │   │
│  │ Shop: ABC Auto Repair                                │   │
│  │ Submitted: 2 minutes ago                             │   │
│  │ Complexity: Medium (12-hour estimate)                │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🏠 Contractor - Dallas, TX          $150  [Claim]  │   │
│  │ Customer: Jane S.                                    │   │
│  │ Contractor: XYZ Construction                         │   │
│  │ Submitted: 15 minutes ago                            │   │
│  │ Complexity: High (multi-party, $25K value)           │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘

```

**Review Workflow**:

```

1. Attorney claims contract

2. Dashboard displays:

   - Transcript (left pane)

   - AI draft (center pane, editable)

   - Clause library (right pane, searchable)

3. Attorney edits contract in-place

4. Attorney adds notes (e.g., "Added warranty void clause")

5. Attorney clicks "Submit for Customer Approval"

6. Customer reviews changes → Approve/Request Revision

7. If approved → Contract locked, attorney paid

```

---

### 2.5 E-Signature Service

**Responsibility**: Facilitate legally-binding signatures

**Integration**: DocuSign API (primary), Adobe Sign (fallback)

**Workflow**:

```

1. Customer approves attorney-reviewed contract

2. Platform generates DocuSign envelope:

   - Recipients: Customer, Shop Owner, Attorney (witness)

   - Signing order: Sequential (Customer → Shop → Attorney)

   - Auth: SMS OTP (for shop owner), email (for customer)

3. DocuSign sends emails/SMS to signers

4. Each signer signs via DocuSign UI

5. Completed contract PDF stored in GCS

6. Platform triggers payment to attorney (if not paid yet)

```

**Legal Compliance**:

- **ESIGN Act (Federal)**: Electronic signatures are legally binding if parties consent

- **UETA (Uniform Electronic Transactions Act)**: Adopted by 47 states

- **DocuSign Certificate**: Provides audit trail (timestamp, IP address, authentication method)

---

## 3. Data Model

### 3.1 PostgreSQL Schema

```sql
-- Users (customers)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  phone VARCHAR(20),
  full_name VARCHAR(255),
  created_at TIMESTAMP DEFAULT NOW(),
  location_state VARCHAR(2),  -- For consent requirements
  stripe_customer_id VARCHAR(255)
);

-- Attorneys
CREATE TABLE attorneys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  bar_number VARCHAR(50) NOT NULL,
  licenses JSONB,  -- e.g., ["TX", "CA", "NY"]
  malpractice_insurance_policy VARCHAR(255),
  malpractice_insurance_expiry DATE,
  contract_types JSONB,  -- e.g., {"auto_repair": 150, "real_estate": 25} (experience counts)
  rating DECIMAL(3,2),  -- 0.00 - 5.00
  avg_review_time_minutes INTEGER,
  total_reviews INTEGER DEFAULT 0,
  total_earnings_cents BIGINT DEFAULT 0,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Contracts
CREATE TABLE contracts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  attorney_id UUID REFERENCES attorneys(id),
  status VARCHAR(50) NOT NULL,  -- 'transcribing', 'draft_generated', 'attorney_review', 'customer_approval', 'signed', 'cancelled'
  contract_type VARCHAR(50),  -- 'auto_repair', 'contractor', 'real_estate', etc.
  jurisdiction VARCHAR(2),  -- 'TX', 'CA', etc.

  -- Files
  audio_file_url TEXT,
  consent_form_url TEXT,
  transcript_json JSONB,
  draft_markdown TEXT,
  attorney_reviewed_markdown TEXT,
  signed_pdf_url TEXT,

  -- Metadata
  negotiation_duration_seconds INTEGER,
  parties JSONB,  -- {"customer": {...}, "service_provider": {...}}
  payment_amount_cents BIGINT,
  timeline JSONB,  -- {"start_date": "...", "completion_date": "..."}

  -- Attorney review
  attorney_claimed_at TIMESTAMP,
  attorney_submitted_at TIMESTAMP,
  attorney_notes TEXT,
  attorney_fee_cents INTEGER,

  -- Signatures
  customer_signed_at TIMESTAMP,
  counterparty_signed_at TIMESTAMP,
  docusign_envelope_id VARCHAR(255),

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Contract clauses library
CREATE TABLE contract_clauses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  clause_type VARCHAR(50) NOT NULL,
  jurisdiction VARCHAR(10) NOT NULL,  -- 'ALL' for universal clauses
  contract_type VARCHAR(50) NOT NULL,
  template_text TEXT NOT NULL,
  required BOOLEAN DEFAULT FALSE,
  embedding VECTOR(768),  -- Vertex AI embedding
  created_at TIMESTAMP DEFAULT NOW()
);

-- Payments
CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contract_id UUID REFERENCES contracts(id),
  attorney_id UUID REFERENCES attorneys(id),
  amount_cents INTEGER NOT NULL,
  stripe_payment_intent_id VARCHAR(255),
  status VARCHAR(50),  -- 'pending', 'succeeded', 'failed'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Audit log (compliance)
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_type VARCHAR(50),  -- 'contract', 'attorney', 'user'
  entity_id UUID,
  action VARCHAR(100),  -- 'created', 'status_changed', 'attorney_assigned', etc.
  actor_id UUID,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

```

### 3.2 Indexes

```sql
CREATE INDEX idx_contracts_user ON contracts(user_id);
CREATE INDEX idx_contracts_attorney ON contracts(attorney_id);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_attorneys_licenses ON attorneys USING GIN(licenses);
CREATE INDEX idx_attorneys_active ON attorneys(active) WHERE active = TRUE;
CREATE INDEX idx_clauses_embedding ON contract_clauses USING ivfflat(embedding vector_cosine_ops);

```

---

## 4. Infrastructure (Google Cloud Platform)

### 4.1 GKE Cluster Configuration

```yaml

# k8s/transcript-to-contract-cluster.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: transcript-to-contract

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: contract-generation-service
  namespace: transcript-to-contract
spec:
  replicas: 3
  selector:
    matchLabels:
      app: contract-generation
  template:
    metadata:
      labels:
        app: contract-generation
    spec:
      containers:

      - name: api
        image: gcr.io/PROJECT_ID/contract-generation:latest
        ports:

        - containerPort: 8000
        env:

        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url

        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-credentials
              key: anthropic-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"

```

### 4.2 Cloud Run (Serverless) for Low-Traffic Services

```yaml

# Ingestion Service (Cloud Run)

service: ingestion-service
runtime: python311
entrypoint: uvicorn src.api.ingestion:app --host 0.0.0.0 --port $PORT

env_variables:
  GCS_BUCKET: transcript-to-contract-uploads
  PUBSUB_TOPIC: transcription-jobs

resources:
  memory: 1Gi
  cpu: 1

scaling:
  min_instances: 0  # Scale to zero when idle
  max_instances: 10

```

### 4.3 Cost Estimate (Year 1)

| Service | Usage | Unit Cost | Monthly Cost |
|---------|-------|-----------|--------------|
| **GKE** | 3 nodes (n1-standard-2) | $0.10/hr | $216 |
| **Cloud Run** | 1M requests, 100ms avg | $0.40/M requests | $0.40 |
| **PostgreSQL** | Cloud SQL (db-n1-standard-2) | $0.09/hr | $64.80 |
| **GCS** | 1TB storage, 10TB egress | $0.02/GB + $0.12/GB | $1,220 |
| **Vertex AI** | 1M embedding API calls | $0.0001/call | $100 |
| **Speech-to-Text** | 10K minutes (AssemblyAI) | $0.00025/sec | $25 |
| **LLM API** | 1K contracts (Claude Sonnet) | $15/1M input + $75/1M output | $300 |
| **DocuSign** | 1K envelopes | $0.50/envelope | $500 |
| **Total** | | | **$2,426/month** |

**Year 1 Projection** (1,000 contracts):

- Infrastructure: $29,112

- **Cost per Contract**: $29.11

- **Customer Price**: $500-1,000

- **Gross Margin**: 94-97%

---

## 5. Security & Compliance

### 5.1 Data Encryption

**At Rest**:

- GCS: AES-256 (Google-managed keys)

- PostgreSQL: Transparent Data Encryption (TDE)

- Secrets: Google Secret Manager

**In Transit**:

- TLS 1.3 (all API endpoints)

- mTLS (service-to-service communication within GKE)

### 5.2 Access Control

**Identity & Access Management (IAM)**:

```

User Roles:

- customer: Can upload files, view own contracts

- attorney: Can claim/review contracts, view transcripts

- admin: Full access (support team)

Service Accounts:

- contract-generation-sa: Read/write to GCS, PostgreSQL

- transcription-sa: Read from GCS, write to Pub/Sub

- backup-sa: Read-only access to PostgreSQL (for backups)

```

**API Authentication**:

- Google Identity Platform (Firebase Auth)

- JWT tokens (1-hour expiry)

- Refresh tokens (30-day expiry)

### 5.3 GDPR/CCPA Compliance

**Right to Erasure**:

```python
@app.delete("/api/v1/users/{user_id}")
async def delete_user_data(user_id: UUID):
    # 1. Delete audio files from GCS
    await gcs.delete_folder(f"users/{user_id}/")

    # 2. Anonymize database records (retain for legal compliance)
    await db.execute("""
        UPDATE contracts
        SET
            audio_file_url = NULL,
            transcript_json = NULL,
            parties = jsonb_set(parties, '{customer}', '{"name": "REDACTED"}'::jsonb)
        WHERE user_id = :user_id
    """, {"user_id": user_id})

    # 3. Delete user account
    await db.execute("DELETE FROM users WHERE id = :user_id", {"user_id": user_id})

    return {"status": "deleted"}

```

**Data Retention Policy**:

- Audio files: Deleted 90 days after contract signing (unless dispute active)

- Transcripts: Retained 7 years (for legal compliance)

- Signed contracts: Retained indefinitely (customer can download anytime)

### 5.4 SOC 2 Type II Certification

**Timeline**: 6-12 months after launch

**Requirements**:

1. **Security**: Encryption, access controls, penetration testing

2. **Availability**: 99.9% uptime SLA

3. **Processing Integrity**: Audit logs, contract version control

4. **Confidentiality**: NDAs with all employees/contractors

5. **Privacy**: GDPR/CCPA compliance, data retention policies

---

## 6. Monitoring & Observability

### 6.1 Metrics (Cloud Monitoring)

**Application Metrics**:

```python
from prometheus_client import Counter, Histogram, Gauge

contracts_created = Counter('contracts_created_total', 'Total contracts created', ['contract_type'])
contract_generation_duration = Histogram('contract_generation_seconds', 'Time to generate contract')
attorney_queue_size = Gauge('attorney_queue_size', 'Contracts awaiting review')

```

**Infrastructure Metrics**:

- GKE: CPU/memory utilization, pod restarts, network I/O

- Cloud Run: Request count, latency, cold starts

- PostgreSQL: Connection pool size, query latency, deadlocks

**Business Metrics**:

- Contracts created (by type, jurisdiction)

- Attorney approval rate (% of drafts approved as-is)

- Customer satisfaction (NPS score)

- Revenue (by customer segment)

### 6.2 Logging (Cloud Logging)

**Structured Logging** (JSON):

```python
import structlog

log = structlog.get_logger()

log.info(
    "contract_generated",
    contract_id=contract.id,
    user_id=contract.user_id,
    contract_type=contract.contract_type,
    jurisdiction=contract.jurisdiction,
    llm_model="claude-3.5-sonnet",
    generation_time_seconds=8.3
)

```

**Log Retention**:

- Application logs: 30 days

- Audit logs: 7 years

- Error logs: 90 days

### 6.3 Alerting (Cloud Monitoring)

**Critical Alerts** (PagerDuty integration):

```yaml
alerts:

  - name: HighErrorRate
    condition: error_rate > 5%
    window: 5 minutes
    severity: critical
    notification: pagerduty


  - name: AttorneyQueueBacklog
    condition: attorney_queue_size > 50
    window: 30 minutes
    severity: warning
    notification: slack


  - name: DatabaseConnectionPoolExhausted
    condition: db_connections_available < 5
    window: 1 minute
    severity: critical
    notification: pagerduty

```

---

## 7. Deployment Pipeline

### 7.1 CI/CD (Cloud Build)

```yaml

# cloudbuild.yaml

steps:
  # Step 1: Run tests

  - name: 'python:3.11'
    entrypoint: 'bash'
    args:

      - '-c'

      - |
        pip install -r requirements.txt
        pytest tests/ --cov=src --cov-report=xml

  # Step 2: Build Docker image

  - name: 'gcr.io/cloud-builders/docker'
    args:

      - 'build'

      - '-t'

      - 'gcr.io/$PROJECT_ID/contract-generation:$COMMIT_SHA'

      - '.'

  # Step 3: Push image to GCR

  - name: 'gcr.io/cloud-builders/docker'
    args:

      - 'push'

      - 'gcr.io/$PROJECT_ID/contract-generation:$COMMIT_SHA'

  # Step 4: Deploy to GKE

  - name: 'gcr.io/cloud-builders/kubectl'
    args:

      - 'set'

      - 'image'

      - 'deployment/contract-generation-service'

      - 'api=gcr.io/$PROJECT_ID/contract-generation:$COMMIT_SHA'
    env:

      - 'CLOUDSDK_COMPUTE_ZONE=us-central1-a'

      - 'CLOUDSDK_CONTAINER_CLUSTER=transcript-to-contract-cluster'

```

### 7.2 Environments

| Environment | Purpose | Deployment Trigger |
|-------------|---------|-------------------|
| **Development** | Feature development, integration testing | Push to `develop` branch |
| **Staging** | Pre-production testing, attorney UAT | Push to `staging` branch |
| **Production** | Live customer traffic | Tag (e.g., `v1.2.3`) |

---

## 8. Disaster Recovery

### 8.1 Backup Strategy

**Database Backups** (Cloud SQL):

- **Automated backups**: Daily at 2 AM UTC (retained 30 days)

- **Point-in-time recovery**: Enabled (retain 7 days of binary logs)

- **Manual backups**: Before each major release

**File Backups** (GCS):

- **Replication**: Multi-region (us-central1 + us-east1)

- **Lifecycle policy**: Move to Nearline after 90 days (reduce cost)

- **Versioning**: Enabled (retain 10 versions)

### 8.2 Recovery Time Objective (RTO) & Recovery Point Objective (RPO)

| Scenario | RTO | RPO | Recovery Procedure |
|----------|-----|-----|-------------------|
| **Database failure** | 1 hour | 1 hour | Restore from automated backup |
| **GKE cluster failure** | 30 minutes | 0 (stateless) | Deploy to standby cluster |
| **GCS bucket deletion** | 4 hours | 24 hours | Restore from replicated bucket |
| **Complete region outage** | 2 hours | 1 hour | Failover to us-east1 |

---

## 9. Roadmap

### 9.1 Phase 1: MVP (Months 1-6)


- [x] Ingestion service (audio upload, consent validation)

- [x] Transcription service (Google Speech-to-Text)

- [x] Contract generation (Claude 3.5 Sonnet, basic clause library)

- [ ] Attorney review platform (Uber Law MVP)

- [ ] E-signature integration (DocuSign)

- [ ] Customer web app (React)

**Success Criteria**: 100 contracts generated, 10 attorneys onboarded

### 9.2 Phase 2: SMB Launch (Months 7-12)


- [ ] Mobile app (iOS, Android)

- [ ] Photographic evidence workflow

- [ ] Small claims court support (trial package generation)

- [ ] Payment integration (Stripe)

- [ ] Customer support portal

**Success Criteria**: 1,000 contracts, $2M ARR

### 9.3 Phase 3: Enterprise Expansion (Months 13-24)


- [ ] Zoom/Teams plugin (in-meeting contract generation)

- [ ] Multi-party contracts (>2 signers)

- [ ] Salesforce integration (CRM sync)

- [ ] Advanced analytics (contract performance, dispute rates)

- [ ] White-label solution (for law firms)

**Success Criteria**: 10 enterprise customers, $10M ARR

### 9.4 Phase 4: Platform Ecosystem (Months 25-36)


- [ ] Third-party integrations (QuickBooks, DocuSign CLM, etc.)

- [ ] Attorney marketplace (v2): ratings, specialties, pricing competition

- [ ] Contract template marketplace (customers buy/sell templates)

- [ ] International expansion (UK, Canada, Australia)

**Success Criteria**: $50M ARR, 100K contracts/year

---

**Document Version**: 1.0
**Last Updated**: 2025-11-17
**Author**: Architecture Team
**Status**: ✅ Ready for Implementation
