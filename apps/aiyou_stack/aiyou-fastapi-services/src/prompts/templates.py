# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Prompt Templates for SELF-ROUTE Implementation
Based on research paper specifications (Table 9)

Templates optimized for Gemini-1.5-Pro/Flash with:
- Strict constraint phrases to prevent parametric knowledge leakage
- Explicit "unanswerable" detection for routing
- Task-specific formatting (legal, multi-hop, narrative, etc.)
"""

from enum import Enum


class TaskType(Enum):
    """Task types with different prompt strategies"""

    LEGAL_COMPLIANCE = "legal_compliance"
    MULTI_HOP = "multi_hop"
    NARRATIVE = "narrative"
    SCIENTIFIC = "scientific"
    SUMMARIZATION = "summarization"
    GENERAL = "general"


class PromptTemplates:
    """Collection of prompt templates for different task types"""

    # ========================================================================
    # LEGAL / COMPLIANCE DOCUMENT PROMPTS
    # ========================================================================

    LEGAL_RAG_PROMPT = """You are analyzing legal and compliance documents.

Document chunks (retrieved by similarity):
{chunks_with_indices}

Question: {query}

Instructions:
1. Determine if you can answer this question based ONLY on the provided document chunks.
2. If you can answer, provide a precise answer citing the chunk index [e.g., "According to chunk 3, ..."].
3. If you CANNOT answer confidently based solely on these chunks, respond with exactly: "unanswerable"

Do not use external knowledge. Do not provide speculative answers.

Answer:"""

    LEGAL_LC_PROMPT = """You are analyzing the following complete legal/compliance document.

Full Document:
{full_context}

Question: {query}

Provide a comprehensive answer based ONLY on the information in this document.
If the document does not contain sufficient information, state this clearly.
Do not use external legal knowledge beyond what is in the document.

Answer:"""

    # ========================================================================
    # MULTI-HOP REASONING PROMPTS
    # ========================================================================

    MULTIHOP_RAG_PROMPT = """Answer the question based on the given passages.

Passages:
{numbered_chunks}

Question: {query}

If you can derive the answer through logical steps using only these passages, provide the answer.
If the passages do not contain the necessary information for all reasoning steps, respond: "unanswerable"

Only give the final answer without explanation. If unanswerable, write exactly: "unanswerable"

Answer:"""

    MULTIHOP_LC_PROMPT = """Answer the question based on the complete text below.

Text: {full_context}

Question: {query}

Provide only the final answer, no explanation needed.

Answer:"""

    # ========================================================================
    # NARRATIVE / DOCUMENT QA PROMPTS
    # ========================================================================

    NARRATIVE_RAG_PROMPT = """You are given excerpts from a story/document and a question.

Story excerpts:
{chunks}

Question: {query}

Answer the question as concisely as possible using only these excerpts.
If the excerpts do not provide enough context to answer accurately, respond: "unanswerable"
Do not provide explanations or reasoning.

Answer:"""

    NARRATIVE_LC_PROMPT = """You are given a complete story/document and a question.

Story: {full_context}

Question: {query}

Answer the question as concisely as you can, using a single phrase if possible.
Base your answer only on the provided story.

Answer:"""

    # ========================================================================
    # SCIENTIFIC / TECHNICAL QA PROMPTS
    # ========================================================================

    SCIENTIFIC_RAG_PROMPT = """You are analyzing scientific/technical document excerpts.

Text excerpts:
{chunks_with_indices}

Question: {query}

Instructions:
1. Answer based ONLY on the provided excerpts
2. Cite chunk numbers when possible
3. If information is insufficient, respond: "unanswerable"

Answer:"""

    SCIENTIFIC_LC_PROMPT = """You are analyzing the following complete scientific/technical document.

Document:
{full_context}

Question: {query}

Provide a precise answer based only on this document.

Answer:"""

    # ========================================================================
    # SUMMARIZATION PROMPTS
    # ========================================================================

    SUMMARIZATION_RAG_PROMPT = """Summarize the information from these text segments relevant to the query.

Text segments:
{chunks}

Query: {query}

Provide a concise summary based on these segments.
If the segments don't contain relevant information, respond: "unanswerable"

Summary:"""

    SUMMARIZATION_LC_PROMPT = """Summarize the following text to address the query.

Text: {full_context}

Query: {query}

Provide a concise, relevant summary.

Summary:"""

    # ========================================================================
    # GENERAL PURPOSE PROMPTS
    # ========================================================================

    GENERAL_RAG_PROMPT = """You are given text chunks and a question.

Text chunks:
{chunks_with_indices}

Question: {query}

(1) Determine if the question can be answered based ONLY on the provided text chunks.
(2) If answerable, provide the answer concisely.
(3) If NOT answerable, respond with exactly: "unanswerable"

Answer:"""

    GENERAL_LC_PROMPT = """Based on the following complete text, answer the question.

Text: {full_context}

Question: {query}

