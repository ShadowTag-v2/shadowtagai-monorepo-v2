# PNT System: Anti-Spoofing Position, Navigation, and Timing

## Executive Summary

AiYou's PNT (Position-Navigation-Timing) system is a **multi-source, cryptographically-authenticated** alternative to vulnerable GPS/GNSS. It provides reliable position and time even when satellite signals are jammed or spoofed.

**Target customers:** Aviation, maritime, automotive (FSD), defense, telco, logistics

**Core innovation:** Combining authenticated GNSS, LEO-assisted PNT (Starlink), terrestrial beacons (5G/cell), inertial fusion, secure hardware roots, ML anomaly detection, and immutable audit trail (ShadowTag).

---

## Problem: GPS is Trivially Spoofed

### Current Vulnerabilities

| Attack Vector | Cost to Attacker | Detection Time (Traditional) | Impact |
|---------------|------------------|------------------------------|--------|
| **Ground spoofer** | $500-2K (portable) | Minutes to never | Drones crash, ships misdirected |
| **Jammer** | $50-500 | Immediate (loss of signal) | Service denial, safety risk |
| **Fake ephemeris** | $10K+ (state actor) | Hours to days | Systematic position drift |
| **Receiver compromise** | Varies | Never (if supply chain) | Complete control |

**Real-world incidents:**

- 2017: >20 ships in Black Sea GPS-spoofed (appeared to be at airport)

- 2019: Moscow GPS jamming reported by rideshare drivers

- 2022: Ukraine conflict: widespread GNSS interference

- 2023: Newark Airport drone incident (possibly GPS-spoofed)

**Why it matters for AiYou:**

- **Aviation:** False position → collision risk, controlled flight into terrain

- **Maritime:** Vessels run aground, enter restricted zones unknowingly

- **Autonomous vehicles:** Tesla FSD, trucks → accidents, theft

- **Finance:** GPS time-stamping for HFT (High-Frequency Trading) → regulatory violations

- **Defense:** Tactical systems disabled by cheap commercial spoofers

---

## AiYou PNT Solution: Multi-Layer Defense

### Architecture Overview

```

┌─────────────────────────────────────────────────────────────┐
│                  AiYou PNT Stack                             │
├─────────────────────────────────────────────────────────────┤
│  L1: Authenticated GNSS      (signed messages)              │
│  L2: LEO-Assisted PNT        (Starlink timing/ranging)      │
│  L3: Terrestrial Beacons     (5G, cell towers, RSUs)        │
│  L4: Local Sensor Fusion     (IMU, odometry, map-matching)  │
│  L5: RF Anti-Spoofing        (multi-antenna, DoA)           │
│  L6: Cryptographic Attestation (TPM, signed PNT messages)   │
│  L7: ML Anomaly Detection    (real-time spoof detection)    │
│  L8: ShadowTag Ledger        (immutable proof-of-location)  │
├─────────────────────────────────────────────────────────────┤
│  Fallback: Graceful degradation if confidence drops         │
└─────────────────────────────────────────────────────────────┘

```

---

## Layer Details

### L1: Authenticated GNSS

**Problem:** Traditional GPS broadcasts are unsigned → easy to fake.

**Solution:** Use GNSS authentication where available.

**Implementations:**

- **Galileo OSNMA** (Open Service Navigation Message Authentication) — operational 2023+

- **GPS NMA** (Navigation Message Authentication) — planned 2025+

- **BeiDou authenticated signals** — available for authorized users

**How it works:**

1. Satellite broadcasts include HMAC signature over navigation message

2. Receiver verifies signature using public key (distributed via secure channel)

3. If signature invalid → discard signal, mark as untrusted

**Limitations:**

- Not all constellations support it yet (GPS civilian is still unsigned)

- Requires updated receivers ($200-1K premium over standard)

- Only verifies message integrity, not signal authenticity (replay attacks still possible)

**AiYou approach:**

- **Treat unauthenticated GNSS as "untrusted input"** until cross-checked by other layers

- **Use authenticated signals (Galileo OSNMA) as higher-confidence anchor** when available

