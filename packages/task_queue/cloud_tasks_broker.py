# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""Google Cloud Tasks broker — canonical queue implementation.

Replaces BullMQ (banned per GEMINI.md Rich Hickey doctrine).
Queue Doctrine: Google Cloud Tasks is the EXCLUSIVE queue broker.

Architecture:
    - Task creation via Cloud Tasks API
    - HTTP target handlers on Cloud Run
    - Dead-letter queue for failed tasks
    - Idempotency via task name deduplication
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Cloud Tasks constants
DEFAULT_QUEUE_PATH = "projects/shadowtag-omega-v4/locations/us-central1/queues"
DEFAULT_HANDLER_BASE = "https://counselconduit-767252945109.us-central1.run.app"


@dataclass(frozen=True)
class TaskPayload:
  """A task to enqueue in Cloud Tasks.

  Attributes:
      queue_name: Queue identifier (e.g., "kernel-chain", "memory-drain").
      handler_path: HTTP path on the handler service (e.g., "/tasks/classify").
      body: JSON-serializable task payload.
      task_id: Optional idempotency key. If set, duplicate enqueues are no-ops.
      schedule_delay: Optional delay before task execution.
  """

  queue_name: str
  handler_path: str
  body: dict[str, Any] = field(default_factory=dict)
  task_id: str | None = None
  schedule_delay: timedelta | None = None


@dataclass
class TaskReceipt:
  """Receipt from a successfully enqueued task.

  Attributes:
      task_name: Full Cloud Tasks resource name.
      queue_name: Queue the task was enqueued to.
      scheduled_time: When the task will execute.
      created_at: When the enqueue call was made.
  """

  task_name: str
  queue_name: str
  scheduled_time: datetime | None = None
  created_at: datetime = field(default_factory=datetime.utcnow)


class CloudTasksBroker:
  """Google Cloud Tasks broker for async job processing.

  Usage:
      broker = CloudTasksBroker(project="shadowtag-omega-v4", location="us-central1")
      receipt = await broker.enqueue(TaskPayload(
          queue_name="kernel-chain",
          handler_path="/tasks/classify",
          body={"document_id": "abc123"},
      ))
  """

  def __init__(
    self,
    project: str = "shadowtag-omega-v4",
    location: str = "us-central1",
    handler_base_url: str = DEFAULT_HANDLER_BASE,
  ):
    self.project = project
    self.location = location
    self.handler_base_url = handler_base_url
    self._client = None

  def _get_client(self):
    """Lazy-load the Cloud Tasks client."""
    if self._client is None:
      try:
        from google.cloud import tasks_v2

        self._client = tasks_v2.CloudTasksClient()
      except ImportError as e:
        raise ImportError(
          "google-cloud-tasks is required. "
          "Install with: uv pip install google-cloud-tasks"
        ) from e
    return self._client

  def _queue_path(self, queue_name: str) -> str:
    """Build the full queue resource path."""
    return f"{DEFAULT_QUEUE_PATH}/{queue_name}"

  async def enqueue(self, payload: TaskPayload) -> TaskReceipt:
    """Enqueue a task to Cloud Tasks.

    Args:
        payload: Task to enqueue.

    Returns:
        TaskReceipt with the created task's resource name.
    """
    import asyncio

    client = self._get_client()

    parent = client.queue_path(self.project, self.location, payload.queue_name)

    task_config: dict[str, Any] = {
      "http_request": {
        "http_method": "POST",
        "url": f"{self.handler_base_url}{payload.handler_path}",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload.body).encode(),
      }
    }

    # Set idempotency key
    if payload.task_id:
      task_config["name"] = f"{parent}/tasks/{payload.task_id}"

    # Set schedule delay
    scheduled_time = None
    if payload.schedule_delay:
      from google.protobuf import timestamp_pb2

      scheduled_time = datetime.utcnow() + payload.schedule_delay
      ts = timestamp_pb2.Timestamp()
      ts.FromDatetime(scheduled_time)
      task_config["schedule_time"] = ts

    # Run in thread pool since Cloud Tasks client is sync
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
      None, lambda: client.create_task(parent=parent, task=task_config)
    )

    logger.info(
      "Enqueued task %s to queue %s",
      response.name,
      payload.queue_name,
    )

    return TaskReceipt(
      task_name=response.name,
      queue_name=payload.queue_name,
      scheduled_time=scheduled_time,
    )

  async def list_queues(self) -> list[str]:
    """List all queues in the project/location."""
    import asyncio

    client = self._get_client()
    parent = f"projects/{self.project}/locations/{self.location}"

    response = await asyncio.get_event_loop().run_in_executor(
      None, lambda: list(client.list_queues(parent=parent))
    )
    return [q.name for q in response]
