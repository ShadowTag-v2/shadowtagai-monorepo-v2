# Rule 51: Pre-Agent Decision Protocol
# Source: NotebookLM × Antigravity Pre-Agent Protocol
# Created: 2026-04-11

## Purpose
Forces diagnostic thinking via NotebookLM BEFORE launching agent execution. Prevents "perfect execution of the wrong thing."

## Core Principle
> Speed amplifies both correct decisions and mistakes. Validate the decision before optimizing the execution.

## Trigger Conditions

The Pre-Agent Protocol MUST run before:
1. Any task with >100 LOC changes
2. Any architectural decision or refactor
3. Any deployment or infrastructure change
4. Any multi-agent parallel dispatch

## The Protocol (3 phases)

### Phase 1: NotebookLM Diagnostics (5 min)
- Upload plan to Master Brain
- Ask: "What's missing? What assumptions haven't been tested?"
- Ask: "What are 2 alternative approaches?"
- Ask: "3 arguments FOR, 3 AGAINST. Which wins?"

### Phase 2: Decision Integrity Gate
ALL four must be YES:
- Gaps acknowledged
- Gaps filled
- Justification clear
- Motivation correct (tested, not impatient)

### Phase 3: Execution with Tested Plan
- Reference verified spec, not original plan
- Run CodeRabbit review on every output
- Upload final artifacts back to Master Brain

## The Critical Question
After every agent output, ask:
> "What if the idea is wrong but perfectly executed?"

## Workflow
`/pre-agent-protocol` — full protocol with CLI commands

## Skill
`pre-agent-protocol` — diagnostic prompts and decision integrity gates

## Integration
- Runs BEFORE: `brainstorming`, `writing-plans`, `executing-plans`
- Runs WITH: `notebooklm-bridge`, `aegaeon-caching-strategist`
- Runs AFTER: `code-review`, `verification-before-completion`
