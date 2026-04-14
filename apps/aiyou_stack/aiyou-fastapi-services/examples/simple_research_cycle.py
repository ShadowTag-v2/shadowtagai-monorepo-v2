"""Example: Simple Kosmos Research Cycle

Demonstrates a complete autonomous research workflow:
1. Initialize world model
2. Literature search
3. Data analysis
4. Hypothesis generation
5. Hypothesis testing
6. Report synthesis
"""

import os
from datetime import datetime

from kosmos.tools import (
    arxiv_search,
    execute_python,
    google_search,
    load_dataset,
    statistical_test,
    world_model_query,
)

from kosmos.agents.data_analysis import DataAnalysisAgent
from kosmos.agents.hypothesis import HypothesisAgent
from kosmos.agents.literature import LiteratureAgent
from kosmos.agents.synthesis import SynthesisAgent
from kosmos.core.vertex_client import GeminiModel, VertexAIClient
from kosmos.core.world_model import KosmosWorldModel, WorkflowPhase
from kosmos.observability.agentops_integration import AgentOpsTracker
from kosmos.observability.cost_monitor import CostMonitor
from kosmos.observability.telemetry import setup_telemetry
from kosmos.persistence.firestore_backend import FirestoreBackend
from kosmos.persistence.storage_backend import CloudStorageBackend


