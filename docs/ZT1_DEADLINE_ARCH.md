# AiYou Design Process: ZT.1 (Zero-Touch Legal Deadline Management)

## 1. Executive Proposal & AiYouJR Alignment
- **Concept:** Automated extraction and calendaring of legal deadlines from raw filings.
- **Purpose (AiYouJR):** Highly aligned. Reduces human cognitive load, fits perfectly into the "Agentic Trade" ecosystem where agents manage the timeline while humans manage the strategy.
- **Reasons (Doctrine):** Leverages our existing `Zero-Drift Semantic Extraction` and the `PgRagGraph`. The "27-Year Legal Persona" is uniquely suited to identify jurisdiction-specific timeline triggers from dense Material Exhibits.

## 2. Army Risk Management (The Brakes) & Pre-Mortem
**[OBJECTION FLAGGED]: The term "Zero-Touch" is structurally dangerous and violates catastrophic risk thresholds.**
- **Failure Mode 1 (Malpractice Default):** The AI extracts "30 days from service" as June 10th, failing to account for a local jurisdiction court holiday on June 9th which pushes the deadline to June 11th, or worse, misidentifying the trigger date entirely.
- **Failure Mode 2 (Context Collapse):** The AI misses an amended scheduling order buried in a 400-page consolidated filing.
- **Mitigation (Required Brakes):** We cannot deploy this as truly "Zero-Touch." It must be deployed as **Agent-Drafted, Human-Verified**. The system extracts the dates, cites the *exact* paragraph from the Material Exhibit (Zero-Drift), and queues it. A human attorney clicks "Approve" to commit it to the firm's master docket.

## 3. The Test Architect (Gemini 3.1 Pro)
*Before writing any integration endpoints, we define the validation gates for ZT.1.*

### TDD Requirements:
1. **Mock Filing Ingestion:** Simulate submitting a Federal Court summons via the `aiyou_ingest` MCP.
2. **Zero-Drift Assertion Check:** The test must query the agent (`/agent/query`) for deadlines. The agent must return a strict JSON payload containing: `[Deadline Date]`, `[Trigger Event]`, `[Exhibit Citation ID]`.
3. **Hallucination Trap:** Pass a document with NO deadlines. The test must assert the model returns an empty array, NOT a fabricated standard 30-day response.
4. **Jurisdictional Overlay Test:** Pass a prompt defining local rules (e.g., "Exclude weekends from 5-day calculations"). Assert the date math executes correctly against the local rule overlay.

## 4. Implementation Status (2026-03-23)

| Component | File | Status |
|---|---|---|
| Jurisdiction Engine | `control/pnkln/pnkln_core/engines/jurisdiction.py` | ✅ Built |
| Legal Agent | `control/pnkln/pnkln_core/agents/legal.py` | ✅ Built |
| FastAPI Router | `apps/aiyou_stack/aiyou-fastapi-services/zt_legal_router.py` | ✅ Built |
| DB Migration | `infra/migrations/002_zt_legal.sql` | ✅ Built |
| TDD Gates (all 4) | `tests/test_zt_legal.py` | ✅ Built |
| MCP Tools | `.mcp.json` → `zt-legal` server | ✅ Built |

**Register router in main app:**
```python
from zt_legal_router import router as zt_router
app.include_router(zt_router)
```

**Run migration:**
```bash
psql $DATABASE_URL -f infra/migrations/002_zt_legal.sql
```

**Run tests:**
```bash
pytest tests/test_zt_legal.py -v
```

**Data flow:**
```
Filing (raw_text)
  → POST /api/v1/zt/matters/{id}/ingest
  → legal.extract_deadlines_from_filing()  [zero_cpu_router → ANE/kvcached]
  → deadline_extractions (status: pending_approval)
  → GET /api/v1/zt/matters/{id}/queue
  → Attorney reviews Zero-Drift citations
  → POST /api/v1/zt/extractions/{id}/approve
  → deadline_extractions (status: approved)
  → fn_schedule_reminders() fires -30d/-14d/-7d/-1d
  → GET /api/v1/zt/matters/{id}/docket
```

**MVP scope:** FRCP federal baseline.
**Next:** SDNY, CDCA, and remaining 50-state local rules via `jurisdiction_holidays` table.

## 5. Valuation / CTO Feasibility Verdict
The Claude valuation projection ($10M-$300M+) is economically accurate *if* the risk is mitigated. Deadlines are the highest-liability surface in a law firm.
- **Recommendation:** Build ZT.1 as a premium modular capability on top of the AiYou Postgres graph. Start with Federal Court (FRCP) as the MVP baseline before expanding to the fragmented 50-state local rules.
