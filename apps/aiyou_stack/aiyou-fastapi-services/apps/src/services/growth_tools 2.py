"""MCP tools for growth engineering."""

import json
import math
from typing import Any


def analyze_metrics(args: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze growth metrics and provide insights.

    Args:
        args: Dictionary containing:
            - metrics: Dictionary of metrics to analyze
            - time_range: Optional time range
            - dimensions: Optional list of dimensions
    """
    metrics = args.get("metrics", {})
    time_range = args.get("time_range", "7d")
    dimensions = args.get("dimensions", [])

    analysis = {
        "summary": {},
        "trends": {},
        "insights": [],
        "recommendations": [],
    }

    # Calculate growth rates
    if "current" in metrics and "previous" in metrics:
        for key in metrics["current"]:
            if key in metrics["previous"] and metrics["previous"][key] != 0:
                current = metrics["current"][key]
                previous = metrics["previous"][key]
                growth_rate = ((current - previous) / previous) * 100
                analysis["summary"][f"{key}_growth"] = round(growth_rate, 2)

    # Calculate AARRR metrics if present
    if "users_acquired" in metrics:
        analysis["summary"]["acquisition"] = metrics["users_acquired"]

    if "users_activated" in metrics and "users_acquired" in metrics:
        activation_rate = (
            metrics["users_activated"] / metrics["users_acquired"] * 100
            if metrics["users_acquired"] > 0
            else 0
        )
        analysis["summary"]["activation_rate"] = round(activation_rate, 2)

        if activation_rate < 25:
            analysis["insights"].append(
                "Low activation rate detected. Users are not reaching the 'aha moment'."
            )
            analysis["recommendations"].append(
                "Optimize onboarding flow to get users to value faster."
            )

    if "users_retained" in metrics and "users_activated" in metrics:
        retention_rate = (
            metrics["users_retained"] / metrics["users_activated"] * 100
            if metrics["users_activated"] > 0
            else 0
        )
        analysis["summary"]["retention_rate"] = round(retention_rate, 2)

        if retention_rate < 40:
            analysis["insights"].append("Low retention rate. Users are not forming habits.")
            analysis["recommendations"].append(
                "Implement engagement loops and habit-forming features."
            )

    # Calculate viral metrics
    if "invites_sent" in metrics and "users_acquired" in metrics:
        invites_per_user = (
            metrics["invites_sent"] / metrics["users_acquired"]
            if metrics["users_acquired"] > 0
            else 0
        )
        analysis["summary"]["invites_per_user"] = round(invites_per_user, 2)

    if "referrals_converted" in metrics and "invites_sent" in metrics:
        conversion_rate = (
            metrics["referrals_converted"] / metrics["invites_sent"] * 100
            if metrics["invites_sent"] > 0
            else 0
        )
        analysis["summary"]["referral_conversion_rate"] = round(conversion_rate, 2)

    # Generate insights based on patterns
    if analysis["summary"]:
        if any(v > 20 for k, v in analysis["summary"].items() if "growth" in k):
            analysis["insights"].append(
                "Strong growth detected. Consider scaling acquisition channels."
            )

    return {"content": [{"type": "text", "text": json.dumps(analysis, indent=2)}]}


def ab_test_calculator(args: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate A/B test sample size and statistical significance.

    Args:
        args: Dictionary containing:
            - baseline_rate: Baseline conversion rate (0-1)
            - minimum_detectable_effect: Minimum effect to detect (0-1)
            - significance_level: Significance level (default 0.05)
            - power: Statistical power (default 0.8)
            - variant_a_conversions: Optional conversions for variant A
            - variant_a_visitors: Optional visitors for variant A
            - variant_b_conversions: Optional conversions for variant B
            - variant_b_visitors: Optional visitors for variant B
    """
    baseline_rate = args.get("baseline_rate", 0.1)
    mde = args.get("minimum_detectable_effect", 0.1)  # 10% relative change
    alpha = args.get("significance_level", 0.05)
    power = args.get("power", 0.8)

    # Calculate required sample size per variant
    # Using simplified formula: n = 16 * p * (1-p) / (effect^2)
    # For more accuracy, use statsmodels or scipy
    p1 = baseline_rate
    p2 = baseline_rate * (1 + mde)
    effect = p2 - p1

    if effect == 0:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": "Effect size cannot be zero"}, indent=2),
                }
            ]
        }

    # Simplified sample size calculation
    pooled_p = (p1 + p2) / 2
    n_per_variant = math.ceil((16 * pooled_p * (1 - pooled_p)) / (effect**2))

    result = {
        "sample_size_per_variant": n_per_variant,
        "total_sample_size": n_per_variant * 2,
        "baseline_rate": baseline_rate,
        "expected_rate_variant_b": p2,
        "minimum_detectable_effect": mde,
        "significance_level": alpha,
        "power": power,
    }

    # If actual data provided, calculate significance
    if all(
        k in args
        for k in [
            "variant_a_conversions",
            "variant_a_visitors",
            "variant_b_conversions",
            "variant_b_visitors",
        ]
    ):
        conv_a = args["variant_a_conversions"]
        vis_a = args["variant_a_visitors"]
        conv_b = args["variant_b_conversions"]
        vis_b = args["variant_b_visitors"]

        rate_a = conv_a / vis_a if vis_a > 0 else 0
        rate_b = conv_b / vis_b if vis_b > 0 else 0

        # Simplified z-test
        pooled_rate = (conv_a + conv_b) / (vis_a + vis_b)
        se = math.sqrt(pooled_rate * (1 - pooled_rate) * (1 / vis_a + 1 / vis_b))
        z_score = (rate_b - rate_a) / se if se > 0 else 0

        # Very simplified p-value (for z > 1.96, p < 0.05)
        is_significant = abs(z_score) > 1.96

        result["actual_results"] = {
            "variant_a_rate": round(rate_a, 4),
            "variant_b_rate": round(rate_b, 4),
            "uplift": round((rate_b - rate_a) / rate_a * 100, 2) if rate_a > 0 else 0,
            "z_score": round(z_score, 2),
            "is_significant": is_significant,
            "recommendation": (
                "Variant B is significantly better"
                if is_significant and rate_b > rate_a
                else "Variant A is significantly better"
                if is_significant and rate_a > rate_b
                else "No significant difference detected"
            ),
        }

    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


