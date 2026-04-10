"""
Training Job Dashboard
=======================
Rich terminal UI for GPU cluster job management.

Pattern from @ramith__: cluster-agnostic prototyping -> production submission.

Features:
- Live GPU cluster monitoring (4 Hz refresh)
- Job queue management
- Progress tracking with loss metrics
- Integration with Gemini 3 Pro pipeline
"""

import asyncio
import contextlib
import logging
import uuid
from datetime import datetime
from enum import Enum, StrEnum

from pydantic import BaseModel, Field
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

logger = logging.getLogger(__name__)


class JobStatus(StrEnum):
    """Status of a training job"""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GPUType(StrEnum):
    """Available GPU types"""

    H100 = "H100"
    A100 = "A100"
    L4 = "L4"
    T4 = "T4"
    V100 = "V100"


class GPUCluster(BaseModel):
    """GPU cluster configuration"""

    name: str
    gpu_type: GPUType
    available_gpus: int
    total_gpus: int
    queue_depth: int
    region: str
    cost_per_hour: float = 0.0


class TrainingJob(BaseModel):
    """A training job in the queue"""

    job_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str
    model_type: str  # gemini-3, llama, custom
    status: JobStatus = JobStatus.PENDING
    cluster: str = ""
    gpus_requested: int = 1
    progress_pct: float = 0.0
    epochs_completed: int = 0
    total_epochs: int = 10
    loss: float | None = None
    learning_rate: float | None = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None


class TrainingMetrics(BaseModel):
    """Aggregated training metrics"""

    total_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    total_gpu_hours: float = 0.0
    estimated_cost: float = 0.0


