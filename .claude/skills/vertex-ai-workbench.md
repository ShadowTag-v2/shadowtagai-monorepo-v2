# Vertex AI Workbench Guidelines for PNKLN

**Version**: 1.0.0
**Auto-activates**: When working with Vertex AI, ML models, training jobs, or deployment
**Scope**: Google Cloud Vertex AI integration patterns for PNKLN Core Stack

---

## Quick Reference

### Essential Commands
```bash
# Initialize Vertex AI
gcloud auth application-default login
gcloud config set project [PROJECT_ID]

# List models
gcloud ai models list --region=us-central1

# List endpoints
gcloud ai endpoints list --region=us-central1

# View training job
gcloud ai custom-jobs describe [JOB_ID] --region=us-central1

# Stream training logs
gcloud ai custom-jobs stream-logs [JOB_ID] --region=us-central1
```

### Python SDK Basics
```python
from google.cloud import aiplatform

aiplatform.init(
    project="your-project-id",
    location="us-central1",
    experiment="experiment-name"  # Optional: for experiment tracking
)
```

---

## Core Principles

### 1. Always Use Vertex AI Experiments
Every training run should be logged to Vertex AI Experiments for reproducibility and comparison.

```python
# ✅ Good - tracked experiment
from google.cloud import aiplatform

aiplatform.init(
    project="pnkln-project",
    location="us-central1",
    experiment="fraud-detection-v1"
)

aiplatform.start_run(run="run-2024-01-15-001")

# Log parameters
aiplatform.log_params({
    "learning_rate": 0.001,
    "batch_size": 32,
    "model_type": "xgboost"
})

# Train model
model = train_model()

# Log metrics
aiplatform.log_metrics({
    "accuracy": 0.95,
    "precision": 0.93,
    "recall": 0.92
})

aiplatform.end_run()

# ❌ Bad - no experiment tracking
model = train_model()  # Where did this come from? What hyperparameters?
```

### 2. Custom Training Jobs for Reproducibility
Use Custom Training Jobs instead of local training for production ML.

```python
from google.cloud import aiplatform

job = aiplatform.CustomTrainingJob(
    display_name="fraud-detection-training",
    script_path="src/training/train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-13:latest",
    requirements=["xgboost==2.0.0", "scikit-learn==1.3.0"],
    model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-7:latest"
)

model = job.run(
    dataset=dataset,
    replica_count=1,
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    model_display_name="fraud-detection-v1",
    args=[
        f"--learning-rate={0.001}",
        f"--batch-size={32}",
    ]
)
```

### 3. Model Registry for Versioning
All trained models must be uploaded to Vertex AI Model Registry with proper versioning.

```python
# ✅ Good - versioned in registry
model = aiplatform.Model.upload(
    display_name="fraud-detection",
    artifact_uri="gs://pnkln-models/fraud-detection/v1.0.0/",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-7:latest",
    description="Fraud detection model trained on 2024-01 data",
    version_aliases=["production", "v1"],
    version_description="Initial production model"
)

# ❌ Bad - model not in registry
# model.pkl saved locally or in random GCS bucket
```

---

## Data Preparation Patterns

See [data-prep.md](resources/vertex-ai-workbench/data-prep.md) for comprehensive data preparation patterns.

### BigQuery to Dataset
```python
from google.cloud import aiplatform

# Create managed dataset from BigQuery
dataset = aiplatform.TabularDataset.create(
    display_name="fraud-transactions",
    bq_source="bq://pnkln-project.datasets.transactions",
    labels={"env": "production", "version": "v1"}
)
```

### Cloud Storage to Dataset
```python
dataset = aiplatform.TabularDataset.create(
    display_name="fraud-transactions",
    gcs_source=["gs://pnkln-data/training/transactions_*.csv"]
)
```

### Data Splitting
```python
# Use Vertex AI Data Labeling for splits
from google.cloud.aiplatform import datasets

training_filter = f'split="training"'
validation_filter = f'split="validation"'
test_filter = f'split="test"'

# Or specify fractions
training_fraction_split = 0.7
validation_fraction_split = 0.15
test_fraction_split = 0.15
```

---

## Model Training Patterns

See [model-training.md](resources/vertex-ai-workbench/model-training.md) for detailed training patterns.

### AutoML Training
```python
from google.cloud import aiplatform

# AutoML Tabular
job = aiplatform.AutoMLTabularTrainingJob(
    display_name="fraud-detection-automl",
    optimization_prediction_type="classification",
    optimization_objective="maximize-au-prc",
    column_specs={
        "amount": "numeric",
        "merchant_category": "categorical",
        "is_fraud": "categorical"
    }
)

model = job.run(
    dataset=dataset,
    target_column="is_fraud",
    training_fraction_split=0.7,
    validation_fraction_split=0.15,
    test_fraction_split=0.15,
    budget_milli_node_hours=1000,
    model_display_name="fraud-detection-automl-v1"
)
```

