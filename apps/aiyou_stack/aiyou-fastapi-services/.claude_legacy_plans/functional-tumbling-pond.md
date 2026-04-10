# ANTIGRAVITY RESTART CONTEXT

## Session End: 2025-11-28 | Commit: 431e4a4c

---

## PHASE 3 COMPLETE: Full Combat Posture (600 agents 24/7)

### What Was Just Pushed

```
769 files changed, 29,425 insertions(+), 1,306 deletions(-)
Commit: 431e4a4c → origin/main
```

### Integration Status

| Component                | Status                 | Files                                 |
| ------------------------ | ---------------------- | ------------------------------------- |
| **Scientific Skills**    | ✅ 117 skills loaded   | `agents/scientific_skills_loader.py`  |
| **Compounding Review**   | ✅ 24 agents           | `agents/compounding_integration.py`   |
| **M2 Deep Research**     | ✅ AIR_CAV layer       | `agents/deep_research_integration.py` |
| **Antigravity Prompts**  | ✅ Skill injection     | `prompts/antigravity_system.py`       |
| **n-autoresearch/Kosmos/BioAgents Server** | ✅ Full combat posture | `bin/n-autoresearch/Kosmos/BioAgents-server`            |

---

## MEMORY SYSTEM: erik-hancock-llm-memory

### Location

```
/Users/pikeymickey/shadowtag_v4-fastapi-services/erik-hancock-llm-memory/
```

### Key Files for Restart

| File                                  | Purpose                        |
| ------------------------------------- | ------------------------------ |
| `QUICKSTART.md`                       | Memory deployment guide        |
| `CURRENT_STATE.md`                    | Current build status           |
| `scripts/sync_to_devices.sh`          | Cross-device memory sync       |
| `scripts/claude_code_memory_local.py` | Deploy memory to Claude Code   |
| `scripts/extract_claude_web.js`       | Browser conversation extractor |
| `scripts/llm_blender_rotation.py`     | 4-LLM orchestration            |
| `configs/vertex_workbench_config.py`  | Vertex AI integration          |

### Memory Sync Commands

```bash
# Morning (pull updates)
./scripts/sync_to_devices.sh pull

# Evening (push changes)
./scripts/sync_to_devices.sh push

# Deploy to Claude Code
python3 scripts/claude_code_memory_local.py

# Cache mode
./scripts/sync_to_devices.sh cache
```

---

## DECISION FRAMEWORK (Locked)

```
╔═══════════════════════════════════════════════════════════╗
║ ID:       Maximum value extraction, no self-imposed limits ║
║ SUPEREGO: Judge #6 gates (legal/regulatory/financial/sec)  ║
║ EGO:      Purpose → Reasons → Brakes → Execute            ║
╠═══════════════════════════════════════════════════════════╣
║ IQ LOCK:  160 (Hard requirement)                          ║
║ POSTURE:  Professional                                    ║
║ STATUS:   Full Combat (All 600 agents active 24/7)        ║
╚═══════════════════════════════════════════════════════════╝
```

---

## SQUADRON STRUCTURE (Current)

```
n-autoresearch/Kosmos/BioAgents CAVALRY SQUADRON (600 agents)
├── HHT (90)      → Judge #6 + S-Staff + Scientific Skills (Clinical)
├── AIR_CAV (120) → M2 Deep Research + Literature/Databases
├── ALPHA (130)   → Heavy Compute + ML/Computation Skills
├── BRAVO (130)   → Rapid Deployment + Visualization/Integration
└── CHARLIE (130) → 24 Review Agents + Bioinformatics/Chemistry
```

---

## REPOS CLONED (Submodules)

| Repo                             | Purpose               | Status        |
| -------------------------------- | --------------------- | ------------- |
| `claude-scientific-skills`       | 117 scientific skills | ✅ Loaded     |
| `compounding-engineering-plugin` | 24 review agents      | ✅ Loaded     |
| `m2-deep-research`               | Multi-agent research  | ✅ Integrated |

---

## KEY FILES FOR NEXT SESSION

### Core Integration Files

```
agents/scientific_skills_loader.py    # 117 skills, 15 domains
agents/compounding_integration.py     # 24 reviewers, 5 categories
agents/deep_research_integration.py   # M2 research layer
prompts/antigravity_system.py         # Skill injection + review layer
prompts/battle_drills.py              # 6 battle drills
agents/autoresearch.py              # 600 agents, full combat posture
agents/cavalry_squadron.py            # Troop structure
agents/gemini_executor.py             # Real Gemini API calls
bin/n-autoresearch/Kosmos/BioAgents-server              # HTTP server :8600
```

### CLAUDE.md (Project Memory)

```
/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/shadowtag_v4-fastapi-services/CLAUDE.md
```

---

## STARTUP SEQUENCE (Next Session)

