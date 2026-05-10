# Experiment: [Experiment Name] - Context

**Last Updated**: [Date/Time]
**Status**: [Data Prep/Training/Tuning/Validation/Deployed/Failed]
**Experiment ID**: [experiment-id]

---

## Quick Reference

### Vertex AI Experiment
```bash
# View experiment in Vertex AI
gcloud ai experiments describe [experiment-id] \
  --region=[region] \
  --project=[project-id]
```

### Key Commands
```bash
# Data preparation
uv run python scripts/prepare_data.py --config configs/[experiment].yaml

# Training
uv run python train.py --experiment-id [experiment-id]

# Evaluation
uv run python evaluate.py --model-path [path]

# Deployment
uv run python deploy.py --model-version [version]
```

---

## Current Status

### What We're Doing Now
[1-2 sentence description of current work]

### Next Steps
1. [Immediate next action]
2. [Action after that]
3. [Action after that]

### Blockers
- [Blocker 1 if any]
- [Blocker 2 if any]

---

## Dataset Context

### Data Location
- **Training**: `gs://[bucket]/[path]` or `bq://[project].[dataset].[table]`
- **Validation**: `gs://[bucket]/[path]` or `bq://[project].[dataset].[table]`
- **Test**: `gs://[bucket]/[path]` or `bq://[project].[dataset].[table]`

### Data Statistics
```
Training samples: [N]
Validation samples: [N]
Test samples: [N]
Features: [N]
Target distribution: [summary]
```

### Feature Engineering Applied
1. [Transformation 1]: [Description]
2. [Transformation 2]: [Description]
3. [Transformation 3]: [Description]

### Data Quality Issues Found
- [Issue 1]: [How handled]
- [Issue 2]: [How handled]

---

## Model Context

### Current Model Version
- **Version**: [v1.0.0]
- **Architecture**: [Description]
- **Training Run ID**: [run-id]
- **Checkpoint**: `gs://[bucket]/checkpoints/[path]`

### Hyperparameters (Current Run)
```python
hyperparameters = {
    "learning_rate": 0.001,
    "batch_size": 32,
    "num_epochs": 100,
    "early_stopping_patience": 10,
    # ... all hyperparameters
}
```

### Hyperparameter Tuning Progress
| Trial | Learning Rate | Batch Size | ... | Primary Metric | Status |
|-------|--------------|------------|-----|----------------|--------|
| 1     | 0.001        | 32         | ... | 0.85           | Complete |
| 2     | 0.01         | 64         | ... | 0.87           | Complete |
| 3     | 0.001        | 128        | ... | Running...     | In Progress |

**Best So Far**: Trial [N] with [metric]=[value]

---

## Training Progress

### Current Training Run
- **Started**: [Date/Time]
- **Status**: [Epoch X/Y]
- **Time Elapsed**: [X hours]
- **ETA**: [Y hours remaining]

### Metrics (Latest Checkpoint)
```
Training Loss: [X]
Validation Loss: [X]
Training [Metric]: [X]
Validation [Metric]: [X]
```

### Training Observations
- [Observation 1: e.g., "Loss plateaued at epoch 50"]
- [Observation 2: e.g., "Validation diverging from training"]

### Training Logs
```bash
# View logs
gcloud ai custom-jobs stream-logs [job-id] --region=[region]

# Or locally
tail -f logs/training_[timestamp].log
```

---

## Environment & Reproducibility

### UV Lock Hash
```
[Hash from uv.lock - first 12 chars for quick verification]
Full: [Full hash]
```

### Python Environment
```
Python: [3.10.x]
CUDA: [11.8] (if applicable)
Key packages:
  - tensorflow: [2.14.0]
  - scikit-learn: [1.3.0]
  - google-cloud-aiplatform: [1.38.0]
```

### Git Context
- **Branch**: [experiment/branch-name]
- **Commit**: [commit-hash]
- **Uncommitted Changes**: [Yes/No - list if yes]

### Random Seeds Used
```python
DATA_SEED = [42]
MODEL_SEED = [42]
TRAINING_SEED = [42]
```

---

## Compute Resources

### Current Training Job
- **Platform**: Vertex AI Custom Training
- **Machine Type**: [n1-standard-8]
- **Accelerators**: [1x NVIDIA_TESLA_V100]
- **Region**: [us-central1]
- **Job ID**: [job-id]

### Resource Utilization
- **GPU Utilization**: [~85%]
- **Memory Usage**: [45 GB / 60 GB]
- **Cost So Far**: $[X.XX]
- **Estimated Total**: $[Y.YY]

---

## Files Modified

### Code
- `src/data/preprocessing.py` - [Changes made]
- `src/models/model.py` - [Changes made]
- `src/training/trainer.py` - [Changes made]
- `configs/experiment_config.yaml` - [Changes made]

### Notebooks
- `notebooks/data_exploration.ipynb` - [What was explored]
- `notebooks/model_analysis.ipynb` - [What was analyzed]

### Tests
- `tests/test_preprocessing.py` - [Tests added]
- `tests/test_model.py` - [Tests added]

---

## Intermediate Results

### Validation Performance (Latest)
```
Metric 1: [X] (target: [Y])
Metric 2: [X] (target: [Y])
Baseline comparison: [+X% improvement]
```

### Error Analysis
- **Common Failure Cases**:
  1. [Pattern 1]: [% of errors]
  2. [Pattern 2]: [% of errors]

- **Insights**:
  - [Insight 1]
  - [Insight 2]

---

## Decisions Made During Execution

### Decision 1: [Date]
**What**: [e.g., "Increased batch size from 32 to 64"]
**Why**: [e.g., "Training was taking too long, GPU underutilized"]
**Impact**: [e.g., "2x speedup, slight memory increase"]

### Decision 2: [Date]
**What**: [Decision description]
**Why**: [Rationale]
**Impact**: [Consequences]

---

## Issues Encountered

### Issue 1: [Title]
- **Discovered**: [Date/Time]
- **Symptom**: [What happened]
- **Root Cause**: [Why it happened]
- **Resolution**: [How fixed]
- **Time Impact**: [+X hours]

### Issue 2: [Title]
[Same structure]

---

## Vertex AI Experiments Integration

### Experiment Metadata
```python
# Logged to Vertex AI Experiments
aiplatform.init(
    experiment="[experiment-name]",
    experiment_tensorboard="[tensorboard-resource-name]"
)

aiplatform.start_run(run="[run-name]")
```

### Metrics Logged
- [Metric 1]: Logged every [N] steps
- [Metric 2]: Logged every [N] steps
- [Metric 3]: Logged at end of epoch

### Artifacts Saved
- Model checkpoints: `gs://[bucket]/experiments/[id]/checkpoints/`
- Training logs: `gs://[bucket]/experiments/[id]/logs/`
- Visualizations: `gs://[bucket]/experiments/[id]/viz/`

---

## Next Agent Handoff

### Current Agent Output
**Agent**: [agent-name]
**Completed**: [Date/Time]
**Work Done**: [Summary]
**Metrics Achieved**: [List]

### Next Agent
**Agent**: [next-agent-name or "developer"]
**Task**: [What to do next]
**Inputs Required**:
- Model checkpoint: [path]
- Validation results: [path]
- [Other inputs]

---

## Links & Resources

- Plan: experiment-[name]-plan.md
- Tasks: experiment-[name]-tasks.md
- Results: experiment-[name]-results.md
- Vertex AI Experiment: [URL]
- TensorBoard: [URL]
- Model Registry: [URL]
- Training Logs: [GCS path]
