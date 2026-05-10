# Training Dashboard Skill

Rich terminal UI for GPU cluster job management.

## Pattern

@ramith__: Cluster-agnostic prototyping → production submission.

## Usage

```python
from dashboards import TrainingDashboard

dashboard = TrainingDashboard()

# Submit jobs

dashboard.submit_job("gemini-finetune", "gemini-3", gpus=4, epochs=20)
dashboard.submit_job("llama-train", "llama-3", gpus=8, epochs=50)

# Run live dashboard (4 Hz refresh)

await dashboard.run()

```

## CLI

```bash
python -m dashboards.training_dashboard

```

## Features

### GPU Cluster Monitoring


- Real-time availability (4 Hz refresh)

- Queue depth tracking

- Cost per hour display

- Multi-cluster support

### Default Clusters

| Cluster | GPU | Total | $/hr |
|---------|-----|-------|------|
| gke-h100-pool | H100 | 16 | $3.22 |
| gke-a100-pool | A100 | 8 | $2.93 |
| gke-l4-pool | L4 | 16 | $0.81 |
| gke-t4-pool | T4 | 8 | $0.35 |

### Job Management


- Submit training jobs

- Auto-cluster selection

- Progress tracking with loss metrics

- Cancel running jobs

### Job States

```

PENDING → QUEUED → RUNNING → COMPLETED
                          ↘ FAILED
                          ↘ CANCELLED

```

## Dashboard Layout

```

┌─────────────────────────────────────────────────────────────┐
│ TRAINING JOB DASHBOARD | Gemini 3 Pro + Claude Code | HH:MM │
├──────────────┬─────────────────────────┬────────────────────┤
│ GPU Clusters │     Training Jobs       │     Metrics        │
│              │                         │                    │
│ Cluster GPU  │ Job    Status Progress  │ SUMMARY            │
│ h100    8/16 │ gemini RUNNING ████░ 40%│ Total: 4           │
│ a100    4/8  │ llama  QUEUED  ░░░░░  0%│ Running: 1         │
│ l4     12/16 │ custom PENDING          │ Completed: 2       │
│ t4      8/8  │                         │ GPU Hours: 12.5h   │
│              │                         │ Est. Cost: $38.50  │
├──────────────┴─────────────────────────┴────────────────────┤
│ [q] Quit  [s] Submit Job  [c] Cancel  [r] Refresh           │
└─────────────────────────────────────────────────────────────┘

```

## API

```python

# Submit a job

job = dashboard.submit_job(
    name="my-training",
    model_type="gemini-3",  # gemini-3, llama-3, custom
    gpus=4,
    epochs=20,
    cluster="gke-h100-pool"  # Optional, auto-selects if omitted
)

# Cancel a job

dashboard.cancel_job(job.job_id)

# Access metrics

metrics = dashboard.metrics
print(f"Total GPU hours: {metrics.total_gpu_hours}")
print(f"Estimated cost: ${metrics.estimated_cost:.2f}")

```

## Files


- `dashboards/training_dashboard.py` - Dashboard implementation

- `dashboards/__init__.py` - Module exports

## Integration

Works with:

- Rich library for terminal UI

- Async event loop for real-time updates

- GKE cluster APIs (production)
