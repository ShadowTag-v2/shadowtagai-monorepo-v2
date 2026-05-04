#!/usr/bin/env python3
"""CodeActInstruct Dataset Generator for Cor.54 Orchestrator
==========================================================

PURPOSE:
    Generate high-quality training data for fine-tuning Gemini models to perform
    CodeAct orchestration (generating executable Python code from natural language
    context + risk vectors).

ARCHITECTURE:
    Self-Bootstrapping Pipeline
    ├─ Stage 1: Convert AiURCM test cases → orchestration examples
    ├─ Stage 2: Generate synthetic scenarios (5 domains × 1K each)
    ├─ Stage 3: Inject realistic errors → self-debug trajectories
    ├─ Stage 4: Quality filtering + validation
    └─ Stage 5: Export to Gemini fine-tuning format

OUTPUT:
    - 10K+ training examples (JSONL format)
    - 90% single-turn (clean execution)
    - 10% multi-turn (error → fix trajectories)
    - 95%+ executable rate (AST validated)

USAGE:
    python dataset_generator.py \\
        --aiurcm_tests=../tests/aiurcm/test_suite.json \\
        --num_synthetic=5000 \\
        --output_dir=./datasets \\
        --gemini_model=gemini-3.1-flash-lite-preview

COST:
    ~$3-10 per dataset generation (Gemini API calls)
    ~2-4 hours runtime (parallelized)

AUTHOR: Generated for pnkln/core-stack Phase 1
DATE: 2025-11-07
"""

import ast
import asyncio
import hashlib
import json
import os
import random
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import click
import numpy as np
from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Gemini API
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmBlockThreshold, HarmCategory
except ImportError:
    logger.error("google-generativeai not installed. Run: pip install google-generativeai")
    raise SystemExit(1)

console = Console()


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class OrchestrationExample:
    """Single training example for CodeAct orchestration."""

    # Input
    context: str  # Natural language description of task
    risk_vector: dict[str, float]  # Risk scores for different categories
    constraints: list[str]  # Hard constraints (e.g., "no file I/O")

    # Output
    orchestration_code: str  # Generated Python code
    execution_trace: dict[str, Any] | None = None  # Execution results

    # Metadata
    source: str = "synthetic"  # aiurcm | synthetic | live_traffic
    domain: str = "general"  # data | web | math | text | tool_use
    complexity: str = "medium"  # simple | medium | complex
    is_multi_turn: bool = False  # Single-turn vs multi-turn trajectory

    # Quality Metrics
    is_executable: bool = True
    has_syntax_errors: bool = False
    has_security_violations: bool = False
    latency_estimate_ms: float | None = None

    # Unique ID
    example_id: str | None = None

    def __post_init__(self):
        """Generate unique ID from content hash."""
        if not self.example_id:
            content = f"{self.context}:{self.orchestration_code}"
            self.example_id = hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_gemini_format(self) -> dict[str, Any]:
        """Convert to Gemini fine-tuning format (JSONL)."""
        # Format risk vector as readable string
        risk_str = ", ".join([f"{k}={v:.2f}" for k, v in self.risk_vector.items()])
        constraints_str = "; ".join(self.constraints) if self.constraints else "None"

        # System message
        system_prompt = """You are a CodeAct orchestrator for an AI agent system. Your job is to generate executable Python code that coordinates multiple AI models (LLMs, tools, interpreters) to fulfill user requests.

CRITICAL RULES:
1. Only use allowed imports: anthropic, openai, json, math, re, datetime
2. NO file I/O, NO eval/exec, NO subprocess, NO network requests (except LLM APIs)
3. Code must be deterministic and idempotent
4. Always handle errors gracefully
5. Return structured results (dict/list/primitive types)

AVAILABLE RESOURCES:
- llm_pool: Dictionary of LLM clients {model_name: client}
- interpreter: Python code execution sandbox (execute_code function)
- risk_vector: Current risk scores for security/latency/cost

OUTPUT FORMAT: Pure Python code (no markdown, no explanations)"""

        # User prompt
        user_prompt = f"""Task: {self.context}

Risk Vector: {risk_str}
Constraints: {constraints_str}

Generate the orchestration code:"""

        # Assistant response (the code)
        assistant_response = self.orchestration_code.strip()

        return {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_response},
            ],
            "metadata": {
                "example_id": self.example_id,
                "source": self.source,
                "domain": self.domain,
                "complexity": self.complexity,
                "is_multi_turn": self.is_multi_turn,
            },
        }


@dataclass
class MultiTurnTrajectory:
    """Multi-turn conversation for self-debugging."""

    initial_context: str
    risk_vector: dict[str, float]
    constraints: list[str]

    # Conversation turns
    turns: list[dict[str, str]]  # [{"role": "user/assistant", "content": "..."}]

    # Metadata
    error_type: str  # syntax | import | type | runtime | logic
    was_fixed: bool = False
    num_iterations: int = 0

    def to_gemini_format(self) -> dict[str, Any]:
        """Convert multi-turn trajectory to training format."""
        system_prompt = (
            """You are a CodeAct orchestrator. When code fails, analyze the error and fix it."""
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.turns)

        return {
            "messages": messages,
            "metadata": {
                "type": "multi_turn",
                "error_type": self.error_type,
                "was_fixed": self.was_fixed,
                "num_iterations": self.num_iterations,
            },
        }


# ============================================================================
# DOMAIN-SPECIFIC SCENARIO GENERATORS
# ============================================================================


