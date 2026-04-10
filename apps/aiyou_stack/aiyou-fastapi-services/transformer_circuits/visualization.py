"""
Visualization utilities for transformer circuits.

Provides tools to visualize:
- QK attribution matrices
- Attribution graphs
- Head loading distributions
- Feature steering effects
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from transformer_circuits.attribution_graph import AttributionGraph
from transformer_circuits.head_loadings import EdgeAttribution
from transformer_circuits.qk_attribution import QKAttributionResult


def plot_qk_attribution_matrix(
    result: QKAttributionResult,
    top_k: int = 20,
    save_path: str | None = None,
) -> go.Figure:
    """
    Visualize QK attributions as a matrix heatmap.

    Shows the bilinear interaction matrix between query and key features,
    highlighting which feature pairs contribute most to the attention score.

    Args:
        result: QKAttributionResult to visualize
        top_k: Number of top features to show on each side
        save_path: Optional path to save figure

    Returns:
        Plotly figure
    """
    # Get top contributing features
    top_attrs = result.get_top_k(k=top_k, only_features=True)

    # Build matrix
    query_features = list(set(a.query_feature_desc for a in top_attrs))
    key_features = list(set(a.key_feature_desc for a in top_attrs))

    matrix = np.zeros((len(query_features), len(key_features)))
    for attr in top_attrs:
        if attr.query_feature_desc in query_features and attr.key_feature_desc in key_features:
            i = query_features.index(attr.query_feature_desc)
            j = key_features.index(attr.key_feature_desc)
            matrix[i, j] = attr.contribution

    # Create heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            x=key_features,
            y=query_features,
            colorscale="RdBu_r",
            zmid=0,
            text=np.round(matrix, 3),
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar=dict(title="Contribution"),
        )
    )

    fig.update_layout(
        title=f"QK Attribution Matrix (Layer {result.layer}, Head {result.head})<br>"
        f"Query pos={result.query_pos}, Key pos={result.key_pos}",
        xaxis_title="Key Features",
        yaxis_title="Query Features",
        height=max(400, len(query_features) * 30),
        width=max(600, len(key_features) * 40),
    )

    if save_path:
        fig.write_html(save_path)

    return fig


def plot_qk_attribution_waterfall(
    result: QKAttributionResult,
    top_k: int = 15,
    save_path: str | None = None,
) -> go.Figure:
    """
    Visualize QK attributions as a waterfall chart.

    Shows how individual feature interactions sum to produce the total attention score.

    Args:
        result: QKAttributionResult to visualize
        top_k: Number of top attributions to show
        save_path: Optional path to save figure

    Returns:
        Plotly figure
    """
    top_attrs = result.get_top_k(k=top_k, only_features=True)

    # Prepare data
    labels = [f"{a.query_feature_desc[:30]} × {a.key_feature_desc[:30]}" for a in top_attrs]
    values = [a.contribution for a in top_attrs]

    # Add total
    labels.append("Total")
    values.append(result.total_score)

    # Create waterfall
    fig = go.Figure(
        go.Waterfall(
            name="QK Contributions",
            orientation="v",
            measure=["relative"] * len(top_attrs) + ["total"],
            x=labels,
            y=values,
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        )
    )

    fig.update_layout(
        title=f"QK Attribution Waterfall (L{result.layer}H{result.head})",
        showlegend=False,
        height=500,
        xaxis_tickangle=-45,
    )

    if save_path:
        fig.write_html(save_path)

    return fig


def plot_head_loadings(
    edge_attribution: EdgeAttribution,
    top_k: int = 10,
    save_path: str | None = None,
) -> go.Figure:
    """
    Visualize head loadings for an attribution graph edge.

    Shows which attention heads mediate the edge and their relative contributions.

    Args:
        edge_attribution: EdgeAttribution to visualize
        top_k: Number of top heads to show
        save_path: Optional path to save figure

    Returns:
        Plotly figure
    """
    top_heads = edge_attribution.get_top_heads(k=top_k)

    labels = [f"L{h.layer}H{h.head}" for h in top_heads]
    contributions = [h.contribution for h in top_heads]
    attention_weights = [h.attention_weight for h in top_heads]

    # Create subplot with two bar charts
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Head Contributions", "Attention Patterns"),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
    )

    # Contributions
    fig.add_trace(
        go.Bar(x=labels, y=contributions, name="Contribution", marker_color="indianred"),
        row=1,
        col=1,
    )

    # Attention weights
    fig.add_trace(
        go.Bar(x=labels, y=attention_weights, name="Attention Weight", marker_color="lightsalmon"),
        row=1,
        col=2,
    )

    fig.update_layout(
        title=f"Head Loadings: {edge_attribution.source_feature[:40]} → "
        f"{edge_attribution.target_feature[:40]}",
        showlegend=False,
        height=400,
    )

    if save_path:
        fig.write_html(save_path)

    return fig


def plot_attribution_graph(
    graph: AttributionGraph,
    layout: str = "hierarchical",
    save_path: str | None = None,
) -> go.Figure:
    """
    Visualize attribution graph as an interactive network diagram.

    Args:
        graph: AttributionGraph to visualize
        layout: Layout algorithm ('hierarchical', 'force', 'circular')
        save_path: Optional path to save figure

    Returns:
        Plotly figure
    """
    # Build edge traces
    edge_traces = []
    for edge in graph.edges:
        # Find positions (simplified - use layer as y, position as x)
        x0, y0 = edge.source.position, edge.source.layer
        x1, y1 = edge.target.position, edge.target.layer

        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode="lines",
            line=dict(width=min(abs(edge.attribution) * 10, 5), color="rgba(125, 125, 125, 0.5)"),
            hoverinfo="text",
            text=f"{edge.source.feature_desc} → {edge.target.feature_desc}<br>"
            f"Attribution: {edge.attribution:.3f}",
            showlegend=False,
        )
        edge_traces.append(edge_trace)

    # Build node trace
    node_x = [node.position for node in graph.nodes]
    node_y = [node.layer for node in graph.nodes]
    node_text = [
        f"{node.feature_desc}<br>L{node.layer} P{node.position}<br>Act: {node.activation:.2f}"
        for node in graph.nodes
    ]
    node_size = [min(abs(node.activation) * 20, 30) for node in graph.nodes]

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=node_size,
            color=[node.activation for node in graph.nodes],
            colorbar=dict(title="Activation"),
            line_width=2,
        ),
        name="Features",
    )

    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])

    fig.update_layout(
        title="Attribution Graph",
        titlefont_size=16,
        showlegend=False,
        hovermode="closest",
        xaxis=dict(title="Context Position", showgrid=True),
        yaxis=dict(title="Layer", showgrid=True),
        height=600,
    )

    if save_path:
        fig.write_html(save_path)

    return fig


def plot_head_usage_analysis(
    graph: AttributionGraph,
    top_k: int = 20,
    save_path: str | None = None,
) -> go.Figure:
    """
    Visualize which attention heads are used most in the graph.

    Args:
        graph: AttributionGraph to analyze
        top_k: Number of top heads to show
        save_path: Optional path to save figure

    Returns:
        Plotly figure
    """
    head_usage = graph.analyze_head_usage()
    sorted_heads = sorted(head_usage.items(), key=lambda x: x[1], reverse=True)[:top_k]

    labels = [f"L{layer}H{head}" for (layer, head), _ in sorted_heads]
    values = [contrib for _, contrib in sorted_heads]

    fig = go.Figure(
        go.Bar(
            x=labels,
            y=values,
            marker_color="steelblue",
            text=[f"{v:.3f}" for v in values],
            textposition="auto",
        )
    )

    fig.update_layout(
        title="Top Attention Heads by Total Contribution",
        xaxis_title="Head",
        yaxis_title="Total Contribution",
        height=500,
    )

    if save_path:
        fig.write_html(save_path)

    return fig


def plot_intervention_scan(
    scale_values: list[float],
    top_logits: list[list[tuple[str, float]]],
    target_token: str,
    feature_name: str,
    save_path: str | None = None,
) -> go.Figure:
    """
    Visualize the effect of steering a feature across a range of scale values.

    Args:
        scale_values: List of scale factors applied
        top_logits: List of top predicted tokens for each scale
        target_token: Token of interest to track
        feature_name: Name of the feature being steered
        save_path: Optional path to save figure

    Returns:
        Plotly figure
    """
    # Track target token probability
    target_probs = []
    for logits in top_logits:
        prob = next((p for tok, p in logits if tok == target_token), 0.0)
        target_probs.append(prob)

    # Track top-1 token
    [logits[0][0] if logits else "" for logits in top_logits]

    fig = go.Figure()

    # Add target token probability
    fig.add_trace(
        go.Scatter(
            x=scale_values,
            y=target_probs,
            mode="lines+markers",
            name=f"P({target_token})",
            line=dict(color="red", width=3),
        )
    )

    # Add vertical line at scale=1.0 (baseline)
    fig.add_vline(x=1.0, line_dash="dash", line_color="gray", annotation_text="Baseline")

    fig.update_layout(
        title=f"Feature Steering: {feature_name}",
        xaxis_title="Scale Factor",
        yaxis_title="Probability",
        height=500,
        hovermode="x unified",
    )

    if save_path:
        fig.write_html(save_path)

    return fig


def plot_concordance_discordance(
    concordance_attention: np.ndarray,
    discordance_attention: np.ndarray,
    tokens: list[str],
    query_pos: int,
    save_path: str | None = None,
) -> go.Figure:
    """
    Visualize concordance vs discordance head attention patterns.

    From the correctness circuits case study in the paper.

    Args:
        concordance_attention: Attention pattern of concordance heads [seq_len]
        discordance_attention: Attention pattern of discordance heads [seq_len]
        tokens: Token sequence
        query_pos: Query position
        save_path: Optional path to save figure

    Returns:
        Plotly figure
    """
    positions = list(range(len(tokens)))

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=positions,
            y=concordance_attention,
            name="Concordance Heads",
            marker_color="green",
            text=tokens,
            textposition="outside",
        )
    )

    fig.add_trace(
        go.Bar(
            x=positions,
            y=-discordance_attention,  # Negative to show below axis
            name="Discordance Heads",
            marker_color="red",
            text=tokens,
            textposition="outside",
        )
    )

    fig.add_vline(x=query_pos, line_dash="dash", line_color="blue", annotation_text="Query")

    fig.update_layout(
        title="Concordance vs Discordance Head Attention Patterns",
        xaxis_title="Position",
        yaxis_title="Attention Weight",
        barmode="relative",
        height=500,
    )

    if save_path:
        fig.write_html(save_path)

    return fig


def create_interactive_dashboard(
    qk_result: QKAttributionResult,
    edge_attribution: EdgeAttribution,
    graph: AttributionGraph,
    save_path: str = "circuits_dashboard.html",
):
    """
    Create an interactive dashboard combining multiple visualizations.

    Args:
        qk_result: QK attribution result
        edge_attribution: Edge attribution with head loadings
        graph: Attribution graph
        save_path: Path to save HTML dashboard
    """
    from plotly.subplots import make_subplots

    # Create subplots
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "QK Attribution Matrix",
            "Head Loadings",
            "Attribution Graph Summary",
            "Top Contributing Heads",
        ),
        specs=[[{"type": "heatmap"}, {"type": "bar"}], [{"type": "table"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    # Add QK attribution heatmap (simplified)
    qk_result.get_top_k(k=10)
    # ... would add actual plots to subplots ...

    # Add head loadings
    # ... add to subplot ...

    # Add summary table
    {
        "Metric": ["Total Attribution", "Attention %", "MLP %", "Residual %"],
        "Value": [
            f"{edge_attribution.total_attribution:.3f}",
            f"{100 * edge_attribution.attention_component / edge_attribution.total_attribution:.1f}%",
            f"{100 * edge_attribution.mlp_component / edge_attribution.total_attribution:.1f}%",
            f"{100 * edge_attribution.residual_component / edge_attribution.total_attribution:.1f}%",
        ],
    }
    # ... add table ...

    # Add top heads analysis
    graph.analyze_head_usage()
    # ... add to subplot ...

    fig.update_layout(
        title_text="Transformer Circuits Analysis Dashboard",
        height=1000,
        showlegend=False,
    )

    fig.write_html(save_path)
    return fig
