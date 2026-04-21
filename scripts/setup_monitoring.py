#!/usr/bin/env python3
"""Create Cloud Monitoring notification channels and alert policies.

Creates:
1. Email notification channel for admin alerts
2. Cloud Monitoring dashboard for dispatch metrics

Usage:
    CLOUDSDK_PYTHON=/opt/homebrew/bin/python3 python3 scripts/setup_monitoring.py
"""

from __future__ import annotations

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ID = "shadowtag-omega-v4"
ADMIN_EMAIL = "founder@shadowtagai.com"


def create_email_notification_channel() -> str | None:
    """Create email notification channel in Cloud Monitoring."""
    try:
        from google.cloud import monitoring_v3

        client = monitoring_v3.NotificationChannelServiceClient()
        project_name = f"projects/{PROJECT_ID}"

        # Check if channel already exists
        existing = list(client.list_notification_channels(
            request={"name": project_name}
        ))
        for ch in existing:
            if ch.type_ == "email" and ch.labels.get("email_address") == ADMIN_EMAIL:
                logger.info("Email channel already exists: %s", ch.name)
                return ch.name

        channel = monitoring_v3.NotificationChannel(
            type_="email",
            display_name="CounselConduit Admin Email",
            labels={"email_address": ADMIN_EMAIL},
            enabled={"value": True},
        )

        result = client.create_notification_channel(
            request={
                "name": project_name,
                "notification_channel": channel,
            }
        )
        logger.info("✓ Created email channel: %s", result.name)
        return result.name

    except ImportError:
        logger.error("google-cloud-monitoring not installed")
        return None
    except Exception as e:
        logger.error("Failed to create email channel: %s", e)
        return None


