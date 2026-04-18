# ShadowTag Verification Layer

## Purpose

ShadowTag is AiYou's cryptographic provenance system that provides **tamper-proof attestation** of:

- **What** computation occurred (model, inputs, outputs)

- **When** it occurred (timestamp + proof)

- **Where** it occurred (geographic location + network node)

- **Who** requested it (authenticated identity, optional)

- **How** to verify it (signatures + public audit trail)

---

## Why This Matters

### Regulatory Drivers

| Regulation | Requirement | ShadowTag Solution |
|------------|-------------|-------------------|
| **EU AI Act (2024)** | High-risk AI must have audit trails | Immutable ledger of all inferences |
| **US NIST AI RMF (2025)** | AI systems must be traceable | Complete provenance chain |
| **SOC 2 Type II** | Demonstrate security controls | Continuous evidence collection |
| **ISO 27001** | Data integrity + non-repudiation | Cryptographic signatures |
| **GDPR** | Data processing records | Timestamped consent + processing logs |
| **HIPAA** | Protected health information audit | Encrypted + signed PHI access logs |
| **DoD RMF Level 5-6** | Classified system verification | Hardware-rooted attestation |

### Business Value

**For enterprises:**

- Prove compliance to auditors

- Dispute resolution (e.g., "our AI didn't generate that")

- Insurance discounts (verified safety controls)

- Premium pricing (verified = trustworthy)

**For AiYou:**

- Differentiation (only verified AI fabric)

- High-margin revenue stream (verification-as-a-service)