```bash
# 1. Start n-autoresearch/Kosmos/BioAgents server
cd "/Users/pikeymickey/Documents/Claude Code/Code/Claude Demo/shadowtag_v4-fastapi-services"
python3 bin/n-autoresearch/Kosmos/BioAgents-server

# 2. Verify squadron
curl http://localhost:8600/squadron

# 3. Check stats
curl http://localhost:8600/jura/stats
```

---

## 0% ERROR RATE ARCHITECTURE (Operational)

```
Task → OPORD → METT-TC → Battle Drill
            ↓
┌──────────────────────────────────────┐
│  LAYER 1: Scientific Skills (117)    │
└──────────────────────────────────────┘
            ↓
┌──────────────────────────────────────┐
│  LAYER 2: M2 Deep Research (AIR_CAV) │
└──────────────────────────────────────┘
            ↓
┌──────────────────────────────────────┐
│  LAYER 3: Review Panel (CHARLIE, 24) │
└──────────────────────────────────────┘
            ↓
┌──────────────────────────────────────┐
│  LAYER 4: Vehicle Consensus (600)    │
└──────────────────────────────────────┘
            ↓
        0% ERROR RATE
```

---

## Updated Squadron Structure (Full Combat Posture)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  n-autoresearch/Kosmos/BioAgents CAVALRY SQUADRON :: FULL COMBAT POSTURE (600 ACTIVE 24/7)    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  HHT (90) ─────────── Judge #6, S-1 to S-6, Scientific Skills (Clinical)    │
│      │                                                                       │
│      ├── AIR_CAV (120) ── M2 Deep Research Integration                       │
│      │                    - Supervisor (Apache) → Query decomposition        │
│      │                    - Planning (Scout) → Subquery generation          │
│      │                    - Search (Lift) → Parallel retrieval              │
│      │                                                                       │
│      ├── ALPHA (130) ──── Heavy Compute + Scientific Skills                  │
│      │                    - Bioinformatics, Cheminformatics, ML             │
│      │                    - gemini-2.5-pro-preview-06-05                     │
│      │                                                                       │
│      ├── BRAVO (130) ──── Rapid Deployment + Scientific Skills               │
│      │                    - `/work` integration from compounding-engineering │
│      │                    - ML/AI rapid prototyping                          │
│      │                    - gemini-2.5-flash-preview-05-20                   │
│      │                                                                       │
│      └── CHARLIE (130) ── Protected Review Ops                               │
│                           - 17 Specialized Reviewers (compounding-eng)       │
│                           - `/review` multi-agent code review               │
│                           - Security, Performance, Architecture             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Files

### Phase 3 Files to Create/Modify

| File                                  | Action | Purpose                                  |
| ------------------------------------- | ------ | ---------------------------------------- |
| `agents/autoresearch.py`            | MODIFY | Remove shift rotation                    |
| `agents/compounding_integration.py`   | CREATE | Integrate 17 reviewers                   |
| `agents/deep_research_integration.py` | CREATE | Integrate M2 research                    |
| `agents/scientific_skills_loader.py`  | CREATE | Load 123 skills                          |
| `prompts/antigravity_system.py`       | MODIFY | Add skill injection slot                 |
| `bin/n-autoresearch/Kosmos/BioAgents-server`            | MODIFY | Remove shift endpoints, add skill loader |

---

## 0% Error Rate Architecture

**Current**: Unanimous vehicle consensus (per Kosmos paper)
**Enhanced**: Multi-layer validation with integrated plugins

```
Task → OPORD → METT-TC → Battle Drill Selection
                    ↓
        ┌──────────────────────────────────────┐
        │  LAYER 1: Scientific Skills Injection │
        │  (123 domain expertise prompts)       │
        └──────────────────────────────────────┘
                    ↓
        ┌──────────────────────────────────────┐
        │  LAYER 2: M2 Deep Research (AIR_CAV) │
        │  (Multi-agent research validation)    │
        └──────────────────────────────────────┘
                    ↓
        ┌──────────────────────────────────────┐
        │  LAYER 3: Compounding Review (CHARLIE)│
        │  (17 specialized code reviewers)      │
        └──────────────────────────────────────┘
                    ↓
        ┌──────────────────────────────────────┐
        │  LAYER 4: Vehicle Consensus          │
        │  (600 agents, unanimous = APPROVE)    │
        └──────────────────────────────────────┘
                    ↓
              0% ERROR RATE
```

---

## Phase 2 Summary (COMPLETED)

**Completed in Phase 1**:

- OPORD Generator (`agents/opord_generator.py`)
- Cavalry Squadron (`agents/cavalry_squadron.py`)
- Vehicle Crews with voting (`agents/vehicle_crews.py`)
- Server integration (`bin/n-autoresearch/Kosmos/BioAgents-server`)

**Phase 2 Deliverables**:

