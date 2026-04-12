import os

from litestar import Litestar, post
from litestar.connection import ASGIConnection
from litestar.exceptions import HTTPException, NotAuthorizedException
from pydantic import BaseModel, ValidationError

API_KEY_NAME = "X-ShadowTag-Knowledge-Key"


class TemporalIdentityPayload(BaseModel):
    execution_hash: str
    initiator_uuid: str
    target_node: str
    authorized_actions: list[str]
    payload_size_bytes: int


async def verify_zero_trust_token(
    connection: ASGIConnection, _: BaseException | None = None
) -> None:
    api_key = connection.headers.get(API_KEY_NAME)
    valid_key = os.getenv("DEVELOPER_KNOWLEDGE_API_KEY")
    if not valid_key:
        raise HTTPException(
            status_code=500,
            detail="CRITICAL: Node drift. Identity validation keys missing from environment.",
        )

    if not api_key or api_key != valid_key:
        raise NotAuthorizedException(
            detail="VIOLATION: Zero-Trust Ingress rejected unauthorized access. Request dropped."
        )


@post("/v1/system/execute/temporal", guards=[verify_zero_trust_token])
async def execute_temporal_job(data: dict) -> dict:
    """
    Litestar counterpart to the FastAPI ingestion. Designed to A/B test
    Pydantic parsing overhead during high-throughput Temporal dispatch.
    """
    try:
        identity = TemporalIdentityPayload(**data)
        return {"status": "Verified", "framework": "litestar", "identity": identity.model_dump()}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"Structural JSON Identity Violation: {e}")


app = Litestar(route_handlers=[execute_temporal_job])
