# Kosmos Project In-Depth Code Review Prompt

## Objective
Conduct a comprehensive code review of the Kosmos autonomous AI scientist project to identify any issues that would prevent it from being operational. Focus on production readiness, critical bugs, missing implementations, configuration problems, and integration failures.

---

## Review Scope

### 1. Critical Path Analysis
Review the main execution flow from entry point to completion:

```
kosmos/cli/main.py → kosmos/workflow/research_loop.py → Gap Implementations (0-5)
```

**Tasks:**
- Trace the complete execution path of `kosmos run` command
- Verify `ResearchWorkflow.run()` method completes all cycles without exceptions
- Check that all 6 gap implementations are properly integrated
- Identify any dead code paths or unreachable branches
- Verify async/await patterns are correctly implemented throughout

---

### 2. Dependency and Import Verification

**Tasks:**
- Run `pip install -e .` and document any installation failures
- Check for circular import issues in the `kosmos/` package
- Verify all imports in `__init__.py` files resolve correctly
- Test import of each major module: `kosmos.workflow`, `kosmos.core`, `kosmos.agents`
- Check for version conflicts in `pyproject.toml` dependencies
- Verify `arxiv` package installation issue (sgmllib3k incompatibility on Python 3.11+)
- Check NumPy version constraint `<2.0.0` compatibility with other packages

**Commands to run:**
```bash
python -c "from kosmos.workflow.research_loop import ResearchWorkflow"
python -c "from kosmos.core.llm import get_llm_client"
python -c "from kosmos.agents import *"
python -c "from kosmos.execution import *"
pip check  # Check for dependency conflicts
```

---

### 3. Configuration System Audit

**Files to review:**
- `kosmos/config.py` (680+ lines)
- `.env.example`
- `kosmos/core/llm.py`

**Tasks:**
- Verify all Pydantic V2 configurations use `model_config = ConfigDict(...)` not `class Config`
- Check environment variable loading with `python-dotenv`
- Test configuration with minimal `.env` (only API key)
- Test configuration with full `.env.example` settings
- Verify default values are sensible for first-time users
- Check that missing optional services (Redis, Neo4j) fail gracefully
- Audit configuration validation errors for clarity

**Critical checks:**
```python
# Test minimal config
from kosmos.config import get_settings
settings = get_settings()
print(settings.llm_provider)
print(settings.database_url)
```

---

### 4. Database and Migration Verification

**Files to review:**
- `kosmos/db/models.py`
- `kosmos/db/database.py`
- `alembic/versions/*.py`
- `alembic.ini`

**Tasks:**
- Verify SQLAlchemy 2.0 compatibility (no deprecated patterns)
- Check all migrations apply cleanly to fresh database
- Verify foreign key relationships are correctly defined
- Test database operations (CRUD) for all models
- Check for N+1 query issues in relationship loading
- Verify connection pool settings for SQLite vs PostgreSQL
- Test concurrent access scenarios

**Commands to run:**
```bash
rm kosmos.db  # Fresh start
alembic upgrade head
alembic current
python -c "from kosmos.db.database import get_session; print('DB OK')"
```

---

### 5. LLM Integration Testing

**Files to review:**
- `kosmos/core/llm.py`
- `kosmos/core/claude_client.py`
- `kosmos/core/openai_client.py`

**Tasks:**
- Verify API client initialization for Anthropic Claude
- Verify API client initialization for OpenAI
- Test model selection and fallback logic
- Check prompt caching implementation
- Verify token counting and rate limiting
- Test error handling for API failures (rate limits, timeouts, invalid responses)
- Check streaming response handling
- Verify cost estimation accuracy

**Test scenarios:**
```python
# Test with valid API key
client = get_llm_client()
response = await client.complete("Test prompt")

# Test error handling
# - Missing API key
# - Invalid API key
# - Rate limit exceeded
# - Model not available
```

---

### 6. Gap Implementation Verification

#### Gap 0: Context Compression
**Files:** `kosmos/compression/compressor.py`, `kosmos/compression/notebook_compressor.py`

**Tasks:**
- Test notebook compression with real Jupyter notebook
- Verify 20:1 compression ratio claim
- Check compression preserves semantic meaning
- Test with edge cases (empty notebook, large notebook, malformed JSON)

#### Gap 1: State Management
**Files:** `kosmos/world_model/artifacts.py`, `kosmos/world_model/state_manager.py`

**Tasks:**
- Verify artifact serialization/deserialization
- Test state persistence across workflow restarts
- Check JSON artifact format compatibility
- Verify knowledge graph integration (optional Neo4j)

