# Architecture Comparison: v1.0.0 vs v2.0.0

**Visual guide to understand what's changing and why**

---

## Stack Evolution

### v1.0.0 Architecture (Current - DEPLOYED)

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Service                      │
│              (6 endpoints, auto-routing)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  PnklnOrchestrator    │
         │  (Intent Detection)   │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌────────┐            ┌──────────┐
    │ Skills │            │  Agents  │
    │   (3)  │            │   (3)    │
    └────────┘            └──────────┘
         │                       │
         ├─ research_explorer    ├─ ultrathink_designer
         ├─ design_critic        ├─ wealth_accelerator
         └─ monetization         └─ orchestrator_meta

         ▼
    ┌────────────────┐
    │  Audit Trail   │
    │ (Boy Scout)    │
    └────────────────┘
         │
         └─ Metrics: time saved, revenue identified/generated
```

**Characteristics:**

- ✓ Static prompts
- ✓ Manual skill/agent design
- ✓ Execution tracking only
- ✓ No learning/evolution
- ✓ No performance ratings
- ✓ No benchmarking

---

### v2.0.0 Architecture (Target - TO BUILD)

```
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Service                            │
│         (11 endpoints: +evolve, +ratings, +benchmark,            │
│          +frameworks, +debate)                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   PnklnOrchestrator v2.0      │
         │   (Intent + Evolution)        │
         └────────────┬──────────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ┌────────┐  ┌──────────┐  ┌──────────────┐
    │ Skills │  │  Agents  │  │  Frameworks  │
    │   (7)  │  │   (6)    │  │   (Fusion)   │
    └────────┘  └──────────┘  └──────────────┘
         │            │              │
         │            │              ├─ RTF-TAG-BAB
         │            │              ├─ CARE-RISE
         │            │              └─ PanelGPT
         │            │
         ├─ v1.0 (3) ├─ v1.0 (3)
         │            │
         └─ NEW (4):  └─ NEW (3):
            ├─ cheat_sheet    ├─ deep_reasoning (DTE)
            ├─ glicko         ├─ panel_debate (MAD)
            ├─ framework      └─ code_crafter
            └─ benchmark
                 │
                 ▼
    ┌────────────────────────────────────┐
    │      Evolution Layer (DTE)         │
    │  Debate → Train (GRPO) → Evolve    │
    └────────────────────────────────────┘
                 │
         ┌───────┴───────┐
         ▼               ▼
    ┌─────────┐    ┌──────────────┐
    │ Glicko  │    │ Benchmarks   │
    │ Ratings │    │ (Validation) │
    └─────────┘    └──────────────┘
         │               │
         │               ├─ HumanEval
         │               ├─ BigCodeBench
         │               └─ SWE-bench
         │
         ▼
    ┌────────────────────────────┐
    │    Enhanced Audit Trail    │
    │ (Boy Scout + Learning)     │
    └────────────────────────────┘
         │
         └─ Metrics: v1.0 + accuracy deltas + rating changes + benchmark scores
```

**New Characteristics:**

- ✓ Self-evolving prompts (DTE)
- ✓ Performance ratings (Glicko-2)
- ✓ Objective validation (benchmarks)
- ✓ Framework fusion (RTF-TAG-BAB-CARE-RISE)
- ✓ Multi-agent debate (PanelGPT)
- ✓ Continuous learning (GRPO training)

---

## Data Flow Comparison

### v1.0.0: Static Execution

```
User Input
    │
    ├─→ Intent Detection (keyword matching)
    │
    ├─→ Skill Selection (static registry lookup)
    │
    ├─→ Execution (prompt → LLM → response)
    │
    ├─→ Audit Logging (metrics tracking)
    │
    └─→ Response to User

[No learning, no evolution, no ratings]
```

### v2.0.0: Intelligent Execution with Learning

```
User Input
    │
    ├─→ Intent Detection (keyword + context + history)
    │
    ├─→ Skill Selection (registry + performance ratings)
    │       │
    │       └─→ Check Glicko ratings → Select highest rated
    │
    ├─→ Execution (evolved prompt → LLM → response)
    │       │
    │       └─→ Apply cheat sheet optimization
    │
    ├─→ Validation (optional benchmark testing)
    │
    ├─→ Rating Update (Glicko-2 based on performance)
    │
    ├─→ Audit Logging (enhanced metrics + learning data)
    │
    ├─→ Evolution Check (trigger DTE if threshold met)
    │       │
    │       ├─→ Debate Phase (MAD on current prompt)
    │       ├─→ Train Phase (GRPO on results)
    │       └─→ Evolve Phase (update prompts)
    │
    └─→ Response to User (with evolution metadata)

[Continuous learning, rating-driven selection, benchmark validation]
```

---

## File Structure Comparison

### v1.0.0 (Current)

```
pnkln/
├── __init__.py
├── skills/
│   └── registry.yaml                 (3 skills)
├── agents/
│   └── registry.yaml                 (3 agents)
└── core/
    ├── __init__.py
    ├── orchestrator.py              (459 lines)
    └── audit.py                     (262 lines)

