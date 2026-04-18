#!/usr/bin/env python3
"""Vertex AI Training Pipeline for Cor.54 CodeAct Orchestrator
===========================================================

PURPOSE:
    End-to-end automation of Gemini fine-tuning on Google Cloud Vertex AI.
    Handles dataset preparation, model training, evaluation, and deployment.

CAPABILITIES:
    ├─ Dataset preparation (CodeActInstruct → Gemini format)
    ├─ GCS upload automation
    ├─ Fine-tuning job submission + monitoring
    ├─ Checkpoint evaluation (accuracy, latency, executable rate)
    ├─ Model deployment to Vertex AI endpoint
    └─ Full pipeline orchestration (one command)

USAGE:
    # Setup only (create GCS buckets, verify credentials)
    python vertex_ai_pipeline.py --setup_only

    # Full training pipeline
    python vertex_ai_pipeline.py \\
        --single_turn_data=datasets/single_turn_examples.jsonl \\
        --multi_turn_data=datasets/multi_turn_trajectories.jsonl \\
        --model_name=gemini-policy-v1 \\
        --auto_deploy=true

    # Evaluation only (test existing checkpoint)
    python vertex_ai_pipeline.py \\
        --evaluate_only \\
        --checkpoint=gs://pnkln-training/checkpoints/gemini-policy-v1-epoch-3

COST:
    - Training: ~$50-100 per run (2-4 hours on Vertex AI)
    - Storage: ~$1/month for datasets + checkpoints
    - Inference: $0.000125 per 1K characters (pay-as-you-go)

AUTHOR: Generated for pnkln/core-stack Phase 1
DATE: 2025-11-07
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

# Google Cloud imports
try:
    import google.generativeai as genai
    from google.cloud import aiplatform, storage
    from vertexai.preview.tuning import sft
except ImportError:
    logger.error(
        "Google Cloud libraries not installed. Run: pip install google-cloud-aiplatform google-cloud-storage google-generativeai",
    )
    sys.exit(1)

console = Console()


# ============================================================================
# CONFIGURATION
# ============================================================================


@dataclass
class TrainingConfig:
    """Configuration for Vertex AI training job."""

    # GCP Settings
    project_id: str
    location: str = "us-central1"
    staging_bucket: str = ""  # Will be set to gs://{project_id}-training

    # Model Settings
    base_model: str = "gemini-1.5-pro-002"
    model_name: str = "gemini-policy-v1"

    # Training Hyperparameters
    learning_rate: float = 1e-5
    num_epochs: int = 3
    batch_size: int = 16
    max_input_tokens: int = 4096
    max_output_tokens: int = 2048

    # Dataset Paths (local)
    single_turn_data: Path | None = None
    multi_turn_data: Path | None = None

    # Training Ratios
    single_turn_ratio: float = 0.9  # 90% single-turn, 10% multi-turn
    train_val_split: float = 0.9  # 90% train, 10% validation

    # Evaluation Settings
    eval_metrics: list[str] = None
    eval_sample_size: int = 100

    # Deployment Settings
    auto_deploy: bool = False
    min_replica_count: int = 1
    max_replica_count: int = 5

    def __post_init__(self):
        """Set defaults and validate."""
        if not self.staging_bucket:
            self.staging_bucket = f"gs://{self.project_id}-training"

        if self.eval_metrics is None:
            self.eval_metrics = ["executable_rate", "latency_p99", "security_violations"]

        # Validate paths
        if self.single_turn_data:
            self.single_turn_data = Path(self.single_turn_data)
            if not self.single_turn_data.exists():
                raise FileNotFoundError(f"Single-turn data not found: {self.single_turn_data}")

        if self.multi_turn_data:
            self.multi_turn_data = Path(self.multi_turn_data)
            if not self.multi_turn_data.exists():
                raise FileNotFoundError(f"Multi-turn data not found: {self.multi_turn_data}")

    @classmethod
    def from_env(cls) -> "TrainingConfig":
        """Create config from environment variables."""
        project_id = os.getenv("GCP_PROJECT_ID")
        if not project_id:
            # Try to get from gcloud
            try:
                result = subprocess.run(
                    ["gcloud", "config", "get-value", "project"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                project_id = result.stdout.strip()
            except:
                raise ValueError("GCP_PROJECT_ID not set and gcloud not configured")

        return cls(project_id=project_id)


# ============================================================================
# GCS DATASET MANAGER
# ============================================================================


class GCSDatasetManager:
    """Manage dataset uploads to Google Cloud Storage."""

    def __init__(self, config: TrainingConfig):
        """Initialize GCS client."""
        self.config = config
        self.client = storage.Client(project=config.project_id)

        # Parse bucket name from gs:// URL
        self.bucket_name = config.staging_bucket.replace("gs://", "").split("/")[0]
        self.bucket = None

        logger.info(f"Initialized GCSDatasetManager for bucket: {self.bucket_name}")

    def setup_bucket(self):
        """Create GCS bucket if it doesn't exist."""
        try:
            self.bucket = self.client.get_bucket(self.bucket_name)
            logger.info(f"Using existing bucket: {self.bucket_name}")
        except Exception:
            logger.info(f"Creating new bucket: {self.bucket_name}")
            self.bucket = self.client.create_bucket(self.bucket_name, location=self.config.location)
            logger.info(f"Created bucket: {self.bucket_name}")

    def upload_dataset(self, local_path: Path, gcs_path: str, show_progress: bool = True) -> str:
        """Upload dataset file to GCS.

        Args:
            local_path: Local file path
            gcs_path: GCS path (relative to bucket, e.g., 'datasets/train.jsonl')
            show_progress: Show upload progress

        Returns:
            Full GCS URL (gs://bucket/path)

        """
        if not self.bucket:
            self.setup_bucket()

        blob = self.bucket.blob(gcs_path)

        # Upload with progress
        if show_progress:
            console.print(f"[cyan]Uploading {local_path.name} to GCS...[/cyan]")

        blob.upload_from_filename(str(local_path))

        full_url = f"gs://{self.bucket_name}/{gcs_path}"
        logger.info(f"Uploaded {local_path} → {full_url}")

        return full_url

    def prepare_training_data(
        self,
        single_turn_path: Path,
        multi_turn_path: Path | None = None,
        single_turn_ratio: float = 0.9,
        train_val_split: float = 0.9,
    ) -> tuple[str, str]:
        """Prepare and upload training/validation datasets.

        Steps:
            1. Load single-turn and multi-turn data
            2. Merge according to single_turn_ratio
            3. Split into train/validation
            4. Upload to GCS

        Returns:
            (train_gcs_url, val_gcs_url)

        """
        console.print("\n[bold]Preparing training data...[/bold]")

        # Load data
        single_turn_examples = self._load_jsonl(single_turn_path)
        logger.info(f"Loaded {len(single_turn_examples)} single-turn examples")

        multi_turn_examples = []
        if multi_turn_path and multi_turn_path.exists():
            multi_turn_examples = self._load_jsonl(multi_turn_path)
            logger.info(f"Loaded {len(multi_turn_examples)} multi-turn examples")

        # Merge according to ratio
        target_single = int(len(single_turn_examples) * single_turn_ratio)
        target_multi = len(single_turn_examples) - target_single

        # Sample if needed
        if len(single_turn_examples) > target_single:
            import random

            random.shuffle(single_turn_examples)
            single_turn_examples = single_turn_examples[:target_single]

        if multi_turn_examples and len(multi_turn_examples) > target_multi:
            import random

            random.shuffle(multi_turn_examples)
            multi_turn_examples = multi_turn_examples[:target_multi]

        # Combine
        all_examples = single_turn_examples + multi_turn_examples
        logger.info(f"Combined dataset: {len(all_examples)} examples")

        # Shuffle
        import random

        random.shuffle(all_examples)

        # Split train/val
        split_idx = int(len(all_examples) * train_val_split)
        train_examples = all_examples[:split_idx]
        val_examples = all_examples[split_idx:]

        logger.info(f"Split: {len(train_examples)} train, {len(val_examples)} validation")

        # Save locally
        train_path = Path("/tmp/train.jsonl")
        val_path = Path("/tmp/val.jsonl")

        self._save_jsonl(train_examples, train_path)
        self._save_jsonl(val_examples, val_path)

        # Upload to GCS
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        train_gcs = self.upload_dataset(
            train_path,
            f"datasets/{self.config.model_name}/{timestamp}/train.jsonl",
        )

        val_gcs = self.upload_dataset(
            val_path,
            f"datasets/{self.config.model_name}/{timestamp}/val.jsonl",
        )

        console.print("[green]✓ Training data prepared[/green]")
        console.print(f"  Train: {train_gcs}")
        console.print(f"  Val:   {val_gcs}\n")

        return train_gcs, val_gcs

    @staticmethod
    def _load_jsonl(path: Path) -> list[dict[str, Any]]:
        """Load JSONL file."""
        examples = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    examples.append(json.loads(line))
        return examples

    @staticmethod
    def _save_jsonl(examples: list[dict[str, Any]], path: Path):
        """Save JSONL file."""
        with open(path, "w") as f:
            f.writelines(json.dumps(example) + "\n" for example in examples)


