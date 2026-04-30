# Resume Prompt: Review E2E Testing Prompts for Skill Alignment

## Task

Review and update the E2E testing prompt files to work optimally with the recently updated E2E testing skill.

## Background

The E2E testing skill at `.claude/skills/kosmos-e2e-testing/` was updated (commit `97ce2d8`) to:
- Fix import paths to match actual Kosmos codebase
- Add detection for Neo4j, Redis, ChromaDB, Python packages
- Add integration test tier
- Add comprehensive environment variable handling
- Add dependency report generation
- Add service availability matrix and known issues

Now we need to review the two prompt files to ensure they align with these changes.

## Files to Review

1. **`e2e_testing_prompt.md`** - Comprehensive E2E testing plan prompt
2. **`e2e_testing_missing_dependencies_report_prompt.md`** - Dependency analysis prompt

## Reference Files (Read First)

1. **`docs/planning/CHECKPOINT_E2E_SKILL_ALIGNMENT_2025-11-26.md`** - Full context and details
2. **`.claude/skills/kosmos-e2e-testing/SKILL.md`** - Updated skill documentation
3. **`.claude/skills/kosmos-e2e-testing/templates/e2e-runner.py`** - Correct import paths
4. **`.claude/skills/kosmos-e2e-testing/lib/provider_detector.py`** - Detection capabilities
5. **`.claude/skills/kosmos-e2e-testing/reference.md`** - Environment variables and markers

## Specific Review Tasks

### For `e2e_testing_prompt.md`:

1. **System Architecture section** - Check if module paths match actual codebase:
   - Should reference `kosmos/compression/compressor.py` not `kosmos/compression/context_compressor.py`
   - Should reference `kosmos/world_model/artifacts.py` not just `kosmos/world_model/`

2. **Gap numbering** - Ensure gaps are numbered 0-5:
   - Gap 0: Context Compression
   - Gap 1: State Management
   - Gap 2: Task Generation
   - Gap 3: Agent Integration
   - Gap 4: Execution Environment
   - Gap 5: Discovery Validation

3. **Entry Points section** - Verify API signatures match actual implementation

4. **Configuration section** - Add any missing environment variables that the skill now supports:
   - `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
   - `REDIS_URL`
   - `CHROMA_PERSIST_DIRECTORY`
   - `SEMANTIC_SCHOLAR_API_KEY`

5. **Test Markers** - Add missing markers:
   - `@pytest.mark.requires_api_key`
   - `@pytest.mark.requires_neo4j`
   - `@pytest.mark.requires_claude`

6. **Test Environment Configurations** - Add integration tier (currently missing)

### For `e2e_testing_missing_dependencies_report_prompt.md`:

1. **Output format** - Should mention that the skill can generate `E2E_TESTING_DEPENDENCY_REPORT.md` automatically via `generate_dependency_report()`

2. **Service detection** - Update to match what the skill now detects (Neo4j, Redis, ChromaDB, Python packages, Python version)

3. **Report structure** - Align with what `lib/report_generator.py` produces

## Expected Output

For each prompt file, provide:
1. List of specific changes needed (with line numbers if possible)
2. Updated sections (if changes are significant)
3. Rationale for each change

## Note

The prompts are used to guide Claude in creating E2E testing plans and dependency reports. They should accurately reflect:
- The actual Kosmos codebase structure
- The capabilities of the E2E testing skill
- Correct class names and import paths
