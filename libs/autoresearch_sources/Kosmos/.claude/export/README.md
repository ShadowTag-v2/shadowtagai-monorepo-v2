# Kosmos X-Ray Export (Enhanced v2)

Portable context-efficient codebase exploration system for AI programmers.

## Enhanced Features (v2)
- **Pydantic/dataclass field extraction** - `name: str = Field(...)` now visible
- **Decorator support** - `@dataclass`, `@property`, `@tool` shown above definitions
- **Global constants** - `SYSTEM_PROMPT = "..."`, `CONFIG = {...}` at module level
- **Line numbers** - `def method(): ...  # L42` for precise navigation
- **Mermaid diagrams** - `--mermaid` flag for dynamic architecture visualization
- **Import verification** - Agent verifies entry points are importable before documenting

## Contents

```
export/
├── README.md                 # This file
├── WARM_START.md             # Example output (regenerate for your repo)
├── install.sh                # One-command installer
├── agents/
│   └── kosmos_architect.md   # Agent for generating documentation
└── kosmos-xray/              # Core skill
    ├── SKILL.md              # Full documentation
    ├── CHEATSHEET.md         # Quick reference
    ├── reference.md          # API documentation
    ├── configs/
    │   ├── ignore_patterns.json
    │   └── priority_modules.json
    ├── scripts/
    │   ├── mapper.py
    │   ├── skeleton.py       # Enhanced with fields, decorators, line numbers
    │   └── dependency_graph.py  # Now has --mermaid flag
    ├── templates/
    │   ├── warm_start.md.template
    │   └── skeleton_format.md
    └── lib/
        ├── __init__.py
        ├── ast_utils.py      # Core AST parsing (single source of truth)
        └── token_estimator.py
```

## Installation

### 1. Copy to Target Repository

```bash
# From the export directory
./install.sh /path/to/target/repo

# Or manually:
mkdir -p /path/to/target/.claude/skills
mkdir -p /path/to/target/.claude/agents
cp -r kosmos-xray /path/to/target/.claude/skills/
cp agents/kosmos_architect.md /path/to/target/.claude/agents/
```

### 2. Customize Configurations

Edit `configs/ignore_patterns.json` for your repo's structure:
```json
{
  "directories": ["node_modules", "dist", "build", "__pycache__", ...],
  "extensions": [".log", ".pyc", ...],
  "files": ["*.min.js", ...]
}
```

Edit `configs/priority_modules.json` for your repo's architecture:
```json
{
  "priority_patterns": {
    "critical": {
      "patterns": ["**/core/**/*.py", "**/main.*"]
    },
    "high": {
      "patterns": ["**/models/**/*.py", "**/services/**/*.py"]
    }
  }
}
```

### 3. Generate WARM_START.md (Use ALL Features)

```bash
# Step 1: Survey codebase
python .claude/skills/kosmos-xray/scripts/mapper.py --summary

# Step 2: Extract critical interfaces (WITH Pydantic fields + line numbers)
python .claude/skills/kosmos-xray/scripts/skeleton.py src/ --priority critical

# Step 3: Generate Mermaid architecture diagram
python .claude/skills/kosmos-xray/scripts/dependency_graph.py src/ --root mypackage --mermaid

# Step 4: Verify imports before documenting
python3 -c "from mypackage.main import App; print('✓')"

# Step 5: Use the agent to generate documentation
# In Claude Code: @kosmos_architect generate
```

## Usage

### Full Exploration Path (Recommended)

```bash
# 1. Survey (500 tokens)
python .claude/skills/kosmos-xray/scripts/mapper.py --summary

# 2. Critical interfaces with Pydantic fields (5K tokens)
python .claude/skills/kosmos-xray/scripts/skeleton.py src/ --priority critical

# 3. Architecture diagram for docs (500 tokens)
python .claude/skills/kosmos-xray/scripts/dependency_graph.py src/ --root pkg --mermaid

# 4. Focused diagram (500 tokens)
python .claude/skills/kosmos-xray/scripts/dependency_graph.py src/ --mermaid --focus api

# 5. Verify imports
python3 -c "from pkg.main import Main; print('✓')"

# Total: ~6.5K tokens for complete architecture understanding
```

### Direct Script Usage

```bash
# mapper.py - Directory structure with token estimates
python .claude/skills/kosmos-xray/scripts/mapper.py [directory] [--summary] [--json]

# skeleton.py - Enhanced interface extraction
python .claude/skills/kosmos-xray/scripts/skeleton.py <path> \
    [--priority critical|high|medium|low] \
    [--private] \
    [--no-line-numbers] \
    [--json]

# dependency_graph.py - Import analysis + Mermaid
python .claude/skills/kosmos-xray/scripts/dependency_graph.py [directory] \
    [--root package_name] \
    [--focus area] \
    [--mermaid] \
    [--json]
```

### Via Agent (Claude Code)

```
@kosmos_architect generate     # Create WARM_START.md (uses ALL features)
@kosmos_architect refresh      # Update existing doc
@kosmos_architect query "X"    # Answer architecture questions
```

### Via Skill Triggers

The skill responds to these phrases:
- "xray", "x-ray"
- "map structure"
- "skeleton"
- "interface"
- "architecture"
- "warm start"

## What Enhanced Skeleton Reveals

**Before (data blind):**
```python
class Hypothesis(BaseModel):
    pass  # Fields invisible!
```

**After (enhanced):**
```python
@dataclass
class PaperAnalysis:  # L34
    paper_id: str  # L36
    executive_summary: str  # L37
    confidence_score: float  # L42
```

## Best Practices

### DO:
- Always use `--priority critical` first to understand core architecture
- Use `--mermaid` output for WARM_START.md diagrams
- Check line numbers when you need to reference specific code
- Use `--private` when understanding internal behavior
- Verify imports before documenting them as entry points

### DON'T:
- Read full files when skeleton would suffice (wastes context)
- Ignore large file warnings from mapper.py
- Skip the Pydantic fields - they define the data contracts
- Forget to include line numbers in documentation references

## Adapting for Non-Python Projects

The scripts are Python-focused but can be adapted:

1. **mapper.py** - Works with any file types, just update `ignore_patterns.json`
2. **skeleton.py** - Python-only (AST parsing), would need rewrite for other languages
3. **dependency_graph.py** - Python-only, would need rewrite for other languages

For non-Python projects, mapper.py still provides value for token budgeting.

## Requirements

- Python 3.8+
- No external dependencies (uses stdlib only: ast, json, os, pathlib, argparse)

## License

Same as parent repository.
