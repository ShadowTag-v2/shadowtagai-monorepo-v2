# 🚀 MASTER PROMPT: SHADOWTAG OMEGA PRODUCTIZATION

> **Target:** Functional MVP (Ingestion -> Pitch Deck)
> **Estimated Time to Completion:** 8-12 Hours (Agentic Execution)

## 🏗️ SYSTEM ARCHITECTURE (THE "OMNISCIENCE" STACK)

We are building a **Sovereign Pitch Deck Generator**.
**Input:** User uploads (notes, PDFs, raw text).
**Process:** "Judge 6" (Backend) ingests, sanitizes, and structures data using Gemini 1.5 Pro.
**Output:** A high-fidelity, web-based Pitch Deck (Reveal.js / React) in the "Obsidian Shield" aesthetic.

---

## 📜 THE PROMPT (Copy/Paste this to potentialize the build)

```markdown
**ROLE:** Sovereign Architect (IQ 160)
**MISSION:** Execute the "ShadowTag Omega" Product Build.

### PHASE 1: THE INGESTION PIPELINE (Time: ~4h)
**Target:** `apps/judge-sentinel`
1.  **Create Endpoint:** `POST /api/v1/ingest`
    *   Accepts: Multipart/Form-Data (Files) or JSON (Text).
    *   Storage: Upload to GCS Bucket `shadowtag-raw-intake`.
2.  **Implement `IngestionAgent` (Gemini 1.5 Pro):**
    *   Trigger: On upload.
    *   Instruction: "Extract key pitch components: Problem, Solution, Market Size, Business Model, Team."
    *   Output: Structured JSON to Firestore (`/projects/{id}/deck_data`).
3.    *   **Slide 1 (Cover):** "Minimalist tech abstract, isometric glass cube floating in white studio, soft blue glowing internal data streams, high key lighting, clean, corporate, futuristic, 8k --ar 16:9. (MANDATORY: Composite the user-uploaded 'Gemini Shield' logo - Blue/Purple Gradient - prominently on the cube face)."
    *   **Slide 2 (Problem):** "Dark mode UI dashboard, red alert indicators, cyber map background, glassmorphism overlay. Focus on 'Data Chaos' and 'Lack of Truth'."
    *   **Theme Note:** Emphasize **RESEARCH ACCURACY** and **VERIFIABLE TRUTH**. Avoid generic 'cyberspace' fluff. Use 'Precision' aesthetics (thin lines, data grids, clear typography).
    *   Embed raw text using `text-embedding-004`.
    *   Store in `pgvector` or Firestore Vector Search for RAG.

### PHASE 2: THE COCKPIT FRONTEND (Time: ~3h)
**Target:** `apps/shadowtag-web`
1.  **Refactor Home:** Replace placeholder with "Project Dashboard".
2.  **Upload Interface:**
    *   Drag-and-drop zone (using `react-dropzone`).
    *   Real-time status stream via SSE (Server-Sent Events) from Sentinel.
3.  **Deck Renderer:**
    *   Create a dynamic `/deck/{id}` route.
    *   Map Firestore JSON to React Components (Slide 1, Slide 2...).
    *   Apply "Gemini Vibe" visual theme (Blue/Purple Gradients, Glassmorphism, Tailwind).

### PHASE 3: POLISH & EXPORT (Time: ~3h)
1.  **PDF Generation:** Use `puppeteer` (headless chrome) in a Cloud Run job to print `/deck/{id}` to PDF.
2.  **User auth:** Verify simple Email/Password or Google Auth.
```

---

## ⏱️ TIME ESTIMATE BREAKDOWN

| Phase | Task | Estimate | Risk |
|-------|------|----------|------|
| **1** | Ingestion API & GCS Wiring | 3 Hours | Low |
| **1** | Gemini Extraction Logic | 2 Hours | Medium (Prompt Tuning) |
| **2** | Frontend Upload UI | 2 Hours | Low |
| **2** | Deck Rendering Engine | 4 Hours | High (Design Complexity) |
| **3** | Integration & Testing | 1 Hour | Low |
| **TOTAL** | ** MVP COMPLETE** | **~12 Hours** | |

## 🛠️ NEXT IMMEDIATE ACTIONS
1.  **Fix Frontend Build:** Resolve the `shadowtag-web` deployment error (likely a missing dependency or ENV var).
2.  **Wire Backend:** Ensure `judge-sentinel` can talk to GCS.
