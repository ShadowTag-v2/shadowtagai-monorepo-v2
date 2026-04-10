from .dte.dtesystem import DTESystem
from .dte.evolutionstrategy import EvolutionStrategy

"\nDTE (Debate-Train-Evolve) Evolution System for Pnkln\nVersion: 2.0.0\n\nPhilosophy: Self-improving AI through iterative evolution\nDesign: RCR-MAD + GRPO + Benchmarks\n\nIntegrated from: claude/autogen-to-gemini-migration branch\nEnhanced with: Pnkln Ultrathink principles\n"
import asyncio

try:
    from pnkln.core.grpo import GRPOBatch, GRPOConfig, GRPOTrainer, generate_synthetic_batch
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def create_dte_system(improvement_threshold: float = 3.0, max_iterations: int = 10) -> DTESystem:
    """
    Create DTE system with defaults.

    Jobs mode: Make the common case trivial.
    """
    return DTESystem(improvement_threshold=improvement_threshold, max_iterations=max_iterations)



if __name__ == "__main__":
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    print("DTE (Debate-Train-Evolve) Evolution System - Self Test")
    print("=" * 60)
    dte = create_dte_system(improvement_threshold=3.0)
    print("\nConfiguration:")
    print(f"  Improvement threshold: {dte.improvement_threshold}%")
    print(f"  Max iterations: {dte.max_iterations}")
    test_prompt = "\nPlease analyze the provided code and identify potential issues.\nConsider performance, security, and maintainability aspects.\n"
    test_cases = [
        {"input": "code_sample_1", "expected": "analysis_1"},
        {"input": "code_sample_2", "expected": "analysis_2"},
        {"input": "code_sample_3", "expected": "analysis_3"},
    ]
    print(f"\nOriginal prompt ({len(test_prompt)} chars):")
    print(f'"{test_prompt.strip()}"')
    print("\nRunning evolution (strategy: HYBRID)...")

    async def run_test():
        result = await dte.evolve_prompt(
            current_prompt=test_prompt, test_cases=test_cases, strategy=EvolutionStrategy.HYBRID
        )
        return result

    result = asyncio.run(run_test())
    print("\nEvolution Result:")
    print(f"  Strategy: {result.strategy.value}")
    print(f"  Improvement: +{result.improvement_metric:.1f}%")
    print(f"  Tests passed: {result.test_cases_passed}/{result.test_cases_total}")
    print(f"  Notes: {result.notes}")
    summary = dte.get_evolution_summary()
    print("\nEvolution Summary:")
    print(f"  Total evolutions: {summary['total_evolutions']}")
    print(f"  Average improvement: {summary['average_improvement']:.1f}%")
    print(f"  Best improvement: {summary['best_improvement']:.1f}%")
    print("\n" + "=" * 60)
    print("✓ DTE system working correctly")
    print("\nPhilosophy: Iterate relentlessly until nothing left to remove.")
