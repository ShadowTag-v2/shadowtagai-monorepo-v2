# PROJECT_KNOWLEDGE.md - PNKLN Infrastructure

**Claude Code Infrastructure for PNKLN Core Stack**
**Version**: 1.0.0
**Date**: 2024-11-15

---

## Executive Summary

This repository implements a comprehensive Claude Code infrastructure system adapted from proven patterns that enabled a solo developer to transform a 100k LOC legacy app into a 300-400k LOC modern TypeScript system in 6 months. The infrastructure solves Claude Code's fatal flaw: **skills sit unused unless forced to activate**.

### Core Breakthrough

**The Problem**: Claude repeatedly ignores documented patterns and skills, leading to inconsistent code quality across large codebases.

**The Solution**: A TypeScript hooks system that analyzes every prompt and file operation, automatically injecting skill suggestions and enforcing quality gates. Result: **zero errors escape** into the codebase.

### System Components

1. **Hooks System**: Automated quality pipeline (formatting, type checking, coverage gates)
2. **Skills Auto-Activation**: Context-aware skill suggestions based on triggers
3. **Dev Docs System**: State management for context resets (3-file pattern)
4. **Specialized Agents**: Auto-rollback, code review, experiment analysis
5. **Board Automation**: Automatic board sync from task completion
6. **Coverage Gate**: Judge #6 enforcement (98% coverage required)

---

## Architecture Overview

### Directory Structure

```
ShadowTag-v2-fastapi-services/
├── .claude/
│   ├── hooks/                    # Quality automation hooks
│   │   ├── post-tool-use-file-tracker.ts
│   │   ├── stop-python-quality-pipeline.ts
│   │   ├── stop-board-sync.ts
│   │   └── user-prompt-submit-skill-activator.ts
│   ├── skills/                   # Auto-activating skills (<500 lines)
│   │   ├── skill-rules.json      # Trigger definitions
│   │   ├── python-dev-guidelines.md
│   │   ├── vertex-ai-workbench.md
│   │   ├── ml-experiment-tracking.md
│   │   └── resources/            # Progressive disclosure resources
│   │       ├── python-dev-guidelines/
│   │       ├── vertex-ai-workbench/
│   │       └── ...
│   ├── agents/                   # Specialized autonomous agents
│   │   ├── auto-rollback-agent.md
│   │   ├── code-architecture-reviewer.md (TODO)
│   │   └── experiment-analyzer.md (TODO)
│   ├── scripts/                  # Utility scripts attached to skills
│   │   ├── coverage-report.py
│   │   ├── vertex-ai-deploy.py (TODO)
│   │   └── ...
│   ├── dev/                      # Dev docs system
│   │   ├── templates/            # Templates for dev docs
│   │   │   ├── task-plan-template.md
│   │   │   ├── task-context-template.md
│   │   │   ├── task-tasks-template.md
│   │   │   ├── experiment-plan-template.md
│   │   │   ├── experiment-context-template.md
│   │   │   └── experiment-results-template.md
│   │   └── active/               # Active task dev docs
│   │       └── [task-name]/
│   │           ├── [task-name]-plan.md
│   │           ├── [task-name]-context.md
│   │           └── [task-name]-tasks.md
│   └── commands/                 # Slash commands (TODO)
├── src/                          # Application source
├── tests/                        # Tests (≥98% coverage)
├── CLAUDE.md                     # Quick reference
├── PROJECT_KNOWLEDGE.md          # This file
└── ...
```

---

## Hooks System Deep Dive

### Hook Execution Flow

```
User edits file → PostToolUse hooks → File tracker logs change
                                    ↓
User sends prompt → UserPromptSubmit hook → Skill activator analyzes
                                           → Injects skill suggestions
                                           → Claude processes enhanced prompt
                                    ↓
Claude responds → Stop hooks → Python quality pipeline
                             → Ruff formats code
                             → MyPy type checks
                             → Pytest coverage gate (98%)
                             → Board sync (if tasks.md exists)
                             → Results displayed to user
```

