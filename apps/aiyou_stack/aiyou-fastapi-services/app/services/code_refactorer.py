import json
import re
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query

from app.models.refactor import (
    AnalyzeRequest,
    AnalyzeResponse,
    CodeIssue,
    RefactorRequest,
    RefactorResponse,
    RefactorType,
)
from config.settings import settings


class CodeRefactorerService:
    """Service for AI-powered code refactoring using Claude Agent SDK."""

    def __init__(self):
        self.model = settings.model
        self.max_tokens = settings.max_tokens

    async def refactor_code(self, request: RefactorRequest) -> RefactorResponse:
        """Refactor code based on the specified refactoring type.

        Args:
            request: RefactorRequest containing code and refactoring parameters

        Returns:
            RefactorResponse with refactored code and analysis

        """
        # Build the prompt based on refactoring type
        system_prompt = self._build_system_prompt(request.refactor_type)
        user_prompt = self._build_refactor_prompt(request)

        # Query Claude Agent SDK
        response_text = await self._query_claude(user_prompt, system_prompt)

        # Parse the response
        refactor_response = self._parse_refactor_response(
            response_text,
            request.code,
            request.language.value,
        )

        return refactor_response

    async def analyze_code(self, request: AnalyzeRequest) -> AnalyzeResponse:
        """Analyze code for quality issues without refactoring.

        Args:
            request: AnalyzeRequest containing code to analyze

        Returns:
            AnalyzeResponse with issues and metrics

        """
        system_prompt = """You are a code analysis expert. Analyze code for:
        - Code quality issues
        - Performance problems
        - Security vulnerabilities
        - Best practice violations
        - Complexity metrics
        - Maintainability concerns

        Provide detailed analysis in JSON format."""

        user_prompt = f"""Analyze the following {request.language.value} code:

```{request.language.value}
{request.code}
```

Return your analysis in the following JSON format:
{{
    "issues": [
        {{
            "line_number": <number or null>,
            "severity": "<error|warning|info>",
            "category": "<category>",
            "message": "<description>",
            "suggestion": "<how to fix>"
        }}
    ],
    "metrics": {{
        "cyclomatic_complexity": <number>,
        "lines_of_code": <number>,
        "maintainability_index": <number>
    }},
    "suggestions": ["<improvement suggestion>"],
    "overall_quality_score": <0-100>
}}"""

        response_text = await self._query_claude(user_prompt, system_prompt)

        # Parse JSON response
        analysis_data = self._extract_json(response_text)

        return AnalyzeResponse(
            issues=[CodeIssue(**issue) for issue in analysis_data.get("issues", [])],
            metrics=analysis_data.get("metrics", {}),
            suggestions=analysis_data.get("suggestions", []),
            overall_quality_score=analysis_data.get("overall_quality_score"),
        )

    def _build_system_prompt(self, refactor_type: RefactorType) -> str:
        """Build system prompt based on refactoring type."""
        base_prompt = """You are a world-class code refactoring specialist. Your expertise includes:
        - Writing clean, readable, and maintainable code
        - Identifying and fixing code smells
        - Optimizing performance
        - Following language-specific best practices
        - Reducing technical debt
        - Improving code structure and design patterns"""

        type_specific = {
            RefactorType.CLEANUP: "\n\nFocus on: Code cleanup, removing dead code, fixing formatting, organizing imports.",
            RefactorType.READABILITY: "\n\nFocus on: Variable naming, code structure, adding helpful comments, simplifying complex logic.",
            RefactorType.PERFORMANCE: "\n\nFocus on: Algorithm optimization, reducing complexity, efficient data structures, caching.",
            RefactorType.MAINTAINABILITY: "\n\nFocus on: Modularity, separation of concerns, reducing coupling, clear interfaces.",
            RefactorType.BEST_PRACTICES: "\n\nFocus on: Language idioms, design patterns, industry standards, security best practices.",
            RefactorType.TECHNICAL_DEBT: "\n\nFocus on: Fixing shortcuts, improving architecture, addressing TODOs, updating deprecated code.",
            RefactorType.FULL: "\n\nFocus on: All aspects - cleanup, readability, performance, maintainability, and best practices.",
        }

        return base_prompt + type_specific.get(refactor_type, "")

    def _build_refactor_prompt(self, request: RefactorRequest) -> str:
        """Build the user prompt for refactoring."""
        context_section = f"\n\nContext: {request.context}" if request.context else ""
        preserve_note = (
            "\n\nIMPORTANT: Preserve the exact functionality of the original code."
            if request.preserve_functionality
            else ""
        )

        prompt = f"""Refactor the following {request.language.value} code.

Refactoring Type: {request.refactor_type.value}{context_section}{preserve_note}

Original Code:
```{request.language.value}
{request.code}
```

Please provide your response in the following format:

## Refactored Code
```{request.language.value}
<refactored code here>
```

## Issues Found
- [Line X] <severity>: <issue description>
- ...

## Improvements Made
1. <improvement description>
2. ...

## Explanation
<Brief explanation of the changes and why they improve the code>

## Complexity Analysis
Before: <complexity metrics>
After: <complexity metrics>
"""
        return prompt

    async def _query_claude(self, user_prompt: str, system_prompt: str) -> str:
        """Query Claude Agent SDK and return the response."""
        full_response = []

        async for message in query(
            prompt=user_prompt,
            options=ClaudeAgentOptions(
                system_prompt=system_prompt,
                model=self.model,
                max_tokens=self.max_tokens,
            ),
        ):
            if hasattr(message, "text") and message.text:
                full_response.append(message.text)

        return "".join(full_response)

    def _parse_refactor_response(
        self,
        response: str,
        original_code: str,
        language: str,
    ) -> RefactorResponse:
        """Parse Claude's refactoring response into structured format."""
        # Extract refactored code
        refactored_code = self._extract_code_block(response, language) or original_code

        # Extract issues
        issues = self._extract_issues(response)

        # Extract improvements
        improvements = self._extract_improvements(response)

        # Extract explanation
        explanation = self._extract_explanation(response)

        # Extract complexity analysis
        complexity_before, complexity_after = self._extract_complexity(response)

        return RefactorResponse(
            original_code=original_code,
            refactored_code=refactored_code,
            issues_found=issues,
            improvements=improvements,
            complexity_before=complexity_before,
            complexity_after=complexity_after,
            explanation=explanation,
        )

    def _extract_code_block(self, text: str, language: str) -> str | None:
        """Extract code from markdown code blocks."""
        patterns = [
            rf"```{language}\n(.*?)```",
            r"```\n(.*?)```",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()

        return None

    def _extract_issues(self, text: str) -> list[CodeIssue]:
        """Extract issues from the response."""
        issues = []
        issues_section = re.search(r"## Issues Found\n(.*?)(?=##|\Z)", text, re.DOTALL)

        if issues_section:
            issue_lines = issues_section.group(1).strip().split("\n")
            for line in issue_lines:
                if line.strip().startswith("-") or line.strip().startswith("*"):
                    # Parse issue line
                    line_num_match = re.search(r"\[Line (\d+)\]", line)
                    severity_match = re.search(r"(error|warning|info)", line, re.IGNORECASE)

                    line_number = int(line_num_match.group(1)) if line_num_match else None
                    severity = severity_match.group(1).lower() if severity_match else "info"

                    # Extract message
                    message = re.sub(r"\[Line \d+\]", "", line)
                    message = re.sub(r"[-*]", "", message).strip()

                    if message:
                        issues.append(
                            CodeIssue(
                                line_number=line_number,
                                severity=severity,
                                category="code_quality",
                                message=message,
                            ),
                        )

        return issues

    def _extract_improvements(self, text: str) -> list[str]:
        """Extract improvements from the response."""
        improvements = []
        improvements_section = re.search(r"## Improvements Made\n(.*?)(?=##|\Z)", text, re.DOTALL)

        if improvements_section:
            improvement_lines = improvements_section.group(1).strip().split("\n")
            for line in improvement_lines:
                if line.strip() and (
                    line.strip().startswith("-")
                    or line.strip().startswith("*")
                    or re.match(r"\d+\.", line.strip())
                ):
                    improvement = re.sub(r"^[-*\d.]+\s*", "", line).strip()
                    if improvement:
                        improvements.append(improvement)

        return improvements

    def _extract_explanation(self, text: str) -> str:
        """Extract explanation from the response."""
        explanation_section = re.search(r"## Explanation\n(.*?)(?=##|\Z)", text, re.DOTALL)

        if explanation_section:
            return explanation_section.group(1).strip()

        return "No explanation provided."

    def _extract_complexity(self, text: str) -> tuple[dict | None, dict | None]:
        """Extract complexity analysis from the response."""
        complexity_section = re.search(r"## Complexity Analysis\n(.*?)(?=##|\Z)", text, re.DOTALL)

        if complexity_section:
            content = complexity_section.group(1).strip()
            before_match = re.search(r"Before:\s*(.+)", content)
            after_match = re.search(r"After:\s*(.+)", content)

            before = {"description": before_match.group(1).strip()} if before_match else None
            after = {"description": after_match.group(1).strip()} if after_match else None

            return before, after

        return None, None

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from text response."""
        # Try to find JSON block
        json_match = re.search(r"```json\n(.*?)```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        return {}
