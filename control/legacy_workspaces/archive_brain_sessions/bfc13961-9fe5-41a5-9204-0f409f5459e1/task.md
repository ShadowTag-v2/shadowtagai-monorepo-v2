# Task List: ShadowTag Omega (PNKLN Google-Native Refinement)

## ⟿ Status: Active
**Current Objective:** Implement the "Ultrathink" Google-Native Security Stack (Zero Outside Vendors).

## [ ] Phase 1: Planning & Context Shift
- [x] Analyze "Ultrathink" directive (Replace DTEX, Hive, etc. with GCP Native).
- [ ] Update `GEMINI.md` with new "Zero Vendor" Doctrine.
- [ ] Create `implementation_plan.md` for the 12 new agents.

## [ ] Phase 2: Agent Implementation (The "Dirty Dozen")
- [ ] **1. Base Cyber + UEBA**: Implement `vertex_ueba_agent.py` (Chronicle + Gemini).
- [ ] **2. Safety**: Implement `suicide_prevention_filter.py` (Vertex AI Safety).
- [ ] **3. Deepfake**: Implement `deepfake_detector.py` (Vision + Video Intel).
- [ ] **4. Watermarking**: Implement `watermark_service.py` (SynthID).
- [ ] **5. Minor Protection**: Implement `minor_protection.py` (Behavioral + Cloud Armor).
- [ ] **6. EU Compliance**: Implement `eu_ai_act_compliance.py` (Logging + BigQuery).
- [ ] **7. Business Logic**: Implement `monte_carlo_risk.py` (BigQuery + Numpy).
- [ ] **8. VPN Detection**: Implement `vpn_detection.py` (Cloud IDS + Threat Intel).
- [ ] **9. Zero Trust**: Implement `zero_trust_enforcer.py` (Access Context Manager).
- [ ] **10. KYB/KYE**: Implement `kyb_kye_agent.py` (Public API Agents).
- [ ] **11. Supply Chain**: Implement `supply_chain_agent.py` (Vision + Maps).
- [ ] **12. Harassment**: Implement `harassment_detector.py` (DLP + Gemini).

## [ ] Phase 3: Infrastructure & Deployment
- [ ] Update `requirements.txt` with new GCP libs (google-cloud-videointelligence, etc.).
- [ ] Create/Update `Dockerfile` for the unified or microservice build.
- [ ] Create `deploy-all.sh` script.
- [ ] Configure `cloudbuild.yaml` for the new stack.

## [ ] Phase 4: Verification ("God Mode")
- [ ] Verify Build.
- [ ] Deploy to Cloud Run.
- [ ] Run `scripts/verify_god_mode.sh` (updated for new agents).
