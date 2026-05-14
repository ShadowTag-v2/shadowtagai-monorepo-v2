# PLAN.md - Multi-Agent Coordination Roadmap

**Version:** 1.0.0
**Created:** 2025-11-29
**Owner:** PNKLN Core Stack

---

## Active Mission

Deploy military-grade multi-agent coordination system using AG2/AutoGen with AiYouJR governance enforcement.

---

## Current Phase: Phase 1 - Foundation

### Objectives
1. Establish AG2/AutoGen infrastructure
2. Deploy AiYouJR governance gates
3. Configure GCS-backed communication layer
4. Initialize Cor (Unified Brain) orchestrator

---

## Task Queue

### ACTIVE TASKS

| ID | Task | Agent | Status | Priority |
|----|------|-------|--------|----------|
| T-001 | Initialize AG2 GroupChatManager | Cor | IN_PROGRESS | CRITICAL |
| T-002 | Configure GCS buckets | NS | PENDING | HIGH |
| T-003 | Deploy Judge #6 validation | Judge | PENDING | HIGH |

### PENDING TASKS

| ID | Task | Agent | Blocked By | Priority |
|----|------|-------|------------|----------|
| T-004 | Connect existing agents to AG2 | Bridge | T-001 | HIGH |
| T-005 | Implement context consolidation | Cor | T-001 | MEDIUM |
| T-006 | Create monitoring dashboard | Ops | T-002 | MEDIUM |

### COMPLETED TASKS

| ID | Task | Agent | Completed | Duration |
|----|------|-------|-----------|----------|
| - | - | - | - | - |

---

## Agent Assignments

### Core Coordination Agents

| Agent | Role | Model | Status |
|-------|------|-------|--------|
| **Cor** | Unified Brain / Orchestrator | Gemini 2.0 Pro | Ready |
| **NS** | Nervous System / GCS Comms | GCS SDK | Ready |
| **Judge #6** | Governance Validator | Gemini 2.0 Flash | Ready |
| **YRM** | Risk Assessment | Local Rules | Ready |

### Domain Agents (from AGENTS.md)

| Agent | Purpose | Integration Status |
|-------|---------|-------------------|
| System Architect | Architecture design | Pending AG2 bridge |
| Security Scanner | Vulnerability detection | Pending AG2 bridge |
| Code Reviewer | Quality assurance | Pending AG2 bridge |
| Test Generator | Automated testing | Pending AG2 bridge |
| API Builder | Endpoint creation | Pending AG2 bridge |

---

## GCS Bucket Configuration

| Bucket | Purpose | Retention |
|--------|---------|-----------|
| `pnkln-aiyoujr-logs` | Governance audit trail | 90 days |
| `pnkln-agent-mail` | Inter-agent messages | 7 days |
| `pnkln-task-artifacts` | Task outputs/reports | 30 days |

---

## Governance Checkpoints

### Phase 1 Exit Criteria

- [ ] AG2 GroupChatManager operational
- [ ] All 3 GCS buckets created and accessible
- [ ] Judge #6 validation passing for test tasks
- [ ] YRM risk scoring functional
- [ ] At least 1 domain agent bridged to AG2

### Phase 2 Entry Requirements

- [ ] 5+ domain agents connected
- [ ] Context consolidation tested at 80% threshold
- [ ] End-to-end task execution verified
- [ ] Monitoring dashboard live

---

## Risk Register

| Risk | Level | Mitigation |
|------|-------|------------|
| AG2 version incompatibility | RA-2 | Pin versions in requirements.txt |
| GCS permission errors | RA-2 | Use service account with minimal scope |
| Context overflow | RA-3 | 80% consolidation rule |
| Agent deadlock | RA-3 | Timeout + circuit breaker |

---

## Communication Protocol

### Agent-to-Agent Messages

```json
{
  "message_id": "uuid",
  "from_agent": "agent_id",
  "to_agent": "agent_id | 'broadcast'",
  "message_type": "TASK | RESULT | STATUS | ERROR",
  "payload": {},
  "timestamp": "ISO-8601",
  "requires_ack": true
}
```

### Message Flow

```
Agent A → GCS (pnkln-agent-mail) → Cor (routes) → Agent B
                                      ↓
                              Judge #6 (validates)
                                      ↓
                              GCS (pnkln-aiyoujr-logs)
```

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| M1: Foundation Complete | Phase 1 | IN_PROGRESS |
| M2: 10 Agents Integrated | Phase 2 | PENDING |
| M3: Production Ready | Phase 3 | PENDING |
| M4: Full 44-Agent Swarm | Phase 4 | PENDING |

---

## Commands

### Start Coordination Session

```bash
# Initialize AG2 environment
python -m templates.multi_agent_coordination.init

# Start Cor orchestrator
python -m templates.multi_agent_coordination.cor --start

# Monitor agent activity
python -m templates.multi_agent_coordination.monitor
```

### Emergency Stop

```bash
# Kill all agents
python -m templates.multi_agent_coordination.cor --kill-all

# Check governance logs
gsutil cat gs://pnkln-aiyoujr-logs/latest.json
```

---

## Notes

- All tasks must pass AiYouJR gates (Purpose/Reasons/Brakes)
- RA-4 (HIGH) risks require human approval from Erik
- Context consolidation triggers at 80% usage
- Audit trail is immutable once written to GCS

---

## Next Actions

1. Complete AG2 GroupChatManager initialization (T-001)
2. Create GCS buckets with proper IAM (T-002)
3. Deploy Judge #6 validation pipeline (T-003)
4. Bridge first domain agent to AG2 (T-004)

---

**Last Updated:** 2025-11-29
**Next Review:** Upon Phase 1 completion
