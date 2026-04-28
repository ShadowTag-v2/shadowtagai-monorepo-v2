# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import time

import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_session():
    """Creates and configures a requests.Session with retry logic."""
    session = requests.Session()
    retry = Retry(connect=5, read=5, backoff_factor=1.0, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session


def get_github_app_token(client_id, pem_path, owner_name):
    """Generates a JWT, fetches GitHub App installations, finds the correct installation ID,
    and then creates an installation access token.
    """
    try:
        with open(pem_path, "rb") as f:
            pem_data = f.read()
    except FileNotFoundError:
        return None

    iat = int(time.time()) - 60
    exp = iat + (10 * 60)
    payload = {"iat": iat, "exp": exp, "iss": str(client_id)}
    encoded_jwt = jwt.encode(payload, pem_data, algorithm="RS256")

    headers = {"Authorization": f"Bearer {encoded_jwt}", "Accept": "application/vnd.github.v3+json"}
    session = get_session()

    try:
        resp = session.get("https://api.github.com/app/installations", headers=headers, timeout=30)
        resp.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.RequestException:
        return None

    installations = resp.json()
    target_installation_id = None
    for inst in installations:
        if inst.get("account", {}).get("login", "").lower() == owner_name.lower():
            target_installation_id = inst.get("id")
            break

    if not target_installation_id and installations:
        target_installation_id = installations[0].get("id")

    if not target_installation_id:
        return None

    token_url = f"https://api.github.com/app/installations/{target_installation_id}/access_tokens"
    try:
        resp = session.post(token_url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json().get("token")
    except requests.exceptions.RequestException:
        return None
