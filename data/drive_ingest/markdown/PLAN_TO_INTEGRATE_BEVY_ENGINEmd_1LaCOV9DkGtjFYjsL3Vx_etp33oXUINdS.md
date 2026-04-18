# PLAN TO INTEGRATE BEVY ENGINE
## Detailed Roadmap for Claude Agent SDK + Bevy Integration

**Project**: PNKLN Multi-Agent System + rust_scriptbots/Bevy
**Objective**: Enable AI agents to control and interact with Bevy game entities in real-time
**Timeline**: 4-6 weeks (with 3 agents working in parallel)

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Phase 1: Foundation](#phase-1-foundation)
4. [Phase 2: Core Integration](#phase-2-core-integration)
5. [Phase 3: Advanced Features](#phase-3-advanced-features)
6. [Phase 4: Production Hardening](#phase-4-production-hardening)
7. [Checkpoints & Gates](#checkpoints--gates)
8. [Risk Mitigation](#risk-mitigation)

---

## Executive Summary

### Goals
1. ✅ Create Bevy plugin (`ClaudeAgentPlugin`) enabling agent-to-game communication
2. ✅ Implement bidirectional message passing between Python/TypeScript agents and Rust/Bevy
3. ✅ Enable agents to spawn entities, update components, and query game state
4. ✅ Maintain 98%+ test coverage per Judge #6 protocol
5. ✅ Deploy to production with ATP 5-19 compliance

### Success Metrics
- **Performance**: Agent commands processed in <16ms (60 FPS game loop)
- **Reliability**: 99.9% uptime for agent-game communication
- **Coverage**: 98%+ test coverage across all integration code
- **Scalability**: Support 100+ concurrent agents controlling entities

### High-Level Approach
```
┌─────────────────┐
│ Claude Agent    │ (Python/TypeScript)
│ SDK             │
└────────┬────────┘
         │ REST API or GCS Agent Mail
         ▼
┌─────────────────┐
│ FastAPI         │ (Python Bridge)
│ Middleware      │
└────────┬────────┘
         │ FFI or IPC
         ▼
┌─────────────────┐
│ ClaudeAgent     │ (Rust Plugin)
│ Plugin          │
└────────┬────────┘
         │ Events & Systems
         ▼
┌─────────────────┐
│ Bevy Engine     │ (Game World)
│ ECS             │
└─────────────────┘
```

---

## Architecture Overview

### Components

#### 1. ClaudeAgentPlugin (Rust)
**Location**: `rust_scriptbots/src/plugins/claude_agent.rs`

**Responsibilities**:
- Register Bevy plugin with app
- Define `AgentCommand` event type
- Implement `process_agent_commands` system
- Handle entity spawning, component updates, state queries

**Risk Level**: RA-3 (Medium - core game integration)

---

#### 2. AgentBridge Service (Python)
**Location**: `ShadowTag-v2-fastapi-services/src/agent_bridge.py`

**Responsibilities**:
- Expose FastAPI endpoints for agent commands
- Translate JSON requests to Rust-compatible format
- Forward commands to Bevy via IPC or FFI
- Return game state to agents

**Risk Level**: RA-2 (Low - middleware layer)

---

#### 3. Agent Mail Integration (GCS)
**Location**: GCS bucket `gs://{PROJECT_ID}-pnkln-agents/agent-mail/`

**Responsibilities**:
- Asynchronous message queue for agent-to-game commands
- Persistent storage for game state snapshots
- Audit trail for all agent actions

**Risk Level**: RA-1 (Routine - cloud storage)

---

#### 4. Game State Synchronization (Rust)
**Location**: `rust_scriptbots/src/systems/agent_sync.rs`

**Responsibilities**:
- Export game state to JSON for agent consumption
- Poll Agent Mail for pending commands
- Apply commands to Bevy world
- Handle errors and conflicts (e.g., entity already deleted)

**Risk Level**: RA-3 (Medium - state management)

---

## Phase 1: Foundation
**Duration**: Week 1-2
**Owner**: WhiteCastle (WC-01) + BrownSnow (BS-02)

### Checkpoint 1.1: Architecture Design
**Owner**: WhiteCastle (WC-01)
**Risk Level**: RA-3

**Tasks**:
1. Define data model for agent commands
   ```rust
   #[derive(Debug, Clone, Serialize, Deserialize)]
   pub enum AgentCommand {
       SpawnEntity { agent_id: String, entity_type: String, position: Vec3 },
       UpdateComponent { entity_id: u64, component: String, data: serde_json::Value },
       QueryState { entity_id: Option<u64>, filter: QueryFilter },
       DeleteEntity { entity_id: u64 },
   }
   ```

2. Design Bevy plugin architecture
   - Event-driven vs. polling approach (recommend events)
   - System ordering (before/after which Bevy stages)
   - Resource management for agent state

3. Plan communication channel
   - **Option A**: REST API (FastAPI → Rust via HTTP)
   - **Option B**: GCS polling (Bevy polls Agent Mail every frame)
   - **Option C**: FFI (Python calls Rust directly via PyO3)
   - **Recommendation**: Option A (REST) for simplicity, Option C (FFI) for performance

4. Risk assessment per PRB framework
   - Document in architecture spec

**Deliverables**:
- `architecture_spec.md` with diagrams
- PRB risk analysis
- Technology selection justification

**Gate**: WhiteCastle sends architecture to OrangeCreek for review (RA-3)

---

### Checkpoint 1.2: Dependency Setup
**Owner**: BrownSnow (BS-02)
**Risk Level**: RA-2

**Tasks**:
1. Add Bevy dependencies to `rust_scriptbots/Cargo.toml`
   ```toml
   [dependencies]
   bevy = "0.12"
   serde = { version = "1.0", features = ["derive"] }
   serde_json = "1.0"
   ```

2. Add FastAPI dependencies to `ShadowTag-v2-fastapi-services/requirements.txt`
   ```txt
   fastapi==0.104.1
   uvicorn[standard]==0.24.0
   anthropic==0.7.0
   claude-agent-sdk==0.1.6
   ```

3. Configure Rust FFI bindings (if Option C selected)
   ```toml
   [lib]
   crate-type = ["cdylib"]  # For Python FFI
   ```

4. Set up development environment
   - Verify Rust + Bevy compile
   - Verify FastAPI + Claude Agent SDK work
   - Set up hot-reload for development

**Deliverables**:
- Updated `Cargo.toml`, `requirements.txt`
- Dev environment setup guide
- Compilation smoke test passing

**Gate**: Auto-approved (RA-2), logged to audit trail

---

### Checkpoint 1.3: Test Infrastructure
**Owner**: OrangeCreek (OC-03)
**Risk Level**: RA-2

**Tasks**:
1. Set up cargo-tarpaulin for Rust coverage
   ```bash
   cargo install cargo-tarpaulin
   cargo tarpaulin --out Html --output-dir ./coverage
   ```

2. Set up pytest + pytest-cov for Python coverage
   ```bash
   pip install pytest pytest-cov
   pytest --cov=src --cov-report=html
   ```

3. Define coverage targets
   - Rust: 98% minimum
   - Python: 98% minimum

4. Create example test cases
   ```rust
   #[cfg(test)]
   mod tests {
       #[test]
       fn test_agent_command_serialization() { ... }
   }
   ```

**Deliverables**:
- Coverage tools configured
- Example tests passing
- CI/CD integration (GitHub Actions or Cloud Build)

**Gate**: Auto-approved (RA-2), coverage reports generated

---

## Phase 2: Core Integration
**Duration**: Week 3-4
**Owner**: BrownSnow (BS-02) + OrangeCreek (OC-03)

### Checkpoint 2.1: ClaudeAgentPlugin Implementation
**Owner**: BrownSnow (BS-02)
**Risk Level**: RA-3

**Tasks**:
1. Implement plugin structure
   ```rust
   pub struct ClaudeAgentPlugin;

   impl Plugin for ClaudeAgentPlugin {
       fn build(&self, app: &mut App) {
           app
               .add_event::<AgentCommand>()
               .add_systems(Update, process_agent_commands);
       }
   }
   ```

2. Implement `process_agent_commands` system
   ```rust
   fn process_agent_commands(
       mut commands: Commands,
       mut events: EventReader<AgentCommand>,
       mut query: Query<(Entity, &Transform)>,
   ) {
       for event in events.read() {
           match event {
               AgentCommand::SpawnEntity { agent_id, entity_type, position } => {
                   // Spawn logic
               }
               // ... other cases
           }
       }
   }
   ```

3. Add error handling
   - Invalid entity IDs
   - Component type mismatches
   - Concurrent modification conflicts

4. Implement logging
   - Log all agent commands
   - Include agent_id, timestamp, command type

**Deliverables**:
- `claude_agent.rs` plugin code
- Unit tests for each command type
- Integration test with Bevy app

**Gate**: Coverage check by OrangeCreek (must be ≥98%)

---

### Checkpoint 2.2: FastAPI Bridge Service
**Owner**: BrownSnow (BS-02)
**Risk Level**: RA-2

**Tasks**:
1. Create FastAPI app
   ```python
   from fastapi import FastAPI
   app = FastAPI()

   @app.post("/agent/command")
   async def send_agent_command(command: AgentCommandSchema):
       # Forward to Bevy
       return {"status": "queued", "command_id": ...}
   ```

2. Define Pydantic schemas
   ```python
   class AgentCommandSchema(BaseModel):
       agent_id: str
       command_type: Literal["spawn", "update", "query", "delete"]
       payload: dict
   ```

3. Implement communication to Rust
   - **If REST**: Use HTTP client to call Rust web server
   - **If FFI**: Use ctypes/cffi to call Rust functions
   - **If GCS**: Write to Agent Mail bucket

4. Add authentication
   - API keys for agents
   - Rate limiting to prevent abuse

**Deliverables**:
- `agent_bridge.py` FastAPI service
- API documentation (auto-generated by FastAPI)
- Integration tests calling Bevy plugin

**Gate**: Auto-approved (RA-2), logged

---

### Checkpoint 2.3: Bidirectional Communication
**Owner**: BrownSnow (BS-02)
**Risk Level**: RA-3

**Tasks**:
1. Implement game state export
   ```rust
   fn export_game_state(query: Query<(Entity, &Transform, &Name)>) -> String {
       let state: Vec<EntityState> = query.iter()
           .map(|(e, t, n)| EntityState { id: e.id(), position: t.translation, name: n.clone() })
           .collect();
       serde_json::to_string(&state).unwrap()
   }
   ```

2. Create `/agent/state` endpoint
   ```python
   @app.get("/agent/state")
   async def get_game_state(entity_id: Optional[int] = None):
       state = fetch_from_bevy(entity_id)
       return {"state": state}
   ```

3. Implement polling mechanism
   - Bevy polls `/agent/commands/pending` endpoint
   - Or Bevy polls GCS Agent Mail bucket

4. Handle state updates
   - Agents query state → make decisions → send commands
   - Commands applied → state updated → agents notified

**Deliverables**:
- State export working
- Agents can query and receive state
- End-to-end test: Agent spawns entity, queries it, updates it, deletes it

**Gate**: OrangeCreek validation (RA-3), coverage ≥98%

---

## Phase 3: Advanced Features
**Duration**: Week 5
**Owner**: WhiteCastle (WC-01) + BrownSnow (BS-02)

### Checkpoint 3.1: Multi-Agent Coordination
**Owner**: WhiteCastle (WC-01)
**Risk Level**: RA-3

**Tasks**:
1. Design conflict resolution
   - Two agents try to control same entity → priority system
   - Agent deletes entity another agent is using → graceful degradation

2. Implement agent registry in Bevy
   ```rust
   #[derive(Resource)]
   struct AgentRegistry {
       agents: HashMap<String, AgentMetadata>,
   }
   ```

3. Add agent permissions
   - Agent A can only control entities it spawned
   - Admin agents can control all entities

4. Implement entity ownership
   - Track which agent owns which entity
   - Prevent unauthorized modifications

**Deliverables**:
- Conflict resolution design doc
- Multi-agent tests (3 agents interacting simultaneously)
- Permission system implemented

**Gate**: Architecture review by OrangeCreek (RA-3)

---

### Checkpoint 3.2: Performance Optimization
**Owner**: BrownSnow (BS-02)
**Risk Level**: RA-3

**Tasks**:
1. Benchmark current performance
   - Measure command processing latency
   - Target: <16ms (60 FPS)

2. Optimize hot paths
   - Use parallel systems where possible
   - Minimize allocations in `process_agent_commands`

3. Implement command batching
   - Instead of processing commands one-by-one, batch them
   - Process all commands in single frame

4. Add performance monitoring
   - Log slow commands (>5ms)
   - Alert if latency exceeds threshold

**Deliverables**:
- Performance benchmarks
- Optimization applied
- Latency <16ms achieved

**Gate**: OrangeCreek performance validation (RA-3)

---

### Checkpoint 3.3: Advanced Agent Capabilities
**Owner**: BrownSnow (BS-02)
**Risk Level**: RA-2

**Tasks**:
1. Implement complex queries
   ```rust
   AgentCommand::QueryState {
       filter: QueryFilter::All(vec![
           Filter::HasComponent("Transform"),
           Filter::InRadius { center: Vec3::ZERO, radius: 10.0 },
       ])
   }
   ```

2. Add event subscriptions
   - Agents subscribe to events (e.g., "entity spawned", "entity destroyed")
   - Bevy sends notifications to Agent Mail

3. Implement agent vision/perception
   - Agents "see" only entities within range
   - Implement raycasting for line-of-sight

4. Add scripting support
   - Agents can upload Lua/Python scripts to run in Bevy
   - Scripts control entities without constant API calls

**Deliverables**:
- Advanced query support
- Event subscription system
- Vision/perception system
- Scripting engine integrated (optional)

**Gate**: Auto-approved (RA-2), logged

---

## Phase 4: Production Hardening
**Duration**: Week 6
**Owner**: OrangeCreek (OC-03) + All Agents

### Checkpoint 4.1: Security Hardening
**Owner**: OrangeCreek (OC-03)
**Risk Level**: RA-4 (Human Approval Required)

**Tasks**:
1. Security audit
   - Input validation (prevent code injection)
   - Rate limiting (prevent DoS)
   - Authentication (API keys, OAuth)

2. Implement sandboxing
   - Agents can't access arbitrary file system
   - Limit CPU/memory usage per agent

3. Add audit logging
   - Log all agent actions with timestamps
   - Retain logs per ShadowTag-v2JR doctrine (RA-4 = 1 year)

4. Penetration testing
   - Attempt to exploit API endpoints
   - Verify defenses work

**Deliverables**:
- Security audit report
- Vulnerabilities patched
- Penetration test results

**Gate**: **HUMAN APPROVAL REQUIRED** (RA-4)
- Security lead reviews audit
- Approves deployment or requests fixes

---

### Checkpoint 4.2: Coverage Validation (Judge #6)
**Owner**: OrangeCreek (OC-03)
**Risk Level**: RA-4 (Human Approval Required)

**Tasks**:
1. Run full test suite
   ```bash
   cargo test --all
   cargo tarpaulin --out Html
   pytest --cov=src --cov-report=html
   ```

2. Verify coverage ≥98%
   - If below, identify gaps
   - Send back to BrownSnow for additional tests

3. Review test quality
   - Are tests meaningful or just hitting lines?
   - Are edge cases covered?

4. Generate coverage report
   - HTML report with line-by-line coverage
   - Upload to GCS for stakeholder review

**Deliverables**:
- Coverage report showing ≥98%
- Test quality assessment
- Gaps documented and addressed

**Gate**: **HUMAN APPROVAL REQUIRED** (RA-4)
- QA lead reviews coverage report
- Approves or requests more tests

---

### Checkpoint 4.3: Production Deployment
**Owner**: All Agents (Coordinated by OrangeCreek)
**Risk Level**: RA-4 (Human Approval Required)

**Tasks**:
1. Create deployment plan
   - Canary deployment (10% of users first)
   - Rollback procedure documented
   - Monitoring dashboards set up

2. Deploy to staging
   - Test in staging environment
   - Run smoke tests
   - Verify no regressions

3. Deploy to production
   - Execute canary deployment
   - Monitor metrics (latency, error rate)
   - If issues, rollback immediately

4. Post-deployment verification
   - Run end-to-end tests in production
   - Verify agents can control entities
   - Check performance metrics

**Deliverables**:
- Deployment plan document
- Staging deployment successful
- Production deployment successful (or rolled back if issues)

**Gate**: **HUMAN APPROVAL REQUIRED** (RA-4)
- Operations lead approves production deployment
- Signs off on rollback plan

---

## Checkpoints & Gates

### Summary Table

| Phase | Checkpoint | Owner | Risk Level | Human Approval? | Estimated Duration |
|-------|------------|-------|------------|-----------------|-------------------|
| 1 | Architecture Design | WC-01 | RA-3 | Review | 3 days |
| 1 | Dependency Setup | BS-02 | RA-2 | No | 1 day |
| 1 | Test Infrastructure | OC-03 | RA-2 | No | 1 day |
| 2 | ClaudeAgentPlugin | BS-02 | RA-3 | Review | 4 days |
| 2 | FastAPI Bridge | BS-02 | RA-2 | No | 2 days |
| 2 | Bidirectional Comm | BS-02 | RA-3 | Review | 3 days |
| 3 | Multi-Agent Coord | WC-01 | RA-3 | Review | 3 days |
| 3 | Performance Opt | BS-02 | RA-3 | Review | 2 days |
| 3 | Advanced Capabilities | BS-02 | RA-2 | No | 2 days |
| 4 | Security Hardening | OC-03 | RA-4 | **YES** | 3 days |
| 4 | Coverage Validation | OC-03 | RA-4 | **YES** | 2 days |
| 4 | Production Deploy | All | RA-4 | **YES** | 2 days |

**Total Estimated Duration**: 28 days (4 weeks)

**Critical Path**: Phase 1 → Phase 2 → Phase 4 (cannot parallelize these)

**Parallelizable**: Phase 3 tasks can run in parallel with Phase 2 cleanup

---

## Risk Mitigation

### Risk 1: Performance Bottleneck
**Probability**: 30%
**Impact**: High (game lags, poor user experience)
**Mitigation**:
- Benchmark early and often
- Implement command batching
- Use parallel systems in Bevy
- Set <16ms latency target from start

**Contingency**: If performance inadequate, move to async processing (agents don't get instant feedback, but game stays smooth)

---

### Risk 2: Coverage Below 98%
**Probability**: 20%
**Impact**: Moderate (Judge #6 blocks deployment)
**Mitigation**:
- Write tests alongside code (TDD)
- OrangeCreek reviews coverage at each checkpoint
- Allocate extra time for test writing

**Contingency**: Request coverage exemption (RA-4 approval) for specific files with rationale

---

### Risk 3: Security Vulnerabilities
**Probability**: 15%
**Impact**: Critical (code injection, data breach)
**Mitigation**:
- Input validation on all endpoints
- Rate limiting
- Security audit in Phase 4
- Penetration testing before production

**Contingency**: Delay production deployment until vulnerabilities patched

---

### Risk 4: Agent Coordination Conflicts
**Probability**: 25%
**Impact**: Moderate (agents interfere with each other)
**Mitigation**:
- Design conflict resolution in Phase 3.1
- Implement entity ownership
- Test multi-agent scenarios

**Contingency**: Limit to single agent per entity in v1, add multi-agent in v2

---

### Risk 5: Bevy Version Incompatibility
**Probability**: 10%
**Impact**: High (plugin doesn't work with existing codebase)
**Mitigation**:
- Lock Bevy version in Cargo.toml
- Test against rust_scriptbots early
- Document required Bevy version

**Contingency**: Fork rust_scriptbots if version upgrade needed

---

## Success Criteria

### Phase 1 Success
- [ ] Architecture approved by OrangeCreek
- [ ] Dependencies installed and compiling
- [ ] Test infrastructure set up

### Phase 2 Success
- [ ] Agent can spawn entity in Bevy
- [ ] Agent can query entity state
- [ ] Agent can update entity components
- [ ] Agent can delete entity
- [ ] Coverage ≥98% for all integration code

### Phase 3 Success
- [ ] Multiple agents coordinate without conflicts
- [ ] Command processing <16ms (60 FPS)
- [ ] Advanced queries working (filters, subscriptions)

### Phase 4 Success
- [ ] Security audit passed
- [ ] Coverage ≥98% validated by Judge #6
- [ ] Production deployment successful
- [ ] No P0/P1 incidents in first week

---

## Post-Launch

### Week 7-8: Monitoring & Iteration
1. Monitor production metrics
   - Latency, error rate, user feedback
2. Address P2/P3 bugs
3. Gather feature requests
4. Plan v2 enhancements

### Future Enhancements (v2)
1. Multi-agent collaborative control (multiple agents control one entity)
2. Agent learning from game state (reinforcement learning)
3. Natural language commands ("spawn a red cube at origin")
4. 3D visualization of agent decision-making

---

## Resources

### Documentation
- [Bevy ECS Guide](https://bevyengine.org/learn/book/getting-started/ecs/)
- [Claude Agent SDK Docs](https://docs.anthropic.com/en/api/agent-sdk)
- [AGENTS.md](./AGENTS.md) - Agent registry
- [ShadowTag-v2JR_DOCTRINE.md](./ShadowTag-v2JR_DOCTRINE.md) - Governance framework

### Tools
- `cargo-tarpaulin`: Code coverage for Rust
- `pytest-cov`: Code coverage for Python
- `cargo-flamegraph`: Performance profiling
- `hey` or `wrk`: Load testing for FastAPI

### Contacts
- **Architecture Questions**: WhiteCastle (WC-01)
- **Implementation Help**: BrownSnow (BS-02)
- **Coverage/Security**: OrangeCreek (OC-03)
- **Human Approvals**: Operations Lead (see PREFLIGHT_CHECKLIST.md)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-14
**Estimated Completion**: 4-6 weeks from start
