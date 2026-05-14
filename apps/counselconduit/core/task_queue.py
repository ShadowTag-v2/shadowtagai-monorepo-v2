# apps/counselconduit/core/task_queue.py
import json
import logging
import os
from typing import Any, Dict

from google.cloud import tasks_v2
from google.protobuf import timestamp_pb2
import datetime

logger = logging.getLogger(__name__)

# Reads from env
PROJECT_ID = os.getenv("GCP_PROJECT", "shadowtag-omega-v4")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
QUEUE_NAME = os.getenv("TASK_QUEUE_NAME", "counselconduit-tasks")
SERVICE_URL = os.getenv(
  "SERVICE_URL", "https://counselconduit-767252945109.us-central1.run.app"
)


class TaskQueueClient:
  """Google Cloud Tasks client for asynchronous job execution."""

  _client = None

  @classmethod
  def get_client(cls):
    if cls._client is None:
      try:
        cls._client = tasks_v2.CloudTasksClient()
      except Exception as e:
        logger.error(f"Failed to initialize CloudTasksClient: {e}")
        # Fallback to None if not running in GCP or credentials missing
    return cls._client

  @classmethod
  def get_parent(cls):
    client = cls.get_client()
    if client:
      return client.queue_path(PROJECT_ID, LOCATION, QUEUE_NAME)
    return None

  @classmethod
  def enqueue_task(
    cls, endpoint: str, payload: Dict[str, Any], in_seconds: int = 0
  ) -> str:
    """Enqueue an HTTP task to Cloud Tasks.

    Args:
        endpoint: URL path (e.g., '/tasks/stripe-fulfillment')
        payload: JSON serializable dictionary
        in_seconds: Delay before execution

    Returns:
        Task name string.
    """
    client = cls.get_client()
    parent = cls.get_parent()

    if not client or not parent:
      logger.warning(
        "Cloud Tasks client unavailable. Fallback: Executing task synchronously?"
      )
      # For this task, if we don't have tasks client, we might just log or fail
      # In a real environment, we'd raise or do a background thread
      raise RuntimeError("Cloud Tasks client not configured")

    url = f"{SERVICE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    task = {
      "http_request": {
        "http_method": tasks_v2.HttpMethod.POST,
        "url": url,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload).encode(),
      }
    }

    if in_seconds > 0:
      timestamp = timestamp_pb2.Timestamp()
      timestamp.FromDatetime(
        datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(seconds=in_seconds)
      )
      task["schedule_time"] = timestamp

    try:
      response = client.create_task(request={"parent": parent, "task": task})
      logger.info(f"Enqueued task {response.name}")
      return response.name
    except Exception as e:
      logger.error(f"Failed to enqueue task: {e}")
      raise