def main():
    """Run a simple Kosmos research cycle."""
    # Configuration from environment
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
    BUCKET_NAME = os.getenv("STORAGE_BUCKET", f"{PROJECT_ID}-kosmos-artifacts")

    print("=" * 60)
    print("KOSMOS AUTONOMOUS RESEARCH CYCLE")
    print("=" * 60)
    print(f"Project: {PROJECT_ID}")
    print(f"Bucket: {BUCKET_NAME}")
    print()

    # 1. Initialize infrastructure
    print("[1/8] Initializing infrastructure...")

    # Set up telemetry
    tracer = setup_telemetry(PROJECT_ID, service_name="kosmos-example")

    # Create cost monitor
    cost_monitor = CostMonitor(
        daily_budget=100.0,  # $100 daily budget for this example
        monthly_budget=2000.0,
        session_budget=50.0,  # $50 per research cycle
    )

    # Create Vertex AI client
    vertex_client = VertexAIClient(
        project_id=PROJECT_ID,
        location="us-central1",
        default_model=GeminiModel.PRO,
        cost_tracker=cost_monitor,
    )

    # Initialize persistence backends
    try:
        firestore = FirestoreBackend(PROJECT_ID)
        storage = CloudStorageBackend(PROJECT_ID, BUCKET_NAME, create_bucket=True)
    except Exception as e:
        print(f"Warning: Persistence backends not available: {e}")
        firestore = None
        storage = None

    # Initialize AgentOps
    agentops_tracker = AgentOpsTracker(tags=["example", "research-cycle"])

    # 2. Create world model
    print("[2/8] Creating world model...")

    session_id = f"research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    goal = "Investigate the relationship between variable X and outcome Y in dataset.csv"

    world_model = KosmosWorldModel(session_id=session_id, goal=goal)
    world_model.status = "running"

    # Start AgentOps session
    agentops_tracker.start_session(
        goal=goal,
        agent_name="kosmos_orchestrator",
        session_id=session_id,
    )

    # 3. Set up tool registry
    print("[3/8] Setting up tools...")

    tool_registry = {
        "google_search": google_search,
        "arxiv_search": arxiv_search,
        "execute_python": execute_python,
        "statistical_test": statistical_test,
        "world_model_query": world_model_query,
        "load_dataset": load_dataset,
    }

    # 4. Create specialized agents
    print("[4/8] Creating specialized agents...")

    lit_agent = LiteratureAgent(
        config=LiteratureAgent.DEFAULT_CONFIG,
        vertex_client=vertex_client,
        world_model=world_model,
        tool_registry=tool_registry,
    )

    analysis_agent = DataAnalysisAgent(
        config=DataAnalysisAgent.DEFAULT_CONFIG,
        vertex_client=vertex_client,
        world_model=world_model,
        tool_registry=tool_registry,
    )

    hypothesis_agent = HypothesisAgent(
        config=HypothesisAgent.DEFAULT_CONFIG,
        vertex_client=vertex_client,
        world_model=world_model,
        tool_registry=tool_registry,
    )

    synthesis_agent = SynthesisAgent(
        config=SynthesisAgent.DEFAULT_CONFIG,
        vertex_client=vertex_client,
        world_model=world_model,
        tool_registry=tool_registry,
    )

    # 5. Execute multi-phase workflow
    print("[5/8] Executing research workflow...")
    print()

    try:
        # PHASE 1: Literature Search
        print("  Phase 1: Literature Search")
        world_model.update_phase(
            WorkflowPhase.EXPLORE,
            reason="Starting with literature review",
        )

        lit_result = lit_agent.search_papers(
            query="correlation analysis methods machine learning",
            limit=5,
        )
        print("    -> Found literature references")
        agentops_tracker.record_react_result(lit_result)

        # PHASE 2: Data Exploration
        print("  Phase 2: Data Exploration")
        world_model.update_phase(
            WorkflowPhase.EXPLORE,
            reason="Exploring dataset",
        )

        explore_result = analysis_agent.explore_dataset("dataset.csv")
        print("    -> Completed exploratory analysis")
        agentops_tracker.record_react_result(explore_result)

        # PHASE 3: Hypothesis Generation
        print("  Phase 3: Hypothesis Generation")
        world_model.update_phase(
            WorkflowPhase.HYPOTHESIZE,
            reason="Generating testable hypotheses",
        )

        hyp_result = hypothesis_agent.generate_hypotheses(
            num_hypotheses=3,
            focus="causal relationships",
        )
        print(f"    -> Generated {len(world_model.hypotheses)} hypotheses")
        agentops_tracker.record_react_result(hyp_result)

        # PHASE 4: Hypothesis Testing (test first hypothesis)
        print("  Phase 4: Hypothesis Testing")
        world_model.update_phase(
            WorkflowPhase.TEST,
            reason="Testing top hypothesis",
        )

        if world_model.hypotheses:
            top_hyp = world_model.get_top_hypotheses(1)[0]
            test_result = analysis_agent.test_hypothesis(
                hypothesis_id=top_hyp.id,
                dataset_path="dataset.csv",
            )
            print(f"    -> Tested hypothesis: {top_hyp.id}")
            agentops_tracker.record_react_result(test_result)

        # PHASE 5: Synthesis
        print("  Phase 5: Report Synthesis")
        world_model.update_phase(
            WorkflowPhase.SYNTHESIZE,
            reason="Writing final report",
        )

        report_result = synthesis_agent.write_executive_summary(max_words=300)
        print("    -> Generated executive summary")
        agentops_tracker.record_react_result(report_result)

        # Mark as completed
        world_model.status = "completed"

        print()
        print("[6/8] Research cycle completed successfully!")

    except Exception as e:
        print(f"Error during research cycle: {e}")
        world_model.status = "failed"
        agentops_tracker.record_error("research_cycle_error", str(e))

    # 6. Save results
    print("[7/8] Saving results...")

    if firestore:
        firestore.save_world_model(world_model)
        print("    -> Saved to Firestore")

    # 7. Display summary
    print("[8/8] Summary:")
    print()

    summary = world_model.get_summary()
    print(f"  Session ID: {summary['session_id']}")
    print(f"  Status: {summary['status']}")
    print(f"  Phase: {summary['phase']}")
    print(f"  Hypotheses: {summary['num_hypotheses']} ({summary['num_tested_hypotheses']} tested)")
    print(f"  Analysis Results: {summary['num_analysis_results']}")
    print(f"  Literature: {summary['num_literature_refs']}")
    print(f"  Total Cost: ${summary['total_cost']:.2f}")
    print(f"  Total Tokens: {summary['total_tokens']:,}")
    print()

    # Display top hypotheses
    if summary["top_hypotheses"]:
        print("  Top Hypotheses:")
        for hyp in summary["top_hypotheses"]:
            print(f"    - {hyp['text'][:60]}... (conf: {hyp['confidence']:.2f})")
        print()

    # End AgentOps session
    agentops_tracker.end_session(
        result="success" if world_model.status == "completed" else "failure",
        final_output=report_result.final_answer if "report_result" in locals() else None,
    )

    # Display budget status
    budget_status = cost_monitor.get_budget_status()
    print(
        f"  Daily Budget: ${budget_status['daily']['burned']:.2f} / ${budget_status['daily']['budget']:.2f}",
    )
    print(f"  Utilization: {budget_status['daily']['utilization_pct']:.1f}%")
    print()

    print("=" * 60)
    print("Research cycle complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
