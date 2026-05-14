# Execution Plan: Prioritized Platform Improvements

## Pipeline Status Report

### GitHub Actions (All Failing - Billing Issue)
| Run ID | Workflow | Status | Reason |
|--------|----------|--------|--------|
| 19692984466 | Python 3.14 + Astral Tooling CI | ❌ FAILED | **Billing limit reached** |
| 19692984473 | AiYou CI Pipeline | ❌ FAILED | Billing limit reached |
| 19692982900 | Safety Evidence Collection | ❌ FAILED | Billing limit reached |
| 19692982874 | Cursor Code Review | ❌ FAILED | Billing limit reached |
| 19692506073 | Ingestion (hourly) | ❌ FAILED | Billing limit reached |

**Root Cause**: GitHub Actions billing needs payment/limit increase.
**Action Required**: Check GitHub Settings → Billing & plans

### Cloud Build (GCP)
- **Status**: Auth token expired - needs `gcloud auth login`

---

## Completed Work

### ✅ PR #290 - Pingora Media Edge (MERGED)
- Rust HLS proxy with TinyUfo cache
- Cloud CDN enabled via BackendConfig
- 16 files, 1749 lines added
- Full K8s deployment manifests

---

## Prioritized Subset - Implementation Plan

### Priority 1: Fix CI/CD Infrastructure
**Why**: All pipelines failing blocks everything else

1. **Fix GitHub Actions Billing**
   - User action: Update payment method or increase spending limit
   - Location: github.com/settings/billing

2. **Re-authenticate GCP**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

### Priority 2: FFmpeg Transcoding Service (CRITICAL)
**Why**: Required for CineVerse ($430M revenue target), needed before media-edge can serve content

**Architecture**:
```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│   Upload   │ → │  FFmpeg    │ → │   GCS      │ → │ media-edge │
│   API      │    │  Worker    │    │  (HLS)     │    │ (Pingora)  │
└────────────┘    └────────────┘    └────────────┘    └────────────┘
```

**Files to Create**:
```
transcode-service/
├── Cargo.toml              # Rust + ffmpeg-next bindings
├── Dockerfile              # FFmpeg 7.0 + Rust
├── src/
│   ├── main.rs             # Tokio runtime + job queue
│   ├── config.rs           # Env config
│   ├── encoder.rs          # H.264/H.265/AV1 presets
│   ├── hls.rs              # HLS packaging (segment + playlist)
│   ├── gcs.rs              # Upload to GCS
│   └── queue.rs            # Cloud Tasks / Pub/Sub consumer
└── k8s/
    ├── deployment.yaml     # GPU node pool (nvidia-l4)
    ├── job-template.yaml   # K8s Job for batch processing
    └── configmap.yaml
```

**Bitrate Ladder (FL1 - Server-Side)**:
| Quality | Resolution | Video Bitrate | Audio |
|---------|------------|---------------|-------|
| 4K      | 3840x2160  | 15 Mbps       | 192k  |
| 1080p   | 1920x1080  | 6 Mbps        | 128k  |
| 720p    | 1280x720   | 3 Mbps        | 128k  |
| 480p    | 854x480    | 1.5 Mbps      | 96k   |
| 360p    | 640x360    | 800 kbps      | 64k   |

### Priority 3: CineVerse Upload API Routes
**Why**: Revenue-critical, models exist but routes incomplete

**Files to Modify**:
- `src/aiyou/routes/cineverse.py` - Add upload endpoints
- `src/aiyou/services/cineverse/upload.py` - New file

**Endpoints**:
```python
POST /api/v1/cineverse/upload/initiate     # Get signed URL
POST /api/v1/cineverse/upload/complete     # Trigger transcode
GET  /api/v1/cineverse/upload/{id}/status  # Check progress
POST /api/v1/cineverse/content/{id}/publish # Make live
```

### Priority 4: Revenue Event Tracking
**Why**: All 4 services need this for monetization

**Files to Create**:
```
src/aiyou/services/revenue/
├── __init__.py
├── tracker.py          # Event emission
├── events.py           # Event types
└── bigquery_sink.py    # BQ writer
```

**Events**:
- `content.view` - Video playback started
- `content.complete` - Video watched to end
- `subscription.started` - New subscription
- `purchase.completed` - One-time purchase

---

## Implementation Sequence

### Phase A: Infrastructure (Immediate)
1. Fix GitHub Actions billing (user action)
2. Re-authenticate GCP CLI
3. Verify media-edge deployment on GKE

### Phase B: Transcode Pipeline
4. Create transcode-service Rust project
5. Implement FFmpeg bindings for H.264/H.265
6. Add HLS packaging (segmenter + m3u8 generator)
7. GCS upload integration
8. K8s deployment with GPU nodes
9. Cloud Build pipeline

### Phase C: CineVerse API
10. Upload initiation endpoint (signed URLs)
11. Transcode trigger endpoint
12. Status polling endpoint
13. Content publish endpoint

### Phase D: Revenue Tracking
14. Event schema definition
15. BigQuery sink implementation
16. Integration with CineVerse routes

---

## Files to Read Before Implementation