1. Antigravity system prompt file
2. METT-TC integration for dynamic prompts
3. Wire prompts into n-autoresearch/Kosmos/BioAgents execution

---

## Antigravity Prompt Architecture

### File: `prompts/antigravity_system.py`

```python
ANTIGRAVITY_SYSTEM_PROMPT = """
▛///▞ ANTIGRAVITY :: {troop_name} @ {vehicle_callsign}
Date: {date}

▛///▞ DECISION FRAMEWORK
ID:       Maximum value extraction, no self-imposed limits
SUPEREGO: Judge #6 gates (legal/regulatory/financial/security)
EGO:      Purpose → Reasons → Brakes → Execute

▛///▞ METT-TC INJECTION
Mission:  {mission_type} - {mission_statement}
Enemy:    {blockers}
Terrain:  {codebase_context}
Troops:   {available_agents} agents, {vehicle_type}
Time:     {timeout}s, {token_budget} tokens
Civilian: {compliance_requirements}

▛///▞ BATTLE DRILL: {battle_drill}
{drill_tasks}

▛///▞ VEHICLE CONSENSUS
You are crew member {agent_index}/{crew_size} in {callsign}.
After analysis, vote: APPROVE / REJECT / ABSTAIN
Unanimous vehicle consensus required for GO.
"""
```

### METT-TC Dynamic Injection

```python
class METTTCContext:
    mission: str           # From OPORD Para 2
    enemy: List[str]       # Blockers, rate limits, complexity
    terrain: Dict          # File paths, dependencies, APIs
    troops: int            # Available agents
    time: int              # Timeout seconds
    civilian: List[str]    # Compliance gates, user data concerns

    def inject(self, base_prompt: str) -> str:
        return base_prompt.format(**self.__dict__)
```

---

## Battle Drill Library

| Drill                 | Trigger                | Tasks                                                             |
| --------------------- | ---------------------- | ----------------------------------------------------------------- |
| **ATTACK_FEATURE**    | MissionType.ATTACK     | Scout codebase → Identify integration → Implement → Test → Deploy |
| **DEFEND_BUG**        | MissionType.DEFEND     | Assess threat → Isolate → Patch → Validate → Harden               |
| **RECON_RESEARCH**    | MissionType.RECON      | Scan codebase → Pattern match → Deep analyze → Document           |
| **MOVEMENT_REFACTOR** | MissionType.MOVEMENT   | Map deps → Incremental move → Verify integrity                    |
| **REACT_TO_CONTACT**  | Error during execution | Halt → Assess → FRAGO → Resume or abort                           |

---

## Implementation Files

| File                            | Purpose                               |
| ------------------------------- | ------------------------------------- |
| `prompts/antigravity_system.py` | Base prompt with METT-TC slots        |
| `prompts/battle_drills.py`      | Drill definitions per mission type    |
| `agents/mett_tc.py`             | Context builder for dynamic injection |
| `agents/opord_generator.py`     | Update to generate METT-TC context    |
| `bin/n-autoresearch/Kosmos/BioAgents-server`      | Wire prompts into `/mission` endpoint |

---

## Execution Flow (Real Gemini Calls)

```
User Task
    ↓
S-2 classifies → MissionType
    ↓
METT-TC Context built
    ↓
Battle Drill selected
    ↓
Per Vehicle (parallel async):
  1. Build prompt with antigravity_system.format()
  2. Call Gemini API (flash for line troops, pro for HHT/AIR CAV)
  3. Parse response for APPROVE/REJECT/ABSTAIN
  4. Aggregate at vehicle level
    ↓
Squadron consensus (134 vehicles)
    ↓
Result with cost tracking
```

---

## Gemini Execution Layer

### File: `agents/gemini_executor.py`

```python
import google.generativeai as genai
from typing import List, Dict
import asyncio

class GeminiVehicleExecutor:
    """Execute Gemini calls per vehicle crew"""

    MODELS = {
        "pro": "gemini-2.5-pro-preview-06-05",
        "flash": "gemini-2.5-flash-preview-05-20",
    }

    async def execute_vehicle(
        self,
        vehicle: Vehicle,
        prompt: str,
        task: str,
    ) -> Dict:
        """Execute task for all agents in vehicle, return consensus"""

        model = self.MODELS["pro" if vehicle.jura_tier == "pro" else "flash"]

        # Call Gemini for each agent (parallel)
        responses = await asyncio.gather(*[
            self._call_gemini(model, prompt, task, agent.agent_id)
            for agent in vehicle.get_all_agents()
        ])

        # Parse votes from responses
        votes = [self._parse_vote(r) for r in responses]

        # Unanimous = all approve
        decision = "APPROVE" if all(v == "APPROVE" for v in votes) else "REJECT"

        return {
            "vehicle_id": vehicle.vehicle_id,
            "callsign": vehicle.callsign,
            "decision": decision,
            "votes": votes,
            "responses": responses,
            "model": model,
        }

    async def _call_gemini(self, model: str, prompt: str, task: str, agent_id: str) -> str:
        """Make actual Gemini API call"""
        client = genai.GenerativeModel(model)
        response = await client.generate_content_async(
            f"{prompt}\n\nTASK: {task}\n\nAgent {agent_id} analysis and vote:"
        )
        return response.text

    def _parse_vote(self, response: str) -> str:
        """Extract vote from response"""
        response_upper = response.upper()
        if "APPROVE" in response_upper:
            return "APPROVE"
        elif "REJECT" in response_upper:
            return "REJECT"
        return "ABSTAIN"
```