Answer:"""

    @staticmethod
    def format_chunks_with_indices(chunks: list[str], indices: list[int] = None) -> str:
        """Format chunks with numbered indices for citation

        Args:
            chunks: List of text chunks
            indices: Optional original chunk indices

        Returns:
            Formatted string with numbered chunks

        """
        formatted_parts = []

        for i, chunk in enumerate(chunks, 1):
            if indices:
                header = f"[Chunk {i} | Document Index: {indices[i - 1]}]"
            else:
                header = f"[Chunk {i}]"

            formatted_parts.append(f"{header}\n{chunk}")

        return "\n\n".join(formatted_parts)

    @staticmethod
    def format_chunks_simple(chunks: list[str]) -> str:
        """Format chunks with simple numbering

        Args:
            chunks: List of text chunks

        Returns:
            Formatted string with numbered chunks

        """
        formatted_parts = []

        for i, chunk in enumerate(chunks, 1):
            formatted_parts.append(f"Passage {i}: {chunk}")

        return "\n\n".join(formatted_parts)

    @classmethod
    def get_rag_prompt(
        cls,
        task_type: TaskType,
        query: str,
        chunks: list[str],
        indices: list[int] = None,
    ) -> str:
        """Get RAG prompt for specific task type

        Args:
            task_type: Type of task (legal, multi-hop, etc.)
            query: User query
            chunks: Retrieved text chunks
            indices: Optional chunk indices

        Returns:
            Formatted RAG prompt

        """
        # Format chunks based on task type
        if task_type in [TaskType.LEGAL_COMPLIANCE, TaskType.SCIENTIFIC, TaskType.GENERAL]:
            chunks_formatted = cls.format_chunks_with_indices(chunks, indices)
        elif task_type == TaskType.MULTI_HOP:
            chunks_formatted = cls.format_chunks_simple(chunks)
        else:  # NARRATIVE, SUMMARIZATION
            chunks_formatted = "\n\n".join(chunks)

        # Select appropriate template
        template_map = {
            TaskType.LEGAL_COMPLIANCE: cls.LEGAL_RAG_PROMPT,
            TaskType.MULTI_HOP: cls.MULTIHOP_RAG_PROMPT,
            TaskType.NARRATIVE: cls.NARRATIVE_RAG_PROMPT,
            TaskType.SCIENTIFIC: cls.SCIENTIFIC_RAG_PROMPT,
            TaskType.SUMMARIZATION: cls.SUMMARIZATION_RAG_PROMPT,
            TaskType.GENERAL: cls.GENERAL_RAG_PROMPT,
        }

        template = template_map[task_type]

        # Fill template
        return template.format(
            query=query,
            chunks_with_indices=chunks_formatted,
            numbered_chunks=chunks_formatted,
            chunks=chunks_formatted,
        )

    @classmethod
    def get_lc_prompt(cls, task_type: TaskType, query: str, full_context: str) -> str:
        """Get Long-Context prompt for specific task type

        Args:
            task_type: Type of task
            query: User query
            full_context: Full document text

        Returns:
            Formatted LC prompt

        """
        template_map = {
            TaskType.LEGAL_COMPLIANCE: cls.LEGAL_LC_PROMPT,
            TaskType.MULTI_HOP: cls.MULTIHOP_LC_PROMPT,
            TaskType.NARRATIVE: cls.NARRATIVE_LC_PROMPT,
            TaskType.SCIENTIFIC: cls.SCIENTIFIC_LC_PROMPT,
            TaskType.SUMMARIZATION: cls.SUMMARIZATION_LC_PROMPT,
            TaskType.GENERAL: cls.GENERAL_LC_PROMPT,
        }

        template = template_map[task_type]

        return template.format(query=query, full_context=full_context)


class QueryClassifier:
    """Classify query complexity to predict routing likelihood
    Based on Section 5.2 failure patterns
    """

    @staticmethod
    def classify_complexity(query: str) -> str:
        """Classify query into complexity categories

        Returns: "SIMPLE", "MULTIHOP", "COMPLEX", "CAUSAL"
        """
        query_lower = query.lower()
        word_count = len(query.split())

        # Pattern A: Multi-hop reasoning
        multihop_patterns = [
            "'s",
            "of the",
            "performed by",
            "directed by",
            "nationality of",
            "location of",
            "where does",
        ]
        if any(pattern in query_lower for pattern in multihop_patterns):
            return "MULTIHOP"

        # Pattern D: Causal/implicit context
        causal_patterns = [
            "what caused",
            "why did",
            "what led to",
            "how did",
            "what made",
            "reason for",
        ]
        if any(query_lower.startswith(pattern) for pattern in causal_patterns):
            return "CAUSAL"

        # Pattern C: Complex queries (>25 words with multiple clauses)
        if word_count > 25 and ("when" in query_lower or "while" in query_lower):
            return "COMPLEX"

        # Default: Simple
        return "SIMPLE"

    @staticmethod
    def detect_task_type(query: str, domain_hint: str = None) -> TaskType:
        """Detect task type from query and domain

        Args:
            query: User query
            domain_hint: Optional domain hint (e.g., "legal", "scientific")

        Returns:
            TaskType enum

        """
        query_lower = query.lower()

        # Domain-based detection
        if domain_hint:
            domain_map = {
                "legal": TaskType.LEGAL_COMPLIANCE,
                "compliance": TaskType.LEGAL_COMPLIANCE,
                "regulatory": TaskType.LEGAL_COMPLIANCE,
                "scientific": TaskType.SCIENTIFIC,
                "technical": TaskType.SCIENTIFIC,
                "story": TaskType.NARRATIVE,
                "narrative": TaskType.NARRATIVE,
            }
            if domain_hint.lower() in domain_map:
                return domain_map[domain_hint.lower()]

        # Query-based detection
        if "summarize" in query_lower or "summary of" in query_lower:
            return TaskType.SUMMARIZATION

        if QueryClassifier.classify_complexity(query) == "MULTIHOP":
            return TaskType.MULTI_HOP

        if any(word in query_lower for word in ["story", "narrative", "character", "plot"]):
            return TaskType.NARRATIVE

        # Default to general
        return TaskType.GENERAL

    @staticmethod
    def should_force_lc(query: str) -> bool:
        """Determine if query should bypass RAG and go straight to LC

        Based on Pattern D (implicit context failures)
        """
        complexity = QueryClassifier.classify_complexity(query)

        # Force LC for causal queries
        if complexity == "CAUSAL":
            return True

        # Force LC for very long, complex queries
        return bool(complexity == "COMPLEX" and len(query.split()) > 40)
