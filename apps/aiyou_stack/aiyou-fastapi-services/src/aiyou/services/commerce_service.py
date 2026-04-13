"""
Commerce service layer.

Extracts all database operations from commerce routes
into a proper service/repository pattern.
"""

from sqlalchemy.orm import Session

from ..models.commerce import Cart, Order, OrderItem, Product


class CommerceService:
    """Service layer for commerce operations."""

    @staticmethod
    def list_products(
        db: Session, category: str | None = None, skip: int = 0, limit: int = 50
    ) -> list[dict]:
        """List active products with optional category filtering."""
        query = db.query(Product).filter(Product.is_active)
        if category:
            query = query.filter(Product.category == category)

        products = query.offset(skip).limit(limit).all()
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

    @staticmethod
    def get_or_create_cart(db: Session, user_id: str) -> Cart:
        """Get existing cart or create a new one for the user."""
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
        return cart

    @staticmethod
    def add_to_cart(db: Session, user_id: str, product_id: str, quantity: int) -> dict:
        """Add item to user cart."""
        cart = CommerceService.get_or_create_cart(db, user_id)

        current_items = list(cart.items) if cart.items else []
        current_items.append({"product_id": product_id, "quantity": quantity})
        cart.items = current_items

        db.commit()
        return {"status": "added", "cart_id": cart.id}

    @staticmethod
    def checkout(
        db: Session,
        user_id: str,
        payment_method: str,
        shipping_address: dict,
    ) -> dict:
        """Process checkout for a user's cart."""
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart or not cart.items:
            raise ValueError("Cart is empty")

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
                    )
                )

        order = Order(
            user_id=user_id,
            total_cents=total_cents,
            subtotal_cents=total_cents,
            shipping_address=shipping_address,
            payment_method=payment_method,
        )
        db.add(order)
        db.flush()

        for oi in order_items:
            oi.order_id = order.id
            db.add(oi)

        cart.items = []
        db.commit()

        return {"order_id": order.id, "status": "processing"}
