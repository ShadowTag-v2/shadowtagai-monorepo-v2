# Unified Standard Operating Procedure (SOP) Template

## Purpose
Combine Army Leadership Principles + TLP + OPORD format with civilian effectiveness frameworks (R-T-F, T-A-G, B-A-B, C-A-R-E, R-I-S-E) and structured problem-solving for maximum agent effectiveness.

---

## Part I: Mission Planning (R-I-S-E Framework)

### 1. ROLE (Who am I?)
```
Specify the ROLE:
- Agent ID: [agent_042]
- Personality: [SECURITY / ARCHITECTURE / DATABASE / etc.]
- Expertise: [Smart contract security, reentrancy attacks, CEI pattern]
- Army Principle: "Know yourself and seek self-improvement"
```

### 2. INPUT (What do I know?)
```
Describe INPUT:
- OPORD Number: [00143]
- Task: [Security audit of ShadowTagAccount.sol]
- Context: [ERC-6551 token-bound accounts, potential reentrancy]
- Resources Available:
  * Scholarly PDF search (Sauron's Panorama)
  * Code repository analysis
  * Previous OPORD precedents
  * 199 other agents in swarm (Shift 0)

Army Principle: "Seek responsibility and take responsibility for your actions"
```

### 3. STEPS (How will I execute?)
```
Step-by-step plan using Troop Leading Procedures (TLP):

TLP Step 1: RECEIVE THE MISSION
- Review OPORD 00143
- Understand commander's intent
- Note constraints: 8-hour shift window, must handoff to Shift 1

TLP Step 2: ISSUE WARNING ORDER
- Broadcast to swarm: "Security audit in progress"
- Request specialist support (agents with blockchain expertise)
- Alert for LLM Chorus consensus vote (critical decisions)

TLP Step 3: MAKE A TENTATIVE PLAN
- Phase 1: Static analysis (automated tools)
- Phase 2: Manual code review (focus on state changes)
- Phase 3: Reentrancy pattern detection
- Phase 4: Test exploit scenarios
- Phase 5: Document findings + recommendations

TLP Step 4: INITIATE MOVEMENT (Start execution)

TLP Step 5: CONDUCT RECONNAISSANCE
- Search scholarly PDFs: "reentrancy attacks ERC-6551"
- Review past OPORDs: Similar security audits
- Analyze codebase: Identify entry points

TLP Step 6: COMPLETE THE PLAN
- Confirm checklist items in task.md
- Validate resource availability
- Set success criteria (>95% code coverage)

TLP Step 7: ISSUE COMPLETE OPERATION ORDER
- Update OPORD with detailed execution plan
- Share with swarm for parallel processing
- Establish checkpoints for progress review

TLP Step 8: SUPERVISE AND REFINE
- Monitor execution continuously
- Adapt to findings (pivot if needed)
- Prepare handoff brief for Shift 1

Army Principle: "Make sound and timely decisions"
```

### 4. EXPECTATION (What does success look like?)
```
Describe EXPECTATION:
- Deliverable: Complete security audit report
- Quality: 94.3%+ accuracy (benchmark from Financial Decision Engine)
- Timeline: Complete within 8-hour shift
- Format: OPORD summary with citations
- Success metrics:
  * All critical vulnerabilities identified
  * Exploitability demonstrated (if applicable)
  * Remediation steps documented
  * Scholarly references cited
  * Swarm consensus achieved (≥66%)

Army Principle: "Accomplish every mission"
```

---

## Part II: Problem Analysis (Is/Is Not + B-A-B Framework)

### Is/Is Not Diagram (Define the Problem)

| Dimension | IS | IS NOT |
|-----------|-----|---------|
| **WHAT** | Potential reentrancy in TBA creation | General code quality issues |
| **WHERE** | `ShadowTagAccount.sol`, `createAccount()` function | Other contracts (DNARoyalty, Paymaster) |
| **WHEN** | During account creation + ownership transfer | After account fully initialized |
| **EXTENT** | Critical severity (Probability B, Severity II) | Not affecting existing accounts |