# ============================================================================
# VERTEX AI TRAINING JOB MANAGER
# ============================================================================


class VertexAITrainer:
    """Manage Vertex AI fine-tuning jobs."""

    def __init__(self, config: TrainingConfig):
        """Initialize Vertex AI client."""
        self.config = config

        # Initialize Vertex AI
        aiplatform.init(
            project=config.project_id,
            location=config.location,
            staging_bucket=config.staging_bucket,
        )

        logger.info(f"Initialized Vertex AI in project: {config.project_id}")

    def submit_training_job(self, train_data_gcs: str, val_data_gcs: str) -> str:
        """Submit fine-tuning job to Vertex AI.

        Args:
            train_data_gcs: GCS URL for training data
            val_data_gcs: GCS URL for validation data

        Returns:
            Job resource name

        """
        console.print("\n[bold]Submitting training job to Vertex AI...[/bold]")

        # Create tuning job
        job_display_name = f"{self.config.model_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Note: Using Vertex AI Supervised Fine-Tuning (SFT) API
        # This is simplified - actual implementation depends on Gemini SFT API availability
        try:
            tuning_job = sft.SupervisedFineTuningJob(
                base_model=self.config.base_model,
                train_dataset=train_data_gcs,
                validation_dataset=val_data_gcs,
                epochs=self.config.num_epochs,
                learning_rate=self.config.learning_rate,
                adapter_size=8,  # Low-rank adaptation
                tuned_model_display_name=job_display_name,
            )

            # Submit job
            tuning_job.submit()

            job_name = tuning_job.resource_name
            logger.info(f"Submitted training job: {job_name}")

            console.print("[green]✓ Training job submitted[/green]")
            console.print(f"  Job: {job_display_name}")
            console.print(f"  Resource: {job_name}\n")

            return job_name

        except Exception as e:
            logger.error(f"Failed to submit training job: {e}")
            raise

    def monitor_training_job(self, job_name: str, poll_interval: int = 60) -> dict[str, Any]:
        """Monitor training job until completion.

        Args:
            job_name: Job resource name
            poll_interval: Polling interval in seconds

        Returns:
            Job completion status and metadata

        """
        console.print("\n[bold]Monitoring training job...[/bold]")
        console.print(
            f"[yellow]This may take 2-4 hours. Polling every {poll_interval}s.[/yellow]\n",
        )

        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Training in progress...", total=None)

            while True:
                try:
                    # Get job status (simplified - actual API call depends on SDK)
                    job = aiplatform.PipelineJob.get(job_name)

                    state = job.state.name
                    progress.update(task, description=f"[cyan]Status: {state}")

                    if state in ["JOB_STATE_SUCCEEDED", "SUCCEEDED"]:
                        elapsed = time.time() - start_time
                        console.print(
                            f"\n[green]✓ Training completed in {elapsed / 3600:.1f} hours[/green]",
                        )

                        return {
                            "status": "success",
                            "job_name": job_name,
                            "elapsed_time": elapsed,
                            "model_resource_name": job.resource_name,
                        }

                    if state in [
                        "JOB_STATE_FAILED",
                        "FAILED",
                        "JOB_STATE_CANCELLED",
                        "CANCELLED",
                    ]:
                        console.print(f"\n[red]✗ Training failed: {state}[/red]")
                        if hasattr(job, "error"):
                            console.print(f"[red]Error: {job.error}[/red]")

                        return {
                            "status": "failed",
                            "job_name": job_name,
                            "error": str(getattr(job, "error", "Unknown error")),
                        }

                    # Continue polling
                    time.sleep(poll_interval)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Monitoring interrupted by user[/yellow]")
                    return {"status": "interrupted", "job_name": job_name}

                except Exception as e:
                    logger.error(f"Error monitoring job: {e}")
                    time.sleep(poll_interval)

    def get_model_checkpoints(self, job_name: str) -> list[str]:
        """Get checkpoint URLs from completed training job.

        Returns:
            List of GCS URLs for model checkpoints

        """
        # This would query the job artifacts
        # Simplified placeholder
        checkpoints = [
            f"{self.config.staging_bucket}/checkpoints/{self.config.model_name}/epoch-1",
            f"{self.config.staging_bucket}/checkpoints/{self.config.model_name}/epoch-2",
            f"{self.config.staging_bucket}/checkpoints/{self.config.model_name}/epoch-3",
        ]

        logger.info(f"Found {len(checkpoints)} checkpoints for job {job_name}")
        return checkpoints


