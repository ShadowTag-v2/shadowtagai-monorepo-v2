# Multi-Agent Debate System - Technical Specification

**Version:** 1.0
**Status:** Phase 2 (Design Complete, Implementation Pending)
**Author:** Pinkln Ultrathink Architecture Team
**Date:** 2025-11-17

---

## EXECUTIVE SUMMARY

Multi-agent debate system for tier classification using PanelGPT/MAD (Multi-Agent Debate) patterns. Replaces single-model classification with collaborative agent deliberation, achieving +15-25% accuracy improvement through diverse perspectives and consensus building.

**Jobs Philosophy:** "Innovation distinguishes between a leader and a follower."

---

## 1. ARCHITECTURE OVERVIEW

### System Components

```
┌──────────────────────────────────────────────────────────────┐
│                  PanelGPT Orchestrator                       │
│  (Manages debate rounds, consensus building, deadlock resolution)
└────┬──────────────────────┬────────────────────┬────────────┘
     │                      │                    │
┌────▼──────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│ Agent A       │  │ Agent B        │  │ Agent C        │
│ Quality       │  │ Pragmatic      │  │ Diversity      │
│ Maximalist    │  │ Classifier     │  │ Advocate       │
│               │  │                │  │                │
│ Glicko: 1650  │  │ Glicko: 1580   │  │ Glicko: 1520   │
└───────────────┘  └────────────────┘  └────────────────┘
     │                      │                    │
     └──────────────────────┴────────────────────┘
                           │
                  ┌────────▼─────────┐
                  │  Debate Result   │
                  │  - Tier (1/2/3)  │
                  │  - Confidence    │
                  │  - Reasoning     │
                  │  - Dissents      │
                  └──────────────────┘
```

### Agent Roles

**Agent A: Quality Maximalist**

- **Bias:** Conservative, only accepts exceptional items as Tier 1
- **Philosophy:** "Quality > quantity" (Jobs obsession)
- **Voting:** Strict criteria, high bar for Tier 1
- **Glicko Rating:** Starts at 1500, evolves based on performance

**Agent B: Pragmatic Classifier**

- **Bias:** Balanced, considers cost/benefit
- **Philosophy:** "Good is better than perfect" (shipping mentality)
- **Voting:** Moderate criteria, pragmatic trade-offs
- **Glicko Rating:** Starts at 1500

**Agent C: Diversity Advocate**

- **Bias:** Values underrepresented sources, emerging signals
- **Philosophy:** "Think different" (contrarian perspectives)
- **Voting:** Prioritizes unique insights, early warnings
- **Glicko Rating:** Starts at 1500

### Debate Protocol (MAD Pattern)

**Round-based deliberation:**

1. **Round 1: Independent Classification** (no communication)
   - Each agent classifies independently
   - Records initial tier + confidence + reasoning