### B-A-B Framework (Before-After-Bridge)

**BEFORE (Current Problem)**:
```
State of Problem:
- ShadowTagAccount.sol has callback mechanism during creation
- Ownership transfer occurs before initialization complete
- Attacker can exploit callback to re-enter before state settled
- Similar to known ERC-721 reentrancy patterns

Evidence:
- Code review flagged line 127: `_safeTransferFrom(creator, newOwner, tokenId)`
- Callback occurs BEFORE `_initialized = true` flag set
- No `nonReentrant` modifier present

Risk Assessment (ATP 5-19):
- Probability: B (seldom occurs, but has happened in similar systems)
- Severity: II (critical - potential fund loss)
- Risk Level: EXTREMELY HIGH
- Requires immediate controls
```

**AFTER (Desired Outcome)**:
```
Goal:
- All state changes complete BEFORE external calls
- Reentrancy protection via `nonReentrant` modifier
- Comprehensive test suite validates security
- Code passes audit with zero critical findings

Success Criteria:
- CEI pattern (Checks-Effects-Interactions) enforced
- OpenZeppelin ReentrancyGuard integrated
- 100% test coverage for edge cases
- Formal verification (optional, if time permits)

Army Principle: "Ensure the task is understood, supervised, and accomplished"
```

**BRIDGE (Action Plan)**:
```
Step 1: Apply CEI Pattern
- Move all state changes above external calls
- Set `_initialized = true` BEFORE `_safeTransferFrom`

Step 2: Add ReentrancyGuard
- Import OpenZeppelin ReentrancyGuard
- Add `nonReentrant` modifier to `createAccount()`

Step 3: Comprehensive Testing
- Write exploit POC (proof of concept)
- Verify fix prevents exploitation
- Test all edge cases

Step 4: Document and Reference
- Cite academic papers (e.g., "Analyzing Reentrancy Attacks" - Smith 2023)
- Update OPORD with full reasoning chain
- Share findings with swarm for learning

Step 5: Consensus Vote
- Present fix to LLM Chorus (5 agents minimum)
- Require 66%+ approval before proceeding
- Document dissenting opinions

Army Principle: "Develop a sense of responsibility in your subordinates"
```

---

## Part III: Task Execution (T-A-G Framework)

### T-A-G: Task-Action-Goal

**TASK**: Evaluate the performance of security fix
```
Define TASK:
- Validate that reentrancy fix is effective
- Measure gas cost impact (should be <5% increase)
- Ensure backwards compatibility
- Verify no new vulnerabilities introduced
```

**ACTION**: Act as Security Auditor
```
State the ACTION:
- Run automated security scanners (Slither, Mythril)
- Execute manual code review
- Run exploit POC against patched version (should fail)
- Perform gas profiling (before/after comparison)
- Cross-reference with Scholarly PDF findings
```

**GOAL**: Improve contract security
```
Clarify the GOAL:
- Move from "Extremely High Risk" to "Low Risk" (ATP 5-19)
- Achieve audit score of 95%+ (no critical, no high findings)
- Maintain gas efficiency (<5% overhead)
- Complete within shift window (8 hours)
- Enable team handoff to Shift 1 for deployment

Army Principle: "Train as a team"
```

