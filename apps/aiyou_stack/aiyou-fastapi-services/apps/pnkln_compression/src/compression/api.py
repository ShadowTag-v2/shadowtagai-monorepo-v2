# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import base64
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.compression.pipeline import PnklnCompressionPipeline

pipeline_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pipeline_instance
    print("Initializing PNKLN Pipeline...")
    pipeline_instance = PnklnCompressionPipeline()
    print("Pipeline Ready.")
    yield
    print("Pipeline Shutdown.")


app = FastAPI(title="PNKLN Compression Service", lifespan=lifespan)


class RequestData(BaseModel):
    context: str
    session_id: str
    domain: str = "general"


@app.post("/decision")
async def decision(req: RequestData):
    if not pipeline_instance:
        raise HTTPException(503, "System initializing")

    try:
        packet, metrics = pipeline_instance.process(req.context, req.session_id, req.domain)

        return {
            "decision": packet.decision.name,
            "packet_base64": base64.b64encode(packet.to_bytes()).decode("utf-8"),
            "latency_ms": metrics.total_latency_ms,
            "sla_met": metrics.sla_met,
            "metrics": metrics.stage_latencies,
        }
    except Exception as e:
        raise HTTPException(500, str(e)) from e


@app.get("/health")
def health():
    return {"status": "ok", "ready": pipeline_instance is not None}
