"""Code Refactorer Agent

Refactoring specialist who improves code quality.
Cleans up that code you wrote at 3am. Makes it readable, fast, and maintainable.

Key Features:
- Code cleanup
- Readability improvement
- Performance optimization
- Maintainability enhancement
- Best practices application
- Technical debt reduction
"""

import re
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query, tool


class Severity(StrEnum):
    """Issue severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Aggressiveness(StrEnum):
    """Refactoring aggressiveness levels"""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class FocusArea(StrEnum):
    """Refactoring focus areas"""

    READABILITY = "readability"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    BEST_PRACTICES = "best-practices"
    TECHNICAL_DEBT = "technical-debt"


@dataclass
class CodeIssue:
    """Represents a code quality issue"""

    type: str
    severity: Severity
    description: str
    location: str | None = None
    suggestion: str | None = None


@dataclass
class CodeMetrics:
    """Code quality metrics"""

    complexity: int | None = None
    maintainability_index: int | None = None
    technical_debt: str | None = None


@dataclass
class CodeAnalysis:
    """Analysis result from code inspection"""

    issues: list[CodeIssue] = field(default_factory=list)
    metrics: CodeMetrics = field(default_factory=CodeMetrics)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class RefactorChange:
    """Represents a single refactoring change"""

    type: str
    description: str
    before: str | None = None
    after: str | None = None
    reasoning: str | None = None


@dataclass
class RefactorResult:
    """Result of a refactoring operation"""

    refactored_code: str
    changes: list[RefactorChange]
    analysis: CodeAnalysis
    summary: str


@dataclass
class RefactorConfig:
    """Configuration options for refactoring"""

    focus: list[FocusArea] = field(
        default_factory=lambda: [
            FocusArea.READABILITY,
            FocusArea.PERFORMANCE,
            FocusArea.MAINTAINABILITY,
            FocusArea.BEST_PRACTICES,
        ],
    )
    language: str = "auto-detect"
    aggressiveness: Aggressiveness = Aggressiveness.MODERATE
    explain_changes: bool = True
    style_guide: str | None = None
    specific_issues: list[str] = field(default_factory=list)


# Custom tool for analyzing code quality
@tool(
    name="analyze_code_quality",
    description="Analyzes code to identify issues, code smells, and areas for improvement",
)
async def analyze_code_tool(code: str, language: str | None = None) -> dict[str, Any]:
    """Analyzes code quality and returns issues, metrics, and recommendations.

    Args:
        code: The code to analyze
        language: Programming language of the code

    Returns:
        Dictionary containing issues, metrics, and recommendations

    """
    issues = []
    recommendations = []

    # Basic heuristic checks
    lines = code.split("\n")

    # Check for outdated syntax (Python-specific)
    if language == "python" or not language:
        if "print " in code and "print(" not in code:
            issues.append(
                {
                    "type": "outdated-syntax",
                    "severity": Severity.MEDIUM.value,
                    "description": "Use of Python 2 print statement",
                    "suggestion": "Use Python 3 print function: print()",
                },
            )

        if re.search(r"\bexec\b", code) or re.search(r"\beval\b", code):
            issues.append(
                {
                    "type": "security",
                    "severity": Severity.CRITICAL.value,
                    "description": "Use of exec/eval detected",
                    "suggestion": "Avoid exec/eval for security and maintainability",
                },
            )

    # Check for long lines
    long_lines = [i for i, line in enumerate(lines, 1) if len(line) > 100]
    if long_lines:
        issues.append(
            {
                "type": "readability",
                "severity": Severity.LOW.value,
                "description": f"Long lines detected at lines: {long_lines[:5]}",
                "suggestion": "Break long lines for better readability (PEP 8: max 79-100 chars)",
            },
        )

    # Check for TODO/FIXME comments
    todo_pattern = re.compile(r"#\s*(TODO|FIXME|XXX|HACK)", re.IGNORECASE)
    todo_matches = sum(1 for line in lines if todo_pattern.search(line))
    if todo_matches > 0:
        issues.append(
            {
                "type": "technical-debt",
                "severity": Severity.MEDIUM.value,
                "description": f"Found {todo_matches} TODO/FIXME comments",
                "suggestion": "Address technical debt markers",
            },
        )

    # Check for deep nesting
    max_indent = max((len(line) - len(line.lstrip()) for line in lines if line.strip()), default=0)
    indent_level = max_indent // 4  # Assuming 4-space indents
    if indent_level > 4:
        issues.append(
            {
                "type": "complexity",
                "severity": Severity.HIGH.value,
                "description": f"Deep nesting detected ({indent_level} levels)",
                "suggestion": "Consider extracting nested logic into separate functions",
            },
        )

    # Check for very long functions (basic heuristic)
    func_pattern = re.compile(r"^\s*def\s+\w+")
    func_starts = [i for i, line in enumerate(lines) if func_pattern.match(line)]
    if func_starts:
        for i, start in enumerate(func_starts):
            end = func_starts[i + 1] if i + 1 < len(func_starts) else len(lines)
            func_length = end - start
            if func_length > 50:
                issues.append(
                    {
                        "type": "complexity",
                        "severity": Severity.MEDIUM.value,
                        "description": f"Long function detected at line {start + 1} ({func_length} lines)",
                        "suggestion": "Consider breaking down into smaller functions",
                    },
                )

    # Check for missing docstrings (Python-specific)
    if (language == "python" or not language) and ("def " in code or "class " in code):  # noqa: SIM102
        if '"""' not in code and "'''" not in code:
            issues.append(
                {
                    "type": "documentation",
                    "severity": Severity.LOW.value,
                    "description": "Missing docstrings",
                    "suggestion": "Add docstrings to functions and classes",
                },
            )

    # Calculate metrics
    complexity = indent_level + len(func_starts)
    maintainability_index = max(0, 100 - (len(issues) * 10))
    technical_debt = "high" if len(issues) > 5 else "medium" if len(issues) > 2 else "low"

    # General recommendations
    recommendations = [
        "Follow consistent naming conventions (PEP 8 for Python)",
        "Add appropriate error handling with try/except",
        "Include documentation for complex logic",
        "Consider extracting reusable functions",
        "Ensure proper separation of concerns",
        "Add type hints for better code clarity (Python 3.5+)",
        "Use context managers (with statements) for resource handling",
        "Consider using dataclasses or named tuples for data structures",
    ]

    return {
        "issues": issues,
        "metrics": {
            "complexity": complexity,
            "maintainability_index": maintainability_index,
            "technical_debt": technical_debt,
        },
        "recommendations": recommendations,
    }