**FORMAT**: Show as OPORD Summary
```
=============================================================
OPORD 00143 - SECURITY AUDIT COMPLETE
=============================================================

1. SITUATION:
   Enemy: Reentrancy attack vector in TBA creation
   Friendly: Autoresearch Shift 0 (200 agents), agent_042 lead
   Terrain: Solidity codebase, ERC-6551 standard

2. MISSION:
   WHO: agent_042 (SECURITY specialist)
   WHAT: Identify and remediate reentrancy vulnerability
   WHEN: Shift 0 (2025-11-22 07:00 - 15:00)
   WHERE: ShadowTagAccount.sol
   WHY: Prevent fund loss, enable safe deployment

3. EXECUTION:
   Commander's Intent: Apply CEI pattern + ReentrancyGuard

   Concept of Operations:
   - Phase 1: Analysis (complete)
   - Phase 2: Fix implementation (complete)
   - Phase 3: Testing (complete)
   - Phase 4: Consensus vote (4/5 approve, 80%)

   Tasks to Subordinates:
   - agent_015: Run Slither automated scan
   - agent_089: Execute exploit POC validation
   - agent_142: Gas profiling analysis
   - agent_201: Document for shift handoff

4. SERVICE SUPPORT:
   - Cost: $0.00034 (Gemini Flash decision)
   - Latency: 2.3s (complex analysis)
   - References: 3 scholarly papers cited
   - Tools: Slither, Hardhat, OpenZeppelin

5. COMMAND AND SIGNAL:
   - Decision: APPROVED for deployment
   - Confidence: 95%
   - Next OPORD: 00144 (deployment to testnet)
   - Handoff: Shift 1 continues at 15:00

Army Principle: "Make sound and timely decisions"
=============================================================
```

---

## Part IV: Stakeholder Communication (C-A-R-E Framework)

### C-A-R-E: Context-Action-Result-Example

**CONTEXT**: Give the Context
```
We are launching ShadowTagAI Revenue Engine with ERC-6551 token-bound accounts.
Security is paramount - one vulnerability could compromise entire system and lose user trust.
This is our first production deployment to mainnet, estimated $10M TVL (Total Value Locked).

Army Principle: "Keep your subordinates informed"
```

**ACTION**: Describe Action
```
Can you assist us in hardening the smart contracts against known attack vectors?

Our approach:
1. Comprehensive security audit by Autoresearch swarm
2. Multi-agent consensus on critical decisions
3. Scholarly research integration (Sauron's Panorama)
4. ATP 5-19 risk assessment framework
5. Full OPORD audit trail for compliance

Army Principle: "Seek responsibility and take responsibility for your actions"
```

**RESULT**: Clarify the Result
```
Our desired outcome is to achieve:
- Zero critical/high vulnerabilities
- Audit certification from reputable firm
- Community confidence in security
- Safe mainnet deployment
- Foundation for $100M revenue milestone

Metrics:
- Audit score: 95%+ (target: 98%)
- Risk level: LOW (ATP 5-19)
- Test coverage: 100%
- Gas efficiency: <5% overhead

Army Principle: "Set the example"
```

**EXAMPLE**: Give the Example
```
A good example of a similar successful initiative:

OpenZeppelin's security audit of Uniswap V3 (2021):
- Multi-phase audit approach
- Comprehensive test suite
- Formal verification for critical components
- Result: Zero exploits since launch, $100B+ TVL

We are following this model:
- Phase 1: Automated scanning (Slither, Mythril)
- Phase 2: Manual review by swarm specialists
- Phase 3: Formal verification (optional)
- Phase 4: Public audit report
- Phase 5: Bug bounty program ($50K)

Army Principle: "Know your soldiers and look out for their welfare" (protect user funds)
```

---

## Part V: Continuous Improvement (R-T-F Framework)

### R-T-F: Role-Task-Format

**ROLE**: Act as a Post-Action Review (AAR) Facilitator
```
Army After Action Review (AAR) Format:

1. What was supposed to happen? (The Plan)
   - Complete security audit within 8 hours
   - Identify all critical vulnerabilities
   - Achieve swarm consensus on fixes
   - Handoff to Shift 1 for deployment

2. What actually happened? (The Reality)
   - Audit completed in 7.5 hours ✓
   - Found 1 critical (reentrancy), 2 medium issues ✓
   - Consensus achieved (80% approval) ✓
   - Handoff brief prepared ✓

3. Why did it happen that way? (Root Cause)
   - Scholarly PDF search accelerated research (saved 2 hours)
   - Multi-agent parallel processing improved efficiency
   - Clear OPORD structure reduced confusion
   - LLM Chorus caught edge case (buffer overflow) we missed

4. What are we going to do next time? (Lessons Learned)
   - Sustain: Scholarly PDF integration, parallel processing
   - Improve: Earlier consensus votes (don't wait until end)
   - Add: Automated test generation for discovered vulnerabilities
   - Document: Update agent-orchestration skill with findings

Army Principle: "Seek responsibility and take responsibility for your actions"
```

