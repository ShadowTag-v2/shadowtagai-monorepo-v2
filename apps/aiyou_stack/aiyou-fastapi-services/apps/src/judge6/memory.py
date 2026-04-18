from typing import Any

import networkx as nx

# from mem0 import Memory # Uncomment when configured
# import faiss # Uncomment when configured


class SovereignMemory:
    """The 'Intelligence' Layer (ATP 2-01.3)
    Integrates Mem0 (Session/User Context) and Custom GraphRAG (Knowledge Graph).
    """

    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        print(f"🧠 [Memory] Initializing Sovereign Memory for user: {user_id}")

        # Initialize Mem0 (Session Context)
        self.mem0 = MockMem0()

        # Initialize Custom GraphRAG (NetworkX)
        self.knowledge_graph = nx.DiGraph()
        self.build_initial_graph()

    def build_initial_graph(self):
        """Initialize the graph with core doctrine."""
        self.knowledge_graph.add_edge("Judge#6", "FinancialGovernance", relation="provides")
        self.knowledge_graph.add_edge("Judge#6", "RiskScoring", relation="performs")
        self.knowledge_graph.add_edge("RiskScoring", "ATP_5_19", relation="based_on")

    def add_context(self, text: str, metadata: dict[str, Any] = None):
        """Ingest new intelligence into the system."""
        print(f"📥 [Memory] Ingesting: '{text[:50]}...'")
        self.mem0.add(text, user_id=self.user_id, metadata=metadata)

        # Simple entity extraction (Mock)
        if "transaction" in text.lower():
            self.knowledge_graph.add_edge("Transaction", "AuditLog", relation="recorded_in")

    def recall(self, query: str) -> dict[str, Any]:
        """Retrieve intelligence using Hybrid Search (Vector + Graph)."""
        print(f"🔍 [Memory] Recalling: '{query}'")

        # 1. Fast Recall (Mem0 - Vector)
        session_context = self.mem0.search(query, user_id=self.user_id)

        # 2. Deep Reasoning (Graph Traversal)
        graph_context = []
        if "risk" in query.lower():
            # Traverse graph for risk-related nodes
            if "RiskScoring" in self.knowledge_graph:
                neighbors = list(self.knowledge_graph.neighbors("RiskScoring"))
                graph_context = [f"RiskScoring -> {n}" for n in neighbors]

        return {
            "session_context": session_context,
            "deep_context": graph_context,
            "synthesis": "Synthesized insight from Sovereign Graph + Vector.",
        }


# --- Mocks for Development ---


class MockMem0:
    def add(self, text, user_id, metadata=None):
        pass

    def search(self, query, user_id):
        return [{"text": "User prefers low-risk transactions.", "score": 0.9}]


if __name__ == "__main__":
    memory = SovereignMemory(user_id="commander_1")
    memory.add_context("Approved transaction tx_1 for $4.50", {"decision": "APPROVED"})
    result = memory.recall("risk profile")
    print("\n--- Memory Recall Result ---")
    print(result)
