# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""QK Attribution: Decompose attention scores as bilinear functions of feature activations.

Based on the paper "Tracing Attention Computation Through Feature Interactions" (2025)
by Kamath, Ameisen, et al.

The core insight: attention scores (pre-softmax) are bilinear in the residual stream
at query and key positions. With a decomposition of the residual stream as a sum of
feature components, we can rewrite attention scores as a sum of dot products between
feature-feature pairs.

Mathematical formulation:
    attention_score(p_k, p_q) = (W_Q^T W_K @ r_k)^T @ r_q

Where:
    - W_QK = W_Q^T W_K (combined QK matrix)
    - r_k, r_q are residual streams at key and query positions
    - Each residual stream decomposes as: r = Σ(a_i * v_i) + bias + error
    - a_i: feature activation, v_i: feature vector (decoder weight)

This gives us:
    score = Σ_i Σ_j (a_i^k * a_j^q * v_i^T W_QK v_j)
          + Σ_i (a_i^k * bias_q^T W_QK v_i)
          + Σ_j (a_j^q * v_j^T W_QK bias_k)
          + bias_q^T W_QK bias_k
          + error terms
"""

from dataclasses import dataclass

import torch
import torch.nn.functional as F
from einops import einsum


@dataclass
class QKAttribution:
    """Represents a single QK attribution term.

    Attributes:
        query_feature_idx: Index of query-side feature (None for bias/error)
        key_feature_idx: Index of key-side feature (None for bias/error)
        contribution: Contribution to attention score
        query_activation: Query-side feature activation
        key_activation: Key-side feature activation
        query_feature_desc: Description of query feature
        key_feature_desc: Description of key feature

    """

    query_feature_idx: int | None
    key_feature_idx: int | None
    contribution: float
    query_activation: float
    key_activation: float
    query_feature_desc: str
    key_feature_desc: str

    @property
    def is_feature_interaction(self) -> bool:
        """True if this is a feature-feature interaction."""
        return self.query_feature_idx is not None and self.key_feature_idx is not None

    @property
    def is_bias_term(self) -> bool:
        """True if this involves a bias term."""
        return self.query_feature_idx is None or self.key_feature_idx is None

    def __repr__(self) -> str:
        return (
            f"QKAttribution(q={self.query_feature_desc}, "
            f"k={self.key_feature_desc}, "
            f"contribution={self.contribution:.4f})"
        )


@dataclass
class QKAttributionResult:
    """Complete QK attribution decomposition for a query-key position pair.

    Attributes:
        query_pos: Query position in context
        key_pos: Key position in context
        layer: Layer index
        head: Attention head index
        total_score: Total attention score (should equal sum of attributions)
        attributions: List of individual attribution terms
        attention_pattern: Full attention pattern for this head (after softmax)

    """

    query_pos: int
    key_pos: int
    layer: int
    head: int
    total_score: float
    attributions: list[QKAttribution]
    attention_pattern: torch.Tensor | None = None

    def get_top_k(self, k: int = 10, only_features: bool = True) -> list[QKAttribution]:
        """Get top-k attributions by absolute contribution.

        Args:
            k: Number of top attributions to return
            only_features: If True, only return feature-feature interactions

        Returns:
            List of top-k QKAttribution objects

        """
        attributions = self.attributions
        if only_features:
            attributions = [a for a in attributions if a.is_feature_interaction]

        return sorted(attributions, key=lambda x: abs(x.contribution), reverse=True)[:k]

    def get_positive_contributors(self, threshold: float = 0.01) -> list[QKAttribution]:
        """Get attributions with positive contribution above threshold."""
        return [
            a for a in self.attributions if a.contribution > threshold and a.is_feature_interaction
        ]

    def get_negative_contributors(self, threshold: float = -0.01) -> list[QKAttribution]:
        """Get attributions with negative contribution below threshold (inhibitory)."""
        return [
            a for a in self.attributions if a.contribution < threshold and a.is_feature_interaction
        ]

    def summarize(self, k: int = 5) -> str:
        """Generate human-readable summary of QK attributions."""
        lines = [
            f"QK Attribution Summary (Layer {self.layer}, Head {self.head})",
            f"Query Position: {self.query_pos}, Key Position: {self.key_pos}",
            f"Total Score: {self.total_score:.4f}",
            f"\nTop {k} Contributing Interactions:",
        ]

        for i, attr in enumerate(self.get_top_k(k=k), 1):
            lines.append(
                f"  {i}. {attr.query_feature_desc} × {attr.key_feature_desc}: "
                f"{attr.contribution:.4f}",
            )

        return "\n".join(lines)


class QKAttributor:
    """Computes QK attributions for transformer attention heads.

    This class implements the QK attribution algorithm from the paper, decomposing
    attention scores into interpretable feature-feature interactions.

    Args:
        W_Q: Query weight matrix [d_head, d_model] or [n_heads, d_head, d_model]
        W_K: Key weight matrix [d_head, d_model] or [n_heads, d_head, d_model]
        feature_vectors: Decoder vectors from SAE [n_features, d_model]
        feature_descriptions: Human-readable descriptions of each feature
        normalize_before_qk: If True, apply layer normalization before QK (e.g., for RoPE)

    """

    def __init__(
        self,
        W_Q: torch.Tensor,
        W_K: torch.Tensor,
        feature_vectors: torch.Tensor,
        feature_descriptions: list[str] | None = None,
        normalize_before_qk: bool = False,
    ):
        self.W_Q = W_Q
        self.W_K = W_K
        self.feature_vectors = feature_vectors
        self.normalize_before_qk = normalize_before_qk

        # Compute W_QK = W_Q^T @ W_K
        if W_Q.dim() == 3:  # Multiple heads
            self.W_QK = einsum(W_Q, W_K, "h dh dm1, h dh dm2 -> h dm1 dm2")
        else:  # Single head
            self.W_QK = einsum(W_Q, W_K, "dh dm1, dh dm2 -> dm1 dm2")

        # Feature descriptions
        if feature_descriptions is None:
            n_features = feature_vectors.shape[0]
            self.feature_descriptions = [f"Feature_{i}" for i in range(n_features)]
        else:
            self.feature_descriptions = feature_descriptions

        # Precompute feature projections through W_QK: v_i^T W_QK v_j
        self._precompute_feature_projections()

    def _precompute_feature_projections(self):
        """Precompute v_i^T W_QK v_j for all feature pairs.

        This is the core bilinear term in the QK attribution.
        Shape: [n_heads, n_features, n_features] or [n_features, n_features]
        """
        # Apply normalization if needed
        feature_vecs = self.feature_vectors
        if self.normalize_before_qk:
            feature_vecs = F.layer_norm(feature_vecs, (feature_vecs.shape[-1],))

        # Compute v^T W_QK for all features
        # v_proj[i] = W_QK @ v_i
        if self.W_QK.dim() == 3:  # Multiple heads
            # [n_heads, d_model, d_model] @ [n_features, d_model, 1]
            # -> [n_heads, n_features, d_model]
            v_proj = einsum(self.W_QK, feature_vecs, "h dm1 dm2, f dm2 -> h f dm1")
            # [n_heads, n_features, d_model] @ [n_features, d_model, 1]
            # -> [n_heads, n_features_q, n_features_k]
            self.feature_projections = einsum(feature_vecs, v_proj, "fq dm, h fk dm -> h fq fk")
        else:  # Single head
            v_proj = self.W_QK @ feature_vecs.T  # [d_model, n_features]
            self.feature_projections = feature_vecs @ v_proj  # [n_features, n_features]

    def compute_attention_score(
        self,
        key_activations: torch.Tensor,
        query_activations: torch.Tensor,
        key_bias: torch.Tensor | None = None,
        query_bias: torch.Tensor | None = None,
        head_idx: int | None = None,
    ) -> float:
        """Compute total attention score for a query-key pair.

        Args:
            key_activations: Feature activations at key position [n_features]
            query_activations: Feature activations at query position [n_features]
            key_bias: Bias term at key position [d_model]
            query_bias: Bias term at query position [d_model]
            head_idx: If W_Q, W_K have multiple heads, which head to use

        Returns:
            Total attention score (pre-softmax)

        """
        # Get feature projections for this head
        if self.feature_projections.dim() == 3:
            assert head_idx is not None, "Must specify head_idx for multi-head model"
            feat_proj = self.feature_projections[head_idx]  # [n_features, n_features]
        else:
            feat_proj = self.feature_projections

        # Feature-feature interactions: Σ_i Σ_j a_i^k * a_j^q * (v_i^T W_QK v_j)
        score = torch.sum(
            key_activations.unsqueeze(1) * query_activations.unsqueeze(0) * feat_proj,
        ).item()

        # Add bias terms if provided
        if key_bias is not None or query_bias is not None:
            W_QK = self.W_QK[head_idx] if self.W_QK.dim() == 3 else self.W_QK

            if key_bias is not None and query_bias is None:
                # Σ_i a_i^k * (v_i^T W_QK bias_q)
                bias_proj = self.feature_vectors @ W_QK @ key_bias
                score += torch.sum(key_activations * bias_proj).item()

            elif query_bias is not None and key_bias is None:
                # Σ_j a_j^q * (bias_k^T W_QK v_j)
                bias_proj = query_bias @ W_QK @ self.feature_vectors.T
                score += torch.sum(query_activations * bias_proj).item()

            elif key_bias is not None and query_bias is not None:
                # Feature-bias interactions
                key_bias_proj = self.feature_vectors @ W_QK @ key_bias
                score += torch.sum(key_activations * key_bias_proj).item()

                query_bias_proj = query_bias @ W_QK @ self.feature_vectors.T
                score += torch.sum(query_activations * query_bias_proj).item()

                # Pure bias term
                score += (query_bias @ W_QK @ key_bias).item()

        return score

    def compute_qk_attributions(
        self,
        key_activations: torch.Tensor,
        query_activations: torch.Tensor,
        query_pos: int,
        key_pos: int,
        layer: int,
        head_idx: int = 0,
        key_bias: torch.Tensor | None = None,
        query_bias: torch.Tensor | None = None,
        include_bias_terms: bool = True,
    ) -> QKAttributionResult:
        """Decompose attention score into feature-feature attributions.

        Args:
            key_activations: Feature activations at key position [n_features]
            query_activations: Feature activations at query position [n_features]
            query_pos: Query position in context
            key_pos: Key position in context
            layer: Layer index
            head_idx: Attention head index
            key_bias: Optional bias term at key position
            query_bias: Optional bias term at query position
            include_bias_terms: Whether to include bias term attributions

        Returns:
            QKAttributionResult with full decomposition

        """
        # Get feature projections for this head
        if self.feature_projections.dim() == 3:
            feat_proj = self.feature_projections[head_idx]
        else:
            feat_proj = self.feature_projections

        attributions = []

        # Feature-feature interactions
        for i in range(len(key_activations)):
            for j in range(len(query_activations)):
                contribution = (
                    key_activations[i].item() * query_activations[j].item() * feat_proj[i, j].item()
                )

                # Only include non-negligible contributions
                if abs(contribution) > 1e-6:
                    attributions.append(
                        QKAttribution(
                            query_feature_idx=j,
                            key_feature_idx=i,
                            contribution=contribution,
                            query_activation=query_activations[j].item(),
                            key_activation=key_activations[i].item(),
                            query_feature_desc=self.feature_descriptions[j],
                            key_feature_desc=self.feature_descriptions[i],
                        ),
                    )

        # Bias terms
        if include_bias_terms and (key_bias is not None or query_bias is not None):
            W_QK = self.W_QK[head_idx] if self.W_QK.dim() == 3 else self.W_QK

            if key_bias is not None:
                key_bias_proj = self.feature_vectors @ W_QK @ key_bias
                for j in range(len(query_activations)):
                    contribution = query_activations[j].item() * key_bias_proj[j].item()
                    if abs(contribution) > 1e-6:
                        attributions.append(
                            QKAttribution(
                                query_feature_idx=j,
                                key_feature_idx=None,
                                contribution=contribution,
                                query_activation=query_activations[j].item(),
                                key_activation=1.0,
                                query_feature_desc=self.feature_descriptions[j],
                                key_feature_desc="[BIAS]",
                            ),
                        )

            if query_bias is not None:
                query_bias_proj = query_bias @ W_QK @ self.feature_vectors.T
                for i in range(len(key_activations)):
                    contribution = key_activations[i].item() * query_bias_proj[i].item()
                    if abs(contribution) > 1e-6:
                        attributions.append(
                            QKAttribution(
                                query_feature_idx=None,
                                key_feature_idx=i,
                                contribution=contribution,
                                query_activation=1.0,
                                key_activation=key_activations[i].item(),
                                query_feature_desc="[BIAS]",
                                key_feature_desc=self.feature_descriptions[i],
                            ),
                        )

        # Compute total score
        total_score = sum(a.contribution for a in attributions)

        return QKAttributionResult(
            query_pos=query_pos,
            key_pos=key_pos,
            layer=layer,
            head=head_idx,
            total_score=total_score,
            attributions=attributions,
        )


def compute_qk_attributions(
    model: torch.nn.Module,
    input_ids: torch.Tensor,
    sae_features: dict[int, tuple[torch.Tensor, torch.Tensor, list[str]]],
    layer: int,
    head: int,
    query_pos: int,
    key_pos: int,
) -> QKAttributionResult:
    """Convenience function to compute QK attributions from a model.

    Args:
        model: Transformer model
        input_ids: Input token IDs [batch_size, seq_len]
        sae_features: Dict mapping layer -> (activations, feature_vectors, descriptions)
                     activations: [batch, seq_len, n_features]
                     feature_vectors: [n_features, d_model]
                     descriptions: List of feature descriptions
        layer: Layer to analyze
        head: Head to analyze
        query_pos: Query position
        key_pos: Key position

    Returns:
        QKAttributionResult

    """
    # Extract attention weights
    # This is model-specific - adjust based on your model architecture
    attn_layer = model.transformer.h[layer].attn  # Example for GPT-2 style
    W_Q = attn_layer.c_attn.weight[:, : attn_layer.embed_dim]  # Simplified
    W_K = attn_layer.c_attn.weight[:, attn_layer.embed_dim : 2 * attn_layer.embed_dim]

    # Get SAE features for this layer
    activations, feature_vectors, descriptions = sae_features[layer]

    # Extract activations at query and key positions
    query_acts = activations[0, query_pos]  # [n_features]
    key_acts = activations[0, key_pos]  # [n_features]

    # Create attributor
    attributor = QKAttributor(W_Q, W_K, feature_vectors, descriptions)

    # Compute attributions
    return attributor.compute_qk_attributions(
        key_activations=key_acts,
        query_activations=query_acts,
        query_pos=query_pos,
        key_pos=key_pos,
        layer=layer,
        head_idx=head,
    )


def compute_attention_scores(
    attributor: QKAttributor,
    key_activations: torch.Tensor,
    query_activations: torch.Tensor,
    head_idx: int = 0,
    apply_softmax: bool = True,
) -> torch.Tensor:
    """Compute attention scores for all query-key pairs.

    Args:
        attributor: QKAttributor instance
        key_activations: Feature activations at all key positions [seq_len, n_features]
        query_activations: Feature activations at all query positions [seq_len, n_features]
        head_idx: Head index
        apply_softmax: If True, apply softmax to get attention pattern

    Returns:
        Attention scores [seq_len_q, seq_len_k] or pattern after softmax

    """
    seq_len_k, n_features_k = key_activations.shape
    seq_len_q, n_features_q = query_activations.shape

    # Get feature projections
    if attributor.feature_projections.dim() == 3:
        feat_proj = attributor.feature_projections[head_idx]
    else:
        feat_proj = attributor.feature_projections

    # Compute all pairwise scores using einsum
    # key_acts: [seq_k, n_feat]
    # query_acts: [seq_q, n_feat]
    # feat_proj: [n_feat, n_feat]
    # Result: [seq_q, seq_k]
    scores = einsum(
        query_activations,
        feat_proj,
        key_activations,
        "sq nf1, nf1 nf2, sk nf2 -> sq sk",
    )

    if apply_softmax:
        return F.softmax(scores, dim=-1)
    return scores
