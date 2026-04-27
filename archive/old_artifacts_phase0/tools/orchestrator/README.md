# ACE-Inspired Opposing-Chain Interrogation Workflow

Implements Agentic Context Engineering (ACE) pattern for self-improving code generation.

## Architecture

```
Run1 (Chain A: Generator)
  → Produces code patch

Run2 (Chain A: Explainer via Cursor Plan Mode)
  → Reverse-engineers explanation of Run1

Run3 (Chain B: Opposition)
  → Critiques A's explanation
  → Optionally proposes corrective patch

Apply (Cursor 4-model stack)
  → Applies patches
  → Runs tests
  → Generates PR summary
```

## Key Benefits (from ACE paper)

| Metric | Baseline | With ACE | Improvement |
|--------|----------|----------|-------------|
| Accuracy | - | +10.6 pp | AppWorld Agents benchmark |
| Token efficiency | 100% | 25-30% | 70-75% cost reduction |
| Adaptation latency | 100% | 13.1% | 86.9% faster updates |
| Context stability | Collapses after ~60 steps | Stable at 18k tokens | No collapse |

## Quick Start

### 1. Prerequisites

```bash
# Ensure multi-model router is running
cd router
npm run dev  # Runs on :8787
```

### 2. Install orchestrator dependencies

```bash
cd tools/orchestrator
npm install
```

### 3. Run full workflow

```bash
# Set your feature request
export FEATURE_REQUEST="Add a /metrics endpoint for Prometheus"

# Run triple pass
npm run triple:pass
```

### 4. Inspect artifacts

```bash
ls -l patches/     # Code patches from Chain A and B
ls -l explain/     # Explanation from Run2
ls -l review/      # Critique from Chain B
```

## Individual Steps

### Run1: Generate Code

```bash
npm run run1:code:A
# Output: patches/A.run1.patch
```

### Run2: Explain (Reverse Engineer)

```bash
npm run run2:explain:A
# Output: explain/A.run2.explain.md
```

### Run3: Oppose / Critique

```bash
npm run run3:oppose:B
# Output: review/B.run3.review.md
#        patches/B.run3.patch (if corrections needed)
```

### Apply in Cursor

```bash
npm run apply:cursor
# Applies patches and runs tests
```

## Integration with Cursor

Add to `.cursor/tasks.json`:

```json
{
  "tasks": [
    {
      "name": "ace_triple_pass",
      "command": "cd tools/orchestrator && npm run triple:pass",
      "description": "Run ACE-inspired opposing-chain workflow"
    }
  ]
}
```

Then in Cursor: `task: ace_triple_pass`

## Configuration

### Model Assignment

Edit `tools/orchestrator/lib/models.mjs`:

```javascript
// Chain A (Generator): Use fast model
callRouter("cheetah", prompt);

// Chain B (Critic): Use reasoning model
callRouter("grok", prompt);

// Explainer: Use strong model
callRouter("openai", prompt);
```

### Feature Request

Pass via environment variable:

```bash
export FEATURE_REQUEST="Your feature description here"
npm run triple:pass
```

Or edit `run1_code_A.mjs` directly.

## Expected Output

### Successful Run

```
🚀 Starting Triple Pass (ACE-inspired workflow)

📝 Run1: Chain A generates code...
✅ Wrote patches/A.run1.patch

📖 Run2: Chain A explains (Plan Mode)...
✅ Wrote explain/A.run2.explain.md

🔍 Run3: Chain B opposes/critiques...
✅ Wrote review/B.run3.review.md

✅ Apply: Cursor applies patches...
✅ Applied patches
Summary: Applied A patch, tests 45/45 pass, no security issues

🎉 Triple Pass completed successfully!
```

### When Chain B Finds Issues

```
🔍 Run3: Chain B opposes/critiques...
✅ Wrote patches/B.run3.patch
✅ Wrote review/B.run3.review.md

Review excerpt:
"⚠️ Potential race condition in /metrics endpoint.
Chain B proposes adding mutex lock (see B.run3.patch)."
```

## Performance

| Stage | Time | Cost (approx) | Model |
|-------|------|---------------|-------|
| Run1 | 5-15s | $0.001 | Cheetah |
| Run2 | 10-30s | $0.02 | GPT-5 |
| Run3 | 10-20s | $0.01 | Grok |
| Apply | 30-120s | $0.05 | Cursor multi-model |
| **Total** | **~1-3 min** | **~$0.08** | - |

Compare to manual code + review: ~30-60 minutes, $50-150 eng cost.

**ROI**: ~50-100× time savings, ~600-1800× cost efficiency.

## Troubleshooting

### Router not available

Ensure the multi-model router is running:

```bash
cd router && npm run dev
```

### Empty patches

Check that `FEATURE_REQUEST` is set:

```bash
echo $FEATURE_REQUEST
```

### Model errors

Check API keys in `router/.env`:

```bash
cat router/.env | grep API_KEY
```

---

**Owner**: ML Engineering & Platform
**Last Updated**: 2025-11-08
**Status**: Placeholder implementation (integrate with actual Cursor API for production)
