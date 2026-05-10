# Shadowtag V2: Enterprise Watermark Tracking System

## Product Overview

Shadowtag V2 is the flagship product of Kosmos Dev—an enterprise-grade watermark tracking system for detecting and cataloging digital watermarks across images, videos, documents, and cloud storage.

**Priority**: 1 (Flagship)
**Status**: active_development
**Type**: enterprise_saas

---

## Problem Statement

Organizations need to:

- Track provenance of digital assets

- Detect unauthorized use of watermarked content

- Verify authenticity of documents and media

- Comply with content licensing requirements

- Identify AI-generated content (SynthID, C2PA)

---

## Core Capabilities

### 1. Watermark Detection

**Visual Watermarks**

- LSB (Least Significant Bit) steganography

- DCT (Discrete Cosine Transform) embedding

- DWT (Discrete Wavelet Transform) patterns

- Perceptual hashing and fingerprinting

- Invisible watermark extraction

**Text Watermarks**

- Unicode steganography (zero-width characters)

- Whitespace encoding patterns

- Linguistic fingerprinting and stylometry

- Hidden text patterns in documents

**Metadata Markers**

- EXIF/IPTC/XMP image metadata

- C2PA/CAI content authenticity manifests

- SynthID AI-generated content markers

- PDF/DOCX structural analysis

- Video container metadata

### 2. Scanning Sources

**Google Drive**

- OAuth2 authentication

- Recursive folder scanning

- Support for native Google formats

- Real-time monitoring option

**Local Memory/Storage**

- File system walking with filters

- Hash-based duplicate detection

- Scheduled automated scans

- Large file handling (streaming)

**Future Sources**

- Amazon S3

- Azure Blob Storage

- Dropbox

- OneDrive

### 3. Analysis Pipeline

Per Kosmos paper architecture:

```

SCAN → DETECT → ANALYZE → VOTE → CONSENSUS → REPORT

```


- **Data Analysis agents** execute detection code

- **Literature Search agents** find relevant patterns/standards

- All findings posted to structured world model

- Multi-agent consensus on findings (≥70% agreement)

- Full traceability with citations

### 4. Reporting

**Executive Summary**

- High-level findings count

- Risk assessment

- Recommended actions

**Technical Report**

- Detailed detection methodology

- Evidence with byte offsets/coordinates

- Confidence scores with justification

- False positive indicators

**Compliance Report**

- Audit trail

- Chain of custody

- Regulatory implications

---

## Technical Architecture

### Within Kosmos Dev

```

kosmos_dev/
├── products/
│   └── shadowtag_v2/
│       ├── SPEC.md              # This document
│       ├── __init__.py
│       ├── detectors/
│       │   ├── __init__.py
│       │   ├── visual.py        # Image/video watermarks
│       │   ├── text.py          # Document steganography
│       │   └── metadata.py      # EXIF, C2PA, SynthID
│       ├── scanners/
│       │   ├── __init__.py
│       │   ├── drive.py         # Google Drive connector
│       │   └── filesystem.py    # Local file scanner
│       └── reporters/
│           ├── __init__.py
│           └── generator.py     # Report generation

```

### Data Flow

```

[Source]     [Detectors]           [World Model]        [Output]
   │              │                      │                 │
   ├─ Drive ─────►├─ VisualDetector ────►│                 │
   │              │                      │                 │
   ├─ Memory ────►├─ TextDetector ──────►├─► Consensus ───►├─► Reports
   │              │                      │                 │
   └─ (S3) ─────►└─ MetadataDetector ──►│                 └─► Alerts

```

---

## Agent Assignments

Per Kosmos paper, agents specialize based on type:

### Data Analysis Agents

| Persona | Shadowtag Focus |
|---------|-----------------|
| CTO | Detection algorithm design, performance optimization |
| CFO | Cost per scan calculation, infrastructure spend |
| COO | Scanning pipeline efficiency, bottleneck analysis |

### Literature Search Agents

