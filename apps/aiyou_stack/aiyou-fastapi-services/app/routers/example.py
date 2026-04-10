"""
Example API endpoints demonstrating monitoring integration.
"""

import asyncio
import random

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.monitoring.logger import get_logger
from app.monitoring.metrics import MetricsCollector

router = APIRouter(prefix="/api/v1", tags=["examples"])
logger = get_logger(__name__)


class Item(BaseModel):
    """Example item model."""

    name: str
    description: str = ""
    price: float


@router.get("/items", summary="List Items")
async def list_items():
    """Example endpoint to list items."""
    logger.info("Listing items")

    items = [
        {"id": 1, "name": "Item 1", "price": 10.99},
        {"id": 2, "name": "Item 2", "price": 20.99},
    ]

    return {"items": items, "total": len(items)}


@router.post("/items", summary="Create Item")
async def create_item(item: Item):
    """Example endpoint to create an item."""
    logger.info("Creating item", item_name=item.name, price=item.price)

    # Simulate business operation
    MetricsCollector.record_business_operation(
        operation_type="item_creation", status="success", duration=0.1
    )

    return {
        "id": random.randint(1000, 9999),
        "name": item.name,
        "description": item.description,
        "price": item.price,
    }


@router.get("/items/{item_id}", summary="Get Item")
async def get_item(item_id: int):
    """Example endpoint to get a specific item."""
    logger.info("Getting item", item_id=item_id)

    # Simulate not found scenario
    if item_id > 100:
        logger.warning("Item not found", item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    return {"id": item_id, "name": f"Item {item_id}", "price": random.uniform(10, 100)}


@router.get("/slow-endpoint", summary="Slow Endpoint (Testing)")
async def slow_endpoint():
    """
    Intentionally slow endpoint for testing monitoring and alerts.
    This will trigger slow request alerts.
    """
    logger.info("Processing slow endpoint")

    # Simulate slow processing
    await asyncio.sleep(6)  # 6 seconds - exceeds 5s threshold

    return {"message": "This was slow!", "duration_seconds": 6}


@router.get("/error-endpoint", summary="Error Endpoint (Testing)")
async def error_endpoint():
    """
    Intentionally failing endpoint for testing error tracking.
    This will trigger error alerts.
    """
    logger.error("Simulating error")

    # Record failed business operation
    MetricsCollector.record_business_operation(operation_type="error_test", status="failure")

    raise HTTPException(status_code=500, detail="Simulated server error")