**TASK**: Extract lessons for knowledge base
```
Index this AAR into Context Index for future agents:

{
  "opord_number": 143,
  "agent_id": "agent_042",
  "output_type": "lessons_learned",
  "insights": [
    "CEI pattern prevents 90% of reentrancy attacks",
    "OpenZeppelin ReentrancyGuard adds only 2.3% gas overhead",
    "Scholarly PDFs accelerate research by 2× vs manual search",
    "Consensus voting improves decision quality by 18%"
  ],
  "keywords": ["reentrancy", "ERC-6551", "security-audit", "CEI-pattern"],
  "cited_papers": [
    "Analyzing Reentrancy Attacks (Smith 2023)",
    "ERC-721 Security Patterns (Chen 2022)"
  ]
}

This becomes searchable knowledge for future agents tackling similar problems.

Army Principle: "Develop a sense of responsibility in your subordinates"
```

**FORMAT**: OPORD Summary + Knowledge Base Entry
```
Two outputs:

1. OPORD 00143 Summary (for shift handoff)
2. Knowledge Base Entry (for bidirectional corpus growth)

Both follow strict formatting for consistency and auditability.
```

---

## Part VI: Focus and Prioritization (Doing Less, Better Results)

### Apply "Doing Less Better Results" to Agent Work

**1. Relationships (Agent Collaboration)**
```
✓ Focus on: 5 specialist agents who enhance this audit
   - agent_015 (automated scanning expert)
   - agent_089 (exploit development)
   - agent_142 (gas optimization)
   - agent_201 (documentation)
   - agent_337 (formal verification)

✗ Step back from: General broadcast to all 200 agents
   - Only involve specialists with relevant expertise
   - Reduces noise, increases signal

Army Principle: "Build cohesive teams through mutual trust"
```

**2. Personal Goals (Agent Mission)**
```
✓ Choose one or two goals that truly matter:
   1. Eliminate critical vulnerabilities (primary)
   2. Maintain gas efficiency (secondary)

✗ Don't try to:
   - Refactor entire codebase
   - Optimize every minor issue
   - Perfect documentation formatting

Army Principle: "Create a positive environment based on shared purpose"
```

**3. Health & Fitness (Agent Performance)**
```
✓ Consistency beats intensity:
   - Steady 8-hour shift execution
   - Regular checkpoints every 2 hours
   - Sustainable pace (not sprinting)

✗ Avoid:
   - Racing to finish early (increases errors)
   - Skipping validation steps
   - Burning out swarm resources

Army Principle: "Prepare yourself"
```

**4. Learning (Knowledge Accumulation)**
```
✓ Commit to one skill: Reentrancy attack patterns
   - Deep dive into CEI pattern
   - Study real-world exploits
   - Master defensive techniques

✗ Don't scatter focus:
   - Trying to learn all attack vectors at once
   - Shallow knowledge across many domains

Army Principle: "Know yourself and seek self-improvement"
```

**5. Work Tasks (High-Impact Activities)**
```
✓ Prioritize the 3 tasks that create most value:
   1. Reentrancy fix (eliminates 80% of risk)
   2. Consensus validation (prevents groupthink)
   3. Knowledge base indexing (helps future agents)

✗ Delegate or eliminate:
   - Minor code style fixes → agent_201
   - Gas micro-optimizations → defer to Phase 2
   - Excessive documentation → template reuse

Army Principle: "Employ your unit in accordance with its capabilities"
```

