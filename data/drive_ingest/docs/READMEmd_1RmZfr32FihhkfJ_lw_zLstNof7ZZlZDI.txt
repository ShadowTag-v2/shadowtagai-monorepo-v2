# ShadowTag Stream Attestation (L4)

This module implements the "ShadowTag on-stream" architecture, adding a 4th layer (L4) for Relational Attestation.

## Components

1.  **Rust Edge Agent (`edge_agent_rust/`)**
    *   **Function**: Captures raw payload, computes L0 (Hash), L1 (Manifest), and L4 (Relational Record).
    *   **Output**: JSON packet with signed attestation.
    *   **Usage**: `cargo run` (Requires Rust environment).

2.  **Node.js Verifier (`verifier_node/`)**
    *   **Function**: Microservice to verify ShadowTag packets.
    *   **Endpoints**:
        *   `POST /verify`: Checks integrity, signatures, and L4 logic (PNT confidence, etc).
        *   `POST /anchor`: Simulates anchoring to a ledger.
    *   **Usage**: `npm install && node server.js`

3.  **Templates (`templates/`)**
    *   `policy_vc.json`: W3C Verifiable Credential template for data usage.
    *   `merkle_anchor.js`: Script simulating the nightly Merkle anchoring job.

## Architecture

*   **L0 Capture**: BLAKE3 Hash of content.
*   **L1 Integrity**: COSE-signed sidecar (CID, TS, DeviceID).
*   **L2 Timeline**: Merkle Tree anchoring (simulated by `merkle_anchor.js`).
*   **L3 Policy**: W3C VC attached to the stream.
*   **L4 Relational**: Spacetime context (GPS, Celestial, Airspace) + Relation links.

## Quick Start

### Run Merkle Anchor Job
```bash
node templates/merkle_anchor.js
```

### Run Verifier
```bash
cd verifier_node
npm install
node server.js
```

### Run Edge Agent (Rust)
```bash
cd edge_agent_rust
cargo run
```
