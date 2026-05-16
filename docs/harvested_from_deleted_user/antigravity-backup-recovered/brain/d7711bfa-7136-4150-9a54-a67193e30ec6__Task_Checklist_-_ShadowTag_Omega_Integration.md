# Task Checklist - ShadowTag Omega Integration

- [x] **Phase 9: Kosmos Integration & Project ID Correction** (COMPLETE)
    - [x] Backend (`judge-sentinel`) Live -> **UPDATED v2 (Governance)**.
    - [x] Frontend (`shadowtag-web`) Live.
    - [x] Governance ("17-Layer Shield") Installed.

- [x] **Phase 10: Ingestion Pipeline Implementation**
    - [x] Create [ingest.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/judge-sentinel/routers/ingest.py) Router (Upload Endpoint).
    - [x] Implement [cloud_operations.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/judge-sentinel/cor/cloud_operations.py) (GCS/Artifact Registry).
    - [x] Wire [risk_router.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/judge-sentinel/risk_router.py) (Governance Check).
    - [x] Deploy Updated Backend (`judge-sentinel`) to Cloud Run.
    - [x] Implement Frontend Upload UI ([IngestTerminal.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/IngestTerminal.tsx)).
    - [x] **Current Status:** Backend LIVE. Frontend Deploying.
    - [ ] Deploy Update to Cloud Run (`judge-sentinel`).
    - [ ] Build Frontend Upload UI (`shadowtag-web`).

- [x] **Phase 11: The Pitch Deck Engine (The "Money" Feature)**
    - [x] Implement [deck_generator.py](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/judge-sentinel/agents/deck_generator.py) (Gemini Pro Vision Logic).
    - [x] Add `/generate-deck` Endpoint to `judge-sentinel`.
    - [x] Create [DeckViewer.tsx](file:///Users/pikeymickey/ShadowTag-v2-stack/ShadowTag-v2/apps/shadowtag-web/components/DeckViewer.tsx) in Frontend.
    - [x] **Status:** DEPLOYED & LIVE.
    - [x] **Goal:** Generate the "Isometric Cube" Slide 1 automatically.
- [ ] **Phase 12: Wiring the Nervous System (Model Verification)**
    - [x] **CRITICAL:** Identify Valid Gemini 3 Model ID (`gemini-3-flash-preview`).
    - [x] Update Backend Code (`judge-sentinel`) to use Verified ID.
    - [/] Deploy Fixed Backend to Cloud Run. (Build `6a857e13` Launched).
    - [ ] Verify End-to-End Pitch Deck Generation.
    - [ ] **Status:** STALLED at Deployment Verification due to Protocol Handover.

- [ ] **Phase 13: The Developer Knowledge Brain**
    - [ ] Implement Developer Knowledge API as Source of Truth.
    - [ ] Index Google Documenation (Firebase, Android, Cloud).
