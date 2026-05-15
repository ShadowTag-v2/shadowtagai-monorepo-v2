# War Room Architecture — Technical Design Document

> **Codename**: Murder Board
> **API**: Oracle Studio v2 (7-Step Cognitive Pipeline)
> **Queue**: Google Cloud Tasks (per doctrine)
> **Database**: Firestore (per doctrine)

---

## Pipeline Overview

```
Client Vent Mode Session
          │
          ▼
  ┌──────────────────────────────────────────────────────────────┐
  │  MURDER BOARD — 7-Step Async Cognitive Pipeline               │
  │                                                                │
  │  1. INTAKE EXTRACTION                                          │
  │     └─ Raw transcript normalization + entity extraction        │
  │  2. WEB OSINT                                                  │
  │     └─ Vertex AI Enterprise Search (ZDR, privilege-sealed)     │
  │  3. VERB AUDIT                                                 │
  │     └─ Kinematic action verb analysis (causes of action map)   │
  │  4. ORACLE SYNTHESIS                                           │
  │     └─ Multi-model strategy memo (Gemini Pro + Claude)         │
  │  5. CITATION CHAIN                                             │
  │     └─ Authority validation + relevance scoring                │
  │  6. BRIEF BUILDER                                              │
  │     └─ Attorney Work-Product PDF assembly                      │
  │  7. VAULT PUSH                                                 │
  │     └─ Clio/OneDrive vault + Shadow Invoice + Heppner receipt  │
  └──────────────────────────────────────────────────────────────┘
          │
          ▼
  Lawyer wakes up to finished intelligence package
```

---

## Stage Details

### Stage 1: Intake Extraction

**Model**: gemini-3.1-flash-lite-preview-thinking (cost-optimized)
**Input**: Raw SSE transcript from Vent Mode session
**Output**: Structured JSON

```json
{
  "entities": ["John Doe", "Acme Corp", "Jane Smith MD"],
  "dates": ["2026-01-15", "2025-03-22"],
  "locations": ["Los Angeles, CA", "New York, NY"],
  "claims": ["medical malpractice", "wrongful termination"],
  "emotional_state": "high distress",
  "urgency_flags": ["statute of limitations approaching", "evidence spoliation risk"]
}
```

### Stage 2: Web OSINT

**Engine**: Vertex AI Enterprise Search (Enterprise ZDR enforced)
**Searches**: Medical records, court filings, news, social media, business registrations
**Output**: Privileged search results (attorney work-product)

### Stage 3: Verb Audit (Action Verb Auditor)

**Purpose**: Maps kinematic action verbs to legal elements of causes of action.

**Verb Ledger Schema** (Firestore: `verb_ledger` collection):
```
{
  session_id: string,
  firm_id: string,
  timestamp: ISO8601,
  verbs: [
    {
      verb: "hit",
      context: "He hit me in the parking lot",
      cause_of_action: "Battery",
      element_matched: "intentional harmful contact",
      confidence: 0.94,
      kinematic_classification: "CONTACT_FORCE"
    }
  ],
  causes_of_action_summary: {
    "Battery": { count: 3, avg_confidence: 0.91 },
    "Negligence": { count: 2, avg_confidence: 0.87 }
  }
}
```

### Stage 4: Oracle Synthesis

**Primary Model**: Gemini Pro (with Aegaeon context cache)
**Fallback**: Claude Sonnet 4
**Prompt**: Full LAWYER_ORACLE_PROMPT with enriched context from Stages 1-3
**Output**: Structured strategy memo with sections: FACTS | ANALYSIS | STRATEGY | RISKS | DEADLINES

### Stage 5: Citation Chain

**Process**:
1. Extract all legal authorities from Oracle output
2. Validate against Westlaw/LexisNexis stubs
3. Score relevance (0.0-1.0) for each citation
4. Flag any unverified or potentially hallucinated citations

**Schema**:
```json
{
  "citations": [
    {
      "index": 1,
      "authority": "Cal. Civ. Code § 1714",
      "type": "statute",
      "excerpt": "Everyone is responsible for an injury...",
      "relevance_score": 0.95,
      "verified": true,
      "source": "westlaw_stub"
    }
  ]
}
```

### Stage 6: Brief Builder

**Output**: Attorney Work-Product PDF
**Sections**: Privilege Header → Executive Summary → Fact Timeline →
Legal Issues → Causes of Action → Recommended Strategy →
Citations Appendix → Kovel Attestation → Verb Matrix

### Stage 7: Vault Push

**Targets**:
- Clio API v4 (primary)
- OneDrive (secondary, for firms without Clio)
- Shadow Invoice (auto-draft billable time entry)
- Heppner Receipt (cryptographic privilege attestation)

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/war-room/murder-board` | Trigger full 7-step pipeline |
| GET | `/api/war-room/status/:sessionId` | Pipeline progress tracking |
| GET | `/api/war-room/verb-audit/:sessionId` | Verb audit results |
| GET | `/api/war-room/citation-chain/:sessionId` | Citation validation results |
| GET | `/api/war-room/brief/:sessionId` | Download generated brief |

---

## Cloud Tasks Integration

Each stage is enqueued as an independent Cloud Task, enabling:
- Retry with exponential backoff
- Per-stage failure isolation
- Progress tracking via Firestore status documents
- Rate limiting per firm/tenant

```
Queue: kovelai-murder-board
Task naming: {session_id}/stage-{1-7}
Max retries: 3
Deadline: 300s per stage
```

---

## Security Invariants

1. ALL pipeline output is Attorney Work-Product (never shown to client)
2. ALL search queries run through Enterprise ZDR (zero data retention)
3. Pipeline is ONLY triggered with valid S.E.U. token + Clio OAuth
4. Transcript is immediately purged from RAM after Stage 1 extraction
5. Citation validation stubs NEVER store query text
6. PDF brief includes embedded Kovel attestation hash
