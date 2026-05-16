# ShadowTag Specification — Cryptographic Provenance Layer

**Version:** 1.0
**Purpose:** Immutable attestation for AI outputs, media, transactions, and sensor data

---

## 🧩 Architecture Overview

ShadowTag provides **L0→L4 attestation** for every data artifact:

```

L0: Raw Capture       → content hash (BLAKE3/SHA-256)
L1: Integrity         → cryptographic signature (COSE_Sign1)
L2: Timeline          → append-only Merkle tree + public anchoring
L3: License/Policy    → W3C Verifiable Credential (usage rights)
L4: Relational        → spatiotemporal attestation (GPS/stars/airspace + relates_to)

```

**Goal:** Prove *what*, *when*, *where*, *who*, and *under what terms* any data was created.

---

## Layer 0: Raw Capture

### Process


1. Device/agent produces payload (JSON, binary, video frame, etc.)

2. Compute content hash immediately:

   - **BLAKE3** (preferred: fast, 256-bit)

   - **SHA-256** (fallback for legacy systems)

3. Assign identifiers:

   - **CID** (Content ID): `b3:8af4e2...` (hash)

   - **EID** (Event ID): `evt_9c7a...` (UUID v7 for time-sortable)

### Example

```json
{
  "eid": "evt_9c7a3b2e",
  "cid": "b3:8af4e2d1c0b9a8f7e6d5c4b3a2f1e0d9",
  "payload_size": 1048576,
  "timestamp_utc": "2025-11-17T23:14:58.231Z"
}

```

---

## Layer 1: Integrity (Cryptographic Signature)

### Process


1. Create compact **sidecar manifest** per chunk:

2. Sign with device key stored in **TPM/HSM** (YubiHSM, AWS CloudHSM, Apple Secure Enclave)

3. Use **COSE (CBOR Object Signing and Encryption)** for binary efficiency

### Manifest Schema

```json
{
  "ver": 1,
  "eid": "evt_9c7a3b2e",
  "cid": "b3:8af4e2...",
  "ts": "2025-11-17T23:14:58.231Z",
  "algo": "blake3",
  "len": 1048576,
  "prev": "b3:7be3d1...",        // hash chain link (previous event)
  "device_id": "dev_a1b2c3",
  "sig": "cose:base64..."        // COSE_Sign1 signature
}

```

### Signature Computation

```python

# Pseudocode

payload = cbor_encode({
    "cid": cid,
    "ts": timestamp,
    "device_id": device_id,
    "prev": prev_cid
})
sig = cose_sign1(payload, device_private_key)

```

### Output


- **In-band:** HTTP header `X-ShadowTag: <base64(cbor_manifest)>`

- **Out-of-band:** Sidecar file `data.json.st.manifest`

**Size:** ~150–400 bytes per event

---

## Layer 2: Timeline (Append-Only Merkle Tree)

### Process


1. Append `(eid, cid, ts, prev, sig)` to **Merkle tree**

2. Compute tree root hash periodically (every 100 events or 60 seconds)

3. Anchor root to **public notary**:

   - **OpenTimestamps** (Bitcoin blockchain)

   - **Sigstore Rekor** (transparency log)

   - **Ethereum L2** (Polygon, Optimism)

### Tree Structure

```

                 ROOT (hash)
                /            \
        H(evt_1, evt_2)    H(evt_3, evt_4)
         /      \            /      \
    evt_1    evt_2      evt_3    evt_4

```

### Anchoring


- **Frequency:** Every 1,000 events or 5 minutes (whichever first)

- **Proof:** Merkle path + timestamp proof from notary

### Benefits


- **Tamper-evident:** Changing any event invalidates root hash

- **Timestamping:** Anchoring proves "existed before time T"

- **Non-repudiation:** Public notary prevents backdating

---

## Layer 3: License/Policy (Verifiable Credentials)

### Process


1. Attach **W3C Verifiable Credential** describing usage rights:

   - Purpose (research, commercial, defense)

   - Retention period

   - Buyer class restrictions

   - Geographic jurisdiction

   - Allowed processors

### Example VC

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "type": ["VerifiableCredential", "DataLicenseCredential"],
  "issuer": "did:web:aiyou.global",
  "issuanceDate": "2025-11-17T23:14:58Z",
  "credentialSubject": {
    "id": "evt_9c7a3b2e",
    "license": {
      "purpose": ["commercial", "analytics"],
      "retention_days": 90,
      "buyer_class": ["enterprise", "government"],
      "jurisdiction": ["US", "EU"],
      "processors": ["approved_list_v3"]
    }
  },
  "proof": {
    "type": "Ed25519Signature2020",
    "created": "2025-11-17T23:15:00Z",
    "proofPurpose": "assertionMethod",
    "verificationMethod": "did:web:aiyou.global#key-1",
    "proofValue": "z58DAdFfa9..."
  }
}

```

### Storage


- Store VC hash in Merkle tree (L2)

- Buyers can verify both integrity (L1) and license (L3) together

---

## Layer 4: Relational Attestation (Spatiotemporal Context)

### Purpose

Bind each event to **where/when** it happened and **what else** it agrees with.

### Data Sources (Legal)


1. **GNSS/GPS:** Raw NMEA + receiver bias + HDOP

2. **Celestial lock:** Star-field matching (astrometry.net) for spoofing cross-check

3. **Airspace context:** FIR/sector ID + ADSB proximity (hashed, non-PII)

4. **Clock trust:** Roughtime/NTP signatures

### Relational Record

```json
{
  "eid": "evt_9c7a3b2e",
  "spacetime": {
    "lat": 37.615,
    "lon": -122.389,
    "alt_m": 12,
    "pnt_conf": 0.93,           // PNT confidence score (0–1)
    "hdop": 0.7,
    "celestial": {              // Optional: star-lock cross-check
      "ra": 15.23,
      "dec": -7.11,
      "conf": 0.88
    },
    "airspace": {               // Optional: aviation context
      "fir": "KZNY",
      "sector": "ZNY42",
      "echo_hash": "b3:..."     // Hashed ADSB proximity summary
    },
    "clock": {
      "ntp": "ok",
      "roughtime_sig": "base64..."
    }
  },
  "relates_to": [
    {"eid": "evt_9b...", "type": "same_device_prev"},
    {"eid": "evt_a1...", "type": "coincident_same_location_±2s"}
  ],
  "sig": "cose:..."             // Signed by regional gateway or device
}

