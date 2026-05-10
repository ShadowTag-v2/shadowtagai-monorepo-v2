# SHADOWTAG SYSTEM MANUAL (v1.0)
**"Simplicity is the ultimate sophistication."**

## 1. The Core: ShadowTag Engine (`watermark.py`)
The engine runs in **SILO MODE** by default to allow rapid testing without Heavy Dependencies (Solana/WavMark).

### How to Run
```bash
python3 services/shadow_tag/watermark.py
```
*   **Input**: It currently initializes the engine.
*   **Output**: "MOCK" status confirming the architecture is wired correctly.

### Toggle to Production
To enable Real Steganography & Blockchain:
1.  Open `services/shadow_tag/watermark.py`
2.  Set `SILO_MODE = False`
3.  Ensure `solana` and `stegano` are installed.

## 2. The Brain: Edge Orchestrator (`orchestrator.js`)
Designed for **Cloudflare Workers**. It routes prompts to the 7-LLM Cluster.

### How to Test (Local)
You can simulate the Edge environment using `node`:
```bash
# Basic syntax check
node --check services/edge/orchestrator.js
```
*Note: Real execution requires the Cloudflare `wrangler` CLI or deployment.*

## 3. The Infrastructure (Gideon)
**Status**: Deploying via Terraform.
*   **Vault**: `gideon-sovereign-vault` (Active)
*   **Workstation**: `gideon-prime` (Provisioning in Air-Gapped Cluster)

## 4. The Pricing (`SHADOWTAG_PRICING_MODEL.md`)
Refer to this artifact for the $150k/mo "Sovereign Node" sales strategy.
