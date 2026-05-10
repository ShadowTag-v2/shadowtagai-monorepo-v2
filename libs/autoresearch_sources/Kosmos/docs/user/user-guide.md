# Kosmos AI Scientist User Guide

**Version:** 0.10.0
**Last Updated:** 2025-01-15

Welcome to Kosmos! This guide will help you get started with autonomous scientific research powered by Claude.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Quick Start](#quick-start)
3. [Using the CLI](#using-the-cli)
4. [Understanding Results](#understanding-results)
5. [Configuration](#configuration)
6. [Domain-Specific Usage](#domain-specific-usage)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

---

## Installation & Setup

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.9, 3.10, 3.11, or 3.12
- **Memory**: Minimum 4 GB RAM (8 GB recommended)
- **Disk**: 2 GB free space for installation and cache
- **Network**: Internet connection for API access

### Prerequisites

You need one of the following for Claude access:

**Option A: Anthropic API Key** (Pay-per-use)
- Sign up at [console.anthropic.com](https://console.anthropic.com/)
- Create an API key
- Costs: ~$3 per 1M input tokens, ~$15 per 1M output tokens

**Option B: Claude Code CLI** (Recommended)
- Requires Claude Max subscription ($20/month)
- No per-token costs - unlimited usage
- Better for heavy research workloads

### Step 1: Install Python

Check your Python version:

```bash
python --version
# Should show Python 3.9+ (3.11 recommended)
```

If you need to install Python:

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**macOS** (with Homebrew):
```bash
brew install python@3.11
```

**Windows**:
Download from [python.org](https://www.python.org/downloads/)

### Step 2: Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/kosmos-ai-scientist.git
cd kosmos-ai-scientist

# Verify you're in the right directory
ls -la
# Should see: kosmos/, tests/, docs/, pyproject.toml, etc.
```

### Step 3: Create Virtual Environment

Always use a virtual environment to avoid conflicts:

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
which python
# Should show: /path/to/kosmos-ai-scientist/venv/bin/python
```

### Step 4: Install Kosmos

```bash
# Install in editable mode with all dependencies
pip install -e .

# Verify installation
kosmos version
# Should show: Kosmos AI Scientist v0.10.0

# Check all dependencies installed
kosmos doctor
# All checks should pass (except API key initially)
```

### Step 5: Configure API Access

#### Option A: Anthropic API

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor

# Add your API key:
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

# Save and exit

# Verify configuration
kosmos doctor
# API Key check should now pass
```

#### Option B: Claude Code CLI

```bash
# 1. Install Claude Code CLI
# Visit https://claude.ai/download and follow instructions

# 2. Authenticate
claude auth
# Follow the authentication flow in your browser

# 3. Copy example environment file
cp .env.example .env

# 4. Edit .env and set API key to all 9s
nano .env

# Add this line (50 nines triggers CLI routing):
ANTHROPIC_API_KEY=99999999999999999999999999999999999999999999999999

# 5. Verify
kosmos doctor
# Should detect CLI mode and pass all checks
```

### Step 6: Initialize Database

```bash
# Initialize SQLite database
kosmos config --validate
# This creates kosmos.db if it doesn't exist

# Verify database created
ls -la kosmos.db
# Should show: kosmos.db with recent timestamp
```

### Optional: Neo4j Knowledge Graph

Kosmos maintains a **persistent knowledge graph** that automatically captures your entire research journey. This is optional but highly recommended for building cumulative knowledge.

**What you get:**
- Automatic persistence of all research artifacts (questions, hypotheses, experiments, results)
- Relationship tracking (SPAWNED_BY, TESTS, SUPPORTS, REFUTES)
- Export/import capabilities for backup and collaboration
- Provenance metadata (who, when, why for every entity)

**Installation:**

**Option A: Automated Setup (Recommended)**

The fastest way to get Neo4j running:

```bash
# One command - handles everything
./scripts/setup_neo4j.sh

# Or using Make
make setup-neo4j
```

**What it does:**
- ✓ Checks Docker is installed and running
- ✓ Creates data directories
- ✓ Validates configuration
- ✓ Starts Neo4j container
- ✓ Waits for health check
- ✓ Verifies connectivity
- ✓ Displays connection info

See [Automated Setup Guide](automated-setup.md) for details.

**Option B: Manual Docker Setup**

Using docker-compose directly:
```bash
# Start Neo4j via docker-compose (included in Kosmos)
docker-compose up -d neo4j

# Verify it's running
docker-compose ps
```

Manual installation:
```bash
# Ubuntu/Debian:
sudo apt install neo4j

# macOS:
brew install neo4j

# Start Neo4j
neo4j start
```

**Configuration:**

Add to your `.env` file:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=kosmos-password
WORLD_MODEL_ENABLED=true
```

**Verify Neo4j is working:**
```bash
# Access Neo4j browser
open http://localhost:7474

# Login with credentials from .env
# Run test query:
MATCH (n) RETURN count(n)
```

**Works without Neo4j:**
If Neo4j is unavailable, Kosmos continues working normally (graceful degradation). Graph features are optional enhancements.

See [World Model Guide](world_model_guide.md) for detailed documentation and CLI commands.

### Verification

Run all diagnostic checks:

```bash
kosmos doctor
```

**Expected output:**
```
Running Diagnostics

Diagnostic Results:
┌─────────────────────┬────────────┬────────┐
│ Check               │ Status     │ Result │
├─────────────────────┼────────────┼────────┤
│ Python Version      │ 3.11       │ ✓ PASS │
│ Package: anthropic  │ Installed  │ ✓ PASS │
│ Package: typer      │ Installed  │ ✓ PASS │
│ Anthropic API Key   │ Configured │ ✓ PASS │
│ Cache Directory     │ Writable   │ ✓ PASS │
│ Database            │ Connected  │ ✓ PASS │
└─────────────────────┴────────────┴────────┘

✓ All checks passed! Kosmos is ready to use.
```

---

## Quick Start

### Your First Research Run

Let's run a simple research project to verify everything works:

```bash
# Run in interactive mode (recommended for first time)
kosmos run --interactive
```

**Interactive Mode Workflow:**

1. **Domain Selection**:
```
Select a scientific domain:
┌───┬────────────────┬─────────────────────────────────────────┐
│ # │ Domain         │ Description                             │
├───┼────────────────┼─────────────────────────────────────────┤
│ 1 │ Biology        │ Genetics, proteins, cells, diseases     │
│ 2 │ Neuroscience   │ Brain, neurons, cognition               │
│ 3 │ Materials      │ Materials science, properties           │
│ 4 │ Physics        │ Physical systems, mechanics             │
│ 5 │ Chemistry      │ Molecules, reactions                    │
│ 6 │ General        │ Cross-domain or other topics            │
└───┴────────────────┴─────────────────────────────────────────┘

Enter domain number: 2  # Select neuroscience
```

2. **Research Question**:
```
Example questions for neuroscience:
• How does synaptic connectivity relate to neural function?
• What are the molecular mechanisms of memory formation?

Enter your research question: How do neurons encode information?
```

3. **Configuration**:
```
Max iterations [10]: 5
Enable budget limit? [y/N]: n
Enable cache? [Y/n]: y
Auto model selection? [Y/n]: y
```

4. **Confirmation**:
```
Configuration Summary:
┌─────────────────┬──────────────────────────────────────────┐
│ Domain          │ Neuroscience                             │
│ Question        │ How do neurons encode information?       │
│ Max Iterations  │ 5                                        │
│ Budget          │ Unlimited                                │
│ Cache Enabled   │ Yes                                      │
└─────────────────┴──────────────────────────────────────────┘

Start research? [Y/n]: y
```

5. **Research Execution**:
```
Running Research

Generating hypotheses...    ████████████████████ 100%
Designing experiments...    ████████████████████ 100%
Executing experiments...    ████████████████████ 100%
Analyzing results...        ████████████████████ 100%
Research progress...        ████████░░░░░░░░░░░░  60% (3/5)

Research ID: run_abc123
```

### Monitoring Progress

In another terminal, watch the research progress:

```bash
# Live status updates (refreshes every 5 seconds)
kosmos status run_abc123 --watch
```

**Output:**
```
Research Overview:
┌─────────────────┬────────────────────────────────┐
│ Run ID          │ run_abc123                     │
│ Domain          │ Neuroscience                   │
│ State           │ RUNNING                        │
│ Progress        │ Iteration 3/5 (60%)            │
│ Question        │ How do neurons encode info?    │
└─────────────────┴────────────────────────────────┘

Progress:
███████████████████████░░░░░  60%

Workflow State:
┌────────────┬─────────────┬──────────┐
│ Phase      │ Status      │ Duration │
├────────────┼─────────────┼──────────┤
│ Hypothesis │ Completed   │ 2m 15s   │
│ Experiment │ Completed   │ 5m 30s   │
│ Execution  │ Running     │ 3m 45s   │
│ Analysis   │ Pending     │ -        │
└────────────┴─────────────┴──────────┘

Metrics:
┌──────────────────┬─────────┐
│ API Calls        │ 45      │
│ Cache Hits       │ 12 (27%)│
│ Cost             │ $3.50   │
│ Time Elapsed     │ 15m 30s │
└──────────────────┴─────────┘

[Auto-refreshing every 5s - Press Ctrl+C to exit]
```

### Viewing Results

Once complete, view the results:

```bash
# Show detailed results
kosmos status run_abc123 --details
```

**Results Display:**
```
✓ Research Complete

Research Overview:
• Run ID: run_abc123
• Domain: Neuroscience
• State: COMPLETED
• Iterations: 5/5
• Duration: 45m 30s
• Cost: $12.50

Hypotheses Generated (3):
┌────┬────────────────────────────────────────┬─────────┬──────────┐
│ #  │ Claim                                  │ Novelty │ Priority │
├────┼────────────────────────────────────────┼─────────┼──────────┤
│ 1  │ Neurons use rate coding to encode...  │ 0.65    │ 0.85     │
│ 2  │ Temporal patterns carry information... │ 0.82    │ 0.90     │
│ 3  │ Population coding enables robust...    │ 0.55    │ 0.70     │
└────┴────────────────────────────────────────┴─────────┴──────────┘

Experiments Executed (8):
┌────┬──────────────────┬──────────┬──────────┐
│ #  │ Type             │ Status   │ Duration │
├────┼──────────────────┼──────────┼──────────┤
│ 1  │ Correlation      │ Complete │ 3m 15s   │
│ 2  │ Statistical Test │ Complete │ 2m 30s   │
│ 3  │ Simulation       │ Complete │ 8m 45s   │
└────┴──────────────────┴──────────┴──────────┘

Key Findings:
• Temporal coding shows strong evidence (p < 0.01)
• Rate coding moderate support (p = 0.04)
• Population coding requires further investigation

Recommendations:
• Focus on temporal pattern analysis
• Investigate spike timing dependencies
• Consider multi-neuron recordings
```

---

## Using the CLI

### Command Overview

```bash
kosmos --help
```

**Available Commands:**
- `run` - Execute research
- `status` - Monitor research status
- `history` - Browse past research
- `cache` - Manage caching system
- `config` - View/validate configuration
- `version` - Show version info
- `info` - System status
- `doctor` - Run diagnostics

### Running Research

#### Interactive Mode (Beginner-Friendly)

Best for first-time users or when you want guidance:

```bash
kosmos run --interactive
```

**Benefits:**
- Guided prompts for all options
- Domain selection with examples
- Configuration with sensible defaults
- Confirmation before starting
- Explanation of each option

#### Direct Mode (Expert)

When you know exactly what you want:

```bash
kosmos run "Your research question here" \
  --domain <domain> \
  --max-iterations <num> \
  --budget <usd> \
  --output results.json
```

**Examples:**

```bash
# Biology research
kosmos run "What causes cancer cell metastasis?" \
  --domain biology \
  --max-iterations 10

# Neuroscience with budget limit
kosmos run "How does sleep affect memory consolidation?" \
  --domain neuroscience \
  --budget 25.00

# Materials science with output
kosmos run "Optimize Li-ion battery cathode materials" \
  --domain materials \
  --max-iterations 15 \
  --output battery_research.json
```

#### Options Reference

**Required:**
- `question` - Research question (or use --interactive)

**Optional:**
- `--interactive` - Launch interactive mode
- `--domain TEXT` - Domain (biology, neuroscience, materials, physics, chemistry, general)
- `--max-iterations INT` - Maximum iterations (default: 10)
- `--budget FLOAT` - Budget limit in USD
- `--no-cache` - Disable caching (not recommended)
- `--output PATH` - Export results to JSON or Markdown file

### Monitoring Research

#### Real-time Status

```bash
# Simple status
kosmos status <run_id>

# Watch mode (live updates)
kosmos status <run_id> --watch

# Detailed view
kosmos status <run_id> --details
```

#### Status Information

The status command shows:
- **Overview**: Run ID, domain, state, progress
- **Progress Bar**: Visual representation of iterations
- **Workflow State**: Current phase and timing
- **Metrics**: API calls, cache performance, cost, duration
- **Recent Activity**: Latest actions and results

### Browsing History

```bash
# Show recent runs
kosmos history

# Show last 20 runs
kosmos history --limit 20

# Filter by domain
kosmos history --domain neuroscience

# Filter by status
kosmos history --status completed

# Filter by time
kosmos history --days 7

# Detailed view
kosmos history --details
```

**Interactive History:**

When viewing history, you can select a run to see full details:

```
Research History (10 runs):
┌────┬──────────────┬────────────────┬──────────────┬──────────┬────────────┐
│ #  │ Run ID       │ Question       │ Domain       │ State    │ Created    │
├────┼──────────────┼────────────────┼──────────────┼──────────┼────────────┤
│ 1  │ run_abc123   │ How do neurons │ Neuroscience │ Complete │ 2 hours ago│
│ 2  │ run_def456   │ Cancer meta... │ Biology      │ Complete │ 1 day ago  │
└────┴──────────────┴────────────────┴──────────────┴──────────┴────────────┘

View details for a run? (Enter run # or 'n'): 1
```

### Managing Cache

The cache system significantly reduces costs. Monitor and optimize it:

```bash
# View cache statistics
kosmos cache --stats
```

**Output:**
```
Cache Statistics

Overall Cache Performance:
┌────────────────────┬─────────┐
│ Metric             │ Value   │
├────────────────────┼─────────┤
│ Total Requests     │ 500     │
│ Cache Hits         │ 175     │
│ Hit Rate           │ 35.0%   │
│ Cost Saved         │ $15.75  │
└────────────────────┴─────────┘

Cache Details:
┌──────────────┬──────┬────────┬──────────┬──────┬──────────┐
│ Cache Type   │ Hits │ Misses │ Hit Rate │ Size │ Storage  │
├──────────────┼──────┼────────┼──────────┼──────┼──────────┤
│ Claude       │ 100  │ 150    │ 40.0%    │ 250  │ 150 MB   │
│ Experiment   │ 50   │ 50     │ 50.0%    │ 100  │ 75 MB    │
│ Embedding    │ 25   │ 25     │ 50.0%    │ 50   │ 10 MB    │
└──────────────┴──────┴────────┴──────────┴──────┴──────────┘

💰 Estimated Cost Savings: $15.75
```

**Cache Management:**

```bash
# Health check
kosmos cache --health

# Optimize (cleanup expired entries)
kosmos cache --optimize

# Clear specific cache
kosmos cache --clear-type claude

# Clear all caches (requires confirmation)
kosmos cache --clear
```

### Managing Knowledge Graphs

Kosmos automatically builds a persistent knowledge graph as you conduct research. Use these commands to manage and explore your accumulated knowledge.

**View Graph Statistics:**

```bash
kosmos graph --stats
```

**Example output:**
```
📊 Knowledge Graph Statistics

Entities:        127
Relationships:   243

Entity Types:
  Hypothesis: 45
  ExperimentProtocol: 28
  ExperimentResult: 23
  ResearchQuestion: 5

Relationship Types:
  SPAWNED_BY: 45
  TESTS: 28
  SUPPORTS: 15
  REFUTES: 8
  REFINED_FROM: 12
```

**Export Knowledge Graph:**

Export your graph for backup or collaboration:

```bash
# Export to JSON file
kosmos graph --export my_research.json

# Example output:
# ✅ Exported 127 entities and 243 relationships
#    File: my_research.json
#    Size: 2.3 MB
```

The export file is human-readable JSON containing all entities, relationships, and provenance metadata.

**Import Knowledge Graph:**

Restore or merge graphs from export files:

```bash
# Merge with existing graph
kosmos graph --import colleague_research.json

# Replace entire graph (clear first)
kosmos graph --import baseline_research.json --clear
```

**Reset Graph:**

Clear all graph data (use with caution):

```bash
# Prompts for confirmation
kosmos graph --reset

# Example:
# ⚠️  Delete all graph data? [y/N]: y
# ✅ Deleted 127 entities
```

**Use Cases:**

```bash
# Daily backup
kosmos graph --export backups/graph_$(date +%Y%m%d).json

# Share with colleague
kosmos graph --export team_knowledge.json

# Start fresh after major milestone
kosmos graph --export milestone_complete.json
kosmos graph --reset
```

**See Also:**
- [World Model Guide](world_model_guide.md) - Complete documentation
- [Neo4j Setup](#optional-neo4j-knowledge-graph) - Installation instructions

### Configuration Management

```bash
# View current configuration
kosmos config --show

# Validate configuration
kosmos config --validate

# Show config file paths
kosmos config --path
```

---

## Understanding Results

### Result Structure

Research results contain:

1. **Metadata**
   - Run ID
   - Question and domain
   - Timestamps (start, end, duration)
   - Configuration (iterations, budget)
   - Status and state

2. **Hypotheses**
   - Generated hypotheses with rationale
   - Novelty scores (0-1)
   - Priority scores (0-1)
   - Testability assessments
   - Status (pending, testing, confirmed, rejected)

3. **Experiments**
   - Experiment designs
   - Execution results
   - Statistical analyses
   - Visualizations (if generated)

4. **Findings**
   - Key insights
   - Statistical significance
   - Confidence levels
   - Recommendations

5. **Metrics**
   - API usage (calls, tokens)
   - Costs (total, per iteration)
   - Cache performance
   - Time breakdown

### Interpreting Scores

**Novelty Score (0-1)**:
- **0.8-1.0**: Highly novel, potential breakthrough
- **0.6-0.8**: Moderately novel, interesting direction
- **0.4-0.6**: Some novelty, incremental advance
- **0.2-0.4**: Limited novelty, well-explored
- **0.0-0.2**: Not novel, well-established

**Priority Score (0-1)**:
- **0.8-1.0**: High priority, test immediately
- **0.6-0.8**: Medium-high priority
- **0.4-0.6**: Medium priority
- **0.2-0.4**: Low priority, consider later
- **0.0-0.2**: Very low priority, skip

**Testability Score (0-1)**:
- **0.8-1.0**: Highly testable, clear methods available
- **0.6-0.8**: Testable with standard methods
- **0.4-0.6**: Moderately testable, some challenges
- **0.2-0.4**: Difficult to test, requires novel methods
- **0.0-0.2**: Not testable with current resources

### Statistical Significance

**P-values**:
- **p < 0.01**: Highly significant, strong evidence
- **p < 0.05**: Significant, moderate evidence
- **p < 0.10**: Marginally significant, weak evidence
- **p ≥ 0.10**: Not significant, insufficient evidence

**Effect Sizes**:
- **Large (≥ 0.8)**: Substantial practical significance
- **Medium (0.5-0.8)**: Moderate practical significance
- **Small (0.2-0.5)**: Small but potentially meaningful
- **Negligible (< 0.2)**: Minimal practical significance

### Exporting Results

Export results in different formats:

```bash
# JSON format (machine-readable)
kosmos run "question" --output results.json

# Markdown format (human-readable)
kosmos run "question" --output results.md

# Export existing run
kosmos status run_abc123 --details > results.txt
```

**JSON Structure:**
```json
{
  "run_id": "run_abc123",
  "question": "How do neurons encode information?",
  "domain": "neuroscience",
  "state": "completed",
  "hypotheses": [
    {
      "id": "hyp_001",
      "claim": "...",
      "novelty_score": 0.82,
      "priority_score": 0.90,
      "status": "confirmed"
    }
  ],
  "experiments": [...],
  "findings": {...},
  "metrics": {...}
}
```

**Markdown Structure:**
```markdown
# Research Results: How do neurons encode information?

**Run ID:** run_abc123
**Domain:** Neuroscience
**Status:** Completed

## Hypotheses

### 1. Temporal coding hypothesis
- **Novelty:** 0.82
- **Priority:** 0.90
- **Status:** Confirmed

...

## Experiments

...

## Key Findings

...
```

---

## Configuration

### Configuration Files

Kosmos uses multiple configuration sources (in priority order):

1. **Environment variables**
2. **`.env` file** (current directory)
3. **`~/.kosmos/config.yml`** (user config)
4. **Default values** (hardcoded)

### Environment Variables

Create a `.env` file in the project root:

```bash
# Claude API Configuration
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here  # Or 999...999 for CLI mode
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_MAX_TOKENS=4096
CLAUDE_TEMPERATURE=1.0

# Research Configuration
MAX_RESEARCH_ITERATIONS=10
ENABLED_DOMAINS=biology,neuroscience,materials,physics,chemistry,general
MIN_NOVELTY_SCORE=0.3

# Database Configuration
DATABASE_URL=sqlite:///kosmos.db
# Or PostgreSQL: postgresql://REDACTED_USER:REDACTED_PASS@localhost/kosmos

# Neo4j Configuration (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Cache Configuration
CACHE_ENABLED=true
CACHE_CLAUDE_TTL_DAYS=7
CACHE_EXPERIMENT_TTL_DAYS=30
CACHE_MAX_MEMORY_MB=512
CACHE_MAX_DISK_MB=5120

# Safety Configuration
ENABLE_SAFETY_CHECKS=true
MAX_EXPERIMENT_EXECUTION_TIME=300
ENABLE_SANDBOXING=true

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=~/.kosmos/logs/kosmos.log
```

### YAML Configuration

Create `~/.kosmos/config.yml`:

```yaml
claude:
  model: claude-3-5-sonnet-20241022
  max_tokens: 4096
  temperature: 1.0
  enable_cache: true

research:
  max_iterations: 10
  enabled_domains:
    - biology
    - neuroscience
    - materials
    - physics
    - chemistry
    - general
  min_novelty_score: 0.3
  auto_model_selection: true

database:
  url: sqlite:///kosmos.db

cache:
  enabled: true
  claude_ttl_days: 7
  experiment_ttl_days: 30
  max_memory_mb: 512
  max_disk_mb: 5120

safety:
  enable_checks: true
  max_execution_time: 300
  enable_sandboxing: true

logging:
  level: INFO
  file: ~/.kosmos/logs/kosmos.log
```

### Per-Domain Configuration

Customize settings for specific domains:

```yaml
domains:
  biology:
    enabled_apis:
      - KEGG
      - UniProt
      - PubMed
    default_experiment_types:
      - gene_expression_analysis
      - pathway_analysis

  neuroscience:
    enabled_apis:
      - FlyWire
      - AllenBrainAtlas
    default_experiment_types:
      - connectivity_analysis
      - activity_correlation
```

---

## Domain-Specific Usage

### Biology

**Best for:**
- Genetics and genomics
- Protein structure and function
- Metabolic pathways
- Disease mechanisms

**Example Questions:**
```bash
kosmos run "What genetic variants affect diabetes risk?" --domain biology
kosmos run "How does TP53 prevent cancer?" --domain biology
kosmos run "What are the metabolic differences in cancer cells?" --domain biology
```

**Available APIs:**
- KEGG (pathways and compounds)
- UniProt (proteins)
- GWAS Catalog (genetic variants)
- GTEx (gene expression)
- ENCODE (functional genomics)
- PubMed (literature)

### Neuroscience

**Best for:**
- Neural connectivity
- Brain function
- Cognitive processes
- Neurological diseases

**Example Questions:**
```bash
kosmos run "How does the hippocampus encode memories?" --domain neuroscience
kosmos run "What causes Alzheimer's disease?" --domain neuroscience
kosmos run "How do brain networks support consciousness?" --domain neuroscience
```

**Available APIs:**
- FlyWire (connectomics)
- Allen Brain Atlas (gene expression)
- NeuroMorpho (neuron morphology)
- PubMed (literature)

### Materials Science

**Best for:**
- Materials properties
- Property prediction
- Materials optimization
- Computational design

**Example Questions:**
```bash
kosmos run "Optimize battery cathode materials" --domain materials
kosmos run "Predict band gap of perovskites" --domain materials
kosmos run "Design materials for solar cells" --domain materials
```

**Available APIs:**
- Materials Project (materials database)
- MP API (properties and calculations)

### Physics

**Best for:**
- Physical systems
- Mechanics
- Thermodynamics
- Quantum systems

**Example Questions:**
```bash
kosmos run "How does turbulence affect flow?" --domain physics
kosmos run "What are the properties of topological insulators?" --domain physics
```

### Chemistry

**Best for:**
- Molecular properties
- Chemical reactions
- Synthesis planning
- Drug design

**Example Questions:**
```bash
kosmos run "Predict reaction yield for synthesis" --domain chemistry
kosmos run "Design inhibitors for enzyme X" --domain chemistry
```

### General (Cross-Domain)

**Best for:**
- Multi-disciplinary questions
- Methodological questions
- Broad topics

**Example Questions:**
```bash
kosmos run "How can we use AI in scientific discovery?" --domain general
kosmos run "What are the best methods for time series analysis?" --domain general
```

---

## Advanced Features

### Budget Management

Set spending limits:

```bash
# Set budget in USD
kosmos run "question" --budget 25.00

# Budget exhausted behavior:
# - Research stops when budget reached
# - Partial results returned
# - Status shows "BUDGET_EXHAUSTED"
```

**Monitoring Budget:**

```bash
kosmos status run_abc123
# Shows:
# Cost: $12.50 / $25.00 (50%)
```

### Parallel Execution

Enable parallel experiment execution (requires more resources):

```python
# In interactive mode
parallel_execution? [y/N]: y
```

### Custom Experiment Types

Define custom experiment templates:

```python
# In Python API
from kosmos.experiments.template import ExperimentTemplate

template = ExperimentTemplate(
    name="my_custom_experiment",
    description="Custom analysis",
    parameters={...},
    code_template="..."
)

director.register_experiment_template(template)
```

---

## Troubleshooting

### Common Issues

#### 1. API Key Not Found

**Symptom:**
```
Error: ANTHROPIC_API_KEY not found
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check .env has API key
cat .env | grep ANTHROPIC_API_KEY

# Verify environment variable loaded
echo $ANTHROPIC_API_KEY

# If not loaded, source .env
export $(cat .env | grep -v '^#' | xargs)
```

#### 2. Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'kosmos'
```

**Solution:**
```bash
# Verify virtual environment activated
which python
# Should show venv path

# Reinstall in editable mode
pip install -e .

# Verify installation
pip show kosmos
```

#### 3. Database Errors

**Symptom:**
```
sqlalchemy.exc.OperationalError: no such table: research_runs
```

**Solution:**
```bash
# Delete old database
rm kosmos.db

# Run doctor to recreate
kosmos doctor
```

#### 4. Cache Issues

**Symptom:**
- Slow performance
- High memory usage
- Disk space issues

**Solution:**
```bash
# Check cache stats
kosmos cache --stats

# Optimize cache
kosmos cache --optimize

# If needed, clear cache
kosmos cache --clear
```

#### 5. Timeout Errors

**Symptom:**
```
TimeoutError: Experiment execution exceeded limit
```

**Solution:**
```bash
# Increase timeout in .env
MAX_EXPERIMENT_EXECUTION_TIME=600  # 10 minutes

# Or disable timeout (not recommended)
MAX_EXPERIMENT_EXECUTION_TIME=0
```

### Getting Help

If you encounter issues:

1. **Run diagnostics:**
   ```bash
   kosmos doctor
   ```

2. **Check logs:**
   ```bash
   tail -f ~/.kosmos/logs/kosmos.log
   ```

3. **Enable debug mode:**
   ```bash
   kosmos --debug run "question"
   ```

4. **Report issue:**
   - GitHub Issues: [github.com/your-org/kosmos/issues](https://github.com/your-org/kosmos/issues)
   - Include: Kosmos version, OS, Python version, error message, logs

---

## Next Steps

- [Architecture Documentation](architecture.md) - Understand the system design
- [Developer Guide](developer_guide.md) - Extend and customize Kosmos
- [API Reference](api/) - Detailed API documentation
- [Examples](../examples/) - Example research projects

---

For questions or support, see the troubleshooting guide or open an issue on GitHub.