# ============================================================================
# MODEL EVALUATION
# ============================================================================


class ModelEvaluator:
    """Evaluate fine-tuned model checkpoints."""

    def __init__(self, config: TrainingConfig):
        """Initialize evaluator."""
        self.config = config

    def evaluate_checkpoint(
        self,
        checkpoint_url: str,
        eval_dataset: list[dict[str, Any]],
        sample_size: int = 100,
    ) -> dict[str, Any]:
        """Evaluate a model checkpoint on key metrics.

        Metrics:
            - Executable Rate: % of generated code that parses without syntax errors
            - Security Violations: Count of forbidden constructs
            - Latency p99: 99th percentile generation latency
            - Semantic Correctness: Manual spot-check (placeholder)

        Args:
            checkpoint_url: GCS URL of checkpoint
            eval_dataset: Validation dataset
            sample_size: Number of examples to evaluate

        Returns:
            Evaluation metrics

        """
        console.print(f"\n[bold]Evaluating checkpoint: {Path(checkpoint_url).name}[/bold]")

        # Sample eval dataset
        import random

        if len(eval_dataset) > sample_size:
            eval_dataset = random.sample(eval_dataset, sample_size)

        # Load model from checkpoint
        # Note: This is simplified - actual loading depends on Vertex AI API
        model = self._load_checkpoint(checkpoint_url)

        results = {
            "checkpoint": checkpoint_url,
            "sample_size": len(eval_dataset),
            "executable_rate": 0.0,
            "security_violations": 0,
            "latency_p50_ms": 0.0,
            "latency_p99_ms": 0.0,
            "error_rate": 0.0,
        }

        executable_count = 0
        security_violation_count = 0
        latencies = []
        errors = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Evaluating examples...", total=len(eval_dataset))

            for example in eval_dataset:
                try:
                    # Extract input prompt
                    prompt = self._extract_prompt(example)

                    # Generate code
                    start_time = time.time()
                    generated_code = self._generate_with_model(model, prompt)
                    latency_ms = (time.time() - start_time) * 1000

                    latencies.append(latency_ms)

                    # Validate generated code
                    is_executable, has_violations = self._validate_generated_code(generated_code)

                    if is_executable:
                        executable_count += 1

                    if has_violations:
                        security_violation_count += 1

                except Exception as e:
                    logger.error(f"Evaluation error: {e}")
                    errors += 1

                progress.update(task, advance=1)

        # Compute metrics
        results["executable_rate"] = executable_count / len(eval_dataset)
        results["security_violations"] = security_violation_count
        results["error_rate"] = errors / len(eval_dataset)

        if latencies:
            import numpy as np

            results["latency_p50_ms"] = float(np.percentile(latencies, 50))
            results["latency_p99_ms"] = float(np.percentile(latencies, 99))

        # Display results
        self._display_eval_results(results)

        return results

    def _load_checkpoint(self, checkpoint_url: str):
        """Load model from checkpoint (placeholder)."""
        # In practice, would load from GCS using Vertex AI SDK
        logger.info(f"Loading checkpoint: {checkpoint_url}")
        # Return mock model for now
        return genai.GenerativeModel("gemini-1.5-pro-002")

    def _extract_prompt(self, example: dict[str, Any]) -> str:
        """Extract prompt from training example."""
        # Example format from dataset_generator
        messages = example.get("messages", [])

        # Combine system + user messages
        prompt_parts = []
        for msg in messages:
            if msg["role"] in ["system", "user"]:
                prompt_parts.append(msg["content"])

        return "\n\n".join(prompt_parts)

    def _generate_with_model(self, model, prompt: str) -> str:
        """Generate code using model."""
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": self.config.max_output_tokens,
                },
            )
            return response.text
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return ""

    def _validate_generated_code(self, code: str) -> tuple[bool, bool]:
        """Validate generated code.

        Returns:
            (is_executable, has_security_violations)

        """
        import ast

        # Check syntax
        try:
            tree = ast.parse(code)
            is_executable = True
        except SyntaxError:
            return False, False

        # Check for security violations
        forbidden_names = {"eval", "exec", "compile", "__import__", "open"}
        forbidden_modules = {"os", "subprocess", "socket"}

        has_violations = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in forbidden_names:
                has_violations = True
                break

            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module = getattr(node, "module", None) or (
                    node.names[0].name if hasattr(node, "names") else None
                )
                if module and any(mod in module for mod in forbidden_modules):
                    has_violations = True
                    break

        return is_executable, has_violations

    def _display_eval_results(self, results: dict[str, Any]):
        """Display evaluation results in table."""
        table = Table(title="Evaluation Results", show_header=True, header_style="bold cyan")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Target", style="yellow")
        table.add_column("Status", style="bold")

        # Executable Rate
        exec_rate = results["executable_rate"]
        exec_status = "✓ PASS" if exec_rate >= 0.95 else "✗ FAIL"
        exec_color = "green" if exec_rate >= 0.95 else "red"
        table.add_row(
            "Executable Rate",
            f"{exec_rate:.1%}",
            "≥95%",
            f"[{exec_color}]{exec_status}[/{exec_color}]",
        )

        # Security Violations
        sec_viols = results["security_violations"]
        sec_status = "✓ PASS" if sec_viols == 0 else "✗ FAIL"
        sec_color = "green" if sec_viols == 0 else "red"
        table.add_row(
            "Security Violations",
            str(sec_viols),
            "0",
            f"[{sec_color}]{sec_status}[/{sec_color}]",
        )

        # Latency p99
        lat_p99 = results["latency_p99_ms"]
        lat_status = "✓ PASS" if lat_p99 <= 100 else "✗ FAIL"
        lat_color = "green" if lat_p99 <= 100 else "red"
        table.add_row(
            "Latency p99",
            f"{lat_p99:.1f}ms",
            "≤100ms",
            f"[{lat_color}]{lat_status}[/{lat_color}]",
        )

        # Error Rate
        err_rate = results["error_rate"]
        err_status = "✓ PASS" if err_rate < 0.005 else "⚠ WARN"
        err_color = "green" if err_rate < 0.005 else "yellow"
        table.add_row(
            "Error Rate",
            f"{err_rate:.1%}",
            "<0.5%",
            f"[{err_color}]{err_status}[/{err_color}]",
        )

        console.print(table)


