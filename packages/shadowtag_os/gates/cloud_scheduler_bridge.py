# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Cloud Scheduler integration for ScheduleCronTool.

Maps CronSchedule entries from sleep_schedule_tools.py to
GCP Cloud Scheduler jobs. Production-ready scheduler management.

Usage:
    from packages.shadowtag_os.gates.cloud_scheduler_bridge import (
        create_cloud_scheduler_job,
        list_cloud_scheduler_jobs,
        delete_cloud_scheduler_job,
    )
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# GCP project defaults
DEFAULT_PROJECT = "shadowtag-omega-v4"
DEFAULT_LOCATION = "us-central1"
DEFAULT_SERVICE_ACCOUNT = "counselconduit-sa@shadowtag-omega-v4.iam.gserviceaccount.com"


@dataclass
class SchedulerJobConfig:
    """Configuration for a Cloud Scheduler job.

    Attributes:
        name: Job name (must be unique within project/location).
        schedule: Cron expression (e.g., "0 */6 * * *").
        description: Human-readable job description.
        target_url: Cloud Run or Cloud Tasks handler URL.
        http_method: HTTP method for the target (GET or POST).
        body: Request body for POST requests.
        timezone: IANA timezone (default: America/New_York).
        retry_count: Number of retries on failure.
        project: GCP project ID.
        location: GCP region.
    """

    name: str
    schedule: str
    description: str = ""
    target_url: str = ""
    http_method: str = "POST"
    body: str = ""
    timezone: str = "America/New_York"
    retry_count: int = 3
    project: str = DEFAULT_PROJECT
    location: str = DEFAULT_LOCATION


def create_cloud_scheduler_job(config: SchedulerJobConfig) -> dict:
    """Create a Cloud Scheduler job.

    Args:
        config: Job configuration.

    Returns:
        Dict with job details or error.
    """
    try:
        from google.cloud import scheduler_v1

        client = scheduler_v1.CloudSchedulerClient()
        parent = f"projects/{config.project}/locations/{config.location}"

        job = scheduler_v1.Job(
            name=f"{parent}/jobs/{config.name}",
            description=config.description,
            schedule=config.schedule,
            time_zone=config.timezone,
            http_target=scheduler_v1.HttpTarget(
                uri=config.target_url,
                http_method=getattr(scheduler_v1.HttpMethod, config.http_method, scheduler_v1.HttpMethod.POST),
                body=config.body.encode("utf-8") if config.body else b"",
                oidc_token=scheduler_v1.OidcToken(
                    service_account_email=DEFAULT_SERVICE_ACCOUNT,
                    audience=config.target_url,
                ),
            ),
            retry_config=scheduler_v1.RetryConfig(
                retry_count=config.retry_count,
            ),
        )

        created = client.create_job(parent=parent, job=job)
        logger.info("Cloud Scheduler: created job %s (%s)", config.name, config.schedule)
        return {
            "name": created.name,
            "schedule": created.schedule,
            "state": str(created.state),
            "target": config.target_url,
        }

    except ImportError:
        logger.warning("google-cloud-scheduler not installed, using local registry")
        # Fallback to local registry
        from packages.shadowtag_os.gates.sleep_schedule_tools import register_cron

        schedule = register_cron(
            schedule_id=config.name,
            cron_expr=config.schedule,
            task_name=config.description or config.name,
            handler=config.target_url,
        )
        return {
            "name": schedule.schedule_id,
            "schedule": schedule.cron_expr,
            "state": "LOCAL_REGISTRY",
            "target": schedule.handler,
        }
    except Exception as exc:
        logger.exception("Failed to create Cloud Scheduler job")
        return {"error": str(exc)}


def list_cloud_scheduler_jobs(
    project: str = DEFAULT_PROJECT,
    location: str = DEFAULT_LOCATION,
) -> list[dict]:
    """List all Cloud Scheduler jobs.

    Returns:
        List of job dicts with name, schedule, state.
    """
    try:
        from google.cloud import scheduler_v1

        client = scheduler_v1.CloudSchedulerClient()
        parent = f"projects/{project}/locations/{location}"

        jobs = []
        for job in client.list_jobs(parent=parent):
            jobs.append(
                {
                    "name": job.name.split("/")[-1],
                    "schedule": job.schedule,
                    "state": str(job.state),
                    "timezone": job.time_zone,
                }
            )
        return jobs

    except ImportError:
        from packages.shadowtag_os.gates.sleep_schedule_tools import list_schedules

        return [{"name": s.schedule_id, "schedule": s.cron_expr, "state": "LOCAL"} for s in list_schedules()]
    except Exception as exc:
        logger.exception("Failed to list Cloud Scheduler jobs")
        return [{"error": str(exc)}]


def delete_cloud_scheduler_job(
    name: str,
    project: str = DEFAULT_PROJECT,
    location: str = DEFAULT_LOCATION,
) -> bool:
    """Delete a Cloud Scheduler job.

    Returns:
        True if deleted, False on error.
    """
    try:
        from google.cloud import scheduler_v1

        client = scheduler_v1.CloudSchedulerClient()
        job_name = f"projects/{project}/locations/{location}/jobs/{name}"
        client.delete_job(name=job_name)
        logger.info("Cloud Scheduler: deleted job %s", name)
        return True

    except ImportError:
        from packages.shadowtag_os.gates.sleep_schedule_tools import remove_schedule

        return remove_schedule(name)
    except Exception:
        logger.exception("Failed to delete Cloud Scheduler job %s", name)
        return False
