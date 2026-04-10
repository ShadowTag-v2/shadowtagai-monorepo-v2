# ShadowTag Acoustic Witness

This module implements the "sonographic chirp" acoustic watermark/beacon system for ShadowTag.

## Components

1.  **Generator (`generator.py`)**: Creates Chirp-Spread Spectrum (CSS) acoustic beacons.
    -   Supports Audible (1-4 kHz) and Ultrasonic (21-24 kHz) bands.
    -   Embeds a 152-bit payload (Version, Epoch, Nonce, ID, HMAC).
    -   Outputs WAV files.

2.  **Receiver (`receiver.py`)**: Simulates a witness node.
    -   Performs matched filtering on audio input.
    -   Detects beacons and extracts metadata.
    -   Generates a cryptographically signed JSON witness report.

3.  **Verifier (`verifier.py`)**: Server-side validation service.
    -   Verifies witness signatures.
    -   Checks timestamp freshness and signal quality (SNR).
    -   Anchors valid reports to the ShadowTag log.

## Usage Demo

Run the full end-to-end flow:

```bash
# 1. Generate Beacon WAVs
python3 generator.py

# 2. Process Audio & Generate Witness Report
python3 receiver.py

# 3. Verify & Anchor Report
python3 verifier.py witness_report.json
```

## Specs

-   **Modulation**: CSS with Gold Code sequences (simulated).
-   **Security**: HMAC-SHA256 signatures on beacons and witness reports.
-   **Hardware Target**: ESP32-S3 or Raspberry Pi Zero 2 W with MEMS microphone.