- Regulatory moat (competitors can't match without rebuilding)

---

## Architecture Layers

### L0: Capture (Raw Data)

Every event generates a unique **Event ID (EID)** and **Content ID (CID)**.

```python
import hashlib
import uuid
from datetime import datetime

def create_event(payload: bytes) -> dict:
    """Capture raw event and compute content hash."""
    eid = f"evt_{uuid.uuid4().hex[:12]}"
    cid = f"blake3:{hashlib.blake3(payload).hexdigest()}"

    return {
        "eid": eid,
        "cid": cid,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "payload_len": len(payload),
        "algo": "blake3"
    }

```

**Output example:**

```json
{
  "eid": "evt_9c4a7f3b2e1d",
  "cid": "blake3:8af43c7b9d2e1a5f...",
  "timestamp_utc": "2025-11-15T14:23:45.678901Z",
  "payload_len": 1048576,
  "algo": "blake3"
}

```

---

### L1: Integrity (Cryptographic Signing)

Create a compact **sidecar manifest** that gets signed with TPM/HSM-backed keys.

```python
import cose
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

def sign_manifest(event: dict, device_key: ec.EllipticCurvePrivateKey, prev_hash: str) -> dict:
    """Create COSE-signed manifest for event."""
    manifest = {
        "eid": event["eid"],
        "cid": event["cid"],
        "ts": event["timestamp_utc"],
        "len": event["payload_len"],
        "prev": prev_hash,  # Hash chain link to previous event
    }

    # COSE Sign1 (RFC 8152)
    msg = cose.Sign1Message(
        phdr={"alg": "ES256"},  # ECDSA P-256
        payload=json.dumps(manifest).encode()
    )
    msg.key = device_key
    signature = msg.encode()

    manifest["sig"] = f"cose:{signature.hex()}"
    return manifest

```

**Manifest schema:**

```json
{
  "eid": "evt_9c4a7f3b2e1d",
  "cid": "blake3:8af43c...",
  "ts": "2025-11-15T14:23:45.678901234Z",
  "len": 1048576,
  "prev": "blake3:7d2f9a...",
  "sig": "cose:a10126a104524...",
  "key_id": "aiyou-sea-01-prod-2025-Q4"
}

```

**Size:** ~150-400 bytes (CBOR-encoded)

**Delivery:**

- **In-band:** HTTP header `X-ShadowTag: <base64(cbor)>`

- **Out-of-band:** Sidecar file `payload.st.manifest`

- **Message bus:** Kafka/NATS message headers

---

### L2: Timeline (Hash Chain + Merkle Tree)

All events append to an **append-only log** forming a hash chain. Periodically, the tree head gets anchored to a public notary.

```python
class ShadowTagLedger:
    """Append-only Merkle tree for event sequencing."""

    def __init__(self):
        self.events = []  # List of (eid, cid, ts, prev, sig)
        self.tree = []    # Merkle tree nodes

    def append(self, manifest: dict):
        """Add event to ledger and update Merkle tree."""
        # Verify signature first
        if not self._verify_signature(manifest):
            raise ValueError(f"Invalid signature for {manifest['eid']}")

        # Verify hash chain
        if self.events:
            last_cid = self.events[-1]["cid"]
            if manifest["prev"] != last_cid:
                raise ValueError(f"Hash chain broken at {manifest['eid']}")

        # Append to ledger
        self.events.append(manifest)

        # Update Merkle tree
        self._update_merkle_tree(manifest)

    def _update_merkle_tree(self, manifest: dict):
        """Compute Merkle root including new manifest."""
        # Simplified; real implementation uses efficient Merkle tree library
        leaf = hashlib.sha256(json.dumps(manifest).encode()).digest()
        self.tree.append(leaf)
        # ... compute intermediate nodes and root ...

    def get_proof(self, eid: str) -> dict:
        """Get Merkle proof for a specific event."""
        # Returns: event + Merkle path + root + anchored timestamp
        pass

```

**Anchoring to public notary:**

- **Service:** OpenTimestamps, Sigstore Rekor, or Ethereum L2

- **Frequency:** Every 10 minutes (batch of ~60K events)

- **Cost:** ~$0.01 per anchor (amortized over batch)

**Proof:**

```json
{
  "eid": "evt_9c4a7f3b2e1d",
  "merkle_root": "sha256:3f8d2a...",
  "merkle_path": ["sha256:4a7b...", "sha256:9e3c..."],
  "anchor": {
    "service": "opentimestamps",
    "timestamp_utc": "2025-11-15T14:30:00Z",
    "tx_hash": "0x7f3b2a..."
  }
}

```

---

### L3: Policy (Consent + Licensing)

Attach a **W3C Verifiable Credential** describing usage rights and consent.

```json
{
  "type": "ShadowTagLicense",
  "version": "1.0",
  "issued_at": "2025-11-15T14:00:00Z",
  "expires_at": "2026-11-15T14:00:00Z",
  "subject": "evt_9c4a7f3b2e1d",
  "usage_rights": {
    "purpose": ["ai_inference", "compliance_audit"],
    "retention_days": 730,
    "allowed_jurisdictions": ["US", "EU"],
    "prohibited_uses": ["surveillance", "profiling"],
    "data_processor": "aiyou-sea-01"
  },
  "consent": {
    "user_id_hash": "sha256:a7f3b2...",  # Hashed, not PII
    "consent_timestamp": "2025-11-15T13:58:00Z",
    "consent_method": "explicit_click"
  },
  "signature": {
    "issuer": "did:aiyou:license-authority",
    "proof": "jws:eyJhbGciOiJFUzI1NiI..."
  }
}

```

**Verification:**

- Buyer checks: Is this data licensed for my use case?

- Regulator checks: Was user consent obtained?

- Auditor checks: Is retention policy compliant?

**Hash embedded in L1 manifest:**

```json
{
  "eid": "evt_9c4a7f3b2e1d",
  "license_hash": "blake3:f2e9a7...",  # Hash of VC
  ...
}

```

Actual VC stored separately (not in payload), but hash proves it existed at time of event.

---

### L4: Relational Attestation (Spatiotemporal Proofing)

Bind each event to **where/when it happened** and to **other events** that corroborate it.

#### Data Sources (Legal)


1. **GNSS/GPS:**

   - Raw NMEA sentences

   - Receiver clock bias + HDOP (precision metric)

   - PNT confidence score (0-1)


2. **Celestial Lock (optional):**

   - Star-field match (astrometry.net)

   - RA/Dec solution + confidence

   - Cross-check for GNSS spoofing (night/clear sky)


3. **Airspace Context (if applicable):**

   - FIR/sector ID (from public ADSB feeds)

   - Hashed summaries of nearby transponders (aggregate, non-PII)


4. **Network Timing:**

   - NTP/Roughtime signatures

   - Monotonic clock offset

#### L4 Record Schema

```json
{
  "eid": "evt_9c4a7f3b2e1d",
  "spacetime": {
    "lat": 47.6062,
    "lon": -122.3321,
    "alt_m": 12,
    "pnt_conf": 0.93,  # GPS confidence
    "hdop": 0.7,
    "celestial": {
      "ra": 15.23,
      "dec": -7.11,
      "conf": 0.88
    },
    "airspace": {
      "fir": "KZNY",
      "sector": "ZNY42",
      "proximity_hash": "blake3:7a3f..."  # Hashed ADSB summary
    },
    "clock": {
      "ntp_status": "ok",
      "roughtime_sig": "..."
    }
  },
  "relates_to": [
    {
      "eid": "evt_9b3c2a...",
      "type": "same_device_prev"  # Sequential event from same device
    },
    {
      "eid": "evt_a1f7b2...",
      "type": "coincident_location_time",  # Different device, same place/time
      "delta_ms": 143,
      "distance_m": 8.2
    }
  ],
  "sig": "cose:..."  # Signed by regional gateway or device
}

```

**Verification logic:**

```python
def verify_spatiotemporal(event: dict) -> dict:
    """Cross-check GNSS, celestial, and network timing."""
    result = {
        "integrity": "pass",
        "confidence": 0.0,
        "warnings": []
    }

    # Check 1: GNSS confidence
    pnt_conf = event["spacetime"]["pnt_conf"]
    if pnt_conf < 0.8:
        result["warnings"].append("Low GNSS confidence")

    # Check 2: Celestial cross-check (if available)
    if "celestial" in event["spacetime"]:
        cel_conf = event["spacetime"]["celestial"]["conf"]
        if abs(pnt_conf - cel_conf) > 0.15:
            result["warnings"].append("GNSS/celestial mismatch - possible spoofing")
            result["confidence"] = min(pnt_conf, cel_conf)
        else:
            result["confidence"] = (pnt_conf + cel_conf) / 2
    else:
        result["confidence"] = pnt_conf

    # Check 3: Coincident events
    for rel in event.get("relates_to", []):
        if rel["type"] == "coincident_location_time":
            result["confidence"] *= 1.2  # Corroboration boost

    result["confidence"] = min(result["confidence"], 1.0)

    if result["confidence"] < 0.5:
        result["integrity"] = "fail"

    return result

```

---

## Deployment Architecture

### Edge Agent (Go/Rust)

Runs on:

- AiYou edge GPU pods

- Customer devices (opt-in SDK)

- IoT sensors / vehicles

**Functions:**

1. Hash chunks of data

2. Build L1 manifest

3. Query location sensors (GNSS, optional sky solver)

4. Emit L4 record

5. Push to Kafka/NATS and ShadowTag ledger API

**Latency budget:**

- Hashing: 0.2-0.8ms per MB (on modern CPU)

- COSE signing: <1ms (with TPM)

- L4 lookups: <1ms (cached)

- **End-to-end overhead:** <5ms per event

### Ledger Service (Node.js / Rust)

Central service maintains:

- Per-tenant Merkle forests (one per stream)

- Append-only event log (PostgreSQL or ClickHouse)

- Public API: `/verify` and `/anchor`

**API endpoints:**

**POST /events**

```bash
curl -X POST https://shadowtag.aiyou.io/api/v1/events \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "eid": "evt_9c4a7f3b2e1d",
    "cid": "blake3:8af43c...",
    "manifest": { ... },
    "l4_attestation": { ... }
  }'

```

**Response:**

```json
{
  "status": "accepted",
  "merkle_root": "sha256:3f8d2a...",
  "next_anchor_time": "2025-11-15T14:40:00Z"
}

```

**GET /verify**

```bash
curl "https://shadowtag.aiyou.io/api/v1/verify?eid=evt_9c4a7f3b2e1d"

```

**Response:**

```json
{
  "eid": "evt_9c4a7f3b2e1d",
  "integrity": "valid",
  "signatures": {
    "manifest": "valid",
    "l4_attestation": "valid"
  },
  "anchored": true,
  "anchor_timestamp": "2025-11-15T14:30:00Z",
  "confidence": {
    "pnt": 0.93,
    "celestial": 0.88,
    "overall": 0.91
  },
  "license": {
    "purpose": ["ai_inference"],
    "retention_ok": true,
    "jurisdiction_ok": true
  },
  "merkle_proof": { ... }
}

```

### Verifier SDK (TypeScript / Python)

Client-side verification without trusting AiYou servers.

```typescript
import { verify } from '@aiyou/shadowtag-sdk';

const result = await verify({
  payload: responseData,
  sidecar: responseSidecar,
  l4Attestation: responseL4,
  policyVC: responsePolicy,
  required: {
    minPntConfidence: 0.8,
    clockSynced: true,
    anchored: true,
    allowedJurisdictions: ['US', 'EU']
  }
});

if (result.integrity === 'valid' && result.confidence >= 0.8) {
  // Trust this data
} else {
  // Reject or flag for review
}

```

---

## Security Model

### Threat Model

| Attack | Mitigation |
|--------|------------|
| **Forged signature** | TPM/HSM keys; public key infrastructure (PKI) |
| **Replay attack** | Timestamp + nonce + hash chain prevents reuse |
| **Backdated events** | Public anchoring (OpenTimestamps) proves event existed by time T |
| **Location spoofing** | Multi-source PNT (GNSS + celestial + network timing) |
| **Key compromise** | Key rotation every 90 days; CRL (certificate revocation list) |
| **Ledger tampering** | Append-only + public anchors = any change breaks Merkle proof |
| **Insider threat** | Multi-party computation for sensitive ops; audit all access |

### Key Management

**Hierarchy:**

```

Root CA (offline, HSM)
  ↓
Intermediate CA (online, HSM)
  ↓
Device/PoP Keys (TPM/HSM, rotated quarterly)

```

**Key rotation:**

- Every 90 days automatically

- Emergency rotation on compromise (within 4 hours)

- Old keys published to CRL

- Signer key ID included in every manifest

**Storage:**

- **Root CA:** Air-gapped HSM (FIPS 140-2 Level 4)

- **Intermediate CA:** YubiHSM2 or AWS CloudHSM (Level 3)

- **Device keys:** TPM 2.0 or Apple Secure Enclave

---

## Privacy Considerations

### What We Never Log


- User PII (names, emails, addresses)

- Full plaintext queries (only hashes)

- Precise user locations (only device/PoP location)

### What We Hash


- User IDs (SHA-256, salted)

- Query text (for cache matching only; not logged)

- Airspace proximity data (aggregate hashes)

### Data Minimization


- Store only: EID, CID, timestamp, PoP ID, model ID, inference time

- Full payloads stored only if customer explicitly opts in (e.g., compliance retention)

- Default retention: 90 days hot, 2 years cold (encrypted S3 Glacier)

### GDPR Compliance


- Right to erasure: We delete L4 attestations (but keep CID hashes for integrity proofs)

- Right to access: API endpoint to retrieve all events for a user_id_hash

- Data portability: Export as JSON/CBOR

---

## Pricing Model

### ShadowTag-as-a-Service

| Tier | Price | Includes |
|------|-------|----------|
| **Starter** | $500/month | 100K events/month, 90-day retention |
| **Pro** | $3K/month | 1M events/month, 2-year retention, API access |
| **Enterprise** | $10K-50K/month | Unlimited events, custom retention, SLA, dedicated support |
| **Audit Package** | $100K-250K one-time + $5K/month | Full compliance audit, runbooks, evidence hosting |

### Per-Event Pricing (for high-volume)


- **Basic attestation:** $0.00001 per event (just L0-L2)

- **Full attestation (L4):** $0.0001 per event (with spatiotemporal proofing)

- **Premium (anchored):** $0.0005 per event (public notary anchor)

### Enterprise Uplift


- **Verified feed:** 25-60% ARPU increase vs raw data

- **Insurance discount:** 10-20% reduction in cyber insurance premiums (verified controls)

---

## Deployment Checklist

**Phase 0 (MVP, Month 0-3):**

- [ ] Implement L0-L2 (hash + sign + Merkle tree)

- [ ] Deploy ledger service (PostgreSQL backend)

- [ ] Build SDK (TypeScript + Python)

- [ ] Integrate with 1 pilot customer (fintech or healthtech)

**Phase 1 (Production, Month 3-6):**

- [ ] Add L4 (spatiotemporal attestation)

- [ ] Public anchoring (OpenTimestamps integration)

- [ ] TPM/HSM key infrastructure

- [ ] API rate limiting + authentication

**Phase 2 (Scale, Month 6-12):**

- [ ] Multi-region ledgers (US, EU, APAC)

- [ ] Key rotation automation

- [ ] SOC 2 Type II certification

- [ ] Enterprise customer onboarding (5-10 customers)

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Signature verification rate** | >99.99% | Errors per 1M events |
| **Anchor latency** | <15 minutes | Time from event to public anchor |
| **False positive rate (spoofing detection)** | <10⁻⁶ per hour | Anomaly detector logs |
| **Customer compliance pass rate** | >95% | Audits passed using ShadowTag evidence |
| **ARPU uplift (verified vs raw)** | >30% | Revenue per customer comparison |

---

## References


- [Starlink-CoreWeave Integration](./starlink-coreweave-integration.md) (where ShadowTag runs)

- [PNT System](./pnt-system.md) (source of L4 location data)

- [Phase 0 Rollout](../04-phase-rollout/phase-0-foundation.md) (implementation plan)

- [COSE RFC 8152](https://datatracker.ietf.org/doc/html/rfc8152)

- [W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model/)

- [OpenTimestamps](https://opentimestamps.org/)
