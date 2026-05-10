# Experiment: [Experiment Name]

**Created**: [Date]
**Status**: [Planned/Running/Completed/Failed]
**Experiment ID**: [experiment-id]

---

## Hypothesis

### Research Question
[What are we trying to learn or prove?]

### Hypothesis Statement
**We believe that** [doing X]
**Will result in** [outcome Y]
**As measured by** [metric Z]

### Expected Outcome
[What we expect to see if hypothesis is correct]

---

## Experiment Configuration

### Dataset
- **Source**: [BigQuery table, Cloud Storage bucket, etc.]
- **Size**: [N samples, X GB]
- **Split**: Train [X%] / Val [Y%] / Test [Z%]
- **Features**: [Number of features, key features]
- **Target**: [Target variable, task type]

### Data Preprocessing
- [ ] Data cleaning: [Steps]
- [ ] Feature engineering: [Transformations]
- [ ] Normalization/scaling: [Method]
- [ ] Class balancing: [If applicable]

---

## Model Architecture

### Approach
[High-level ML approach: regression, classification, clustering, etc.]

### Model Type
[Specific model: XGBoost, Neural Network, LightGBM, etc.]

### Architecture Details
```python
# Model configuration
model_config = {
    "model_type": "...",
    "hyperparameters": {
        "learning_rate": 0.001,
        "batch_size": 32,
        # ...
    }
}
```

### Baseline for Comparison
- **Model**: [Baseline model type]
- **Performance**: [Expected baseline metrics]

---

## Hyperparameters

### Fixed Parameters
- Parameter 1: [Value] - [Rationale]
- Parameter 2: [Value] - [Rationale]

### Tuning Search Space
```python
hyperparameter_search_space = {
    "learning_rate": [0.001, 0.01, 0.1],
    "num_layers": [2, 3, 4],
    "hidden_size": [64, 128, 256],
    # ...
}
```

### Tuning Strategy
- **Method**: [Grid search, random search, Bayesian optimization]
- **Trials**: [Number of trials]
- **Metric to optimize**: [Metric name]

---

## Success Metrics

### Primary Metrics
1. **[Metric 1]**: Target [X], Baseline [Y]
2. **[Metric 2]**: Target [X], Baseline [Y]

### Secondary Metrics
1. **[Metric 3]**: Monitor for [reason]
2. **[Metric 4]**: Monitor for [reason]

### Business Metrics (if applicable)
- **[Business Metric 1]**: [How ML metrics translate to business value]

---

## Training Configuration

### Compute Resources
- **Platform**: Vertex AI Training
- **Machine Type**: [n1-standard-4, a2-highgpu-1g, etc.]
- **Accelerator**: [None, 1x V100, 4x T4, etc.]
- **Estimated Cost**: $[X] per run

### Training Parameters
- **Epochs**: [N]
- **Early Stopping**: [Patience, metric]
- **Checkpointing**: [Frequency, metric]
- **Logging**: [Frequency]

---

## Deployment Strategy

### Model Versioning
- **Registry**: Vertex AI Model Registry
- **Version**: [v1.0.0]
- **Model Name**: [model-name]

### Endpoint Configuration
- **Traffic Split**: [100% new model or A/B test %]
- **Instance Type**: [n1-standard-2, etc.]
- **Min/Max Replicas**: [1/10]

### Monitoring
- **Prediction Drift**: [How to detect]
- **Performance Degradation**: [Thresholds]
- **Alerting**: [Alert channels]

---

## Validation Plan

### Offline Validation
- [ ] Cross-validation on training set
- [ ] Hold-out test set evaluation
- [ ] Error analysis by segment

### Online Validation (if deploying)
- [ ] Shadow mode testing
- [ ] A/B test with [X%] traffic
- [ ] Monitor for [Y] days

### Acceptance Criteria
- **Must Have**:
  - [Metric 1] > [threshold]
  - [Metric 2] < [threshold]
- **Nice to Have**:
  - [Metric 3] > [threshold]

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data quality issues | [H/M/L] | [H/M/L] | [Validation steps] |
| Overfitting | [H/M/L] | [H/M/L] | [Regularization, validation] |
| Insufficient data | [H/M/L] | [H/M/L] | [Data augmentation, transfer learning] |
| Cost overrun | [H/M/L] | [H/M/L] | [Budget alerts, preemptible instances] |

---

## Timeline

- **Data Preparation**: [Start - End]
- **Model Development**: [Start - End]
- **Hyperparameter Tuning**: [Start - End]
- **Validation**: [Start - End]
- **Deployment** (if applicable): [Start - End]
- **Total Duration**: [X days/weeks]

---

## Reproducibility Requirements

### Environment
- **Python**: [3.10]
- **Key Libraries**: [tensorflow==2.x, scikit-learn==1.x]
- **UV Lock Hash**: [Will be captured in context.md]

### Random Seeds
- **Data Split**: [seed value]
- **Model Init**: [seed value]
- **Training**: [seed value]

### Versioning
- **Code**: Git commit hash [will be captured]
- **Data**: Dataset version/snapshot [identifier]
- **Model**: Model artifact version [identifier]

---

## Resources

- **Documentation**: [Links to relevant docs]
- **Prior Experiments**: [Links to related experiments]
- **Reference Papers**: [Academic papers, blog posts]
- **Vertex AI Experiments**: [Link to Vertex AI Experiments run]

---

## Approval

- [ ] Hypothesis clearly defined
- [ ] Success metrics identified
- [ ] Resources estimated
- [ ] Risks identified
- [ ] Timeline reasonable
- [ ] Ready to execute

**Approved by**: [Name]
**Date**: [Date]
