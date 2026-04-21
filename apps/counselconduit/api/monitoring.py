# apps/counselconduit/api/monitoring.py
"""Cloud Monitoring custom metric export for NadirClaw dispatch.

Exports dispatch metrics to Google Cloud Monitoring using the
google-cloud-monitoring SDK. Designed to be called periodically
by Cloud Scheduler or an internal cron loop.
"""

from __future__ import annotations

import logging
import time

logger = logging.getLogger("counselconduit.monitoring")

# Metric type prefix in Cloud Monitoring
METRIC_PREFIX = "custom.googleapis.com/counselconduit"
PROJECT_ID = "shadowtag-omega-v4"


async def export_metrics_to_cloud_monitoring() -> dict:
    """Push dispatch metrics to Google Cloud Monitoring.

    Uses google.cloud.monitoring_v3 TimeSeries API.
    Falls back gracefully if SDK not installed (local dev).
    """
    try:
        from google.cloud import monitoring_v3

        from apps.counselconduit.api.model_router import get_dispatch_metrics

        client = monitoring_v3.MetricServiceClient()
        project_name = f"projects/{PROJECT_ID}"

        metrics = get_dispatch_metrics()
        series_list = []
        now = time.time()

        for metric_key, value in metrics.items():
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"{METRIC_PREFIX}/{metric_key}"
            series.resource.type = "cloud_run_revision"
            series.resource.labels["project_id"] = PROJECT_ID
            series.resource.labels["service_name"] = "counselconduit"
            series.resource.labels["revision_name"] = "latest"
            series.resource.labels["location"] = "us-central1"

            point = monitoring_v3.Point()
            point.value.int64_value = value

            interval = monitoring_v3.TimeInterval()
            interval.end_time.seconds = int(now)
            interval.end_time.nanos = int((now % 1) * 1e9)
            point.interval = interval

            series.points = [point]
            series_list.append(series)

        if series_list:
            client.create_time_series(
                request={
                    "name": project_name,
                    "time_series": series_list,
                }
            )
            logger.info("Exported %d metrics to Cloud Monitoring", len(series_list))
        else:
            logger.debug("No metrics to export")

        return {"exported": len(series_list), "status": "ok"}

    except ImportError:
        logger.debug("google-cloud-monitoring not installed — skipping export")
        return {"exported": 0, "status": "skipped", "reason": "sdk_not_installed"}
    except Exception as e:
        logger.warning("Cloud Monitoring export failed: %s", e)
        return {"exported": 0, "status": "error", "reason": str(e)}


async def configure_fallback_saturation_alert() -> dict:
    """Configure Cloud Monitoring alert for fallback chain saturation.

    Triggers when fallback hits exceed threshold within window.
    """
    try:
        from google.cloud import monitoring_v3

        client = monitoring_v3.AlertPolicyServiceClient()
        project_name = f"projects/{PROJECT_ID}"

        policy = monitoring_v3.AlertPolicy(
            display_name="NadirClaw Fallback Saturation Alert",
            conditions=[
                monitoring_v3.AlertPolicy.Condition(
                    display_name="Fallback chain hits > 50/min",
                    condition_threshold=monitoring_v3.AlertPolicy.Condition.MetricThreshold(
                        filter=f'metric.type = "{METRIC_PREFIX}/fallback.*"',
                        comparison=monitoring_v3.AlertPolicy.Condition.MetricThreshold.ComparisonType.COMPARISON_GT,
                        threshold_value=50,
                        duration={"seconds": 60},
                        aggregations=[
                            monitoring_v3.Aggregation(
                                alignment_period={"seconds": 60},
                                per_series_aligner=monitoring_v3.Aggregation.Aligner.ALIGN_RATE,
                            )
                        ],
                    ),
                )
            ],
            notification_channels=[],  # Add channels via Cloud Console
            combiner=monitoring_v3.AlertPolicy.ConditionCombinerType.OR,
            enabled={"value": True},
        )

        result = client.create_alert_policy(
            request={
                "name": project_name,
                "alert_policy": policy,
            }
        )
        logger.info("Created fallback saturation alert: %s", result.name)
        return {"alert_policy": result.name, "status": "created"}

    except ImportError:
        return {"status": "skipped", "reason": "sdk_not_installed"}
    except Exception as e:
        logger.warning("Alert policy creation failed: %s", e)
        return {"status": "error", "reason": str(e)}
