import logging
import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

# This URL will be updated once the Cloud Run deployment finishes
# For now, we use a placeholder or env var
VERIFIER_SERVICE_URL = os.getenv(
    "SHADOWTAG_VERIFIER_URL", "https://shadowtag-verifier-placeholder-uc.a.run.app/verify",
)


class ChirpReport(BaseModel):
    device_id: int
    epoch: int
    nonce: int
    hmac_tag: str
    snr_db: float
    witness_id: str


@router.post("/shadowtag/report")
async def forward_report(payload: ChirpReport):
    """Forward a chirp report to the ShadowTag Verifier Service (Cloud Run).
    Enforces UCMJ-style discipline: 5s timeout or die.
    """
    logger.info(
        f"Received chirp report from witness {payload.witness_id} for device {payload.device_id}",
    )

    try:
        async with httpx.AsyncClient() as client:
            # UCMJ Discipline: 5.0s timeout. No mercy.
            resp = await client.post(VERIFIER_SERVICE_URL, json=payload.dict(), timeout=5.0)

        if resp.status_code == 200:
            return resp.json()
        logger.warning(f"Verifier returned error: {resp.status_code} - {resp.text}")
        raise HTTPException(status_code=502, detail=f"Verifier rejected report: {resp.text}")

    except httpx.TimeoutException:
        logger.error("Verifier timed out (UCMJ Violation). Aborting.")
        raise HTTPException(status_code=504, detail="Verifier service timed out (UCMJ Violation)")
    except httpx.RequestError as e:
        logger.error(f"Connection failed: {e}")
        raise HTTPException(status_code=503, detail="Verifier service unavailable")
