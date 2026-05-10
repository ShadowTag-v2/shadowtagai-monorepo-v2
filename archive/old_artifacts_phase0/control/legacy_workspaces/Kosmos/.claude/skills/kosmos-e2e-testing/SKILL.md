# Kosmos E2E Testing Skill

Comprehensive end-to-end testing automation for the Kosmos autonomous AI scientist project. Supports local models (Ollama), external APIs (Anthropic/OpenAI), and Docker sandbox for full workflow testing.

## Triggers

| Trigger | Description |
|---------|-------------|
| `kosmos test` | Run Kosmos tests with auto-detected provider |
| `kosmos e2e` | Set up and run E2E testing |
| `test workflow` | Test the ResearchWorkflow component |
| `local testing` | Configure local model testing |
| `provider switch` | Switch between test providers |
| `benchmark models` | Compare local vs API performance |
| `setup docker` | Set up Docker sandbox for Gap 4 |

## Quick Start

### 1. Check Environment
```bash
# Run health check to see what's available
.claude/skills/kosmos-e2e-testing/scripts/health-check.sh
```

### 2. Run Tests by Tier

```bash
# Sanity tests (~30s) - Quick validation with fast model
./scripts/run-tests.sh sanity

# Smoke tests (~2min) - Component checks
./scripts/run-tests.sh smoke

# E2E tests (~10min) - Full workflow with reasoning model
./scripts/run-tests.sh e2e

# Full suite (~20min) - Everything with coverage
./scripts/run-tests.sh full
```

### 3. Specify Provider

```bash
# Use fast local model (Qwen3 4B)
./scripts/run-tests.sh sanity local-fast

# Use reasoning model (DeepSeek-R1 8B)
./scripts/run-tests.sh e2e local-reasoning

# Use Anthropic API
./scripts/run-tests.sh e2e anthropic

# Auto-detect best available
./scripts/run-tests.sh e2e auto
```

## Test Tiers

| Tier | Duration | Provider | What It Tests |
|------|----------|----------|---------------|
| **Sanity** | ~30s | Fast local | Basic imports, config loading, mock workflow |
| **Smoke** | ~2min | Fast local | Unit tests + smoke tests |
| **E2E** | ~10min | Reasoning | Full research workflow, all gaps |
| **Production** | ~20min | External API | Final validation with Claude/GPT-4 |

## Provider Configuration

### Local Models (Ollama)

**Fast Model (qwen3:4b)**
- Speed: 30-40 tok/s
- VRAM: 2-3 GB
- Use for: Sanity, smoke, rapid iteration

**Reasoning Model (deepseek-r1:8b)**
- Speed: 6-7 tok/s
- VRAM: 5-6 GB
- Use for: E2E, complex reasoning, validation

### Setup Local Models
```bash
# Install models
ollama pull qwen3:4b
ollama pull deepseek-r1:8b

# Verify
ollama list
```

### External APIs

Set in `.env` or use config files:

```bash
# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
export OPENAI_API_KEY=sk-...

# Or source config file
source .claude/skills/kosmos-e2e-testing/configs/anthropic.env
```

## Docker Sandbox (Gap 4)

Required for full E2E testing that involves code execution.

### Auto-Setup
```bash
.claude/skills/kosmos-e2e-testing/scripts/setup-docker.sh
```

### Manual Setup
```bash
# Build sandbox image
cd docker/sandbox
docker build -t kosmos-sandbox:latest .

# Verify
docker run --rm kosmos-sandbox:latest python3 -c "import pandas; print('OK')"
```

## Integration with local-llm Skill

This skill works with the global `local-llm` skill for model management:

```bash
# Use local-llm triggers for model operations
# "How do I manage Ollama models?" → local-llm skill
# "Run Kosmos E2E tests" → this skill

# Shared model names
# qwen3:4b - Same as local-llm fast-model template
# deepseek-r1:8b - Same as local-llm reasoning-model template
```

## Python API

