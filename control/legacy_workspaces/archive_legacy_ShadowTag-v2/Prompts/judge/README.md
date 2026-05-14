# Judge #6 Prompt Templates

This directory contains system prompt templates for **Judge #6**, a high-accuracy, low-latency risk enforcement engine that applies ATP 5-19 Risk Frameworks to user inputs.

## Directory Structure

```
judge/
├── README.md                           # This file
├── metadata/
│   └── judge-versions.json             # Version registry and metadata
├── examples/
│   └── [benchmark test cases]          # Test cases for validation
├── v1/
│   └── [baseline prompts]              # v1 baseline (pre-pattern integration)
└── v2/                                 # v2 with four-pattern integration
    ├── variants/
    │   ├── variant-a-original-draft.md # Verbose variant (~800 tokens)
    │   └── variant-b-reconstructed.md  # Compressed variant (~420 tokens)
    └── AB-TEST-CONFIG.json             # A/B testing configuration
```

## What is Judge #6?

Judge #6 is a risk enforcement engine designed to:
- Evaluate user inputs against ATP 5-19 Risk Frameworks
- Make binary decisions: ALLOW, BLOCK, or FLAG_FOR_REVIEW
- Operate within strict SLA constraints (p99 latency ≤ 90ms)
- Maintain high accuracy with minimal false positives/negatives

### ATP 5-19 Framework Categories

- **A - Benign Intent**: Standard, low-risk queries
- **B - Misinformation**: Medical misinformation, scientific falsehoods
- **C - Harmful Instructions**: Dangerous/illegal instructions

## Version History

### v1 (Baseline)
- Initial Judge #6 implementation
- Baseline for accuracy comparisons
- No pattern integration

### v2 (Current - A/B Testing)
**Status**: A/B testing in progress
**Created**: 2025-11-14
**Expected Improvement**: 10-15% accuracy gain over v1

#### Four Integrated Patterns
1. **Scratchpad Reasoning**: Chain-of-thought before final output
2. **Structured Output Format**: Strict JSON schema
3. **Few-Shot Learning**: Gold standard examples
4. **Role Definition & Constraints**: Clear operational boundaries

#### Variants

**Variant A: Original Draft**
- Token count: ~800
- Latency profile: At risk (may breach p99 ≤ 90ms)
- Source: Gemini Analysis
- Approach: Verbose, explicit scaffolding

**Variant B: Reconstructed**
- Token count: ~420 (-47% vs Variant A)
- Latency profile: Safe (well under p99 target)
- Source: Ultrathink Review + Jobs Doctrine
- Approach: Compressed, optimized for latency
- Hypothesis: Equal accuracy, superior latency

## A/B Testing

**Objective**: Validate that 47% token reduction maintains accuracy while improving latency

**Test Parameters**:
- Sample size: 1,000 inputs
- Distribution: 50% Variant A, 50% Variant B
- Categories: Benign queries, misinformation, harmful instructions, edge cases

**Success Criteria**:
- Accuracy confidence interval < 2%
- p99 latency ≤ 90ms for both variants
- No increase in false negatives

**Kill Switch Conditions**:
- p99 latency > 90ms → Immediate termination
- Accuracy drop > 2% vs baseline → Immediate termination
- False negative rate > 5% → Immediate termination

## Usage

### Loading a Prompt Template

```python
# Example: Load Variant B (Reconstructed)
from prompt_loader import load_judge_prompt

prompt = load_judge_prompt(
    version="v2",
    variant="b"
)
```

### Running A/B Tests

```python
# Example: Execute A/B test
from ab_test_runner import run_ab_test

results = run_ab_test(
    config_path="prompts/judge/v2/AB-TEST-CONFIG.json",
    sample_size=1000
)
```

## Output Format

All Judge #6 variants produce standardized JSON output:

```json
{
  "decision": "ALLOW|BLOCK|FLAG_FOR_REVIEW",
  "policy_citation": "ATP-5-19.[Section]",
  "justification": "<30 words max>"
}
```

## Design Philosophy

> "Simplicity is the ultimate sophistication. This is the prompt."
> — Jobs Doctrine Applied

### Key Principles
1. **Contract-First Design**: Output format leads, not trails
2. **Zero Meta-Commentary**: Models execute, they don't need motivation
3. **Aggressive Compression**: Remove anything that doesn't improve accuracy
4. **Latency-Aware**: Token count is a first-class constraint
5. **Validated Elegance**: Can't remove more without losing function

## SLA Constraints

- **p99 Latency**: ≤ 90ms
- **Accuracy Threshold**: Baseline + 10%
- **False Negative Rate**: ≤ 2%
- **False Positive Rate**: ≤ 5%

## Next Steps

1. Execute 1,000-sample A/B benchmark test
2. Measure accuracy delta between variants
3. Measure latency profile (p50, p95, p99)
4. Declare winner based on success criteria
5. Promote winning variant to production
6. Monitor production metrics for 7 days
7. Document findings for future optimizations

## References

- **Design Critique**: See `/docs/JUDGE-6-V2-DESIGN-CRITIQUE.md`
- **Version Registry**: See `metadata/judge-versions.json`
- **A/B Test Config**: See `v2/AB-TEST-CONFIG.json`

## Contributing

When modifying Judge prompts:
1. Always create a new variant for testing
2. Update `metadata/judge-versions.json`
3. Run A/B tests before promoting to production
4. Document all changes in version changelog
5. Validate against SLA constraints

---

**Maintained by**: JR Engine (Core Decision Authority)
**Last Updated**: 2025-11-14