# System prompt for the Code Refactorer agent
CODE_REFACTORER_SYSTEM_PROMPT = """You are an expert Code Refactorer agent specializing in improving code quality.

Your mission is to transform poorly written, hard-to-maintain code into clean, efficient, and maintainable solutions.

## Core Responsibilities:

1. **Code Cleanup**: Remove dead code, unused variables, and redundant logic
2. **Readability**: Improve naming, structure, and formatting for better comprehension
3. **Performance**: Identify and fix performance bottlenecks and inefficiencies
4. **Maintainability**: Restructure code to be easier to modify and extend
5. **Best Practices**: Apply industry-standard patterns and conventions
6. **Technical Debt**: Identify and reduce accumulated technical debt

## Refactoring Principles:

- **Don't change behavior**: Maintain the same functionality unless explicitly asked
- **Small steps**: Make incremental, testable changes
- **Preserve tests**: Ensure existing tests still pass (or update them appropriately)
- **Document changes**: Explain why each change improves the code
- **Consider context**: Understand the broader system before refactoring
- **Be pragmatic**: Balance idealism with practical constraints

## Analysis Approach:

1. **Understand**: Read and comprehend the code's purpose and current state
2. **Identify**: Find code smells, anti-patterns, and improvement opportunities
3. **Prioritize**: Focus on high-impact improvements first
4. **Refactor**: Apply systematic transformations
5. **Validate**: Ensure changes maintain correctness and improve quality
6. **Explain**: Provide clear reasoning for each change

## Common Refactoring Patterns:

- Extract Method/Function: Break down large functions
- Rename: Use descriptive, meaningful names
- Remove Duplication: Apply DRY (Don't Repeat Yourself)
- Simplify Conditionals: Reduce complexity in if/else chains
- Replace Magic Numbers: Use named constants
- Improve Error Handling: Add proper try/catch and validation
- Optimize Loops: Improve iteration efficiency
- Update Syntax: Use modern language features
- Add Type Safety: Include type annotations where beneficial
- Organize Imports: Clean up and structure dependencies

## Code Smells to Watch For:

- Long methods/functions (>20-30 lines)
- Large classes (God objects)
- Long parameter lists (>3-4 parameters)
- Duplicate code
- Dead code
- Speculative generality
- Inappropriate intimacy between modules
- Feature envy (method using more of another class than its own)
- Data clumps (same data items together repeatedly)
- Primitive obsession (overuse of primitives instead of objects)
- Switch/case statements that could be polymorphism
- Lazy classes (classes that don't do enough)
- Deep nesting (>3 levels)
- Comments explaining what code does (code should be self-explanatory)

## Language-Specific Best Practices:

### Python:
- Follow PEP 8 style guide
- Use list/dict comprehensions appropriately
- Leverage context managers (with statements)
- Add type hints (PEP 484)
- Use dataclasses for data structures
- Prefer f-strings for formatting
- Use pathlib for file operations
- Apply EAFP (Easier to Ask Forgiveness than Permission)

### JavaScript/TypeScript:
- Use const/let instead of var
- Prefer arrow functions for callbacks
- Use async/await over callbacks
- Apply destructuring for cleaner code
- Use template literals
- Leverage spread/rest operators
- Add TypeScript types
- Use modern ES6+ features

### General:
- SOLID principles
- Design patterns where appropriate
- Dependency injection
- Interface segregation
- Single responsibility principle

## Output Format:

When refactoring, provide:
1. **Analysis**: Issues found and their severity
2. **Refactored Code**: The improved version
3. **Change Summary**: List of specific changes made
4. **Explanations**: Why each change improves the code
5. **Recommendations**: Additional improvements for future consideration

Always be constructive and educational. Help developers understand not just what to change, but why it matters."""