### Custom Training with Hyperparameter Tuning
```python
from google.cloud.aiplatform import hyperparameter_tuning as hpt

# Define hyperparameter search space
custom_job = aiplatform.CustomJob.from_local_script(
    display_name="fraud-detection-hpt",
    script_path="src/training/train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/xgboost-cpu.1-7:latest"
)

hpt_job = aiplatform.HyperparameterTuningJob(
    display_name="fraud-detection-hpt",
    custom_job=custom_job,
    metric_spec={"auc": "maximize"},
    parameter_spec={
        "learning_rate": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
        "max_depth": hpt.IntegerParameterSpec(min=3, max=10, scale="linear"),
        "n_estimators": hpt.DiscreteParameterSpec(values=[100, 200, 500], scale="linear")
    },
    max_trial_count=20,
    parallel_trial_count=5
)

hpt_job.run()

# Get best trial
best_trial = hpt_job.trials[0]  # Sorted by metric
best_params = best_trial.parameters
```

---

## Model Deployment Patterns

See [deployment.md](resources/vertex-ai-workbench/deployment.md) for comprehensive deployment strategies.

### Create Endpoint
```python
endpoint = aiplatform.Endpoint.create(
    display_name="fraud-detection-endpoint",
    description="Production fraud detection endpoint",
    labels={"env": "production"}
)
```

### Deploy Model to Endpoint
```python
model.deploy(
    endpoint=endpoint,
    deployed_model_display_name="fraud-detection-v1",
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=10,
    traffic_split={"0": 100},  # 100% traffic to this model
    accelerator_type="NVIDIA_TESLA_T4",  # Optional GPU
    accelerator_count=1
)
```

### A/B Testing Deployment
```python
# Deploy new model version with traffic split
new_model.deploy(
    endpoint=endpoint,
    deployed_model_display_name="fraud-detection-v2",
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=10,
    traffic_split={
        "model-v1-id": 90,  # 90% to existing model
        "model-v2-id": 10   # 10% to new model (canary)
    }
)
```

---

## Prediction Patterns

### Online Prediction (Real-time)
```python
# Single prediction
prediction = endpoint.predict(instances=[{
    "amount": 150.00,
    "merchant_category": "online_retail",
    "transaction_time": "2024-01-15T10:30:00Z"
}])

print(f"Fraud probability: {prediction.predictions[0][1]}")

# Batch prediction (sync, for small batches)
predictions = endpoint.predict(instances=[
    {"amount": 150.00, "merchant_category": "online_retail"},
    {"amount": 2500.00, "merchant_category": "electronics"},
    # ... up to ~100 instances
])
```

### Batch Prediction (Asynchronous)
```python
from google.cloud import aiplatform

batch_prediction_job = model.batch_predict(
    job_display_name="fraud-detection-batch",
    gcs_source=["gs://pnkln-data/prediction/input/*.jsonl"],
    gcs_destination_prefix="gs://pnkln-data/prediction/output/",
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    instances_format="jsonl",
    predictions_format="jsonl"
)

# Wait for completion (or check async)
batch_prediction_job.wait()

# Get output location
output_location = batch_prediction_job.output_info.gcs_output_directory
```

---

## Monitoring & Logging

### Model Monitoring
```python
from google.cloud.aiplatform import model_monitoring

# Create monitoring job
monitoring_job = aiplatform.ModelDeploymentMonitoringJob.create(
    display_name="fraud-detection-monitoring",
    endpoint=endpoint,
    logging_sampling_strategy=model_monitoring.RandomSampleConfig(sample_rate=0.5),
    schedule_config=model_monitoring.ScheduleConfig(monitor_interval=3600),  # hourly
    alert_config=model_monitoring.EmailAlertConfig(
        user_emails=["team@pnkln.com"]
    ),
    objective_configs=[
        model_monitoring.ObjectiveConfig(
            training_dataset=dataset,
            training_prediction_skew_detection_config=model_monitoring.SkewDetectionConfig(
                data_drift_thresholds={
                    "amount": 0.1,
                    "merchant_category": 0.1
                },
                default_skew_threshold=0.05
            ),
            prediction_drift_detection_config=model_monitoring.DriftDetectionConfig(
                drift_thresholds={
                    "amount": 0.1
                },
                default_drift_threshold=0.05
            )
        )
    ]
)
```

### Explanation AI
```python
# Enable explanations on deployment
model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-4",
    explanation_metadata=aiplatform.explain.ExplanationMetadata(
        inputs={
            "amount": {"input_tensor_name": "amount"},
            "merchant_category": {"input_tensor_name": "merchant_category"}
        },
        outputs={"is_fraud": {"output_tensor_name": "is_fraud"}}
    ),
    explanation_parameters=aiplatform.explain.ExplanationParameters(
        {"sampled_shapley_attribution": {"path_count": 10}}
    )
)

# Get predictions with explanations
response = endpoint.explain(instances=[{
    "amount": 150.00,
    "merchant_category": "online_retail"
}])

prediction = response.predictions[0]
explanation = response.explanations[0]
attributions = explanation.attributions[0].feature_attributions
```

---

## Cost Optimization