---

## Cost Estimation

Per mission with 134 vehicles, ~600 agents:

| Tier      | Model            | Agents | Input Tokens | Output Tokens | Cost               |
| --------- | ---------------- | ------ | ------------ | ------------- | ------------------ |
| PRO       | gemini-2.5-pro   | 210    | ~500 each    | ~200 each     | ~$0.50             |
| FLASH     | gemini-2.5-flash | 390    | ~500 each    | ~200 each     | ~$0.05             |
| **Total** |                  | 600    | 300K         | 120K          | **~$0.55/mission** |

Rate limit fallback: ID → EGO → SUPEREGO chain already implemented.

---

## Why Cavalry Squadron (Not Battalion)

| Criteria      | Infantry Battalion   | Cavalry Squadron          | Winner  |
| ------------- | -------------------- | ------------------------- | ------- |
| Size          | 600-800              | 300-500 (scalable)        | Cavalry |
| Speed         | Dismount-focused     | Mounted mobility          | Cavalry |
| Recon         | Limited              | Primary mission           | Cavalry |
| Combined Arms | Separate attachments | Organic (Air+Armor+Scout) | Cavalry |
| Anonymity     | Formation-based      | Vehicle-based crews       | Cavalry |
| Error Rate    | Standard             | 0% via vehicle redundancy | Cavalry |

---

## Existing Doctrine Assets (Already Implemented)

| Asset                   | Location                                                          | Cavalry Adaptation      |
| ----------------------- | ----------------------------------------------------------------- | ----------------------- |
| FM 6-0 Adaptation       | `.claude/docs/fm-6-0-agent-swarm-adaptation.md`                   | Add Cavalry ops         |
| ADP 6-22 Leadership     | `.claude/docs/adp-6-22-agent-leadership.md`                       | Vehicle commander model |
| OPORD Templates         | `.claude/skills/agent-orchestration/resources/opord-templates.md` | Add FRAGO templates     |
| Ranger Handbook Tactics | `.claude/docs/ranger-handbook-swarm-tactics.md`                   | Add Cavalry TTPs        |

---

## CAVALRY SQUADRON "n-autoresearch/Kosmos/BioAgents" (600 agents)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HHT (HEADQUARTERS & HEADQUARTERS TROOP) - 90 agents                        │
│  Model: gemini-2.5-pro-preview-06-05 (Governance tier)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Squadron Commander: Judge #6 (1 master agent - FINAL AUTHORITY)            │
│  XO: JR Engine (1 agent - Purpose/Reasons/Brakes)                           │
│                                                                              │
│  S-1 (Personnel):     12 agents - Agent lifecycle, shift rotation           │
│  S-2 (Intel):         15 agents - Research, competitive analysis            │
│  S-3 (Operations):    15 agents - OPORD generation, mission planning        │
│  S-4 (Logistics):     12 agents - Resource allocation, cost tracking        │
│  S-6 (Comms):         12 agents - API integration, MCP coordination         │
│  FSE (Fire Support):  10 agents - Precision strikes, escalation             │
│  Scout PLT (organic): 12 agents - HQ reconnaissance                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    │                               │                               │
    ▼                               ▼                               ▼
┌───────────────────┐    ┌───────────────────┐    ┌───────────────────┐
│ AIR CAV TROOP     │    │ ALPHA TROOP       │    │ BRAVO TROOP       │
│ "AERIAL SCOUTS"   │    │ "ARMOR" (Abrams)  │    │ "STRYKER"         │
│ 120 agents        │    │ 130 agents        │    │ 130 agents        │
│ gemini-2.5-pro    │    │ gemini-2.5-flash  │    │ gemini-2.5-flash  │
├───────────────────┤    ├───────────────────┤    ├───────────────────┤
│ Attack Helo (40)  │    │ Tank PLT (43)     │    │ Scout PLT (43)    │
│ - Apache pairs    │    │ - Heavy compute   │    │ - Fast recon      │
│ Scout/Obs (40)    │    │ Scout PLT (43)    │    │ Rifle PLT (43)    │
│ - Research        │    │ - Ground recon    │    │ - Execution       │
│ Lift PLT (40)     │    │ Mortar (44)       │    │ MGS (44)          │
│ - Data transport  │    │ - Indirect fire   │    │ - Mobile support  │
└───────────────────┘    └───────────────────┘    └───────────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │ CHARLIE TROOP     │
                    │ "BRADLEY" (IFV)   │
                    │ 130 agents        │
                    │ gemini-2.5-flash  │
                    ├───────────────────┤
                    │ Bradley PLT (43)  │
                    │ - Protected ops   │
                    │ Dismount PLT (43) │
                    │ - Detailed work   │
                    │ TOW Section (44)  │
                    │ - Long-range      │
                    └───────────────────┘
