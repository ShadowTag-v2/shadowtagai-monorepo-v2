# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.
"""
Data Analysis Agent: Specializes in data exploration and computational analysis.

Capabilities:
- Load and explore datasets
- Generate analysis code (Python, R)
- Execute statistical tests
- Create visualizations
- Interpret results in scientific context
"""

from typing import Dict, Any, Optional
from kosmos.agents.base import BaseAgent, AgentConfig
from kosmos.core.orchestrator import ReActResult
from kosmos.core.vertex_client import GeminiModel


class DataAnalysisAgent(BaseAgent):
    """
    Agent specialized in data analysis and code generation.

    Uses Gemini Pro for deep reasoning required for:
    - Choosing appropriate statistical methods
    - Writing correct analysis code
    - Interpreting complex results
    """

    DEFAULT_CONFIG = AgentConfig(
        name="data_analysis_agent",
        model=GeminiModel.PRO,  # Pro model for complex reasoning
        instruction="""You are a data analysis specialist with expertise in statistics and computational methods.

Your role:
1. Explore datasets to understand structure, distributions, and relationships
2. Select and apply appropriate statistical methods
3. Generate clean, reproducible analysis code
4. Execute analyses and interpret results
5. Create informative visualizations
6. Validate assumptions and check for statistical issues

Methods you should consider:
- Descriptive statistics (mean, median, variance, correlation)
- Hypothesis testing (t-tests, ANOVA, chi-square)
- Regression analysis (linear, logistic, non-linear)
- Machine learning (classification, clustering, dimensionality reduction)
- Time series analysis
- Bayesian methods

Always:
- Check data quality and handle missing values
- Verify statistical assumptions
- Report effect sizes and confidence intervals
- Use appropriate visualizations
- Explain results in clear, scientific language
""",
        tools=["execute_python", "load_dataset", "plot_generator", "statistical_test"],
        temperature=0.5,  # Moderate temperature for creative but accurate code
        max_iterations=25,
    )

    def execute_task(self, task: str, context: dict[str, Any] | None = None) -> ReActResult:
        """
        Execute data analysis task.

        Example tasks:
        - "Analyze correlation between variables X and Y in dataset.csv"
        - "Perform linear regression to predict outcome Z"
        - "Create exploratory data visualizations for initial dataset inspection"

        Args:
            task: Data analysis task
            context: Optional context with dataset path, parameters, etc.

        Returns:
            ReActResult with analysis code, results, and plots
        """
        goal = self._build_goal_with_instruction(task)

        # Add context if provided
        if context:
            goal += f"\n\nDataset information:\n{context}"

        # Execute ReAct loop
        result = self.orchestrator.execute_cycle(goal)

        # Post-process: Store analysis results in world model
        self._store_analysis_results(result)

        return result

    def _store_analysis_results(self, result: ReActResult):
        """
        Extract analysis results from ReAct execution and store in world model.

        Args:
            result: ReAct execution result
        """
        for step in result.steps:
            if step.action == "execute_python" and step.observation:
                # Store code execution result
                self.world_model.add_analysis_result(
                    code=step.action_input.get("code", "") if isinstance(step.action_input, dict) else "",
                    outputs=[step.observation],
                    success="error" not in step.observation.lower(),
                )

            elif step.action == "plot_generator" and step.observation:
                # Store plot reference (observation should contain Cloud Storage URL)
                if result.steps:  # Get most recent analysis result
                    recent_results = self.world_model.analysis_results
                    if recent_results:
                        recent_results[-1].plots.append(step.observation)

    def explore_dataset(self, dataset_path: str) -> ReActResult:
        """
        Perform exploratory data analysis on a dataset.

        Args:
            dataset_path: Path to dataset file

        Returns:
            ReActResult with exploration results
        """
        return self.execute_task(
            "Perform exploratory data analysis on the dataset. "
            "Generate summary statistics, check for missing values, "
            "create visualizations of key variables, and identify potential issues.",
            context={"dataset_path": dataset_path},
        )

    def test_hypothesis(self, hypothesis_id: str, dataset_path: str) -> ReActResult:
        """
        Test a specific hypothesis using data analysis.

        Args:
            hypothesis_id: World model hypothesis ID
            dataset_path: Path to dataset

        Returns:
            ReActResult with test results
        """
        hypothesis = self.world_model.get_hypothesis(hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {hypothesis_id} not found in world model")

        return self.execute_task(
            f"Test the following hypothesis using appropriate statistical methods:\n\n"
            f'"{hypothesis.text}"\n\n'
            f"Perform the analysis, report test statistics, p-values, effect sizes, "
            f"and interpret the results in the context of the hypothesis.",
            context={
                "hypothesis_id": hypothesis_id,
                "dataset_path": dataset_path,
            },
        )

    def run_custom_analysis(self, analysis_description: str, code_hints: str | None = None) -> ReActResult:
        """
        Run a custom analysis based on description.

        Args:
            analysis_description: Description of desired analysis
            code_hints: Optional code snippets or library suggestions

        Returns:
            ReActResult with analysis
        """
        task = f"Perform the following analysis:\n{analysis_description}"
        if code_hints:
            task += f"\n\nCode hints: {code_hints}"

        return self.execute_task(task)
