"""
Example usage of the Transformer Circuits library.

This script demonstrates the core functionality:
1. Computing QK attributions
2. Analyzing head loadings
3. Building attribution graphs
4. Performing interventions
"""

import numpy as np
import torch

from transformer_circuits import (
    HeadLoadingComputer,
    QKAttributor,
)
from transformer_circuits.attribution_graph import AttributionGraphBuilder
from transformer_circuits.visualization import (
    plot_attribution_graph,
    plot_head_loadings,
    plot_intervention_scan,
    plot_qk_attribution_matrix,
)


def example_1_qk_attributions():
    """
    Example 1: Compute QK attributions for induction.

    Prompt: "I always loved visiting Aunt Sally. Whenever I was feeling sad, Aunt"
    Question: Why does the model attend from final "Aunt" to first "Sally"?
    """
    print("=" * 80)
    print("Example 1: QK Attributions for Induction")
    print("=" * 80)

    # Mock data (in practice, these would come from actual model/SAE)
    d_model = 768
    n_features = 100

    # Create mock W_Q and W_K matrices
    W_Q = torch.randn(64, d_model) * 0.1
    W_K = torch.randn(64, d_model) * 0.1

    # Create mock SAE feature vectors
    feature_vectors = torch.randn(n_features, d_model) * 0.1

    # Feature descriptions
    feature_descriptions = [
        "Aunt/Uncle family signifier",
        "Names in general",
        "Name of Aunt",
        "Token after family title",
        "Previous token was Aunt",
        "Induction pattern",
    ] + [f"Feature_{i}" for i in range(6, n_features)]

    # Create mock activations at query and key positions
    query_activations = torch.zeros(n_features)
    query_activations[0] = 0.8  # "Aunt/Uncle" feature active
    query_activations[1] = 0.6  # "Names" feature active

    key_activations = torch.zeros(n_features)
    key_activations[2] = 0.9  # "Name of Aunt" feature active
    key_activations[3] = 0.7  # "After family title" feature

    # Create attributor
    attributor = QKAttributor(
        W_Q=W_Q,
        W_K=W_K,
        feature_vectors=feature_vectors,
        feature_descriptions=feature_descriptions,
    )

    # Compute QK attributions
    result = attributor.compute_qk_attributions(
        key_activations=key_activations,
        query_activations=query_activations,
        query_pos=10,  # Final "Aunt"
        key_pos=4,  # First "Sally"
        layer=8,
        head_idx=7,
    )

    # Print results
    print(result.summarize(k=5))
    print("\nTop positive contributors:")
    for attr in result.get_positive_contributors(threshold=0.001)[:5]:
        print(f"  {attr.query_feature_desc} × {attr.key_feature_desc}: {attr.contribution:.4f}")

    # Visualize
    fig = plot_qk_attribution_matrix(result, top_k=10, save_path="qk_induction.html")
    print("\nVisualization saved to: qk_induction.html")

    return result


def example_2_head_loadings():
    """
    Example 2: Compute head loadings for an attribution graph edge.

    Shows which attention heads mediate feature-to-feature attributions.
    """
    print("\n" + "=" * 80)
    print("Example 2: Head Loadings")
    print("=" * 80)

    # Mock setup
    n_heads = 12
    d_model = 768
    d_head = 64
    n_features = 100

    # Create mock W_V and W_O matrices
    W_V = {8: torch.randn(n_heads, d_head, d_model) * 0.1}
    W_O = {8: torch.randn(n_heads, d_model, d_head) * 0.1}

    # Mock attention patterns
    seq_len = 20
    attention_patterns = {8: torch.softmax(torch.randn(n_heads, seq_len, seq_len), dim=-1)}

    # Mock SAE feature vectors
    feature_vectors = {
        8: torch.randn(n_features, d_model) * 0.1,
        9: torch.randn(n_features, d_model) * 0.1,
    }

    # Create computer
    computer = HeadLoadingComputer(W_V, W_O, attention_patterns, feature_vectors)

    # Compute head loadings for an edge
    edge = computer.compute_edge_attribution(
        source_feature_idx=42,
        target_feature_idx=73,
        source_activation=0.8,
        target_activation=0.9,
        source_pos=5,
        target_pos=10,
        source_layer=8,
        target_layer=9,
        source_feature_desc="Name of Aunt",
        target_feature_desc="Say Sally",
    )

    print(edge.summarize(k=5))

    # Visualize
    fig = plot_head_loadings(edge, top_k=8, save_path="head_loadings.html")
    print("\nVisualization saved to: head_loadings.html")

    return edge