---

### L2: LEO-Assisted PNT (Starlink/OneWeb/Kuiper)

**Problem:** Traditional GNSS satellites orbit at 20,000+ km (MEO/GEO) → easy to mimic from ground.

**Solution:** LEO satellites orbit at 340-1,200 km → much harder geometry for ground spoofers.

**AiYou implementation:**


1. **Starlink timing signals:**

   - Starlink satellites broadcast timing beacons (similar to GNSS)

   - Encrypted + signed by SpaceX keys

   - Ground receivers time-of-arrival (TOA) multilateration


2. **Ranging via satellite downlink:**

   - Measure round-trip time to known Starlink satellite position

   - Cross-check with GNSS-derived position

   - If discrepancy >100m → flag as potential spoofing


3. **Signed navigation messages:**

   - SpaceX (or LEO operator) cryptographically signs ephemeris data

   - Receivers verify signature before using position data

**Benefits:**

- **Different geometry** than GNSS (harder to spoof both simultaneously)

- **Lower latency** (340km vs 20,000km → ~1ms vs ~67ms light-travel time)

- **SpaceX controls keys** → spoofing requires compromising SpaceX (vs commodity GPS spoofer)

**Partnership required:**

- Starlink Partner API access for PNT feed (currently private)

- MOU with SpaceX for commercial PNT service

- Estimated cost: $0.01-0.05 per device per month (wholesale)

---

### L3: Terrestrial PNT Beacons

**Problem:** Satellites can be jammed from ground. Need non-GNSS backup.

**Solution:** Ground-based ranging + timing signals.

#### 5G Timing Beacons

5G cell towers already broadcast precise timing (for network sync). AiYou leverages this:


1. **Time-of-Flight (ToF) ranging:**

   - Measure signal propagation delay from multiple 5G towers

   - Multilateration (similar to GPS, but ground-based)

   - Accuracy: 5-50 meters (urban), better with carrier-phase


2. **Carrier-grade timing:**

   - 5G towers sync to GPS + fiber (PTP/PTPv2) → accurate to <100ns

   - Even if GPS jammed, fiber timing persists

**AiYou deployment:**

- Partner with telcos (Verizon, T-Mobile, AT&T) to access timing API

- Or: deploy our own beacon network (CBRS spectrum, unlicensed 5.8GHz)

#### Dedicated Beacons (Roadside Units, RSUs)

**For highways / critical corridors:**

- Install AiYou-owned beacon transmitters every 1-5 km

- DSRC (5.9GHz) or C-V2X (cellular-vehicle) protocol

- Each beacon:

  - Knows its own location (surveyed to <1m accuracy)

  - Broadcasts signed timing messages

  - Costs ~$2K-5K per unit

**Use case:** Autonomous truck corridors (I-5, I-95, I-10)

---

### L4: Local Sensor Fusion

**Problem:** All external signals (GNSS, LEO, 5G) can be jammed or denied in some environments (tunnels, urban canyons, inside buildings).

**Solution:** Onboard sensors provide dead-reckoning during outages.

**Sensors:**

1. **IMU (Inertial Measurement Unit):**

   - 3-axis accelerometer + gyroscope + magnetometer

   - Drift rate: consumer-grade drifts ~1 m/s²; tactical-grade <0.01 m/s²

   - Cost: $50-500 (consumer), $5K-50K (tactical)


2. **Odometry:**

   - Wheel encoders (vehicles)

   - Visual odometry (cameras + SLAM)

   - LiDAR SLAM (expensive but accurate)


3. **Map-matching:**

   - Compare sensor-derived position to known road network (OpenStreetMap, HERE)

   - Snap to most likely road segment

**Fusion algorithm:**