### PostToolUse Hooks

#### File Edit Tracker

**File**: `.claude/hooks/post-tool-use-file-tracker.ts`

**Purpose**: Logs all file edits to enable downstream hooks to know which files changed without redundant analysis.

**Tracks**:

- `Edit`, `Write`, `MultiEdit`, `NotebookEdit` operations
- File path, repo, operation type, timestamp

**Output**: `.claude/hooks/edited-files.json`

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "files": [
    {
      "path": "src/services/user_service.py",
      "repo": "ShadowTag-v2-fastapi-services",
      "operation": "Edit",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Stop Hooks

#### Python Quality Pipeline

**File**: `.claude/hooks/stop-python-quality-pipeline.ts`

**Purpose**: Automated quality checks after Claude responds. **#NoMessLeftBehind** pipeline.

**Sequence**:

1. Reads edited files from file tracker
2. Filters for Python files (`.py`)
3. Runs `uv run ruff format .` (auto-formatting)
4. Runs `uv run mypy --strict .` (type checking)
5. Runs `uv run pytest --cov --cov-fail-under=98` (**Judge #6 enforcement**)
6. Displays results with:
   - Format status (✅/⚠️)
   - Type errors (inline if ≤5, suggest agent if >5)
   - Coverage status (✅ pass, ❌ fail with delta)

**Coverage Gate Behavior**:

```
✅ Coverage: 98.5% (threshold: 98%)
```

or

```
❌ COVERAGE GATE FAILED (Judge #6 violation)
   Current: 96.5% | Required: 98% | Delta: -1.7%

🚨 COMMIT BLOCKED: Coverage dropped below 98%
Actions:
  1. Add tests to cover uncovered lines
  2. Launch auto-rollback agent to attempt automatic fixes
  3. After 3 failed attempts, agent will revert changes

Missing coverage: 45, 46, 50-55, 78
```

**Integration**: Triggers `auto-rollback-agent` suggestion on failure.

#### Board Sync

**File**: `.claude/hooks/stop-board-sync.ts`

**Purpose**: Parse task completion from `*-tasks.md` files and update project board automatically.

**Reads**:

- Frontmatter metadata (board_id, epic, priority, status)
- Checkbox completion (- [x] vs - [ ])
- Phase checkpoints

**Actions**:

- Calculates completion percentage
- Determines status based on completion (0% = To Do, 1-99% = In Progress, 100% = Done)
- Posts updates to board API (template - implement for your board)
- Logs sync results

**Example Output**:

```
=== 📊 Board Automation Sync ===

Found 1 task file(s) to process

📋 Task: implement-fraud-detection
   Board: project-board-123
   Epic: EPIC-456
   Progress: 15/20 (75.0%)
   Status: In Progress (no change)
   Checkpoints:
     - Phase 1: Complete
     - Phase 2: Complete
     - Phase 3: Pending

   ✅ Would update board (API integration pending)
```

**Note**: Board API calls are currently commented out. Implement based on your board system (Jira, Linear, GitHub Projects, etc.).

### UserPromptSubmit Hooks

#### Skill Auto-Activator

**File**: `.claude/hooks/user-prompt-submit-skill-activator.ts`

**Purpose**: Analyze prompts BEFORE Claude processes them and inject skill suggestions when triggers match. This solves the #1 problem: **skills won't activate without this hook**.

**Trigger Dimensions**:

1. **Keywords**: Explicit topics (e.g., "vertex ai", "bigquery", "fastapi")
2. **Intent Patterns**: Regex matching actions (e.g., `create.*route`, `train.*model`)
3. **File Patterns**: Recently edited files (e.g., `**/ml/**/*.py`)
4. **Content Patterns**: Code patterns in files (e.g., `from google.cloud import aiplatform`)

**Loads**: `.claude/skills/skill-rules.json`

**Output**: Enhanced prompt with skill recommendations prepended:

```
=== 💡 Skill Recommendations (Auto-Activated) ===

The following skills may be relevant for this task:

**vertex-ai-workbench** (high priority)
  Vertex AI Workbench patterns for data prep, model training, deployment, and monitoring
  Triggered by: keyword: "vertex ai", intent: "train.*model"
  Consider loading: /skill vertex-ai-workbench

**python-dev-guidelines** (high priority)
  Core Python development patterns, FastAPI best practices, async/await, type hints, error handling
  Triggered by: file pattern: "**/*.py"
  Consider loading: /skill python-dev-guidelines

=== End Skill Recommendations ===

[original user prompt]
```

**Result**: Claude sees skill suggestions and context, dramatically improving adherence to best practices.

---

## Skills System Deep Dive

### The 500-Line Rule

**Problem**: Large skills (1,500+ lines) hit context limits and Claude never loads them.

**Solution**: Main skill files under 500 lines with progressive disclosure through resource files.

**Example Structure**:

```
.claude/skills/
├── python-dev-guidelines.md          # 398 lines - main file
└── resources/
    └── python-dev-guidelines/
        ├── architecture.md            # Detailed layered architecture
        ├── error-handling.md          # Comprehensive error patterns
        ├── testing.md                 # Testing strategies
        ├── async-patterns.md          # Advanced async/await
        ├── database.md                # SQLAlchemy patterns
        └── api-design.md              # REST API design
```

**Token Efficiency**: 40-60% improvement for most queries.

### Skill Rules Schema

**File**: `.claude/skills/skill-rules.json`

**Structure**:

```json
{
  "rules": [
    {
      "skill": "python-dev-guidelines",
      "triggers": {
        "keywords": ["python", "fastapi", "async"],
        "intent_patterns": ["create.*route", "implement.*api"],
        "file_patterns": ["**/*.py", "**/routes/**"],
        "content_patterns": ["from fastapi import", "async def"]
      },
      "priority": "high",
      "description": "Core Python development patterns..."
    }
  ]
}
```

**Trigger Logic**:

- **ANY** trigger dimension matching → skill recommended
- Multiple triggers → higher confidence
- Priority determines sort order (high → medium → low)

### Core Skills

#### python-dev-guidelines

**File**: `.claude/skills/python-dev-guidelines.md` (398 lines)

**Scope**: FastAPI, async/await, type hints, error handling, layered architecture

**Resources**:

- `architecture.md` - Detailed layered architecture patterns
- `error-handling.md` - Comprehensive error handling strategies
- `testing.md` - Testing patterns, fixtures, coverage strategies
- `async-patterns.md` - Advanced async/await patterns
- `database.md` - SQLAlchemy patterns, migrations, transactions
- `api-design.md` - REST API design, versioning, documentation

**Auto-activates**: Python files, FastAPI keywords, route/service/API intents

#### vertex-ai-workbench

**File**: `.claude/skills/vertex-ai-workbench.md` (485 lines)

**Scope**: Vertex AI training, deployment, monitoring, cost optimization

**Resources**:

- `data-prep.md` - Data ingestion, preprocessing, feature engineering
- `model-training.md` - Custom training, AutoML, hyperparameter tuning
- `deployment.md` - Endpoint management, A/B testing, canary deployments
- `monitoring.md` - Model monitoring, drift detection, alerts
- `pipelines.md` - Vertex AI Pipelines for MLOps automation

**Auto-activates**: Vertex AI keywords, ML training intents, `**/ml/**/*.py` files

#### ml-experiment-tracking

**Scope**: Experiment tracking, metrics logging, hyperparameter tuning

**Auto-activates**: Experiment keywords, metrics logging, experiment files

#### bigquery-integration

**Scope**: BigQuery data loading, querying, feature engineering

**Auto-activates**: BigQuery keywords, data loading intents, `**/data/**/*.py` files

#### testing-coverage

**Scope**: Pytest patterns, 98% coverage enforcement, mocking strategies

**Auto-activates**: Test keywords, `**/tests/**/*.py` files

---

## Dev Docs System Deep Dive

### The Problem: Extreme Amnesia

Claude suffers from "extreme amnesia"—losing track of objectives mid-implementation, especially after context resets.

### The Solution: 3-File Pattern

**Mandatory files for every task**:

1. **`[task-name]-plan.md`**: The accepted strategic plan
   - Executive summary
   - Phases (Foundation → Implementation → Validation)
   - Architecture decisions
   - Risks & mitigations
   - Timeline

2. **`[task-name]-context.md`**: Current state, the "brain dump"
   - What we're building right now
   - Next immediate steps
   - Key files modified
   - Decisions made during execution
   - Known issues/blockers
   - Agent handoff protocol

3. **`[task-name]-tasks.md`**: Completion checklist
   - Board metadata (board_id, epic, priority)
   - Phase-by-phase tasks with checkboxes
   - Checkpoint timestamps
   - Automated board sync on completion

### Workflow

#### Phase 1: Planning

1. Use **planning mode** or `strategic-plan-architect` agent
2. Research codebase, generate comprehensive plan
3. **Review thoroughly** - catch mistakes before implementation
4. Approve plan when ready

#### Phase 2: Dev Docs Creation

```bash
# Copy templates
cp .claude/dev/templates/task-*.md .claude/dev/active/my-task/

# Or use /create-dev-docs slash command (TODO)
```

Fill in:

- **plan.md**: Paste approved strategic plan, add details
- **context.md**: Initial state, key files, architecture overview
- **tasks.md**: Break plan into checkboxed tasks, add board metadata

#### Phase 3: Implementation

1. Implement following the plan
2. **Update context.md** periodically (decisions, blockers, next steps)
3. **Check off tasks.md** as completed
4. Before context reset: `/update-dev-docs` (TODO) captures state

#### Phase 4: Context Reset Recovery

After compaction:

1. Say "continue" or "resume [task-name]"
2. Claude reads:
   - `plan.md` - strategic direction
   - `context.md` - current state
   - `tasks.md` - what's done, what's next
3. Seamlessly resumes from "Next Immediate Steps"

### ML Experiments Variant

**Use experiment-specific templates for ML work**:

1. **`experiment-[name]-plan.md`**:
   - Hypothesis (we believe X → Y, measured by Z)
   - Dataset, model architecture, hyperparameters
   - Success metrics, validation plan
   - Timeline, risks

2. **`experiment-[name]-context.md`**:
   - Current training status
   - Hyperparameter tuning progress
   - UV lock hash (for reproducibility)
   - Git commit, random seeds
   - Vertex AI experiment ID, TensorBoard link

3. **`experiment-[name]-results.md`**:
   - Hypothesis validation (confirmed/rejected)
   - Final metrics vs baseline
   - Hyperparameter tuning results
   - Error analysis, model interpretability
   - Deployment readiness, monitoring plan

**Board Integration**: Add frontmatter to context/tasks for experiment tracking on board.

---

## Specialized Agents Deep Dive

### Auto-Rollback Agent

**File**: `.claude/agents/auto-rollback-agent.md`

**Purpose**: Enforce Judge #6 (98% coverage) by automatically fixing coverage drops or reverting changes.

**Trigger**: `stop-python-quality-pipeline` detects coverage < 98%

**Strategy**:

1. **Attempt 1-3**: Add tests
   - Analyze uncovered code
   - Identify test gaps
   - Write missing tests (error handling, edge cases)
   - Verify coverage restored
2. **Attempt 4**: Auto-rollback
   - Save patch to `.claude/rollback/changes_TIMESTAMP.patch`
   - Revert changes (`git checkout .` or `git reset --hard`)
   - Create rollback report
   - Notify developer

**Input Format**:

```json
{
  "trigger": "coverage_gate_failure",
  "coverage": {
    "current": 96.5,
    "previous": 98.2,
    "threshold": 98,
    "delta": -1.7
  },
  "uncovered_files": [
    {
      "path": "src/services/user_service.py",
      "missing_lines": [45, 46, 50, 51, 52, 53, 54, 55, 78],
      "coverage": 85
    }
  ]
}
```

**Output Format**:

```json
{
  "attempt": 1,
  "status": "success",
  "coverage_after": 98.5,
  "actions_taken": ["Added test_create_user_with_invalid_email", "Added test_handle_database_error"],
  "tests_added": ["tests/test_user_service.py::test_create_user_with_invalid_email"]
}
```

**Success Metrics**:

- Coverage restored: ✅/❌
- Attempts used: 1-3 (target: ≤2)
- Rollback rate: <10%

### Other Agents (TODO)

#### code-architecture-reviewer

**Purpose**: Review code for architectural best practices
**Trigger**: Manual (`/code-review`) or post-implementation
**Checks**: Layered architecture, error handling, type hints, async patterns

#### experiment-analyzer

**Purpose**: Analyze ML experiment results, generate insights
**Trigger**: After experiment completion
**Output**: Results summary, recommendations for next iteration

#### vertex-ai-deployer

**Purpose**: Automate Vertex AI model deployment
**Trigger**: Manual (`/deploy-model`) or post-training
**Actions**: Upload to registry, create endpoint, configure monitoring

---

## Agent Coordination Protocol

### File-Based State Machine

The dev docs pattern **IS** a state machine architecture:

| Component        | Dev Docs              | AutoGen         | LangGraph               |
| ---------------- | --------------------- | --------------- | ----------------------- |
| **State**        | context.md            | Message history | StateGraph (typed dict) |
| **Tasks**        | tasks.md              | Task queue      | Workflow steps          |
| **Strategy**     | plan.md               | Manager agent   | Graph definition        |
| **Coordination** | Agents update context | GroupChat       | Graph execution         |

### State Management

**context.md Frontmatter** (standardized for agent coordination):

```yaml
workflow: fraud-detection-implementation
current_agent: data-preparation-agent
phase: phase-2-model-training
state: training-in-progress
```

**State History**:

```
- 2024-01-15T10:00:00Z: started → data-prep | data-preparation-agent | Loading BigQuery data
- 2024-01-15T11:30:00Z: data-prep → training | model-training-agent | Data ready, starting training
```

### Agent Handoff

**Protocol** (in context.md):

```markdown
### Agent Handoff Protocol

#### Current Agent Output

**Agent**: data-preparation-agent
**Completed**: 2024-01-15T11:30:00Z
**Work Done**: Loaded 1M rows from BigQuery, applied feature engineering, split 70/15/15
**Files Modified**: src/data/preprocessing.py, configs/data_config.yaml
**Tests Added**: tests/test_preprocessing.py (coverage: 98.5%)
**Status**: Success

#### Next Agent

**Agent**: model-training-agent
**Inputs Required**:

- Training data: gs://pnkln-data/processed/train.csv
- Validation data: gs://pnkln-data/processed/val.csv
- Config: configs/training_config.yaml

**Task**: Train XGBoost model with hyperparameter tuning (20 trials)

**Context**: Data preprocessing complete, features engineered, ready for training
```

### Auto-Orchestration (TODO)

**Stop Hook Enhancement**: Read context.md, auto-launch next agent when current agent completes:

```typescript
// Pseudo-code for future implementation
if (contextUpdated && currentAgentComplete) {
  const nextAgent = parseNextAgentFromContext(contextMd);
  if (nextAgent) {
    launchAgent({
      type: nextAgent.name,
      inputs: nextAgent.inputs,
      task: nextAgent.task,
    });
  }
}
```

---

## Board Automation Deep Dive

### Metadata Schema

**In `*-tasks.md` frontmatter**:

```yaml
board_id: project-board-123 # Board identifier
epic: EPIC-456 # Epic/feature ID
priority: High # High/Medium/Low
assignee: developer-name # Assigned to
labels: [ml, vertex-ai, backend] # Tags
status: In Progress # To Do/In Progress/Review/Done
```

### Checkbox Parsing

The `stop-board-sync` hook parses checkboxes:

- `- [x] Completed task` → completed
- `- [ ] Pending task` → pending

**Completion calculation**:

```
completion_rate = (completed / total) * 100
```

**Status determination**:

- 0% → "To Do"
- 1-99% → "In Progress"
- 100% → "Done"

### Phase Checkpoints

**Format in tasks.md**:

```markdown
**Phase 1 Checkpoint**: 2024-01-15T11:30:00Z
```

**Parsing**:

- Not yet complete: `[Completion date/time when done]`
- Complete: Actual timestamp

**Hook output**:

```
Checkpoints:
  - Phase 1: Complete
  - Phase 2: Complete
  - Phase 3: Pending
```

### Board API Integration

**Currently**: Template with commented-out API calls

**To Implement**: Based on your board system (Jira, Linear, GitHub Projects, etc.)

**Example (Jira)**:

```typescript
async function updateBoardStatus(payload: BoardUpdatePayload): Promise<void> {
  const response = await fetch(`https://your-domain.atlassian.net/rest/api/3/issue/${payload.epic}`, {
    method: "PUT",
    headers: {
      Authorization: `Basic ${Buffer.from(`${email}:${apiToken}`).toString("base64")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      fields: {
        status: { name: payload.status },
        customfield_10016: payload.completion_rate, // Story Points or Progress
        labels: payload.labels,
      },
    }),
  });

  if (!response.ok) {
    throw new Error(`Jira API error: ${response.statusText}`);
  }
}
```

**Example (Linear)**:

```typescript
const { LinearClient } = require("@linear/sdk");

async function updateBoardStatus(payload: BoardUpdatePayload): Promise<void> {
  const client = new LinearClient({ apiKey: process.env.LINEAR_API_KEY });

  await client.updateIssue(payload.epic, {
    stateId: getLinearStateId(payload.status), // Map status to Linear state
    progress: payload.completion_rate / 100,
    labelIds: await getLinearLabelIds(payload.labels),
  });
}
```

---

## Quality Checklist

### Before Committing Code

- [ ] All functions have type hints
- [ ] All async operations use `await`
- [ ] Error handling covers all external interactions
- [ ] Tests written (coverage ≥98%)
- [ ] Docstrings on public functions
- [ ] No blocking I/O in async functions
- [ ] Database sessions use context managers
- [ ] Pydantic schemas for all API inputs/outputs
- [ ] Logging on error paths
- [ ] Configuration from environment variables

**Automated Checks** (via hooks):

- ✅ Ruff formatting
- ✅ MyPy type checking (strict)
- ✅ Pytest coverage gate (98%)
- 📋 Board sync (if tasks.md exists)

---

## Integration Roadmap

### Week 1-3 (HIGH Priority - Simple)

#### Python Hook Adaptation ✅

**Status**: Complete
**Files**:

- `.claude/hooks/post-tool-use-file-tracker.ts`
- `.claude/hooks/stop-python-quality-pipeline.ts`
- `.claude/hooks/user-prompt-submit-skill-activator.ts`

#### Coverage Gate Hook ✅

**Status**: Complete
**File**: `.claude/hooks/stop-python-quality-pipeline.ts`
**Features**: 98% threshold, blocks commits, displays delta

#### Board Metadata Extension ✅

**Status**: Complete (template)
**File**: `.claude/hooks/stop-board-sync.ts`
**Next**: Implement board API integration for your board system

#### Skill-Rules.json ✅

**Status**: Complete
**File**: `.claude/skills/skill-rules.json`
**Covers**: Python, Vertex AI, ML, BigQuery, Testing

#### Dev Docs Templates ✅

**Status**: Complete
**Files**:

- `.claude/dev/templates/task-plan-template.md`
- `.claude/dev/templates/task-context-template.md`
- `.claude/dev/templates/task-tasks-template.md`
- `.claude/dev/templates/experiment-plan-template.md`
- `.claude/dev/templates/experiment-context-template.md`
- `.claude/dev/templates/experiment-results-template.md`

### Month 1-2 (HIGH Priority - Moderate)

#### Auto-Rollback Agent ✅

**Status**: Complete (spec)
**File**: `.claude/agents/auto-rollback-agent.md`
**Next**: Test with actual coverage failures

#### ML Experiment Dev Docs ✅

**Status**: Complete (templates)
**Next**: Use for first ML experiment

#### Agent Coordination Protocol

**Status**: TODO
**File**: `.claude/skills/agent-handoff-protocol.md`
**Scope**: Formalize multi-agent workflows

#### CodeRabbit CLI Integration

**Status**: TODO
**Hook**: Add `coderabbit review` to Stop hooks
**Benefits**: 40+ linters/SAST, codebase graph analysis

### Month 3-6 (MEDIUM Priority)

#### Python Process Management

**Status**: TODO
**Alternative**: supervisor, honcho, or systemd
**Purpose**: Port PM2 patterns (log management, auto-restart)

#### Test-First Enforcer

**Status**: TODO
**Hook**: PreToolUse hook warning if editing code without tests

#### Vertex AI Experiments Integration

**Status**: TODO
**Skill**: Extend `ml-experiment-tracking` to sync with Vertex AI Experiments API

#### Utility Scripts

**Status**: Partial (coverage-report.py complete)
**TODO**:

- `vertex-ai-deploy.py`
- `vertex-ai-monitor.py`
- `bigquery-load.py`
- `board-sync-manual.py`

#### Slash Commands

**Status**: TODO
**Directory**: `.claude/commands/`
**Commands**:

- `/dev-docs` - Create comprehensive strategic plan
- `/dev-docs-update` - Update dev docs before compaction
- `/create-dev-docs` - Convert plan to dev doc files
- `/code-review` - Launch code-architecture-reviewer
- `/auto-rollback` - Launch auto-rollback-agent
- `/test-route` - Test authenticated routes

---

## Critical Success Factors

### 1. Start with Hooks

**80% of value** comes from the hook system. Everything else builds on this foundation.

### 2. Dev Docs Are Foundational

The 3-file pattern enables:

- Context reset recovery
- Board automation
- Multi-agent coordination
- Experiment tracking

### 3. Skills Auto-Activation Differentiates

The `skill-rules.json` + `user-prompt-submit-skill-activator` hook solves Claude Code's #1 problem.

### 4. Incremental UV Adoption

Use `uv pip` interface first, migrate to full `uv` project management later. Don't block on migration.

### 5. Agent Specialization

Keep agents focused. Avoid generic "do everything" agents. Explicit input/output formats.

### 6. Planning Is Non-Negotiable

**Quote from source developer**: "If you aren't at a minimum using planning mode before asking Claude to implement something, you're gonna have a bad time."

Use planning mode or `strategic-plan-architect` before every implementation.

### 7. Review Consistently

Have Claude review its own code periodically using specialized agents. Catches issues before they accumulate.

---

## Productivity Metrics

### From Source Developer (6 Months)

- **Scale**: Solo rewrote 300-400k LOC in 6 months
- **Context Efficiency**: 40-60% token reduction after modular skills
- **Error Elimination**: Zero errors escaping since implementing hooks
- **Debugging**: PM2 enabled autonomous debugging without "human log-fetching service"
- **Planning Overhead**: 15% context after planning (sustainable with dev docs)
- **Coverage**: Decent coverage on previously zero-coverage codebase
- **DX Transformation**: From "absolute nightmare" to streamlined
- **Time Allocation**: From debugging AI mess → building new features
- **Job Security**: Became "AI guru", proposing large redesigns previously impossible

**Infrastructure Investment**: "A couple of days to get right" initially, "paid for itself ten times over"

---

## Lessons Learned

### What Works

1. **Systematic infrastructure beats ad-hoc prompting** at scale
2. **Hooks enforce quality** without manual gates
3. **Dev docs prevent context loss** across resets
4. **Skills auto-activation** dramatically improves consistency
5. **Specialized agents** handle specific tasks better than generic prompts
6. **Planning first** catches mistakes before implementation
7. **Progressive disclosure** (500-line rule) keeps skills usable

### Common Pitfalls

1. **Skills won't activate without hooks** - #1 problem
2. **Large skills hit context limits** - Use modular pattern
3. **Forgetting to plan** - Quality suffers dramatically
4. **Not reviewing plans** - Catches misunderstandings early
5. **Lazy prompting** (end-of-day) - Results show the difference
6. **Stubbornly using AI for everything** - Sometimes just fix it yourself (2 min vs 30 min)

### Prompt Engineering Insights

**Be Specific**: Ask for specific results. Discuss plans before implementation.

**Don't Lead**: Neutral questions get balanced answers. Claude "tells you what it thinks you want to hear."

**Re-prompt Often**: Double-ESC to bring up previous prompts. "Armed with knowledge of what you don't want."

**Context Is King**: "Ask not what Claude can do for you, ask what context you can give to Claude."

**Sometimes Step In**: If 30 min struggling vs 2 min fixing yourself, just fix it. No shame.

---

## Future Enhancements

### LangGraph Integration

**Opportunity**: Formalize state machine with LangGraph
**Benefits**: Persistent checkpoints, branching workflows, human-in-the-loop
**Challenge**: Adds dependency, complexity

### AutoGen Multi-Agent

**Opportunity**: Complex multi-agent reasoning for large refactorings
**Benefits**: Specialized agents collaborating
**Challenge**: Learning curve, debugging multi-agent interactions

### CodeRabbit Continuous Learning

**Opportunity**: Capture CodeRabbit findings → skill resources
**Benefits**: Institutional memory, preventing future violations
**Implementation**: Stop hook parses CodeRabbit output, appends to skill resources

### Vertex AI Pipelines

**Opportunity**: ML workflow automation (data prep → training → evaluation → deployment)
**Benefits**: Reproducible, scalable, monitored
**Skill**: Create `vertex-ai-pipelines.md` with Kubeflow Pipelines patterns

### Real-Time Board Sync

**Opportunity**: Webhook from board → update dev docs
**Benefits**: Bidirectional sync (board updates tasks.md, tasks.md updates board)
**Challenge**: Merge conflicts, race conditions

---

## Conclusion

This infrastructure transforms Claude Code from a frustrating tool producing inconsistent output into a reliable pair programmer capable of solo delivering enterprise-scale projects.

**The key insight**: Claude Code's power lies not in its ability to write code, but in its ability to follow systematic processes when properly guided. The hooks, skills, dev docs, and agents provide that guidance automatically.

**The result**: A development environment where quality is enforced, context is preserved, progress is tracked, and the developer can focus on building features instead of debugging AI-generated messes.

**Judge #6 is not just watching—Judge #6 is automated, enforced, and backed by an agent that will either fix coverage or revert your code.**

Welcome to the future of AI-assisted development.

---

**Version**: 1.0.0
**Last Updated**: 2024-11-15
**Maintained By**: PNKLN Team
**Questions?**: See CLAUDE.md for quick reference or `.claude/skills/` for domain-specific guidance
