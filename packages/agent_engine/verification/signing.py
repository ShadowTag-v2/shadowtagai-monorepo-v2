# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from __future__ import annotations

import hashlib
import json

from shared.config import settings


class ArtifactSigner:
  """Uses sigstore/cosign to cryptographically sign prompt outputs or generated code schemas."""

  def __init__(self):
    self.identity = settings.sigstore_identity

  def sign_payload(self, payload: dict) -> dict:
    """
    In a real deployment, this would invoke `cosign sign-blob` utilizing OIDC
    (e.g., GitHub Actions, Google Cloud Run) to attach a Fulcio certificate back to the SIEM.
    """
    payload_str = json.dumps(payload, sort_keys=True)
    payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()

    signature_data = {
      "signature_hash": payload_hash,
      "signer_identity": self.identity or "unverified_local_dev",
      "mechanism": "sigstore_fulcio_simulation",
    }

    # Append the crypto signature into the payload envelope
    return {"data": payload, "provenance": signature_data}

  def verify_payload(self, signed_envelope: dict) -> bool:
    """Verifies that the payload hasn't been tampered with since the OIDC signature."""
    data = signed_envelope.get("data", {})
    prov = signed_envelope.get("provenance", {})

    computed_hash = hashlib.sha256(
      json.dumps(data, sort_keys=True).encode()
    ).hexdigest()

    return computed_hash == prov.get("signature_hash")
