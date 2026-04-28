# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tools for Market Analyst Agent"""

from datetime import datetime


class CompetitiveAnalysisTools:
    """Tools for competitive analysis and market research"""

    @staticmethod
    def create_feature_matrix(product: str, competitors: list[str], features: list[str]) -> dict:
        """Create a feature comparison matrix

        Args:
            product: Your product name
            competitors: List of competitor names
            features: List of features to compare

        Returns:
            Dictionary with matrix structure

        """
        matrix = {
            "product": product,
            "competitors": competitors,
            "features": features,
            "timestamp": datetime.utcnow().isoformat(),
            "comparison": {},
        }

        # Initialize empty comparison grid
        for feature in features:
            matrix["comparison"][feature] = {product: None, **dict.fromkeys(competitors)}

        return matrix

    @staticmethod
    def calculate_feature_coverage(feature_matrix: dict) -> dict:
        """Calculate feature coverage statistics

        Args:
            feature_matrix: Feature comparison matrix

        Returns:
            Coverage statistics

        """
        total_features = len(feature_matrix.get("features", []))
        product = feature_matrix.get("product", "Unknown")
        competitors = feature_matrix.get("competitors", [])

        stats = {"total_features": total_features, "coverage": {}}

        # Calculate coverage for product and each competitor
        for entity in [product] + competitors:
            has_features = 0
            for feature_data in feature_matrix.get("comparison", {}).values():
                if feature_data.get(entity):
                    has_features += 1

            stats["coverage"][entity] = {
                "count": has_features,
                "percentage": (has_features / total_features * 100) if total_features > 0 else 0,
            }

        return stats

    @staticmethod
    def identify_gaps(feature_matrix: dict, product: str) -> dict:
        """Identify feature gaps where competitors have features you don't

        Args:
            feature_matrix: Feature comparison matrix
            product: Your product name

        Returns:
            Gap analysis results

        """
        gaps = {"critical_gaps": [], "parity_gaps": [], "unique_features": []}

        comparison = feature_matrix.get("comparison", {})
        competitors = feature_matrix.get("competitors", [])

        for feature, data in comparison.items():
            has_feature = data.get(product, False)
            competitors_with_feature = [comp for comp in competitors if data.get(comp, False)]

            if not has_feature and competitors_with_feature:
                gap_info = {
                    "feature": feature,
                    "competitors_with_it": competitors_with_feature,
                    "coverage": len(competitors_with_feature) / len(competitors)
                    if competitors
                    else 0,
                }

                # Critical if most competitors have it
                if gap_info["coverage"] >= 0.5:
                    gaps["critical_gaps"].append(gap_info)
                else:
                    gaps["parity_gaps"].append(gap_info)

            elif has_feature and not competitors_with_feature:
                gaps["unique_features"].append({"feature": feature, "differentiator": True})

        return gaps

    @staticmethod
    def prioritize_features(features: list[dict], criteria: dict = None) -> list[dict]:
        """Prioritize features based on impact and effort

        Args:
            features: List of features with impact/effort ratings
            criteria: Custom prioritization criteria

        Returns:
            Prioritized feature list

        """
        if criteria is None:
            criteria = {"impact_weight": 0.6, "effort_weight": 0.4}

        impact_map = {"high": 3, "medium": 2, "low": 1}
        effort_map = {"low": 3, "medium": 2, "high": 1}  # Lower effort = higher score

        for feature in features:
            impact_score = impact_map.get(feature.get("impact", "").lower(), 1)
            effort_score = effort_map.get(feature.get("effort", "").lower(), 1)

            feature["priority_score"] = (
                impact_score * criteria["impact_weight"] + effort_score * criteria["effort_weight"]
            )

        # Sort by priority score (descending)
        prioritized = sorted(features, key=lambda x: x.get("priority_score", 0), reverse=True)

        # Add priority labels
        for i, feature in enumerate(prioritized):
            if i < len(prioritized) * 0.2:
                feature["priority"] = "P0"
            elif i < len(prioritized) * 0.5:
                feature["priority"] = "P1"
            else:
                feature["priority"] = "P2"

        return prioritized

    @staticmethod
    def generate_swot_matrix(
        strengths: list[str],
        weaknesses: list[str],
        opportunities: list[str],
        threats: list[str],
    ) -> dict:
        """Generate a SWOT analysis matrix

        Args:
            strengths: List of strengths
            weaknesses: List of weaknesses
            opportunities: List of opportunities
            threats: List of threats

        Returns:
            SWOT matrix dictionary

        """
        return {
            "swot_analysis": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "opportunities": opportunities,
                "threats": threats,
            },
            "strategic_insights": {
                "leverage": [
                    f"Use {s} to capitalize on {o}"
                    for s in strengths[:2]
                    for o in opportunities[:2]
                ],
                "improve": [
                    f"Address {w} to mitigate {t}" for w in weaknesses[:2] for t in threats[:2]
                ],
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


class MarketPositioningTools:
    """Tools for market positioning analysis"""

    @staticmethod
    def define_positioning_statement(
        target_market: str,
        category: str,
        unique_benefit: str,
        reason_to_believe: str,
    ) -> str:
        """Generate a positioning statement

        Args:
            target_market: Target customer segment
            category: Product category
            unique_benefit: Key differentiator
            reason_to_believe: Proof point

        Returns:
            Positioning statement

        """
        return (
            f"For {target_market} who need {category}, "
            f"our product is the solution that {unique_benefit}. "
            f"Unlike competitors, {reason_to_believe}."
        )

    @staticmethod
    def identify_unfair_advantages(capabilities: list[dict]) -> list[dict]:
        """Identify potential unfair advantages

        Args:
            capabilities: List of capabilities with attributes

        Returns:
            Ranked unfair advantages

        """
        unfair_advantages = []

        for cap in capabilities:
            # Score based on uniqueness, defensibility, and value
            uniqueness = cap.get("uniqueness", 0)  # 1-10
            defensibility = cap.get("defensibility", 0)  # 1-10
            value = cap.get("customer_value", 0)  # 1-10

            score = uniqueness * 0.4 + defensibility * 0.3 + value * 0.3

            if score >= 7:
                unfair_advantages.append(
                    {**cap, "advantage_score": score, "is_unfair_advantage": True},
                )

        return sorted(unfair_advantages, key=lambda x: x["advantage_score"], reverse=True)