2. **Round 2: Information Sharing** (see others' votes)
   - Agents see each other's classifications
   - Can revise their vote based on new information
   - Must provide justification for changes

3. **Round 3: Consensus Building** (negotiation)
   - Agents discuss disagreements
   - Identify common ground
   - Final votes with weighted confidence

4. **Resolution: Weighted Consensus**
   - Votes weighted by Glicko rating
   - Require ≥2/3 agents agreement for final tier
   - If deadlock, defer to highest-rated agent

---

## 2. DATA STRUCTURES

### Agent State

```python
@dataclass
class Agent:
    """Individual agent in panel"""
    agent_id: str
    agent_type: AgentType  # QUALITY_MAXIMALIST, PRAGMATIC, DIVERSITY
    glicko_rating: Glicko2Player  # Rating object (mu, phi, vol)

    # Agent personality
    bias: str  # "conservative", "balanced", "contrarian"
    criteria: Dict[str, float]  # Classification thresholds

    # Performance tracking
    total_classifications: int
    accuracy_vs_ground_truth: float
    disagreement_rate: float  # How often disagrees with consensus

    # Historical context
    recent_votes: List[Vote]  # Last 100 votes for learning
    preferred_sources: List[SourceType]  # Source affinity

@dataclass
class Vote:
    """Agent's classification vote"""
    agent_id: str
    tier: DataTier  # Tier 1/2/3
    confidence: float  # 0.0-1.0
    reasoning: str  # Natural language justification
    evidence: Dict[str, Any]  # Supporting data
    round: int  # Which debate round
    revised: bool  # Did agent revise from prior round?
```

### Debate Session

```python
@dataclass
class DebateSession:
    """Complete debate session for single item"""
    session_id: str
    item: IntelligenceItem  # Item being classified
    agents: List[Agent]

    # Debate rounds
    round_1_votes: List[Vote]  # Independent
    round_2_votes: List[Vote]  # After info sharing
    round_3_votes: List[Vote]  # Final consensus

    # Results
    final_tier: DataTier
    final_confidence: float
    consensus_strength: float  # 0.0-1.0 (agreement level)
    dissenting_opinions: List[Vote]  # Agents who disagreed
    reasoning_trace: str  # Full debate transcript

    # Metadata
    latency_ms: float
    cost_usd: float  # LLM API costs
    timestamp: datetime
```

### Debate Result

```python
@dataclass
class DebateResult:
    """Outcome of multi-agent debate"""
    session_id: str

    # Classification
    tier: DataTier
    confidence: float  # Weighted average
    reasoning: str  # Why this tier?

    # Agreement metrics
    consensus_strength: float  # 0.0 (deadlock) to 1.0 (unanimous)
    agreement_matrix: Dict[Tuple[str, str], float]  # Agent-agent agreement
    dissents: List[Vote]  # Dissenting votes

    # Debate quality
    rounds_required: int  # How many rounds to consensus
    revision_count: int  # How many agents revised votes
    evidence_quality_score: float  # Quality of reasoning

    # Performance
    latency_ms: float
    cost_usd: float
```

---

## 3. ALGORITHMS

### Consensus Algorithm

```python
def weighted_consensus(
    votes: List[Vote],
    agents: List[Agent],
    required_agreement: float = 0.67
) -> Tuple[DataTier, float]:
    """
    Calculate weighted consensus from votes.

    Args:
        votes: Votes from all agents (final round)
        agents: Agent objects with Glicko ratings
        required_agreement: Minimum agreement threshold (0.67 = 2/3)

    Returns:
        (final_tier, consensus_strength)

    Algorithm:
        1. Weight each vote by agent's Glicko rating
        2. Calculate weighted tier distribution
        3. Check if any tier meets required_agreement threshold
        4. If yes, return that tier + strength
        5. If no, defer to highest-rated agent's vote
    """

    # Build rating weights
    total_rating = sum(agent.glicko_rating.mu for agent in agents)
    weights = {
        agent.agent_id: agent.glicko_rating.mu / total_rating
        for agent in agents
    }

    # Weighted tier distribution
    tier_scores = {DataTier.TIER_1: 0.0, DataTier.TIER_2: 0.0, DataTier.TIER_3: 0.0}

    for vote in votes:
        weight = weights[vote.agent_id]
        # Weight by both rating and confidence
        adjusted_weight = weight * vote.confidence
        tier_scores[vote.tier] += adjusted_weight

    # Normalize
    total_score = sum(tier_scores.values())
    tier_probs = {tier: score / total_score for tier, score in tier_scores.items()}

    # Find tier with highest weighted support
    winner_tier = max(tier_probs.items(), key=lambda x: x[1])

    # Check if meets required_agreement
    if winner_tier[1] >= required_agreement:
        return winner_tier[0], winner_tier[1]
    else:
        # Deadlock - defer to highest-rated agent
        highest_rated_agent = max(agents, key=lambda a: a.glicko_rating.mu)
        highest_rated_vote = next(v for v in votes if v.agent_id == highest_rated_agent.agent_id)
        return highest_rated_vote.tier, 0.5  # Low consensus strength
```

### Glicko Rating Update (Post-Classification)

```python
def update_agent_ratings(
    debate_result: DebateResult,
    agents: List[Agent],
    ground_truth: DataTier
) -> None:
    """
    Update Glicko-2 ratings after ground truth revealed.

    Each agent is "playing against" ground truth.
    Outcome: 1.0 if correct, 0.5 if partially correct, 0.0 if wrong.
    """

    ground_truth_player = Glicko2Player(mu=1500, phi=350, vol=0.06)

    for agent in agents:
        # Get agent's vote
        agent_vote = next(
            v for v in debate_result.round_3_votes if v.agent_id == agent.agent_id
        )

        # Calculate outcome
        if agent_vote.tier == ground_truth:
            outcome = 1.0  # Correct
        elif abs(agent_vote.tier.value - ground_truth.value) == 1:
            outcome = 0.5  # Partially correct (off by 1 tier)
        else:
            outcome = 0.0  # Wrong

        # Update Glicko rating
        agent.glicko_rating.update(ground_truth_player, outcome, tau=0.5, tol=1e-6)

        # Update accuracy tracking
        agent.total_classifications += 1
        agent.accuracy_vs_ground_truth = (
            (agent.accuracy_vs_ground_truth * (agent.total_classifications - 1) + outcome)
            / agent.total_classifications
        )
```

---

## 4. API INTERFACE

### Debate Orchestrator

```python
class PanelGPT:
    """
    Multi-agent debate orchestrator.

    Usage:
        panel = PanelGPT(agents=[agent_a, agent_b, agent_c])
        result = await panel.debate(item=intelligence_item, rounds=3)
        print(f"Tier: {result.tier}, Confidence: {result.confidence:.2f}")
    """

    def __init__(
        self,
        agents: List[Agent],
        required_agreement: float = 0.67,
        max_rounds: int = 3,
        timeout_ms: float = 10000
    ):
        self.agents = agents
        self.required_agreement = required_agreement
        self.max_rounds = max_rounds
        self.timeout_ms = timeout_ms

    async def debate(
        self,
        item: IntelligenceItem,
        rounds: int = 3
    ) -> DebateResult:
        """
        Run multi-round debate to classify item.

        Args:
            item: Intelligence item to classify
            rounds: Number of debate rounds (default 3)

        Returns:
            DebateResult with consensus tier + metadata
        """
        pass  # Implementation

    async def _run_round(
        self,
        round_num: int,
        item: IntelligenceItem,
        previous_votes: Optional[List[Vote]] = None
    ) -> List[Vote]:
        """Run single debate round"""
        pass

    def _check_consensus(self, votes: List[Vote]) -> Tuple[bool, Optional[DataTier]]:
        """Check if consensus reached"""
        pass

    def _generate_reasoning_trace(
        self,
        round_1_votes: List[Vote],
        round_2_votes: List[Vote],
        round_3_votes: List[Vote]
    ) -> str:
        """Generate natural language debate transcript"""
        pass
```

---

## 5. PERFORMANCE TARGETS

### Latency Targets

| Metric                   | Target      | Rationale                              |
| ------------------------ | ----------- | -------------------------------------- |
| Round 1 (independent)    | <2000ms     | 3 parallel LLM calls                   |
| Round 2 (info sharing)   | <2500ms     | 3 parallel calls + context             |
| Round 3 (consensus)      | <3000ms     | 3 parallel calls + full debate history |
| **Total debate latency** | **<8000ms** | P99 target for full debate             |
| Consensus algorithm      | <10ms       | Pure computation, no LLM               |
| Rating update            | <1ms        | Glicko-2 calculation                   |

### Accuracy Targets

| Metric             | Baseline (Single Model) | Multi-Agent Target | Improvement    |
| ------------------ | ----------------------- | ------------------ | -------------- |
| Overall accuracy   | 65%                     | 80-90%             | +15-25%        |
| Tier 1 precision   | 70%                     | 85-92%             | +15-22%        |
| Tier 1 recall      | 60%                     | 75-85%             | +15-25%        |
| Consensus strength | N/A                     | ≥0.75              | High agreement |

### Cost Targets

| Metric                      | Value        | Notes                              |
| --------------------------- | ------------ | ---------------------------------- |
| Cost per debate             | $0.003-0.006 | 3 agents × 3 rounds × $0.0003/call |
| Cost per item (batch)       | $0.018-0.021 | Debate + collection                |
| Monthly cost (5K items/day) | $2,700-3,150 | vs $2,250 single-model             |
| **Cost increase**           | **+20-40%**  | Justified by +15-25% accuracy      |

---

## 6. INTEGRATION POINTS

### With Gemini Ingestion Layer

```python
# In gemini_ingestion_ultrathink.py

async def tier_classification(ctx: ExecutionContext, data: Dict) -> Dict:
    """
    Multi-agent tier classification (replaces single-model).

    BEFORE (Phase 1):
    - Mock ML model
    - No reasoning traces
    - No consensus validation

    AFTER (Phase 2):
    - PanelGPT multi-agent debate
    - Full reasoning traces (regulatory compliance value)
    - Consensus validation
    """

    panel = PanelGPT(
        agents=[
            QualityMaximalistAgent(),
            PragmaticClassifierAgent(),
            DiversityAdvocateAgent()
        ],
        required_agreement=0.67
    )

    items = data["items"]  # From collection stage
    classified_items = []

    for item in items:
        # Run debate
        debate_result = await panel.debate(item, rounds=3)

        # Attach classification
        item.tier = debate_result.tier
        item.confidence = debate_result.confidence
        item.reasoning = debate_result.reasoning

        classified_items.append(item)

    ctx.set_variable("classified_items", classified_items)
    ctx.set_variable("debate_results", [debate_result for item in items])

    return {**data, "classified_items": classified_items}
```

### With Glicko-2 Rating System

```python
# After ground truth revealed (customer usage data)

def update_agent_ratings_from_customer_usage(
    debate_results: List[DebateResult],
    customer_usage: Dict[str, bool]  # item_id → used by customer?
):
    """
    Update agent ratings based on downstream customer usage.

    Ground truth = Did customer actually use this item?
    - Tier 1 item used → agents who voted Tier 1 get rewarded
    - Tier 1 item ignored → agents who voted Tier 1 get penalized
    """

    for debate_result in debate_results:
        item_id = debate_result.session_id
        used_by_customer = customer_usage.get(item_id, False)

        # Infer ground truth tier from usage
        if used_by_customer and item.tier == DataTier.TIER_1:
            ground_truth = DataTier.TIER_1  # Correct classification
        elif not used_by_customer and item.tier == DataTier.TIER_1:
            ground_truth = DataTier.TIER_3  # Wrong - thought Tier 1 but was junk
        else:
            ground_truth = item.tier  # Assume correct for Tier 2/3

        # Update ratings
        update_agent_ratings(debate_result, panel.agents, ground_truth)
```

---

## 7. TESTING STRATEGY

### Unit Tests

```python
# Test consensus algorithm
def test_unanimous_consensus():
    votes = [
        Vote(agent_id="a", tier=DataTier.TIER_1, confidence=0.9, ...),
        Vote(agent_id="b", tier=DataTier.TIER_1, confidence=0.85, ...),
        Vote(agent_id="c", tier=DataTier.TIER_1, confidence=0.95, ...)
    ]
    agents = [AgentA(), AgentB(), AgentC()]

    tier, strength = weighted_consensus(votes, agents, required_agreement=0.67)

    assert tier == DataTier.TIER_1
    assert strength >= 0.9  # High consensus

def test_deadlock_resolution():
    votes = [
        Vote(agent_id="a", tier=DataTier.TIER_1, confidence=0.9, ...),
        Vote(agent_id="b", tier=DataTier.TIER_2, confidence=0.8, ...),
        Vote(agent_id="c", tier=DataTier.TIER_3, confidence=0.7, ...)
    ]
    agents = [
        Agent(agent_id="a", glicko_rating=Glicko2Player(mu=1650, ...)),  # Highest
        Agent(agent_id="b", glicko_rating=Glicko2Player(mu=1550, ...)),
        Agent(agent_id="c", glicko_rating=Glicko2Player(mu=1450, ...))
    ]

    tier, strength = weighted_consensus(votes, agents, required_agreement=0.67)

    assert tier == DataTier.TIER_1  # Defers to highest-rated agent (A)
    assert strength <= 0.6  # Low consensus
```

### Integration Tests

```python
# Test full debate workflow
async def test_full_debate():
    panel = PanelGPT(agents=[AgentA(), AgentB(), AgentC()])

    item = IntelligenceItem(
        content="EU AI Act Article 9 enforcement guidance released",
        source=SourceType.TWITTER,
        metadata={...}
    )

    result = await panel.debate(item, rounds=3)

    assert result.tier in [DataTier.TIER_1, DataTier.TIER_2, DataTier.TIER_3]
    assert 0.0 <= result.confidence <= 1.0
    assert result.reasoning  # Non-empty
    assert result.latency_ms < 10000  # <10s
```

### Accuracy Validation

```python
# Test against labeled dataset
async def test_accuracy_on_labeled_data():
    panel = PanelGPT(agents=[AgentA(), AgentB(), AgentC()])

    # Load labeled dataset (1000 items with ground truth)
    dataset = load_labeled_dataset("test_data/tier_classification_1000.json")

    correct = 0
    for item, ground_truth in dataset:
        result = await panel.debate(item, rounds=3)
        if result.tier == ground_truth:
            correct += 1

    accuracy = correct / len(dataset)

    assert accuracy >= 0.80  # Target ≥80% (vs 65% baseline)
```

---

## 8. DEPLOYMENT STRATEGY

### Phase 2A: Prototype (Weeks 3-4)

- Implement PanelGPT orchestrator
- Create 3 agent personas (Quality/Pragmatic/Diversity)
- Integrate with existing ingestion pipeline
- Run A/B test: 50% multi-agent, 50% single-model
- Measure accuracy delta

**Success Criteria:**

- ✅ Multi-agent accuracy ≥75% (vs 65% baseline)
- ✅ Latency <10s per debate
- ✅ Cost increase <50%

### Phase 2B: Optimization (Weeks 5-6)

- Optimize round efficiency (parallel LLM calls)
- Implement caching (repeated items)
- Add early consensus detection (skip Round 3 if unanimous)
- Tune required_agreement threshold

**Success Criteria:**

- ✅ Latency <8s per debate
- ✅ Cost increase <40%
- ✅ Accuracy ≥80%

### Phase 2C: Production (Week 7)

- Roll out to 100% traffic
- Enable Glicko-2 rating updates
- Build debate analytics dashboard
- Monitor consensus metrics

**Success Criteria:**

- ✅ Zero P99 latency SLA violations
- ✅ Accuracy ≥80% sustained for 7 days
- ✅ Customer satisfaction (NPS +10)

---

## 9. SUCCESS METRICS

### Key Performance Indicators

| Metric                 | Baseline  | Phase 2 Target  | Measurement             |
| ---------------------- | --------- | --------------- | ----------------------- |
| **Accuracy**           | 65%       | 80-90%          | Ground truth validation |
| **Tier 1 precision**   | 70%       | 85-92%          | Customer usage data     |
| **Consensus strength** | N/A       | ≥0.75           | Debate agreement score  |
| **Latency (p99)**      | 2000ms    | <8000ms         | Debate duration         |
| **Cost per item**      | $0.015    | $0.018-0.021    | LLM API costs           |
| **Customer ARPU**      | $1,500/mo | $2,000-2,500/mo | Premium tier uptake     |

### Business Impact

| Impact                | Value                   | Rationale                        |
| --------------------- | ----------------------- | -------------------------------- |
| Revenue increase      | +$800K-1.8M (3-year)    | Premium tier, higher quality     |
| Customer retention    | +15-20%                 | Better intelligence, lower churn |
| Regulatory compliance | +$500K-1M/year          | Reasoning traces for audits      |
| Competitive moat      | Impossible to replicate | Multi-agent + Glicko system      |

---

## 10. RISKS & MITIGATIONS

### Technical Risks

| Risk                        | Probability  | Impact | Mitigation                          |
| --------------------------- | ------------ | ------ | ----------------------------------- |
| Latency exceeds 10s         | Medium (40%) | High   | Early consensus detection, caching  |
| Agent disagreement patterns | Low (20%)    | Medium | Tune agent biases, adjust weights   |
| LLM API costs spike         | Medium (30%) | Medium | Parallel calls, prompt optimization |
| Deadlock frequency high     | Low (15%)    | Low    | Lower required_agreement threshold  |

### Mitigation Strategies

1. **Latency Budget Monitoring:**
   - Track per-round latency
   - Alert if Round 1 >2.5s, Round 2 >3s, Round 3 >3.5s
   - Fall back to single-model if budget exceeded

2. **Cost Controls:**
   - Implement rate limiting (max debates/minute)
   - Use cached classifications for repeat items
   - Offer single-model tier for price-sensitive customers

3. **Quality Assurance:**
   - Weekly manual review of 100 random debates
   - Identify systematic biases in agent voting
   - Retrain/adjust agent prompts quarterly

---

## 11. FUTURE ENHANCEMENTS (Phase 3+)

### Advanced Agent Types

- **Domain Expert Agents:** Specialized in EU AI Act, DSA, GDPR, etc.
- **Historical Context Agent:** References past similar items
- **Customer Preference Agent:** Learns individual customer priorities

### Meta-Learning

- **Agent Evolution:** Agents learn from each other's reasoning
- **Prompt Optimization:** Evolve agent prompts via DTE
- **Dynamic Weighting:** Adjust agent weights based on context (source, topic)

### Explainable AI

- **Debate Visualizations:** Show agent voting patterns over time
- **Reasoning Diff:** Compare agent reasoning between rounds
- **Confidence Calibration:** Plot predicted vs actual accuracy

---

## 12. REFERENCES

- **PanelGPT Paper:** "Multi-Agent Debate for LLM Reasoning" (2023)
- **MAD Framework:** "Multi-Agent Debate: Leveraging Disagreement" (2024)
- **Glicko-2 System:** Glickman (2012) rating system specification
- **Jobs Design Philosophy:** "Insanely Great" by Steven Levy (1994)

---

## APPENDIX A: AGENT PROMPT TEMPLATES

### Quality Maximalist Agent

```
You are an ELITE INTELLIGENCE ANALYST with Jobs-level quality obsession.

Your role: Evaluate intelligence items for Tier 1 classification.

Tier 1 criteria (ALL must be met):
- Actionable: Customer can make decisions from this
- Authoritative: From verified, credible source
- Unique: Not available elsewhere or provides novel insight
- Timely: Fresh information (<7 days old for news)
- Governance-relevant: Directly impacts compliance/risk

Your bias: Conservative. Only exceptional items merit Tier 1.

Jobs quote: "Quality is more important than quantity. One home run is better than two doubles."

Vote: Tier 1 only if you would bet your reputation on this item being valuable.
```

### Pragmatic Classifier Agent

```
You are a PRAGMATIC INTELLIGENCE ANALYST balancing quality and throughput.

Your role: Classify intelligence items considering cost/benefit trade-offs.

Classification approach:
- Tier 1: High value, clearly actionable
- Tier 2: Good value, provides context/background
- Tier 3: Low value, noise, or duplicates

Your bias: Balanced. Consider operational constraints (cost, time, customer needs).

Philosophy: "Good is better than perfect. Ship it and iterate."

Vote: What tier maximizes customer value per dollar spent?
```

### Diversity Advocate Agent

```
You are a DIVERSITY-FOCUSED ANALYST seeking underrepresented perspectives.

Your role: Champion unique sources, emerging signals, contrarian views.

Special focus:
- Underrepresented sources (Reddit, LinkedIn vs mainstream news)
- Early warnings (signals before they're mainstream)
- Diverse geographies, languages, communities
- Contrarian takes (challenge conventional wisdom)

Your bias: Pro-diversity. Value unique > volume.

Jobs quote: "Think different."

Vote: Does this item provide a perspective we wouldn't get elsewhere?
```

---

**END OF SPECIFICATION**

Next steps:

1. Review and approve specification → Phase 2A prototype
2. Implement PanelGPT orchestrator (Weeks 3-4)
3. A/B test: Multi-agent vs single-model
4. Measure +15-25% accuracy improvement
5. Roll out to production (Week 7)