```

---

## Vehicle-Based Agent Groupings (Safety & Companionship)

Agents "ride" in virtual vehicles - never operate alone:

| Vehicle              | Agents | Crew | Dismounts | Use Case                          |
| -------------------- | ------ | ---- | --------- | --------------------------------- |
| **M1 Abrams**        | 4      | 4    | 0         | Heavy computation, no dismount    |
| **M2 Bradley**       | 9      | 3    | 6         | Protected ops + detailed work     |
| **M1126 Stryker**    | 11     | 2    | 9         | Rapid deployment, max parallelism |
| **AH-64 Apache**     | 2      | 2    | 0         | Attack pairs, always redundant    |
| **UH-60 Black Hawk** | 14     | 4    | 10        | Mass transport, lift operations   |
| **OH-58 Kiowa**      | 2      | 2    | 0         | Scout pairs, recon                |

### Anonymous Voting via Vehicle Crews

```python
class VehicleCrew:
    """
    Agents in same vehicle vote anonymously.
    All votes aggregated at vehicle level before squadron-level consensus.

    Kosmos Paper Integration: 0% error rate via unanimous vehicle consensus.
    """

    def anonymous_vote(self, decision: dict) -> dict:
        # Each agent votes independently
        votes = [agent.vote(decision) for agent in self.crew]

        # Vehicle-level aggregation (anonymous to squadron)
        vehicle_vote = {
            "vehicle_id": self.id,
            "approve": sum(1 for v in votes if v == "approve"),
            "reject": sum(1 for v in votes if v == "reject"),
            "abstain": sum(1 for v in votes if v == "abstain"),
            # Individual votes NOT exposed - anonymous
        }

        # 0% error: Require unanimous for vehicle to vote "approve"
        vehicle_vote["decision"] = "approve" if vehicle_vote["approve"] == len(self.crew) else "reject"

        return vehicle_vote
```

---

## OPORD Automation (Priority #1)

### Why OPORD Format for Agent Swarms

1. **Battle-Tested**: 5-paragraph format proven across centuries of military ops
2. **Proven Structure**: G1-G9 staff sections map to agent specializations
3. **Mission Command**: Decentralized execution with centralized intent (perfect for distributed AI)
4. **Institutional Memory**: Running Estimate = Context Index + Corpus Guard
5. **Continuous Improvement**: AAR process already baked in

### OPORD Generator Class

```python
# agents/opord_generator.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class MissionType(str, Enum):
    ATTACK = "attack"           # New feature development
    DEFEND = "defend"           # Bug fixing, security patching
    RECONNAISSANCE = "recon"    # Research, analysis
    MOVEMENT = "movement"       # Refactoring, migration
    STABILITY = "stability"     # Maintenance, optimization

@dataclass
class OPORD:
    """5-Paragraph Operations Order for Agent Swarm"""

    # Para 1: SITUATION
    situation: Dict[str, any] = None  # Enemy (blockers), Friendly (resources), Attachments

    # Para 2: MISSION
    mission: str = ""                  # Who, What, When, Where, Why (5 W's)

    # Para 3: EXECUTION
    commander_intent: str = ""         # End state vision
    concept_of_operations: str = ""    # How we'll accomplish
    tasks_to_subordinate_units: Dict[str, List[str]] = None  # Troop assignments
    coordinating_instructions: List[str] = None  # Timing, priorities

    # Para 4: SERVICE SUPPORT
    logistics: Dict[str, any] = None   # API keys, compute budget, tokens

    # Para 5: COMMAND AND SIGNAL
    command: Dict[str, str] = None     # Who's in charge at each echelon
    signal: Dict[str, str] = None      # Communication protocols


