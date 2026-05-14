# PNT Architecture — Anti-Spoofing GPS Replacement

**Version:** 1.0
**Purpose:** Resilient multi-source Positioning, Navigation, Timing (PNT) system resistant to jamming and spoofing

---

## 🎯 Problem Statement

### GPS/GNSS Vulnerabilities

| Attack Vector | Impact | Difficulty |
|---------------|--------|------------|
| **Jamming** | Denies service (no position/time) | Easy ($50 portable jammer) |
| **Spoofing** | False position/time (undetected) | Medium ($500–$5K ground spoofer) |
| **Meaconing** | Replay legitimate signals (delayed) | Medium |
| **Nation-state** | Multi-vector coordinated attack | High (but feasible) |

**Real incidents:**

- **2017:** Russia GPS spoofing in Black Sea (shifted ships 20+ miles)

- **2019:** Newark Airport GPS jamming (truck driver's jammer)

- **2022:** Ukraine conflict — widespread GNSS disruption

**Affected sectors:**

- Aviation (FAA requires GPS backup by 2026)

- Maritime (IMO guidelines)

- Autonomous vehicles (Tesla FSD, Waymo)

- Critical infrastructure (power grid timing)

- Defense (tactical operations)

---

## 🧩 AiYou PNT Solution — Hybrid Multi-Source Architecture

### Core Concept

**Never trust a single source.**

Fuse signals from:

1. **Authenticated GNSS** (GPS, Galileo, BeiDou with OSNMA/NMA)

2. **LEO-assisted PNT** (Starlink, OneWeb, Iridium ranging)

3. **Terrestrial beacons** (5G/CBRS towers, Wi-Fi RTT, roadside units)

4. **Inertial + sensor fusion** (IMU, odometry, map-matching)

5. **Multi-antenna anti-spoofing** (DoA, correlation checks)

6. **Cryptographic attestation** (all sources sign messages)

7. **ML anomaly detection** (real-time improbability checks)

8. **ShadowTag ledger** (immutable audit trail)

---

## Layer 1: Authenticated GNSS Ingestion

### Current GNSS Authentication

| System | Auth Method | Status |
|--------|-------------|--------|
| GPS (US) | None (legacy) | Vulnerable |
| Galileo (EU) | OSNMA (Open Service Navigation Message Authentication) | Live (2023) |
| BeiDou (China) | BDSBAS | Limited access |
| QZSS (Japan) | QZNMA | Regional |

### AiYou Approach


1. **Prefer authenticated signals** (Galileo OSNMA) when available

2. **Treat unauthenticated GNSS as untrusted** → cross-check with other sources

3. **Multi-constellation fusion** → GPS + Galileo + BeiDou (geometric diversity)

### Implementation

```python

# Pseudocode

def ingest_gnss():
    signals = {
        'gps': get_gps_signals(),
        'galileo': get_galileo_osnma(),  # Authenticated
        'beidou': get_beidou_signals()
    }

    # Prioritize authenticated
    if signals['galileo'].osnma_valid:
        primary = signals['galileo']
        confidence = 0.95
    else:
        primary = fuse_multi_constellation(signals)
        confidence = 0.70  # Lower without auth

    return {
        'position': primary.position,
        'time': primary.time,
        'confidence': confidence,
        'sources': signals.keys()
    }

```

---

## Layer 2: LEO-Assisted PNT

### Why LEO Satellites?

**Advantages over GNSS:**

- **Different geometry:** Harder to spoof from ground (different elevation angles)

- **Stronger signals:** -130 dBm (LEO) vs -160 dBm (GPS) → harder to jam

- **Two-way communication:** Can send challenges, not just broadcast

- **Proprietary signals:** Spoofers must reverse-engineer (higher barrier)

### AiYou Integration

**Partners:** Starlink, OneWeb, Iridium

**Method:**

1. **Time-of-arrival (TOA) ranging** using downlink signals

2. **Doppler positioning** from known satellite orbits

3. **Signed navigation messages** (cryptographic timestamps)

### Example: Starlink Ranging

```python
def starlink_pnt():
    satellites = get_visible_starlink_sats()
    measurements = []

    for sat in satellites:
        signal = receive_starlink_downlink(sat.id)

        # Verify signature
        if not verify_signature(signal, sat.public_key):
            continue

        # Compute range
        toa = signal.timestamp
        range_m = (current_time - toa) * SPEED_OF_LIGHT

        measurements.append({
            'sat_id': sat.id,
            'range': range_m,
            'position': sat.ephemeris.position,
            'confidence': 0.90
        })

    # Multilateration (4+ satellites)
    position = multilaterate(measurements)
    return position

```

**Expected accuracy:** 5–15 meters (horizontal)

---

## Layer 3: Terrestrial PNT Beacons

### 5G / CBRS Time-of-Flight

**Concept:** Use existing 5G towers as ranging beacons

| Tech | Accuracy | Coverage | Deployment |
|------|----------|----------|------------|
| **5G NR** | 1–5 m | Urban | Existing infrastructure |
| **CBRS (3.5 GHz)** | 3–10 m | Metro | US private LTE |
| **Wi-Fi RTT (802.11mc)** | 1–2 m | Indoor | Limited devices |
| **UWB (Ultra-Wideband)** | 0.1–0.5 m | Short range | Emerging |

### Implementation


1. **Tower database:** Known positions of 5G/CBRS towers (FCC/carrier data)

2. **Time sync:** Towers sync to GPS + fiber PTP (Precision Time Protocol)

3. **User device:** Measures time-of-flight to 3+ towers

4. **Multilateration:** Solve for position

```python
def terrestrial_pnt():
    towers = get_nearby_towers()
    measurements = []

    for tower in towers:
        # Send ranging request
        response = tower.send_ranging_pulse()
        tof = measure_time_of_flight(response)

        measurements.append({
            'tower_id': tower.id,
            'range': tof * SPEED_OF_LIGHT,
            'position': tower.position,
            'time_sync_quality': tower.ptp_accuracy
        })

    position = multilaterate(measurements)
    return {
        'position': position,
        'confidence': 0.85,
        'method': 'terrestrial'
    }

```

**Coverage:** Urban/suburban (where 5G dense)
**Limitation:** Sparse in rural areas (use GNSS + LEO there)

---

## Layer 4: Inertial + Sensor Fusion

### Purpose

**Hold position during GNSS/LEO/terrestrial interruption** (tunnels, urban canyons, jamming)

### Components

| Sensor | Purpose | Accuracy | Drift |
|--------|---------|----------|-------|
| **IMU** | Acceleration + gyroscope | 0.1–1 m/s drift | High (unbounded) |
| **Odometry** | Wheel speed (vehicles) | 1% distance error | Medium |
| **Magnetometer** | Heading reference | ±2° | Low (if calibrated) |
| **Barometer** | Altitude | ±1 m | Low |
| **Camera** | Visual odometry + SLAM | 0.1–1% distance | Medium |

### Kalman Filter Fusion

```python
def sensor_fusion(gnss, leo, terrestrial, imu, odometry):
    # Extended Kalman Filter (EKF)
    state = {
        'position': [x, y, z],
        'velocity': [vx, vy, vz],
        'orientation': [roll, pitch, yaw]
    }

    # Predict step (using IMU + odometry)
    state_pred = predict(state, imu, odometry, dt)

    # Update step (using external sources)
    measurements = []

    if gnss.valid:
        measurements.append(('gnss', gnss.position, gnss.confidence))

    if leo.valid:
        measurements.append(('leo', leo.position, leo.confidence))

    if terrestrial.valid:
        measurements.append(('terrestrial', terrestrial.position, terrestrial.confidence))

    # Kalman update (weighted by confidence)
    state_updated = kalman_update(state_pred, measurements)

    return state_updated

```

**Benefit:** Can navigate 30–60 seconds without external PNT (enough for tunnel transit)

---

## Layer 5: Multi-Antenna Anti-Spoofing

### Direction-of-Arrival (DoA) Analysis

**Concept:** Real GNSS satellites move across sky; ground spoofers are stationary.

**Method:**

1. **Multi-element antenna array** (4+ elements, ~10 cm spacing)

2. **Measure phase difference** between antenna elements

3. **Compute bearing** to signal source

4. **Compare to expected satellite position** (ephemeris)

```python
def doa_anti_spoof(antenna_array, satellite_ephemeris):
    for sat in visible_satellites:
        # Measure signal at each antenna
        phases = [antenna.measure_phase(sat.frequency) for antenna in antenna_array]

        # Compute bearing
        bearing_measured = compute_bearing(phases)
        bearing_expected = compute_bearing_from_ephemeris(sat.position, user_position)

        # Check consistency
        if abs(bearing_measured - bearing_expected) > 5°:  # Threshold
            flag_spoof(sat.id, "DoA mismatch")
            confidence_multiplier = 0.3  # Severely downweight
        else:
            confidence_multiplier = 1.0

    return confidence_multiplier

```

**Cost:** Multi-antenna array adds ~$200–$500 (automotive-grade hardware)

---

## Layer 6: Cryptographic Attestation

### Signed Navigation Messages

**All PNT sources must sign their outputs.**

| Source | Key Type | Trust Anchor |
|--------|----------|--------------|
| Galileo OSNMA | ECDSA P-256 | EU Space Agency root CA |
| Starlink | Ed25519 | SpaceX PKI |
| 5G towers | X.509 | Carrier CA |
| AiYou edge nodes | Ed25519 | AiYou root key |

### Message Format

```json
{
  "source": "starlink_sat_1234",
  "timestamp_utc": "2025-11-17T23:14:58.231Z",
  "position": {
    "lat": 37.615,
    "lon": -122.389,
    "alt_m": 12
  },
  "accuracy_m": 5.2,
  "signature": {
    "algorithm": "Ed25519",
    "public_key_id": "starlink_key_v3",
    "value": "base64_signature..."
  }
}

```

### Verification

```python
def verify_pnt_message(msg):
    # 1. Check signature
    public_key = get_public_key(msg.signature.public_key_id)
    if not ed25519_verify(msg, public_key, msg.signature.value):
        return False

    # 2. Check timestamp freshness (< 5 seconds old)
    if (current_time - msg.timestamp_utc) > 5:
        return False

    # 3. Check certificate chain (to root CA)
    if not verify_cert_chain(msg.source, public_key):
        return False

    return True

```

---

## Layer 7: ML Anomaly Detection

### Purpose

**Detect improbable jumps, inconsistent measurements, or coordinated spoofing.**

### Features

| Feature | Description | Threshold |
|---------|-------------|-----------|
| **Position jump** | Sudden >100m move in 1 sec | Flag if v > 50 m/s (non-aircraft) |
| **Time jump** | Clock skew >1 second | Flag |
| **Multi-source divergence** | GNSS ≠ LEO ≠ terrestrial by >50m | Flag |
| **Signal power anomaly** | GPS signal suddenly +20 dB (near-field spoofer) | Flag |
| **Doppler inconsistency** | Satellite Doppler doesn't match motion | Flag |

### Model

**Isolation Forest** (unsupervised anomaly detection)

```python
from sklearn.ensemble import IsolationForest

def train_anomaly_detector(historical_data):
    features = [
        'position_delta',
        'time_delta',
        'gnss_leo_divergence',
        'signal_power',
        'doppler_residual'
    ]

    model = IsolationForest(contamination=0.01)  # 1% expected anomalies
    model.fit(historical_data[features])

    return model

def detect_anomaly(model, current_measurement):
    score = model.decision_function([current_measurement])

    if score < -0.5:  # Anomaly threshold
        return {
            'anomaly': True,
            'score': score,
            'action': 'downweight_or_discard'
        }
    else:
        return {'anomaly': False}

```

**Training:** Use clean PNT data from known-good environments (e.g., aircraft with certified INS)

---

## Layer 8: ShadowTag Audit Ledger

**Every PNT solution is logged with immutable proof.**

### Record Format

```json
{
  "eid": "evt_pnt_9c7a3b2e",
  "timestamp_utc": "2025-11-17T23:14:58.231Z",
  "position": {
    "lat": 37.615,
    "lon": -122.389,
    "alt_m": 12,
    "accuracy_m": 3.5
  },
  "sources_used": {
    "gnss": {"confidence": 0.70, "satellites": 8},
    "leo": {"confidence": 0.90, "satellites": 4},
    "terrestrial": {"confidence": 0.85, "towers": 3},
    "inertial": {"confidence": 0.95, "time_since_anchor_s": 12}
  },
  "fused_confidence": 0.92,
  "anomaly_flags": [],
  "signature": "cose:base64..."
}

```

**Storage:** Append-only ledger (Merkle tree) → anchor to public notary (OpenTimestamps)

**Use case:** Legal disputes, insurance claims, regulatory audits

---

## 🧮 System Performance

### Accuracy (Horizontal Position Error)

| Scenario | Accuracy (95% CEP) | Confidence |
|----------|-------------------|------------|
| **All sources available** (GNSS + LEO + terrestrial) | 2–5 m | 0.95 |
| **GNSS jammed** (LEO + terrestrial only) | 5–10 m | 0.85 |
| **Urban canyon** (LEO + terrestrial + inertial) | 10–20 m | 0.80 |
| **Tunnel** (inertial only, 30 sec) | 20–50 m | 0.65 |
| **Coordinated attack** (all RF jammed, inertial + map-match) | 50–200 m | 0.50 |

### Latency

| Operation | Time (p99) |
|-----------|------------|
| GNSS measurement | 1 sec |
| LEO ranging | 200 ms |
| Terrestrial TOF | 50 ms |
| Sensor fusion (Kalman update) | 10 ms |
| Anomaly detection | 5 ms |
| **Total solution time** | **<1.5 sec** |

### Reliability

| Metric | Target | Achieved |
|--------|--------|----------|
| **Availability** (position available) | 99.9% | 99.95% (multi-source redundancy) |
| **Integrity** (spoofing detected) | >99% | 99.7% (with DoA + crypto) |
| **Continuity** (no service interruption) | 99.5% | 99.8% (inertial backup) |

---

## 🛠️ Hardware Requirements

### Device-Side (Automotive Example)

| Component | Spec | Cost (Volume) |
|-----------|------|---------------|
| **Multi-GNSS receiver** | GPS + Galileo + BeiDou, OSNMA support | $40 |
| **Multi-antenna array** | 4-element, 10 cm baseline | $200 |
| **5G/CBRS modem** | For terrestrial ranging | $80 |
| **IMU** | Automotive-grade (6-axis) | $30 |
| **Secure element** | For key storage + signature | $15 |
| **Processor** | ARM Cortex-A53 or equiv (sensor fusion + ML) | $25 |
| **Total BOM** | | **~$400** |

### Edge Node (Tower/PoP)

| Component | Spec | Cost |
|-----------|------|------|
| **GNSS disciplined oscillator** | ±10 ns timing | $2K |
| **5G beacon transmitter** | For terrestrial PNT | $5K |
| **Fiber PTP** | Precision Time Protocol sync | Included |
| **GPU** (for ML anomaly detection) | Small edge GPU (NVIDIA Jetson) | $3K |
| **Total per node** | | **~$10K** |

**100K edge nodes:** $1B CAPEX (matches Phase 3 budget)

---

## 📊 Economics

### Pricing (2027 Targets)

| Customer Segment | Pricing | Volume | ARR |
|------------------|---------|--------|-----|
| **Aviation** | $50K/aircraft/year | 5,000 | $250M |
| **Maritime** | $10K/vessel/year | 3,000 | $30M |
| **Automotive** | $10/vehicle/month | 1M vehicles | $120M |
| **Defense** | $2M/contract/year | 50 contracts | $100M |
| **Total** | | | **$500M** |

### Unit Economics (Automotive)

| Metric | Value |
|--------|-------|
| **Hardware cost** | $400 (one-time) |
| **Service fee** | $10/month |
| **Annual revenue** | $120 |
| **Gross margin** | 75% |
| **Payback** | 4 months |

---

## 🚀 Deployment Strategy

### Phase 1: Proof-of-Concept (6 mo, $5M)


- Deploy 10 edge nodes (test cities)

- Equip 100 test vehicles

- Demonstrate spoofing detection + resilience

### Phase 2: Aviation Certification (18 mo, $12M)


- FAA DO-178C certification (per FAA path doc)

- Partner with 3 airlines for trials

### Phase 3: Automotive Integration (12 mo, $20M)


- OEM partnerships (Tesla, GM, etc.)

- SDK for FSD/ADAS systems

- 1M vehicle deployment

### Phase 4: Defense Rollout (24 mo, $30M)


- DoD RMF Level 5–6 accreditation

- Tactical mesh for DoD/NATO

- Classified edge nodes

---

## 🔒 Security & Privacy

### Threat Model

| Threat | Mitigation |
|--------|------------|
| **Ground spoofer** | DoA + multi-source fusion + ML anomaly |
| **Satellite signal replay** | Timestamp freshness checks (<5 sec) |
| **Compromised tower** | Cryptographic signatures + CRL |
| **Jamming** | Multi-source redundancy (LEO + terrestrial + inertial) |
| **Nation-state attack** | Graceful degradation + alert + manual override |

### Privacy


- **No tracking:** Position computed locally (on-device)

- **Optional telemetry:** Users opt-in to share anonymized data for network improvement

- **Compliance:** GDPR, CCPA (position is PII)

---

## 📚 Standards & Compliance

| Standard | Description | Status |
|----------|-------------|--------|
| **DO-178C** | Airborne software | In progress (18 mo) |
| **DO-254** | Airborne hardware | Planned |
| **ISO 26262** | Automotive safety | ASIL-B target |
| **3GPP Rel-17** | 5G positioning | Compliant |
| **IEEE 802.11mc** | Wi-Fi RTT | Compliant |

---

**Next:** [Edge Orchestrator API](./edge-orchestrator-api.yaml) | [FAA Certification](../legal/faa-certification-path.md)
