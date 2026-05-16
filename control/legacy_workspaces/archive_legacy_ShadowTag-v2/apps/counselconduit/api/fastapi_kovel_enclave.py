# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
import os
import logging
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from contextlib import asynccontextmanager


# Retention-minimized logger setup
class RedactedFormatter(logging.Formatter):
  def format(self, record: logging.LogRecord) -> str:
    # Prevent any sensitive context from leaking into logs
    msg = super().format(record)
    if "secret" in msg.lower() or "token" in msg.lower():
      return "[REDACTED LOG]"
    return msg


logger = logging.getLogger("kovel_enclave")
handler = logging.StreamHandler()
handler.setFormatter(RedactedFormatter("[kovel-enclave] %(levelname)s - %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------
# Telemetry Interface (Triple-Dip Architecture)
# ---------------------------------------------------------
class TelemetryEvent(BaseModel):
  event_type: str
  tenant_id: str
  model_family: str
  tokens_used: int
  cached_tokens_yield: int
  retention_policy_applied: bool


class TelemetryProvider:
  @staticmethod
  def capture(event: TelemetryEvent) -> None:
    """
    Record usage for the Triple-Dip pipeline securely.
    No transcript data or sensitive prompts ever enter this stream.
    """
    if not event.retention_policy_applied:
      logger.error("Attempted telemetry capture without explicit retention policy.")
      raise ValueError("All telemetry requires retention_policy_applied=True")
    logger.info(f"Captured {event.event_type} telemetry for Tenant {event.tenant_id}")


# ---------------------------------------------------------
# Kovel Doctrine Initialization
# ---------------------------------------------------------
KOVEL_KMS_SECRET = os.getenv("KOVEL_KMS_SECRET")


@asynccontextmanager
async def lifespan(app: FastAPI):
  # INSECURE FALLBACK REMOVED: Immediate fatal exit if KMS secret is missing.
  if not KOVEL_KMS_SECRET:
    logger.critical("KOVEL_KMS_SECRET is missing from environment. Refusing to boot.")
    raise RuntimeError("Missing KMS Secret for Kovel Doctrine Engine.")
  logger.info("Kovel Enclave Booting. Zero-retention checks active.")
  yield
  logger.info("Kovel Enclave Terminating. Memory buffers dropped.")


app = FastAPI(lifespan=lifespan)


# ---------------------------------------------------------
# Retention-Minimization Middleware (No-Store Headers)
# ---------------------------------------------------------
@app.middleware("http")
async def apply_zero_retention_headers(request: Request, call_next):
  """
  Forces non-retention headers on all incoming and outgoing connections.
  """
  response: Response = await call_next(request)
  response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
  response.headers["Pragma"] = "no-cache"
  response.headers["Expires"] = "0"
  response.headers["X-Retention-Policy"] = "ZERO_RETENTION_ASSERTED"
  return response


# ---------------------------------------------------------
# API Routes
# ---------------------------------------------------------
class ConduitRequest(BaseModel):
  tenant_id: str
  prompt_payload: str
  vertex_context_cache_enabled: bool = True


class ConduitResponse(BaseModel):
  status: str
  model_used: str
  output: str
  message: str


@app.post("/v1/conduit/process", response_model=ConduitResponse)
async def process_conduit_payload(payload: ConduitRequest):
  """
  Primary ingestion route. Processes payload safely via Vertex AI models,
  taking advantage of supported 2.5 context caching discounts logically,
  but never retaining the raw prompt state beyond execution.
  """
  logger.info(f"Processing isolated payload for tenant {payload.tenant_id}")

  # Simulate processing via actual supported Vertex models
  target_model = "gemini-2.5-flash-lite"

  # Fake processing simulation...
  fake_output = f"[Simulated execution using {target_model}]"

  # Capture billing telemetry (no sensitive data)
  TelemetryProvider.capture(
    TelemetryEvent(
      event_type="vertex_invocation",
      tenant_id=payload.tenant_id,
      model_family=target_model,
      tokens_used=420,
      cached_tokens_yield=3000 if payload.vertex_context_cache_enabled else 0,
      retention_policy_applied=True,
    )
  )

  # 100% Volatile output returned
  return ConduitResponse(
    status="SUCCESS",
    model_used=target_model,
    output=fake_output,
    message="Zero retention applied. Buffers clearing.",
  )
