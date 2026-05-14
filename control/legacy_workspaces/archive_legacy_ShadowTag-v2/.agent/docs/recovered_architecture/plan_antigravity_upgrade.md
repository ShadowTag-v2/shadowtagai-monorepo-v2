# Implementation Plan: Antigravity Workspace Upgrade

## Objective
Upgrade the current workspace to fully implement the "Antigravity Workspace Template" standards, focusing on the "Flying Monkeys" agent swarm and "Judge #6" governance engine.

## Phase 1: Infinite Memory Engine
**Goal**: Implement recursive summarization in `src/memory.py` to handle long-running agent contexts without hitting token limits.

- [ ] Modify `src/memory.py` to include `summarize_history()` method.
- [ ] Implement token counting and auto-summarization trigger.
- [ ] Store summaries in `memory_summary.json` while keeping recent logs in `memory_current.json`.

## Phase 2: Judge #6 LLM Integration
**Goal**: Replace keyword-based validation in `src/pnkln/judge_six.py` with actual Gemini 3 Deep Think validation.

- [ ] Update `_validate_purpose` to call Gemini API.
- [ ] Implement `_validate_reasons` with logic checks via LLM.
- [ ] Ensure `_check_brakes` remains deterministic (regex/keyword) for safety.

## Phase 3: Agent Swarm Integration
**Goal**: Connect `src/agent.py` to the `FlyingMonkeys` swarm logic.

- [ ] Update `src/agent.py` to import `FlyingMonkeys` from `agents/flying_monkeys.py`.
- [ ] Replace mock `act()` method with actual swarm orchestration.
- [ ] Ensure `mission.md` is read and respected by the agent.

## Phase 4: Tools Standardization
**Goal**: Expose Python tools for the agent.

- [ ] Create `src/tools/governance_tools.py` wrapping Judge #6.
- [ ] Create `src/tools/swarm_tools.py` for managing agent units.

## Execution Strategy
1.  **Memory Upgrade**: Immediate priority to support long-context operations.
2.  **Judge Upgrade**: Critical for "Make Cash" mission safety.
3.  **Integration**: Final wiring of components.
