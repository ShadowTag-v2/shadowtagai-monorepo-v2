"""
Head Loadings: Compute attention head contributions to attribution graph edges.

Based on the paper "Tracing Attention Computation Through Feature Interactions" (2025).

The key challenge: when transcoder features are separated by L layers, the number of
possible attention head paths grows exponentially with L. To solve this, we "checkpoint"
attributions at each layer using SAEs on residual streams.

For an edge between two SAE features in adjacent layers, the attribution decomposes as:
    attribution = attention_component + mlp_component + residual_component

The attention component can be further decomposed by head:
    attention_component = Σ_h (a_source * a_target * v_target^T O_h V_h v_source * attn_h(p_s, p_t))

where:
    - a_source, a_target: feature activations
    - v_source, v_target: feature vectors (SAE decoder weights)
    - O_h, V_h: output and value matrices for head h
    - attn_h(p_s, p_t): attention pattern of head h from source to target position
"""

from dataclasses import dataclass

import torch
from einops import einsum


@dataclass
class HeadLoading:
    """Represents the contribution of a single attention head to a graph edge.

    Attributes:
        layer: Layer index of the attention head
        head: Head index within the layer
        contribution: Contribution to the edge (can be positive or negative)
        attention_weight: Attention pattern value at (source_pos, target_pos)
        ov_projection: v_target^T O_h V_h v_source (OV circuit projection)
    """

    layer: int
    head: int
    contribution: float
    attention_weight: float
    ov_projection: float

    def __repr__(self) -> str:
        return (
            f"HeadLoading(L{self.layer}H{self.head}, "
            f"contrib={self.contribution:.4f}, "
            f"attn={self.attention_weight:.4f})"
        )


@dataclass
class EdgeAttribution:
    """Complete attribution for an edge in the attribution graph.

    Attributes:
        source_feature: Source feature index/description
        target_feature: Target feature index/description
        source_pos: Source context position
        target_pos: Target context position
        source_layer: Source layer
        target_layer: Target layer
        total_attribution: Total attribution value
        attention_component: Total attention-mediated component
        mlp_component: MLP-mediated component
        residual_component: Residual connection component
        head_loadings: Individual head contributions
    """

    source_feature: str
    target_feature: str
    source_pos: int
    target_pos: int
    source_layer: int
    target_layer: int
    total_attribution: float
    attention_component: float
    mlp_component: float
    residual_component: float
    head_loadings: list[HeadLoading]

    def get_top_heads(self, k: int = 5) -> list[HeadLoading]:
        """Get top-k heads by absolute contribution."""
        return sorted(self.head_loadings, key=lambda x: abs(x.contribution), reverse=True)[:k]

    def get_significant_heads(self, threshold: float = 0.01) -> list[HeadLoading]:
        """Get heads with contribution above threshold (as fraction of total)."""
        abs_threshold = abs(self.total_attribution) * threshold
        return [h for h in self.head_loadings if abs(h.contribution) > abs_threshold]

    def summarize(self, k: int = 3) -> str:
        """Generate human-readable summary."""
        lines = [
            f"Edge: {self.source_feature} (L{self.source_layer}, pos={self.source_pos})",
            f"   -> {self.target_feature} (L{self.target_layer}, pos={self.target_pos})",
            f"Total Attribution: {self.total_attribution:.4f}",
            f"  Attention: {self.attention_component:.4f} "
            f"({100 * self.attention_component / self.total_attribution:.1f}%)",
            f"  MLP: {self.mlp_component:.4f}",
            f"  Residual: {self.residual_component:.4f}",
            f"\nTop {k} Contributing Heads:",
        ]

        for i, head in enumerate(self.get_top_heads(k), 1):
            pct = (
                100 * head.contribution / self.attention_component
                if self.attention_component != 0
                else 0
            )
            lines.append(
                f"  {i}. L{head.layer}H{head.head}: {head.contribution:.4f} ({pct:.1f}% of attn)"
            )

        return "\n".join(lines)


