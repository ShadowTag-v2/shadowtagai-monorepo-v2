"""X402 Protocol — USDC Micropayment Enforcement Middleware

Implements HTTP 402 Payment Required challenge/response protocol
for priced CounselConduit endpoints (ScholarEval, premium queries).

Protocol Flow:
    1. Client requests priced endpoint without X-Payment header
    2. Server responds 402 with payment challenge JSON:
       {
         "protocol": "x402",
         "chain": "base",
         "token": "USDC",
         "amount": "0.05",
         "recipient": "0x...",
         "nonce": "<unique>"
       }
    3. Client signs USDC transfer on Base L2, submits:
       X-Payment: <base64-encoded-receipt>
    4. Server verifies receipt, allows access

Phase 3 Status: Stub implementation — accepts all payments.
Production will integrate with Base L2 RPC for on-chain verification.
"""

from __future__ import annotations

import time
from typing import Any

import structlog
from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = structlog.get_logger(__name__)

# Endpoints that require X402 payment
PRICED_ENDPOINTS: dict[str, float] = {
  "/api/v1/evaluate": 0.05,  # $0.05 USDC per evaluation
}

# Stub recipient address (Phase 3: replace with real multisig)
RECIPIENT_ADDRESS = "0x0000000000000000000000000000000000000402"


class X402PaymentVerifier:
  """Verifies X402 payment receipts.

  Phase 3 stub: accepts all payments with valid X-Payment header.
  Production: verifies USDC transfer on Base L2 via RPC.
  """

  def __init__(
    self,
    recipient: str = RECIPIENT_ADDRESS,
    secret: str = "",
  ) -> None:
    """Initialize verifier with recipient address and HMAC secret.

    Args:
      recipient: The wallet address to receive payments.
      secret: HMAC secret for receipt verification (Phase 3: unused).
    """
    self.recipient = recipient
    self.secret = secret

  async def verify(self, receipt: str, expected_amount: float) -> dict[str, Any]:
    """Verify a payment receipt.

    Returns verification result dict.
    """
    # Phase 3 stub: accept any non-empty receipt
    if not receipt or len(receipt) < 10:
      return {"valid": False, "reason": "Invalid receipt format"}

    return {
      "valid": True,
      "amount": expected_amount,
      "chain": "base",
      "token": "USDC",
      "verified_at": time.time(),
    }


class X402Middleware(BaseHTTPMiddleware):
  """Middleware enforcing X402 payment on priced endpoints."""

  def __init__(
    self,
    app: Any,
    verifier: X402PaymentVerifier | None = None,
  ) -> None:
    super().__init__(app)
    self.verifier = verifier or X402PaymentVerifier()

  async def dispatch(
    self,
    request: Request,
    call_next: RequestResponseEndpoint,
  ) -> Response:
    path = request.url.path

    # Check if this is a priced endpoint
    price = None
    for endpoint, amount in PRICED_ENDPOINTS.items():
      if path.startswith(endpoint) and request.method == "POST":
        price = amount
        break

    if price is None:
      return await call_next(request)

    # Check for X-Payment header
    payment_header = request.headers.get("X-Payment")
    if not payment_header:
      # Return 402 challenge
      return JSONResponse(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        content={
          "protocol": "x402",
          "chain": "base",
          "token": "USDC",
          "amount": str(price),
          "recipient": self.verifier.recipient,
          "nonce": f"x402_{int(time.time())}",
          "message": "Payment required. Submit X-Payment header with signed USDC receipt.",
        },
      )

    # Verify payment
    result = await self.verifier.verify(payment_header, price)

    if not result["valid"]:
      raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail=f"Payment verification failed: {result.get('reason', 'unknown')}",
      )

    logger.info(
      "x402_payment_verified",
      path=path,
      amount=price,
    )

    return await call_next(request)