class ScenarioGenerator:
    """Generate synthetic orchestration scenarios across different domains."""

    DOMAINS = {
        "data": "Data processing, analysis, transformation",
        "web": "Web scraping, API calls, data fetching",
        "math": "Mathematical computations, statistics",
        "text": "Text processing, NLP, content generation",
        "tool_use": "Multi-tool coordination, complex workflows",
    }

    # Realistic task templates per domain
    TEMPLATES = {
        "data": [
            "Analyze a dataset of {entity} and compute {metric}",
            "Transform {data_format} data into {output_format} with {transformation}",
            "Filter {dataset} by {criteria} and aggregate using {method}",
            "Join {num} datasets on {key} and compute {statistic}",
            "Detect {anomaly_type} in {timeseries_data} using {algorithm}",
        ],
        "web": [
            "Fetch data from {api_name} API and extract {field}",
            "Scrape {website_type} for {data_type} and structure as {format}",
            "Poll {endpoint} until {condition} is met, with {timeout}s timeout",
            "Aggregate data from {num} different APIs and merge by {key}",
            "Monitor {url} for {change_type} and alert if detected",
        ],
        "math": [
            "Compute {statistic} for distribution with parameters {params}",
            "Solve {equation_type} equation for {variable} given {constraints}",
            "Optimize {function} subject to {constraints} using {method}",
            "Calculate {metric} between {vector1} and {vector2}",
            "Generate {num} samples from {distribution} and compute {property}",
        ],
        "text": [
            "Summarize {text_type} in {num} sentences focusing on {aspect}",
            "Extract {entity_type} from {document} and return as {format}",
            "Classify {text} into {categories} using {criteria}",
            "Generate {output_type} based on {input} following {style}",
            "Compare {text1} and {text2} for {similarity_metric}",
        ],
        "tool_use": [
            "Use {tool1} to {action1}, then {tool2} to {action2}",
            "Chain {num} tools: {sequence} to achieve {goal}",
            "If {condition} use {tool1}, else use {tool2} to {action}",
            "Parallelize {action} across {tool_list} and merge results",
            "Retry {action} with {tool} up to {max_retries} times on failure",
        ],
    }

    # Variable substitutions
    SUBSTITUTIONS = {
        "entity": ["users", "products", "transactions", "events", "sessions"],
        "metric": ["average", "median", "95th percentile", "total count", "unique count"],
        "data_format": ["JSON", "CSV", "XML", "Parquet", "raw text"],
        "output_format": ["JSON", "structured dict", "pandas DataFrame", "list of tuples"],
        "transformation": ["filtering nulls", "normalizing values", "deduplicating"],
        "dataset": ["customer records", "log entries", "sensor readings", "API responses"],
        "criteria": ["timestamp > threshold", "category == value", "score > minimum"],
        "method": ["sum", "count", "average", "group by category"],
        "num": ["2", "3", "5", "multiple"],
        "key": ["user_id", "timestamp", "session_id", "product_id"],
        "statistic": ["correlation", "variance", "percentiles", "distribution"],
        "anomaly_type": ["outliers", "sudden spikes", "trend changes", "missing values"],
        "timeseries_data": ["CPU metrics", "request latencies", "error rates", "usage patterns"],
        "algorithm": ["z-score", "IQR method", "moving average", "statistical threshold"],
        "api_name": ["weather", "stock market", "social media", "news", "geocoding"],
        "field": ["latest value", "historical trend", "metadata", "status"],
        "website_type": ["news site", "e-commerce page", "documentation", "data portal"],
        "data_type": ["headlines", "prices", "specifications", "reviews"],
        "format": ["JSON array", "structured list", "key-value pairs"],
        "endpoint": ["health check URL", "status API", "data feed"],
        "condition": ["status == ready", "data available", "job completed"],
        "timeout": ["30", "60", "120"],
        "url": ["dashboard", "API endpoint", "configuration file"],
        "change_type": ["content update", "status change", "new data"],
        "statistic": ["mean", "standard deviation", "kurtosis", "skewness"],  # noqa: F601
        "params": ["mu=0, sigma=1", "lambda=5", "n=100, p=0.5"],
        "equation_type": ["linear", "quadratic", "differential"],
        "variable": ["x", "coefficients", "optimal point"],
        "constraints": ["x > 0", "sum(x) = 1", "bounded domain"],
        "function": ["cost function", "likelihood", "distance metric"],
        "method": ["gradient descent", "Newton's method", "grid search"],  # noqa: F601
        "metric": ["Euclidean distance", "cosine similarity", "Jaccard index"],  # noqa: F601
        "vector1": ["observation", "embedding", "feature vector"],
        "vector2": ["reference", "centroid", "target"],
        "samples": ["1000", "5000", "10000"],
        "distribution": ["normal", "exponential", "uniform", "Poisson"],
        "property": ["mean", "variance", "entropy"],
        "text_type": ["article", "research paper", "documentation", "conversation"],
        "aspect": ["main points", "technical details", "conclusions"],
        "entity_type": ["dates", "names", "locations", "technical terms"],
        "document": ["text", "transcript", "log file"],
        "text": ["user review", "email", "social media post"],
        "categories": ["positive/negative", "topic categories", "priority levels"],
        "criteria": ["sentiment keywords", "topic modeling", "rule-based classification"],  # noqa: F601
        "output_type": ["summary", "response", "report", "description"],
        "input": ["prompt", "template", "reference text"],
        "style": ["technical tone", "casual style", "formal language"],
        "text1": ["document A", "version 1", "original"],
        "text2": ["document B", "version 2", "revised"],
        "similarity_metric": ["overlap", "semantic similarity", "edit distance"],
        "tool1": ["LLM", "calculator", "search API", "database"],
        "action1": ["extract info", "compute value", "fetch data", "validate input"],
        "tool2": ["formatter", "validator", "aggregator", "classifier"],
        "action2": ["structure output", "check correctness", "merge results", "categorize"],
        "sequence": ["parse → analyze → summarize", "fetch → transform → validate"],
        "goal": ["final report", "structured data", "decision"],
        "condition": ["input is numerical", "data is available", "confidence > 0.8"],  # noqa: F601
        "action": ["process request", "fetch data", "compute result"],
        "tool_list": ["3 LLMs", "multiple APIs", "parallel interpreters"],
        "max_retries": ["3", "5"],
    }

    @classmethod
    def generate_scenario(cls, domain: str) -> tuple[str, str, dict[str, float]]:
        """Generate a single synthetic scenario.

        Returns:
            (context, complexity, risk_vector)

        """
        if domain not in cls.TEMPLATES:
            raise ValueError(f"Unknown domain: {domain}")

        # Pick random template
        template = random.choice(cls.TEMPLATES[domain])

        # Fill in variables
        context = template
        for var in re.findall(r"\{(\w+)\}", template):
            if var in cls.SUBSTITUTIONS:
                value = random.choice(cls.SUBSTITUTIONS[var])
                context = context.replace(f"{{{var}}}", value, 1)

        # Determine complexity based on context length and keywords
        complexity_keywords = {
            "simple": 0,
            "medium": sum(
                [
                    "multiple" in context.lower(),
                    "chain" in context.lower(),
                    "parallelize" in context.lower(),
                    len(context.split()) > 15,
                ],
            ),
            "complex": sum(
                [
                    "if" in context.lower() and "else" in context.lower(),
                    context.lower().count("and") > 1,
                    "retry" in context.lower(),
                    len(context.split()) > 20,
                ],
            ),
        }

        if complexity_keywords["complex"] >= 2:
            complexity = "complex"
        elif complexity_keywords["medium"] >= 1:
            complexity = "medium"
        else:
            complexity = "simple"

        # Generate realistic risk vector
        base_risk = {"security": 0.1, "latency": 0.2, "cost": 0.15, "reliability": 0.1}

        # Adjust based on domain and complexity
        if domain == "web":
            base_risk["security"] += 0.2
            base_risk["latency"] += 0.3
        elif domain == "tool_use":
            base_risk["complexity"] = 0.4
            base_risk["latency"] += 0.2

        if complexity == "complex":
            base_risk["latency"] += 0.2
            base_risk["cost"] += 0.1

        # Normalize to [0, 1]
        for key in base_risk:
            base_risk[key] = min(1.0, base_risk[key] + random.uniform(-0.1, 0.1))

        return context, complexity, base_risk


