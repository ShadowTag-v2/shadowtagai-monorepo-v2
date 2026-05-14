# Implementation Plan - SPM Loop & Dual Sidecar

## Goal Description

Implement the "Self-Prompting Monkey" (SPM) loop and the Dual Sidecar architecture (Judge #6 + Jetski) as defined in the "Omega Protocol" update. This provides a rigorous 4-iteration code generation loop with browser-based reality checks ("Jetski") and governance gating ("Judge #6").

## Proposed Changes

### Jetski Sidecar (Browser Automation)

#### [NEW] [src/jetski/browser_engine.py](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/src/jetski/browser_engine.py)

- Implements `JetskiEngine` using Selenium Wire and Chrome CDP.
- Capabilities: Endpoint verification, Page rendering, Network interception.

#### [NEW] [src/jetski/server.py](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/src/jetski/server.py)

- FastAPI interface for the Jetski engine.
- Endpoints: `/verify/endpoint`, `/verify/render`, `/intercept`.

#### [NEW] [jetski.Dockerfile](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/jetski.Dockerfile)

- Dockerfile for the Jetski sidecar (Python 3.11 + Chrome + ChromeDriver).

#### [NEW] [requirements-jetski.txt](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/requirements-jetski.txt)

- Dependencies: `selenium-wire`, `selenium`, `fastapi`, `uvicorn`, `requests`.

### Governance Sidecar (Judge #6 + SPM)

#### [MODIFY] [src/governance/voting/spm_engine.py](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/src/governance/voting/spm_engine.py)

- Implement `SPMEngine` to orchestrate the 4-iteration loop.
- Integrate `Jetski` (via API calls to sidecar) and `GCA_Core` (Vertex AI).

#### [MODIFY] [src/governance/memory/memory_bank.py](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/src/governance/memory/memory_bank.py)

- Update to use Firestore for persistent rule storage.

#### [MODIFY] [src/governance/mcp_server.py](file:///Users/pikeymickey/aiyou-stack/ShadowTag-v2/src/governance/mcp_server.py)

- Expose `execute_omega_loop` and `health_check`.
- Bind to proper Cloud Run port.

## Verification Plan

### Automated Tests

- Verify `jetski.Dockerfile` builds (if Docker available).
- Run `tests/test_omega.py` (to be created) to mock-execute the loop.