class TrainingDashboard:
    """
    Rich terminal dashboard for training job management.

    Pattern from @ramith__: cluster-agnostic prototyping -> production submission.

    Usage:
        dashboard = TrainingDashboard()
        await dashboard.run()
    """

    # Default clusters
    DEFAULT_CLUSTERS = [
        GPUCluster(
            name="gke-h100-pool",
            gpu_type=GPUType.H100,
            available_gpus=8,
            total_gpus=16,
            queue_depth=3,
            region="us-central1",
            cost_per_hour=3.22,
        ),
        GPUCluster(
            name="gke-a100-pool",
            gpu_type=GPUType.A100,
            available_gpus=4,
            total_gpus=8,
            queue_depth=5,
            region="us-central1",
            cost_per_hour=2.93,
        ),
        GPUCluster(
            name="gke-l4-pool",
            gpu_type=GPUType.L4,
            available_gpus=12,
            total_gpus=16,
            queue_depth=2,
            region="us-central1",
            cost_per_hour=0.81,
        ),
        GPUCluster(
            name="gke-t4-pool",
            gpu_type=GPUType.T4,
            available_gpus=8,
            total_gpus=8,
            queue_depth=0,
            region="us-central1",
            cost_per_hour=0.35,
        ),
    ]

    def __init__(self):
        self.console = Console()
        self.clusters: dict[str, GPUCluster] = {c.name: c for c in self.DEFAULT_CLUSTERS}
        self.jobs: dict[str, TrainingJob] = {}
        self.metrics = TrainingMetrics()
        self.refresh_rate = 4  # Hz
        self._running = False

    def create_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3),
        )
        layout["main"].split_row(
            Layout(name="clusters", ratio=1),
            Layout(name="jobs", ratio=2),
            Layout(name="metrics", ratio=1),
        )
        return layout

    def render_header(self) -> Panel:
        """Render the header panel"""
        title = Text()
        title.append("TRAINING JOB DASHBOARD", style="bold cyan")
        title.append(" | ", style="dim")
        title.append("Gemini 3 Pro + Claude Code", style="green")
        title.append(" | ", style="dim")
        title.append(datetime.now().strftime("%H:%M:%S"), style="yellow")
        return Panel(title, style="bold")

    def render_clusters_panel(self) -> Panel:
        """Render the GPU clusters panel"""
        table = Table(title="GPU Clusters", expand=True, show_header=True)
        table.add_column("Cluster", style="cyan", no_wrap=True)
        table.add_column("GPU", style="green")
        table.add_column("Avail", justify="right")
        table.add_column("Queue", justify="right")
        table.add_column("$/hr", justify="right", style="yellow")

        for cluster in self.clusters.values():
            # Color availability based on capacity
            avail_ratio = cluster.available_gpus / cluster.total_gpus
            if avail_ratio > 0.5:
                avail_style = "green"
            elif avail_ratio > 0.2:
                avail_style = "yellow"
            else:
                avail_style = "red"

            table.add_row(
                cluster.name[:20],
                cluster.gpu_type.value,
                f"[{avail_style}]{cluster.available_gpus}/{cluster.total_gpus}[/]",
                str(cluster.queue_depth),
                f"${cluster.cost_per_hour:.2f}",
            )
        return Panel(table, title="[bold]Resources[/]", border_style="blue")

    def render_jobs_panel(self) -> Panel:
        """Render the training jobs panel"""
        table = Table(title="Training Jobs", expand=True, show_header=True)
        table.add_column("Job", style="cyan", no_wrap=True, width=12)
        table.add_column("Model", style="yellow", width=12)
        table.add_column("Status", width=10)
        table.add_column("Progress", width=15)
        table.add_column("Loss", justify="right", width=8)

        # Sort jobs by status priority (running first, then pending, etc.)
        status_priority = {
            JobStatus.RUNNING: 0,
            JobStatus.QUEUED: 1,
            JobStatus.PENDING: 2,
            JobStatus.COMPLETED: 3,
            JobStatus.FAILED: 4,
            JobStatus.CANCELLED: 5,
        }
        sorted_jobs = sorted(
            self.jobs.values(),
            key=lambda j: (status_priority.get(j.status, 99), -j.submitted_at.timestamp()),
        )

        for job in sorted_jobs[:10]:  # Show top 10 jobs
            # Status styling
            status_styles = {
                JobStatus.RUNNING: "[bold green]RUNNING[/]",
                JobStatus.COMPLETED: "[green]DONE[/]",
                JobStatus.FAILED: "[red]FAILED[/]",
                JobStatus.QUEUED: "[yellow]QUEUED[/]",
                JobStatus.PENDING: "[dim]PENDING[/]",
                JobStatus.CANCELLED: "[dim red]CANCEL[/]",
            }
            status_text = status_styles.get(job.status, job.status.value)

            # Progress bar
            filled = int(job.progress_pct / 10)
            empty = 10 - filled
            progress_bar = f"[green]{'█' * filled}[/][dim]{'░' * empty}[/] {job.progress_pct:.0f}%"

            # Loss display
            loss_text = f"{job.loss:.4f}" if job.loss else "-"

            table.add_row(
                job.name[:12],
                job.model_type[:12],
                status_text,
                progress_bar,
                loss_text,
            )

        if not self.jobs:
            table.add_row("[dim]No jobs[/]", "", "", "", "")

        return Panel(table, title="[bold]Jobs[/]", border_style="green")

    def render_metrics_panel(self) -> Panel:
        """Render the metrics panel"""
        self._update_metrics()

        content = Text()
        content.append("SUMMARY\n", style="bold underline")
        content.append("\nTotal Jobs: ", style="dim")
        content.append(f"{self.metrics.total_jobs}\n", style="cyan")
        content.append("Running: ", style="dim")
        content.append(f"{self.metrics.running_jobs}\n", style="green")
        content.append("Completed: ", style="dim")
        content.append(f"{self.metrics.completed_jobs}\n", style="blue")
        content.append("Failed: ", style="dim")
        content.append(f"{self.metrics.failed_jobs}\n", style="red")

        content.append("\nCOSTS\n", style="bold underline")
        content.append("\nGPU Hours: ", style="dim")
        content.append(f"{self.metrics.total_gpu_hours:.1f}h\n", style="yellow")
        content.append("Est. Cost: ", style="dim")
        content.append(f"${self.metrics.estimated_cost:.2f}\n", style="yellow")

        return Panel(content, title="[bold]Metrics[/]", border_style="yellow")

    def render_footer(self) -> Panel:
        """Render the footer panel"""
        footer = Text()
        footer.append("[q]", style="bold cyan")
        footer.append(" Quit  ", style="dim")
        footer.append("[s]", style="bold cyan")
        footer.append(" Submit Job  ", style="dim")
        footer.append("[c]", style="bold cyan")
        footer.append(" Cancel  ", style="dim")
        footer.append("[r]", style="bold cyan")
        footer.append(" Refresh", style="dim")
        return Panel(footer, style="dim")

    def _update_metrics(self):
        """Update aggregated metrics"""
        self.metrics.total_jobs = len(self.jobs)
        self.metrics.running_jobs = sum(
            1 for j in self.jobs.values() if j.status == JobStatus.RUNNING
        )
        self.metrics.completed_jobs = sum(
            1 for j in self.jobs.values() if j.status == JobStatus.COMPLETED
        )
        self.metrics.failed_jobs = sum(
            1 for j in self.jobs.values() if j.status == JobStatus.FAILED
        )

        # Calculate GPU hours and costs
        total_hours = 0.0
        total_cost = 0.0
        for job in self.jobs.values():
            if job.started_at:
                end_time = job.completed_at or datetime.utcnow()
                hours = (end_time - job.started_at).total_seconds() / 3600
                total_hours += hours * job.gpus_requested

                # Get cluster cost
                if job.cluster in self.clusters:
                    total_cost += (
                        hours * job.gpus_requested * self.clusters[job.cluster].cost_per_hour
                    )

        self.metrics.total_gpu_hours = total_hours
        self.metrics.estimated_cost = total_cost

    def submit_job(
        self,
        name: str,
        model_type: str = "gemini-3",
        gpus: int = 1,
        epochs: int = 10,
        cluster: str | None = None,
    ) -> TrainingJob:
        """Submit a new training job"""
        # Auto-select cluster if not specified
        if not cluster:
            for c in self.clusters.values():
                if c.available_gpus >= gpus:
                    cluster = c.name
                    break

        job = TrainingJob(
            name=name,
            model_type=model_type,
            gpus_requested=gpus,
            total_epochs=epochs,
            cluster=cluster or "",
            status=JobStatus.PENDING if not cluster else JobStatus.QUEUED,
        )

        self.jobs[job.job_id] = job
        logger.info(f"Submitted job {job.job_id}: {name}")
        return job

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            if job.status in (JobStatus.PENDING, JobStatus.QUEUED, JobStatus.RUNNING):
                job.status = JobStatus.CANCELLED
                logger.info(f"Cancelled job {job_id}")
                return True
        return False

    async def _simulate_job_progress(self):
        """Simulate job progress for demo purposes"""
        while self._running:
            for job in self.jobs.values():
                if job.status == JobStatus.QUEUED:
                    # Start queued jobs
                    if job.cluster in self.clusters:
                        cluster = self.clusters[job.cluster]
                        if cluster.available_gpus >= job.gpus_requested:
                            job.status = JobStatus.RUNNING
                            job.started_at = datetime.utcnow()
                            cluster.available_gpus -= job.gpus_requested
                            cluster.queue_depth = max(0, cluster.queue_depth - 1)

                elif job.status == JobStatus.RUNNING:
                    # Progress running jobs
                    job.progress_pct = min(100, job.progress_pct + 2)
                    job.epochs_completed = int(job.progress_pct / 100 * job.total_epochs)
                    job.loss = max(0.001, 2.0 * (1 - job.progress_pct / 100) + 0.001)

                    # Complete job
                    if job.progress_pct >= 100:
                        job.status = JobStatus.COMPLETED
                        job.completed_at = datetime.utcnow()
                        if job.cluster in self.clusters:
                            self.clusters[job.cluster].available_gpus += job.gpus_requested

            await asyncio.sleep(0.5)

    async def run(self):
        """Run the live dashboard"""
        self._running = True
        layout = self.create_layout()

        # Start job simulation in background
        simulation_task = asyncio.create_task(self._simulate_job_progress())

        try:
            with Live(layout, console=self.console, refresh_per_second=self.refresh_rate):
                while self._running:
                    layout["header"].update(self.render_header())
                    layout["clusters"].update(self.render_clusters_panel())
                    layout["jobs"].update(self.render_jobs_panel())
                    layout["metrics"].update(self.render_metrics_panel())
                    layout["footer"].update(self.render_footer())
                    await asyncio.sleep(1 / self.refresh_rate)
        finally:
            self._running = False
            simulation_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await simulation_task

    def stop(self):
        """Stop the dashboard"""
        self._running = False


# Demo usage
async def demo():
    """Demo the training dashboard"""
    dashboard = TrainingDashboard()

    # Submit some demo jobs
    dashboard.submit_job("gemini-finetune", "gemini-3", gpus=4, epochs=20)
    dashboard.submit_job("llama-train", "llama-3", gpus=8, epochs=50)
    dashboard.submit_job("custom-model", "custom", gpus=2, epochs=10)
    dashboard.submit_job("vision-model", "gemini-3-vision", gpus=4, epochs=30)

    # Run the dashboard
    await dashboard.run()


if __name__ == "__main__":
    asyncio.run(demo())