### Use Preemptible Instances for Training
```python
# Save 60-91% on training costs
job = aiplatform.CustomTrainingJob(
    display_name="fraud-detection-training",
    script_path="src/training/train.py",
    container_uri="us-docker.pkg.dev/vertex-ai/training/xgboost-cpu.1-7:latest"
)

model = job.run(
    replica_count=1,
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    reduction_server_count=0,
    reduction_server_machine_type=None,
    base_output_dir="gs://pnkln-models/checkpoints",
    enable_web_access=False,
    # Cost savings
    boot_disk_type="pd-standard",  # vs pd-ssd
    boot_disk_size_gb=100,
    service_account=None,
    restart_job_on_worker_restart=True  # Handle preemption
)
```

### Auto-scaling for Endpoints
```python
model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-2",  # Smaller instance
    min_replica_count=1,  # Scale down when idle
    max_replica_count=10,  # Scale up under load
    autoscaling_target_cpu_utilization=60,
    autoscaling_target_accelerator_duty_cycle=None
)
```

---

## Integration with FastAPI

### Prediction Endpoint
```python
# src/routes/predictions.py
from fastapi import APIRouter, HTTPException
from google.cloud import aiplatform
from src.schemas.prediction import PredictionRequest, PredictionResponse
from src.config import get_settings

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])

settings = get_settings()

# Initialize Vertex AI
aiplatform.init(
    project=settings.google_cloud_project,
    location=settings.vertex_ai_location
)

@router.post("/fraud", response_model=PredictionResponse)
async def predict_fraud(request: PredictionRequest) -> PredictionResponse:
    """
    Predict fraud probability for a transaction.

    Args:
        request: Transaction data

    Returns:
        Fraud probability and explanation

    Raises:
        HTTPException: 500 on prediction error
    """
    try:
        endpoint = aiplatform.Endpoint(
            endpoint_name=settings.fraud_detection_endpoint_id
        )

        instances = [{
            "amount": request.amount,
            "merchant_category": request.merchant_category,
            "transaction_time": request.transaction_time.isoformat()
        }]

        prediction = endpoint.predict(instances=instances)

        return PredictionResponse(
            fraud_probability=prediction.predictions[0][1],
            is_fraud=prediction.predictions[0][1] > 0.5,
            model_version=endpoint.traffic_split
        )

    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=500,
            detail="Prediction service unavailable"
        )
```

---

## Progressive Disclosure Resources

For detailed guidance on specific topics, see:

- **[data-prep.md](resources/vertex-ai-workbench/data-prep.md)** - Data ingestion, preprocessing, feature engineering
- **[model-training.md](resources/vertex-ai-workbench/model-training.md)** - Custom training, AutoML, hyperparameter tuning
- **[deployment.md](resources/vertex-ai-workbench/deployment.md)** - Endpoint management, A/B testing, canary deployments
- **[monitoring.md](resources/vertex-ai-workbench/monitoring.md)** - Model monitoring, drift detection, alerts
- **[pipelines.md](resources/vertex-ai-workbench/pipelines.md)** - Vertex AI Pipelines for MLOps automation

---

## Common Pitfalls

### 1. Not Using Managed Datasets
```python
# ❌ Bad - manual data handling
df = pd.read_csv("gs://bucket/data.csv")
train_df, val_df = train_test_split(df)

# ✅ Good - Vertex AI managed dataset
dataset = aiplatform.TabularDataset.create(
    display_name="fraud-data",
    gcs_source=["gs://bucket/data.csv"]
)
```

### 2. Hardcoding Endpoint IDs
```python
# ❌ Bad - hardcoded endpoint
endpoint = aiplatform.Endpoint("1234567890")

# ✅ Good - from configuration
from src.config import get_settings
settings = get_settings()
endpoint = aiplatform.Endpoint(settings.fraud_detection_endpoint_id)
```

### 3. No Error Handling for Predictions
```python
# ❌ Bad - no error handling
prediction = endpoint.predict(instances=[data])

# ✅ Good - proper error handling
try:
    prediction = endpoint.predict(instances=[data])
except Exception as e:
    logger.error(f"Prediction failed: {e}")
    # Fallback logic or raise HTTPException
```

---

## Quality Checklist

Before deploying ML models, verify:

- [ ] Model logged to Vertex AI Experiments
- [ ] Hyperparameters tracked and versioned
- [ ] Model uploaded to Model Registry
- [ ] Endpoint configured with auto-scaling
- [ ] Monitoring enabled (drift detection)
- [ ] A/B testing strategy defined
- [ ] Cost optimization (preemptible instances, right-sized machines)
- [ ] Integration tests for prediction endpoint
- [ ] Error handling and fallback logic
- [ ] Explanation AI enabled (if required)

---

**Related Skills**: ml-experiment-tracking, bigquery-integration, python-dev-guidelines
**Hooks**: This skill auto-activates when working with Vertex AI, ML training, or deployment keywords.
**Scripts**: See `.claude/scripts/vertex-ai-deploy.py` for automated deployment script.