def viral_coefficient_calculator(args: dict[str, Any]) -> dict[str, Any]:
    """
    Calculate viral coefficient (K-factor) and viral loop metrics.

    Args:
        args: Dictionary containing:
            - invites_sent_per_user: Average invites sent per user
            - conversion_rate: Conversion rate of invites (0-1)
            - cycle_time_days: Time for one viral cycle in days
            - initial_users: Optional initial user count
            - time_horizon_days: Optional time horizon for projection
    """
    invites = args.get("invites_sent_per_user", 0)
    conv_rate = args.get("conversion_rate", 0)
    cycle_time = args.get("cycle_time_days", 7)
    initial_users = args.get("initial_users", 1000)
    time_horizon = args.get("time_horizon_days", 90)

    # Calculate K-factor
    k_factor = invites * conv_rate

    result = {
        "viral_coefficient": round(k_factor, 3),
        "invites_per_user": invites,
        "conversion_rate": conv_rate,
        "cycle_time_days": cycle_time,
        "interpretation": "",
        "recommendations": [],
    }

    # Interpret K-factor
    if k_factor > 1:
        result["interpretation"] = (
            "Viral! Each user brings more than 1 new user. Growth is exponential."
        )
        cycles_in_horizon = time_horizon / cycle_time
        projected_users = initial_users * (k_factor**cycles_in_horizon)
        result["projected_users"] = int(projected_users)
    elif k_factor == 1:
        result["interpretation"] = "Sustainable. Each user brings exactly 1 new user."
    else:
        result["interpretation"] = (
            f"Sub-viral. Growth depends on other channels. Each user brings {k_factor} new users."
        )
        result["recommendations"].append(
            "Increase invites per user or improve conversion rate to achieve virality."
        )

    # Add recommendations based on components
    if invites < 1:
        result["recommendations"].append(
            f"Increase invites per user from {invites} to >1 by making sharing easier."
        )

    if conv_rate < 0.2:
        result["recommendations"].append(
            f"Improve conversion rate from {conv_rate * 100:.1f}% to >20% with better targeting."
        )

    if cycle_time > 14:
        result["recommendations"].append(
            f"Reduce cycle time from {cycle_time} days to <14 days for faster growth."
        )

    # Calculate what's needed for virality
    if k_factor < 1:
        needed_invites = 1 / conv_rate if conv_rate > 0 else float("inf")
        needed_conv_rate = 1 / invites if invites > 0 else float("inf")

        result["to_achieve_virality"] = {
            "option_1": f"Increase invites per user to {needed_invites:.2f}",
            "option_2": f"Increase conversion rate to {needed_conv_rate * 100:.1f}%",
        }

    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


