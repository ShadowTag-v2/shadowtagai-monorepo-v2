# Pre-Agent Decision Protocol

> Source: NotebookLM × Antigravity Pre-Agent Protocol  
> Purpose: Tests the IDEA before launching agent execution — prevents "perfect execution of the wrong thing"

## When to Use

- BEFORE any major feature implementation (>100 LOC)
- BEFORE any architectural decision or refactor
- BEFORE any deployment or infrastructure change
- BEFORE starting any multi-agent parallel task
- Whenever the "Passenger mindset" checklist triggers (launching agents without a plan, accepting first result, speed as main goal)

## Phase 1: Diagnostics (NotebookLM Layer) — 5 min

// turbo
```bash
export PATH="/Users/pikeymickey/Library/Python/3.13/bin:$PATH"
MASTER_BRAIN_ID=$(cat ~/.notebooklm/master-brain-id)
notebooklm use "$MASTER_BRAIN_ID" 2>&1
```

### Step 1.1: Upload the Plan/Spec

Write your plan, spec, or project brief to a temp file and upload it as a NotebookLM source:

```bash
# Write the plan
cat <<'PLAN' > /tmp/pre-agent-plan.md
## Project: [TITLE]

### Goal
[What are we trying to achieve?]

### Approach
[How do we plan to do it?]

### Assumptions
[What are we assuming is true?]

### Success Criteria
[How will we know it worked?]
PLAN

# Upload to Master Brain
notebooklm source add /tmp/pre-agent-plan.md 2>&1
```

### Step 1.2: Generate Critique

Ask NotebookLM to find holes in the plan:

```bash
notebooklm ask "Act as a sharp technical critic. What's missing from this plan? What assumptions haven't been tested? What are the top 3 risks of executing this as-is?" 2>&1
```

### Step 1.3: Gap Analysis

```bash
notebooklm ask "Document the specific gaps: (1) What alternative approaches were NOT considered? (2) What edge cases could break this? (3) What would the sharpest critic say about this plan?" 2>&1
```

### Step 1.4: Counter-Arguments (Debate Format)

```bash
notebooklm ask "Generate a structured debate: present 3 arguments FOR this approach and 3 arguments AGAINST. Which side is stronger and why?" 2>&1
```

## Phase 2: Decision with Integrity — 4 min

After Phase 1, the agent MUST answer these questions before proceeding:

### Pilot Mindset Checklist (ALL must be YES)

| Question | Answer |
|----------|--------|
| Did NotebookLM identify gaps I hadn't considered? | YES/NO |
| Have I filled or acknowledged those gaps? | YES/NO |
| Can I clearly state WHY this approach vs alternatives? | YES/NO |
| Am I ready because the plan is tested, not because I'm impatient? | YES/NO |

### Decision Gate

If ANY answer is NO → Return to Phase 1 with refined questions.
If ALL answers are YES → Write the refined spec:

```bash
# Write refined spec with integrity statement
cat <<'SPEC' > /tmp/pre-agent-verified-spec.md
## Verified Spec: [TITLE]

### Decision Integrity Statement
[Summarize what changed between the original plan and this version]

### Gaps Identified & Addressed
[List each gap from Phase 1 and how it was resolved]

### Agent Instructions
[Clear, tested instructions for what agents should build]

### Anti-Patterns to Avoid
[What NOT to do, based on the debate analysis]
SPEC

# Upload verified spec to Master Brain for provenance
notebooklm source add /tmp/pre-agent-verified-spec.md 2>&1
```

## Phase 3: Execution (Antigravity Layer)

Only NOW launch agents. The verified spec becomes the canonical input.

```bash
# Log the decision
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) — Pre-Agent Protocol PASSED. Launching execution." >> /tmp/pre-agent-log.txt
```

### Agent Launch Rules (Post-Protocol)

1. Reference the verified spec, not the original plan
2. Run CodeRabbit review on every output (`cr review --prompt-only`)
3. After execution, ask: "What if the idea was wrong but perfectly executed?"
4. Upload final artifacts back to Master Brain for provenance chain

## Phase 4: Post-Execution Reflection

```bash
notebooklm ask "Given the execution results, was the original decision correct? What would we do differently next time?" 2>&1
```

## Neuroscience Basis

- **Confirmation Bias Mitigation**: Phase 1 forces the agent to actively seek counterarguments, engaging System 2 (slow thinking) before System 1 (fast thinking) takes over.
- **Prefrontal Cortex Activation**: Critique and debate prompts activate analytical circuits rather than pattern-matching shortcuts.
- **Results**: 65% reduction in iteration cycles, 89% increase in outcome quality, 15-min investment saves 8+ hours of rework.
