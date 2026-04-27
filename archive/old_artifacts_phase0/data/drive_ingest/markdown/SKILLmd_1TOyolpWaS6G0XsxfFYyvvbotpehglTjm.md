# Agent Orchestration - Autoresearch Swarm Patterns

**Version**: 1.0
**Last Updated**: 2025-11-22
**Scope**: 600-agent swarm orchestration with Army OPORD principles

## Overview

This skill enforces **Army Operations Order (OPORD)** format and **Army Leadership Principles** for commanding the Autoresearch swarm. Every atomic thread follows the 5-paragraph OPORD structure for perfect uniformity.

## Army Leadership Principles (Embedded in Agents)

1. **Know yourself and seek self-improvement** - Agents track expertise_level and biases
2. **Be technically and tactically proficient** - PhD/JD credentials enforced
3. **Seek responsibility and take responsibility** - Task ownership via Context Index
4. **Make sound and timely decisions** - Judge#6 governance integration
5. **Set the example** - Senior agents mentor junior agents
6. **Know your soldiers and look out for their welfare** - Shift rotation prevents burnout
7. **Keep your soldiers informed** - Broadcast tasks with full context
8. **Develop a sense of responsibility in your subordinates** - Delegation to child agents
9. **Ensure the task is understood, supervised, and accomplished** - Quality gates
10. **Train your soldiers as a team** - LLM Chorus for consensus
11. **Employ your unit in accordance with its capabilities** - Personality-based routing

## OPORD 5-Paragraph Format for Atomic Threads

Every atomic chat thread follows this **uniform template**:

### Template Structure

```markdown
# OPORD [NUMBER] - [TASK TITLE]

## 1. SITUATION
**Enemy Forces**: [Blockers, technical debt, bugs]
**Friendly Forces**: [Available agents, tools, resources]
**Attachments/Detachments**: [External dependencies, APIs]
**Civil Considerations**: [User impact, compliance requirements]

## 2. MISSION
**WHO**: [Agent IDs or shift number]
**WHAT**: [Specific task]
**WHEN**: [Deadline or priority]
**WHERE**: [File paths, services, components]
**WHY**: [Business objective, revenue impact]

## 3. EXECUTION
**Commander's Intent**: [End state vision]
**Concept of Operations**: [High-level approach]
**Tasks to Subordinate Units**:
  - Agent Squad A: [Specific task]
  - Agent Squad B: [Specific task]
**Coordinating Instructions**:
  - Phase Lines: [Milestones]
  - Checkpoints: [Quality gates]
  - Consolidation: [Merge strategy]

## 4. SERVICE SUPPORT
**Logistics**: [Dependencies, libraries, APIs]
**Personnel**: [Agent assignments, expertise required]
**Medical**: [Error handling, rollback procedures]

## 5. COMMAND & SIGNAL
**Command**: [SwarmOrchestrator, BarExamProtocol gates]
**Signal**: [Communication channels, Context Index logging]
**Succession of Command**: [Fallback agents if primary fails]

---

**ACKNOWLEDGE**: [Agent signatures]
**TIME HACK**: [Timestamp]
```

## Troop Leading Procedures (TLP) for Task Execution

1. **Receive the Mission** - Parse task from SwarmOrchestrator
2. **Issue Warning Order** - Notify shift agents immediately
3. **Make a Tentative Plan** - Use `/dev-docs` to create plan.md
4. **Initiate Movement** - Assign agents to subtasks
5. **Conduct Reconnaissance** - Analyze codebase, dependencies
6. **Complete the Plan** - Finalize plan.md with user approval
7. **Issue the Order** - Broadcast OPORD to agents
8. **Supervise and Refine** - Monitor via Context Index, adjust

## Shift Management (200 Agents per Shift)

```python
# Shift rotation follows 8-hour cycles
SHIFT_0 = agents[0:200]    # 0000-0800 UTC
SHIFT_1 = agents[200:400]  # 0800-1600 UTC
SHIFT_2 = agents[400:600]  # 1600-0000 UTC

# Each shift gets:
# - Fresh short_term_memory (cleared on rotation)
# - Handoff brief from previous shift (via Context Index)
# - OPORD for current tasks
```

## Task Broadcasting Pattern

```python
def broadcast_task(self, task: str, shift: int = 0) -> Dict:
    """
    Broadcast task using OPORD format.

    Army Principle: "Ensure the task is understood, supervised, and accomplished"
    """
    active_agents = self.get_shift(shift)

    # Create OPORD
    opord = self._generate_opord(
        task=task,
        agents=active_agents,
        situation=self._assess_situation(),
        mission=self._define_mission(task),
        execution=self._plan_execution(task, active_agents)
    )

    # Log to Context Index
    self.context_index.create_context(
        issue_title=f"OPORD-{self.opord_counter}",
        brief=opord,
        tags=["opord", f"shift-{shift}", "broadcast"]
    )

    return {
        "opord_number": self.opord_counter,
        "agents_notified": len(active_agents),
        "execution_phases": opord["execution"]["phases"]
    }
```

## Consensus via LLM Chorus

For critical decisions, use **LLM Chorus** (multiple agents vote):

```python
# Minimum 3 agents for consensus
# Require 2/3 majority for approval
# Log dissenting opinions to Context Index
```

## Resources

- [opord-templates.md](resources/opord-templates.md) - Full OPORD examples
- [shift-handoff.md](resources/shift-handoff.md) - Shift change procedures
- [task-routing.md](resources/task-routing.md) - SwarmOrchestrator integration
- [consensus.md](resources/consensus.md) - LLM Chorus voting patterns

## Enforcement

This skill auto-activates when:
- Keywords: `flying.*monkeys`, `swarm`, `orchestrat`, `agent.*spawn`, `shift.*rotation`
- File paths: `agents/**/*.py`, `src/ShadowTag-v2/orchestrator/**/*.py`
- Intent: Agent management, task delegation, swarm coordination