def create_dispatch_dashboard() -> str | None:
    """Create Cloud Monitoring dashboard for NadirClaw dispatch metrics."""
    try:
        from google.cloud import monitoring_dashboard_v1

        client = monitoring_dashboard_v1.DashboardsServiceClient()
        parent = f"projects/{PROJECT_ID}"

        dashboard = monitoring_dashboard_v1.Dashboard(
            display_name="NadirClaw Dispatch Dashboard",
            grid_layout=monitoring_dashboard_v1.GridLayout(
                columns=2,
                widgets=[
                    monitoring_dashboard_v1.Widget(
                        title="Dispatch Rate by Tier",
                        xy_chart=monitoring_dashboard_v1.XyChart(
                            data_sets=[
                                monitoring_dashboard_v1.XyChart.DataSet(
                                    time_series_query=monitoring_dashboard_v1.TimeSeriesQuery(
                                        time_series_filter=monitoring_dashboard_v1.TimeSeriesFilter(
                                            filter='metric.type = "custom.googleapis.com/counselconduit/dispatch.simple" OR metric.type = "custom.googleapis.com/counselconduit/dispatch.complex" OR metric.type = "custom.googleapis.com/counselconduit/dispatch.agentic"',
                                        ),
                                    ),
                                    plot_type=monitoring_dashboard_v1.XyChart.DataSet.PlotType.LINE,
                                ),
                            ],
                        ),
                    ),
                    monitoring_dashboard_v1.Widget(
                        title="Fallback Chain Hits",
                        xy_chart=monitoring_dashboard_v1.XyChart(
                            data_sets=[
                                monitoring_dashboard_v1.XyChart.DataSet(
                                    time_series_query=monitoring_dashboard_v1.TimeSeriesQuery(
                                        time_series_filter=monitoring_dashboard_v1.TimeSeriesFilter(
                                            filter='metric.type = "custom.googleapis.com/counselconduit/fallback.*"',
                                        ),
                                    ),
                                    plot_type=monitoring_dashboard_v1.XyChart.DataSet.PlotType.STACKED_BAR,
                                ),
                            ],
                        ),
                    ),
                    monitoring_dashboard_v1.Widget(
                        title="Circuit Breaker State",
                        scorecard=monitoring_dashboard_v1.Scorecard(
                            time_series_query=monitoring_dashboard_v1.TimeSeriesQuery(
                                time_series_filter=monitoring_dashboard_v1.TimeSeriesFilter(
                                    filter='resource.type = "cloud_run_revision" AND metric.type = "run.googleapis.com/request_count" AND metric.labels.response_code = "503"',
                                ),
                            ),
                        ),
                    ),
                    monitoring_dashboard_v1.Widget(
                        title="Request Latency (p95)",
                        xy_chart=monitoring_dashboard_v1.XyChart(
                            data_sets=[
                                monitoring_dashboard_v1.XyChart.DataSet(
                                    time_series_query=monitoring_dashboard_v1.TimeSeriesQuery(
                                        time_series_filter=monitoring_dashboard_v1.TimeSeriesFilter(
                                            filter='resource.type = "cloud_run_revision" AND metric.type = "run.googleapis.com/request_latencies"',
                                        ),
                                    ),
                                    plot_type=monitoring_dashboard_v1.XyChart.DataSet.PlotType.LINE,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

        result = client.create_dashboard(
            request={
                "parent": parent,
                "dashboard": dashboard,
            }
        )
        logger.info("✓ Created dashboard: %s", result.name)
        return result.name

    except ImportError:
        logger.warning("google-cloud-monitoring-dashboards not installed — skipping dashboard")
        return None
    except Exception as e:
        logger.error("Dashboard creation failed: %s", e)
        return None


def setup_alert_policies(notification_channel_name: str | None) -> None:
    """Set up alert policies for dispatch monitoring."""
    if not notification_channel_name:
        logger.warning("No notification channel — skipping alert policies")
        return

    try:
        # Import and run monitor alert functions
        sys.path.insert(0, ".")
        from apps.counselconduit.api.monitoring import (
            configure_circuit_breaker_alert,
            configure_fallback_saturation_alert,
        )

        import asyncio

        channels = [notification_channel_name]

        result1 = asyncio.run(configure_fallback_saturation_alert(channels))
        logger.info("Fallback alert: %s", result1)

        result2 = asyncio.run(configure_circuit_breaker_alert(channels))
        logger.info("Circuit breaker alert: %s", result2)

    except Exception as e:
        logger.error("Alert policy setup failed: %s", e)


def create_cloud_scheduler_job() -> None:
    """Create Cloud Scheduler job for session cleanup every 5 minutes."""
    try:
        from google.cloud import scheduler_v1

        client = scheduler_v1.CloudSchedulerClient()
        parent = f"projects/{PROJECT_ID}/locations/us-central1"
        job_name = f"{parent}/jobs/counselconduit-session-cleanup"

        # Check if job exists
        try:
            existing = client.get_job(request={"name": job_name})
            logger.info("Job already exists: %s", existing.name)
            return
        except Exception:
            pass

        job = scheduler_v1.Job(
            name=job_name,
            description="Evict expired NadirClaw session pins every 5 minutes",
            schedule="*/5 * * * *",
            time_zone="America/Los_Angeles",
            http_target=scheduler_v1.HttpTarget(
                uri="https://counselconduit-6byqzjbd7a-uc.a.run.app/admin/session-cleanup",
                http_method=scheduler_v1.HttpMethod.POST,
                oidc_token=scheduler_v1.OidcToken(
                    service_account_email=f"counselconduit-sa@{PROJECT_ID}.iam.gserviceaccount.com",
                    audience="https://counselconduit-6byqzjbd7a-uc.a.run.app",
                ),
            ),
            retry_config=scheduler_v1.RetryConfig(
                retry_count=3,
                max_retry_duration={"seconds": 60},
            ),
        )

        result = client.create_job(
            request={
                "parent": parent,
                "job": job,
            }
        )
        logger.info("✓ Created scheduler job: %s", result.name)

    except ImportError:
        logger.warning("google-cloud-scheduler not installed — skipping")
    except Exception as e:
        logger.error("Scheduler job creation failed: %s", e)


if __name__ == "__main__":
    logger.info("=== NadirClaw Monitoring & Scheduler Setup ===")

    # 1. Create notification channel
    channel_name = create_email_notification_channel()

    # 2. Create dashboard
    create_dispatch_dashboard()

    # 3. Set up alert policies
    setup_alert_policies(channel_name)

    # 4. Create Cloud Scheduler job
    create_cloud_scheduler_job()

    logger.info("=== Setup complete ===")
