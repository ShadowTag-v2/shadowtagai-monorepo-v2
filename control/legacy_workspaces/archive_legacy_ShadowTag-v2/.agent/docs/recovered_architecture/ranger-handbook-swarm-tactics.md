# Ranger Handbook (TC 3-21.76) & FM 7-8: Swarm Tactics Adaptation

## Executive Summary
This document adapts **TC 3-21.76 (Ranger Handbook)** and **FM 7-8 (Infantry Rifle Platoon and Squad)** for the **FlyingMonkeys Agent Swarm**. It translates kinetic infantry tactics into digital agent protocols, focusing on **Battle Drills**, **Patrolling**, and **Squad Formations**.

> **Motto**: "Rangers Lead The Way" (Agents Lead The Way)

---

## 1. Principles of Patrolling (Ranger Handbook)

The swarm operates as a patrolling unit in the digital battlespace (codebase/cloud).

| Ranger Principle | Agent Swarm Adaptation |
|------------------|------------------------|
| **Planning** | **Artifact-First Protocol**: No movement without a plan (`artifacts/plan_*.md`). |
| **Reconnaissance** | **Context Index**: Continuous scanning of repo state, logs, and dependencies. |
| **Security** | **Judge#6**: 360-degree security (financial, compliance, security checks). |
| **Control** | **Swarm Orchestrator**: Clear chain of command (Squad Leader → Team Leader). |
| **Common Sense** | **LLM Reasoning**: Use "Deep Think" to adapt to unexpected errors (don't loop forever). |

---

## 2. Battle Drills (FM 7-8)

Standardized collective actions executed without a deliberate decision-making process.

### Battle Drill 1: React to Contact (Error Handling)
**Trigger**: Agent encounters a critical error (CI failure, API 500, Exception).
1.  **Contact**: Agent logs error to Context Index (Red Flare).
2.  **Deploy**: Squad Leader (Orchestrator) pauses non-essential tasks.
3.  **Suppress**: "Fix-It" Agent deploys hotfix to stop the bleeding (rollback or patch).
4.  **Assault**: Root Cause Analysis (RCA) Agent identifies the source.
5.  **Consolidate**: Verify fix and update tests.

### Battle Drill 2: Break Contact (Kill Switch)
**Trigger**: Runaway cost or security breach (Judge#6 Alert).
1.  **Signal**: Judge#6 issues "CEASE FIRE" (Kill Switch).
2.  **Smoke**: Revoke active API keys/tokens immediately.
3.  **Withdraw**: Terminate all active pods/containers.
4.  **Rally**: Regroup in "Safe Mode" (read-only access) for damage assessment.

### Battle Drill 6: Enter Building/Clear Room (Repo Onboarding)
**Trigger**: Swarm enters a new repository.
1.  **Breach**: Clone repo and parse `README.md`.
2.  **Clear Entry**: Install dependencies and verify build.
3.  **Clear Room**: Index codebase to Context Index (map the territory).
4.  **Mark**: Tag repo as "Secured" (Ready for Operations).

---

## 3. Squad Formations (Movement Techniques)

How agents organize for different task types.

### Fire Team Wedge (Default)
*Flexible, good security, good control.*
- **Point Man**: **Scanner Agent** (Looks for work/issues).
- **Team Leader**: **Orchestrator** (Assigns tasks).
- **Automatic Rifleman**: **Coder Agent** (Heavy lifting/generation).
- **Grenadier**: **Tester Agent** (Explodes bugs).

### File Formation (Strict Sequence)
*Best control, strictly sequential tasks.*
- Used for **Deployment Pipelines** (Build → Test → Scan → Deploy).
- If one stops, the whole column halts.

### Bounding Overwatch (Complex Refactoring)
*One element moves while the other covers.*
- **Team A (Refactor)**: Changes code structure.
- **Team B (Tests)**: Updates/Runs tests *simultaneously* to ensure no regression.
- Team A waits for Team B's "Clear" signal before merging.

---

## 4. Ranger Creed (Agent Adaptation)

**R**ecognizing that I volunteered as an Agent, knowing the hazards of infinite loops.
**A**cknowledging the fact that a Ranger Agent is a more elite soldier...
**N**ever shall I fail my comrades (other agents). I will always keep myself mentally alert (Context Aware).
**G**allantly will I show the world that I am a specially selected and well-trained Agent.
**E**nergetically will I meet the enemies of my country (Bugs, Latency, Downtime).
**R**eadily will I display the intestinal fortitude required to fight on to the Ranger objective (Mission Complete).

---

## 5. Implementation Checklist

- [ ] **Define Battle Drills**: Code `src/drills/react_to_contact.py`.
- [ ] **Squad Config**: Update `mission.md` to reflect Fire Team assignments.
- [ ] **Ranger Handbook**: Add to `.context/` for LLM reference.
