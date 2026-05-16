# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
PNKLN Core Stack - AiYou Feed Ranking Engine

AI-presumed ranking (not engagement-based):
- Energy-based neural models
- Latent density scoring
- Semantic similarity
- Quality-over-popularity

Based on "neural PDF" research:
- Energy models for content scoring
- Density-based ranking
- No follower count bias
"""

from dataclasses import dataclass
from datetime import datetime

import structlog
import numpy as np
import torch
import torch.nn as nn

from ingestion.classification.tier_classifier import IngestedItem, TierScore
from shadowtag.neural_hash import NeuralFingerprint


logger = structlog.get_logger(__name__)


@dataclass
class ContentItem:
    """Content item in AiYou platform."""

    item_id: str
    source_item: IngestedItem
    tier_score: TierScore
    shadow_tag_fingerprint: NeuralFingerprint | None

    # AI ranking scores
    energy_score: float  # Energy-based model score
    density_score: float  # Latent density (from neural PDF)
    novelty_score: float  # How unique/novel is this content
    quality_score: float  # Technical/aesthetic quality

    # Computed rank
    ai_presumed_rank: float  # Final ranking score (0.0-1.0)

    # Metadata
    published_at: datetime
    verified: bool  # ShadowTag verified


class EnergyRankingModel(nn.Module):
    """
    Energy-based model for content ranking.

    Based on energy models from neural PDF research:
    - Lower energy = higher quality content
    - Energy landscape learned from data
    - Independent of social signals
    """

    def __init__(self, input_dim: int = 512, hidden_dim: int = 256):
        super().__init__()

        self.energy_network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Compute energy for content features.

        Args:
            x: Content features (batch_size, input_dim)

        Returns:
            Energy scores (batch_size, 1) - lower is better
        """
        return self.energy_network(x)


