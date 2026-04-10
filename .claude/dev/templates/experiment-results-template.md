# Experiment: [Experiment Name] - Results

**Completed**: [Date]
**Status**: [Success/Partial Success/Failed]
**Experiment ID**: [experiment-id]

---

## Executive Summary

### Outcome
[2-3 sentences: Did we prove/disprove hypothesis? What did we learn?]

### Key Findings
1. [Finding 1]
2. [Finding 2]
3. [Finding 3]

### Recommendation
**[Deploy/Iterate/Abandon]**: [Brief rationale]

---

## Hypothesis Validation

### Original Hypothesis
**We believed that** [doing X]
**Would result in** [outcome Y]
**As measured by** [metric Z]

### Actual Outcome
**Result**: [Hypothesis confirmed/rejected/partially confirmed]
**Evidence**: [Supporting data]

---

## Model Performance

### Final Metrics

#### Training Set
```
Metric 1: [X.XX]
Metric 2: [X.XX]
Metric 3: [X.XX]
```

#### Validation Set
```
Metric 1: [X.XX] (target: [Y.YY]) - [✅/❌]
Metric 2: [X.XX] (target: [Y.YY]) - [✅/❌]
Metric 3: [X.XX] (target: [Y.YY]) - [✅/❌]
```

#### Test Set (Final Evaluation)
```
Metric 1: [X.XX]
Metric 2: [X.XX]
Metric 3: [X.XX]
```

### Comparison to Baseline
| Metric | Baseline | Our Model | Δ | % Improvement |
|--------|----------|-----------|---|---------------|
| Metric 1 | [X.XX] | [Y.YY] | [+Z.ZZ] | [+XX%] |
| Metric 2 | [X.XX] | [Y.YY] | [+Z.ZZ] | [+XX%] |
| Metric 3 | [X.XX] | [Y.YY] | [+Z.ZZ] | [+XX%] |

### Statistical Significance
- **Test Used**: [t-test, bootstrap, etc.]
- **P-value**: [X.XXX]
- **Confidence Interval**: [[lower, upper]]
- **Conclusion**: [Statistically significant/not significant]

---

## Hyperparameter Tuning Results

### Search Summary
- **Total Trials**: [N]
- **Search Method**: [Grid/Random/Bayesian]
- **Optimization Metric**: [metric-name]

### Best Configuration
```python
best_hyperparameters = {
    "learning_rate": 0.001,
    "batch_size": 64,
    "num_layers": 3,
    "hidden_size": 128,
    # ... all tuned parameters
}
```

### Top 5 Trials
| Trial | Metric | Learning Rate | Batch Size | ... |
|-------|--------|--------------|------------|-----|
| 17    | 0.921  | 0.001        | 64         | ... |
| 23    | 0.918  | 0.001        | 128        | ... |
| 9     | 0.915  | 0.005        | 64         | ... |
| 31    | 0.912  | 0.001        | 32         | ... |
| 14    | 0.910  | 0.01         | 64         | ... |

### Hyperparameter Importance
1. **[Parameter 1]**: [High/Medium/Low impact] - [Description]
2. **[Parameter 2]**: [High/Medium/Low impact] - [Description]
3. **[Parameter 3]**: [High/Medium/Low impact] - [Description]

---

## Error Analysis

### Confusion Matrix (for classification)
```
               Predicted
             0      1      2
Actual  0  [TN]   [FP]   [FP]
        1  [FN]   [TP]   [FP]
        2  [FN]   [FP]   [TP]
```

### Error Distribution
| Error Type | Count | % of Total | Avg Error Magnitude |
|------------|-------|-----------|-------------------|
| [Type 1]   | [N]   | [X%]      | [Y.YY]           |
| [Type 2]   | [N]   | [X%]      | [Y.YY]           |
| [Type 3]   | [N]   | [X%]      | [Y.YY]           |

### Common Failure Patterns
1. **[Pattern 1]**: [% of errors]
   - **Example**: [Specific example]
   - **Root Cause**: [Why model fails]
   - **Potential Fix**: [How to address]

2. **[Pattern 2]**: [% of errors]
   - **Example**: [Specific example]
   - **Root Cause**: [Why model fails]
   - **Potential Fix**: [How to address]

### Performance by Segment
| Segment | Metric 1 | Metric 2 | Sample Size |
|---------|----------|----------|-------------|
| [Seg 1] | [X.XX]   | [X.XX]   | [N]         |
| [Seg 2] | [X.XX]   | [X.XX]   | [N]         |
| [Seg 3] | [X.XX]   | [X.XX]   | [N]         |

---

## Model Interpretability

### Feature Importance
| Rank | Feature | Importance | Description |
|------|---------|-----------|-------------|
| 1    | [feat1] | [X.XX]    | [What it means] |
| 2    | [feat2] | [X.XX]    | [What it means] |
| 3    | [feat3] | [X.XX]    | [What it means] |
| 4    | [feat4] | [X.XX]    | [What it means] |
| 5    | [feat5] | [X.XX]    | [What it means] |