#### Gap 2: Orchestration
**Files:** `kosmos/orchestration/plan_creator.py`, `kosmos/orchestration/plan_reviewer.py`, `kosmos/orchestration/delegation.py`

**Tasks:**
- Test plan generation with various research objectives
- Verify 5-dimension scoring in plan reviewer
- Check delegation routing logic
- Test novelty detection for duplicate avoidance

#### Gap 3: Skill Loading
**Files:** `kosmos/agents/skill_loader.py`, `kosmos/skills/`

**Tasks:**
- Verify skill discovery mechanism
- Test skill loading for each domain (biology, materials, physics, chemistry)
- Check skill registry completeness (116+ claimed skills)
- Test dynamic skill injection into agent prompts

#### Gap 4: Code Execution (CRITICAL)
**Files:** `kosmos/execution/`, `docker/sandbox/`

**Tasks:**
- **CRITICAL**: Verify Docker availability and sandbox build
- Test container pooling and lifecycle management
- Verify resource limits (CPU, memory, network)
- Test package installation within sandbox
- Check timeout handling for runaway code
- Verify output capture (stdout, stderr, exceptions)
- Test Jupyter kernel gateway connectivity
- Check security: no host filesystem access, no network egress

**Commands to run:**
```bash
docker images | grep kosmos-sandbox
docker run --rm kosmos-sandbox:latest python --version
cd docker/sandbox && docker build -t kosmos-sandbox:latest .
```

#### Gap 5: Validation
**Files:** `kosmos/validation/scholar_eval.py`

**Tasks:**
- Verify 8-dimension scoring implementation
- Test score aggregation and weighting
- Check threshold configuration for discovery acceptance
- Test validation with sample discoveries

---

### 7. Agent System Review

**Files to review:**
- `kosmos/agents/base_agent.py`
- `kosmos/agents/research_agent.py`
- `kosmos/agents/hypothesis_agent.py`
- `kosmos/agents/experiment_agent.py`
- `kosmos/agents/analysis_agent.py`

**Tasks:**
- Verify agent initialization and lifecycle
- Check message passing between agents
- Test agent state serialization
- Verify prompt templates are complete
- Check for context window overflow handling
- Test agent error recovery

---

### 8. Literature Search Integration

**Files to review:**
- `kosmos/literature/arxiv_client.py`
- `kosmos/literature/semantic_scholar.py`
- `kosmos/literature/pubmed_client.py`

**Tasks:**
- Test arXiv search (note: arxiv package may be broken)
- Test Semantic Scholar API integration
- Test PubMed API integration
- Verify rate limiting implementation
- Check error handling for API failures
- Test citation parsing and formatting

---

### 9. CLI Functionality Testing

**Commands to test:**
```bash
# Installation
pip install -e .
kosmos --help

# Configuration
kosmos config show
kosmos config validate

# Cache management
kosmos cache status
kosmos cache clear

# Status
kosmos status

# Main workflow (requires API key)
kosmos run "Test research question" --num-cycles 1 --tasks-per-cycle 2 --dry-run

# Profiling
kosmos profile enable
kosmos profile show
```

---

### 10. Test Suite Verification

**Tasks:**
- Run full unit test suite: `pytest tests/unit/ -v`
- Run integration tests: `pytest tests/integration/ -v`
- Run smoke tests: `pytest tests/smoke/ -v`
- Document all failing tests and root causes
- Check test coverage: `pytest --cov=kosmos tests/unit/`
- Verify test fixtures are current with implementation

**Expected results:**
- Unit tests: 273/273 passing
- Integration tests: 43/96 passing (investigate failures)
- E2E tests: 0/4 passing (require Docker + API keys)
- Smoke tests: 7/7 passing

---

### 11. Security Audit

**Tasks:**
- Check for hardcoded secrets or API keys
- Verify `.gitignore` excludes sensitive files
- Audit Docker sandbox for container escape vulnerabilities
- Check input validation for user-provided research questions
- Verify SQL injection prevention in database operations
- Check for command injection in Bash execution
- Audit code execution sandbox isolation
- Review dependency vulnerabilities: `pip-audit` or `safety check`

---

### 12. Error Handling and Logging

**Tasks:**
- Verify consistent error handling patterns
- Check logging configuration and levels
- Test error messages for clarity and actionability
- Verify exceptions don't leak sensitive information
- Check graceful degradation when optional services unavailable

---

### 13. Performance Considerations

**Tasks:**
- Identify potential bottlenecks in research loop
- Check for memory leaks in long-running workflows
- Verify async operations don't block event loop
- Test with large artifact sets
- Check database query performance

---

## Output Format

