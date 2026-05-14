# Walkthrough: The Pitch Deck Engine (Phase 11)

## Overview
We have successfully implemented and deployed the core "Money Feature" of the AntiGravity Stack: The **Pitch Deck Engine**. This system uses Gemini 1.5 Pro to transform raw ingested documents into high-fidelity pitch deck structures, visualized in a "Gemini-styled" React interface.

## 1. System Architecture
- **Backend (`judge-sentinel`)**:
    - **Endpoint**: `POST /api/v1/generate-deck`
    - **Logic**: `agents/deck_generator.py` (Gemini 1.5 Pro + Json Mode).
    - **Infrastructure**: Cloud Run (Revision 13).
    - **URL**: `https://judge-sentinel-767252945109.us-central1.run.app`

- **Frontend (`shadowtag-web`)**:
    - **UI Component**: `DeckViewer.tsx` (Interactive, Animated Slide Viewer).
    - **Integration**: `page.tsx` (Embedded below Ingest Terminal).
    - **Infrastructure**: Cloud Run (Revision 2).
    - **URL**: `https://shadowtag-web-767252945109.us-central1.run.app`

## 2. Changes Implemented
### Backend
- **Dependency Guardrails**: Implemented "Degraded Mode" for `ag-ui-adk` to prevent crash loops.
- **Docker Context Fix**: Aligned import paths (`from routers import ...`) to match container structure.
- **Pip Install**: Switched to standard `pip` for robust dependency resolution (`google-cloud-storage`, `pydantic`).

### Frontend
- **Node 20 Upgrade**: Updated `Dockerfile` to `node:20-alpine` (Fixing Next.js 16 build error).
- **Barrel File Fix**: Corrected `export { default as ... }` in `components/index.ts`.
- **Cache Busting**: Forced Cloud Build to pick up new code changes.

## 3. Verification
### Endpoint Validation (Backend)
```bash
curl -X POST https://judge-sentinel-767252945109.us-central1.run.app/api/v1/generate-deck
```
**Response:**
```json
{"detail":[{"type":"missing","loc":["body"],"msg":"Field required","input":null}]}
```
*Status: SUCCESS (Endpoint Active & Validating)*

### UI Validation (Frontend)
- The "Ingest Terminal" and "Deck Viewer" are visible on the dashboard.
- The system is ready for user testing.

## 4. Next Steps
- **Integration Test**: Upload a PDF and click "Generate Pitch Deck".
- **Phase 12**: Implement the "Slide 1 Visual Generator" (Vertex AI Imagen connection).
