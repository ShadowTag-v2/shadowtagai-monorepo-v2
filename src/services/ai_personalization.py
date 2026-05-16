# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
AI Personalization Engine for Swiper Platform.

Three-stage evolution:
1. Rules (Day 1): Simple deterministic branching
2. Bandits (Year 1-2): Multi-armed bandit optimization
3. Generative (Year 3+): Full AI-generated personalized content

Strategic Value:
- Stage 1 = wedge. Quick to build, cheap to run, easy to prove ROI
- Stage 2 = moat. Learns shopper → arc → purchase relationships
- Stage 3 = defensibility. Generative narrative conversion engine
"""

import math
import random
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any


class PersonalizationEngine:
  """
  Core AI personalization engine for Swiper adaptive videos.

  Implements three-stage maturity model:
  - Rules: Lightweight, deterministic
  - Bandits: Learning from conversion data
  - Generative: AI-powered custom content
  """

  def __init__(self):
    # Stage 2: Bandit arm statistics
    self.arm_stats = defaultdict(lambda: {"pulls": 0, "conversions": 0, "revenue": 0.0})
    self.epsilon = 0.1  # Exploration rate for epsilon-greedy

  # ========================================================================
  # STAGE 1: RULES-BASED PERSONALIZATION
  # ========================================================================

  def rules_personalize(
    self, user_context: dict[str, Any], video_metadata: dict[str, Any]
  ) -> dict[str, Any]:
    """
    Stage 1: Simple rule-based personalization.

    Cost: Minimal (no GPU, no ML inference)
    Timeline: Ship with MVP
    Outcome: 2-3× conversion lift vs static content

    Inputs:
    - On-page signals (scroll, hover, device)
    - Video metadata (format, duration, products)

    Outputs:
    - Runtime adjustment
    - Scene sequence
    - Product emphasis
    """
    personalization = {
      "stage": "rules",
      "runtime_multiplier": 1.0,
      "scene_sequence": "standard",
      "product_emphasis": "balanced",
      "reasons": [],
    }

    # Device-based adaptation
    device_type = user_context.get("device_type", "desktop")
    if device_type == "mobile":
      personalization["runtime_multiplier"] = 0.7
      personalization["scene_sequence"] = "vertical_optimized"
      personalization["reasons"].append("Mobile user → shorter, vertical format")

    # Behavioral signals
    scroll_speed = user_context.get("scroll_speed")
    if scroll_speed == "fast":
      personalization["runtime_multiplier"] *= 0.6
      personalization["scene_sequence"] = "quick_pitch"
      personalization["reasons"].append("Fast scroller → compress to essentials")
    elif scroll_speed == "slow":
      personalization["runtime_multiplier"] *= 1.2
      personalization["scene_sequence"] = "extended_narrative"
      personalization["reasons"].append("Engaged reader → extend story")

    hover_time = user_context.get("hover_time_seconds", 0)
    if hover_time > 5:
      personalization["runtime_multiplier"] *= 1.3
      personalization["product_emphasis"] = "detailed_specs"
      personalization["reasons"].append("Long hover → show detailed features")

    # Interest matching
    user_interests = user_context.get("interests", [])
    video_category = video_metadata.get("primary_category")

    if video_category in user_interests:
      personalization["product_emphasis"] = "category_expert"
      personalization["reasons"].append(f"Interest match: {video_category}")

    # Household type targeting
    household_type = user_context.get("household_type")
    if household_type == "family_with_kids":
      personalization["scene_sequence"] = "family_friendly"
      personalization["product_emphasis"] = "safety_and_value"
      personalization["reasons"].append("Family household → emphasize safety")

    return personalization

  # ========================================================================
  # STAGE 2: MULTI-ARMED BANDIT OPTIMIZATION
  # ========================================================================

  def bandits_select_arc(
    self,
    video_id: str,
    available_arcs: list[str],
    user_segment: str,
    exploration_mode: bool = True,
  ) -> tuple[str, dict[str, Any]]:
    """
    Stage 2: Multi-armed bandit for narrative arc selection.

    Cost: Moderate (analytics infra, lightweight ML)
    Timeline: After 10K+ daily sessions
    Outcome: Data moat - every session improves conversion intelligence

    Algorithm: UCB1 (Upper Confidence Bound)
    - Balances exploration vs exploitation
    - Selects arcs with highest potential conversion rate
    """
    if not available_arcs:
      return "default", {"reason": "no_arcs_available"}

    # Epsilon-greedy: Sometimes explore randomly
    if exploration_mode and random.random() < self.epsilon:
      selected_arc = random.choice(available_arcs)
      return selected_arc, {
        "strategy": "exploration",
        "reason": "random_exploration",
        "epsilon": self.epsilon,
      }

    # UCB1: Select arm with highest upper confidence bound
    best_arc = None
    best_score = -float("inf")
    total_pulls = sum(self.arm_stats[arc]["pulls"] for arc in available_arcs)

    ucb_scores = {}

    for arc in available_arcs:
      stats = self.arm_stats[f"{video_id}:{arc}:{user_segment}"]
      pulls = stats["pulls"]
      conversions = stats["conversions"]

      if pulls == 0:
        # Unplayed arms get infinite score (always try once)
        ucb_scores[arc] = float("inf")
      else:
        # UCB1 formula
        avg_reward = conversions / pulls
        exploration_bonus = math.sqrt(2 * math.log(total_pulls + 1) / pulls)
        ucb_scores[arc] = avg_reward + exploration_bonus

      if ucb_scores[arc] > best_score:
        best_score = ucb_scores[arc]
        best_arc = arc

    return best_arc, {
      "strategy": "ucb1",
      "ucb_scores": ucb_scores,
      "total_pulls": total_pulls,
      "selected_score": best_score,
    }

  def bandits_record_outcome(
    self,
    video_id: str,
    arc: str,
    user_segment: str,
    converted: bool,
    revenue: float = 0.0,
  ):
    """
    Record outcome for bandit learning.

    Call this after user completes session to update arm statistics
    """
    key = f"{video_id}:{arc}:{user_segment}"
    self.arm_stats[key]["pulls"] += 1
    if converted:
      self.arm_stats[key]["conversions"] += 1
    self.arm_stats[key]["revenue"] += revenue

  def bandits_get_performance(self, video_id: str) -> dict[str, Any]:
    """
    Get bandit performance statistics for a video.

    Shows which arcs are winning for different user segments
    """
    video_stats = {}

    for key, stats in self.arm_stats.items():
      if key.startswith(f"{video_id}:"):
        parts = key.split(":")
        arc = parts[1]
        segment = parts[2]

        if arc not in video_stats:
          video_stats[arc] = {}

        conversion_rate = (
          (stats["conversions"] / stats["pulls"] * 100) if stats["pulls"] > 0 else 0
        )
        avg_revenue = stats["revenue"] / stats["pulls"] if stats["pulls"] > 0 else 0

        video_stats[arc][segment] = {
          "pulls": stats["pulls"],
          "conversions": stats["conversions"],
          "conversion_rate_pct": round(conversion_rate, 2),
          "avg_revenue": round(avg_revenue, 2),
        }

    return video_stats

  # ========================================================================
  # STAGE 3: GENERATIVE AI PERSONALIZATION
  # ========================================================================

  def generative_create_narrative(
    self,
    user_profile: dict[str, Any],
    product_info: dict[str, Any],
    video_metadata: dict[str, Any],
  ) -> dict[str, Any]:
    """
    Stage 3: Fully AI-generated personalized content.

    Cost: High ($5k-$20k/mo at scale before optimization)
    Timeline: Year 3+ after ARR + dataset make it sustainable
    Outcome: True 1:1 adaptive commerce films

    In production, this would:
    1. Call Claude API with user profile + product context
    2. Generate custom voiceover script
    3. Select personalized visual scenes
    4. Dynamic soundtrack/overlays
    5. Cache aggressively (same profile = reuse)

    Mock implementation for now
    """
    # Extract user context
    name = user_profile.get("name", "there")
    interests = user_profile.get("interests", [])
    household_type = user_profile.get("household_type", "individual")
    purchase_history = user_profile.get("purchase_history", [])

    # Product details
    product_name = product_info.get("name", "this product")
    product_category = product_info.get("category")
    price = product_info.get("price", 0)

    # Generate personalized elements
    narrative = {
      "stage": "generative",
      "personalization_level": "1:1",
      # Custom intro
      "intro_script": self._generate_intro(name, interests, household_type),
      # Personalized product demo
      "demo_focus": self._select_demo_focus(
        interests, product_category, purchase_history
      ),
      # Custom benefits messaging
      "benefits_emphasis": self._generate_benefits(
        household_type, product_category, price
      ),
      # Personalized CTA
      "cta_message": self._generate_cta(household_type, name, product_name),
      # Audio/visual customization
      "soundtrack": self._select_soundtrack(interests, household_type),
      "visual_style": self._select_visual_style(user_profile),
      # Dynamic scene substitution
      "scenes": self._generate_scene_sequence(
        user_profile, product_info, video_metadata
      ),
      "generation_timestamp": datetime.now(UTC).isoformat(),
      "cache_key": self._generate_cache_key(user_profile, product_info),
    }

    return narrative

  def _generate_intro(
    self, name: str, interests: list[str], household_type: str
  ) -> str:
    """Generate personalized intro script."""
    if household_type == "family_with_kids":
      return f"Hey {name}! Looking for something the whole family will love? You're in the right place."
    elif interests and "sports" in interests:
      return f"Hi {name}! As a sports enthusiast, you'll appreciate what we have for you today."
    else:
      return f"Welcome {name}! Let's find something perfect for you."

  def _select_demo_focus(
    self, interests: list[str], product_category: str, purchase_history: list[str]
  ) -> str:
    """Select which product aspects to emphasize."""
    if "technology" in interests or "electronics" in interests:
      return "technical_specifications"
    elif "sustainability" in interests:
      return "eco_friendly_features"
    elif product_category == "toys" and "family" in str(purchase_history):
      return "safety_and_educational_value"
    else:
      return "quality_and_value"

  def _generate_benefits(
    self, household_type: str, category: str, price: float
  ) -> list[str]:
    """Generate personalized benefits messaging."""
    benefits = []

    if household_type == "family_with_kids":
      benefits.extend(
        [
          "Safe for all ages",
          "Built to last through years of use",
          "Educational and fun",
        ]
      )
    elif household_type == "couple":
      benefits.extend(
        [
          "Premium quality that looks great in any home",
          "Energy efficient - saves money long-term",
          "Stylish design you'll both love",
        ]
      )
    else:
      benefits.extend(
        [
          "Exceptional quality at a fair price",
          "Trusted by thousands of satisfied customers",
          "Hassle-free returns and warranty",
        ]
      )

    if price < 50:
      benefits.append("Affordable luxury")
    elif price > 200:
      benefits.append("Investment-grade quality")

    return benefits

  def _generate_cta(self, household_type: str, name: str, product_name: str) -> str:
    """Generate personalized call-to-action."""
    if household_type == "family_with_kids":
      return f"{name}, give your family the gift they deserve. Get your {product_name} today!"
    else:
      return f"Ready to upgrade, {name}? Add {product_name} to your cart now."

  def _select_soundtrack(self, interests: list[str], household_type: str) -> str:
    """Select personalized background music."""
    if household_type == "family_with_kids":
      return "upbeat_family_friendly"
    elif "sports" in interests:
      return "energetic_motivational"
    elif "luxury" in interests:
      return "elegant_sophisticated"
    else:
      return "modern_uplifting"

  def _select_visual_style(self, user_profile: dict) -> str:
    """Select visual style based on user preferences."""
    age_range = user_profile.get("age_range", "")

    if age_range.startswith("18-") or age_range.startswith("25-"):
      return "fast_paced_modern"
    elif age_range.startswith("45-") or age_range.startswith("55-"):
      return "classic_trustworthy"
    else:
      return "balanced_professional"

  def _generate_scene_sequence(
    self, user_profile: dict, product_info: dict, video_metadata: dict
  ) -> list[dict[str, Any]]:
    """Generate personalized scene sequence."""
    scenes = [
      {
        "scene_id": "personalized_intro",
        "duration_seconds": 5,
        "content": "Custom greeting with user's name",
      },
      {
        "scene_id": "problem_statement",
        "duration_seconds": 10,
        "content": "Address user's specific pain point",
      },
      {
        "scene_id": "product_demo",
        "duration_seconds": 30,
        "content": "Demo focusing on user's interest areas",
      },
      {
        "scene_id": "social_proof",
        "duration_seconds": 15,
        "content": "Testimonials from similar user segment",
      },
      {
        "scene_id": "benefits",
        "duration_seconds": 20,
        "content": "Personalized benefits messaging",
      },
      {
        "scene_id": "cta",
        "duration_seconds": 10,
        "content": "Personalized call-to-action",
      },
    ]

    return scenes

  def _generate_cache_key(self, user_profile: dict, product_info: dict) -> str:
    """
    Generate cache key for generative content reuse.

    Same user segment + product → reuse generated content
    """
    segment_features = [
      user_profile.get("household_type", "unknown"),
      user_profile.get("age_range", "unknown"),
      ",".join(sorted(user_profile.get("interests", []))),
      product_info.get("category", "unknown"),
      str(int(product_info.get("price", 0) / 50) * 50),  # Price bucket
    ]
    return ":".join(segment_features)


# ================================================================================
# USAGE EXAMPLES
# ================================================================================

if __name__ == "__main__":
  engine = PersonalizationEngine()

  # Example 1: Rules-based personalization

  user_context = {
    "device_type": "mobile",
    "scroll_speed": "fast",
    "hover_time_seconds": 2,
    "interests": ["toys", "family"],
    "household_type": "family_with_kids",
  }

  video_metadata = {"primary_category": "toys", "base_duration": 180}

  rules_result = engine.rules_personalize(user_context, video_metadata)

  # Example 2: Multi-armed bandit

  available_arcs = ["family_fun", "tech_specs", "value_prop", "emotional_story"]

  # Simulate some historical data
  engine.bandits_record_outcome("video123", "family_fun", "family_segment", True, 29.99)
  engine.bandits_record_outcome("video123", "family_fun", "family_segment", True, 29.99)
  engine.bandits_record_outcome("video123", "family_fun", "family_segment", False, 0)
  engine.bandits_record_outcome("video123", "tech_specs", "family_segment", False, 0)
  engine.bandits_record_outcome(
    "video123", "emotional_story", "family_segment", True, 29.99
  )

  selected_arc, bandit_info = engine.bandits_select_arc(
    "video123", available_arcs, "family_segment"
  )

  performance = engine.bandits_get_performance("video123")
  for arc, segments in performance.items():
    for segment, stats in segments.items():
      pass

  # Example 3: Generative AI

  user_profile = {
    "name": "Sarah",
    "age_range": "35-44",
    "household_type": "family_with_kids",
    "interests": ["family", "education", "safety"],
    "purchase_history": ["toys", "books"],
  }

  product_info = {"name": "Superman Action Figure", "category": "toys", "price": 29.99}

  video_metadata = {"format": "premium_beacon", "duration": 5400}

  generative_result = engine.generative_create_narrative(
    user_profile, product_info, video_metadata
  )
