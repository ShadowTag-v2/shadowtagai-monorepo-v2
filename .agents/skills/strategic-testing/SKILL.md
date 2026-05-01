---
name: strategic-testing
description: Replaces vibe-clicking with surgical integration testing. Includes VCR fixture recording and Ralph Loop porting verification.
---
# Instructions
Do not write 100% boilerplate unit tests. Do not "vibe click" around the app.
Instead, identify the single critical path most likely to break in production. Write ONE Playwright test for that exact path. 
*Reality Constraint:* The Playwright config MUST simulate a 3G network and enforce a strict 30,000ms `actionTimeout`. If the user cannot complete the core action in 30 seconds, it is a product bug, not a feature gap.

## VCR Fixture Recording Pattern (API Cassette Recorder)

**Source:** Claude Code architecture (Reid Barber reverse engineering analysis).

When testing code that calls external LLM APIs (Gemini, Anthropic, etc.), use the VCR (Visual Cassette Recorder) pattern:

### Principle
1. **First run (record mode):** Make the real API call. Serialize the request + response pair to a fixture file in `tests/fixtures/vcr/`.
2. **Subsequent runs (replay mode):** Intercept the API call and return the recorded fixture. No live API needed.
3. **Gate:** Activate only when `NODE_ENV === 'test'` or `PYTEST_CURRENT_TEST` is set. Never record in production.

### Python Implementation (vcrpy)
```python
import vcr

@vcr.use_cassette('tests/fixtures/vcr/gemini_generate.yaml', record_mode='new_episodes')
def test_gemini_generation():
    # First run: real API call recorded to YAML fixture
    # Subsequent runs: replayed from fixture
    response = client.generate_content("test prompt")
    assert response.text is not None
```

### TypeScript Implementation (nock)
```typescript
import nock from 'nock';
import fs from 'fs';

const FIXTURE_PATH = 'tests/fixtures/vcr/gemini_generate.json';

function withVCR(scope: string, testFn: () => Promise<void>) {
  if (fs.existsSync(FIXTURE_PATH)) {
    // Replay mode
    const fixture = JSON.parse(fs.readFileSync(FIXTURE_PATH, 'utf-8'));
    nock(scope).post('/v1/models/gemini:generateContent').reply(200, fixture);
  }
  // Record mode handled by nock.recorder.rec()
}
```

### Rules
- Fixture files MUST be committed to git (they are deterministic test data, not secrets).
- Scrub API keys from recorded fixtures before committing.
- Re-record when the API contract changes (bump fixture version).
- Fixture file naming: `{test_module}__{test_function}.yaml`

## Ralph Loop — Cross-Language Port Verification

**Source:** Geoffrey Huntley's porting methodology (ghuntley.com/porting/).

When porting a codebase from one language to another, use the 4-stage Ralph Loop:

### Stage 1: Compress Tests → Specs
Study every file in `tests/*` using separate subagents. Document behavioral contracts in `/specs/*.md` with citations linking back to original test implementations.

### Stage 2: Compress Product Code → Specs
Study every file in `src/*` using separate subagents. Document functionality in `/specs/*.md` with citations to source implementations.

### Stage 3: Generate TODO → Execute
Create a prioritized TODO from specs. Execute one task per loop iteration. The agent follows citations in specs back to original source code for reference during implementation.

### Stage 4: Strict Compilation Gate
Configure the target language compiler/linter to maximum strictness. Each loop iteration must compile clean.

### Key Insight
Citations in specs tease the `file_read` tool to study original implementations. Reducing code to specs first **decouples the source language from the target**, transforming code into language-agnostic PRDs.
