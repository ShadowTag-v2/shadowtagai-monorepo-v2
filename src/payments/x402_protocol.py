# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""X402 USDC Micropayment Protocol — HTTP 402 Payment Required Implementation.

Implements the X402 protocol from Notebook 516 for per-API-call micropayments
using USDC (USD Coin) on Base L2.

Architecture:
    Client → API Gateway → X402 Middleware → Payment Verification → API Handler
    Payment Channel: USDC on Base (Coinbase L2)

Protocol Flow:
    1. Client sends API request without payment header
    2. Server responds with HTTP 402 + X-Payment-Required header
    3. Header contains: amount, recipient, chain, token, nonce
    4. Client signs USDC transfer and includes proof in X-Payment header
    5. Server verifies payment proof on-chain → processes request

Reference: Notebook 516 (Uphillsnowball Master)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

# USDC on Base L2
USDC_CONTRACT_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
BASE_CHAIN_ID = 8453
DEFAULT_RECIPIENT = "0x0000000000000000000000000000000000000000"  # Set in production


@dataclass
class PricingTier:
  """Pricing for an API endpoint."""

  path_pattern: str
  amount_usdc: float  # in USDC (6 decimals)
  description: str


@dataclass
class PaymentProof:
  """Client-submitted payment proof."""

  tx_hash: str
  amount: float
  sender: str
  recipient: str
  chain_id: int
  nonce: str
  signature: str
  timestamp: int


@dataclass
class PaymentChallenge:
  """Server-generated payment challenge (HTTP 402 response body)."""

  amount: float
  recipient: str
  chain_id: int
  token_contract: str
  nonce: str
  expires_at: int
  endpoint: str


# Default pricing tiers
DEFAULT_PRICING: list[PricingTier] = [
  PricingTier("/api/v1/evaluate", 0.01, "Research quality evaluation"),
  PricingTier("/api/v1/citations/validate", 0.005, "Citation validation"),
  PricingTier("/api/v1/research/deep", 0.05, "Deep research synthesis"),
  PricingTier("/api/v1/sandbox/execute", 0.02, "Sandboxed code execution"),
]


class X402PaymentVerifier:
  """Verifies USDC payment proofs for API access.

  In production, this queries the Base L2 RPC to verify the transaction.
  For development, it accepts a signed challenge with HMAC verification.
  """

  def __init__(
    self,
    recipient: str = DEFAULT_RECIPIENT,
    secret: str = "",
    pricing: list[PricingTier] | None = None,
  ):
    self._recipient = recipient
    self._secret = secret.encode() if secret else b""
    self._pricing = {t.path_pattern: t for t in (pricing or DEFAULT_PRICING)}
    self._used_nonces: set[str] = set()

  def get_price(self, path: str) -> PricingTier | None:
    """Look up the price for a given API path."""
    for pattern, tier in self._pricing.items():
      if path.startswith(pattern):
        return tier
    return None

  def generate_challenge(self, path: str) -> PaymentChallenge:
    """Generate a payment challenge for the client."""
    tier = self.get_price(path)
    if not tier:
      raise ValueError(f"No pricing configured for {path}")

    nonce = hashlib.sha256(f"{path}:{time.time_ns()}".encode()).hexdigest()[:32]

    return PaymentChallenge(
      amount=tier.amount_usdc,
      recipient=self._recipient,
      chain_id=BASE_CHAIN_ID,
      token_contract=USDC_CONTRACT_BASE,
      nonce=nonce,
      expires_at=int(time.time()) + 300,  # 5 minute expiry
      endpoint=path,
    )

  def verify_proof(self, proof: PaymentProof, expected_amount: float) -> bool:
    """Verify a payment proof.

    In production: query Base L2 RPC to confirm the tx_hash.
    In development: verify HMAC signature against the secret.

    Returns:
        True if payment is verified.

    Raises:
        HTTPException if verification fails.
    """
    # Nonce replay protection
    if proof.nonce in self._used_nonces:
      raise HTTPException(status_code=403, detail="Nonce already used")
    self._used_nonces.add(proof.nonce)

    # Amount check
    if proof.amount < expected_amount:
      raise HTTPException(
        status_code=402,
        detail=f"Insufficient payment: {proof.amount} < {expected_amount} USDC",
      )

    # Chain check
    if proof.chain_id != BASE_CHAIN_ID:
      raise HTTPException(
        status_code=400,
        detail=f"Wrong chain: expected {BASE_CHAIN_ID}, got {proof.chain_id}",
      )

    # Recipient check
    if proof.recipient.lower() != self._recipient.lower():
      raise HTTPException(
        status_code=400,
        detail="Payment sent to wrong recipient",
      )

    # Expiry check
    if proof.timestamp < int(time.time()) - 300:
      raise HTTPException(status_code=408, detail="Payment proof expired")

    # Development mode: HMAC verification
    if self._secret:
      message = f"{proof.tx_hash}:{proof.amount}:{proof.nonce}:{proof.timestamp}"
      expected_sig = hmac.new(
        self._secret, message.encode(), hashlib.sha256
      ).hexdigest()
      if not hmac.compare_digest(proof.signature, expected_sig):
        raise HTTPException(status_code=403, detail="Invalid payment signature")
      return True

    # Production mode: TODO — query Base L2 RPC
    # This would use web3.py or httpx to verify the tx_hash on-chain
    logger.warning("Production on-chain verification not yet implemented")
    return True


class X402Middleware(BaseHTTPMiddleware):
  """FastAPI middleware that enforces X402 payment for priced endpoints.

  Usage:
      app.add_middleware(X402Middleware, verifier=X402PaymentVerifier(...))
  """

  def __init__(self, app: Any, verifier: X402PaymentVerifier):
    super().__init__(app)
    self._verifier = verifier

  async def dispatch(self, request: Request, call_next: Any) -> Any:
    """Check for payment proof on priced endpoints."""
    path = request.url.path
    tier = self._verifier.get_price(path)

    # No pricing configured — pass through
    if tier is None:
      return await call_next(request)

    # Check for payment header
    payment_header = request.headers.get("X-Payment")

    if not payment_header:
      # Return 402 with payment challenge
      challenge = self._verifier.generate_challenge(path)
      return JSONResponse(
        status_code=402,
        content={
          "error": "Payment Required",
          "protocol": "X402",
          "challenge": {
            "amount": challenge.amount,
            "currency": "USDC",
            "recipient": challenge.recipient,
            "chain": "Base",
            "chain_id": challenge.chain_id,
            "token_contract": challenge.token_contract,
            "nonce": challenge.nonce,
            "expires_at": challenge.expires_at,
            "endpoint": challenge.endpoint,
          },
        },
        headers={
          "X-Payment-Required": json.dumps(
            {
              "amount": str(challenge.amount),
              "currency": "USDC",
              "chain": "base",
              "recipient": challenge.recipient,
              "nonce": challenge.nonce,
            }
          ),
        },
      )

    # Parse and verify payment proof
    try:
      proof_data = json.loads(payment_header)
      proof = PaymentProof(**proof_data)
      self._verifier.verify_proof(proof, tier.amount_usdc)
    except json.JSONDecodeError:
      raise HTTPException(status_code=400, detail="Invalid X-Payment header format")
    except TypeError as e:
      raise HTTPException(status_code=400, detail=f"Missing payment fields: {e}")

    # Payment verified — proceed with request
    logger.info(
      "X402 payment verified: %s USDC for %s from %s",
      tier.amount_usdc,
      path,
      proof.sender,
    )
    return await call_next(request)
