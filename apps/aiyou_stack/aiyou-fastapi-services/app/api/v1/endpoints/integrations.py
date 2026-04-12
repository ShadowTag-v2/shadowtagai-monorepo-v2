"""Integration endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import get_current_user
from app.models.integration import IntegrationStatus
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationCredentialCreate,
    IntegrationCredentialResponse,
    IntegrationResponse,
    IntegrationTestRequest,
    IntegrationTestResponse,
    IntegrationUpdate,
    OAuthCallbackRequest,
    OAuthInitiateResponse,
)
from app.services.integration_service import IntegrationService
from app.services.oauth_service import OAuthService

router = APIRouter()


@router.post("", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def create_integration(
    integration_data: IntegrationCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new integration"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    integration = service.create_integration(user_id, integration_data)
    return integration


@router.get("", response_model=list[IntegrationResponse])
def list_integrations(
    provider: str | None = Query(None),
    status_filter: IntegrationStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user integrations"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    integrations = service.list_integrations(
        user_id=user_id, provider=provider, status=status_filter, skip=skip, limit=limit
    )
    return integrations


@router.get("/{integration_id}", response_model=IntegrationResponse)
def get_integration(
    integration_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get integration by ID"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    integration = service.get_integration(integration_id, user_id)

    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")

    return integration


@router.put("/{integration_id}", response_model=IntegrationResponse)
def update_integration(
    integration_id: int,
    integration_data: IntegrationUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update integration"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    integration = service.update_integration(integration_id, user_id, integration_data)

    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")

    return integration


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_integration(
    integration_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete integration"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    success = service.delete_integration(integration_id, user_id)

    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")

    return None


@router.post("/{integration_id}/credentials", response_model=IntegrationCredentialResponse)
def add_credentials(
    integration_id: int,
    credentials: IntegrationCredentialCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add or update integration credentials"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    credential = service.add_credentials(integration_id, user_id, credentials)

    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")

    return credential


@router.get("/{integration_id}/credentials", response_model=IntegrationCredentialResponse)
def get_credentials(
    integration_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get integration credentials (without sensitive data)"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    credential = service.get_credentials(integration_id, user_id)

    if not credential:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credentials not found")

    return credential


@router.post("/{integration_id}/test", response_model=IntegrationTestResponse)
async def test_integration(
    integration_id: int,
    test_request: IntegrationTestRequest | None = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Test integration connection"""
    user_id = int(current_user.get("sub"))
    service = IntegrationService(db)
    result = await service.test_integration(integration_id, user_id, test_request)
    return result


@router.post("/{integration_id}/oauth/initiate", response_model=OAuthInitiateResponse)
def initiate_oauth(
    integration_id: int,
    redirect_uri: str = Query(..., description="OAuth redirect URI"),
    scope: str | None = Query(None, description="OAuth scope"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Initiate OAuth flow for integration"""
    user_id = int(current_user.get("sub"))

    # Get integration
    service = IntegrationService(db)
    integration = service.get_integration(integration_id, user_id)

    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found")

    # Initiate OAuth
    oauth_service = OAuthService(db)
    result = oauth_service.initiate_oauth_flow(
        provider=integration.provider,
        integration_id=integration_id,
        redirect_uri=redirect_uri,
        scope=scope,
    )

    return result


@router.post("/{integration_id}/oauth/callback", response_model=IntegrationResponse)
async def oauth_callback(
    integration_id: int,
    callback_data: OAuthCallbackRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Handle OAuth callback"""
    user_id = int(current_user.get("sub"))

    oauth_service = OAuthService(db)
    integration = await oauth_service.handle_oauth_callback(
        code=callback_data.code, state=callback_data.state, user_id=user_id
    )

    if not integration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth callback failed")

    return integration


@router.post("/{integration_id}/oauth/refresh", response_model=IntegrationCredentialResponse)
async def refresh_oauth_token(
    integration_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Refresh OAuth access token"""
    user_id = int(current_user.get("sub"))

    oauth_service = OAuthService(db)
    credential = await oauth_service.refresh_access_token(integration_id, user_id)

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to refresh token"
        )

    return credential