api/
└── main.py                          (325 lines)

tests/
└── test_orchestrator.py             (255 lines)

docs/
├── DEPLOYMENT.md
└── TRANSFER_PACKAGE.md

Total: 9 Python files, 2 YAML files
```

### v2.0.0 (Target)

```
pnkln/
├── __init__.py
├── skills/
│   └── registry.yaml                 (7 skills) ⬅ +4 skills
├── agents/
│   └── registry.yaml                 (6 agents) ⬅ +3 agents
├── core/
│   ├── __init__.py
│   ├── orchestrator.py              (enhanced)
│   ├── audit.py                     (enhanced)
│   ├── glicko.py                    ⬅ NEW (Glicko-2 rating)
│   ├── grpo.py                      ⬅ NEW (GRPO training)
│   ├── benchmarks.py                ⬅ NEW (HumanEval/etc)
│   ├── cheatsheet.py                ⬅ NEW (Prompt optimization)
│   └── frameworks.py                ⬅ NEW (RTF-TAG-BAB-CARE-RISE)
├── evolution/                        ⬅ NEW DIRECTORY
│   ├── __init__.py
│   ├── dte.py                       ⬅ NEW (Debate-Train-Evolve)
│   ├── debate.py                    ⬅ NEW (MAD/PanelGPT)
│   └── training.py                  ⬅ NEW (GRPO orchestration)
└── validation/                       ⬅ NEW DIRECTORY
    ├── __init__.py
    ├── humaneval.py                 ⬅ NEW
    ├── bigcodebench.py              ⬅ NEW
    └── swebench.py                  ⬅ NEW

api/
└── main.py                          (enhanced: +5 endpoints)

tests/
├── test_orchestrator.py             (enhanced)
├── test_glicko.py                   ⬅ NEW
├── test_grpo.py                     ⬅ NEW
├── test_dte.py                      ⬅ NEW
├── test_benchmarks.py               ⬅ NEW
└── test_integration_v2.py           ⬅ NEW (full stack)

docs/
├── DEPLOYMENT.md
├── TRANSFER_PACKAGE.md
├── EVOLUTION_V2.md                  ⬅ NEW
├── RESTART_PROMPT_V2.md             ⬅ NEW
└── ARCHITECTURE_COMPARISON.md       ⬅ NEW (this file)

Total: 23 Python files, 2 YAML files
```

**New additions:** +14 Python files, 8 categories of new functionality

---

## Skill Evolution Detail

### v1.0.0 Skills

| ID                          | Name                   | Category | Frameworks    | Purpose               |
| --------------------------- | ---------------------- | -------- | ------------- | --------------------- |
| `research_explorer_v1`      | Research Explorer      | Research | CoT, RCR, ToT | Deep exploration      |
| `design_critic_v1`          | Design Critic          | Design   | RCR, MAD      | Jobs-aesthetic review |
| `monetization_architect_v1` | Monetization Architect | Business | CoT, RCR      | Revenue architecture  |

### v2.0.0 Skills (All 7)

| ID                          | Name                   | Category   | Frameworks            | Purpose                             | NEW?      |
| --------------------------- | ---------------------- | ---------- | --------------------- | ----------------------------------- | --------- |
| `research_explorer_v1`      | Research Explorer      | Research   | CoT, RCR, ToT         | Deep exploration                    | No        |
| `design_critic_v1`          | Design Critic          | Design     | RCR, MAD              | Jobs-aesthetic review               | No        |
| `monetization_architect_v1` | Monetization Architect | Business   | CoT, RCR              | Revenue architecture                | No        |
| `cheat_sheet_fusion_v1`     | Cheat Sheet Fusion     | Prompts    | DTE                   | Evolved prompt optimization (21→10) | ✓ **YES** |
| `glicko_mastery_v1`         | Glicko Mastery         | Rating     | Glicko-2              | Performance tracking (mu/phi/vol)   | ✓ **YES** |
| `framework_fusion_v1`       | Framework Fusion       | Reasoning  | RTF-TAG-BAB-CARE-RISE | Meta-framework coordination         | ✓ **YES** |
| `benchmark_testing_v1`      | Benchmark Testing      | Validation | N/A                   | HumanEval/BigCodeBench/SWE-bench    | ✓ **YES** |

---

## Agent Evolution Detail

### v1.0.0 Agents

| ID                        | Persona            | Skills                 | Purpose                 |
| ------------------------- | ------------------ | ---------------------- | ----------------------- |
| `ultrathink_designer`     | Steve Jobs         | research, design       | Beautiful inevitability |
| `wealth_accelerator`      | Revenue Strategist | monetization, research | 10x income via leverage |
| `pnkln_orchestrator_meta` | Execution Engine   | all skills             | Auto-routing            |

### v2.0.0 Agents (All 6)

| ID                        | Persona            | Skills                           | Purpose                             | NEW?      |
| ------------------------- | ------------------ | -------------------------------- | ----------------------------------- | --------- |
| `ultrathink_designer`     | Steve Jobs         | research, design                 | Beautiful inevitability             | No        |
| `wealth_accelerator`      | Revenue Strategist | monetization, research           | 10x income via leverage             | No        |
| `pnkln_orchestrator_meta` | Execution Engine   | all skills                       | Auto-routing                        | No        |
| `deep_reasoning_agent`    | DTE Reasoner       | research, framework, cheatsheet  | Multi-stage DTE-evolved reasoning   | ✓ **YES** |
| `panel_debate_agent`      | Multi-Perspective  | research, design, framework      | PanelGPT/MAD consensus              | ✓ **YES** |
| `code_crafter_agent`      | Code Generator     | cheatsheet, framework, benchmark | Benchmark-validated code generation | ✓ **YES** |

---

## Key Differences Summary

### Architectural Philosophy

**v1.0.0:** _Elegant foundation_

- Prove the concept
- Beautiful, simple, inevitable
- Manual curation of skills/agents
- Focus: Reliable execution

**v2.0.0:** _Intelligent ecosystem_

- Build on proven foundation
- Add self-evolution capabilities
- Automated improvement via learning
- Focus: Continuous optimization

### When to Use Each

**Use v1.0.0 when:**

- Stability is paramount
- Manual control preferred
- Deterministic behavior required
- Simpler stack preferred

**Use v2.0.0 when:**

- Performance optimization needed
- Self-improvement desired
- Objective validation required
- Advanced reasoning essential

### Migration Strategy

**Option 1: Feature Flag (Recommended)**

```python
orchestrator = create_orchestrator(
    version="2.0.0",              # or "1.0.0"
    enable_evolution=True,        # DTE on/off
    enable_ratings=True,          # Glicko on/off
    enable_benchmarks=False       # Validation on/off
)
```

**Option 2: Separate Instances**

```python
# v1.0.0 for production stability
orchestrator_stable = create_orchestrator(version="1.0.0")

