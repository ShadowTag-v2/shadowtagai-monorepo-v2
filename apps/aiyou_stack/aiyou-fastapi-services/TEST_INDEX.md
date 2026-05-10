# TEST INDEX — pnkln

**Date:** 2025-10-29

This index enumerates smoke and validation tests to quickly verify a demo environment on Vertex AI Studio or a Cloud Shell-adjacent setup.

## A. Smoke Tests

1. **Environment Check**
   - File: `pnkln/tests/smoke/00_env_check.sh`
   - Purpose: Verify Python, pip, and (if needed) gcloud are available.
   - Run:

     ```bash
     %%bash
     chmod +x pnkln/tests/smoke/00_env_check.sh
     ./pnkln/tests/smoke/00_env_check.sh
     ```

2. **Demo Runner**
   - File: `pnkln/scripts/run_demo.sh`
   - Purpose: Execute a minimal end-to-end demo flow that exercises shell cells and a prompt template.
   - Run:

     ```bash
     %%bash
     chmod +x pnkln/scripts/run_demo.sh
     ./pnkln/scripts/run_demo.sh
     ```

## B. Validation Tests

1. **Prompt Template Validation**
   - File: `pnkln/tests/validation/prompt_validation.py`
   - Purpose: Ensure prompt templates render without missing variables and conform to a simple schema.
   - Run:

     ```bash
     %%bash
     python3 pnkln/tests/validation/prompt_validation.py
     ```

## C. Optional / Extendable

- Add API integration checks (e.g., Vertex AI Models, PaLM/Claude/OpenAI toggles via env flags).
- Add integration smoke for Secret Manager and IAM role checks.
- Add notebook-based unit tests (pytest) if desired.
