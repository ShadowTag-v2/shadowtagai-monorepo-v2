# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import logging

import google.cloud.logging

from observability.pii import redact_pii
from shared.config import settings


def set_up_observability():
  logger = logging.getLogger("CorCSRMC")
  logger.setLevel(logging.INFO)

  # Basic console output
  ch = logging.StreamHandler()
  ch.setLevel(logging.INFO)
  fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  ch.setFormatter(fmt)
  logger.addHandler(ch)

  # Note: google-cloud-logging auto-detects credentials locally via application-default.
  # We apply a strict PII scrubbing filter BEFORE it goes over the wire.
  try:
    client = google.cloud.logging.Client(project=settings.gcp_project_id)

    # We hook into standard python logging, so all existing logger calls get picked up
    # We add a custom Filter to the GCP handler to scrub PII.
    class PIIFilter(logging.Filter):
      def filter(self, record: logging.LogRecord) -> bool:
        # Only scrub the message content
        if isinstance(record.msg, str):
          record.msg = redact_pii(record.msg)
        return True

    cloud_handler = client.get_default_handler()
    cloud_handler.addFilter(PIIFilter())

    # Apply to our core logger
    logger.addHandler(cloud_handler)
    logger.info(
      f"GCP Cloud Logging tracking initialized for project {settings.gcp_project_id} with PII redact filter."
    )
  except Exception as e:
    logger.warning(
      f"Could not initialize GCP Logging (are credentials loaded?). Fallback to stdout. Err: {e}"
    )


set_up_observability()