class HeadLoadingComputer:
    """Computes head loadings for attribution graph edges.

    This class implements the head loading algorithm, decomposing edges into
    contributions from individual attention heads.

    Args:
        W_V: Value weight matrices [n_layers, n_heads, d_head, d_model]
        W_O: Output weight matrices [n_layers, n_heads, d_model, d_head]
        attention_patterns: Attention patterns [n_layers, n_heads, seq_len, seq_len]
        feature_vectors: SAE decoder vectors per layer, dict: layer -> [n_features, d_model]
    """

    def __init__(
        self,
        W_V: dict[int, torch.Tensor],
        W_O: dict[int, torch.Tensor],
        attention_patterns: dict[int, torch.Tensor],
        feature_vectors: dict[int, torch.Tensor],
    ):
        self.W_V = W_V
        self.W_O = W_O
        self.attention_patterns = attention_patterns
        self.feature_vectors = feature_vectors

        # Precompute OV circuits: O_h @ V_h for each head
        self.W_OV = {}
        for layer in W_V:
            # W_V[layer]: [n_heads, d_head, d_model]
            # W_O[layer]: [n_heads, d_model, d_head]
            # W_OV: [n_heads, d_model, d_model]
            self.W_OV[layer] = einsum(W_O[layer], W_V[layer], "h dm dh, h dh dm2 -> h dm dm2")

    def _compute_ov_projections(
        self,
        source_feature_vec: torch.Tensor,
        target_feature_vec: torch.Tensor,
        layer: int,
    ) -> torch.Tensor:
        """Compute v_target^T W_OV_h v_source for all heads in layer.

        Args:
            source_feature_vec: Source feature vector [d_model]
            target_feature_vec: Target feature vector [d_model]
            layer: Layer index

        Returns:
            OV projections for all heads [n_heads]
        """
        # [n_heads, d_model, d_model] @ [d_model] -> [n_heads, d_model]
        ov_source = einsum(self.W_OV[layer], source_feature_vec, "h dm1 dm2, dm2 -> h dm1")

        # [d_model] @ [n_heads, d_model] -> [n_heads]
        ov_projections = einsum(target_feature_vec, ov_source, "dm, h dm -> h")

        return ov_projections

    def compute_head_loadings(
        self,
        source_feature_idx: int,
        target_feature_idx: int,
        source_activation: float,
        target_activation: float,
        source_pos: int,
        target_pos: int,
        source_layer: int,
        target_layer: int,
    ) -> list[HeadLoading]:
        """Compute head loadings for an edge between two features.

        Args:
            source_feature_idx: Index of source feature
            target_feature_idx: Index of target feature
            source_activation: Activation of source feature
            target_activation: Activation of target feature
            source_pos: Source context position
            target_pos: Target context position
            source_layer: Source layer (should be target_layer - 1)
            target_layer: Target layer

        Returns:
            List of HeadLoading objects for each head
        """
        assert target_layer == source_layer + 1, "Head loadings only defined for adjacent layers"

        # Get feature vectors
        source_vec = self.feature_vectors[source_layer][source_feature_idx]
        target_vec = self.feature_vectors[target_layer][target_feature_idx]

        # Compute OV projections for all heads in source layer
        ov_projections = self._compute_ov_projections(source_vec, target_vec, source_layer)

        # Get attention patterns for all heads
        # attention_patterns[layer]: [n_heads, seq_len, seq_len]
        attention_weights = self.attention_patterns[source_layer][:, target_pos, source_pos]
        # Shape: [n_heads]

        # Compute contribution for each head
        # contribution_h = a_source * a_target * ov_projection_h * attention_weight_h
        head_loadings = []
        n_heads = ov_projections.shape[0]

        for head_idx in range(n_heads):
            contribution = (
                source_activation
                * target_activation
                * ov_projections[head_idx].item()
                * attention_weights[head_idx].item()
            )

            head_loadings.append(
                HeadLoading(
                    layer=source_layer,
                    head=head_idx,
                    contribution=contribution,
                    attention_weight=attention_weights[head_idx].item(),
                    ov_projection=ov_projections[head_idx].item(),
                )
            )

        return head_loadings

    def compute_edge_attribution(
        self,
        source_feature_idx: int,
        target_feature_idx: int,
        source_activation: float,
        target_activation: float,
        source_pos: int,
        target_pos: int,
        source_layer: int,
        target_layer: int,
        source_feature_desc: str = None,
        target_feature_desc: str = None,
        mlp_contribution: float | None = None,
        residual_contribution: float | None = None,
    ) -> EdgeAttribution:
        """Compute complete edge attribution including all components.

        Args:
            source_feature_idx: Index of source feature
            target_feature_idx: Index of target feature
            source_activation: Activation of source feature
            target_activation: Activation of target feature
            source_pos: Source context position
            target_pos: Target context position
            source_layer: Source layer
            target_layer: Target layer
            source_feature_desc: Description of source feature
            target_feature_desc: Description of target feature
            mlp_contribution: Optional precomputed MLP contribution
            residual_contribution: Optional precomputed residual contribution

        Returns:
            EdgeAttribution object
        """
        # Compute head loadings
        head_loadings = self.compute_head_loadings(
            source_feature_idx=source_feature_idx,
            target_feature_idx=target_feature_idx,
            source_activation=source_activation,
            target_activation=target_activation,
            source_pos=source_pos,
            target_pos=target_pos,
            source_layer=source_layer,
            target_layer=target_layer,
        )

        # Sum up attention component
        attention_component = sum(h.contribution for h in head_loadings)

        # Use provided MLP and residual contributions, or estimate as 0
        mlp_comp = mlp_contribution if mlp_contribution is not None else 0.0
        res_comp = residual_contribution if residual_contribution is not None else 0.0

        # Total attribution
        total_attr = attention_component + mlp_comp + res_comp

        # Feature descriptions
        source_desc = source_feature_desc or f"Feature_{source_feature_idx}"
        target_desc = target_feature_desc or f"Feature_{target_feature_idx}"

        return EdgeAttribution(
            source_feature=source_desc,
            target_feature=target_desc,
            source_pos=source_pos,
            target_pos=target_pos,
            source_layer=source_layer,
            target_layer=target_layer,
            total_attribution=total_attr,
            attention_component=attention_component,
            mlp_component=mlp_comp,
            residual_component=res_comp,
            head_loadings=head_loadings,
        )