```python
from lib.provider_detector import detect_all, recommend_test_tier
from lib.test_runner import run_tests
from lib.config_manager import load_config, switch_provider

# Check what's available
status = detect_all()
print(f"Ollama: {status['ollama']}")
print(f"Docker: {status['docker_sandbox']}")
print(f"Recommended tier: {recommend_test_tier(status)}")

# Run tests programmatically
results = run_tests(tier='e2e', provider='local-reasoning')
print(f"Passed: {results['passed']}/{results['total']}")
```

## Directory Structure

```
.claude/skills/kosmos-e2e-testing/
├── SKILL.md              # This file
├── CHEATSHEET.md         # Quick reference
├── reference.md          # Technical details
├── examples.md           # Usage examples
├── configs/              # Provider configurations
│   ├── local-fast.env
│   ├── local-reasoning.env
│   ├── anthropic.env
│   └── openai.env
├── templates/            # Test scripts
│   ├── sanity-test.py
│   ├── smoke-test.py
│   ├── e2e-runner.py
│   └── benchmark.py
├── scripts/              # Shell automation
│   ├── run-tests.sh
│   ├── setup-docker.sh
│   ├── switch-provider.sh
│   └── health-check.sh
└── lib/                  # Python library
    ├── provider_detector.py
    ├── test_runner.py
    ├── config_manager.py
    └── report_generator.py
```

## Service Availability Matrix

| Test Category | Anthropic | Docker | Neo4j | Redis | ChromaDB |
|---------------|-----------|--------|-------|-------|----------|
| Unit (gap modules) | Mock | No | No | No | No |
| Unit (literature) | Mock | No | No | No | No |
| Unit (knowledge) | Mock | No | Yes | No | Yes |
| Unit (execution) | No | Yes | No | No | No |
| Integration | Real/Mock | No | Mock | Mock | Mock |
| E2E | Real | Yes | Optional | Optional | Optional |

## Known Issues & Limitations

1. **arxiv package incompatibility**: Fails on Python 3.11+ due to `sgmllib3k` dependency. Literature search features limited.

2. **Docker requirement**: Gap 4 execution environment requires Docker. Without it, code execution uses mock/direct implementations.

3. **Database model issues**: Some tests skip due to "Hypothesis model ID missing autoincrement=True" - model definition issue.

4. **Complex agent setup**: Some agents (ExperimentDesigner, DataAnalyst) require complex object initialization.

5. **API mismatches**: Some integration tests have API mismatches with current implementation.

6. **No R support**: Paper references R packages; implementation is Python-only.

7. **Single-user**: No multi-tenancy or user isolation.

## Troubleshooting

### Ollama Not Responding
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start service
ollama serve

# Check logs
journalctl -u ollama -f
```

### Docker Issues
```bash
# Check Docker daemon
docker info

# Start Docker
sudo systemctl start docker

# Rebuild sandbox if corrupted
docker rmi kosmos-sandbox:latest
./scripts/setup-docker.sh
```

### Tests Timing Out
```bash
# Increase timeout
pytest tests/e2e/ -v --timeout=900

# Or run with reasoning model (slower but more reliable)
./scripts/run-tests.sh e2e local-reasoning
```

### API Key Issues
```bash
# Verify key is set
echo $ANTHROPIC_API_KEY

# Check .env file
cat .env | grep API_KEY

# Re-source config
source .claude/skills/kosmos-e2e-testing/configs/anthropic.env
```

### Python 3.11+ Package Issues
```bash
# If arxiv package fails
# Option 1: Use mock for literature search
export MOCK_LITERATURE_SEARCH=true

# Option 2: Install alternative client
pip install arxiv-python

# Option 3: Pin Python to 3.10
pyenv install 3.10.12
pyenv local 3.10.12
```

### Generate Dependency Report
```bash
# Generate E2E_TESTING_DEPENDENCY_REPORT.md
python -c "from lib.report_generator import generate_dependency_report; generate_dependency_report()"
```

## See Also

- `CHEATSHEET.md` - Quick command reference
- `reference.md` - Technical API documentation
- `examples.md` - Detailed usage examples
- `~/.claude/skills/local-llm/` - Local model management
- `E2E_TESTING_GUIDE.md` - General E2E testing guide
