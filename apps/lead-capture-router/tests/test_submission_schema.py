# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import httpx
import pytest

# Assumes the firebase emulator is running locally
EMULATOR_URL = "http://127.0.0.1:5001/shadowtag-omega-v4/us-central1/captureLead"


@pytest.mark.asyncio
async def test_valid_submission():
    payload = {
        "name": "John Doe",
        "email": "john@doe.com",
        "company": "ShadowTag",
        "message": "This is a strictly compliant message over 10 characters.",
        "leadSource": "kovelai_landing",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(EMULATOR_URL, json=payload)
    # Testing for the success response
    assert response.status_code == 200
    assert response.json().get("success") is True


@pytest.mark.asyncio
async def test_invalid_email_boundary():
    payload = {
        "name": "Jane Doe",
        "email": "not-an-email",
        "message": "This is another valid message.",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(EMULATOR_URL, json=payload)
    assert response.status_code == 400
    details = response.json().get("details", [])
    assert any("Invalid email" in str(d) for d in details)


@pytest.mark.asyncio
async def test_short_name_boundary():
    payload = {
        "name": "A",  # Under 2 chars
        "email": "valid@email.com",
        "message": "This is another valid message.",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(EMULATOR_URL, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_short_message_boundary():
    payload = {
        "name": "Jane Doe",
        "email": "valid@email.com",
        "message": "Too short",  # Under 10 chars
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(EMULATOR_URL, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_missing_required_fields():
    payload = {
        "company": "Only company provided",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(EMULATOR_URL, json=payload)
    assert response.status_code == 400
