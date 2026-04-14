"""Literature Agent: Specializes in academic literature search and citation.

Capabilities:
- Search papers via Google Scholar, arXiv, Semantic Scholar
- Extract key findings and relevant sections
- Build citation graph
- Maintain literature references in world model
"""

from typing import Any

from kosmos.agents.base import AgentConfig, BaseAgent
from kosmos.core.orchestrator import ReActResult
from kosmos.core.vertex_client import GeminiModel


class LiteratureAgent(BaseAgent):
    """Agent specialized in literature search and knowledge extraction.

    Uses Gemini Flash for fast, cost-effective search operations.
    Populates world model with literature references and citation graph.
    """

    DEFAULT_CONFIG = AgentConfig(
        name="literature_agent",
        model=GeminiModel.FLASH,  # Fast model for search tasks
        instruction="""You are a literature research specialist.

Your role:
1. Search academic literature using available tools
2. Extract key findings, methodologies, and results from papers
3. Identify relevant citations and relationships between papers
4. Assess relevance of papers to the current research goal
5. Maintain citation graph and literature database

Focus on:
- High-quality peer-reviewed sources
- Recent publications (last 5 years preferred)
- Papers with high citation counts
- Methodological rigor

Always provide:
- Full citation information (title, authors, year, venue)
- Relevance score (0-1) with justification
- Key findings summary (2-3 sentences)
""",
        tools=["google_search", "arxiv_search", "semantic_scholar_search"],
        temperature=0.3,  # Lower temperature for focused search
        max_iterations=15,
    )

    def execute_task(self, task: str, context: dict[str, Any] | None = None) -> ReActResult:
        """Execute literature search task.

        Example tasks:
        - "Find papers on reinforcement learning for protein folding"
        - "Search for recent work on autonomous AI agents"
        - "Identify seminal papers cited by [paper_id]"

        Args:
            task: Literature search task
            context: Optional context with search parameters

        Returns:
            ReActResult with discovered papers

        """
        goal = self._build_goal_with_instruction(task)

        # Add context if provided
        if context:
            goal += f"\n\nAdditional context:\n{context}"

        # Execute ReAct loop
        result = self.orchestrator.execute_cycle(goal)

        # Post-process: Extract literature refs and add to world model
        self._extract_and_store_references(result)

        return result

    def _extract_and_store_references(self, result: ReActResult):
        """Extract literature references from ReAct result and add to world model.

        Parses agent observations for paper metadata and stores in world model.

        Args:
            result: ReAct execution result

        """
        # Simplified extraction logic - real implementation would parse
        # structured output from search tools
        for step in result.steps:
            if step.action in ["arxiv_search", "semantic_scholar_search", "google_search"]:
                if step.observation and "title:" in step.observation.lower():
                    # This is a placeholder - actual implementation would
                    # parse structured JSON from search tools
                    self.world_model.add_literature(
                        title="Extracted paper title",  # Parse from observation
                        authors=["Author1", "Author2"],  # Parse from observation
                        abstract="Paper abstract...",  # Parse from observation
                        relevance_score=0.8,  # Calculate based on agent assessment
                        url=None,  # Extract if available
                    )

    def search_papers(self, query: str, limit: int = 10) -> ReActResult:
        """Convenience method for paper search.

        Args:
            query: Search query
            limit: Maximum number of papers to return

        Returns:
            ReActResult with search results

        """
        return self.execute_task(
            f"Search for papers matching: '{query}'. Return top {limit} most relevant papers.",
            context={"limit": limit},
        )

    def find_citations(self, paper_id: str, depth: int = 1) -> ReActResult:
        """Find citations for a given paper.

        Args:
            paper_id: Paper identifier (DOI, arXiv ID, etc.)
            depth: Citation depth (1 = direct citations, 2 = second-order, etc.)

        Returns:
            ReActResult with citation graph

        """
        return self.execute_task(
            f"Find all papers that cite '{paper_id}'. Build citation graph to depth {depth}.",
            context={"paper_id": paper_id, "depth": depth},
        )
