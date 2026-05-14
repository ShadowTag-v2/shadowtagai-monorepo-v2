# FM 7-8 & Ranger Handbook: Swarm Doctrine Adaptation

## 1. Organization & Structure

| Doctrine Unit | Size | Agent Swarm Equivalent | Function |
|:---|:---:|:---|:---|
| **Fire Team** | 4 | **Micro-Cluster** | Smallest autonomous unit. 1 Leader + 3 Specialists (Coder, Tester, Reviewer). |
| **Squad** | 9 | **Sub-Squad** | 2 Fire Teams + Squad Leader. Coordinates local tasks (e.g., Feature implementation). |
| **Platoon** | 40 | **Squad (Current)** | 3-4 Sub-Squads. Strategic unit (e.g., "Security Squad", "Backend Squad"). |
| **Company** | 150 | **Shift** | 3-4 Platoons. Operational unit for a 4-hour block. |

**Optimization:**
- **Current:** 24 Squads × 25 Agents = 600 Agents.
- **Proposed (Doctrine):** 25 Platoons × 24 Agents (2 Squads of 12) = 600 Agents.
- **Benefit:** Better alignment with "Span of Control" (1 leader : 3-5 subordinates).

## 2. Battle Drills (Algorithmic Translation)

### Drill 1: React to Contact (Error Handling)
**Trigger:** Exception, API Failure, Test Failure.
**Algorithm:**
1.  **Contact:** Agent logs error (Red Flare).
2.  **Suppress:** Fire Team pauses new requests to affected service.
3.  **Maneuver:** "Fix-It" agent flanks (analyzes root cause).
4.  **Assault:** Apply patch/rollback.

### Drill 2: Break Contact (Kill Switch)
**Trigger:** Cost spike (> $5/min), Security Alert (Judge#6 Alert).
**Algorithm:**
1.  **Signal:** Judge#6 broadcasts "CEASE FIRE".
2.  **Smoke:** Revoke active tokens.
3.  **Withdraw:** Terminate pods, revert to Safe Mode (Read-Only).

### Drill 6: Enter & Clear Room (Pipeline Processing)
**Trigger:** New Repo/Feature.
**Algorithm:**
1.  **Breach:** Clone & Install.
2.  **Clear Entry:** Verify Build & Lint.
3.  **Clear Room:** Run Tests & Security Scan.
4.  **Mark:** Tag as "Ready for Deployment".

## 3. Patrol Principles (Ranger Handbook)

- **Planning:** Artifact-First Protocol (`plan_*.md`).
- **Reconnaissance:** Context Index (Continuous scanning).
- **Security:** Judge#6 (360-degree compliance).
- **Control:** Swarm Orchestrator (Chain of Command).
- **Common Sense:** LLM Reasoning (Adaptability).

## 4. Warning Order (WARNORD) Format
**Agent Tasking Protocol:**
1.  **Situation:** Current state of repo/memory.
2.  **Mission:** The Task (Who, What, When, Where, Why).
3.  **General Instructions:** Resource limits, tools allowed.
4.  **Specific Instructions:** Role assignments.
5.  **Timeline:** Deadlines and milestones.