For each issue found, document:

```markdown
### Issue: [Brief Title]

**Severity:** Critical | High | Medium | Low
**Category:** [Dependency | Configuration | Runtime | Security | Test | Documentation]
**Location:** [File path and line number]

**Description:**
[Detailed description of the issue]

**Impact:**
[How this prevents operational status]

**Reproduction Steps:**
[Commands or code to reproduce]

**Recommended Fix:**
[Specific fix with code examples if applicable]

**Verification:**
[How to verify the fix works]
```

---

## Execution Checklist

Use this checklist to track review progress:

- [ ] Environment setup (Python 3.11+, pip install -e .)
- [ ] Configuration validation (.env file, API keys)
- [ ] Database migration verification
- [ ] LLM client connectivity test
- [ ] Gap 0: Compression module test
- [ ] Gap 1: State management test
- [ ] Gap 2: Orchestration test
- [ ] Gap 3: Skill loader test
- [ ] Gap 4: Docker execution test (CRITICAL)
- [ ] Gap 5: Validation test
- [ ] Agent system test
- [ ] Literature search test
- [ ] CLI commands test
- [ ] Unit test suite run
- [ ] Integration test suite run
- [ ] Security scan
- [ ] Error handling audit
- [ ] Documentation accuracy check

---

## Known Issues to Verify

Based on preliminary analysis, verify these known issues:

1. **Docker Not Available** - Gap 4 execution requires Docker sandbox
2. **arxiv Package Incompatibility** - sgmllib3k fails on Python 3.11+
3. **Integration Test Failures** - 53/96 failing, need root cause analysis
4. **E2E Tests Blocked** - Require Docker + real API keys
5. **Pydantic V2 Migration** - Verify all `class Config` converted to `model_config`
6. **NumPy Version Constraint** - `<2.0.0` may cause conflicts
7. **Optional Service Handling** - Neo4j, Redis graceful degradation

---

## Final Deliverable

Produce a comprehensive report with:

1. **Executive Summary** - Overall operational readiness assessment
2. **Critical Blockers** - Issues that must be fixed before operation
3. **High Priority Issues** - Issues that significantly impact functionality
4. **Medium Priority Issues** - Issues that degrade experience but don't block
5. **Low Priority Issues** - Minor improvements and technical debt
6. **Test Results Summary** - Pass/fail counts with failure analysis
7. **Recommended Fix Order** - Prioritized list of fixes
8. **Operational Checklist** - Steps to make system fully operational

---

## Output Instructions

### Write Output to File

After completing the code review, write the full report to:

```
/mnt/c/python/Kosmos/CODE_REVIEW_REPORT_1125.md
```

The report file should include:
- Date and time of review
- Reviewer identifier (e.g., "Claude Code Review")
- All sections from the Final Deliverable above
- Complete issue documentation using the Output Format template
- Test results with pass/fail counts
- Recommendations summary

### Commit and Push to Remote Repository

After writing the report file, commit and push to the remote repository:

```bash
# Stage the review report
git add CODE_REVIEW_REPORT_1125.md

# Create commit with descriptive message
git commit -m "$(cat <<'EOF'
Add comprehensive code review report (2024-11-25)

- Complete operational readiness assessment
- Document critical blockers and priority issues
- Include test suite results and failure analysis
- Provide recommended fix order and verification steps

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Push to remote repository
git push origin master
```

### Post-Push Verification

After pushing, verify the commit was successful:

```bash
# Verify commit exists on remote
git log origin/master -1 --oneline

# Verify file is in remote
git ls-tree origin/master --name-only | grep CODE_REVIEW
```

---

## Summary of Actions

When executing this code review prompt, perform these steps in order:

1. **Conduct Review** - Follow all sections in Review Scope (1-13)
2. **Document Issues** - Use the Output Format template for each issue found
3. **Compile Report** - Create the Final Deliverable with all required sections
4. **Write to File** - Save report to `CODE_REVIEW_REPORT_1125.md`
5. **Git Add** - Stage the new report file
6. **Git Commit** - Commit with descriptive message
7. **Git Push** - Push to remote repository (origin/master)
8. **Verify** - Confirm push was successful

---

## Additional Notes

- This review targets the Kosmos v0.2.0-alpha release
- Focus on issues that prevent the autonomous research workflow from completing
- Consider both development (SQLite, mock execution) and production (PostgreSQL, Docker) modes
- Document workarounds for issues that cannot be immediately fixed
- Reference the original paper (Lu et al., 2024) for expected behavior verification
- The output file `CODE_REVIEW_REPORT_1125.md` should be committed to the repository for tracking
