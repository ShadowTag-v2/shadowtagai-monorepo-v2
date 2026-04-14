import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "redacted@shadowtag-v4.local"
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    # First, register the user
    await async_client.post(
        "/api/v1/auth/register", json={"email": "redacted@shadowtag-v4.local", "password": "pass"},
    )
    # Attempt duplicate
    response = await async_client.post(
        "/api/v1/auth/register", json={"email": "redacted@shadowtag-v4.local", "password": "pass"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    # Register
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )
    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(async_client: AsyncClient):
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "redacted@shadowtag-v4.local", "password": "[VAPORIZED_PWD]"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_protected_route_dependency(async_client: AsyncClient):
    from fastapi import Depends

    from src.main import app
    from src.security import get_current_user

    # Add a temporary test route
    @app.get("/api/v1/test_protected")
    async def protected_route(user=Depends(get_current_user)):
        return {"user_email": getattr(user, "email", "unknown")}

    # Register & Login to get token
    await async_client.post(
        "/api/v1/auth/register", json={"email": "redacted@shadowtag-v4.local", "password": "pass"},
    )
    login_response = await async_client.post(
        "/api/v1/auth/login", data={"username": "redacted@shadowtag-v4.local", "password": "pass"},
    )
    token = login_response.json()["access_token"]

    # Test without token
    reject_response = await async_client.get("/api/v1/test_protected")
    assert reject_response.status_code == 401

    # Test with token
    success_response = await async_client.get(
        "/api/v1/test_protected", headers={"Authorization": f"Bearer {token}"},
    )
    assert success_response.status_code == 200
    assert success_response.json()["user_email"] == "redacted@shadowtag-v4.local"
