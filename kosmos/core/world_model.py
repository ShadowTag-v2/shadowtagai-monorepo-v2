# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
World Model: Persistent state tracking across autonomous discovery cycles.

Implements the 'structured world-model' concept from Kosmos paper (arxiv 2511.02824).
Maintains hypotheses, analysis results, literature references, and knowledge graphs
across multi-phase research workflows.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
import networkx as nx


class WorkflowPhase(Enum):
    """Kosmos workflow phases for autonomous research cycles."""

    INGEST = "ingest"  # Load datasets, initial literature search
    EXPLORE = "explore"  # Data exploration, pattern identification
    HYPOTHESIZE = "hypothesize"  # Generate candidate hypotheses
    TEST = "test"  # Design & execute experiments/analysis
    VALIDATE = "validate"  # Statistical validation, literature cross-check
    SYNTHESIZE = "synthesize"  # Write final report with citations


@dataclass
class Hypothesis:
    """A testable research hypothesis generated during discovery."""

    id: str
    text: str
    confidence: float = 0.0
    supporting_evidence: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tested: bool = False
    test_results: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Hypothesis:
        """Create from dictionary."""
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class AnalysisResult:
    """Result from a data analysis or experiment execution."""

    id: str
    hypothesis_id: str | None
    code: str
    outputs: list[str] = field(default_factory=list)
    plots: list[str] = field(default_factory=list)  # Cloud Storage URLs
    statistical_tests: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str | None = None
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d["executed_at"] = self.executed_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalysisResult:
        """Create from dictionary."""
        if isinstance(data["executed_at"], str):
            data["executed_at"] = datetime.fromisoformat(data["executed_at"])
        return cls(**data)


@dataclass
class LiteratureRef:
    """Reference to academic literature discovered during research."""

    id: str
    title: str
    authors: list[str]
    abstract: str
    url: str | None = None
    relevance_score: float = 0.0
    citations_extracted: list[str] = field(default_factory=list)
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        d = asdict(self)
        d["added_at"] = self.added_at.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LiteratureRef:
        """Create from dictionary."""
        if isinstance(data["added_at"], str):
            data["added_at"] = datetime.fromisoformat(data["added_at"])
        return cls(**data)


