# BullMQ → Cloud Tasks + Pub/Sub Migration Specification
## PNKLN BIOS/Kosmos Serverless Purity Compliance

**Status:** PENDING
**Doctrine Violation:** BullMQ requires persistent Redis, violating Cloud Run ONLY mandate
**Resolution:** Port all BullMQ patterns to Cloud Tasks + Pub/Sub
**Effort:** ~2-3 weeks
**Risk:** LOW (patterns map cleanly; no functionality loss)

---

## 1. Current BullMQ Architecture (TO BE REPLACED)

```
BIOS/Kosmos Research Pipeline:
  User Request → BullMQ Queue → Redis (persistent) → BullMQ Worker → Result
                                    ↑
                              DOCTRINE VIOLATION
                        (requires persistent Redis,
                         not serverless, not Cloud Run)
```

### BullMQ Components in Use:
- **research-queue**: Deep Research Plan→Execute→Refine cycles
- **literature-queue**: Fast/Deep literature search jobs
- **analysis-queue**: Python code execution + data analysis
- **novelty-queue**: Hypothesis novelty evaluation
- **Bull Board**: Dashboard for job monitoring
- **WebSocket notifications**: Real-time progress to clients

---

## 2. Target Architecture (Cloud Tasks + Pub/Sub)

```
BIOS/Kosmos Research Pipeline (Serverless):
  User Request → Cloud Tasks Queue → Cloud Run Service (triggered by Pub/Sub) → Result
                       ↓
                  Firestore (job state)
                       ↓
                  Pub/Sub (progress events → Eventarc → SSE to client)
```

### Migration Map:

| BullMQ Component | Cloud Tasks + Pub/Sub Equivalent | Notes |
|---|---|---|
| `new Queue('research')` | `cloudTasks.createQueue({name: 'research'})` | Direct mapping |
| `new Worker('research', handler)` | Cloud Run service with Pub/Sub trigger | Event-driven, scale-to-zero |
| `queue.add('job', data)` | `cloudTasks.createTask({queue, httpRequest})` | HTTP target = Cloud Run URL |
| `job.progress(50)` | Pub/Sub publish to `research-progress` topic | Push subscription to SSE endpoint |
| `job.getState()` | Firestore doc `jobs/{jobId}` | Read current state |
| `queue.getCompleted()` | Firestore query `where('state', '==', 'completed')` | Index on state field |
| Bull Board dashboard | Cloud Tasks console + custom Cloud Run dashboard | Built-in GCP monitoring |
| `job.retry()` | Cloud Tasks retry config (exponential backoff) | `maxRetryDuration`, `minBackoff`, `maxBackoff` |
| WebSocket notifications | Eventarc → Cloud Run SSE endpoint | Or Pub/Sub push to client webhook |

---

## 3. Implementation Plan

### Week 1: Core Infrastructure
1. Create Cloud Tasks queues (research, literature, analysis, novelty)
2. Create Pub/Sub topics (research-progress, literature-progress, analysis-progress, novelty-progress)
3. Create Firestore collection `jobs` with schema:
   ```json
   {
     "jobId": "string",
     "queue": "string",
     "state": "pending|active|completed|failed",
     "data": {},
     "result": {},
     "progress": 0-100,
     "createdAt": "timestamp",
     "updatedAt": "timestamp",
     "retryCount": 0,
     "error": null
   }
   ```
4. Deploy Cloud Run services for each worker (research-worker, literature-worker, analysis-worker, novelty-worker)

### Week 2: Agent Migration
1. Port Planning Agent to Cloud Tasks trigger pattern
2. Port Literature Agent (Fast + Deep modes) with appropriate timeout configs
   - Fast mode: 30s timeout
   - Deep mode: 300s timeout (full-text PDF processing)
3. Port Data Analysis Agent with persistent knowledge base writes to Firestore
4. Port Novelty Detection Agent

### Week 3: Integration & Testing
1. Wire Pub/Sub progress events to SSE endpoint for real-time client updates
2. Deploy monitoring dashboard on Cloud Run (replaces Bull Board)
3. Integration testing: full Deep Research Plan→Execute→Refine cycle
4. Load testing: verify scale-to-zero behavior and cold start latency
5. Decommission Redis/BullMQ dependencies

---

## 4. Cloud Tasks Configuration

```yaml
# research queue
queue:
  name: research
  rateLimits:
    maxDispatchesPerSecond: 10
    maxConcurrentDispatches: 5
  retryConfig:
    maxAttempts: 3
    minBackoff: 10s
    maxBackoff: 300s
    maxDoublings: 3

# literature queue (higher throughput for Fast mode)
queue:
  name: literature
  rateLimits:
    maxDispatchesPerSecond: 50
    maxConcurrentDispatches: 20
  retryConfig:
    maxAttempts: 5
    minBackoff: 5s
    maxBackoff: 60s
```

---

## 5. Cost Comparison

| Component | BullMQ + Redis (Current) | Cloud Tasks + Pub/Sub (Target) |
|---|---|---|
| Redis (Memorystore) | $73/mo (basic, 1GB) | $0 (eliminated) |
| VM/GKE for workers | $50-200/mo (persistent) | $0 (Cloud Run scale-to-zero) |
| Cloud Tasks | N/A | ~$0.40/million tasks |
| Pub/Sub | N/A | ~$40/TB messages |
| Firestore (job state) | N/A | ~$0.06/100K reads |
| **Total** | **$123-273/mo** | **< $5/mo at current scale** |

Savings: $118-268/mo = $1,416-3,216/yr

---

## 6. Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Cloud Run cold starts on worker services | MEDIUM | Set min-instances=1 for research-worker (critical path) |
| Firestore consistency for rapid state updates | LOW | Use transactions for state transitions |
| Deep mode timeout (300s) exceeds Cloud Tasks default | LOW | Set `dispatchDeadline` to 1800s for literature queue |
| Loss of Bull Board monitoring UX | LOW | Build lightweight Cloud Run dashboard or use GCP console |

---

## 7. Doctrine Compliance Verification

After migration:
- [ ] Zero Redis dependencies
- [ ] Zero persistent VMs or GKE nodes
- [ ] All workers on Cloud Run (source-based deploy)
- [ ] git push → deployed
- [ ] Scale-to-zero when idle
- [ ] Cloud Run ONLY doctrine: COMPLIANT ✓
