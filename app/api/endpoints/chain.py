# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Receipt Chain Endpoints

API endpoints for managing and querying receipt chains.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path

from shadowtag_v2.receipt_chain import ChainStorage, ChainVerifier
from app.core.config import settings
from app.api.schemas.chain import ChainSummary, ReceiptDetail, VerificationResult

router = APIRouter()


@router.get("/list", response_model=list[ChainSummary])
async def list_chains():
    """
    List all receipt chains.

    Returns:
        List of chain summaries
    """
    storage = ChainStorage(Path(settings.CHAIN_DB_PATH))
    chains = storage.list_chains()
    storage.close()

    return [ChainSummary(**chain) for chain in chains]


@router.get("/{chain_id}")
async def get_chain(chain_id: str):
    """
    Get detailed information about a specific chain.

    Args:
        chain_id: Chain identifier

    Returns:
        Chain summary and statistics
    """
    storage = ChainStorage(Path(settings.CHAIN_DB_PATH))
    chain = storage.load_chain(chain_id)
    storage.close()

    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    return chain.get_chain_summary()


@router.get("/{chain_id}/verify", response_model=VerificationResult)
async def verify_chain(chain_id: str):
    """
    Verify the cryptographic integrity of a chain.

    Args:
        chain_id: Chain identifier

    Returns:
        Verification result with details
    """
    storage = ChainStorage(Path(settings.CHAIN_DB_PATH))
    chain = storage.load_chain(chain_id)
    storage.close()

    if not chain:
        raise HTTPException(status_code=404, detail="Chain not found")

    verifier = ChainVerifier()
    result = verifier.verify_chain(chain)

    return VerificationResult(is_valid=result.is_valid, errors=result.errors, warnings=result.warnings, details=result.details)


@router.get("/receipt/{operation_id}", response_model=ReceiptDetail)
async def get_receipt(operation_id: str):
    """
    Get a specific receipt by operation ID.

    Args:
        operation_id: Operation identifier

    Returns:
        Receipt details
    """
    storage = ChainStorage(Path(settings.CHAIN_DB_PATH))
    receipts = storage.search_receipts(operation_id=operation_id)
    storage.close()

    if not receipts:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return ReceiptDetail(**receipts[0])


@router.get("/search")
async def search_receipts(
    operation_type: str | None = None,
    media_type: str | None = None,
    payload_hash: str | None = None,
):
    """
    Search for receipts matching criteria.

    Args:
        operation_type: Filter by operation type
        media_type: Filter by media type
        payload_hash: Filter by payload hash

    Returns:
        List of matching receipts
    """
    storage = ChainStorage(Path(settings.CHAIN_DB_PATH))
    receipts = storage.search_receipts(
        operation_type=operation_type,
        media_type=media_type,
        payload_hash=payload_hash,
    )
    storage.close()

    return receipts