class NoveltyDetector(nn.Module):
    """
    Detects content novelty for ranking.

    Prevents redundant/repetitive content from dominating feed:
    - Semantic similarity to recent content
    - Anomaly detection for truly novel content
    - Diversity promotion
    """

    def __init__(self, embedding_dim: int = 256):
        super().__init__()

        self.encoder = nn.Sequential(nn.Linear(512, embedding_dim), nn.LayerNorm(embedding_dim), nn.ReLU())

        # Memory bank of recent embeddings
        self.memory_size = 1000
        self.memory = None  # Initialized on first use

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Compute novelty score.

        Args:
            x: Content features (batch_size, 512)

        Returns:
            Novelty scores (batch_size, 1) - higher is more novel
        """
        embeddings = self.encoder(x)

        if self.memory is None:
            # Initialize memory
            self.memory = embeddings.detach().clone()
            return torch.ones(x.size(0), 1)

        # Calculate novelty as distance from memory bank
        # Higher distance = more novel
        distances = torch.cdist(embeddings, self.memory)
        min_distances, _ = distances.min(dim=1)

        # Normalize to 0-1
        novelty = torch.sigmoid(min_distances / 10.0).unsqueeze(1)

        # Update memory (FIFO)
        self.memory = torch.cat([self.memory, embeddings.detach()], dim=0)[-self.memory_size :]

        return novelty


class FeedRankingEngine:
    """
    Main AI-presumed feed ranking engine.

    Combines multiple signals:
    - Energy-based content quality
    - Latent density (from neural fingerprint)
    - Novelty/uniqueness
    - ShadowTag verification status
    - Tier classification

    NO engagement metrics used (no likes, views, followers).
    """

    def __init__(self):
        # Initialize models
        self.energy_model = EnergyRankingModel()
        self.novelty_detector = NoveltyDetector()

        # Set to eval mode
        self.energy_model.eval()
        self.novelty_detector.eval()

        # TODO: Load pre-trained weights
        # self.energy_model.load_state_dict(torch.load('models/energy_ranker.pt'))
        # self.novelty_detector.load_state_dict(torch.load('models/novelty_detector.pt'))

        # Ranking weights
        self.weights = {"energy": 0.30, "density": 0.25, "novelty": 0.20, "tier": 0.15, "verification": 0.10}

        self._rank_count = 0

        logger.info("feed_ranking_engine_initialized", weights=self.weights)

    def rank_item(self, item: ContentItem) -> ContentItem:
        """
        Compute AI-presumed rank for a single content item.

        Args:
            item: Content item to rank

        Returns:
            Same item with ai_presumed_rank filled in
        """
        # Extract features
        features = self._extract_features(item)

        with torch.no_grad():
            # 1. Energy score (lower energy = better)
            energy = self.energy_model(features)
            energy_score = float(1.0 / (1.0 + torch.exp(energy).item()))  # Invert

            # 2. Density score (from neural fingerprint or tier score)
            if item.shadow_tag_fingerprint:
                density_score = item.shadow_tag_fingerprint.density_score
            else:
                density_score = item.tier_score.overall

            # 3. Novelty score
            novelty = self.novelty_detector(features)
            novelty_score = float(novelty.item())

        # 4. Tier score (Tier 1 = highest)
        tier_map = {1: 1.0, 2: 0.7, 3: 0.4}
        tier_score = tier_map.get(item.tier_score.tier, 0.5)

        # 5. Verification score
        verification_score = 1.0 if item.verified else 0.5

        # Compute weighted rank
        ai_presumed_rank = (
            energy_score * self.weights["energy"]
            + density_score * self.weights["density"]
            + novelty_score * self.weights["novelty"]
            + tier_score * self.weights["tier"]
            + verification_score * self.weights["verification"]
        )

        # Update item
        item.energy_score = energy_score
        item.density_score = density_score
        item.novelty_score = novelty_score
        item.quality_score = (energy_score + density_score) / 2
        item.ai_presumed_rank = round(ai_presumed_rank, 4)

        self._rank_count += 1

        logger.debug(
            "item_ranked", item_id=item.item_id, rank=item.ai_presumed_rank, energy=energy_score, density=density_score, novelty=novelty_score
        )

        return item

    def rank_batch(self, items: list[ContentItem]) -> list[ContentItem]:
        """
        Rank multiple items in batch.

        Args:
            items: List of content items

        Returns:
            Same items with rankings, sorted by ai_presumed_rank (desc)
        """
        # Rank each item
        ranked_items = [self.rank_item(item) for item in items]

        # Sort by rank (highest first)
        ranked_items.sort(key=lambda x: x.ai_presumed_rank, reverse=True)

        return ranked_items

    def generate_feed(self, candidate_items: list[ContentItem], max_items: int = 50, diversity_factor: float = 0.8) -> list[ContentItem]:
        """
        Generate personalized feed from candidate items.

        Args:
            candidate_items: Pool of items to rank
            max_items: Maximum items in feed
            diversity_factor: 0.0-1.0, higher = more diverse

        Returns:
            Ordered feed items
        """
        # Rank all candidates
        ranked = self.rank_batch(candidate_items)

        # Apply diversity filtering
        if diversity_factor > 0:
            ranked = self._apply_diversity(ranked, diversity_factor)

        # Return top N
        feed = ranked[:max_items]

        logger.info(
            "feed_generated", candidate_count=len(candidate_items), feed_size=len(feed), avg_rank=np.mean([item.ai_presumed_rank for item in feed])
        )

        return feed

    def _extract_features(self, item: ContentItem) -> torch.Tensor:
        """
        Extract feature vector for ranking models.

        In production, this would use:
        - Pre-trained vision models (e.g., CLIP)
        - Audio feature extractors
        - Text embeddings (e.g., Sentence-BERT)

        For now, generates placeholder features.
        """
        # TODO: Implement actual feature extraction

        # Placeholder: random features
        features = torch.randn(1, 512)

        return features

    def _apply_diversity(self, ranked_items: list[ContentItem], diversity_factor: float) -> list[ContentItem]:
        """
        Apply diversity filtering to prevent similar content clustering.

        Uses Maximum Marginal Relevance (MMR):
        - Balance relevance (AI rank) with diversity
        - Penalize items similar to already-selected items
        """
        if not ranked_items:
            return []

        selected = [ranked_items[0]]  # Always take top item
        candidates = ranked_items[1:]

        while len(candidates) > 0 and len(selected) < len(ranked_items):
            # Find most diverse item among remaining candidates
            best_idx = 0
            best_score = -float("inf")

            for i, candidate in enumerate(candidates):
                # Relevance score (AI rank)
                relevance = candidate.ai_presumed_rank

                # Diversity score (min similarity to selected items)
                similarities = [self._content_similarity(candidate, s) for s in selected]
                diversity = 1.0 - max(similarities) if similarities else 1.0

                # MMR score
                mmr_score = diversity_factor * relevance + (1 - diversity_factor) * diversity

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i

            # Add best candidate to selected
            selected.append(candidates.pop(best_idx))

        return selected

    def _content_similarity(self, item1: ContentItem, item2: ContentItem) -> float:
        """
        Calculate similarity between two content items.

        Returns 0.0-1.0 (1.0 = identical)
        """
        # TODO: Implement actual similarity (e.g., cosine similarity of embeddings)

        # Placeholder: simple heuristic
        if item1.source_item.source == item2.source_item.source:
            return 0.7  # Same source = somewhat similar
        else:
            return 0.3

    def get_stats(self) -> dict:
        """Get ranking engine statistics."""
        return {
            "total_rankings": self._rank_count,
            "model": "energy_based_neural",
            "ranking_weights": self.weights,
            "engagement_bias": "none",  # Key differentiator!
        }
