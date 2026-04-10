# pnkln — Roll-Up Packet for Google Sales (Nick)

**Date:** 2025-10-29
**Owner:** pnkln (formerly ShadowTag-v4/Omega)
**Contact:** Founder (private), via this package handoff

## Executive Summary
pnkln compiles our scripts and prompt templates into Google Vertex AI Studio–friendly assets. This packet is designed for a quick sales/solutions review by Google Cloud (Nick). It includes:
- A consolidated **README** (this file)
- A **Test Index** with smoke/validation checks
- Vertex AI Studio **shell-cell ready** snippets and **prompt templates**
- Demo scripts to run locally or in Vertex AI Notebooks

> Note: This is a structure & sample content roll-up. If you require the full private codebase, we can deliver via a secure channel upon mutual NDA.

---

## What pnkln Does (at a glance)
- Converts mixed scripts & prompts → **Vertex AI Studio native cells** (Jupyter/Notebook compatible)
- Standardizes naming & structure under the **pnkln** namespace
- Preps **demo flows** for sales/SE enablement & quick proof-of-value

## Who It's For
- **Google Cloud Sales / Solutions (Nick)** evaluating feasibility & fit for Vertex AI + GCP
- **SEs** who want runnable, minimal demo scripts and validation checks

---

## Contents

```
pnkln/
  docs/
    SALES_BRIEF_NICK.md
  prompts/
    pnkln_prompt_templates.md
  scripts/
    run_demo.sh
    deploy_gcp.sh
  tests/
    smoke/
      00_env_check.sh
    validation/
      prompt_validation.py
  vertex_studio/
    demo_notebook_shell_cells.txt
README.md
TEST_INDEX.md
```

---

## Quick Start (Vertex AI Studio / Notebooks)

Open a Vertex AI Notebook and paste the following **shell cell** blocks as-is.

### 1) Environment & CLI checks
```bash
%%bash
set -euo pipefail
echo "[pnkln] Env check"
python3 --version
pip3 --version
gcloud --version || echo "gcloud not installed"
```

### 2) (Optional) Auth to GCP
```bash
%%bash
# If in a local notebook; on Vertex AI Workbench, you may already be authenticated.
gcloud auth login --brief || true
gcloud config set project $GCP_PROJECT_ID
```

### 3) Run the demo
```bash
%%bash
chmod +x pnkln/scripts/run_demo.sh
./pnkln/scripts/run_demo.sh
```

---

## Security Notes
- No user PII shipped here.
- Keep everything encrypted at rest and in transit.
- For any data integrations, use secret managers / scoped service accounts only.

## Next Steps
- If this packet is sufficient for initial review, we'll schedule a deeper technical session to walk through full assets and private repos under NDA.