async def refactor_code(code: str, config: RefactorConfig | None = None) -> RefactorResult:
    """Main Code Refactorer agent function.

    Args:
        code: The code to refactor
        config: Refactoring configuration options

    Returns:
        RefactorResult containing the refactored code, changes, analysis, and summary

    """
    if config is None:
        config = RefactorConfig()

    # Build the prompt for the agent
    prompt = f"Please refactor the following code:\n\n```{config.language}\n{code}\n```\n\n"

    prompt += "**Refactoring Configuration:**\n"
    prompt += f"- Focus areas: {', '.join(f.value for f in config.focus)}\n"
    prompt += f"- Aggressiveness: {config.aggressiveness.value}\n"
    prompt += f"- Language: {config.language}\n"

    if config.style_guide:
        prompt += f"- Style guide: {config.style_guide}\n"

    if config.specific_issues:
        prompt += f"- Specific issues to address: {', '.join(config.specific_issues)}\n"

    prompt += "\n**Instructions:**\n"
    prompt += "1. First, analyze the code to identify issues and improvement opportunities\n"
    prompt += "2. Apply refactoring based on the focus areas and aggressiveness level\n"
    prompt += "3. Provide the refactored code\n"
    prompt += f"4. List all changes made{' with detailed explanations' if config.explain_changes else ''}\n"
    prompt += "5. Provide a summary of improvements\n"

    # Query the agent with custom tools
    result = None
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            system_prompt=CODE_REFACTORER_SYSTEM_PROMPT,
            tools=[analyze_code_tool],
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
        ),
    ):
        result = message

    # Extract text content from the result
    response_text = ""
    if result and hasattr(result, "content"):
        for block in result.content:
            if hasattr(block, "type") and block.type == "text":
                response_text += block.text

    # Extract refactored code from markdown code blocks
    code_block_match = re.search(r"```[\w]*\n([\s\S]*?)\n```", response_text)
    refactored_code = code_block_match.group(1) if code_block_match else code

    # Build the result object
    return RefactorResult(
        refactored_code=refactored_code,
        changes=[],  # Would be populated from structured response
        analysis=CodeAnalysis(),
        summary=response_text,
    )