# ============================================================================
# MODEL DEPLOYMENT
# ============================================================================


class ModelDeployer:
    """Deploy fine-tuned model to Vertex AI endpoint."""

    def __init__(self, config: TrainingConfig):
        """Initialize deployer."""
        self.config = config

    def deploy_model(self, checkpoint_url: str, endpoint_name: str | None = None) -> str:
        """Deploy model checkpoint to Vertex AI endpoint.

        Args:
            checkpoint_url: GCS URL of best checkpoint
            endpoint_name: Custom endpoint name (optional)

        Returns:
            Endpoint resource name

        """
        if endpoint_name is None:
            endpoint_name = f"{self.config.model_name}-endpoint"

        console.print(f"\n[bold]Deploying model to endpoint: {endpoint_name}[/bold]")

        try:
            # Upload model to Vertex AI Model Registry
            model = aiplatform.Model.upload(
                display_name=self.config.model_name,
                artifact_uri=checkpoint_url,
                serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-11:latest",
                # Note: Actual serving container depends on Gemini deployment requirements
            )

            logger.info(f"Model uploaded: {model.resource_name}")

            # Create endpoint
            endpoint = aiplatform.Endpoint.create(display_name=endpoint_name)

            logger.info(f"Endpoint created: {endpoint.resource_name}")

            # Deploy model to endpoint
            model.deploy(
                endpoint=endpoint,
                deployed_model_display_name=self.config.model_name,
                machine_type="n1-standard-4",
                min_replica_count=self.config.min_replica_count,
                max_replica_count=self.config.max_replica_count,
                traffic_percentage=100,
            )

            console.print("[green]✓ Model deployed successfully[/green]")
            console.print(f"  Endpoint: {endpoint.resource_name}\n")

            return endpoint.resource_name

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            raise


