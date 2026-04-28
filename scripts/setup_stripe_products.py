# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

import json
import os

import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_products():
    products_data = [
        {
            "name": "Cor2.0 Pro",
            "description": "Unlimited queries with RoT optimization",
            "price": 2000,
            "interval": "month",
        },
        {
            "name": "Cor2.0 Math Auditor",
            "description": "100% accuracy on risk calculations",
            "price": 4900,
            "interval": "month",
        },
    ]

    created = []
    for p in products_data:
        product = stripe.Product.create(name=p["name"], description=p["description"])
        price = stripe.Price.create(
            product=product.id,
            unit_amount=p["price"],
            currency="usd",
            recurring={"interval": p["interval"]},
        )
        created.append({"product_id": product.id, "price_id": price.id, "name": p["name"]})

    with open("stripe_products.json", "w") as f:
        json.dump(created, f, indent=2)

    return created


if __name__ == "__main__":
    products = create_products()
    for p in products:
        env_key = p["name"].upper().replace(" ", "_").replace("COR2.0_", "")
