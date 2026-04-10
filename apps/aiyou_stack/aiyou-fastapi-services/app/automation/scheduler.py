"""
Scheduler for managing scheduled jobs and automation.
"""

import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from croniter import croniter
from sqlalchemy import select

from app.automation.engine import workflow_engine
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.automation import ScheduledJob

logger = logging.getLogger(__name__)


class AutomationScheduler:
    """
    Manages scheduled jobs for automation workflows.
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            timezone=settings.SCHEDULER_TIMEZONE,
            job_defaults={"coalesce": True, "max_instances": settings.SCHEDULER_MAX_INSTANCES},
        )
        self._initialized = False

    async def start(self):
        """Start the scheduler and load all scheduled jobs."""
        if self._initialized:
            logger.warning("Scheduler already initialized")
            return

        logger.info("Starting automation scheduler")

        # Load all scheduled jobs from database
        await self.load_jobs()

        # Start the scheduler
        self.scheduler.start()
        self._initialized = True

        logger.info("Automation scheduler started")

    async def stop(self):
        """Stop the scheduler."""
        if not self._initialized:
            return

        logger.info("Stopping automation scheduler")
        self.scheduler.shutdown()
        self._initialized = False
        logger.info("Automation scheduler stopped")

    async def load_jobs(self):
        """Load all enabled scheduled jobs from database."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(ScheduledJob).where(ScheduledJob.enabled))
            jobs = result.scalars().all()

            logger.info(f"Loading {len(jobs)} scheduled jobs")

            for job in jobs:
                try:
                    await self.add_job(job)
                except Exception as e:
                    logger.error(f"Failed to load job {job.id}: {e}")

    async def add_job(self, scheduled_job: ScheduledJob):
        """
        Add a scheduled job to the scheduler.

        Args:
            scheduled_job: ScheduledJob instance to schedule
        """
        job_id = f"scheduled_job_{scheduled_job.id}"

        # Remove existing job if present
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        # Determine trigger type
        trigger = None

        if scheduled_job.cron_expression:
            # Validate cron expression
            if not croniter.is_valid(scheduled_job.cron_expression):
                raise ValueError(f"Invalid cron expression: {scheduled_job.cron_expression}")

            trigger = CronTrigger.from_crontab(scheduled_job.cron_expression)

        elif scheduled_job.interval_seconds:
            trigger = IntervalTrigger(seconds=scheduled_job.interval_seconds)

        else:
            raise ValueError("Either cron_expression or interval_seconds must be set")

        # Add job to scheduler
        self.scheduler.add_job(
            func=self._execute_scheduled_job,
            trigger=trigger,
            id=job_id,
            name=scheduled_job.name,
            args=[scheduled_job.id],
            replace_existing=True,
            next_run_time=scheduled_job.next_run_time or None,
        )

        logger.info(f"Added scheduled job {job_id}: {scheduled_job.name}")

    async def remove_job(self, scheduled_job_id: int):
        """
        Remove a scheduled job from the scheduler.

        Args:
            scheduled_job_id: ID of the scheduled job to remove
        """
        job_id = f"scheduled_job_{scheduled_job_id}"

        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled job {job_id}")

    async def _execute_scheduled_job(self, scheduled_job_id: int):
        """
        Execute a scheduled job.

        Args:
            scheduled_job_id: ID of the scheduled job to execute
        """
        async with AsyncSessionLocal() as session:
            # Get scheduled job
            result = await session.execute(
                select(ScheduledJob).where(ScheduledJob.id == scheduled_job_id)
            )
            scheduled_job = result.scalar_one_or_none()

            if not scheduled_job:
                logger.error(f"Scheduled job {scheduled_job_id} not found")
                return

            if not scheduled_job.enabled:
                logger.warning(f"Scheduled job {scheduled_job_id} is disabled, skipping")
                return

            # Update last run time
            scheduled_job.last_run_time = datetime.utcnow()

            # Calculate next run time
            job = self.scheduler.get_job(f"scheduled_job_{scheduled_job_id}")
            if job and job.next_run_time:
                scheduled_job.next_run_time = job.next_run_time.replace(tzinfo=None)

            await session.commit()

            # Execute workflow
            logger.info(f"Executing scheduled job {scheduled_job_id}: {scheduled_job.name}")

            try:
                execution = await workflow_engine.execute_workflow(
                    workflow_id=scheduled_job.workflow_id,
                    input_data=scheduled_job.parameters,
                    scheduled_job_id=scheduled_job.id,
                )

                logger.info(
                    f"Scheduled job {scheduled_job_id} completed with status: {execution.status}"
                )

            except Exception as e:
                logger.error(f"Scheduled job {scheduled_job_id} failed: {e}")


# Global scheduler instance
automation_scheduler = AutomationScheduler()