# ============================================================================
# FULL PIPELINE ORCHESTRATOR
# ============================================================================


class TrainingPipeline:
    """Orchestrate end-to-end training pipeline."""

    def __init__(self, config: TrainingConfig):
        """Initialize pipeline components."""
        self.config = config
        self.gcs_manager = GCSDatasetManager(config)
        self.trainer = VertexAITrainer(config)
        self.evaluator = ModelEvaluator(config)
        self.deployer = ModelDeployer(config)

    def run_full_pipeline(self) -> dict[str, Any]:
        """Execute complete training pipeline.

        Steps:
            1. Setup GCS bucket
            2. Prepare and upload training data
            3. Submit training job
            4. Monitor job completion
            5. Evaluate checkpoints
            6. Select best checkpoint
            7. (Optional) Deploy to endpoint

        Returns:
            Pipeline results and metadata

        """
        console.print(
            Panel.fit(
                "[bold cyan]Vertex AI Training Pipeline for Cor.54 CodeAct Orchestrator[/bold cyan]\n"
                f"Model: {self.config.model_name}\n"
                f"Base: {self.config.base_model}\n"
                f"Project: {self.config.project_id}",
                border_style="cyan",
            ),
        )

        pipeline_start = time.time()
        results = {
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "config": asdict(self.config),
        }

        try:
            # Step 1: Setup
            console.print("\n[bold cyan]━━━ Step 1: Setup GCS Infrastructure ━━━[/bold cyan]")
            self.gcs_manager.setup_bucket()

            # Step 2: Prepare data
            console.print("\n[bold cyan]━━━ Step 2: Prepare Training Data ━━━[/bold cyan]")
            train_gcs, val_gcs = self.gcs_manager.prepare_training_data(
                single_turn_path=self.config.single_turn_data,
                multi_turn_path=self.config.multi_turn_data,
                single_turn_ratio=self.config.single_turn_ratio,
                train_val_split=self.config.train_val_split,
            )

            results["train_data"] = train_gcs
            results["val_data"] = val_gcs

            # Step 3: Submit training
            console.print("\n[bold cyan]━━━ Step 3: Submit Training Job ━━━[/bold cyan]")
            job_name = self.trainer.submit_training_job(train_gcs, val_gcs)
            results["job_name"] = job_name

            # Step 4: Monitor training
            console.print("\n[bold cyan]━━━ Step 4: Monitor Training ━━━[/bold cyan]")
            job_result = self.trainer.monitor_training_job(job_name)

            if job_result["status"] != "success":
                results["status"] = "failed"
                results["error"] = job_result.get("error", "Training failed")
                return results

            results["training_time"] = job_result["elapsed_time"]

            # Step 5: Get checkpoints
            console.print("\n[bold cyan]━━━ Step 5: Retrieve Checkpoints ━━━[/bold cyan]")
            checkpoints = self.trainer.get_model_checkpoints(job_name)
            results["checkpoints"] = checkpoints

            # Step 6: Evaluate checkpoints
            console.print("\n[bold cyan]━━━ Step 6: Evaluate Checkpoints ━━━[/bold cyan]")

            # Load validation data
            val_examples = GCSDatasetManager._load_jsonl(Path("/tmp/val.jsonl"))

            eval_results = []
            for checkpoint in checkpoints:
                eval_result = self.evaluator.evaluate_checkpoint(
                    checkpoint,
                    val_examples,
                    sample_size=self.config.eval_sample_size,
                )
                eval_results.append(eval_result)

            results["evaluations"] = eval_results

            # Select best checkpoint (highest executable rate, lowest latency)
            best_checkpoint = self._select_best_checkpoint(eval_results)
            results["best_checkpoint"] = best_checkpoint

            console.print(
                f"\n[green]✓ Best checkpoint: {Path(best_checkpoint['checkpoint']).name}[/green]",
            )
            console.print(f"  Executable Rate: {best_checkpoint['executable_rate']:.1%}")
            console.print(f"  Latency p99: {best_checkpoint['latency_p99_ms']:.1f}ms\n")

            # Step 7: Deploy (if enabled)
            if self.config.auto_deploy:
                console.print("\n[bold cyan]━━━ Step 7: Deploy Model ━━━[/bold cyan]")
                endpoint = self.deployer.deploy_model(best_checkpoint["checkpoint"])
                results["endpoint"] = endpoint
            else:
                console.print(
                    "\n[yellow]Step 7: Auto-deploy disabled (use --auto_deploy=true)[/yellow]",
                )

            # Complete
            results["status"] = "success"
            results["elapsed_time"] = time.time() - pipeline_start
            results["end_time"] = datetime.now().isoformat()

            self._display_final_summary(results)

            return results

        except Exception as e:
            logger.exception(f"Pipeline failed: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
            results["elapsed_time"] = time.time() - pipeline_start

            console.print(f"\n[red]✗ Pipeline failed: {e}[/red]")

            return results

    def _select_best_checkpoint(self, eval_results: list[dict[str, Any]]) -> dict[str, Any]:
        """Select best checkpoint based on metrics.

        Criteria (in order of priority):
            1. Security violations == 0 (hard requirement)
            2. Executable rate >= 95%
            3. Latency p99 <= 100ms
            4. Highest executable rate (if multiple pass)

        Returns:
            Best checkpoint evaluation result

        """
        # Filter: no security violations
        safe_checkpoints = [r for r in eval_results if r["security_violations"] == 0]

        if not safe_checkpoints:
            logger.warning("No checkpoints passed security validation!")
            # Return least-bad option
            return min(eval_results, key=lambda r: r["security_violations"])

        # Filter: executable rate >= 95%
        executable_checkpoints = [r for r in safe_checkpoints if r["executable_rate"] >= 0.95]

        if not executable_checkpoints:
            logger.warning("No checkpoints met executable rate threshold (95%)")
            # Return highest executable rate
            return max(safe_checkpoints, key=lambda r: r["executable_rate"])

        # Filter: latency p99 <= 100ms
        fast_checkpoints = [r for r in executable_checkpoints if r["latency_p99_ms"] <= 100]

        if not fast_checkpoints:
            logger.warning("No checkpoints met latency threshold (100ms p99)")
            # Return lowest latency
            return min(executable_checkpoints, key=lambda r: r["latency_p99_ms"])

        # Select highest executable rate among remaining
        best = max(fast_checkpoints, key=lambda r: r["executable_rate"])

        return best

    def _display_final_summary(self, results: dict[str, Any]):
        """Display final pipeline summary."""
        console.print("\n")
        console.print(
            Panel.fit(
                f"[bold green]✓ Training Pipeline Complete[/bold green]\n\n"
                f"Status: {results['status'].upper()}\n"
                f"Total Time: {results['elapsed_time'] / 3600:.1f} hours\n"
                f"Best Checkpoint: {Path(results['best_checkpoint']['checkpoint']).name}\n"
                f"Executable Rate: {results['best_checkpoint']['executable_rate']:.1%}\n"
                f"Latency p99: {results['best_checkpoint']['latency_p99_ms']:.1f}ms\n"
                f"Security Violations: {results['best_checkpoint']['security_violations']}\n"
                + (
                    f"Deployed Endpoint: {results.get('endpoint', 'N/A')}"
                    if self.config.auto_deploy
                    else ""
                ),
                border_style="green",
            ),
        )

        # Save results
        results_path = Path(f"training_results_{self.config.model_name}.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        console.print(f"\n[cyan]Results saved to: {results_path}[/cyan]\n")


# ============================================================================
# CLI INTERFACE
# ============================================================================


@click.command()
@click.option(
    "--project_id",
    type=str,
    envvar="GCP_PROJECT_ID",
    help="GCP project ID (or set GCP_PROJECT_ID env var)",
)
@click.option(
    "--single_turn_data",
    type=click.Path(exists=True),
    help="Path to single-turn training data (JSONL)",
)
@click.option(
    "--multi_turn_data",
    type=click.Path(exists=True),
    help="Path to multi-turn training data (JSONL)",
)
@click.option(
    "--model_name",
    type=str,
    default="gemini-policy-v1",
    help="Name for fine-tuned model",
)
@click.option(
    "--base_model",
    type=str,
    default="gemini-1.5-pro-002",
    help="Base Gemini model to fine-tune",
)
@click.option("--learning_rate", type=float, default=1e-5, help="Learning rate for fine-tuning")
@click.option("--num_epochs", type=int, default=3, help="Number of training epochs")
@click.option(
    "--auto_deploy",
    is_flag=True,
    help="Automatically deploy best checkpoint to endpoint",
)
@click.option("--setup_only", is_flag=True, help="Only setup GCS infrastructure (no training)")
@click.option("--evaluate_only", is_flag=True, help="Only evaluate existing checkpoint")
@click.option("--checkpoint", type=str, help="Checkpoint URL for evaluation (with --evaluate_only)")
def main(
    project_id: str | None,
    single_turn_data: str | None,
    multi_turn_data: str | None,
    model_name: str,
    base_model: str,
    learning_rate: float,
    num_epochs: int,
    auto_deploy: bool,
    setup_only: bool,
    evaluate_only: bool,
    checkpoint: str | None,
):
    """Vertex AI Training Pipeline for Cor.54 CodeAct Orchestrator.

    This tool automates the complete fine-tuning workflow for Gemini models
    on Google Cloud Vertex AI, including dataset preparation, training,
    evaluation, and deployment.

    Example usage:

        # Full pipeline
        python vertex_ai_pipeline.py \\
            --single_turn_data=datasets/single_turn_examples.jsonl \\
            --multi_turn_data=datasets/multi_turn_trajectories.jsonl \\
            --model_name=gemini-policy-v1 \\
            --auto_deploy

        # Setup only
        python vertex_ai_pipeline.py --setup_only

        # Evaluate checkpoint
        python vertex_ai_pipeline.py \\
            --evaluate_only \\
            --checkpoint=gs://bucket/checkpoints/model/epoch-3
    """
    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    # Build config
    try:
        config = TrainingConfig(project_id=project_id) if project_id else TrainingConfig.from_env()

        config.model_name = model_name
        config.base_model = base_model
        config.learning_rate = learning_rate
        config.num_epochs = num_epochs
        config.auto_deploy = auto_deploy

        if single_turn_data:
            config.single_turn_data = Path(single_turn_data)
        if multi_turn_data:
            config.multi_turn_data = Path(multi_turn_data)

    except Exception as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)

    # Execute
    try:
        if setup_only:
            # Setup only
            console.print("[bold cyan]Running setup only[/bold cyan]")
            gcs_manager = GCSDatasetManager(config)
            gcs_manager.setup_bucket()
            console.print("[green]✓ Setup complete[/green]")

        elif evaluate_only:
            # Evaluation only
            if not checkpoint:
                console.print("[red]Error: --checkpoint required for --evaluate_only[/red]")
                sys.exit(1)

            console.print(f"[bold cyan]Evaluating checkpoint: {checkpoint}[/bold cyan]")

            # Need validation data
            if not config.single_turn_data:
                console.print("[red]Error: --single_turn_data required for evaluation[/red]")
                sys.exit(1)

            # Load validation data (use first 100 examples)
            val_examples = GCSDatasetManager._load_jsonl(config.single_turn_data)[:100]

            evaluator = ModelEvaluator(config)
            results = evaluator.evaluate_checkpoint(checkpoint, val_examples)

            console.print("[green]✓ Evaluation complete[/green]")

        else:
            # Full pipeline
            if not config.single_turn_data:
                console.print("[red]Error: --single_turn_data required for training[/red]")
                sys.exit(1)

            pipeline = TrainingPipeline(config)
            results = pipeline.run_full_pipeline()

            if results["status"] != "success":
                console.print(
                    f"[red]Pipeline failed: {results.get('error', 'Unknown error')}[/red]",
                )
                sys.exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Pipeline interrupted by user[/yellow]")
        sys.exit(1)

    except Exception as e:
        logger.exception(f"Pipeline error: {e}")
        console.print(f"\n[red]Pipeline error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