### SHAP/LIME Analysis (if applicable)
[Key insights from model explanation techniques]

### Model Behavior Insights
- [Insight 1: e.g., "Model relies heavily on feature X"]
- [Insight 2: e.g., "Model struggles with edge case Y"]
- [Insight 3: e.g., "Interaction between features A and B is critical"]

---

## Training Efficiency

### Resource Utilization
- **Total Training Time**: [X hours, Y minutes]
- **GPU Hours**: [Z hours]
- **Peak Memory**: [X GB]
- **Average GPU Utilization**: [Y%]

### Cost Analysis
- **Training Cost**: $[X.XX]
- **Tuning Cost**: $[Y.YY]
- **Total Experiment Cost**: $[Z.ZZ]
- **Cost per 1% improvement**: $[A.AA]

### Efficiency Observations
- [Observation 1: e.g., "Could reduce training time by X% with larger batch size"]
- [Observation 2: e.g., "Early stopping saved Y hours"]

---

## Visualizations

### Learning Curves
![Training/Validation Loss](path/to/loss_curve.png)
![Training/Validation Metric](path/to/metric_curve.png)

**Observations**:
- [Observation 1]
- [Observation 2]

### Prediction Distribution
![Prediction Distribution](path/to/pred_dist.png)

**Observations**:
- [Observation 1]
- [Observation 2]

### Error Analysis Plots
![Error by Feature](path/to/error_analysis.png)

**Observations**:
- [Observation 1]
- [Observation 2]

---

## Deployment Readiness

### Production Criteria
- [ ] Meets performance targets: [Yes/No]
- [ ] No critical failure modes: [Yes/No]
- [ ] Acceptable inference latency: [X ms]
- [ ] Model size reasonable: [X MB]
- [ ] Resource requirements acceptable: [Yes/No]

### Deployment Configuration (if deploying)
```yaml
deployment:
  model_version: v1.0.0
  endpoint: [endpoint-name]
  instance_type: n1-standard-2
  min_replicas: 1
  max_replicas: 10
  traffic_split:
    v1.0.0: 100%  # or A/B test config
```

### Monitoring Plan
- **Prediction Drift**:
  - Metric: [KL divergence, PSI, etc.]
  - Threshold: [X]
  - Alert: [When threshold exceeded]

- **Performance Degradation**:
  - Metric: [Online metric to track]
  - Threshold: [Y]
  - Alert: [When below threshold]

---

## Lessons Learned

### What Worked Well
1. [Success 1]
2. [Success 2]
3. [Success 3]

### What Didn't Work
1. [Challenge 1 and how we addressed it]
2. [Challenge 2 and how we addressed it]

### Unexpected Discoveries
1. [Discovery 1]
2. [Discovery 2]

### Would Do Differently Next Time
1. [Change 1]
2. [Change 2]

---

## Next Steps

### If Deploying
- [ ] Submit model to registry
- [ ] Create endpoint in Vertex AI
- [ ] Configure monitoring and alerting
- [ ] Set up A/B test (if applicable)
- [ ] Document inference API
- [ ] Train support team

### If Iterating
**Experiment v2 Focus**:
- [Improvement 1]: [Rationale]
- [Improvement 2]: [Rationale]
- [Improvement 3]: [Rationale]

### Open Questions for Future Work
1. [Question 1]
2. [Question 2]

---

## Reproducibility

### Artifacts
- **Model Checkpoint**: `gs://[bucket]/models/[name]/[version]/model.pkl`
- **Training Code**: Git commit [hash]
- **Training Data**: `bq://[project].[dataset].[table]` (snapshot [date])
- **Config**: `configs/experiment_[name].yaml`
- **Environment**: `uv.lock` hash [first 12 chars]

### Reproduction Steps
```bash
# 1. Restore environment
uv sync --locked

# 2. Prepare data
uv run python scripts/prepare_data.py --config configs/[experiment].yaml

# 3. Train model
uv run python train.py \
  --experiment-id [experiment-id] \
  --config configs/[experiment].yaml \
  --seed 42

# 4. Evaluate
uv run python evaluate.py \
  --model-path gs://[bucket]/models/[name]/[version]/model.pkl \
  --test-data [path]
```

### Verification
- **Training Metrics Match**: [Yes/No]
- **Validation Metrics Match**: [Yes/No]
- **Test Metrics Match**: [Yes/No]
- **Reproduced by**: [Name/Date]

---

## References

- **Plan**: experiment-[name]-plan.md
- **Context**: experiment-[name]-context.md
- **Tasks**: experiment-[name]-tasks.md
- **Vertex AI Experiment**: [URL]
- **Model Registry**: [URL]
- **Related Papers**: [Citations]
- **Prior Experiments**: [Links]

---

## Sign-off

**Completed by**: [Name]
**Reviewed by**: [Name]
**Approved for**: [Production/Next Iteration/Archive]
**Date**: [Date]
