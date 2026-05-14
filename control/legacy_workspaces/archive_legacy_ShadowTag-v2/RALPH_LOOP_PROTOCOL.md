# Ralph Trinity Protocol: The 3-Cycle Verification Loop

> **Philosophy**: "Three votes, three judgments, two refinements, one commit."
> **Actors**:
> *   **Monkeys (Swarm)**: Consensus & Voting (The "Board").
> *   **Judge (Compliance)**: Rules & Constraints (The "Brakes").
> *   **GCA (You)**: Refiner, Proposer, & Executor (The "Hands").

## 1. The Trinity Cycle Flow

### Phase 0: Ignition
*   **Input**: User's Raw Prompt.
*   **GCA Action**: "Smart Action" formatting. Scaffolding resources for the Whiteboard.
*   **Output**: A votable Proposal.

### Phase 1: The First Pass (Rough Draft)
1.  **Monkeys Vote**: Assess the Proposal.
2.  **Judge Clears**: Compliance check (Tokens, Latency, Security).
3.  **GCA Action**: Apply **Standard Proposed Changes #1** (Initial cleanup, structure, types).

### Phase 2: The Second Pass (Refinement)
1.  **Monkeys Vote**: Assess Refinement #1.
2.  **Judge Clears**: Deep scan (Logic, Safety).
3.  **GCA Action**: Apply **Standard Proposed Changes #2** (Optimization, Polish, Edge Cases).

### Phase 3: The Final Pass (Ratification)
1.  **Monkeys Vote**: Verify Final State against **Original User Prompt** (Intent check).
2.  **Judge Clears**: Final Gate (Release Approval).
3.  **GCA Action**:
    *   **Write to Codebase**.
    *   **Commit to Git**.

## 2. Implementation Logic (Python)

```python
def pnkln_trinity_cycle(user_prompt):
    # 0. Ignition
    proposal = gca_format_prompt(user_prompt)

    # Cycle 1
    vote_1 = monkeys_vote(proposal)
    judge_1 = judge_compliance(proposal)
    refinement_1 = gca_refine_standard(proposal, pass_num=1)

    # Cycle 2
    vote_2 = monkeys_vote(refinement_1)
    judge_2 = judge_compliance(refinement_1)
    refinement_2 = gca_refine_standard(refinement_1, pass_num=2)

    # Cycle 3 (Ratification)
    vote_3 = monkeys_vote_intent(user_prompt, refinement_2)
    judge_3 = judge_compliance(refinement_2)

    if all([judge_1, judge_2, judge_3]) and vote_3['pass']:
        gca_write_and_commit(refinement_2)
        return "COMMITTED"
    return "REJECTED"
```

## 3. Integration with GCA
GCA (The Agent) must:
1.  **Scaffold**: Provide "Whiteboard" resources (Context, Files) before Vote 1.
2.  **Refine**: Have pre-baked "Standard Changes" (Linting, Typing, Docs) ready for Passes 1 & 2.
3.  **Execute**: Only touch the disk after Judge Clear #3.