class OPORDGenerator:
    """
    Generates OPORDs for n-autoresearch/Kosmos/BioAgents Cavalry Squadron.
    Maps user tasks to military mission format.
    """

    def __init__(self, squadron_config: dict):
        self.squadron = squadron_config
        self.hht = squadron_config.get("HHT", {})

    def generate(self, task: str, context: dict = None) -> OPORD:
        """Generate OPORD from user task"""

        # S-2 Intel: Analyze task
        mission_type = self._classify_mission(task)

        # S-3 Ops: Build OPORD
        opord = OPORD(
            situation=self._build_situation(context),
            mission=self._build_mission(task, mission_type),
            commander_intent=self._build_intent(task),
            concept_of_operations=self._build_concept(mission_type),
            tasks_to_subordinate_units=self._assign_troops(mission_type),
            coordinating_instructions=self._build_coord_instructions(),
            logistics=self._build_logistics(context),
            command=self._build_command_structure(),
            signal=self._build_signal_plan(),
        )

        return opord

    def _classify_mission(self, task: str) -> MissionType:
        """S-2 classifies mission type from task description"""
        task_lower = task.lower()

        if any(w in task_lower for w in ["add", "create", "implement", "build"]):
            return MissionType.ATTACK
        elif any(w in task_lower for w in ["fix", "bug", "patch", "secure"]):
            return MissionType.DEFEND
        elif any(w in task_lower for w in ["research", "analyze", "find", "search"]):
            return MissionType.RECONNAISSANCE
        elif any(w in task_lower for w in ["refactor", "migrate", "move", "rename"]):
            return MissionType.MOVEMENT
        else:
            return MissionType.STABILITY

    def _assign_troops(self, mission_type: MissionType) -> Dict[str, List[str]]:
        """S-3 assigns troops based on mission type"""

        assignments = {
            MissionType.ATTACK: {
                "AIR_CAV": ["Aerial recon of codebase", "Identify integration points"],
                "ALPHA_ARMOR": ["Heavy compute - core implementation"],
                "BRAVO_STRYKER": ["Rapid prototyping", "Test coverage"],
                "CHARLIE_BRADLEY": ["Protected deployment", "Rollback plan"],
            },
            MissionType.DEFEND: {
                "AIR_CAV": ["Threat assessment", "Attack vector analysis"],
                "ALPHA_ARMOR": ["Patch development", "Hardening"],
                "BRAVO_STRYKER": ["Quick response fixes"],
                "CHARLIE_BRADLEY": ["Security validation", "Pen testing"],
            },
            MissionType.RECONNAISSANCE: {
                "AIR_CAV": ["Primary recon - full codebase scan"],
                "ALPHA_ARMOR": ["Deep analysis on findings"],
                "BRAVO_STRYKER": ["Parallel search threads"],
                "CHARLIE_BRADLEY": ["Document findings"],
            },
            MissionType.MOVEMENT: {
                "AIR_CAV": ["Map dependencies", "Impact analysis"],
                "ALPHA_ARMOR": ["Execute migration"],
                "BRAVO_STRYKER": ["Incremental moves"],
                "CHARLIE_BRADLEY": ["Verify integrity post-move"],
            },
            MissionType.STABILITY: {
                "AIR_CAV": ["Monitor performance"],
                "ALPHA_ARMOR": ["Optimization cycles"],
                "BRAVO_STRYKER": ["Maintenance tasks"],
                "CHARLIE_BRADLEY": ["Quality assurance"],
            },
        }

        return assignments.get(mission_type, assignments[MissionType.STABILITY])
```

### FRAGO (Fragmentary Order) for Dynamic Updates

```python
@dataclass
class FRAGO:
    """
    Fragmentary Order - updates to existing OPORD.
    Used for mid-mission adjustments without full replanning.
    """
    parent_opord_id: str
    changes: Dict[str, any]
    effective_immediately: bool = True
    reason: str = ""

    def apply_to(self, opord: OPORD) -> OPORD:
        """Apply FRAGO changes to existing OPORD"""
        for field, value in self.changes.items():
            if hasattr(opord, field):
                setattr(opord, field, value)
        return opord
```

### TLP (Troop Leading Procedures) + OODA Integration

```python
class TroopLeadingProcedures:
    """
    8-Step TLP with OODA loop embedded for tactical agility.
    Each step maps to Squadron staff functions.
    """

    STEPS = [
        ("receive_mission", "S-3", "OBSERVE"),      # Receive & understand
        ("issue_warning_order", "S-3", "OBSERVE"),  # Alert troops
        ("make_tentative_plan", "S-3", "ORIENT"),   # Initial planning
        ("initiate_movement", "S-4", "ORIENT"),     # Resource positioning
        ("conduct_reconnaissance", "S-2", "ORIENT"), # Gather intel
        ("complete_the_plan", "S-3", "DECIDE"),     # Finalize OPORD
        ("issue_opord", "CDR", "DECIDE"),           # Commander approves
        ("supervise_and_refine", "XO", "ACT"),      # Execute & adjust
    ]

    async def execute(self, task: str, squadron) -> OPORD:
        """Execute TLP to generate and issue OPORD"""

        context = {}

        for step_name, staff_section, ooda_phase in self.STEPS:
            # Get responsible agents from staff section
            agents = squadron.get_section(staff_section)

            # Execute step with OODA phase awareness
            result = await self._execute_step(
                step_name, agents, task, context, ooda_phase
            )
            context[step_name] = result

            # OODA: Loop back if needed
            if ooda_phase == "ACT" and result.get("needs_replan"):
                return await self.execute(task, squadron)  # Full replan

        return context["complete_the_plan"]