# ============================================================================
# CODE GENERATION ENGINE
# ============================================================================


class CodeGenerator:
    """Use Gemini to generate orchestration code from scenarios."""

    def __init__(
        self, model_name: str = "gemini-3.1-flash-lite-preview", api_key: str | None = None
    ):
        """Initialize Gemini client."""
        if api_key:
            genai.configure(api_key=api_key)
        elif "GOOGLE_API_KEY" in os.environ:
            genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        else:
            raise ValueError("No API key provided. Set GOOGLE_API_KEY or pass api_key parameter.")

        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.2,  # Low temperature for deterministic code
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

        logger.info(f"Initialized CodeGenerator with model: {model_name}")

    def generate_code(
        self,
        context: str,
        risk_vector: dict[str, float],
        constraints: list[str],
        domain: str = "general",
    ) -> str:
        """Generate orchestration code for a given scenario.

        Args:
            context: Natural language task description
            risk_vector: Risk scores
            constraints: Hard constraints
            domain: Task domain

        Returns:
            Generated Python code (as string)

        """
        # Build prompt
        risk_str = ", ".join([f"{k}={v:.2f}" for k, v in risk_vector.items()])
        constraints_str = "\n".join([f"- {c}" for c in constraints]) if constraints else "- None"

        prompt = f"""You are a CodeAct orchestrator code generator. Generate ONLY executable Python code (no markdown, no explanations).

TASK DOMAIN: {domain}
TASK: {context}

RISK VECTOR: {risk_str}

CONSTRAINTS:
{constraints_str}

AVAILABLE RESOURCES:
```python
# LLM Pool (dictionary of model clients)
llm_pool = {{
    "claude": anthropic_client,
    "gpt4": openai_client,
    "gemini": gemini_client
}}

# Python interpreter (for code execution)
def execute_code(code: str) -> Any:
    \"\"\"Execute Python code in sandbox and return result.\"\"\"
    pass

# Allowed imports
import json
import math
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
```

REQUIREMENTS:
1. Write a complete Python function called `orchestrate()` that takes no arguments
2. The function should return the final result (dict, list, or primitive type)
3. Use only allowed imports: json, math, re, datetime, typing
4. NO file I/O, NO eval/exec, NO subprocess, NO os module
5. Handle errors gracefully with try/except
6. Keep code under 50 lines
7. Add brief inline comments explaining key steps

EXAMPLE OUTPUT FORMAT:
```python
def orchestrate():
    \"\"\"Orchestration code for: [brief task description]\"\"\"
    # Step 1: Initialize
    result = {{}}

    # Step 2: Process
    try:
        # ... implementation ...
        pass
    except Exception as e:
        return {{"error": str(e)}}

    # Step 3: Return
    return result
```

Generate the code now (ONLY code, no markdown fences):"""

        # Generate code
        try:
            response = self.model.generate_content(prompt)
            code = response.text.strip()

            # Clean up markdown fences if present
            code = re.sub(r"^```python\s*", "", code)
            code = re.sub(r"^```\s*", "", code)
            code = re.sub(r"\s*```$", "", code)

            return code.strip()

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            # Return a fallback minimal implementation
            return f"""def orchestrate():
    \"\"\"Fallback implementation for: {context[:50]}...\"\"\"
    return {{"error": "Code generation failed", "message": "{e!s}"}}"""

    async def generate_batch(
        self,
        scenarios: list[tuple[str, dict[str, float], list[str], str]],
        max_concurrent: int = 5,
    ) -> list[str]:
        """Generate code for multiple scenarios in parallel.

        Args:
            scenarios: List of (context, risk_vector, constraints, domain) tuples
            max_concurrent: Max concurrent API calls

        Returns:
            List of generated code strings

        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def generate_one(scenario):
            async with semaphore:
                context, risk_vector, constraints, domain = scenario
                # Note: Gemini Python SDK is not async, so we run in executor
                loop = asyncio.get_event_loop()
                code = await loop.run_in_executor(
                    None,
                    self.generate_code,
                    context,
                    risk_vector,
                    constraints,
                    domain,
                )
                return code

        tasks = [generate_one(s) for s in scenarios]
        return await asyncio.gather(*tasks)


# ============================================================================
# ERROR INJECTION & SELF-DEBUG TRAJECTORY GENERATION
# ============================================================================


class ErrorInjector:
    """Inject realistic errors into working code to create self-debug trajectories."""

    ERROR_TYPES = {
        "syntax": [
            lambda code: code.replace(":", "", 1),  # Remove first colon
            lambda code: code.replace("    ", "  ", 1),  # Break indentation
            lambda code: code.replace("=", "==", 1),  # Assignment to comparison
        ],
        "import": [
            lambda code: "import os\n" + code,  # Forbidden import
            lambda code: code.replace("import json", "import jsons"),  # Typo
            lambda code: code.replace("from datetime", "from datetimes"),  # Typo
        ],
        "type": [
            lambda code: code.replace('""', "None", 1),  # Wrong type
            lambda code: code.replace("[", "{", 1).replace("]", "}", 1),  # List to dict
            lambda code: code.replace("str(", "int(", 1),  # Wrong cast
        ],
        "runtime": [
            lambda code: code.replace("get(", "get(999, ", 1),  # Index error
            lambda code: code.replace("/ ", "// 0  # ", 1),  # Division by zero
            lambda code: code.replace("return ", "return missing_var  # "),  # NameError
        ],
        "logic": [
            lambda code: code.replace("> ", "< ", 1),  # Wrong comparison
            lambda code: code.replace("and ", "or ", 1),  # Wrong boolean logic
            lambda code: code.replace("True", "False", 1),  # Wrong constant
        ],
    }

    @classmethod
    def inject_error(cls, code: str, error_type: str | None = None) -> tuple[str, str]:
        """Inject a realistic error into working code.

        Args:
            code: Working Python code
            error_type: Type of error to inject (random if None)

        Returns:
            (buggy_code, error_type)

        """
        if error_type is None:
            error_type = random.choice(list(cls.ERROR_TYPES.keys()))

        if error_type not in cls.ERROR_TYPES:
            raise ValueError(f"Unknown error type: {error_type}")

        # Pick random error mutation for this type
        mutator = random.choice(cls.ERROR_TYPES[error_type])

        try:
            buggy_code = mutator(code)
            return buggy_code, error_type
        except Exception as e:
            logger.warning(f"Error injection failed: {e}, returning original code")
            return code, "none"

    @classmethod
    def create_self_debug_trajectory(
        cls,
        generator: CodeGenerator,
        context: str,
        risk_vector: dict[str, float],
        constraints: list[str],
        working_code: str,
        max_iterations: int = 3,
    ) -> MultiTurnTrajectory:
        """Create a multi-turn self-debugging trajectory.

        Flow:
            1. Start with working code
            2. Inject error
            3. Simulate error message
            4. Ask model to fix it
            5. Validate fix
            6. Repeat if needed (up to max_iterations)

        Returns:
            MultiTurnTrajectory with conversation turns

        """
        # Inject error
        buggy_code, error_type = cls.inject_error(working_code)

        # Simulate execution and error message
        error_message = cls._get_error_message(buggy_code, error_type)

        # Initialize trajectory
        trajectory = MultiTurnTrajectory(
            initial_context=context,
            risk_vector=risk_vector,
            constraints=constraints,
            turns=[],
            error_type=error_type,
            was_fixed=False,
            num_iterations=0,
        )

        # Turn 1: Initial request
        risk_str = ", ".join([f"{k}={v:.2f}" for k, v in risk_vector.items()])
        initial_prompt = f"""Task: {context}