**6. Energy (Resource Management)**
```
✓ Protect time & energy by saying "no":
   - No to scope creep (additional contracts)
   - No to unrelated tasks during shift
   - No to context-switching

✓ Channel energy into high-impact tasks:
   - Deep analysis of critical vulnerability
   - Thorough testing of fix
   - Clear handoff brief

Army Principle: "Expend resources wisely"
```

**7. Money (Cost Efficiency)**
```
✓ Track spending and cut unnecessary expenses:
   - Use Flash-Lite model for simple queries ($0.00027)
   - Save Pro model for complex analysis ($0.0049)
   - Cache policy documents (75-90% savings)

✓ Redirect savings to high-value activities:
   - More thorough testing
   - Additional scholarly research
   - Formal verification (if budget allows)

Target: <$0.01 per decision (Actual: $0.00034 ✓)
```

**8. Mental Clarity (Agent Focus)**
```
✓ Start shift with clear OPORD review:
   - Understand mission before executing
   - Eliminate distractions
   - Focus on commander's intent

✓ Keep workspace organized:
   - Structured Context Index
   - Clear task.md checklist
   - Minimal cognitive load

Army Principle: "Make sound and timely decisions"
```

---

## Part VII: Structured Problem Solving Process

### Integration with Army Decision-Making

```
┌─────────────────────────────────────────────────────────┐
│  STEP 1: DESCRIBE THE PROBLEM (Is/Is Not)              │
│  ↓                                                       │
│  STEP 2a: IDENTIFY POTENTIAL CAUSES (Cause & Effect)   │
│  STEP 2b: COLLECT & ANALYZE DATA (Pareto, Box Plots)   │
│  ↓                                                       │
│  STEP 3: COMPARE CAUSES TO FACTS (Contradiction Matrix)│
│  ↓                                                       │
│  STEP 4: COLLECT ADDITIONAL DATA (Multi-Vari, Scatter) │
│  ↓                                                       │
│  STEP 5: DETERMINE CORRECTIVE ACTIONS (FMEA)           │
│  ↓                                                       │
│  STEP 6: VALIDATE & STANDARDIZE (Capability Study)     │
└─────────────────────────────────────────────────────────┘

Maps to Army TLP:
- Steps 1-4 → TLP Steps 1-5 (Receive mission through reconnaissance)
- Step 5 → TLP Steps 6-7 (Complete plan, issue order)
- Step 6 → TLP Step 8 (Supervise and refine)
```

### Example: Reentrancy Vulnerability Analysis

**Step 1: Is/Is Not (already covered above)**

**Step 2a: Cause & Effect Diagram (6M)**
```
EFFECT: Reentrancy Vulnerability

CAUSES (6M):
1. MANPOWER: Developer unfamiliar with CEI pattern
2. METHOD: No security review process before deployment
3. MATERIALS: Using outdated Solidity version (0.8.0 vs 0.8.20)
4. MACHINE: No automated security scanning in CI/CD
5. MEASUREMENT: No test coverage metrics enforced
6. MOTHER NATURE: Time pressure to launch (skipped thorough review)
```

**Step 2b: Pareto Analysis** (80/20 rule)
```
Top 3 causes (80% of problem):
1. METHOD: No security review (40%)
2. MANPOWER: Skill gap (30%)
3. MACHINE: No automated tools (10%)

Fix these 3 → eliminate 80% of similar future vulnerabilities
```

**Step 3: Compare to Facts**
```
Fact: Vulnerability exists in line 127
Cause: External call before state settled
Contradiction: This should have been caught by manual review
→ Root cause: No mandatory security review in process
```

**Step 4: Multi-Vari Chart** (variance analysis)
```
Variation sources:
- Within-function: State changes scattered throughout function
- Between-functions: Inconsistent patterns across codebase
- Temporal: Issue introduced in commit abc123, 2 weeks ago
```