def retention_analyzer(args: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze user retention and cohort behavior.

    Args:
        args: Dictionary containing:
            - cohort_data: List of cohorts with retention data
            - cohort_date: Date of the cohort
            - day_1_retained: Users retained on day 1
            - day_7_retained: Users retained on day 7
            - day_30_retained: Users retained on day 30
    """
    cohort_data = args.get("cohort_data", [])

    if not cohort_data:
        # Single cohort analysis
        d1 = args.get("day_1_retained", 0)
        d7 = args.get("day_7_retained", 0)
        d30 = args.get("day_30_retained", 0)
        total_users = args.get("total_users", 100)

        cohort_data = [
            {
                "cohort_date": args.get("cohort_date", "2024-01-01"),
                "total_users": total_users,
                "day_1": d1,
                "day_7": d7,
                "day_30": d30,
            }
        ]

    analysis = {"cohorts": [], "insights": [], "recommendations": []}

    for cohort in cohort_data:
        total = cohort.get("total_users", 0)
        if total == 0:
            continue

        cohort_analysis = {
            "cohort_date": cohort.get("cohort_date"),
            "total_users": total,
            "retention_rates": {},
        }

        # Calculate retention rates
        for day in ["day_1", "day_7", "day_30", "day_60", "day_90"]:
            if day in cohort:
                rate = (cohort[day] / total * 100) if total > 0 else 0
                cohort_analysis["retention_rates"][day] = round(rate, 2)

        analysis["cohorts"].append(cohort_analysis)

    # Generate insights
    if analysis["cohorts"]:
        avg_d1 = sum(c["retention_rates"].get("day_1", 0) for c in analysis["cohorts"]) / len(
            analysis["cohorts"]
        )
        avg_d7 = sum(c["retention_rates"].get("day_7", 0) for c in analysis["cohorts"]) / len(
            analysis["cohorts"]
        )
        avg_d30 = sum(c["retention_rates"].get("day_30", 0) for c in analysis["cohorts"]) / len(
            analysis["cohorts"]
        )

        analysis["average_retention"] = {
            "day_1": round(avg_d1, 2),
            "day_7": round(avg_d7, 2),
            "day_30": round(avg_d30, 2),
        }

        # Benchmarks (industry averages)
        if avg_d1 < 25:
            analysis["insights"].append(
                "Day 1 retention is below 25% benchmark. Users aren't finding immediate value."
            )
            analysis["recommendations"].append(
                "Optimize onboarding to deliver value in first session."
            )

        if avg_d7 < 15:
            analysis["insights"].append(
                "Day 7 retention is below 15% benchmark. Users aren't forming habits."
            )
            analysis["recommendations"].append(
                "Add engagement hooks and notifications to bring users back."
            )

        if avg_d30 < 10:
            analysis["insights"].append(
                "Day 30 retention is below 10% benchmark. Long-term value is unclear."
            )
            analysis["recommendations"].append(
                "Build features that increase investment and long-term engagement."
            )

        # Calculate retention curve slope
        if avg_d1 > 0:
            d1_to_d7_drop = ((avg_d1 - avg_d7) / avg_d1 * 100) if avg_d1 > 0 else 0
            d7_to_d30_drop = ((avg_d7 - avg_d30) / avg_d7 * 100) if avg_d7 > 0 else 0

            analysis["churn_analysis"] = {
                "d1_to_d7_drop": round(d1_to_d7_drop, 2),
                "d7_to_d30_drop": round(d7_to_d30_drop, 2),
            }

            if d1_to_d7_drop > 50:
                analysis["insights"].append("High churn in first week. Focus on early engagement.")

    return {"content": [{"type": "text", "text": json.dumps(analysis, indent=2)}]}


def funnel_analyzer(args: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze conversion funnels and identify drop-off points.

    Args:
        args: Dictionary containing:
            - funnel_steps: List of funnel steps with counts
                [{"step": "Landing", "count": 1000}, {"step": "Signup", "count": 300}, ...]
    """
    funnel_steps = args.get("funnel_steps", [])

    if not funnel_steps or len(funnel_steps) < 2:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"error": "Need at least 2 funnel steps"}, indent=2),
                }
            ]
        }

    analysis = {
        "steps": [],
        "overall_conversion": 0,
        "insights": [],
        "recommendations": [],
    }

    total_entered = funnel_steps[0]["count"]
    previous_count = total_entered

    for i, step in enumerate(funnel_steps):
        step_name = step["step"]
        step_count = step["count"]

        # Calculate conversion from previous step
        conversion_from_prev = (step_count / previous_count * 100) if previous_count > 0 else 0

        # Calculate conversion from start
        conversion_from_start = (step_count / total_entered * 100) if total_entered > 0 else 0

        # Calculate drop-off
        drop_off = previous_count - step_count
        drop_off_rate = (drop_off / previous_count * 100) if previous_count > 0 else 0

        step_analysis = {
            "step": step_name,
            "count": step_count,
            "conversion_from_previous": round(conversion_from_prev, 2),
            "conversion_from_start": round(conversion_from_start, 2),
            "drop_off": drop_off,
            "drop_off_rate": round(drop_off_rate, 2),
        }

        analysis["steps"].append(step_analysis)

        # Identify problem areas
        if drop_off_rate > 50 and i > 0:
            analysis["insights"].append(
                f"Critical drop-off at '{step_name}': {drop_off_rate:.1f}% of users lost."
            )
            analysis["recommendations"].append(
                f"Investigate and optimize the '{funnel_steps[i - 1]['step']}' to '{step_name}' transition."
            )

        previous_count = step_count

    # Overall conversion
    final_count = funnel_steps[-1]["count"]
    overall = (final_count / total_entered * 100) if total_entered > 0 else 0
    analysis["overall_conversion"] = round(overall, 2)

    # General recommendations
    if overall < 5:
        analysis["recommendations"].append(
            "Overall conversion is very low (<5%). Consider A/B testing each step."
        )

    # Find the biggest drop-off
    if len(analysis["steps"]) > 1:
        biggest_drop = max(
            (s for s in analysis["steps"] if "drop_off_rate" in s),
            key=lambda x: x["drop_off_rate"],
        )
        analysis["biggest_drop_off"] = {
            "step": biggest_drop["step"],
            "drop_off_rate": biggest_drop["drop_off_rate"],
        }
        analysis["recommendations"].insert(
            0,
            f"Prioritize optimizing '{biggest_drop['step']}' - the biggest drop-off point.",
        )

    return {"content": [{"type": "text", "text": json.dumps(analysis, indent=2)}]}