```

### Alternative Leadership Strategies Considered

| Strategy                           | Pros                                              | Cons                              | Verdict                  |
| ---------------------------------- | ------------------------------------------------- | --------------------------------- | ------------------------ |
| **Army Battalion (Current)**       | Proven at scale, clear hierarchy, doctrine exists | More rigid, slower adaptation     | **KEEP**                 |
| **OODA Loop (Boyd)**               | Faster iteration, parallel execution              | No org structure                  | **HYBRID** - Add to TLP  |
| **Spotify Model**                  | Autonomous squads, less hierarchy                 | Designed for humans, not AI       | Skip                     |
| **Amazon Two-Pizza**               | Small teams, fast decisions                       | 75 teams = coordination nightmare | Skip                     |
| **Netflix Freedom/Responsibility** | High autonomy                                     | No guard rails for AI             | Skip                     |
| **Google SRE**                     | Error budgets, reliability focus                  | Operations only, no strategy      | **HYBRID** - Add metrics |

### Recommendation: HYBRID Approach

```
ARMY DOCTRINE (Structure) + OODA (Speed) + SRE (Reliability)
```

---

## Proposed Battalion Structure for 600 Agents

```
┌─────────────────────────────────────────────────────────────────────┐
│  BATTALION HEADQUARTERS (BN HQ) - 60 agents                         │
│  Model: gemini-2.5-pro-preview-06-05 (Governance tier)              │
├─────────────────────────────────────────────────────────────────────┤
│  S-1 (Personnel):    10 agents - Agent lifecycle, shift rotation    │
│  S-2 (Intel):        10 agents - Research, competitive analysis     │
│  S-3 (Operations):   10 agents - Mission planning, OPORD issue      │
│  S-4 (Logistics):    10 agents - Resource allocation, cost tracking │
│  S-5 (Plans):        10 agents - Architecture, strategic planning   │
│  S-6 (Comms):        10 agents - Integration, API coordination      │
└─────────────────────────────────────────────────────────────────────┘
                                 │
     ┌───────────────────────────┼───────────────────────────┐
     │                           │                           │
     ▼                           ▼                           ▼
┌─────────────┐           ┌─────────────┐           ┌─────────────┐
│ ALPHA CO    │           │ BRAVO CO    │           │ CHARLIE CO  │
│ (BACKEND)   │           │ (FRONTEND)  │           │ (SECURITY)  │
│ 135 agents  │           │ 135 agents  │           │ 135 agents  │
├─────────────┤           ├─────────────┤           ├─────────────┤
│ 1st PLT:    │           │ 1st PLT:    │           │ 1st PLT:    │
│   API (45)  │           │   UI/UX (45)│           │   PenTest   │
│ 2nd PLT:    │           │ 2nd PLT:    │           │ 2nd PLT:    │
│   DB (45)   │           │   Mobile(45)│           │   CodeRev   │
│ 3rd PLT:    │           │ 3rd PLT:    │           │ 3rd PLT:    │
│   Svc (45)  │           │   Integ (45)│           │   Comply    │
└─────────────┘           └─────────────┘           └─────────────┘
     │                           │                           │
     └───────────────────────────┼───────────────────────────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │ DELTA CO (ML/AI)    │
                     │ 135 agents          │
                     ├─────────────────────┤
                     │ 1st PLT: Training   │
                     │ 2nd PLT: Inference  │
                     │ 3rd PLT: Evaluation │
                     └─────────────────────┘

Model Distribution:
- HQ Company (60): gemini-2.5-pro-preview-06-05 (Governance)
- Line Companies (540): gemini-2.5-flash-preview-05-20 (Execution)
```

---

## Career Field Mapping to Agent Specialization

| Army MOS              | Agent Squad  | Role                               | Count |
| --------------------- | ------------ | ---------------------------------- | ----- |
| 11B (Infantry)        | EXECUTION    | Bulk task processing               | 360   |
| 35F (Intel Analyst)   | RESEARCH     | Data analysis, pattern recognition | 45    |
| 25B (IT Specialist)   | DEVOPS       | Infrastructure, deployment         | 45    |
| 17C (Cyber Ops)       | SECURITY     | Penetration testing, code review   | 45    |
| 42A (HR Specialist)   | ADMIN        | Agent lifecycle, shift management  | 30    |
| 91B (Mechanic)        | MAINTENANCE  | Error recovery, self-healing       | 30    |
| 27D (Paralegal)       | COMPLIANCE   | Legal review, governance           | 15    |
| 12B (Combat Engineer) | ARCHITECTURE | System design                      | 30    |

---

## OPORD Integration with JURA Tiers

```python
# Proposed mapping in bin/n-autoresearch/Kosmos/BioAgents-server