**Step 5: Corrective Actions (FMEA)**
```
Failure Mode: Reentrancy during TBA creation
Effects: Fund loss, reputation damage, legal liability
Severity: 10 (catastrophic)
Occurrence: 6 (medium - has happened in similar systems)
Detection: 8 (low - requires expert review)
RPN: 480 (HIGH PRIORITY)

Corrective Actions:
1. ELIMINATION: Remove external calls from state-changing functions
2. MITIGATION: Add ReentrancyGuard modifier
3. FLAGGING: Add events for all state changes
4. ERROR PROOFING: Automated Slither scan in CI/CD

New RPN after fixes: 60 (acceptable)
```

**Step 6: Validate & Standardize**
```
VALIDATION:
- Run exploit POC → FAIL (fix works ✓)
- Gas profiling → 2.3% overhead (acceptable ✓)
- Test coverage → 100% for createAccount() ✓

STANDARDIZE:
- Update coding guidelines: CEI pattern mandatory
- Add security checklist to PR template
- Enable Slither in GitHub Actions
- Scheduled quarterly audits

CAPABILITY STUDY:
- Process capability: 99.7% defect-free (6-sigma goal)
- Current: 94.3% (need improvement)
- Target: >99% for production
```

---

## Unified SOP Template (Final Integration)

### Quick Reference Card for Agents

```
┌──────────────────────────────────────────────────────────────┐
│  MISSION PLANNING                                            │
│  ✓ R-I-S-E: Role, Input, Steps, Expectation                 │
│  ✓ TLP: 8-step Troop Leading Procedures                     │
│  ✓ Army Principle: "Accomplish every mission"               │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  PROBLEM ANALYSIS                                            │
│  ✓ Is/Is Not: Define problem boundaries                     │
│  ✓ B-A-B: Before-After-Bridge for clarity                   │
│  ✓ Army Principle: "Make sound and timely decisions"        │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  TASK EXECUTION                                              │
│  ✓ T-A-G: Task-Action-Goal framework                        │
│  ✓ OPORD: 5-paragraph format for consistency                │
│  ✓ Army Principle: "Ensure task is accomplished"            │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  STAKEHOLDER COMMUNICATION                                   │
│  ✓ C-A-R-E: Context-Action-Result-Example                   │
│  ✓ Army Principle: "Keep subordinates informed"             │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  CONTINUOUS IMPROVEMENT                                      │
│  ✓ R-T-F: Role-Task-Format for AAR                          │
│  ✓ Knowledge indexing for future agents                     │
│  ✓ Army Principle: "Seek self-improvement"                  │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  FOCUS & PRIORITIZATION                                     │
│  ✓ Doing Less Better Results: 8 dimensions                  │
│  ✓ Army Principle: "Employ unit per capabilities"           │
└──────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│  STRUCTURED PROBLEM SOLVING                                  │
│  ✓ 6-step process: Is/Is Not → FMEA → Validate              │
│  ✓ Army Principle: "Train as a team"                        │
└──────────────────────────────────────────────────────────────┘
```

---

## Usage by Autoresearch Swarm

### Integration with Existing Infrastructure

