# Erik Interaction Plugin

Claude Agent SDK plugin for Erik's communication patterns and JR validation framework.

## Installation

Plugin is already installed at:
```
.claude/plugins/erik-interaction/
```

## Validation

Plugin structure validated ✅

```bash
node validate-plugin.mjs
```

Output:
- ✓ 6 skills loaded
- ✓ 3 hooks configured (UserPromptSubmit, PreToolUse, PostToolUse)
- ✓ 3 Python scripts executable
- ✓ All files present and executable

## Loading the Plugin

### Option 1: Claude Code CLI (Auto-load)

If using Claude Code CLI with plugin support:

```bash
claude --plugins .claude/plugins/erik-interaction
```

### Option 2: SDK Integration

In your Node.js application:

```javascript
import { runAgent } from '@anthropic-ai/claude-agent-sdk';

const result = await runAgent({
  plugins: [
    { type: 'local', path: './.claude/plugins/erik-interaction' }
  ],
  prompt: 'Your question here',
  apiKey: process.env.ANTHROPIC_API_KEY
});
```

### Option 3: Test Script

```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run loader
node load-erik-plugin.mjs
```

## Plugin Components

### Skills (6)

1. **erik-response-formatter** - Direct answer format, no preamble
   - First line = answer
   - OPTIONS/RISKS/NEXT structure
   - No "I'll help you..." openings

2. **context-auto-loader** - Memory definitions and auto-search
   - Judge #6, Cor.53, JR framework
   - Auto-loads context from past conversations
   - Bootstrap constraints ($60-65K, 2 weeks)

3. **jr-auto-validator** - JR constraint validation
   - 3× ROI minimum
   - 4:1 LTV:CAC minimum
   - <90ms p99 latency
   - Kill switches required
   - $65K/mo max burn

4. **command-interpreter** - Shorthand command mapping
   - "costs?" → Full cost breakdown
   - "easy button" → Simplest implementation
   - "next?" → Single action
   - "deploy this" → GKE manifests
   - "objections?" → JR violations list

5. **technical-depth-defaulter** - Expert-level output
   - No pseudocode
   - Actual values only
   - Complete K8s manifests
   - Real error handling

6. **past-conversation-auto-search** - Context detection
   - Auto-search on "last time", "the judge", etc
   - Silent execution (no "I searched...")
   - Mid-context question detection

### Hooks (3)

1. **UserPromptSubmit.sh** - Pre-question context loading
   - Calls `context-loader.py`
   - Injects additional context
   - Pattern matching on question

2. **PreToolUse.sh** - JR validation before tool execution
   - Calls `jr-validator.py`
   - Blocks JR violations
   - Approves compliant operations

3. **PostToolUse.sh** - Memory updates after tools
   - Calls `memory-updater.py`
   - Tracks components, costs, metrics
   - Updates session memory

### Scripts (3)

1. **context-loader.py** (165 lines)
   - Pattern matching for context triggers
   - Search query construction
   - Context injection into prompt

2. **jr-validator.py** (162 lines)
   - Metric extraction from tool input
   - Constraint validation
   - Decision: approve/block/ask

3. **memory-updater.py** (142 lines)
   - Component info extraction
   - Cost tracking
   - Metrics persistence

## JR Framework Constraints

```python
JR_CONSTRAINTS = {
    "roi_minimum": 3.0,           # 3× ROI minimum
    "ltv_cac_minimum": 4.0,       # 4:1 LTV:CAC minimum
    "p99_latency_ms": 90,         # <90ms p99 latency
    "kill_switch": "required",    # All deployments
    "iteration_weeks": 2,         # Max iteration cycle
    "monthly_burn_max": 65000,    # $65K max monthly burn
    "env_restriction": "vertex",  # Vertex AI Workbench only
}
```

## Response Format

All responses follow this structure:

```
[DIRECT ANSWER IN FIRST LINE]

IMPLEMENTATION:
[actual code with real values]

OPTIONS:
1. BEST: [ignore constraints]
2. FAST: [2-week MVP]
3. CHEAP: [bootstrap reality]

RISKS:
- [ATP 5-19 assessment]
- [Kill triggers]

NEXT: [single specific action]
```

## Auto-Activation

Plugin auto-activates for:
- User: erik, ehanc69
- Questions with component references ("the judge", "the deployment")
- Mid-context questions ("deploy this", "costs?")
- Update requests ("change", "fix", "update")

## Memory Context

Plugin maintains context for:
- Judge #6: 3-layer hybrid (Gemini Flash → Claude Haiku → Local)
- Cor.53: Current orchestration version
- JR: Purpose/Reasons/Brakes framework
- NS: Namespace system (ShadowTag-v2jr-core, ShadowTag-v2jr-governance, ShadowTag-v2jr-data)
- GKE: us-central1-a, n2-standard-8 cluster
- Bootstrap: $60-65K/mo, 2-week iterations

## Testing

1. **Structure validation:**
   ```bash
   node validate-plugin.mjs
   ```

2. **Plugin loading:**
   ```bash
   node load-erik-plugin.mjs
   ```

3. **Hook testing:**
   ```bash
   # Test context loader
   .claude/plugins/erik-interaction/scripts/context-loader.py \
     --session-id test \
     --input "deploy the judge"

   # Test JR validator
   .claude/plugins/erik-interaction/scripts/jr-validator.py \
     --tool Bash \
     --input '{"roi": 2.5, "p99_latency": 120}'
   ```

## Version

- **Version:** 1.0.0
- **SDK Compatibility:** @anthropic-ai/claude-agent-sdk ^0.1.30
- **Created:** 2025-11-17

## Structure

```
.claude/plugins/erik-interaction/
├── README.md                        # This file
├── plugin.json                      # SDK configuration
├── skills/                          # 6 skill definitions
│   ├── erik-response-formatter.md
│   ├── context-auto-loader.md
│   ├── jr-auto-validator.md
│   ├── command-interpreter.md
│   ├── technical-depth-defaulter.md
│   └── past-conversation-auto-search.md
├── hooks/                           # 3 lifecycle hooks
│   ├── UserPromptSubmit.sh
│   ├── PreToolUse.sh
│   └── PostToolUse.sh
└── scripts/                         # 3 Python validators
    ├── context-loader.py
    ├── jr-validator.py
    └── memory-updater.py
```

## Files

- Total lines: 1,483
- Skills: 6 markdown files
- Hooks: 3 bash wrappers
- Scripts: 3 Python modules (469 lines)

## Git

```
Commit: 39c6fcf
Branch: claude/review-agent-frameworks-011CUuNocbGzKdKwr3SfAzpb
```