async def analyze_code(code: str, language: str | None = None) -> CodeAnalysis:
    """Analyze code without refactoring.

    Args:
        code: The code to analyze
        language: Programming language of the code

    Returns:
        CodeAnalysis containing issues, metrics, and recommendations

    """
    prompt = f"""Please analyze the following code for issues, code smells, and improvement opportunities:

```{language or ""}
{code}
```

Provide a detailed analysis including:
1. List of issues with severity levels
2. Code quality metrics
3. Specific recommendations for improvement"""

    result = None
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            system_prompt=CODE_REFACTORER_SYSTEM_PROMPT,
            tools=[analyze_code_tool],
            model="claude-sonnet-4-5-20250929",
        ),
    ):
        result = message

    # Use the analyze_code_quality tool result if available
    if result and hasattr(result, "content"):
        for block in result.content:
            if (
                hasattr(block, "type")
                and block.type == "tool_result"
                and hasattr(block, "name")
                and block.name == "analyze_code_quality"
            ):
                tool_data = block.content
                return CodeAnalysis(
                    issues=[CodeIssue(**issue) for issue in tool_data.get("issues", [])],
                    metrics=CodeMetrics(**tool_data.get("metrics", {})),
                    recommendations=tool_data.get("recommendations", []),
                )

    # Fallback to empty analysis
    return CodeAnalysis()


async def refactor_interactive(
    code: str,
    config: RefactorConfig | None = None,
) -> AsyncGenerator[str, str | None]:
    """Interactive refactoring session.

    Args:
        code: The initial code to refactor
        config: Refactoring configuration options

    Yields:
        Responses from the refactoring agent

    """
    if config is None:
        config = RefactorConfig()

    current_code = code

    initial_prompt = f"""I have code that needs refactoring. Let's work on it together interactively.

Initial code:
```{config.language}
{current_code}
```

Configuration: {config.__dict__}

Please start by analyzing the code and suggesting the first improvement."""

    # First interaction
    async for message in query(
        prompt=initial_prompt,
        options=ClaudeAgentOptions(
            system_prompt=CODE_REFACTORER_SYSTEM_PROMPT,
            tools=[analyze_code_tool],
            model="claude-sonnet-4-5-20250929",
            stream=True,
        ),
    ):
        if hasattr(message, "type") and message.type == "text":
            yield message.text

    # Allow for follow-up iterations
    while True:
        user_feedback = yield ""
        if not user_feedback or user_feedback.lower() == "done":
            break

        async for message in query(
            prompt=user_feedback,
            options=ClaudeAgentOptions(
                system_prompt=CODE_REFACTORER_SYSTEM_PROMPT,
                model="claude-sonnet-4-5-20250929",
                stream=True,
            ),
        ):
            if hasattr(message, "type") and message.type == "text":
                yield message.text


# Public API
__all__ = [
    "CODE_REFACTORER_SYSTEM_PROMPT",
    "Aggressiveness",
    "CodeAnalysis",
    "FocusArea",
    "RefactorConfig",
    "RefactorResult",
    "Severity",
    "analyze_code",
    "refactor_code",
    "refactor_interactive",
]
