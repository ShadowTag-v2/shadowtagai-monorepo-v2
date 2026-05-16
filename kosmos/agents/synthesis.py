# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Synthesis Agent: Specializes in synthesizing findings into structured reports.

Capabilities:
- Synthesize results from multiple sources
- Write scientific reports with proper structure
- Format citations and references
- Create executive summaries
- Generate publication-ready figures
"""

from typing import Any
from kosmos.agents.base import BaseAgent, AgentConfig
from kosmos.core.orchestrator import ReActResult
from kosmos.core.vertex_client import GeminiModel


class SynthesisAgent(BaseAgent):
  """
  Agent specialized in synthesis and report writing.

  Uses Gemini Pro for high-quality scientific writing.
  Produces structured reports that synthesize findings from
  literature, analyses, and hypothesis testing.
  """

  DEFAULT_CONFIG = AgentConfig(
    name="synthesis_agent",
    model=GeminiModel.PRO,  # Pro model for high-quality writing
    instruction="""You are a scientific writing and synthesis specialist.

Your role:
1. Synthesize findings from multiple sources (literature, data, hypotheses)
2. Write clear, rigorous scientific reports
3. Structure content logically with proper sections
4. Format citations and references correctly
5. Create executive summaries for non-technical audiences

Report structure:
- **Abstract**: 150-250 word summary of entire work
- **Introduction**: Background, motivation, research questions
- **Methods**: Data sources, analysis approaches, tools used
- **Results**: Key findings with supporting evidence (tables, figures)
- **Discussion**: Interpretation, implications, limitations
- **Conclusions**: Main takeaways and future directions
- **References**: Properly formatted citations

Writing principles:
- **Clarity**: Use clear, precise language
- **Rigor**: Support claims with evidence
- **Objectivity**: Present findings honestly, acknowledge uncertainty
- **Conciseness**: Eliminate unnecessary words
- **Logical flow**: Organize ideas coherently

Citation style:
- Use APA, IEEE, or Nature format (specify in context)
- Include all necessary metadata (authors, year, title, venue)
- Maintain citation consistency throughout

Always:
- Check for statistical claims that need supporting evidence
- Verify that figures/tables are referenced in text
- Ensure proper attribution of ideas
- Flag areas needing more evidence
""",
    tools=["report_writer", "citation_formatter", "figure_generator"],
    temperature=0.6,  # Moderate temperature for creative but accurate writing
    max_iterations=20,
  )

  def execute_task(
    self, task: str, context: dict[str, Any] | None = None
  ) -> ReActResult:
    """
    Execute synthesis/writing task.

    Example tasks:
    - "Write research report synthesizing all findings"
    - "Create executive summary of hypothesis testing results"
    - "Generate discussion section interpreting analysis results"

    Args:
        task: Synthesis task
        context: Optional context with formatting preferences, etc.

    Returns:
        ReActResult with generated report
    """
    goal = self._build_goal_with_instruction(task)

    # Add world model context
    summary = self.world_model.get_summary()
    goal += "\n\nAvailable content to synthesize:\n"
    goal += f"- Research goal: {self.world_model.goal}\n"
    goal += f"- Phase: {summary['phase']}\n"
    goal += f"- Hypotheses: {summary['num_hypotheses']} "
    goal += f"({summary['num_tested_hypotheses']} tested)\n"
    goal += f"- Analysis results: {summary['num_analysis_results']}\n"
    goal += f"- Literature references: {summary['num_literature_refs']}\n"

    # Add top hypotheses for context
    if summary["top_hypotheses"]:
      goal += "\n\nTop hypotheses:\n"
      for h in summary["top_hypotheses"]:
        goal += f"- {h['text']} (confidence: {h['confidence']:.2f})\n"

    if context:
      goal += f"\n\nFormatting preferences:\n{context}"

    # Execute ReAct loop
    result = self.orchestrator.execute_cycle(goal)

    return result

  def write_full_report(
    self,
    title: str | None = None,
    citation_style: str = "APA",
  ) -> ReActResult:
    """
    Write a complete research report synthesizing all findings.

    Args:
        title: Optional report title (auto-generated if None)
        citation_style: Citation format (APA, IEEE, Nature, etc.)

    Returns:
        ReActResult with full report
    """
    if title is None:
      title = f"Research Report: {self.world_model.goal}"

    return self.execute_task(
      f"Write a complete research report with title: '{title}'\n\n"
      f"Include all standard sections: Abstract, Introduction, Methods, "
      f"Results, Discussion, Conclusions, References.\n\n"
      f"Synthesize all available findings from hypotheses, analyses, and literature.\n"
      f"Use proper scientific writing style and {citation_style} citation format.",
      context={"title": title, "citation_style": citation_style},
    )

  def write_executive_summary(self, max_words: int = 500) -> ReActResult:
    """
    Write an executive summary for non-technical audiences.

    Args:
        max_words: Maximum word count

    Returns:
        ReActResult with executive summary
    """
    return self.execute_task(
      f"Write an executive summary (max {max_words} words) for a general audience.\n\n"
      f"Focus on:\n"
      f"1. What question did we investigate?\n"
      f"2. What did we find? (key results)\n"
      f"3. Why does it matter? (implications)\n\n"
      f"Use plain language, avoid jargon, focus on impact.",
      context={"max_words": max_words, "audience": "general"},
    )

  def write_section(
    self,
    section_name: str,
    content_focus: str | None = None,
  ) -> ReActResult:
    """
    Write a specific report section.

    Args:
        section_name: Section to write (e.g., "Methods", "Discussion")
        content_focus: Optional focus/emphasis for this section

    Returns:
        ReActResult with section content
    """
    task = f"Write the {section_name} section of a research report."

    if content_focus:
      task += f"\n\nFocus on: {content_focus}"

    task += (
      f"\n\nFollow standard scientific writing conventions for {section_name} sections."
    )

    return self.execute_task(task)

  def format_references(self, citation_style: str = "APA") -> ReActResult:
    """
    Generate properly formatted reference list from world model literature.

    Args:
        citation_style: Citation format (APA, IEEE, Nature, etc.)

    Returns:
        ReActResult with formatted references
    """
    lit_refs = self.world_model.literature_refs

    if not lit_refs:
      return ReActResult(
        success=True,
        final_answer="No literature references in world model.",
        steps=[],
        total_iterations=0,
        termination_reason="no_work",
      )

    refs_text = "\n".join(
      [
        f"{i + 1}. {ref.title} - {', '.join(ref.authors)}"
        for i, ref in enumerate(lit_refs)
      ]
    )

    return self.execute_task(
      f"Format the following references in {citation_style} style:\n\n"
      f"{refs_text}\n\n"
      f"Produce a properly formatted reference list, sorted alphabetically by author.",
      context={"citation_style": citation_style},
    )

  def create_figures_and_tables(self) -> ReActResult:
    """
    Generate publication-ready figures and tables from analysis results.

    Returns:
        ReActResult with figure/table descriptions and references
    """
    return self.execute_task(
      "Review all analysis results and create:\n"
      "1. List of publication-ready figures (with captions)\n"
      "2. List of tables summarizing key results\n"
      "3. Recommendations for figure/table placement in report\n\n"
      "For each figure/table, provide:\n"
      "- Descriptive caption\n"
      "- Data source\n"
      "- Key takeaway message"
    )
