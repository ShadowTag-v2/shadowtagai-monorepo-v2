# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
from typing import List, Dict


class ProductLayer:
    def __init__(
        self,
        layer_id: int,
        name: str,
        description: str,
        pricing_monthly: str,
        valuation_premium: str,
        required_frameworks: list[str],
        included_in_base: bool,
        ast_rewrite_enabled: bool = False,
    ):
        self.layer_id = layer_id
        self.name = name
        self.description = description
        self.pricing_monthly = pricing_monthly
        self.valuation_premium = valuation_premium
        self.required_frameworks = required_frameworks
        self.included_in_base = included_in_base
        self.ast_rewrite_enabled = ast_rewrite_enabled


class ProductMatrix:
    def __init__(self):
        self.layers: dict[str, ProductLayer] = {}

        # New York RAISE Act Shield Framework
        self.layers["LAYER_25"] = ProductLayer(
            layer_id=25,
            name="New York RAISE Act Shield (2027)",
            description="Frontier-model safety protocols, 72-hour incident reporting, chatbot UPL disclosure mandate, bias audits, NYSHRL disparate-impact protection. Avoids $1M–$3M penalties + federal preemption risk.",
            pricing_monthly="$65,000–$85,000/yr premium tier (or +$2,500–$4,000/mo)",
            valuation_premium="+35–50% (New York market access + liability immunity)",
            required_frameworks=["NY_RAISE_ACT_2027"],
            included_in_base=False,
            ast_rewrite_enabled=True,
        )

    def get_active_layers(self, subscribed_tiers: list[str]) -> list[ProductLayer]:
        return [self.layers[t] for t in subscribed_tiers if t in self.layers]


product_matrix = ProductMatrix()