BATTALION_JURA_MAPPING = {
    "S3_OPS": {"tier": "pro", "model": "gemini-2.5-pro-preview-06-05"},
    "ALPHA_CO": {"tier": "flash", "model": "gemini-2.5-flash-preview-05-20"},
    "BRAVO_CO": {"tier": "flash", "model": "gemini-2.5-flash-preview-05-20"},
    "CHARLIE_CO": {"tier": "pro", "model": "gemini-2.5-pro-preview-06-05"},  # Security = Pro
    "DELTA_CO": {"tier": "flash", "model": "gemini-2.5-flash-preview-05-20"},
}
```

---

## Implementation Files to Modify

1. **`bin/n-autoresearch/Kosmos/BioAgents-server`** - Add battalion structure
2. **`agents/autoresearch.py`** - Add company/platoon routing
3. **`src/shadowtag_v4/jura/limiter.py`** - Map companies to JURA tiers
4. **`.claude/docs/battalion-structure.md`** - New doctrine document
5. **`prompts/n-autoresearch/Kosmos/BioAgents_universal.txt`** - Add OPORD awareness

---

## Automation: Display "🐒 n-autoresearch/Kosmos/BioAgents THINKING" Status

### Option 1: Add to CLAUDE.md (Recommended)

```markdown
## n-autoresearch/Kosmos/BioAgents Integration

When processing tasks, always display status:

- "🐒 n-autoresearch/Kosmos/BioAgents THINKING" when sending to n-autoresearch/Kosmos/BioAgents
- Include: tier, agents assigned, model, latency
```

### Option 2: Hook in `.claude/hooks/`

Create `.claude/hooks/n-autoresearch/Kosmos/BioAgents-status.sh` to inject status automatically.

---

## Gemini 2.5 Pro Preview Usage

Currently active in:

- `bin/n-autoresearch/Kosmos/BioAgents-server` (BULK + GOVERNANCE tiers)
- `src/shadowtag_v4/services/gemini_core.py` (GeminiAntigravity with fallback)
- `atomic_pipeline/clients/gemini_client.py` (API client)

All using rate-limit fallback chain:

1. gemini-2.5-pro-preview-06-05 (ID tier)
2. gemini-2.5-flash-preview-05-20 (EGO tier)
3. gemini-2.0-flash (SUPEREGO tier - guaranteed)

---

## User Decisions (Confirmed)

| Decision           | Choice                                             |
| ------------------ | -------------------------------------------------- |
| **Structure**      | Cavalry Squadron (Air + Armor + Stryker + Bradley) |
| **Priority**       | OPORD Automation first                             |
| **Agent Grouping** | Vehicle-based for companionship/safety             |
| **Voting**         | Anonymous via vehicle crews                        |
| **Error Rate**     | 0% via unanimous vehicle consensus (Kosmos paper)  |

---

## Implementation Order

### Phase 1: OPORD Automation (Priority)

1. Create `agents/opord_generator.py` with OPORD, FRAGO, TLP classes
2. Create `agents/cavalry_squadron.py` with vehicle/troop structures
3. Add mission classification and troop assignment logic

### Phase 2: Cavalry Squadron Structure

4. Update `bin/n-autoresearch/Kosmos/BioAgents-server` with squadron routing
5. Create `agents/vehicle_crews.py` with anonymous voting
6. Map vehicles to JURA tiers (Abrams=Pro, Stryker=Flash, etc.)

### Phase 3: Integration

7. Update `agents/autoresearch.py` to use squadron dispatch
8. Add squadron status to `/jura/stats` endpoint
9. Create `.claude/docs/cavalry-squadron-doctrine.md`

### Phase 4: Status Display

10. Add "n-autoresearch/Kosmos/BioAgents THINKING" status indicator
11. Show: tier, troop assigned, vehicle count, model, latency

---

## Critical Files to Modify

| File                         | Changes                                    |
| ---------------------------- | ------------------------------------------ |
| `agents/opord_generator.py`  | **NEW** - OPORD, FRAGO, TLP classes        |
| `agents/cavalry_squadron.py` | **NEW** - Squadron/Troop/Vehicle structure |
| `agents/vehicle_crews.py`    | **NEW** - Anonymous voting engine          |
| `bin/n-autoresearch/Kosmos/BioAgents-server`   | Add squadron routing, status endpoint      |
| `agents/autoresearch.py`   | Integrate squadron dispatch                |
| `src/shadowtag_v4/jura/limiter.py`  | Map vehicle types to JURA tiers            |
