# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Attribution Graph: Represent transformer forward pass as interpretable causal graphs.

Based on the paper "Tracing Attention Computation Through Feature Interactions" (2025).

Attribution graphs represent the computation of a transformer as a directed acyclic graph (DAG)
where:
- Nodes represent SAE features at specific (layer, position) locations
- Edges represent attributions (influence) from source to target features
- Edges are annotated with head loadings showing which attention heads mediate them

This module provides tools to construct, analyze, and visualize attribution graphs enriched
with QK attribution information.
"""

from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
import torch

from transformer_circuits.head_loadings import EdgeAttribution, HeadLoading
from transformer_circuits.qk_attribution import QKAttributionResult


@dataclass
class AttributionNode:
    """Represents a feature at a specific (layer, position) in the computation graph.

    Attributes:
        feature_idx: Index of the SAE feature
        feature_desc: Human-readable description of the feature
        layer: Layer index
        position: Context position
        activation: Activation value of the feature
        node_id: Unique identifier for this node

    """

    feature_idx: int
    feature_desc: str
    layer: int
    position: int
    activation: float
    node_id: str = field(init=False)

    def __post_init__(self):
        self.node_id = f"L{self.layer}_P{self.position}_F{self.feature_idx}"

    def __hash__(self):
        return hash(self.node_id)

    def __eq__(self, other):
        return isinstance(other, AttributionNode) and self.node_id == other.node_id

    def __repr__(self):
        return f"Node({self.feature_desc}, L{self.layer}, pos={self.position}, act={self.activation:.3f})"


@dataclass
class AttributionEdge:
    """Represents an attribution edge between two features.

    Attributes:
        source: Source node
        target: Target node
        attribution: Total attribution value
        edge_attribution: Detailed edge attribution with head loadings
        qk_attributions: Optional QK attributions for heads mediating this edge

    """

    source: AttributionNode
    target: AttributionNode
    attribution: float
    edge_attribution: EdgeAttribution | None = None
    qk_attributions: dict[tuple[int, int], QKAttributionResult] = field(default_factory=dict)
    # Key: (layer, head) -> QKAttributionResult

    @property
    def crosses_positions(self) -> bool:
        """True if edge connects different context positions."""
        return self.source.position != self.target.position

    @property
    def mediating_heads(self) -> list[HeadLoading]:
        """Get heads that mediate this edge."""
        if self.edge_attribution:
            return self.edge_attribution.head_loadings
        return []

    @property
    def top_mediating_heads(self) -> list[HeadLoading]:
        """Get top contributing heads."""
        if self.edge_attribution:
            return self.edge_attribution.get_top_heads(k=5)
        return []

    def get_qk_attribution_for_head(self, layer: int, head: int) -> QKAttributionResult | None:
        """Get QK attribution for a specific head."""
        return self.qk_attributions.get((layer, head))

    def __repr__(self):
        heads_str = ""
        if self.mediating_heads:
            top_heads = self.edge_attribution.get_top_heads(k=2)
            heads_str = f", heads=[{', '.join(f'L{h.layer}H{h.head}' for h in top_heads)}...]"

        return (
            f"Edge({self.source.feature_desc} -> {self.target.feature_desc}, "
            f"attr={self.attribution:.3f}{heads_str})"
        )


class AttributionGraph:
    """Attribution graph representing transformer computation.

    This class provides tools to construct, prune, analyze, and visualize
    attribution graphs enriched with QK attribution information.

    Attributes:
        nodes: Set of all nodes in the graph
        edges: List of all edges in the graph
        adjacency: Dict mapping node_id -> list of outgoing edges
        reverse_adjacency: Dict mapping node_id -> list of incoming edges

    """

    def __init__(self):
        self.nodes: set[AttributionNode] = set()
        self.edges: list[AttributionEdge] = []
        self.adjacency: dict[str, list[AttributionEdge]] = defaultdict(list)
        self.reverse_adjacency: dict[str, list[AttributionEdge]] = defaultdict(list)
        self._node_map: dict[str, AttributionNode] = {}

    def add_node(self, node: AttributionNode) -> AttributionNode:
        """Add a node to the graph (idempotent)."""
        if node.node_id not in self._node_map:
            self.nodes.add(node)
            self._node_map[node.node_id] = node
        return self._node_map[node.node_id]

    def add_edge(self, edge: AttributionEdge):
        """Add an edge to the graph."""
        # Ensure nodes are in graph
        edge.source = self.add_node(edge.source)
        edge.target = self.add_node(edge.target)

        # Add edge
        self.edges.append(edge)
        self.adjacency[edge.source.node_id].append(edge)
        self.reverse_adjacency[edge.target.node_id].append(edge)

    def get_node(self, layer: int, position: int, feature_idx: int) -> AttributionNode | None:
        """Get node by (layer, position, feature_idx)."""
        node_id = f"L{layer}_P{position}_F{feature_idx}"
        return self._node_map.get(node_id)

    def get_outgoing_edges(self, node: AttributionNode) -> list[AttributionEdge]:
        """Get all outgoing edges from a node."""
        return self.adjacency[node.node_id]

    def get_incoming_edges(self, node: AttributionNode) -> list[AttributionEdge]:
        """Get all incoming edges to a node."""
        return self.reverse_adjacency[node.node_id]

    def prune_by_attribution(self, threshold: float = 0.01) -> "AttributionGraph":
        """Create pruned graph keeping only edges with |attribution| > threshold.

        Args:
            threshold: Minimum absolute attribution to keep edge

        Returns:
            New pruned AttributionGraph

        """
        pruned = AttributionGraph()

        for edge in self.edges:
            if abs(edge.attribution) > threshold:
                pruned.add_edge(edge)

        return pruned

    def prune_to_path(
        self,
        start_node: AttributionNode,
        end_node: AttributionNode,
        max_paths: int = 10,
    ) -> "AttributionGraph":
        """Create pruned graph containing only paths from start to end.

        Args:
            start_node: Starting node
            end_node: Ending node
            max_paths: Maximum number of paths to include

        Returns:
            New pruned AttributionGraph

        """
        # Find paths using DFS
        paths = self._find_paths(start_node, end_node, max_paths)

        # Create pruned graph with edges from paths
        pruned = AttributionGraph()
        for path in paths:
            for edge in path:
                if edge not in pruned.edges:
                    pruned.add_edge(edge)

        return pruned

    def _find_paths(
        self,
        start: AttributionNode,
        end: AttributionNode,
        max_paths: int,
    ) -> list[list[AttributionEdge]]:
        """Find paths from start to end using DFS."""
        paths = []
        visited = set()

        def dfs(current: AttributionNode, path: list[AttributionEdge]):
            if len(paths) >= max_paths:
                return

            if current == end:
                paths.append(path.copy())
                return

            if current.node_id in visited:
                return

            visited.add(current.node_id)

            for edge in self.get_outgoing_edges(current):
                dfs(edge.target, path + [edge])

            visited.remove(current.node_id)

        dfs(start, [])
        return paths

    def get_nodes_by_layer(self, layer: int) -> list[AttributionNode]:
        """Get all nodes at a specific layer."""
        return [n for n in self.nodes if n.layer == layer]

    def get_nodes_by_position(self, position: int) -> list[AttributionNode]:
        """Get all nodes at a specific position."""
        return [n for n in self.nodes if n.position == position]

    def get_cross_position_edges(self) -> list[AttributionEdge]:
        """Get all edges that cross context positions."""
        return [e for e in self.edges if e.crosses_positions]

    def get_attention_mediated_edges(
        self,
        min_attention_fraction: float = 0.5,
    ) -> list[AttributionEdge]:
        """Get edges where attention component is dominant.

        Args:
            min_attention_fraction: Minimum fraction of attribution from attention

        Returns:
            List of attention-mediated edges

        """
        result = []
        for edge in self.edges:
            if edge.edge_attribution:
                attn_frac = abs(edge.edge_attribution.attention_component) / abs(edge.attribution)
                if attn_frac >= min_attention_fraction:
                    result.append(edge)
        return result

    def analyze_head_usage(self) -> dict[tuple[int, int], float]:
        """Analyze which heads are used most across the graph.

        Returns:
            Dict mapping (layer, head) -> total contribution across all edges

        """
        head_contributions = defaultdict(float)

        for edge in self.edges:
            if edge.edge_attribution:
                for head_loading in edge.edge_attribution.head_loadings:
                    key = (head_loading.layer, head_loading.head)
                    head_contributions[key] += abs(head_loading.contribution)

        return dict(head_contributions)

    def get_feature_importance(self, layer: int | None = None) -> dict[str, float]:
        """Compute feature importance based on total attribution flowing through.

        Args:
            layer: If specified, only compute for nodes at this layer

        Returns:
            Dict mapping node_id -> total attribution (in + out)

        """
        importance = defaultdict(float)

        for edge in self.edges:
            if layer is None or edge.source.layer == layer:
                importance[edge.source.node_id] += abs(edge.attribution)
            if layer is None or edge.target.layer == layer:
                importance[edge.target.node_id] += abs(edge.attribution)

        return dict(importance)

    def to_dict(self) -> dict:
        """Convert graph to dictionary for serialization."""
        return {
            "nodes": [
                {
                    "id": n.node_id,
                    "feature_idx": n.feature_idx,
                    "feature_desc": n.feature_desc,
                    "layer": n.layer,
                    "position": n.position,
                    "activation": n.activation,
                }
                for n in self.nodes
            ],
            "edges": [
                {
                    "source": e.source.node_id,
                    "target": e.target.node_id,
                    "attribution": e.attribution,
                    "top_heads": [
                        {"layer": h.layer, "head": h.head, "contribution": h.contribution}
                        for h in e.top_mediating_heads[:3]
                    ]
                    if e.edge_attribution
                    else [],
                }
                for e in self.edges
            ],
        }

    def summarize(self) -> str:
        """Generate summary statistics of the graph."""
        cross_pos_edges = len(self.get_cross_position_edges())
        attn_edges = len(self.get_attention_mediated_edges())

        lines = [
            "Attribution Graph Summary",
            f"  Nodes: {len(self.nodes)}",
            f"  Edges: {len(self.edges)}",
            f"  Cross-position edges: {cross_pos_edges} ({100 * cross_pos_edges / len(self.edges):.1f}%)",
            f"  Attention-mediated edges: {attn_edges} ({100 * attn_edges / len(self.edges):.1f}%)",
            f"\nLayers: {min(n.layer for n in self.nodes)} to {max(n.layer for n in self.nodes)}",
            f"Positions: {min(n.position for n in self.nodes)} to {max(n.position for n in self.nodes)}",
        ]

        # Top heads
        head_usage = self.analyze_head_usage()
        if head_usage:
            top_heads = sorted(head_usage.items(), key=lambda x: x[1], reverse=True)[:5]
            lines.append("\nTop 5 Most Used Heads:")
            for (layer, head), contrib in top_heads:
                lines.append(f"  L{layer}H{head}: {contrib:.3f}")

        return "\n".join(lines)


class AttributionGraphBuilder:
    """Builder for constructing attribution graphs from model activations.

    This class provides a convenient interface to build attribution graphs
    from SAE features and model components.
    """

    def __init__(
        self,
        sae_activations: dict[int, torch.Tensor],
        sae_features: dict[int, torch.Tensor],
        sae_descriptions: dict[int, list[str]],
        seq_length: int,
    ):
        """Initialize graph builder.

        Args:
            sae_activations: Dict mapping layer -> activations [seq_len, n_features]
            sae_features: Dict mapping layer -> feature vectors [n_features, d_model]
            sae_descriptions: Dict mapping layer -> list of feature descriptions
            seq_length: Sequence length

        """
        self.sae_activations = sae_activations
        self.sae_features = sae_features
        self.sae_descriptions = sae_descriptions
        self.seq_length = seq_length
        self.graph = AttributionGraph()

    def add_nodes_from_activations(
        self,
        layer: int,
        position: int,
        top_k: int = 20,
        min_activation: float = 0.1,
    ) -> list[AttributionNode]:
        """Add nodes for top-k activated features at (layer, position).

        Args:
            layer: Layer index
            position: Position index
            top_k: Number of top features to add
            min_activation: Minimum activation threshold

        Returns:
            List of added nodes

        """
        activations = self.sae_activations[layer][position]
        top_indices = torch.topk(activations, k=min(top_k, len(activations))).indices

        nodes = []
        for idx in top_indices:
            act = activations[idx].item()
            if act >= min_activation:
                node = AttributionNode(
                    feature_idx=idx.item(),
                    feature_desc=self.sae_descriptions[layer][idx.item()],
                    layer=layer,
                    position=position,
                    activation=act,
                )
                self.graph.add_node(node)
                nodes.append(node)

        return nodes

    def build_from_logit(
        self,
        target_logit_feature: tuple[int, int, int],  # (layer, position, feature_idx)
        max_depth: int = 3,
        top_k_per_layer: int = 10,
        min_attribution: float = 0.01,
    ) -> AttributionGraph:
        """Build graph by tracing backwards from a target logit.

        Args:
            target_logit_feature: (layer, position, feature_idx) of target
            max_depth: Maximum depth to trace backwards
            top_k_per_layer: Top-k features to consider per layer
            min_attribution: Minimum attribution to include edge

        Returns:
            Constructed AttributionGraph

        """
        layer, position, feature_idx = target_logit_feature

        # Add target node
        target_node = AttributionNode(
            feature_idx=feature_idx,
            feature_desc=self.sae_descriptions[layer][feature_idx],
            layer=layer,
            position=position,
            activation=self.sae_activations[layer][position, feature_idx].item(),
        )
        self.graph.add_node(target_node)

        # Trace backwards
        self._trace_backwards(target_node, max_depth, top_k_per_layer, min_attribution)

        return self.graph

    def _trace_backwards(
        self,
        target_node: AttributionNode,
        depth_remaining: int,
        top_k: int,
        min_attribution: float,
    ):
        """Recursively trace backwards from target node."""
        if depth_remaining == 0 or target_node.layer == 0:
            return

        source_layer = target_node.layer - 1

        # For same position and adjacent positions
        for source_pos in range(
            max(0, target_node.position - 1),
            min(self.seq_length, target_node.position + 2),
        ):
            # Get top-k active features at source
            activations = self.sae_activations[source_layer][source_pos]
            top_indices = torch.topk(activations, k=top_k).indices

            for source_idx in top_indices:
                # Create source node
                source_node = AttributionNode(
                    feature_idx=source_idx.item(),
                    feature_desc=self.sae_descriptions[source_layer][source_idx.item()],
                    layer=source_layer,
                    position=source_pos,
                    activation=activations[source_idx].item(),
                )
                self.graph.add_node(source_node)

                # Compute attribution (simplified - in practice would use gradients)
                # This is a placeholder
                attribution = (
                    source_node.activation * target_node.activation * np.random.rand() * 0.1
                )  # Placeholder

                if abs(attribution) > min_attribution:
                    edge = AttributionEdge(
                        source=source_node,
                        target=target_node,
                        attribution=attribution,
                    )
                    self.graph.add_edge(edge)

                    # Recurse
                    self._trace_backwards(source_node, depth_remaining - 1, top_k, min_attribution)
