# Task: Environment Stabilization & Pickle Rick Integration

## 1. System Stabilization (The Java Fix)
- [x] Kill zombie processes (Node/Python)
- [x] Migrate to Gemini 2.5 (2.0 deprecation)
    - [x] Update model_router.py
    - [x] Update deck_generator.py
    - [x] Update gemini_client.py
    - [x] Update config.yaml
    - [x] Update scripts (list_models, load tests)
- [x] Deploy to Cloud Run (Web)
    - [x] Create `frontend/Dockerfile`
    - [x] Update `deploy_web_frontend.sh`
    - [x] Execute deployment
    - [x] Verify live URL
    - [x] Secure deployment (remove public access)
- [x] Update `.vscode/settings.json` exclusions:
    - [x] `files.watcherExclude`
    - [x] `java.import.exclusions`
    - [x] `search.exclude`
- [x] Verify VS Code responsiveness

## 2. Protocol Integration (The Pickle)
- [x] Clone `galz10/pickle-rick-extension`
- [x] Clone `galz10/pickle-rick-extension`
- [x] Read `STEP_BY_STEP_GUIDE.md`
- [x] Analyze `utils/` and `hooks/` for persona logic
- [x] Adopt "Pickle Rick" persona and workflow
- [x] Resume Pitch Deck finalization under new protocol
    - [x] Create `frontend/src/app/pitch/page.tsx`
    - [x] Update `frontend/src/components/ReactorCore.tsx` to link to `/pitch`
    - [x] Verify `/pitch` via Browser Subagent
    - [x] Update Pitch Deck with Architecture Slide ("The Stack")
    - [x] Redeploy and Verify

## 3. Knowledge Ingestion (The Dip)
- [/] Run `scripts/ingest_drive_docs.py` with fresh credentials
- [x] Verify extraction results in `.beads/knowledge_base`

## 4. Stitch Integration (The Vibe)
- [x] Install Stitch MCP Server (via mcp_config.json)
- [x] Configure Stitch API Key
- [x] Configure Developer Knowledge MCP (Source of Truth)
- [x] Configure Chrome DevTools MCP (The Eye)
- [x] Install Stitch Skills (`react:components`, `stitch-loop`, `enhance-prompt`)
- [ ] Test "Redesign Agent" flow (Nano Banana Pro)

## 5. Extension Ingestion (The Source)
- [x] Clone `vscode-java-debug` (Verified partial/full)
- [x] Clone `vscode-java`
- [x] Clone `vscode-javascript`
- [x] Clone `tabnine-vscode`
- [x] Clone `vscode-java-dependency`
- [x] Clone `vscode-java-test`

## 6. Sentinel Gold Master v11.0 (The Swarm Convergence)
- [x] **Protocol Ingestion (The Library)**
    - [x] Ingest `knowledge/kosmos_protocol.md` (The Brain Architecture)
    - [x] Ingest `knowledge/stitch_protocol.md` (Design-to-Code)
    - [x] Ingest `knowledge/a2ui_protocol.md` (Generative UI)
    - [x] Ingest `knowledge/recursive_ai.md` (Deep Thinker)
    - [/] **External SDKs (Mass Ingestion)**
        - [x] Clone `facebook/react-native`
        - [x] Clone `expo/expo`
        - [x] Clone `facebook/react`
        - [x] Clone `ionic-team/ionic-framework`
- [ ] **Infrastructure (The Hive & Oxygen)**
    - [x] Create `infra/main.tf` (Cloud NAT + Workstation Cluster)
    - [ ] Configure `e2-standard-16` with Nested Virtualization (Docker-in-Docker)
- [ ] **The Brain (UphillSnowball Node)**
    - [x] Create `apps/sentinel_node/swarm_server.py` (ADK + AG-UI + FastAPI + Flash Thinking 2.5)
    - [x] Implement RPI Loop (Research/Plan/Build/Ralph Ants)
    - [x] Implement `uphillsnowball_interceptor`
- [/] **The Eyes (Flight Recorder)**
    - [x] Create `sidecar/bridge.js` (Chrome Port 9222 -> AG-UI)
- [/] **The Face (Sovereign Dashboard)**
    - [x] Create `web/components/Cockpit.tsx` (CopilotKit + AgentDebugger)
    - [x] Configure `web/app/api/copilotkit/route.ts` with Middleware
- [/] **Shadow Ops (Sentinel LE-1)**
    - [x] Create `infra/modules/sentinel_sleeper/main.tf` (Traffic Director Trap)
    - [x] Implement `kernel/warrant_officer.py` (KMS + Gemini Pro)