# MCP tool registry
GROWTH_TOOLS = {
    "analyze_metrics": {
        "function": analyze_metrics,
        "description": "Analyze growth metrics and provide insights",
        "input_schema": {
            "type": "object",
            "properties": {
                "metrics": {"type": "object", "description": "Metrics to analyze"},
                "time_range": {
                    "type": "string",
                    "description": "Time range for analysis",
                },
                "dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Dimensions to analyze",
                },
            },
            "required": ["metrics"],
        },
    },
    "ab_test_calculator": {
        "function": ab_test_calculator,
        "description": "Calculate A/B test sample size and significance",
        "input_schema": {
            "type": "object",
            "properties": {
                "baseline_rate": {"type": "number"},
                "minimum_detectable_effect": {"type": "number"},
                "significance_level": {"type": "number"},
                "power": {"type": "number"},
            },
            "required": ["baseline_rate", "minimum_detectable_effect"],
        },
    },
    "viral_coefficient_calculator": {
        "function": viral_coefficient_calculator,
        "description": "Calculate viral coefficient and growth projections",
        "input_schema": {
            "type": "object",
            "properties": {
                "invites_sent_per_user": {"type": "number"},
                "conversion_rate": {"type": "number"},
                "cycle_time_days": {"type": "number"},
            },
            "required": ["invites_sent_per_user", "conversion_rate"],
        },
    },
    "retention_analyzer": {
        "function": retention_analyzer,
        "description": "Analyze user retention and cohort behavior",
        "input_schema": {
            "type": "object",
            "properties": {
                "cohort_data": {"type": "array"},
                "total_users": {"type": "number"},
                "day_1_retained": {"type": "number"},
                "day_7_retained": {"type": "number"},
                "day_30_retained": {"type": "number"},
            },
        },
    },
    "funnel_analyzer": {
        "function": funnel_analyzer,
        "description": "Analyze conversion funnels and identify drop-offs",
        "input_schema": {
            "type": "object",
            "properties": {
                "funnel_steps": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step": {"type": "string"},
                            "count": {"type": "number"},
                        },
                    },
                }
            },
            "required": ["funnel_steps"],
        },
    },
}
