# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
State for the chatbot
"""

from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


# Define the state for the chatbot
class State(TypedDict):
    # Message storage
    messages: Annotated[list[BaseMessage], add_messages]

    # Current product information
    category_type: str | None  # Product category
    product_type: str | None  # Product type
    product_brand: str | None  # Product brand
    product_rating: float | None  # Product rating
    product_review: int | None  # Number of product reviews
    product_price: float | None  # Product price

    # Shopping cart
    cart_items: list[dict[str, Any]]  # List of items in the cart

    # Transaction status
    finished: bool | None  # Whether the transaction is complete