def compute_head_loadings(
    model: torch.nn.Module,
    input_ids: torch.Tensor,
    sae_features: dict[int, tuple[torch.Tensor, torch.Tensor, list[str]]],
    source_feature_idx: int,
    target_feature_idx: int,
    source_pos: int,
    target_pos: int,
    source_layer: int,
    target_layer: int,
) -> EdgeAttribution:
    """Convenience function to compute head loadings from a model.

    Args:
        model: Transformer model
        input_ids: Input token IDs
        sae_features: Dict mapping layer -> (activations, feature_vectors, descriptions)
        source_feature_idx: Source feature index
        target_feature_idx: Target feature index
        source_pos: Source position
        target_pos: Target position
        source_layer: Source layer
        target_layer: Target layer

    Returns:
        EdgeAttribution object
    """
    # Extract model components (model-specific)
    W_V = {}
    W_O = {}
    attention_patterns = {}
    feature_vectors = {}

    for layer in range(source_layer, target_layer):
        attn = model.transformer.h[layer].attn  # Example for GPT-2 style
        W_V[layer] = attn.v_proj.weight  # [n_heads * d_head, d_model]
        W_O[layer] = attn.o_proj.weight  # [d_model, n_heads * d_head]

        # Get attention pattern (would need to run forward pass with hooks)
        # This is a placeholder - actual implementation would capture from forward pass
        attention_patterns[layer] = torch.zeros(
            attn.num_heads, len(input_ids[0]), len(input_ids[0])
        )

        # Get feature vectors
        _, feature_vecs, _ = sae_features[layer]
        feature_vectors[layer] = feature_vecs

    # Create computer
    computer = HeadLoadingComputer(W_V, W_O, attention_patterns, feature_vectors)

    # Get activations
    source_acts, _, source_descs = sae_features[source_layer]
    target_acts, _, target_descs = sae_features[target_layer]

    source_act = source_acts[0, source_pos, source_feature_idx].item()
    target_act = target_acts[0, target_pos, target_feature_idx].item()

    # Compute edge attribution
    return computer.compute_edge_attribution(
        source_feature_idx=source_feature_idx,
        target_feature_idx=target_feature_idx,
        source_activation=source_act,
        target_activation=target_act,
        source_pos=source_pos,
        target_pos=target_pos,
        source_layer=source_layer,
        target_layer=target_layer,
        source_feature_desc=source_descs[source_feature_idx],
        target_feature_desc=target_descs[target_feature_idx],
    )