```python

# Simplified Kalman filter fusion

def fuse_sensors(gnss, leo, terrestrial, imu, map_match) -> Position:
    """Weighted fusion of all PNT sources."""
    weights = {
        "gnss": gnss.confidence * 0.4,
        "leo": leo.confidence * 0.3,
        "terrestrial": terrestrial.confidence * 0.2,
        "imu": imu.confidence * 0.05,
        "map": map_match.confidence * 0.05,
    }

    # Weighted average
    lat = sum(src.lat * w for src, w in zip([gnss, leo, terrestrial, imu, map_match], weights.values()))
    lon = sum(src.lon * w for src, w in zip([gnss, leo, terrestrial, imu, map_match], weights.values()))

    # Compute overall confidence
    confidence = sum(weights.values()) / sum(1 for src in [gnss, leo, terrestrial, imu, map_match] if src.available)

    return Position(lat, lon, confidence)

```

**Hold time:** How long can system operate without external signals?

- **Consumer IMU:** 30-60 seconds before drift >10m

- **Automotive-grade:** 5-10 minutes before drift >10m

- **Tactical IMU:** 30-60 minutes before drift >10m

---

### L5: RF Anti-Spoofing (Multi-Antenna)

**Problem:** Single-antenna receivers can't tell if signal is coming from satellite or ground spoofer.

**Solution:** Multi-element antenna array measures **direction-of-arrival (DoA)**.

**How it works:**

1. **Expected DoA:** Satellites are known to be in the sky (elevation >10°)

2. **Spoofer DoA:** Ground-based spoofer appears at low elevation or wrong azimuth

3. **Detection:** If DoA inconsistent with satellite ephemeris → flag as spoof

**Hardware:**

- **Antenna:** 4-8 element array (patch antennas)

- **RF front-end:** Phase-coherent sampling (GPS L1 + L5)

- **Processing:** Cross-correlation → DoA estimation

- **Cost:** $500-2K (commercial), $5K-20K (defense-grade)

**Nulling:** Advanced systems can digitally "null out" spoofer direction while preserving real satellite signals.

---

### L6: Cryptographic Attestation

**All PNT messages are signed by trusted keys.**

**Hierarchy:**

```

Root CA (offline HSM)
  ↓
Regional PNT Authority (online HSM)
  ↓
Beacon/PoP Keys (TPM, rotated quarterly)

```

**Signed message format:**

```json
{
  "type": "pnt_solution",
  "timestamp_utc": "2025-11-15T14:23:45.678901234Z",
  "position": {
    "lat": 47.6062,
    "lon": -122.3321,
    "alt_m": 12.3,
    "confidence": 0.93
  },
  "sources": {
    "gnss": { "sats": 12, "hdop": 0.7, "authenticated": true },
    "leo": { "sats": 4, "source": "starlink", "authenticated": true },
    "terrestrial": { "beacons": 3, "authenticated": true }
  },
  "signature": {
    "key_id": "aiyou-pnt-sea-01-2025-Q4",
    "algorithm": "ES256",
    "sig": "cose:a10126a1045..."
  }
}

```

**Verification:**

- Client downloads public keys from `/.well-known/aiyou-pnt-keys.json`

- Verifies signature (COSE/JWS)

- Checks key is not revoked (CRL lookup)

- Trusts position if signature valid + confidence >0.8

---

### L7: ML Anomaly Detection

**Real-time models detect improbable behavior patterns.**

**Features (per second):**

- Position delta (expected: <100 m/s for ground vehicles, <300 m/s for aircraft)

- Velocity consistency (Kalman filter residual)

- Multi-source agreement (GNSS vs LEO vs terrestrial)

- Signal characteristics (power levels, multipath, SNR)

**Model:** XGBoost or LightGBM (fast inference <1ms)

**Training data:**

- Normal operation (millions of km of real driving/flying)

- Synthetic spoofing attacks (simulated)

- Known spoofing incidents (public datasets)

**Output:**

```json
{
  "anomaly_score": 0.92,  // 0-1 scale
  "triggers": ["sudden_position_jump", "multi_source_disagreement"],
  "action": "flag_for_review"
}

```

**Thresholds:**

- Score >0.8 → Alert user, switch to safe mode

- Score >0.95 → Auto-reject position, use last-known-good + IMU dead-reckoning

---

### L8: ShadowTag Ledger (Immutable Proof-of-Location)

Every PNT solution gets logged to append-only ledger.

