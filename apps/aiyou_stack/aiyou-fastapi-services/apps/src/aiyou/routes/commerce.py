"""Commerce Mall API Routes.

Handles product catalog, cart, and checkout.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models.commerce import Cart, Order, OrderItem, Product
from ..models.user import User

router = APIRouter(prefix="/commerce", tags=["commerce"])


class ProductResponse(BaseModel):
    id: str
    name: str
    price_cents: int
    description: str
    image_urls: list[str]


class CartItem(BaseModel):
    product_id: str
    quantity: int


class CheckoutRequest(BaseModel):
    payment_method: str
    shipping_address: dict


@router.get("/products", response_model=list[ProductResponse])
async def list_products(
    category: str = None,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
):
    """List products with optional filtering."""
    query = db.query(Product).filter(Product.is_active)
    if category:
        query = query.filter(Product.category == category)

    products = query.offset(skip).limit(limit).all()
    # Pydantic will handle serialization via ORM mode (configure in Pydantic model v2 or explicit dict)
    # For now returning simple dict list
    return [
        {
            "id": p.id,
            "name": p.name,
            "price_cents": p.price_cents,
            "description": str(p.description),
            "image_urls": p.image_urls or [],
        }
        for p in products
    ]


@router.post("/cart", status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item: CartItem,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add item to user cart."""
    # Find or create cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)

    # Logic to add/update item in cart.items JSON
    # Simplified: just append for now. Production needs proper merging.
    current_items = list(cart.items) if cart.items else []
    current_items.append(item.dict())
    cart.items = current_items

    db.commit()
    return {"status": "added", "cart_id": cart.id}


@router.post("/checkout")
async def checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process checkout."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Calculate total
    total_cents = 0
    order_items = []

    for item in cart.items:
        prod = db.query(Product).filter(Product.id == item["product_id"]).first()
        if prod:
            subtotal = prod.price_cents * item["quantity"]
            total_cents += subtotal
            order_items.append(
                OrderItem(
                    product_id=prod.id,
                    quantity=item["quantity"],
                    price_cents=prod.price_cents,
                    subtotal_cents=subtotal,
                ),
            )

    # Create Order
    order = Order(
        user_id=current_user.id,
        total_cents=total_cents,
        subtotal_cents=total_cents,  # simplified
        shipping_address=request.shipping_address,
        payment_method=request.payment_method,
    )
    db.add(order)
    db.flush()  # get ID

    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    # Clear cart
    cart.items = []

    db.commit()
    return {"order_id": order.id, "status": "processing"}
