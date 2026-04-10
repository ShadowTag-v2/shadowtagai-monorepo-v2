from libs.monetization.pricing_matrix import SubscriptionTier


class EntitlementManager:
    """
    The Gatekeeper.
    Determines which layers of the 'Onion' are accessible based on Payment Tier.
    Supports Admin Overrides (Severability).
    """

    def __init__(self):
        self._admin_overrides = {}

    def get_enabled_features(self, tier: str) -> list[str]:
        # Parse enum string back to object if needed, or handle string directly
        try:
            tier_enum = SubscriptionTier(tier)
        except ValueError:
            tier_enum = SubscriptionTier.BASIC

        # BASE FEATURES (Tier 1: Basic Defense)
        features = [
            "CORE_DEFENSE",
            "SILENCER",
            "TROOP_B",
            "LAYER_14_INFRA_OPTIMIZER",
            "LAYER_15_SUPPLY_CHAIN_SEC",
            "LAYER_16_PRODUCT_GATE",
            "LAYER_18_COMPETITIVE_CHECK",
            "LAYER_19_MILESTONE_TRACKER",
        ]

        # EU COMPLIANCE (Tier 2: +30%)
        if tier_enum in [
            SubscriptionTier.EU_COMPLIANCE,
            SubscriptionTier.FINANCIAL,
            SubscriptionTier.SOVEREIGN,
        ]:
            features.append("EU_26_GDPR")
            features.append("PRIVACY_SHIELD")
            features.append("LAYER_12_REGULATORY_MATRIX")
            features.append("LAYER_13_ADTECH_STANDARDS")

        # FINANCIAL LAYER (Tier 3: Dynamic)
        if tier_enum in [SubscriptionTier.FINANCIAL, SubscriptionTier.SOVEREIGN]:
            features.append("FIN_CRIMES_MODULE")
            features.append("MONTE_CARLO_RISK")
            features.append("ACTIVE_DEFENSE_METRICS")
            features.append("LAYER_17_BLOCKCHAIN_GATE")
            features.append("LAYER_20_IMPACT_MODEL")

        # SOVEREIGN (Tier 30: $1M)
        if tier_enum == SubscriptionTier.SOVEREIGN:
            features.append("SOVEREIGN_RIGHTS")
            features.append("ZERO_KNOWLEDGE")
            features.append("BRAKE_OVERRIDE")
            features.append("LAYER_21_IQ_160_LOCK")

        # Apply Admin Overrides (The "Toggle")
        for feat, enabled in self._admin_overrides.items():
            if enabled and feat not in features:
                features.append(feat)
            elif not enabled and feat in features:
                features.remove(feat)

        return features

    def admin_override(self, feature: str, enable: bool):
        """
        Severability Switch.
        Allows Admin to turn specific layers ON/OFF regardless of tier.
        """
        print(f"   🔧 ADMIN OVERRIDE: {feature} -> {enable}")
        self._admin_overrides[feature] = enable

    def check_access(self, tier: str, required_feature: str) -> bool:
        features = self.get_enabled_features(tier)
        return required_feature in features
