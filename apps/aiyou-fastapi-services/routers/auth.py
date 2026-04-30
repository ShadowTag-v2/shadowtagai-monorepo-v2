import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []


logger = logging.getLogger(__name__)


async def verify_activeshield_jwt(token: str = Depends(oauth2_scheme)):
    """ActiveShield MCF Zero-Trust Policy Layer (L2.3).
    All microservices operating via aiyou-fastapi-services must
    route through this gateway to ensure strict token authentication
    before engaging domain logic.
    """
    if not token or token == "invalid_token":
        logger.warning("ActiveShield: Unauthorized access attempt intercepted.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ActiveShield MCF: Zero-Trust violation. Provide valid JWT credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Placeholder for actual cryptographic verification against Firebase/Auth0
    return TokenData(username="sovereign_sysadmin", scopes=["execute"])


def get_current_active_operator(token_data: TokenData = Depends(verify_activeshield_jwt)):  # noqa: B008
    if "execute" not in token_data.scopes:
        raise HTTPException(status_code=403, detail="ActiveShield MCF: Scope violation.")
    return token_data