| Persona | Shadowtag Focus |
|---------|-----------------|
| CEO | Market research on competitor solutions |
| Cofounder | Strategic positioning, feature prioritization |
| General Counsel | C2PA standards, copyright law, DMCA compliance |

### Synthesis Agent

Aggregates all findings into final consensus report with 79.4% target accuracy.

---

## API Design

### Scan Endpoint

```python
POST /api/v1/shadowtag/scan
{
    "sources": [
        {"type": "drive", "folder_id": "root"},
        {"type": "memory", "path": "/data/assets"}
    ],
    "detectors": ["visual", "text", "metadata"],
    "options": {
        "recursive": true,
        "max_files": 1000,
        "file_types": ["image/*", "video/*", "application/pdf"]
    }
}

Response:
{
    "scan_id": "scan_abc123",
    "status": "in_progress",
    "estimated_duration_minutes": 15
}

```

### Results Endpoint

```python
GET /api/v1/shadowtag/scan/{scan_id}/results

Response:
{
    "scan_id": "scan_abc123",
    "status": "complete",
    "summary": {
        "files_scanned": 847,
        "findings": 23,
        "consensus_reached": 19,
        "contested": 4
    },
    "findings": [
        {
            "id": "finding_xyz",
            "type": "visual_watermark",
            "source": "drive://1abc.../image.jpg",
            "confidence": 0.87,
            "consensus": "agreed",
            "evidence": {
                "method": "LSB",
                "location": "bottom-right quadrant",
                "pattern": "company_logo_v2"
            }
        }
    ]
}

```

### Report Endpoint

```python
GET /api/v1/shadowtag/scan/{scan_id}/report?format=pdf

Response: PDF binary

```

---

## Quality Metrics

### Detection Accuracy


- Target: 79.4% (Kosmos benchmark)

- False positive rate: <5%

- False negative rate: <10%

### Performance


- Throughput: 100 files/minute

- Latency: <1s per small file, <10s per video

- Scalability: 10,000 files per scan

### Cost


- Per file: ~$0.001 (Flash) to $0.01 (Pro)

- Per scan (1000 files): $1-10

- Monthly budget cap: configurable

---

## Security Considerations

### Data Handling


- Files processed in memory, not stored

- Results encrypted at rest

- OAuth tokens stored securely

- Audit log of all scans

### Compliance


- GDPR: No PII retention without consent

- SOC2: Full audit trails

- DMCA: Watermark detection for rights management

### Access Control


- Role-based permissions

- API key authentication

- Rate limiting per account

---

## Development Phases

### Phase 1: Core Detectors


- [ ] Visual watermark detector (LSB, DCT)

- [ ] Text steganography detector

- [ ] Metadata extractor (EXIF, XMP)

### Phase 2: Scanners


- [ ] Google Drive connector with OAuth2

- [ ] Local file system scanner

- [ ] Async scanning pipeline

### Phase 3: Integration


- [ ] World model integration

- [ ] Multi-agent consensus flow

- [ ] Report generation

### Phase 4: API & UI


- [ ] FastAPI endpoints

- [ ] Webhook notifications

- [ ] Dashboard (optional)

### Phase 5: Production


- [ ] GKE deployment

- [ ] Monitoring & alerting

- [ ] Documentation

---

## Success Criteria

### MVP (Phase 1-3)


- Detect 3+ watermark types

- Scan Google Drive and local files

- Generate basic report

- 70%+ accuracy

### V1.0 (Phase 4-5)


- Full API with authentication

- 79.4% accuracy (Kosmos target)

- <5% false positive rate

- Production deployment on GKE

### Future


- Real-time monitoring

- Additional cloud storage providers

- Custom watermark training

- Enterprise SSO

---

## References


- [C2PA Specification](https://c2pa.org/specifications/)

- [SynthID by Google DeepMind](https://deepmind.google/technologies/synthid/)

- [Kosmos Paper](https://arxiv.org/abs/2511.02824)

- Cofounder Profiles: `erik-hancock-llm-memory/drive_knowledge/documents/`