class MultiLayerHeadLoadingComputer:
    """Computes head loadings across multiple layers with path tracking.

    For edges that span multiple layers, we need to track attention paths.
    This class handles the exponential path problem by using SAE checkpointing.
    """

    def __init__(
        self,
        W_V: dict[int, torch.Tensor],
        W_O: dict[int, torch.Tensor],
        attention_patterns: dict[int, torch.Tensor],
        feature_vectors: dict[int, torch.Tensor],
        sae_activations: dict[int, torch.Tensor],
    ):
        self.W_V = W_V
        self.W_O = W_O
        self.attention_patterns = attention_patterns
        self.feature_vectors = feature_vectors
        self.sae_activations = sae_activations

        # Create single-layer computers for each layer
        self.layer_computers = {}
        for layer in W_V:
            self.layer_computers[layer] = HeadLoadingComputer(
                {layer: W_V[layer]},
                {layer: W_O[layer]},
                {layer: attention_patterns[layer]},
                {
                    layer: feature_vectors[layer],
                    layer + 1: feature_vectors.get(layer + 1, feature_vectors[layer]),
                },
            )

    def compute_multi_hop_attribution(
        self,
        source_feature_idx: int,
        target_feature_idx: int,
        source_pos: int,
        target_pos: int,
        source_layer: int,
        target_layer: int,
        max_intermediate_features: int = 10,
    ) -> list[EdgeAttribution]:
        """Compute attribution through intermediate SAE features.

        This traces paths: source -> intermediate_features -> target
        where intermediate features act as "checkpoints" at each layer.

        Args:
            source_feature_idx: Source feature index
            target_feature_idx: Target feature index
            source_pos: Source position
            target_pos: Target position
            source_layer: Source layer
            target_layer: Target layer (must be > source_layer + 1)
            max_intermediate_features: Max number of intermediate features to consider per layer

        Returns:
            List of EdgeAttribution objects for the important paths
        """
        if target_layer == source_layer + 1:
            # Direct edge - use single-layer computation
            return [
                self.layer_computers[source_layer].compute_edge_attribution(
                    source_feature_idx,
                    target_feature_idx,
                    self.sae_activations[source_layer][source_pos, source_feature_idx].item(),
                    self.sae_activations[target_layer][target_pos, target_feature_idx].item(),
                    source_pos,
                    target_pos,
                    source_layer,
                    target_layer,
                )
            ]

        # Multi-hop: need to find important intermediate features
        paths = []

        # For each intermediate layer, find top-k active features
        for intermediate_layer in range(source_layer + 1, target_layer):
            # Get top active features at intermediate position
            intermediate_acts = self.sae_activations[intermediate_layer][target_pos]
            top_features = torch.topk(intermediate_acts, k=max_intermediate_features).indices

            for intermediate_idx in top_features:
                # Compute source -> intermediate
                edge1 = self.layer_computers[source_layer].compute_edge_attribution(
                    source_feature_idx,
                    intermediate_idx.item(),
                    self.sae_activations[source_layer][source_pos, source_feature_idx].item(),
                    intermediate_acts[intermediate_idx].item(),
                    source_pos,
                    target_pos,
                    source_layer,
                    intermediate_layer,
                )

                # Compute intermediate -> target
                edge2 = self.layer_computers[intermediate_layer].compute_edge_attribution(
                    intermediate_idx.item(),
                    target_feature_idx,
                    intermediate_acts[intermediate_idx].item(),
                    self.sae_activations[target_layer][target_pos, target_feature_idx].item(),
                    target_pos,
                    target_pos,
                    intermediate_layer,
                    target_layer,
                )

                # Combine paths
                paths.append((edge1, edge2))

        return paths