```

### Benefits


- **Spoof resistance:** GNSS + star-lock disagreement → lower confidence, alert

- **Jurisdiction proofs:** "Data collected in UK airspace at time T"

- **Relational audits:** "These 3 streams occurred same place/time" → stronger authenticity

- **Premium SKUs:** "Attested+Relational" feeds priced 2–5× higher

---

## 🛠️ Implementation Architecture

### Edge Agent (Device-Side)

**Language:** Rust or Go
**Functions:**

1. Hash chunk → compute CID

2. Build L1 manifest

3. Query location sensor (GNSS), clock, optional star solver

4. Emit L4 record

5. Push to Kafka/NATS + ShadowTag ledger API

**Latency:** ~0.5–2ms per event (hashing + signing)

### Ledger Service (Cloud-Side)

**Language:** Node.js (TypeScript) or Rust
**Functions:**

1. Maintain per-tenant Merkle forests (one per stream)

2. `/verify` API: given (payload + sidecar + L4) → return attestation report

3. Nightly anchoring job → OpenTimestamps / Rekor

**API Example:**

```http
POST /verify
Content-Type: application/json

{
  "payload": "base64...",
  "sidecar": { /* L1 manifest */ },
  "l4": { /* L4 record */ },
  "policy_vc": { /* W3C VC */ }
}

Response:
{
  "integrity": "valid",
  "anchored": true,
  "anchor_tx": "0x1234...",
  "license_ok": true,
  "pnt_conf": 0.93,
  "celestial_conf": 0.88,
  "airspace_match": true,
  "verification_ts": "2025-11-17T23:20:00Z"
}

```

### Verifier SDK

**Languages:** TypeScript, Python, Rust

```typescript
import { verify } from '@aiyou/shadowtag';

const result = await verify({
  payload,
  sidecar,
  l4,
  policyVC,
  required: {
    minPntConf: 0.8,
    clock: 'synced',
    anchored: true
  }
});

if (result.valid) {
  console.log('Attestation verified!');
}

```

---

## 🔒 Security Considerations

### Key Management


- **Device keys:** Stored in TPM/HSM (YubiHSM, AWS CloudHSM, Apple Secure Enclave)

- **Rotation:** Rolling keys per day/week for HMAC/signing

- **Revocation:** Publish CRL (Certificate Revocation List); log signer key IDs in every record

### Privacy


- **No PII:** Location is of sensor, not persons

- **Aggregation:** Airline proximity → hashed summaries (non-identifiable)

- **Consent:** Only collect/attest data with explicit permission

### Chain of Custody


- Every transform (resample, compress) creates new CID with `derived_from` link

- Audit trail: full provenance graph from capture → processing → delivery

---

## 📊 Performance Benchmarks

| Operation | Latency | Throughput |
|-----------|---------|------------|
| BLAKE3 hash (1MB) | 0.8ms | 1.2 GB/s |
| COSE_Sign1 (Ed25519) | 0.2ms | 5K sigs/sec |
| Merkle append | 0.1ms | 10K events/sec |
| L4 enrichment (GNSS + clock) | 0.5ms | — |
| **End-to-end overhead** | **1.5–3ms** | **300–600 events/sec (single core)** |

**Scaling:** Horizontal sharding by tenant ID (100K+ events/sec cluster-wide)

---

## 💰 Monetization

### Pricing Tiers


- **Base feed (L1–L2):** $0.50–$2 per 1K events

- **Licensed feed (L3):** +$0.50 per 1K events

- **Relational feed (L4):** +$1–$3 per 1K events (2–5× multiplier for enterprise)

### Enterprise Contracts


- **Audit hosting:** $5K–$50K/year + $0.05–$0.50 per event record

- **Custom SLAs:** +25–60% uplift for attested+relational feeds

- **Compliance bundles:** SOC2 + ISO 27001 + RMF evidence packages ($100K–$250K/audit)

---

## 🧪 Testing & Validation

### Unit Tests


- Hash collision resistance

- Signature verification (valid/invalid keys)

- Merkle proof generation + verification

### Integration Tests


- End-to-end: capture → sign → anchor → verify

- Multi-tenant isolation

- Anchoring retry logic (OpenTimestamps timeout)

### Chaos Tests


- Signature tampering detection

- Clock skew handling

- Partial Merkle tree recovery

---

## 📚 References


- **COSE (RFC 8152):** https://datatracker.ietf.org/doc/html/rfc8152

- **W3C Verifiable Credentials:** https://www.w3.org/TR/vc-data-model/

- **OpenTimestamps:** https://opentimestamps.org/

- **Sigstore Rekor:** https://docs.sigstore.dev/rekor/overview/

- **BLAKE3:** https://github.com/BLAKE3-team/BLAKE3

---

**Next:** [Edge Orchestrator API](./edge-orchestrator-api.yaml) | [PNT Architecture](./pnt-architecture.md)