# v2.0.0 for experimentation
orchestrator_evolved = create_orchestrator(version="2.0.0", enable_evolution=True)
```

---

## Branch Strategy

### Current State

```
main
  └─ claude/pnkln-ultrathink-framework-01URALiZh8CRvMhLV9FeXVce (v1.0.0) ✓ DEPLOYED
```

### Proposed v2.0.0 Development

```
main
  ├─ claude/pnkln-ultrathink-framework-01URALiZh8CRvMhLV9FeXVce (v1.0.0) ✓
  │
  └─ claude/pnkln-ecosystem-v2-[NEW_SESSION_ID] (v2.0.0) ⬅ CREATE THIS
       │
       ├─ Branch from v1.0.0
       ├─ Add evolution/, validation/ directories
       ├─ Extend skills/agents registries
       ├─ Implement Glicko/GRPO/DTE
       └─ Merge when benchmarks pass
```

**Note:** The reference to `claude/kernel-chaining-architecture-01XDGPpkmfkiiiNWRNFnkJKR` suggests exploration of chaining patterns. That should be analyzed separately and potentially merged if proven beneficial.

---

## Risk Assessment

### v1.0.0 Risks (Mitigated)

- ✓ No evolution → Manual updates needed (acceptable, proven stable)
- ✓ No ratings → Selection by keywords only (works well for clear intent)
- ✓ No benchmarks → Trust through testing (tests pass, audit trail works)

### v2.0.0 Additional Risks (To Manage)

- ⚠ Evolution instability → **Mitigation:** Feature flags, gradual rollout
- ⚠ Rating drift → **Mitigation:** Glicko tolerances, manual override
- ⚠ Benchmark dependencies → **Mitigation:** Graceful degradation if unavailable
- ⚠ Increased complexity → **Mitigation:** Maintain v1.0.0 simplicity as fallback

---

## Implementation Phases

### Phase 1: Foundation Extensions (Week 1)

- [ ] Create `pnkln/core/glicko.py`
- [ ] Create `pnkln/core/grpo.py`
- [ ] Add tests for both
- [ ] Verify backward compatibility

### Phase 2: Skills & Agents (Week 2)

- [ ] Extend `skills/registry.yaml` (+4 skills)
- [ ] Extend `agents/registry.yaml` (+3 agents)
- [ ] Update orchestrator for new skills
- [ ] Add integration tests

### Phase 3: Evolution Layer (Week 3)

- [ ] Create `evolution/` directory
- [ ] Implement DTE cycle
- [ ] Implement GRPO training loop
- [ ] Add debate orchestration

### Phase 4: Validation Layer (Week 4)

- [ ] Create `validation/` directory
- [ ] Integrate HumanEval
- [ ] Integrate BigCodeBench
- [ ] Integrate SWE-bench
- [ ] Create end-to-end tests

### Phase 5: API & Documentation (Week 5)

- [ ] Add 5 new endpoints
- [ ] Update all documentation
- [ ] Create migration guide
- [ ] Benchmark performance

---

**Next Action:** Choose implementation path and create v2.0.0 branch

**Philosophy Check:** Does v2.0.0 add or simplify?
**Answer:** Adds capability (evolution, ratings, validation) while maintaining v1.0.0 simplicity as foundation. Each addition has single, clear purpose. **Steve would ship this.**
