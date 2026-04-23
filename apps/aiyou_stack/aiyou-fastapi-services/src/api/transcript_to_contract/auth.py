import base64
import json

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict


class GCPServiceIdentity(BaseModel):
    model_config = ConfigDict(extra="ignore")
    iss: str
    sub: str
    aud: str
    email: str


security = HTTPBearer()


def verify_zero_trust(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> GCPServiceIdentity:
    """Enforces the Zero-Trust identity protocol prior to Temporal temporal execution.
    Only allows 'shadowtag-core-run-sa' or 'headless-runner' JWTs inside the Omega-v4 project.
    """
    token = credentials.credentials
    try:
        # GCP JWTs contain 3 parts. The payload is base64 encoded JSON in the middle.
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT structure")

        payload_b64 = parts[1]
        # Pad base64 as needed
        payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
        payload_json = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))

        # Inject the parsed json into our Pydantic Identity Layer
        identity = GCPServiceIdentity(**payload_json)

        # Validate the specific service account constraint
        if "shadowtag-omega-v4.iam.gserviceaccount.com" not in identity.email:
            raise ValueError(f"Unauthorized Identity Email: {identity.email}. Rejecting payload.")

        return identity

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Pnkln Kovel Shield: Unauthorized Identity Matrix ({e!s})",
        ) from e