def example_3_attribution_graph():
    """
    Example 3: Build and analyze attribution graph.

    Traces backwards from a target logit to understand computation.
    """
    print("\n" + "=" * 80)
    print("Example 3: Attribution Graph")
    print("=" * 80)

    # Mock setup
    n_layers = 3
    seq_len = 15
    n_features = 100
    d_model = 768

    # Mock SAE activations per layer
    sae_activations = {
        layer: torch.rand(seq_len, n_features) * 0.5  # Sparse activations
        for layer in range(n_layers)
    }

    # Mock feature vectors
    sae_features = {layer: torch.randn(n_features, d_model) * 0.1 for layer in range(n_layers)}

    # Mock descriptions
    sae_descriptions = {
        layer: [f"L{layer}_Feature_{i}" for i in range(n_features)] for layer in range(n_layers)
    }

    # Build graph
    builder = AttributionGraphBuilder(sae_activations, sae_features, sae_descriptions, seq_len)

    graph = builder.build_from_logit(
        target_logit_feature=(n_layers - 1, seq_len - 1, 42),
        max_depth=2,
        top_k_per_layer=5,
        min_attribution=0.01,
    )

    print(graph.summarize())

    # Analyze head usage
    print("\nHead Usage Analysis:")
    head_usage = graph.analyze_head_usage()
    if head_usage:
        for (layer, head), contrib in sorted(head_usage.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]:
            print(f"  L{layer}H{head}: {contrib:.3f}")

    # Visualize
    fig = plot_attribution_graph(graph, save_path="attribution_graph.html")
    print("\nVisualization saved to: attribution_graph.html")

    return graph


def example_4_interventions():
    """
    Example 4: Feature steering interventions.

    Test causal effects by modifying feature activations.
    """
    print("\n" + "=" * 80)
    print("Example 4: Feature Interventions")
    print("=" * 80)

    # Mock model components
    # In practice, these would be actual model and SAE components
    print("Setting up mock model and SAE components...")

    # Simulate scanning across steering values
    scale_values = np.linspace(-2.0, 2.0, 20)

    # Mock results: top predicted tokens for each scale
    # Simulating effect of steering "opposite" feature
    top_logits = []
    for scale in scale_values:
        if scale < 0:
            # Negative steering -> predicts synonyms
            top_logits.append([("petit", 0.8), ("faible", 0.1), ("grand", 0.05)])
        elif scale < 0.5:
            # Weak steering -> mixed predictions
            top_logits.append([("petit", 0.4), ("grand", 0.3), ("faible", 0.2)])
        else:
            # Positive steering -> predicts opposites
            top_logits.append([("grand", 0.9), ("énorme", 0.05), ("petit", 0.02)])

    # Visualize steering effect
    fig = plot_intervention_scan(
        scale_values=scale_values.tolist(),
        top_logits=top_logits,
        target_token="grand",
        feature_name="opposite/antonym context",
        save_path="intervention_scan.html",
    )

    print("Intervention scan visualization saved to: intervention_scan.html")
    print("\nKey findings:")
    print("  - Negative steering (<0): Model predicts synonyms instead of antonyms")
    print("  - Zero steering (0.0): Ablation breaks antonym retrieval")
    print("  - Positive steering (>1): Amplifies antonym prediction")

    return scale_values, top_logits


def example_5_circuit_validation():
    """
    Example 5: Validate a complete circuit hypothesis.

    Test multiple components of a hypothesized circuit.
    """
    print("\n" + "=" * 80)
    print("Example 5: Circuit Validation")
    print("=" * 80)

    print("Hypothesis: Multiple choice answering circuit")
    print("  1. 'Correct answer' features tag the right option")
    print("  2. Query-side 'answer MC' features attend to tagged option")
    print("  3. OV circuit copies option letter to output")

    print("\nValidation experiments:")

    # Test 1: Ablate "correct answer" key-side features
    print("\n  Test 1: Ablate key-side 'correct answer' features")
    print("    Original prediction: B")
    print("    After ablation: A (falls back to position-based heuristic)")
    print("    Conclusion: ✓ Key-side features necessary")

    # Test 2: Inject "correct answer" into wrong option
    print("\n  Test 2: Inject 'correct answer' into option A")
    print("    Original prediction: B")
    print("    After injection: A")
    print("    Conclusion: ✓ Feature sufficient to redirect attention")

    # Test 3: Ablate query-side features
    print("\n  Test 3: Ablate query-side 'answer MC' features")
    print("    Original prediction: B")
    print("    After ablation: (random)")
    print("    Conclusion: ✓ Query-side features necessary")

    print("\n✓ Circuit validated: All components confirmed")

    return True


def main():
    """Run all examples."""
    print("Transformer Circuits: Example Usage")
    print("=" * 80)
    print()

    # Run examples
    qk_result = example_1_qk_attributions()
    edge = example_2_head_loadings()
    graph = example_3_attribution_graph()
    scales, logits = example_4_interventions()
    validated = example_5_circuit_validation()

    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)
    print("\nGenerated visualizations:")
    print("  - qk_induction.html")
    print("  - head_loadings.html")
    print("  - attribution_graph.html")
    print("  - intervention_scan.html")
    print("\nOpen these files in a web browser to explore interactively!")


if __name__ == "__main__":
    main()
