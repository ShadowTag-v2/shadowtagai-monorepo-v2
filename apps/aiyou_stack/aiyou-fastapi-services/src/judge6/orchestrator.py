# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Judge 6 LangGraph Orchestrator
Multi-agent workflow for compliance document analysis
"""

import json
import logging
import operator
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, TypedDict

from google.cloud import firestore, monitoring_v3

# RIPPED OUT BY NAG 2 - Langchain crashes on Py 3.14
# from langchain_core.messages import HumanMessage, SystemMessage
# from langchain_google_vertexai import ChatVertexAI
# from langgraph.checkpoint.memory import MemorySaver
# from langgraph.graph import END, START, StateGraph


class MockGraph:
    pass


class MockVertex:
    pass


HumanMessage = SystemMessage = MockVertex
ChatVertexAI = MockVertex
MemorySaver = MockGraph
END = START = StateGraph = Any

logger = logging.getLogger(__name__)


class ComplianceFramework(StrEnum):
    """Supported compliance frameworks"""

    FDA_21CFR_PART11 = "FDA 21 CFR Part 11"
    SEC_FILINGS = "SEC Filings"
    ITAR = "ITAR"
    CMMC = "CMMC"
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    SOC2 = "SOC 2"


class WorkflowStep(StrEnum):
    """Workflow processing steps"""

    CLASSIFY = "classify"
    PARSE = "parse"
    EXTRACT = "extract"
    CHECK = "check"
    RECOMMEND = "recommend"
    COMPLETE = "complete"


class Cor.Claude_Code_6State(TypedDict):
    """Shared state across all Judge 6 agents.
    Uses Annotated with operator.add for list fields to enable proper state merging.
    """

    # Document metadata
    workflow_id: str
    document_id: str
    document_content: str
    document_type: str

    # Framework detection
    compliance_framework: ComplianceFramework
    confidence_score: float

    # Extracted entities
    extracted_policies: Annotated[list[dict], operator.add]
    extracted_entities: Annotated[list[dict], operator.add]

    # Compliance analysis
    violations: Annotated[list[dict], operator.add]
    warnings: Annotated[list[dict], operator.add]

    # Recommendations
    recommendations: Annotated[list[dict], operator.add]

    # Workflow state
    current_step: WorkflowStep
    agent_outputs: dict[str, Any]
    error: str

    # Performance tracking
    start_time: datetime
    end_time: datetime
    tokens_used: int


class Cor.Claude_Code_6Orchestrator:
    """LangGraph-based orchestrator for Judge 6 multi-agent compliance analysis.

    Uses supervisor pattern with specialized agents for each workflow step.
    """

    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_endpoint: str = None,
        firestore_collection: str = "Cor.Claude_Code_6_workflows",
    ):
        self.project_id = project_id
        self.location = location
        self.model_endpoint = model_endpoint or "http://judge-6-vllm.judge-6.svc.cluster.local:8000"

        # Initialize Firestore for durable state
        self.firestore_client = firestore.Client(project=project_id)
        self.firestore_collection = firestore_collection

        # Initialize monitoring
        self.monitoring_client = monitoring_v3.MetricServiceClient()

        # Initialize LLM clients for different agents
        self.supervisor_llm = ChatVertexAI(
            model="gemini-3.1-flash-lite-preview",
            project=project_id,
            location=location,
            temperature=0.1,  # Low temperature for consistent routing
        )

        self.thinking_llm = ChatVertexAI(
            model="gemini-3.1-flash-lite-preview-thinking-exp-1219",
            project=project_id,
            location=location,
            temperature=0.3,  # Slightly higher for reasoning
        )

        self.fast_llm = ChatVertexAI(
            model="gemini-3.1-flash-lite-preview",
            project=project_id,
            location=location,
            temperature=0,  # Deterministic for classification
        )

        # Build workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph state machine for Judge 6 workflow.

        Graph structure:
        START → Supervisor → ClassifyDocument → ParseDocument → ExtractPolicies
                ↓                                                      ↓
           CheckCompliance ←────────────────────────────────────────────
                ↓
           GenerateRecommendations → END
        """
        workflow = StateGraph(Cor.Claude_Code_6State)

        # Add nodes (agents)
        workflow.add_node("supervisor", self._supervisor_agent)
        workflow.add_node("classify_document", self._classify_document_agent)
        workflow.add_node("parse_document", self._parse_document_agent)
        workflow.add_node("extract_policies", self._extract_policies_agent)
        workflow.add_node("check_compliance", self._check_compliance_agent)
        workflow.add_node("generate_recommendations", self._generate_recommendations_agent)

        # Define edges (control flow)
        workflow.add_edge(START, "supervisor")

        # Supervisor routes to first agent
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {"classify": "classify_document", "complete": END},
        )

        # Linear flow after classification
        workflow.add_edge("classify_document", "parse_document")
        workflow.add_edge("parse_document", "extract_policies")
        workflow.add_edge("extract_policies", "check_compliance")
        workflow.add_edge("check_compliance", "generate_recommendations")

        # Recommendations complete the workflow
        workflow.add_edge("generate_recommendations", END)

        # Compile with checkpointing for resume capability
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    def _supervisor_agent(self, state: Cor.Claude_Code_6State) -> Cor.Claude_Code_6State:
        """Supervisor agent that initializes and monitors the workflow."""
        logger.info(f"Supervisor: Processing workflow {state.get('workflow_id')}")

        # Initialize workflow if first run
        if not state.get("current_step"):
            state["current_step"] = WorkflowStep.CLASSIFY
            state["start_time"] = datetime.utcnow()
            state["extracted_policies"] = []
            state["extracted_entities"] = []
            state["violations"] = []
            state["warnings"] = []
            state["recommendations"] = []
            state["agent_outputs"] = {}
            state["tokens_used"] = 0

            # Save initial state to Firestore
            self._save_state(state)

        return state

    def _classify_document_agent(self, state: Cor.Claude_Code_6State) -> Cor.Claude_Code_6State:
        """Classify document and detect compliance framework."""
        logger.info("Agent: Classifying document")

        prompt = f"""You are a compliance framework classifier.

Analyze this document and determine which compliance framework it relates to:
- FDA 21 CFR Part 11 (pharmaceutical)
- SEC Filings (financial)
- ITAR (defense/export control)
- CMMC (cybersecurity maturity)
- HIPAA (healthcare privacy)
- GDPR (data privacy)
- SOC 2 (security controls)

Document content (first 2000 chars):
{state["document_content"][:2000]}

Return ONLY a JSON object with:
{{
    "framework": "framework name",
    "confidence": 0.95,
    "reasoning": "brief explanation",
    "document_type": "type description"
}}
"""

        messages = [
            SystemMessage(content="You are a compliance framework expert."),
            HumanMessage(content=prompt),
        ]

        response = self.fast_llm.invoke(messages)

        # Parse response (in production, use structured output)

        try:
            result = json.loads(
                response.content.removeprefix("```json\n").removesuffix("```").strip()
            )
            state["compliance_framework"] = result["framework"]
            state["confidence_score"] = result["confidence"]
            state["document_type"] = result.get("document_type", "unknown")
            state["agent_outputs"]["classify"] = result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            state["error"] = f"Classification error: {e}"
            state["compliance_framework"] = ComplianceFramework.SOC2  # Default fallback
            state["confidence_score"] = 0.5

        state["current_step"] = WorkflowStep.PARSE
        self._save_state(state)

        return state

    def _parse_document_agent(self, state: Cor.Claude_Code_6State) -> Cor.Claude_Code_6State:
        """Parse document structure and extract key sections."""
        logger.info("Agent: Parsing document structure")

        prompt = f"""You are a document structure parser for {state["compliance_framework"]} compliance.

Extract the key sections and structure from this document:

{state["document_content"][:10000]}

Return a JSON object with:
{{
    "title": "document title",
    "sections": [
        {{"section_name": "Introduction", "start_line": 1, "end_line": 50}},
        ...
    ],
    "key_dates": ["2025-01-01", ...],
    "referenced_standards": ["21 CFR 11.10", ...]
}}
"""

        messages = [
            SystemMessage(content="You are an expert document parser."),
            HumanMessage(content=prompt),
        ]

        response = self.fast_llm.invoke(messages)

        try:
            result = json.loads(
                response.content.removeprefix("```json\n").removesuffix("```").strip()
            )
            state["agent_outputs"]["parse"] = result
        except Exception as e:
            logger.error(f"Parsing failed: {e}")
            state["agent_outputs"]["parse"] = {"error": str(e)}

        state["current_step"] = WorkflowStep.EXTRACT
        self._save_state(state)

        return state

    def _extract_policies_agent(self, state: Cor.Claude_Code_6State) -> Cor.Claude_Code_6State:
        """Extract compliance policies and requirements using thinking model."""
        logger.info("Agent: Extracting compliance policies")

        framework = state["compliance_framework"]

        prompt = f"""You are a {framework} compliance expert.

Extract ALL compliance policies and requirements from this document.

Document:
{state["document_content"]}

For each policy, return:
{{
    "policy_id": "unique identifier",
    "requirement": "what is required",
    "scope": "who it applies to",
    "verification": "how to verify compliance",
    "severity": "critical|high|medium|low"
}}

Return as JSON array: {{"policies": [...]}}
"""

        messages = [
            SystemMessage(
                content=f"You are a {framework} compliance expert with deep knowledge of regulations.",
            ),
            HumanMessage(content=prompt),
        ]

        response = self.thinking_llm.invoke(messages)

        try:
            result = json.loads(
                response.content.removeprefix("```json\n").removesuffix("```").strip()
            )
            state["extracted_policies"] = result.get("policies", [])
            state["agent_outputs"]["extract"] = result
        except Exception as e:
            logger.error(f"Policy extraction failed: {e}")
            state["extracted_policies"] = []

        state["current_step"] = WorkflowStep.CHECK
        self._save_state(state)

        return state

    def _check_compliance_agent(self, state: Cor.Claude_Code_6State) -> Cor.Claude_Code_6State:
        """Check extracted policies against compliance framework requirements."""
        logger.info("Agent: Checking compliance")

        framework = state["compliance_framework"]
        policies = state["extracted_policies"]

        prompt = f"""You are a {framework} compliance auditor.

These policies were extracted from a document:
{json.dumps(policies, indent=2)}

Check each policy for:
1. Completeness (all required elements present)
2. Clarity (unambiguous language)
3. Enforceability (can be verified/tested)
4. Alignment with {framework} requirements

Return:
{{
    "violations": [
        {{"policy_id": "...", "issue": "...", "severity": "critical|high|medium|low", "remedy": "..."}}
    ],
    "warnings": [
        {{"policy_id": "...", "concern": "...", "suggestion": "..."}}
    ],
    "compliance_score": 0.85
}}
"""

        messages = [
            SystemMessage(content=f"You are a strict {framework} compliance auditor."),
            HumanMessage(content=prompt),
        ]

        response = self.thinking_llm.invoke(messages)

        try:
            result = json.loads(
                response.content.removeprefix("```json\n").removesuffix("```").strip()
            )
            state["violations"] = result.get("violations", [])
            state["warnings"] = result.get("warnings", [])
            state["agent_outputs"]["check"] = result
        except Exception as e:
            logger.error(f"Compliance check failed: {e}")
            state["violations"] = []
            state["warnings"] = []

        state["current_step"] = WorkflowStep.RECOMMEND
        self._save_state(state)

        return state

    def _generate_recommendations_agent(self, state: Cor.Claude_Code_6State) -> Cor.Claude_Code_6State:
        """Generate remediation recommendations for violations and warnings."""
        logger.info("Agent: Generating recommendations")

        violations = state["violations"]
        warnings = state["warnings"]
        framework = state["compliance_framework"]

        prompt = f"""You are a {framework} compliance consultant.

Generate actionable recommendations to address these issues:

Violations:
{json.dumps(violations, indent=2)}

Warnings:
{json.dumps(warnings, indent=2)}

For each issue, provide:
{{
    "issue_id": "...",
    "recommendation": "specific action to take",
    "implementation_steps": ["step 1", "step 2", ...],
    "estimated_effort": "hours or days",
    "priority": "critical|high|medium|low",
    "related_standards": ["standard reference", ...]
}}

Return: {{"recommendations": [...]}}
"""

        messages = [
            SystemMessage(content=f"You are an expert {framework} compliance consultant."),
            HumanMessage(content=prompt),
        ]

        response = self.thinking_llm.invoke(messages)

        try:
            result = json.loads(
                response.content.removeprefix("```json\n").removesuffix("```").strip()
            )
            state["recommendations"] = result.get("recommendations", [])
            state["agent_outputs"]["recommend"] = result
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            state["recommendations"] = []

        # Finalize workflow
        state["current_step"] = WorkflowStep.COMPLETE
        state["end_time"] = datetime.utcnow()

        self._save_state(state)
        self._record_metrics(state)

        return state

    def _route_from_supervisor(self, state: Cor.Claude_Code_6State) -> str:
        """Routing function for supervisor to next agent."""
        if state.get("current_step") == WorkflowStep.CLASSIFY:
            return "classify"
        return "complete"

    def _save_state(self, state: Cor.Claude_Code_6State):
        """Save workflow state to Firestore for durability and audit trail."""
        try:
            doc_ref = self.firestore_client.collection(self.firestore_collection).document(
                state["workflow_id"],
            )
            doc_ref.set(
                {
                    "workflow_id": state["workflow_id"],
                    "document_id": state["document_id"],
                    "compliance_framework": state.get("compliance_framework"),
                    "current_step": state.get("current_step"),
                    "violations_count": len(state.get("violations", [])),
                    "warnings_count": len(state.get("warnings", [])),
                    "recommendations_count": len(state.get("recommendations", [])),
                    "updated_at": firestore.SERVER_TIMESTAMP,
                    "state_snapshot": state,
                },
                merge=True,
            )
        except Exception as e:
            logger.error(f"Failed to save state to Firestore: {e}")

    def _record_metrics(self, state: Cor.Claude_Code_6State):
        """Record workflow metrics to Cloud Monitoring."""
        try:
            duration = (state["end_time"] - state["start_time"]).total_seconds()

            # Record duration metric
            series = monitoring_v3.TimeSeries()
            series.metric.type = "custom.googleapis.com/Cor.Claude_Code_6/workflow_duration_seconds"
            series.resource.type = "global"
            series.points = [
                monitoring_v3.Point(
                    {
                        "interval": {"end_time": {"seconds": int(datetime.utcnow().timestamp())}},
                        "value": {"double_value": duration},
                    },
                ),
            ]

            project_name = f"projects/{self.project_id}"
            self.monitoring_client.create_time_series(name=project_name, time_series=[series])

            logger.info(f"Workflow {state['workflow_id']} completed in {duration:.2f}s")
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")

    def process_document(self, document_id: str, document_content: str) -> dict[str, Any]:
        """Process a compliance document through the Judge 6 workflow.

        Args:
            document_id: Unique identifier for the document
            document_content: Full text content of the document

        Returns:
            Final workflow state with compliance analysis results

        """
        import uuid

        workflow_id = f"wf-{uuid.uuid4()}"

        initial_state = Cor.Claude_Code_6State(
            workflow_id=workflow_id,
            document_id=document_id,
            document_content=document_content,
            document_type="",
            compliance_framework=None,
            confidence_score=0.0,
            extracted_policies=[],
            extracted_entities=[],
            violations=[],
            warnings=[],
            recommendations=[],
            current_step=None,
            agent_outputs={},
            error="",
            start_time=None,
            end_time=None,
            tokens_used=0,
        )

        # Execute workflow
        config = {"configurable": {"thread_id": workflow_id}}
        final_state = self.workflow.invoke(initial_state, config)

        return final_state


# Example usage
if __name__ == "__main__":
    import os

    project_id = os.getenv("GCP_PROJECT_ID", "pnkln-prod")

    orchestrator = Cor.Claude_Code_6Orchestrator(project_id=project_id)

    sample_document = """
    FDA 21 CFR Part 11 Compliance Policy

    1. Electronic Records
    All electronic records must be maintained in accordance with 21 CFR 11.10.

    2. Electronic Signatures
    Electronic signatures must be unique to one individual and verified.

    3. Audit Trail
    Systems must maintain secure, computer-generated audit trails.
    """

    result = orchestrator.process_document(
        document_id="sample-fda-policy-001",
        document_content=sample_document,
    )

    print(f"Workflow ID: {result['workflow_id']}")
    print(f"Framework: {result['compliance_framework']}")
    print(f"Violations: {len(result['violations'])}")
    print(f"Recommendations: {len(result['recommendations'])}")
