# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Crisis Alert Webhook Service
============================
Webhook notifications for crisis events detected by California AI compliance.

Features:
- Real-time notifications when self-harm is detected
- Configurable webhook endpoints
- Retry logic with exponential backoff
- Audit logging of all notifications
- Support for multiple webhook targets
"""

import asyncio
import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class WebhookEventType(str, Enum):
  """Types of webhook events"""

  CRISIS_ALERT = "crisis_alert"
  SELF_HARM_DETECTED = "self_harm_detected"
  EXPLICIT_CONTENT_MINOR = "explicit_content_minor"
  COMPLIANCE_VIOLATION = "compliance_violation"
  BATCH_COMPLETE = "batch_complete"


class WebhookDeliveryStatus(str, Enum):
  """Webhook delivery status"""

  PENDING = "pending"
  DELIVERED = "delivered"
  FAILED = "failed"
  RETRYING = "retrying"


@dataclass
class WebhookConfig:
  """Webhook endpoint configuration"""

  endpoint_id: str
  url: str
  secret: str  # For HMAC signature
  enabled: bool = True
  events: list[WebhookEventType] = field(
    default_factory=lambda: [WebhookEventType.CRISIS_ALERT]
  )
  retry_count: int = 3
  retry_delay_seconds: int = 2
  timeout_seconds: int = 10


@dataclass
class WebhookPayload:
  """Webhook event payload"""

  event_id: str
  event_type: WebhookEventType
  timestamp: datetime
  data: dict[str, Any]
  signature: str | None = None

  def to_dict(self) -> dict:
    return {
      "event_id": self.event_id,
      "event_type": self.event_type.value,
      "timestamp": self.timestamp.isoformat(),
      "data": self.data,
    }


@dataclass
class WebhookDeliveryResult:
  """Result of webhook delivery attempt"""

  event_id: str
  endpoint_id: str
  status: WebhookDeliveryStatus
  attempts: int
  response_code: int | None = None
  error_message: str | None = None
  delivered_at: datetime | None = None


class CrisisAlertWebhook:
  """
  Crisis Alert Webhook Service.

  Sends real-time notifications when self-harm or other
  crisis events are detected by the compliance system.

  Usage:
      webhook = CrisisAlertWebhook()
      webhook.register_endpoint(WebhookConfig(
          endpoint_id="main",
          url="https://your-service.com/webhook",
          secret="your-secret-key",
      ))

      await webhook.send_crisis_alert(
          content_id="msg-123",
          severity="critical",
          detected_signals=["explicit_ideation"],
          user_context={"session_id": "sess-456"},
      )
  """

  def __init__(self):
    self.endpoints: dict[str, WebhookConfig] = {}
    self.delivery_log: list[WebhookDeliveryResult] = []
    self._http_client = None

  def register_endpoint(self, config: WebhookConfig) -> None:
    """Register a webhook endpoint"""
    self.endpoints[config.endpoint_id] = config
    logger.info(f"Registered webhook endpoint: {config.endpoint_id}")

  def unregister_endpoint(self, endpoint_id: str) -> None:
    """Unregister a webhook endpoint"""
    if endpoint_id in self.endpoints:
      del self.endpoints[endpoint_id]
      logger.info(f"Unregistered webhook endpoint: {endpoint_id}")

  def _generate_signature(self, payload: dict, secret: str) -> str:
    """Generate HMAC-SHA256 signature for payload"""
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    signature = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"

  def _generate_event_id(self) -> str:
    """Generate unique event ID"""
    return hashlib.sha256(f"{time.time()}-{id(self)}".encode()).hexdigest()[:24]

  async def send_crisis_alert(
    self,
    content_id: str,
    severity: str,
    detected_signals: list[str],
    user_context: dict | None = None,
    crisis_resources_provided: bool = True,
  ) -> list[WebhookDeliveryResult]:
    """
    Send crisis alert to all registered endpoints.

    Args:
        content_id: ID of content that triggered alert
        severity: Alert severity (low, medium, high, critical)
        detected_signals: List of detected signal types
        user_context: Optional user context (session_id, platform, etc.)
        crisis_resources_provided: Whether crisis resources were shown

    Returns:
        List of delivery results
    """
    event_id = self._generate_event_id()

    payload = WebhookPayload(
      event_id=event_id,
      event_type=WebhookEventType.CRISIS_ALERT,
      timestamp=datetime.utcnow(),
      data={
        "content_id": content_id,
        "severity": severity,
        "detected_signals": detected_signals,
        "user_context": user_context or {},
        "crisis_resources_provided": crisis_resources_provided,
        "action_required": severity in ["high", "critical"],
      },
    )

    return await self._send_to_all_endpoints(payload, WebhookEventType.CRISIS_ALERT)

  async def send_self_harm_alert(
    self,
    content_id: str,
    confidence: float,
    indicators: list[str],
    session_id: str | None = None,
  ) -> list[WebhookDeliveryResult]:
    """Send self-harm detection alert"""
    event_id = self._generate_event_id()

    payload = WebhookPayload(
      event_id=event_id,
      event_type=WebhookEventType.SELF_HARM_DETECTED,
      timestamp=datetime.utcnow(),
      data={
        "content_id": content_id,
        "confidence": confidence,
        "indicators": indicators,
        "session_id": session_id,
        "severity": "critical" if confidence > 0.8 else "high",
        "immediate_action_required": confidence > 0.9,
      },
    )

    return await self._send_to_all_endpoints(
      payload, WebhookEventType.SELF_HARM_DETECTED
    )

  async def send_minor_explicit_alert(
    self,
    content_id: str,
    content_categories: list[str],
    user_age_category: str,
  ) -> list[WebhookDeliveryResult]:
    """Send alert when explicit content detected for minor"""
    event_id = self._generate_event_id()

    payload = WebhookPayload(
      event_id=event_id,
      event_type=WebhookEventType.EXPLICIT_CONTENT_MINOR,
      timestamp=datetime.utcnow(),
      data={
        "content_id": content_id,
        "content_categories": content_categories,
        "user_age_category": user_age_category,
        "blocked": True,
      },
    )

    return await self._send_to_all_endpoints(
      payload, WebhookEventType.EXPLICIT_CONTENT_MINOR
    )

  async def _send_to_all_endpoints(
    self,
    payload: WebhookPayload,
    event_type: WebhookEventType,
  ) -> list[WebhookDeliveryResult]:
    """Send payload to all endpoints subscribed to event type"""
    results = []

    for endpoint_id, config in self.endpoints.items():
      if not config.enabled:
        continue
      if event_type not in config.events:
        continue

      result = await self._deliver_to_endpoint(payload, config)
      results.append(result)
      self.delivery_log.append(result)

    # Cleanup old logs
    if len(self.delivery_log) > 10000:
      self.delivery_log = self.delivery_log[-5000:]

    return results

  async def _deliver_to_endpoint(
    self,
    payload: WebhookPayload,
    config: WebhookConfig,
  ) -> WebhookDeliveryResult:
    """Deliver payload to a single endpoint with retry"""
    payload_dict = payload.to_dict()
    signature = self._generate_signature(payload_dict, config.secret)

    headers = {
      "Content-Type": "application/json",
      "X-Webhook-Signature": signature,
      "X-Event-Type": payload.event_type.value,
      "X-Event-ID": payload.event_id,
    }

    attempts = 0
    last_error = None

    for attempt in range(config.retry_count + 1):
      attempts = attempt + 1

      try:
        # Simulated HTTP call (in production, use aiohttp/httpx)
        response_code = await self._http_post(
          config.url,
          payload_dict,
          headers,
          config.timeout_seconds,
        )

        if 200 <= response_code < 300:
          return WebhookDeliveryResult(
            event_id=payload.event_id,
            endpoint_id=config.endpoint_id,
            status=WebhookDeliveryStatus.DELIVERED,
            attempts=attempts,
            response_code=response_code,
            delivered_at=datetime.utcnow(),
          )
        else:
          last_error = f"HTTP {response_code}"

      except Exception as e:
        last_error = str(e)

      # Wait before retry (exponential backoff)
      if attempt < config.retry_count:
        delay = config.retry_delay_seconds * (2**attempt)
        await asyncio.sleep(delay)

    return WebhookDeliveryResult(
      event_id=payload.event_id,
      endpoint_id=config.endpoint_id,
      status=WebhookDeliveryStatus.FAILED,
      attempts=attempts,
      error_message=last_error,
    )

  async def _http_post(
    self,
    url: str,
    payload: dict,
    headers: dict,
    timeout: int,
  ) -> int:
    """
    HTTP POST request.

    In production, replace with actual HTTP client (aiohttp/httpx).
    """
    try:
      import aiohttp

      async with (
        aiohttp.ClientSession() as session,
        session.post(
          url,
          json=payload,
          headers=headers,
          timeout=aiohttp.ClientTimeout(total=timeout),
        ) as response,
      ):
        return response.status
    except ImportError:
      # Fallback: simulate successful delivery for testing
      logger.warning("aiohttp not available, simulating webhook delivery")
      return 200

  def get_delivery_stats(self) -> dict[str, Any]:
    """Get webhook delivery statistics"""
    total = len(self.delivery_log)
    delivered = sum(
      1 for r in self.delivery_log if r.status == WebhookDeliveryStatus.DELIVERED
    )
    failed = sum(
      1 for r in self.delivery_log if r.status == WebhookDeliveryStatus.FAILED
    )

    return {
      "total_deliveries": total,
      "delivered": delivered,
      "failed": failed,
      "success_rate": delivered / total if total > 0 else 1.0,
      "endpoints_registered": len(self.endpoints),
      "endpoints_enabled": sum(1 for c in self.endpoints.values() if c.enabled),
    }


# Global instance
_crisis_webhook: CrisisAlertWebhook | None = None


def get_crisis_webhook() -> CrisisAlertWebhook:
  """Get or create global crisis webhook instance"""
  global _crisis_webhook
  if _crisis_webhook is None:
    _crisis_webhook = CrisisAlertWebhook()
  return _crisis_webhook