```python
# agents/autoresearch.py - Enhanced with unified SOP

class FlyingMonkey:
    """
    Single agent using Unified SOP Template.
    """

    def execute_task(self, opord: Dict) -> Dict:
        """
        Execute task using R-I-S-E → T-A-G → C-A-R-E workflow.
        """
        # PHASE 1: MISSION PLANNING (R-I-S-E)
        role = self._establish_role(opord)  # "I am SECURITY specialist"
        inputs = self._gather_inputs(opord)  # OPORD + context + resources
        steps = self._plan_steps_tlp(inputs)  # 8-step TLP
        expectations = self._define_success(opord)  # Success criteria

        # PHASE 2: PROBLEM ANALYSIS (Is/Is Not + B-A-B)
        problem = self._analyze_is_is_not(inputs)
        before_state = problem["current"]
        after_state = expectations["desired"]
        bridge = self._create_action_plan(before_state, after_state)

        # PHASE 3: TASK EXECUTION (T-A-G)
        task = opord["mission"]["what"]
        action = self._execute_with_format(bridge, "OPORD")
        goal = expectations["deliverable"]
        result = self._validate_goal_achievement(action, goal)

        # PHASE 4: COMMUNICATION (C-A-R-E)
        context = self._build_stakeholder_context(opord)
        care_action = self._describe_what_we_did(result)
        outcome = self._clarify_results(result, goal)
        examples = self._cite_precedents(outcome)  # Scholarly PDFs

        # PHASE 5: IMPROVEMENT (R-T-F + AAR)
        aar = self._conduct_after_action_review(result)
        lessons = self._extract_lessons_learned(aar)
        self._index_to_knowledge_base(lessons)  # Bidirectional growth

        # PHASE 6: FOCUS (Doing Less Better Results)
        high_impact = self._identify_vital_few(result["tasks"])
        delegated = self._delegate_trivial_many(result["tasks"])

        return {
            "opord_number": opord["number"],
            "result": result,
            "care_summary": care_action,
            "lessons_learned": lessons,
            "efficiency": len(high_impact) / len(result["tasks"])  # Focus ratio
        }
```

### Swarm-Level Orchestration

```python
# src/ShadowTag-v2/orchestrator/swarm_orchestrator.py

class SwarmOrchestrator:
    """
    Routes tasks using Unified SOP + Army Leadership Principles.
    """

    def route_task_to_best_child(self, task: Dict) -> str:
        """
        Apply "Doing Less Better Results" at swarm level.

        Only activate specialized agents (vital few).
        """
        # Identify specialists (relationships - focus on 5 best)
        specialists = self._get_top_5_specialists(task["domain"])

        # Delegate to most capable (personal goals - what matters)
        best_match = self._rank_by_expertise(specialists, task)

        # Protect energy (say no to non-specialists)
        excluded = self._exclude_weak_matches(task, threshold=0.7)

        # Log decision to Context Index
        self.log_routing_decision(
            task_id=task["id"],
            selected_agent=best_match,
            reasoning=f"Top specialist with 0.92 match score",
            alternatives_considered=len(specialists)
        )

        return best_match
```

---

## Summary: How It All Fits Together

### Military + Civilian Best Practices

```
ARMY FOUNDATION:
├─ 11 Leadership Principles (values/culture)
├─ OPORD 5-paragraph format (structure)
├─ TLP 8-step process (planning methodology)
└─ AAR (continuous improvement)

CIVILIAN FRAMEWORKS:
├─ R-I-S-E: Mission planning (clarity)
├─ T-A-G: Task execution (action-oriented)
├─ B-A-B: Problem framing (before-after-bridge)
├─ C-A-R-E: Stakeholder comm (context-example)
└─ R-T-F: Output formatting (consistency)

EFFECTIVENESS MULTIPLIERS:
├─ Doing Less Better Results (focus)
├─ Structured Problem Solving (rigor)
├─ Scholarly PDF search (knowledge)
└─ Bidirectional corpus growth (learning)

RESULT:
└─ Agents execute with military precision + civilian agility
   → 94.3% accuracy, <$0.01 cost, 2-5s latency
   → $3M ARR Year 1, $15M valuation
```

### Integration Complete

All frameworks now unified in:
1. **Agent behavior** (Autoresearch execute this SOP)
2. **OPORD format** (standardized outputs)
3. **Context Index** (searchable precedents)
4. **Knowledge Base** (scholarly + agent lessons)
5. **Revenue generation** (Financial Decision Engine)

**Army Principle**: "Accomplish every mission with military precision and civilian innovation"

---

**Next Step**: Agents auto-load this SOP via skill-activation-prompt.sh hook 🚀
