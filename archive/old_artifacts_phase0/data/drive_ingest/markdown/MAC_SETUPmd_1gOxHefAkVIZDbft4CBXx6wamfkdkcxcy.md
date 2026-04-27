# Mac Local Setup Guide

**Pnkln Agent Platform v0.2.0 - Collection → Enforcement**

Quick guide for Mac developers to install and test locally.

---

## Prerequisites

- macOS 10.15+ (Catalina or later)
- Python 3.10+ (3.11 recommended)
- Homebrew (optional but recommended)
- Git
- 2GB free disk space

---

## Quick Start (3 commands)

```bash
# 1. Clone repository (if not already)
git clone https://github.com/ehanc69/ShadowTag-v2-fastapi-services.git
cd ShadowTag-v2-fastapi-services

# 2. Run setup
./mac_setup.sh

# 3. Run demo
source venv/bin/activate
python examples/mac_local_demo.py
```

**Expected output:**
```
✓ ALL TESTS PASSED - MAC SETUP VALIDATED
```

---

## Alternative: Using Makefile

```bash
# Show available commands
make help

# Quick setup + demo
make dev

# Full setup + tests
make all

# Individual commands
make setup    # Run setup script
make demo     # Run demo
make test     # Run pytest
make clean    # Clean artifacts
```

---

## Manual Setup (Step-by-Step)

### 1. Install Python 3.11

```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify installation
python3 --version  # Should show 3.11.x
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

**Note:** Activate venv before running any Python commands.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 4. Validate Installation

```bash
python -c "from pnkln_agents import *; print('✓ Success')"
```

### 5. Run Demo

```bash
python examples/mac_local_demo.py
```

---

## Troubleshooting

### Python Version Issues

**Problem:** `python3: command not found`

**Solution:**
```bash
# Install Python via Homebrew
brew install python@3.11

# Add to PATH (if needed)
echo 'export PATH="/usr/local/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Virtual Environment Activation

**Problem:** `venv/bin/activate: No such file or directory`

**Solution:**
```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'pnkln_agents'`

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall package
pip install -e .

# Verify
python -c "import pnkln_agents; print(pnkln_agents.__version__)"
```

### Permission Denied

**Problem:** `Permission denied: ./mac_setup.sh`

**Solution:**
```bash
chmod +x mac_setup.sh
./mac_setup.sh
```

### Slow Installation

**Problem:** Dependencies taking >5 minutes to install

**Solution:**
```bash
# Use pip cache
pip install --cache-dir ~/.cache/pip -r requirements.txt

# Or install minimal dependencies first
pip install fastapi pydantic pytest
pip install -e .
```

---

## Testing

### Quick Validation (30 seconds)

```bash
make test-quick
# OR
python examples/mac_local_demo.py
```

### Full Test Suite (2-5 minutes)

```bash
make test
# OR
pytest tests/ -v
```

### Test Coverage

```bash
pytest --cov=src/pnkln_agents --cov-report=html
open htmlcov/index.html
```

---

## Development Workflow

### 1. Activate Environment

```bash
source venv/bin/activate
```

### 2. Make Changes

Edit files in `src/pnkln_agents/`

### 3. Test Changes

```bash
# Quick validation
python -c "from pnkln_agents import *"

# Run specific test
pytest tests/unit/test_jr_engine.py -v

# Run all tests
pytest
```

### 4. Format Code

```bash
make format
# OR
black src/
```

### 5. Lint Code

```bash
make lint
# OR
ruff check src/
```

---

## Environment Variables (Optional)

Create `.env` file for local configuration:

```bash
# Local development
APP_ENV=development
APP_DEBUG=true

# API keys (when needed)
# GEMINI_API_KEY=your_key_here
# YOUTUBE_API_KEY=your_key_here
# TWITTER_API_KEY=your_key_here
```

Load with:
```bash
source .env
```

---

## What's Tested?

The `mac_local_demo.py` script validates:

1. ✅ **Core Imports** - All modules load correctly
2. ✅ **JR Engine** - Purpose/Reasons/Brakes validation (<500μs)
3. ✅ **Judge #6 Lite** - GDPR/CAN-SPAM compliance (<90ms)
4. ✅ **Gemini Ingestion** - Multi-source collection
5. ✅ **Intelligence Agent** - Full pipeline (collection → enforcement)
6. ✅ **Compliance SDR** - Lead generation with enforcement
7. ✅ **Configuration** - Bootstrap constraints, revenue model, ingestion config

---

## Performance Benchmarks (Mac M1/M2)

| Component | Target | Typical Mac Performance |
|-----------|--------|------------------------|
| JR Engine | <500μs | ~50-100μs |
| Judge #6 | <90ms | ~5-20ms |
| Ingestion (10 items) | N/A | ~100-500ms |
| Full Demo | N/A | ~2-5 seconds |

---

## Next Steps After Setup

1. **Review Architecture:**
   - Read `docs/adr/001-enforcement-first-architecture.md`
   - Read `docs/adr/002-collection-enforcement-pipeline.md`

2. **Explore Code:**
   - `src/pnkln_agents/core/` - Core components
   - `src/pnkln_agents/agents/` - Agent implementations
   - `src/pnkln_agents/config/` - Configuration

3. **Run Examples:**
   - `examples/compliance_sdr_demo.py` - Enforcement-only demo
   - `examples/mac_local_demo.py` - Full validation

4. **Deploy:**
   - See `docs/deployment.md` for GKE deployment

---

## Cleanup

```bash
# Deactivate venv
deactivate

# Remove venv and artifacts
make clean

# Or manually
rm -rf venv/
rm -rf build/ dist/ *.egg-info
```

---

## Support

- **Issues:** [GitHub Issues](https://github.com/ehanc69/ShadowTag-v2-fastapi-services/issues)
- **Documentation:** [docs/](docs/)
- **ADRs:** [docs/adr/](docs/adr/)

---

**Status:** ✅ Mac setup validated for v0.2.0

**Last Updated:** 2025-11-15

**Version:** 0.2.0 (Collection + Enforcement)
