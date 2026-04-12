from fastapi import APIRouter, HTTPException
import os

from app.models.orchestrator import GenerateRequest, DraftSpec
from app.services.hf_pool import HFClientPool, HFEndpoint
from app.services.llm_orchestrator import produce_with_dual_review

router = APIRouter()

# Global pool, initialized on startup
HF_POOL = None

def get_hf_pool():
    if not HF_POOL:
        raise HTTPException(503, "HF Pool not initialized")
    return HF_POOL

@router.on_event("startup")
async def startup():
    global HF_POOL
    # Load endpoints from env/secret store; examples only.
    # In production, these should come from settings/secrets
    HF_POOL = HFClientPool(endpoints=[
        HFEndpoint(name="hf1", api_key=os.getenv("HF_KEY_1", ""), model_id="meta-llama/Meta-Llama-3-8B-Instruct"),
        HFEndpoint(name="hf2", api_key=os.getenv("HF_KEY_2", ""), model_id="mistralai/Mistral-7B-Instruct-v0.3"),
    ])

@router.post("/generate")
async def generate(req: GenerateRequest):
    if not req.task:
        raise HTTPException(400, "task is required")

    spec = DraftSpec(task=req.task, constraints=req.constraints, style=req.style)
    pool = get_hf_pool()

    result = await produce_with_dual_review(pool, spec)
    return result