class KosmosWorldModel:
    """
    Persistent state management for Kosmos-pattern autonomous agents.

    Maintains:
    - Research hypotheses with confidence scores
    - Analysis results and experimental outcomes
    - Literature references and citation graph
    - Knowledge graph of entities and relationships
    - Current workflow phase and progress tracking

    This is the 'world model' that coordinates across specialized agents
    (data analysis, literature search, hypothesis generation, synthesis).
    """

    def __init__(self, session_id: str, goal: str):
        """
        Initialize a new world model for a research session.

        Args:
            session_id: Unique identifier for this research session
            goal: High-level research goal/question
        """
        self.session_id = session_id
        self.goal = goal
        self.created_at = datetime.now(timezone.utc)

        # Core state
        self.hypotheses: list[Hypothesis] = []
        self.analysis_results: list[AnalysisResult] = []
        self.literature_refs: list[LiteratureRef] = []

        # Knowledge graph: nodes = entities, edges = relationships
        self.knowledge_graph = nx.DiGraph()

        # Workflow state
        self.phase = WorkflowPhase.INGEST
        self.phase_history: list[dict[str, Any]] = []

        # Metadata
        self.total_cost: float = 0.0
        self.total_tokens: int = 0
        self.status: str = "initialized"  # initialized, running, completed, failed

    def add_hypothesis(self, text: str, confidence: float = 0.5, evidence: list[str] = None) -> Hypothesis:
        """
        Add a new research hypothesis to the world model.

        Args:
            text: Hypothesis statement
            confidence: Initial confidence score (0-1)
            evidence: Supporting evidence references

        Returns:
            Created Hypothesis object
        """
        hypothesis = Hypothesis(
            id=f"hyp_{len(self.hypotheses) + 1:03d}",
            text=text,
            confidence=confidence,
            supporting_evidence=evidence or [],
        )
        self.hypotheses.append(hypothesis)
        return hypothesis

    def add_analysis_result(
        self,
        code: str,
        outputs: list[str],
        hypothesis_id: str | None = None,
        **kwargs,
    ) -> AnalysisResult:
        """
        Add an analysis result to the world model.

        Args:
            code: Analysis code that was executed
            outputs: Text outputs from execution
            hypothesis_id: Associated hypothesis (if testing one)
            **kwargs: Additional fields (plots, statistical_tests, etc.)

        Returns:
            Created AnalysisResult object
        """
        result = AnalysisResult(
            id=f"result_{len(self.analysis_results) + 1:03d}",
            hypothesis_id=hypothesis_id,
            code=code,
            outputs=outputs,
            **kwargs,
        )
        self.analysis_results.append(result)
        return result

    def add_literature(
        self,
        title: str,
        authors: list[str],
        abstract: str,
        relevance_score: float = 0.5,
        **kwargs,
    ) -> LiteratureRef:
        """
        Add a literature reference to the world model.

        Args:
            title: Paper title
            authors: List of author names
            abstract: Paper abstract
            relevance_score: Relevance to current research (0-1)
            **kwargs: Additional fields (url, citations_extracted, etc.)

        Returns:
            Created LiteratureRef object
        """
        ref = LiteratureRef(
            id=f"lit_{len(self.literature_refs) + 1:03d}",
            title=title,
            authors=authors,
            abstract=abstract,
            relevance_score=relevance_score,
            **kwargs,
        )
        self.literature_refs.append(ref)
        return ref

    def update_phase(self, new_phase: WorkflowPhase, reason: str = ""):
        """
        Transition to a new workflow phase.

        Args:
            new_phase: Target phase
            reason: Explanation for phase transition (for observability)
        """
        self.phase_history.append(
            {
                "from_phase": self.phase.value,
                "to_phase": new_phase.value,
                "reason": reason,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        self.phase = new_phase

    def add_knowledge(self, entity: str, entity_type: str = "concept", **attributes):
        """
        Add an entity to the knowledge graph.

        Args:
            entity: Entity name/ID
            entity_type: Type of entity (concept, dataset, variable, etc.)
            **attributes: Additional node attributes
        """
        self.knowledge_graph.add_node(entity, type=entity_type, **attributes)

    def add_relationship(self, source: str, target: str, relation: str, **attributes):
        """
        Add a relationship to the knowledge graph.

        Args:
            source: Source entity
            target: Target entity
            relation: Relationship type (causes, correlates_with, derived_from, etc.)
            **attributes: Additional edge attributes
        """
        self.knowledge_graph.add_edge(source, target, relation=relation, **attributes)

    def get_hypothesis(self, hypothesis_id: str) -> Hypothesis | None:
        """Retrieve a hypothesis by ID."""
        for h in self.hypotheses:
            if h.id == hypothesis_id:
                return h
        return None

    def update_hypothesis_confidence(self, hypothesis_id: str, new_confidence: float):
        """Update confidence score for a hypothesis."""
        hyp = self.get_hypothesis(hypothesis_id)
        if hyp:
            hyp.confidence = new_confidence

    def get_top_hypotheses(self, k: int = 5) -> list[Hypothesis]:
        """Get top-k hypotheses by confidence score."""
        return sorted(self.hypotheses, key=lambda h: h.confidence, reverse=True)[:k]

    def get_untested_hypotheses(self) -> list[Hypothesis]:
        """Get all hypotheses that haven't been tested yet."""
        return [h for h in self.hypotheses if not h.tested]

    def record_cost(self, tokens: int, model: str, cost: float):
        """
        Record token usage and cost for observability.

        Args:
            tokens: Number of tokens consumed
            model: Model name (gemini-2.5-pro, gemini-2.5-flash)
            cost: Cost in USD
        """
        self.total_tokens += tokens
        self.total_cost += cost

    def get_summary(self) -> dict[str, Any]:
        """
        Get a summary of the current world model state.

        Returns:
            Dictionary with key metrics and statistics
        """
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "status": self.status,
            "phase": self.phase.value,
            "created_at": self.created_at.isoformat(),
            "num_hypotheses": len(self.hypotheses),
            "num_tested_hypotheses": sum(1 for h in self.hypotheses if h.tested),
            "num_analysis_results": len(self.analysis_results),
            "num_literature_refs": len(self.literature_refs),
            "knowledge_graph_nodes": self.knowledge_graph.number_of_nodes(),
            "knowledge_graph_edges": self.knowledge_graph.number_of_edges(),
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
            "top_hypotheses": [{"id": h.id, "text": h.text, "confidence": h.confidence} for h in self.get_top_hypotheses(3)],
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize world model to dictionary for persistence.

        Returns:
            Dictionary representation suitable for Firestore/JSON storage
        """
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "phase": self.phase.value,
            "phase_history": self.phase_history,
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "analysis_results": [r.to_dict() for r in self.analysis_results],
            "literature_refs": [ref.to_dict() for ref in self.literature_refs],
            "knowledge_graph": nx.node_link_data(self.knowledge_graph),
            "total_cost": self.total_cost,
            "total_tokens": self.total_tokens,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KosmosWorldModel:
        """
        Deserialize world model from dictionary.

        Args:
            data: Dictionary from to_dict()

        Returns:
            Reconstructed KosmosWorldModel instance
        """
        model = cls(session_id=data["session_id"], goal=data["goal"])
        model.created_at = datetime.fromisoformat(data["created_at"])
        model.status = data["status"]
        model.phase = WorkflowPhase(data["phase"])
        model.phase_history = data["phase_history"]
        model.total_cost = data["total_cost"]
        model.total_tokens = data["total_tokens"]

        model.hypotheses = [Hypothesis.from_dict(h) for h in data["hypotheses"]]
        model.analysis_results = [AnalysisResult.from_dict(r) for r in data["analysis_results"]]
        model.literature_refs = [LiteratureRef.from_dict(ref) for ref in data["literature_refs"]]
        model.knowledge_graph = nx.node_link_graph(data["knowledge_graph"])

        return model

    def __repr__(self) -> str:
        return f"KosmosWorldModel(session={self.session_id}, phase={self.phase.value}, hypotheses={len(self.hypotheses)}, status={self.status})"
