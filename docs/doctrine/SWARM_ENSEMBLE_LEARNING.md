# Swarm-Style Ensemble Learning Pattern

**Core Doctrine for Multi-Agent AI Systems**

Based on: CIKD (Collaborative Inter-agent Knowledge Distillation), NeurIPS 2019

---

## 1. Core Loop

```
SCORE → ELECT BEST → DISTILL → REPEAT
```

### The Pattern

1. **Maintain K parallel agents** (not 1 agent)
   - Each agent explores with different initialization
   - Diversity drives exploration of solution space

2. **Periodically score all agents** on objective metric
   - Latency, quality, cost, win-rate, ROI
   - Use rolling window, not point-in-time

3. **Elect current best-performing agent as "teacher"**
   - Teacher's behavior becomes the reference

4. **Distill teacher's knowledge to "students"**
   - Students align toward teacher while retaining exploration
   - NOT hard replacement—soft nudging via KL divergence or state sharing

5. **Repeat**
   - Teacher can change each cycle
   - Emergent behavior: ensemble converges without killing weak agents

---

## 2. Why This Works

| Property                   | Benefit                                            |
| -------------------------- | -------------------------------------------------- |
| **Diversity preservation** | Weak agents may have useful partial solutions      |
| **Soft alignment**         | Avoids premature convergence to local optima       |
| **Sample efficiency**      | Agents share discoveries, not just final solutions |
| **Robustness**             | No single point of failure                         |
| **Emergent leadership**    | Best agent changes as environment changes          |

---

## 3. Mapping to MDMP / Staff Process

| Military Concept                      | CIKD Equivalent                       |
| ------------------------------------- | ------------------------------------- |
| Multiple staff sections building COAs | K parallel agents exploring solutions |
| Commander selects best COA elements   | Elect teacher from performance window |
| Staff re-aligns planning assumptions  | Students distill from teacher         |
| Continuous refinement                 | Repeat loop                           |
| Running estimate updates              | Periodic scoring cycle                |

**Key insight:** This is exactly how a well-run staff operates—multiple viewpoints, periodic alignment to best elements, while preserving capacity to explore alternatives.

---

## 4. Implementation for 600-Agent Flying n-autoresearch/Kosmos/BioAgents

### Architecture

```
24 squads × 25 agents = 600 total
→ Treat each SQUAD as an ensemble member
→ 24 parallel "agents" at the ensemble level
```

### Scoring Metrics (per squad)

```python
score = (
    0.4 * (1 / avg_latency_ms) +      # Speed
    0.3 * success_rate +               # Quality
    0.2 * (1 / avg_cost) +             # Efficiency
    0.1 * task_throughput              # Volume
)
```

### Teacher Election

```python
def elect_teacher(squads: List[Squad], window: int = 100) -> int:
    """Elect best-performing squad as teacher."""
    scores = [compute_score(s, window) for s in squads]
    return np.argmax(scores)
```

### Distillation (Pseudo-Distillation for Non-RL)

For LLM/rules-based agents without gradient-based training:

```python
def distill(teacher: Squad, student: Squad, alpha: float = 0.3):
    """Soft-align student toward teacher behavior."""
    # Copy teacher's successful patterns
    student.pheromone_trail = (
        (1 - alpha) * student.pheromone_trail +
        alpha * teacher.pheromone_trail
    )

    # Align hyperparameters
    student.routing_weights = (
        (1 - alpha) * student.routing_weights +
        alpha * teacher.routing_weights
    )

    # Preserve student's unique exploration
    student.exploration_rate *= 1.1  # Boost after distillation
```

---

## 5. Applications

### A. COA Generation Engine

- K planners generate different approaches
- Score by feasibility, risk, resource efficiency
- Best elements propagate to all planners

### B. Contract Scoring Ensemble

- Multiple models score same contract
- Best model's weights partially update others
- Diversity prevents groupthink

### C. Risk Scenario Simulators

- Parallel Monte Carlo simulations
- Best-performing simulation seeds next round
- Emergent convergence to high-value scenarios

### D. LLM Response Ensemble

- K LLM calls with different temperatures/prompts
- Score by user feedback or objective metric
- Winner's prompt/params influence others

---

## 6. Distillation Window & Cadence

| System Type                  | Window Size      | Distillation Cadence |
| ---------------------------- | ---------------- | -------------------- |
| Real-time (latency-critical) | 50-100 samples   | Every 5 minutes      |
| Batch processing             | 500-1000 samples | Every hour           |
| Strategic planning           | 5000+ samples    | Daily                |

**Rule of thumb:** Distill when variance across agents is high but best agent is stable for 3+ scoring cycles.

---

## 7. Anti-Patterns to Avoid

### ❌ Hard replacement

Don't kill weak agents—they may have useful partial knowledge.

### ❌ Single teacher forever

Teacher should change as environment/objective changes.

### ❌ Full alignment

Students should retain exploration capacity (exploration_rate boost after distillation).

### ❌ Synchronous updates

Distillation can be async—agents don't need to wait for each other.

### ❌ Global teacher only

Consider hierarchical distillation: squad-level teachers, then platoon-level.

---

## 8. Metrics to Track

```python
metrics = {
    "teacher_stability": "How often does teacher change?",
    "ensemble_variance": "How different are agent behaviors?",
    "convergence_rate": "How fast does ensemble converge?",
    "exploration_diversity": "Are agents still exploring?",
    "distillation_impact": "Performance delta post-distillation"
}
```

**Healthy ensemble:** Teacher changes occasionally, variance decreases over time but never hits zero, all agents still exploring at low rate.

---

## 9. Integration Points

### With memory_fabric.py

- Store ensemble scores in global tier
- Store teacher ID in global tier
- Store squad-specific patterns in team tier

### With running_estimate.py

- Use running estimate metrics as scoring inputs
- Kill conditions trigger emergency distillation (everyone aligns to most stable agent)

### With swarm_orchestrator.py

- Distillation happens during MDMP Step 5 (COA Comparison)
- Teacher election happens during MDMP Step 6 (COA Approval)

---

## 10. Reference

Hong et al., "Swarm-inspired Reinforcement Learning via Collaborative Inter-agent Knowledge Distillation," NeurIPS 2019 Deep RL Workshop.

Key results:

- 20-40% sample efficiency gain over vanilla SAC
- Works on continuous control (MuJoCo)
- Scales with ensemble size

**Our adaptation:** Replace gradient-based distillation with state/weight sharing for non-RL agents.

---

## Summary

**Always multiple agents. Periodically elect a best one. Distill its behavior into the rest. Repeat.**

This is the core learning doctrine for all Flying n-autoresearch/Kosmos/BioAgents multi-agent systems.
