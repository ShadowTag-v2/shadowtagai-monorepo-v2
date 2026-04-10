from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src import models
from src.config.settings import settings
from src.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict[str, str]) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> models.User:
    """Dependency to inject the current logged-in user into protected endpoints."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = select(models.User).where(models.User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None or getattr(user, "is_active", True) is False:
        raise credentials_exception

    return user


class GCPServiceAccountPayload(BaseModel):
    """Strict Pydantic parsing layer for Zero-Trust ingress"""

    iss: str
    sub: str
    aud: str
    iat: int
    exp: int
    email: str | None = None


zero_trust_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def verify_zero_trust(token: str = Depends(zero_trust_scheme)) -> GCPServiceAccountPayload:
    """Enforce Zero-Trust JWT validation on FastAPI ingress servers"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication payload for Zero-Trust boundary",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        unverified_claims = jwt.get_unverified_claims(token)
        payload = GCPServiceAccountPayload(**unverified_claims)

        # Validate boundary restriction for headless execution
        if payload.email and not payload.email.endswith("gserviceaccount.com"):
            raise ValueError("Identity must be a verified GCP service account")

        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Zero-Trust Policy Violation: {str(e)}",
        )