**Use cases:**

1. **Forensics:** "Where was this truck at 14:23:45 UTC?"

2. **Audit:** "Prove this aircraft was in US airspace during classified operation"

3. **Dispute resolution:** "Driver claims GPS showed different route"

4. **Insurance:** "Vehicle's black box location matches reported accident site"

**Schema:** See [ShadowTag L4 Relational Attestation](./shadowtag-verification.md#l4-relational-attestation-spatiotemporal-proofing)

**Retention:**

- **High-value (aviation, defense):** 7-10 years

- **Commercial (logistics):** 2-3 years

- **Consumer (rideshare):** 90 days

---

## Attack Model & Mitigations

| Attack | AiYou Mitigation | Difficulty Increase |
|--------|------------------|---------------------|
| **Ground spoofer (GPS only)** | Multi-source (LEO + terrestrial) + DoA check | 100× |
| **Multi-constellation spoof** | LEO has different geometry; DoA catches ground source | 500× |
| **Jammer** | Terrestrial beacons + IMU fallback | 10× (still degrades, but graceful) |
| **Compromised upstream (fake ephemeris)** | Cryptographic signatures + cross-checks | 1000× (requires key compromise) |
| **Supply-chain (receiver backdoor)** | TPM attestation + remote verification | 100× (requires physical/firmware access) |
| **Nation-state multi-vector** | All layers + ML anomaly → triggers alarm, fails safe | Extremely difficult; detection <2s |

---

## MVP Implementation (6-12 Months)

### Function

LEO + inertial + local ML overlay for **automotive and critical asset tracking**.

### Components


1. **Device SDK (Python/Rust)**

   - Sensor fusion (GNSS + IMU + map-match)

   - Signature verification (COSE)

   - Local anomaly detection (XGBoost model <5MB)


2. **Edge PNT Microservice (FastAPI)**

   - Accepts raw telemetry (NMEA, IMU, cell tower IDs)

   - Returns signed position/time corrections

   - Runs ML anomaly model

   - Logs to ShadowTag


3. **Multi-Source Ingestion:**

   - Authenticated GNSS (Galileo OSNMA via u-blox F9P receiver)

   - Starlink timing feed (via partner API)

   - 5G beacon simulator (for testing, 3 fake towers)


4. **ShadowTag Logging Service:**

   - PostgreSQL append-only log

   - Public anchor every 10 minutes (OpenTimestamps)


5. **Dashboard:**

   - Live map of tracked assets

   - Anomaly alerts

   - Forensic playback (historical tracks)

### Timeline & Cost

| Phase | Duration | Cost | Deliverables |
|-------|----------|------|--------------|
| **Lab prototype** | 3 months | $250K-500K | SDK, edge service, anomaly model |
| **Field pilot** | 6 months | $500K-1.5M | 10-50 vehicles, spoof detection demo |
| **Commercial beta** | 12 months | $2M-5M | 1K+ devices, telco partnerships |

**Funding sources:**

- Seed round ($8M total, allocate $2M to PNT)

- Government grants (DHS SBIR, DoD contracts for anti-spoofing R&D)

---

## Unit Economics (Per Device)

### Hardware

| Component | Cost (Bulk) | Purpose |
|-----------|-------------|---------|
| **Multi-band GNSS (u-blox F9P or equivalent)** | $150-300 | GPS/Galileo/BeiDou with OSNMA |
| **Multi-antenna array (4-element)** | $80-150 | DoA for anti-spoofing |
| **IMU (automotive-grade)** | $50-100 | Dead-reckoning during jamming |
| **Cellular modem (4G/5G)** | $30-60 | Terrestrial beacon reception + backhaul |
| **TPM 2.0 module** | $5-15 | Secure key storage |
| **Compute (ARM SoC)** | $20-40 | Sensor fusion + ML inference |
| **Enclosure + power** | $30-50 | Ruggedized, automotive/marine-rated |
| **Total per unit** | **$365-715** | Consumer/commercial |
| **Total per unit (defense-grade)** | **$1,500-3,000** | Tactical IMU, encrypted RF, DO-178C certified |

### Service Revenue (Annual per Device)

| Customer Type | Monthly Fee | Annual Revenue | Margin |
|---------------|-------------|----------------|--------|
| **Consumer/Fleet** | $3-8 | $36-96 | 75% |
| **Aviation (certified)** | $100-500 | $1,200-6,000 | 80% |
| **Defense** | $500-2,000 | $6,000-24,000 | 85% |
| **Forensic/Audit (on-demand)** | — | $500-5,000 per incident | 90% |

### Break-Even

**Example: Fleet logistics (1,000 trucks)**

**Upfront:**

- Hardware: $500 × 1,000 = $500K

- Installation: $200 × 1,000 = $200K

- **Total CAPEX:** $700K

**Annual:**

- Service revenue: $60 × 1,000 = $60K/year

- Hardware warranty/support: $10K/year

- Cloud infrastructure: $5K/year

- **Net profit:** $45K/year

**Payback:** 700K / 45K = **15.5 years** ❌ **Too long!**

**Better model: Hardware-as-a-Service**

- Monthly fee includes hardware amortized over 3 years

- $20/month device cost + $8/month service = $28/month total

- **Annual revenue:** $28 × 12 × 1,000 = $336K

- **Annual cost:** $150K (hardware amortization + service)

- **Net profit:** $186K/year

- **Payback:** <4 years ✅

---

## Go-to-Market

### Phase 1: High-Pain Verticals (Month 0-12)

**Target:** Customers already suffering from GPS spoofing/jamming.

| Vertical | Pain Point | AiYou Solution | Initial Customers |
|----------|------------|----------------|-------------------|
| **Defense/Military** | GPS denial in contested areas | Multi-source PNT, works under jamming | DoD, NATO pilots |
| **Aviation** | Safety-critical navigation | Certified backup PNT, audit trails | Regional airlines, biz jets |
| **Autonomous Vehicles** | Spoofing → accidents | Anti-spoof + lane-level accuracy | Tesla FSD beta, trucking fleets |
| **Maritime** | Ships misdirected, grounding | Verified location + forensics | Container ships, offshore rigs |

**Sales strategy:**

- Direct sales (defense, aviation)

- Pilot programs (90-day free trial)

- Government contracts (SBIR/STTR, direct procurement)

### Phase 2: Scale (Month 12-36)

**Target:** Broader commercial adoption.

| Segment | Device Volume | Annual Service Revenue |
|---------|---------------|------------------------|
| Commercial fleet (trucks, delivery) | 50K-100K | $3M-8M |
| Precision agriculture (tractors, drones) | 20K-50K | $1M-3M |
| Telco (5G tower timing verification) | 10K-30K | $5M-15M |
| Financial (HFT timestamp verification) | 1K-5K | $10M-50M |

**Channels:**

- OEM partnerships (Qualcomm, u-blox for receiver integration)

- Telco bundles (T-Mobile, Verizon sell as "Verified GPS" add-on)

- Insurance partnerships (State Farm, Progressive offer discounts for AiYou-equipped vehicles)

---

## Regulatory & Certification

### Aviation (FAA/EASA)

**Required:** DO-178C (software), DO-254 (hardware), DO-160 (environmental)

**Timeline:** 18-36 months, $3M-10M

**Approval path:**

1. Technical Standard Order (TSO) for PNT unit

2. Supplemental Type Certificate (STC) for aircraft installation

3. Part 23/25 certification (if backup navigation system)

**Benefits:**

- Can market as "certified GPS backup" for general aviation

- Required for IFR (Instrument Flight Rules) operations

- Premium pricing ($5K-20K per aircraft)

### Automotive (ISO 26262, ASIL)

**Required:** ASIL-B or ASIL-D (for safety-critical localization)

**Timeline:** 12-24 months, $1M-5M

**OEM integration:**

- Tesla, Waymo, Cruise for FSD/autonomy

- Trucking OEMs (Volvo, Daimler, PACCAR)

### Defense (NIST/CMMC, RMF)

**Required:**

- NIST 800-171 (cybersecurity)

- CMMC Level 2-3 (for DoD contracts)

- RMF Level 5-6 (for classified systems)

**Timeline:** 12-18 months, $2M-8M

**Contracts:**

- Direct DoD procurement (sole-source or competitive)

- Prime contractor subcontracts (Lockheed, Raytheon, Northrop)

---

## 3-Year Revenue Projection

| Year | Devices Deployed | Service ARR | Hardware Revenue | Total Revenue | Gross Margin |
|------|------------------|-------------|------------------|---------------|--------------|
| **Y1 (Pilot)** | 500-1,000 | $500K-1M | $500K | $1M-1.5M | 40% |
| **Y2 (Scale)** | 10K-20K | $15M-30M | $5M-10M | $20M-40M | 65% |
| **Y3 (Enterprise)** | 50K-100K | $80M-200M | $20M-40M | $100M-240M | 70% |

**Profitability:** Cash-flow positive by Month 18 (Q3 Y2)

---

## Strategic Value to AiYou Ecosystem

### Integration with Other Layers


1. **ShadowTag:** PNT solutions feed into L4 spatiotemporal attestation

2. **Edge Mesh:** PNT corrections distributed via AiYou PoPs (low latency)

3. **Starlink:** LEO timing signals from Starlink satellites (partnership)

4. **5G Beacons:** Telco partnerships for terrestrial PNT (co-sell with edge compute)

### Competitive Moat

**After 10K devices deployed:**

- Network effects (more devices = more corroboration = higher confidence)

- Regulatory approvals (FAA/EASA/DoD certs = multi-year, multi-million $ barrier)

- Hardware ecosystem (OEMs integrate, switching cost high)

- Data moat (historical PNT logs enable better anomaly models)

**Estimated replacement cost for competitor:** $100M-500M + 3-5 years

---

## Next Steps (30-Day Action Plan)


1. **Assemble team:**

   - 1× PNT engineer (GNSS/RF background)

   - 1× Sensor fusion engineer (Kalman filters, IMU)

   - 1× ML engineer (anomaly detection)

   - 1× Backend engineer (edge service, ShadowTag integration)

   - **Cost:** $80K-120K/month (loaded)


2. **Prototype stack:**

   - Order hardware (u-blox F9P receivers, IMUs, dev boards): $10K-20K

   - Build fusion SDK + simulated LEO feed adapter: 4-6 weeks

   - Integrate with ShadowTag ledger: 2-3 weeks


3. **Lab testing:**

   - Controlled spoofing tests (no public transmission)

   - Measure detection latency, false positive rate

   - Document results for pilot proposals


4. **Engage partners:**

   - Starlink (PNT API access MOU)

   - CoreWeave (edge service hosting)

   - Telco (5G beacon access)


5. **Pilot recruitment:**

   - 1× fleet operator (trucking or delivery)

   - 1× maritime operator (offshore or container shipping)

   - 1× defense pilot (via DoD SBIR or direct contract)

**Total 30-day budget:** $150K-250K

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Spoof detection rate** | >98% | Lab + field tests |
| **False positive rate** | <1 per 1,000 hours | Anomaly detector logs |
| **Multi-source fusion accuracy** | <5m (95th percentile) | Compared to surveyed ground truth |
| **Time-to-detect (spoofing)** | <2 seconds | Lab replay tests |
| **Jamming resilience** | >90% availability during 50% GNSS outage | Simulated jamming |
| **Customer NPS (Net Promoter Score)** | >60 | Post-pilot survey |

---

## References


- [ShadowTag Verification (L4 Spatial)](./shadowtag-verification.md)

- [Starlink Integration (LEO PNT source)](./starlink-coreweave-integration.md)

- [Phase 4 Rollout (Defense & PNT)](../04-phase-rollout/phase-4-defense-pnt.md)

- [GNSS Spoofing Research Papers](https://gpspatron.com/spoofing-detection/)

- [Galileo OSNMA Specification](https://www.gsc-europa.eu/galileo/services/galileo-open-service-navigation-message-authentication-osnma)