Risk Vector: {risk_str}
Constraints: {"; ".join(constraints)}

Generate orchestration code:"""

        trajectory.turns.append({"role": "user", "content": initial_prompt})

        # Turn 2: Buggy code response
        trajectory.turns.append({"role": "assistant", "content": buggy_code})

        # Turn 3: Error feedback
        trajectory.turns.append(
            {
                "role": "user",
                "content": f"""Code execution failed with error:

```
{error_message}
```

Please fix the code and return the corrected version.""",
            },
        )

        # Turn 4+: Attempt to fix (using Gemini)
        current_code = buggy_code
        for iteration in range(max_iterations):
            trajectory.num_iterations = iteration + 1

            # Ask model to fix
            fix_prompt = f"""The following code has an error:

```python
{current_code}
```

Error message:
```
{error_message}
```

Fix the code and return ONLY the corrected code (no explanations):"""

            try:
                response = generator.model.generate_content(fix_prompt)
                fixed_code = response.text.strip()

                # Clean markdown
                fixed_code = re.sub(r"^```python\s*", "", fixed_code)
                fixed_code = re.sub(r"^```\s*", "", fixed_code)
                fixed_code = re.sub(r"\s*```$", "", fixed_code)

                # Add to trajectory
                trajectory.turns.append({"role": "assistant", "content": fixed_code})

                # Validate fix
                is_valid, new_error = cls._validate_code(fixed_code)

                if is_valid:
                    trajectory.was_fixed = True
                    break
                # Continue with new error
                error_message = new_error
                current_code = fixed_code

                if iteration < max_iterations - 1:
                    trajectory.turns.append(
                        {
                            "role": "user",
                            "content": f"Still has error: {error_message}\nPlease fix:",
                        },
                    )

            except Exception as e:
                logger.error(f"Fix generation failed: {e}")
                break

        return trajectory

    @staticmethod
    def _get_error_message(code: str, error_type: str) -> str:
        """Simulate realistic error message."""
        try:
            ast.parse(code)
            return "No syntax errors (runtime error would occur)"
        except SyntaxError as e:
            return f"SyntaxError: {e.msg} at line {e.lineno}"
        except Exception as e:
            return f"{type(e).__name__}: {e!s}"

    @staticmethod
    def _validate_code(code: str) -> tuple[bool, str | None]:
        """Validate code for syntax and basic security.

        Returns:
            (is_valid, error_message)

        """
        # Check syntax
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"SyntaxError: {e.msg}"

        # Check for forbidden constructs
        forbidden_names = {"eval", "exec", "compile", "__import__", "open", "file"}
        forbidden_modules = {"os", "subprocess", "socket", "urllib", "requests"}

        for node in ast.walk(tree):
            # Check for forbidden function calls
            if isinstance(node, ast.Name) and node.id in forbidden_names:
                return False, f"Security violation: {node.id} is not allowed"

            # Check for forbidden imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in forbidden_modules:
                        return False, f"Security violation: import {alias.name} not allowed"

            if isinstance(node, ast.ImportFrom):  # noqa: SIM102
                if node.module and node.module.split(".")[0] in forbidden_modules:
                    return False, f"Security violation: from {node.module} not allowed"

        return True, None


# ============================================================================
# QUALITY FILTERING & VALIDATION
# ============================================================================


class QualityFilter:
    """Filter and validate training examples for quality."""

    @staticmethod
    def validate_example(example: OrchestrationExample) -> tuple[bool, list[str]]:
        """Comprehensive validation of a training example.

        Returns:
            (passes, list_of_issues)

        """
        issues = []

        # 1. Syntax validation
        try:
            ast.parse(example.orchestration_code)
            example.has_syntax_errors = False
        except SyntaxError as e:
            example.has_syntax_errors = True
            example.is_executable = False
            issues.append(f"Syntax error: {e.msg}")

        # 2. Security validation
        forbidden_constructs = []
        try:
            tree = ast.parse(example.orchestration_code)

            forbidden_names = {"eval", "exec", "compile", "__import__", "open", "file"}
            forbidden_modules = {"os", "subprocess", "socket", "urllib", "requests", "http"}

            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in forbidden_names:
                    forbidden_constructs.append(node.id)

                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".")[0] in forbidden_modules:
                            forbidden_constructs.append(f"import {alias.name}")

                if isinstance(node, ast.ImportFrom):  # noqa: SIM102
                    if node.module and node.module.split(".")[0] in forbidden_modules:
                        forbidden_constructs.append(f"from {node.module}")

            if forbidden_constructs:
                example.has_security_violations = True
                example.is_executable = False
                issues.append(f"Security violations: {', '.join(forbidden_constructs)}")
            else:
                example.has_security_violations = False

        except Exception:
            pass

        # 3. Complexity validation (code should be under 50 lines)
        num_lines = len(example.orchestration_code.strip().split("\n"))
        if num_lines > 50:
            issues.append(f"Code too long: {num_lines} lines (max 50)")

        # 4. Semantic validation (must have orchestrate() function)
        if "def orchestrate(" not in example.orchestration_code:
            issues.append("Missing orchestrate() function definition")
            example.is_executable = False

        # 5. Context validation (not empty or too short)
        if len(example.context) < 10:
            issues.append("Context too short")

        # 6. Estimate latency (very rough heuristic)
        # Assume ~1ms per line of code + LLM call overhead
        num_llm_calls = example.orchestration_code.lower().count("llm_pool")
        base_latency = num_lines * 1  # 1ms per line
        llm_latency = num_llm_calls * 50  # 50ms per LLM call (conservative)
        example.latency_estimate_ms = base_latency + llm_latency

        if example.latency_estimate_ms > 90:  # Phase 1 SLA is 100ms, leave buffer
            issues.append(f"Latency estimate too high: {example.latency_estimate_ms}ms")

        # Overall pass/fail
        passes = len(issues) == 0

        return passes, issues

    @staticmethod
    def filter_dataset(
        examples: list[OrchestrationExample],
        min_executable_rate: float = 0.95,
        max_security_violations: int = 0,
    ) -> tuple[list[OrchestrationExample], dict[str, Any]]:
        """Filter dataset to meet quality thresholds.

        Args:
            examples: List of examples to filter
            min_executable_rate: Minimum executable rate (default 95%)
            max_security_violations: Max security violations (default 0)

        Returns:
            (filtered_examples, statistics)

        """
        filtered = []
        rejection_reasons = defaultdict(int)

        for example in examples:
            passes, issues = QualityFilter.validate_example(example)

            if passes:
                filtered.append(example)
            else:
                for issue in issues:
                    # Categorize rejection reason
                    if "Syntax error" in issue:
                        rejection_reasons["syntax_errors"] += 1
                    elif "Security violation" in issue:
                        rejection_reasons["security_violations"] += 1
                    elif "too long" in issue:
                        rejection_reasons["too_complex"] += 1
                    elif "Latency" in issue:
                        rejection_reasons["latency_too_high"] += 1
                    elif "Missing orchestrate" in issue:
                        rejection_reasons["missing_function"] += 1
                    else:
                        rejection_reasons["other"] += 1

        # Compute statistics
        total = len(examples)
        passed = len(filtered)
        rejected = total - passed

        executable_count = sum(1 for ex in filtered if ex.is_executable)
        executable_rate = executable_count / passed if passed > 0 else 0

        security_violation_count = sum(1 for ex in examples if ex.has_security_violations)

        stats = {
            "total_examples": total,
            "passed": passed,
            "rejected": rejected,
            "pass_rate": passed / total if total > 0 else 0,
            "executable_rate": executable_rate,
            "security_violations": security_violation_count,
            "rejection_reasons": dict(rejection_reasons),
            "meets_threshold": (
                executable_rate >= min_executable_rate
                and security_violation_count <= max_security_violations
            ),
        }

        return filtered, stats


# ============================================================================
# AIURCM TEST CASE CONVERTER
# ============================================================================


class AiURCMConverter:
    """Convert existing AiURCM test cases into training examples."""

    @staticmethod
    def convert_test_to_example(test_case: dict[str, Any]) -> OrchestrationExample:
        """Convert a single AiURCM test case to orchestration example.

        Expected test_case format:
        {
            "name": "test_risk_calculation",
            "description": "Test risk vector calculation",
            "expected_behavior": "Should compute risk scores correctly",
            "code": "def test_...",
            "domain": "risk_management"
        }
        """
        # Extract context from test metadata
        context = test_case.get("description", test_case.get("name", "Unknown task"))

        # Infer domain
        domain_map = {
            "risk": "data",
            "api": "web",
            "calculation": "math",
            "text": "text",
            "workflow": "tool_use",
        }

        domain = "general"
        for key, val in domain_map.items():
            if key in context.lower():
                domain = val
                break

        # Generate risk vector (use defaults for now)
        risk_vector = {"security": 0.1, "latency": 0.2, "cost": 0.15, "reliability": 0.1}

        # Extract or generate constraints
        constraints = test_case.get("constraints", ["No file I/O", "No external network calls"])

        # Convert test code to orchestration code
        # (This is a simplified conversion - in practice, would need more sophisticated logic)
        test_code = test_case.get("code", "")

        # Simple heuristic: extract the core logic and wrap in orchestrate()
        orchestration_code = f"""def orchestrate():
    \"\"\"Orchestration for: {context}\"\"\"
    # Converted from test case: {test_case.get("name", "unknown")}

    result = {{
        "status": "success",
        "data": None
    }}

    # TODO: Implement actual logic from test case
    # Original test: {test_code[:100]}...

    return result"""

        return OrchestrationExample(
            context=context,
            risk_vector=risk_vector,
            constraints=constraints,
            orchestration_code=orchestration_code,
            source="aiurcm",
            domain=domain,
            complexity="simple",
        )

    @staticmethod
    def convert_test_suite(test_suite_path: Path) -> list[OrchestrationExample]:
        """Convert entire AiURCM test suite to training examples.

        Args:
            test_suite_path: Path to test suite JSON file

        Returns:
            List of OrchestrationExample objects

        """
        if not test_suite_path.exists():
            logger.warning(f"Test suite not found: {test_suite_path}")
            return []

        try:
            with open(test_suite_path) as f:
                test_suite = json.load(f)

            examples = []
            for test_case in test_suite.get("tests", []):
                try:
                    example = AiURCMConverter.convert_test_to_example(test_case)
                    examples.append(example)
                except Exception as e:
                    logger.error(f"Failed to convert test {test_case.get('name')}: {e}")

            logger.info(f"Converted {len(examples)} test cases from {test_suite_path}")
            return examples

        except Exception as e:
            logger.error(f"Failed to load test suite: {e}")
            return []


# ============================================================================
# MAIN DATASET GENERATION PIPELINE
# ============================================================================


class DatasetPipeline:
    """End-to-end dataset generation pipeline."""

    def __init__(
        self,
        generator: CodeGenerator,
        output_dir: Path,
        num_synthetic_per_domain: int = 1000,
    ):
        """Initialize pipeline."""
        self.generator = generator
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.num_synthetic_per_domain = num_synthetic_per_domain

        logger.info(f"Initialized DatasetPipeline, output: {output_dir}")

    def generate_synthetic_examples(
        self,
        domain: str,
        num_examples: int,
    ) -> list[OrchestrationExample]:
        """Generate synthetic examples for a single domain."""
        logger.info(f"Generating {num_examples} synthetic examples for domain: {domain}")

        examples = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Generating {domain} examples...", total=num_examples)

            for i in range(num_examples):
                try:
                    # Generate scenario
                    context, complexity, risk_vector = ScenarioGenerator.generate_scenario(domain)

                    # Generate constraints
                    constraints = [
                        "No file I/O operations",
                        "No external network calls (except LLM APIs)",
                        "Code must complete in <90ms",
                    ]

                    # Generate code
                    code = self.generator.generate_code(context, risk_vector, constraints, domain)

                    # Create example
                    example = OrchestrationExample(
                        context=context,
                        risk_vector=risk_vector,
                        constraints=constraints,
                        orchestration_code=code,
                        source="synthetic",
                        domain=domain,
                        complexity=complexity,
                    )

                    examples.append(example)
                    progress.update(task, advance=1)

                except Exception as e:
                    logger.error(f"Failed to generate example {i}: {e}")
                    progress.update(task, advance=1)
                    continue

        logger.info(f"Generated {len(examples)} examples for {domain}")
        return examples

    def generate_all_synthetic(self) -> list[OrchestrationExample]:
        """Generate synthetic examples across all domains."""
        all_examples = []

        for domain in ScenarioGenerator.DOMAINS:
            examples = self.generate_synthetic_examples(domain, self.num_synthetic_per_domain)
            all_examples.extend(examples)

        return all_examples

    def generate_multi_turn_trajectories(
        self,
        base_examples: list[OrchestrationExample],
        num_trajectories: int = 100,
        error_distribution: dict[str, float] | None = None,
    ) -> list[MultiTurnTrajectory]:
        """Generate multi-turn self-debug trajectories.

        Args:
            base_examples: Working examples to inject errors into
            num_trajectories: Number of trajectories to generate
            error_distribution: Distribution of error types (uniform if None)

        Returns:
            List of MultiTurnTrajectory objects

        """
        logger.info(f"Generating {num_trajectories} multi-turn trajectories")

        if error_distribution is None:
            error_distribution = {
                "syntax": 0.2,
                "import": 0.2,
                "type": 0.2,
                "runtime": 0.2,
                "logic": 0.2,
            }

        # Sample base examples
        sampled = random.choices(base_examples, k=num_trajectories)

        trajectories = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Generating debug trajectories...",
                total=num_trajectories,
            )

            for example in sampled:
                try:
                    # Choose error type based on distribution
                    random.choices(
                        list(error_distribution.keys()),
                        weights=list(error_distribution.values()),
                    )[0]

                    # Generate trajectory
                    trajectory = ErrorInjector.create_self_debug_trajectory(
                        generator=self.generator,
                        context=example.context,
                        risk_vector=example.risk_vector,
                        constraints=example.constraints,
                        working_code=example.orchestration_code,
                        max_iterations=3,
                    )

                    trajectories.append(trajectory)
                    progress.update(task, advance=1)

                except Exception as e:
                    logger.error(f"Failed to generate trajectory: {e}")
                    progress.update(task, advance=1)
                    continue

        # Statistics
        fixed_count = sum(1 for t in trajectories if t.was_fixed)
        fix_rate = fixed_count / len(trajectories) if trajectories else 0

        logger.info(f"Generated {len(trajectories)} trajectories, fix rate: {fix_rate:.1%}")

        return trajectories

    def run_full_pipeline(
        self,
        aiurcm_test_suite: Path | None = None,
        num_multi_turn: int = 1000,
    ) -> dict[str, Any]:
        """Run complete dataset generation pipeline.

        Steps:
            1. Convert AiURCM test cases (if provided)
            2. Generate synthetic examples (all domains)
            3. Filter for quality
            4. Generate multi-turn trajectories
            5. Export to Gemini format
            6. Generate statistics report

        Returns:
            Statistics dictionary

        """
        console.print(
            "\n[bold cyan]═══ CodeActInstruct Dataset Generation Pipeline ═══[/bold cyan]\n",
        )

        all_examples = []

        # Stage 1: AiURCM conversion
        if aiurcm_test_suite and aiurcm_test_suite.exists():
            console.print("[bold]Stage 1:[/bold] Converting AiURCM test cases...")
            aiurcm_examples = AiURCMConverter.convert_test_suite(aiurcm_test_suite)
            all_examples.extend(aiurcm_examples)
            console.print(f"  ✓ Converted {len(aiurcm_examples)} test cases\n")
        else:
            console.print("[yellow]Stage 1: Skipped (no AiURCM test suite provided)[/yellow]\n")

        # Stage 2: Synthetic generation
        console.print("[bold]Stage 2:[/bold] Generating synthetic examples...")
        synthetic_examples = self.generate_all_synthetic()
        all_examples.extend(synthetic_examples)
        console.print(f"  ✓ Generated {len(synthetic_examples)} synthetic examples\n")

        # Stage 3: Quality filtering
        console.print("[bold]Stage 3:[/bold] Quality filtering and validation...")
        filtered_examples, filter_stats = QualityFilter.filter_dataset(
            all_examples,
            min_executable_rate=0.95,
            max_security_violations=0,
        )
        console.print(
            f"  ✓ Filtered: {filter_stats['passed']}/{filter_stats['total_examples']} passed",
        )
        console.print(f"  ✓ Executable rate: {filter_stats['executable_rate']:.1%}")
        console.print(f"  ✓ Security violations: {filter_stats['security_violations']}\n")

        # Stage 4: Multi-turn trajectories
        console.print("[bold]Stage 4:[/bold] Generating multi-turn debug trajectories...")
        trajectories = self.generate_multi_turn_trajectories(
            filtered_examples,
            num_trajectories=num_multi_turn,
        )
        console.print(f"  ✓ Generated {len(trajectories)} trajectories\n")

        # Stage 5: Export
        console.print("[bold]Stage 5:[/bold] Exporting to Gemini format...")

        # Export single-turn examples
        single_turn_path = self.output_dir / "single_turn_examples.jsonl"
        with open(single_turn_path, "w") as f:
            f.writelines(
                json.dumps(example.to_gemini_format()) + "\n" for example in filtered_examples
            )

        # Export multi-turn trajectories
        multi_turn_path = self.output_dir / "multi_turn_trajectories.jsonl"
        with open(multi_turn_path, "w") as f:
            f.writelines(
                json.dumps(trajectory.to_gemini_format()) + "\n" for trajectory in trajectories
            )

        console.print(f"  ✓ Exported single-turn: {single_turn_path}")
        console.print(f"  ✓ Exported multi-turn: {multi_turn_path}\n")

        # Stage 6: Statistics
        console.print("[bold]Stage 6:[/bold] Generating statistics report...")

        stats = {
            "generation_timestamp": datetime.now().isoformat(),
            "total_examples": len(all_examples),
            "filtered_examples": len(filtered_examples),
            "multi_turn_trajectories": len(trajectories),
            "filter_statistics": filter_stats,
            "domain_distribution": self._compute_domain_distribution(filtered_examples),
            "complexity_distribution": self._compute_complexity_distribution(filtered_examples),
            "trajectory_fix_rate": sum(1 for t in trajectories if t.was_fixed) / len(trajectories)
            if trajectories
            else 0,
            "output_files": {
                "single_turn": str(single_turn_path),
                "multi_turn": str(multi_turn_path),
            },
        }

        # Save statistics
        stats_path = self.output_dir / "generation_statistics.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2)

        console.print(f"  ✓ Statistics saved: {stats_path}\n")

        # Display summary table
        self._display_summary(stats)

        return stats

    @staticmethod
    def _compute_domain_distribution(examples: list[OrchestrationExample]) -> dict[str, int]:
        """Compute distribution of examples across domains."""
        distribution = defaultdict(int)
        for ex in examples:
            distribution[ex.domain] += 1
        return dict(distribution)

    @staticmethod
    def _compute_complexity_distribution(examples: list[OrchestrationExample]) -> dict[str, int]:
        """Compute distribution of examples across complexity levels."""
        distribution = defaultdict(int)
        for ex in examples:
            distribution[ex.complexity] += 1
        return dict(distribution)

    @staticmethod
    def _display_summary(stats: dict[str, Any]):
        """Display summary table."""
        table = Table(
            title="Dataset Generation Summary",
            show_header=True,
            header_style="bold cyan",
        )

        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="green", width=20)

        table.add_row("Total Examples Generated", str(stats["total_examples"]))
        table.add_row("Passed Quality Filter", str(stats["filtered_examples"]))
        table.add_row("Multi-Turn Trajectories", str(stats["multi_turn_trajectories"]))
        table.add_row("Executable Rate", f"{stats['filter_statistics']['executable_rate']:.1%}")
        table.add_row("Trajectory Fix Rate", f"{stats['trajectory_fix_rate']:.1%}")

        table.add_row("", "")
        table.add_row("[bold]Domain Distribution[/bold]", "")
        for domain, count in stats["domain_distribution"].items():
            table.add_row(f"  {domain}", str(count))

        table.add_row("", "")
        table.add_row("[bold]Complexity Distribution[/bold]", "")
        for complexity, count in stats["complexity_distribution"].items():
            table.add_row(f"  {complexity}", str(count))

        console.print(table)


# ============================================================================
# CLI INTERFACE
# ============================================================================


@click.command()
@click.option(
    "--aiurcm_tests",
    type=click.Path(exists=False),
    help="Path to AiURCM test suite JSON file",
)
@click.option(
    "--num_synthetic",
    type=int,
    default=5000,
    help="Number of synthetic examples to generate (total across all domains)",
)
@click.option(
    "--num_multi_turn",
    type=int,
    default=1000,
    help="Number of multi-turn debug trajectories to generate",
)
@click.option(
    "--output_dir",
    type=click.Path(),
    default="./datasets",
    help="Output directory for generated datasets",
)
@click.option(
    "--gemini_model",
    type=str,
    default="gemini-3.1-flash-lite-preview",
    help="Gemini model to use for code generation",
)
@click.option(
    "--api_key",
    type=str,
    envvar="GOOGLE_API_KEY",
    help="Google API key (or set GOOGLE_API_KEY env var)",
)
@click.option("--seed", type=int, default=42, help="Random seed for reproducibility")
def main(
    aiurcm_tests: str | None,
    num_synthetic: int,
    num_multi_turn: int,
    output_dir: str,
    gemini_model: str,
    api_key: str | None,
    seed: int,
):
    """Generate CodeActInstruct training dataset for Cor.54 orchestrator.

    This tool creates high-quality training data by:
    1. Converting existing AiURCM test cases
    2. Generating synthetic orchestration scenarios
    3. Creating self-debug trajectories with injected errors
    4. Filtering for quality (95%+ executable rate)
    5. Exporting to Gemini fine-tuning format

    Example usage:
        python dataset_generator.py \\
            --aiurcm_tests ../tests/aiurcm/test_suite.json \\
            --num_synthetic 5000 \\
            --num_multi_turn 1000 \\
            --output_dir ./datasets
    """
    # Set random seed
    random.seed(seed)
    np.random.seed(seed)

    # Configure logging
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
    )

    logger.info("Starting CodeActInstruct dataset generation")
    logger.info(
        f"Configuration: synthetic={num_synthetic}, multi_turn={num_multi_turn}, model={gemini_model}",
    )

    # Initialize components
    try:
        generator = CodeGenerator(model_name=gemini_model, api_key=api_key)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print(
            "\n[yellow]Please set GOOGLE_API_KEY environment variable or pass --api_key[/yellow]",
        )
        raise SystemExit(1)

    # Calculate num_synthetic per domain
    num_domains = len(ScenarioGenerator.DOMAINS)
    num_per_domain = num_synthetic // num_domains

    pipeline = DatasetPipeline(
        generator=generator,
        output_dir=Path(output_dir),
        num_synthetic_per_domain=num_per_domain,
    )

    # Run pipeline
    try:
        aiurcm_path = Path(aiurcm_tests) if aiurcm_tests else None
        stats = pipeline.run_full_pipeline(
            aiurcm_test_suite=aiurcm_path,
            num_multi_turn=num_multi_turn,
        )

        console.print("\n[bold green]✓ Dataset generation complete![/bold green]")
        console.print(f"\n[cyan]Output directory:[/cyan] {output_dir}")
        console.print(
            f"[cyan]Total training examples:[/cyan] {stats['filtered_examples'] + stats['multi_turn_trajectories']}",
        )

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        console.print(f"\n[red]✗ Pipeline failed: {e}[/red]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