| File | Purpose |
|------|---------|
| `src/aiyou/models/cineverse.py` | Content model structure |
| `src/aiyou/services/cineverse/` | Existing service patterns |
| `IMPLEMENTATION_STATUS.md` | Phase 4 requirements |
| `media-edge/src/gcs.rs` | GCS integration pattern |

---

## Resource Requirements

| Service | CPU | Memory | GPU | Replicas |
|---------|-----|--------|-----|----------|
| media-edge | 1 | 1Gi | - | 3-20 |
| transcode-service | 4 | 8Gi | 1x L4 | 1-5 |
| cineverse-api | 500m | 512Mi | - | 3 |

---

## Success Criteria

- [x] FFmpeg transcoding produces valid HLS output (PR #291 merged)
- [x] Upload → Transcode → Serve pipeline implemented (PR #291)
- [x] Revenue events schema ready for BigQuery (PR #291)
- [ ] GitHub Actions pipelines passing (billing issue)
- [ ] media-edge serves transcoded content with cache HITs

---

## Priority 5: NEXUSUS AI Landing Page

### Overview
**NEXUSUS AI** is a futuristic FPS game landing page for GamePort integration.
- Theme: "The first FPS where the environment evolves based on your combat style"
- Neural network-themed shooter with adaptive AI environments
- Cyberpunk aesthetic: cyan (#00ffff), dark gradients, particle effects

### User-Provided Assets
The user provided complete HTML/CSS/JS code including:
- Hero section with animated particle background
- Grid overlay with glow effects
- Dynamic stats circles (NEURAL SYNC, PLAYERS, etc.)
- "INSTANT LINK" and "WATCH TRAILER" CTAs
- Responsive navigation
- Entrance animations

### Files to Create
```
landing-pages/
└── gameport/
    └── nexusus/
        ├── index.html         # Main landing page
        ├── css/
        │   └── nexusus.css    # Cyberpunk styles
        └── js/
            └── nexusus.js     # Particle system, animations
```

### FastAPI Static Serving
Add static file serving in `app/main.py`:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/games", StaticFiles(directory="landing-pages/gameport"), name="game-landings")
```

### Integration Points
- **GamePort Catalog**: Add NEXUSUS to game registry
- **Revenue Tracking**: Track ad impressions and game launches
- **ShadowTag**: Session verification for game launches

### Implementation Steps
1. Create directory structure: `landing-pages/gameport/nexusus/`
2. Add HTML file with hero, nav, and stats sections
3. Add CSS with particle animations and cyberpunk theme
4. Add JS for particle system and dynamic effects
5. Mount static files in FastAPI
6. Register in GamePort service catalog

---

## Priority 6: FedRAMP Compliance & Governance Trace UI

### Federal Requirements (OMB M-25-22, effective Sept 30, 2025)
- **Buy American AI**: No Chinese models (Kimi, DeepSeek), no open-source
- **High-Impact AI Classification**: Decisions affecting civil rights, privacy, health
- **Audit Trail Requirements**: Explainable AI with timestamped decision chains
- **Chief AI Officer Reporting**: Annual use case inventories

### Approved AI Stack (FedRAMP Authorized Only)
| Service | Provider | FedRAMP Level |
|---------|----------|---------------|
| Reasoning | Azure OpenAI (GPT-4o) | FedRAMP High |
| Execution | AWS Bedrock (Claude) | FedRAMP High |
| Search | Perplexity Enterprise | FedRAMP 20x |
| Productivity | Microsoft Copilot | FedRAMP High |
| Infrastructure | GCP (acquired-jet project) | FedRAMP Moderate |

### PNKLN Governance Trace UI
**Purpose**: Visual audit trail replay for AI decisions (compliance with High-Impact AI requirements)

**Files to Create**:
```
templates/governance/
├── trace.html          # Terminal-style decision replay
├── css/
│   └── trace.css       # CRT scanline effects, PNKLN branding
└── js/
    └── trace.js        # Typewriter animation, verdict reveal
```

**Features**:
- Signed URL access (GCS with expiring tokens)
- Step-by-step logic trace replay
- Color-coded verdict (APPROVED/REJECTED)
- Mock data fallback for preview mode
- Mobile responsive terminal UI

**Flask Integration**:
```python
@app.route("/governance/trace/<decision_id>")
async def governance_trace(decision_id: str):
    trace_url = generate_signed_url(f"traces/{decision_id}.json")
    return render_template("governance/trace.html",
                          decision_id=decision_id,
                          trace_url=trace_url)
```

### Implementation Steps
1. Create `templates/governance/trace.html` from user-provided code
2. Add GCS signed URL generation utility
3. Create Flask/FastAPI route for trace viewer
4. Integrate with Judge Six decision logging
5. Add to ShadowTag verification flow

---

## Phase 2: Infrastructure Evolution (2025 Research Stack)

### Priority 7: Pingora Hardening (FL2 Architecture)
**Why**: November 2025 Cloudflare outage exposed panic vulnerabilities

**Key Improvements from Research**:
- Ban `unwrap()` in production code (use `match` or `?` operator)
- Implement `catch_unwind` at task boundaries
- Add "lame duck" graceful shutdown (return 503 while draining)
- HTTP/3 (QUIC) support via `tokio-quiche`

**Files to Modify**:
```
media-edge/src/
├── main.rs       # Add catch_unwind wrapper
├── lib.rs        # Replace unwrap() with proper error handling
├── health.rs     # Add lame duck state for graceful shutdown
└── quic.rs       # New: HTTP/3 listener integration
```

**Code Pattern (Panic-Free)**:
```rust
// BEFORE (panic-prone)
let features = load_features(config_file).unwrap();

// AFTER (panic-free)
let features = match load_features(config_file) {
    Ok(f) => f,
    Err(e) => {
        log::error!("Failed to load features: {}", e);
        return Err(ServiceError::ConfigLoad(e));
    }
};
```

### Priority 8: Contract Ingestion (Gemini + PostgreSQL)
**Why**: Legal document analysis for compliance automation

**Architecture**:
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Upload    │ → │   Gemini    │ → │ PostgreSQL  │
│   (GCS)     │    │   1.5 Pro   │    │   (Schema)  │
└─────────────┘    └─────────────┘    └─────────────┘
```

**PostgreSQL Schema**:
```sql
CREATE TABLE contracts (
    id UUID PRIMARY KEY,
    gcs_uri TEXT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    contract_type VARCHAR(50),
    effective_date DATE,
    counterparties TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY,
    contract_id UUID REFERENCES contracts(id) ON DELETE CASCADE,
    risk_score INT CHECK (risk_score >= 0 AND risk_score <= 100),
    flagged_clauses JSONB NOT NULL DEFAULT '[]'::JSONB,
    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Files to Create**:
```
src/aiyou/services/contracts/
├── __init__.py
├── ingest.py           # Gemini analysis (async)
├── schema.py           # Pydantic models
├── repository.py       # SQLAlchemy/asyncpg
└── routes.py           # FastAPI endpoints
```

### Priority 9: Deep Learning Containers (GKE + Vertex AI)
**Why**: Standardized ML environment for Judge Six, video analysis

**Container Strategy**:
- Use Google DLC Base Images (M128+, no Conda)
- Derivative containers for custom dependencies
- TPU-optimized images for training

**Key Images**:
| Use Case | Image | Framework |
|----------|-------|-----------|
| Inference | `pytorch-cu124` | PyTorch 2.4 |
| Training | `tf2-cu123` | TensorFlow 2.17 |
| Hugging Face | `tgi-gpu` | Text Generation Inference |

**Files to Create**:
```
ml-containers/
├── Dockerfile.inference    # Custom inference container
├── Dockerfile.training     # TPU/GPU training
├── requirements.txt        # Python deps
└── k8s/
    ├── inference-deployment.yaml
    └── training-job.yaml
```

### Priority 10: ShadowTagAi Sovereign Kernel
**Why**: Revenue gates + truth ledger = profitable AI

**Components**:
1. **Payment Gateway** (402 gates)
2. **NFT Minter** (Polygon ERC-721)
3. **Truth Ledger** (IPFS + blockchain)
4. **Bar Exam Protocol** (Code evolution latch)

**Revenue Doctrine**:
```python
@router.post("/analyze/video")
async def analyze_video(request: AnalyzeRequest, user: User = Depends(get_current_user)):
    # THE GATE: No free compute
    if user.balance < PRICE_PER_ANALYSIS:
        raise HTTPException(status_code=402, detail="Insufficient Credits")

    # THE BRAIN: Gemini analysis
    result = await gemini_analyze(request.video_uri)

    # THE PROOF: Mint verification
    tx_hash = await mint_verification_nft(result.hash, user.wallet)

    # Deduct credits
    await deduct_credits(user.id, PRICE_PER_ANALYSIS)

    return {"result": result, "verification_tx": tx_hash}
```

**Files to Create**:
```
src/shadowtag/
├── __init__.py
├── payment_gateway.py      # 402 revenue gates
├── nft_minter.py           # Polygon ERC-721
├── bar_exam_protocol.py    # Code evolution latch
├── gemini_core.py          # Multimodal analysis
└── contracts/
    └── ShadowTagNFT.sol    # Solidity contract
```

---

## Immediate Actions

### Step 0: Merge PR #292
```bash
gh pr merge 292 --merge
git checkout main && git pull
```

### Step 1: Clean Stale Branches
```bash
# Delete merged remote branches
git fetch --prune
for branch in $(git branch -r --merged origin/main | grep -v main); do
    git push origin --delete ${branch#origin/}
done
```

---

## Updated Success Criteria

- [x] PR #290 - Pingora Media Edge (MERGED)
- [x] PR #291 - Transcode + CineVerse + Revenue (MERGED)
- [ ] PR #292 - NEXUSUS + Governance (OPEN → Merge)
- [ ] Priority 7 - Pingora panic-free hardening
- [ ] Priority 8 - Contract ingestion pipeline
- [ ] Priority 9 - DL Container infrastructure
- [ ] Priority 10 - ShadowTagAi Kernel
