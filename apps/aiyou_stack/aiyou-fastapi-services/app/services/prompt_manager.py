"""Prompt management system with templates and engineering."""

import json
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger()


class PromptTemplate:
    """A reusable prompt template with variable substitution."""

    def __init__(
        self,
        name: str,
        template: str,
        description: str | None = None,
        variables: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.name = name
        self.template = template
        self.description = description
        self.variables = variables or []
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()

    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(
                "Template rendering failed - missing variable",
                template_name=self.name,
                missing_variable=str(e),
            )
            raise ValueError(f"Missing required variable: {e}") from e

    def to_dict(self) -> dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "variables": self.variables,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class PromptManager:
    """Manager for prompt templates and engineering."""

    def __init__(self):
        self.templates: dict[str, PromptTemplate] = {}
        self._load_default_templates()
        logger.info("Prompt manager initialized")

    def _load_default_templates(self):
        """Load default prompt templates."""
        defaults = [
            PromptTemplate(
                name="basic_chat",
                template="You are a helpful AI assistant. {instruction}",
                description="Basic chat prompt",
                variables=["instruction"],
            ),
            PromptTemplate(
                name="code_assistant",
                template=(
                    "You are an expert programming assistant. "
                    "Programming language: {language}\n"
                    "Task: {task}\n"
                    "Provide clear, well-commented code with explanations."
                ),
                description="Code generation and assistance",
                variables=["language", "task"],
            ),
            PromptTemplate(
                name="summarization",
                template=(
                    "Please summarize the following text in {style} style. "
                    "Maximum length: {max_length} words.\n\n"
                    "Text to summarize:\n{text}"
                ),
                description="Text summarization",
                variables=["style", "max_length", "text"],
            ),
            PromptTemplate(
                name="question_answering",
                template=(
                    "Answer the following question based on the provided context. "
                    "If the answer cannot be found in the context, say so.\n\n"
                    "Context:\n{context}\n\n"
                    "Question: {question}\n\n"
                    "Answer:"
                ),
                description="Context-based question answering",
                variables=["context", "question"],
            ),
            PromptTemplate(
                name="creative_writing",
                template=(
                    "Write a creative {content_type} with the following requirements:\n"
                    "Genre: {genre}\n"
                    "Tone: {tone}\n"
                    "Theme: {theme}\n"
                    "Length: approximately {length} words"
                ),
                description="Creative writing prompts",
                variables=["content_type", "genre", "tone", "theme", "length"],
            ),
            PromptTemplate(
                name="data_analysis",
                template=(
                    "Analyze the following data and provide insights:\n\n"
                    "Data:\n{data}\n\n"
                    "Analysis focus: {focus}\n"
                    "Output format: {output_format}"
                ),
                description="Data analysis and insights",
                variables=["data", "focus", "output_format"],
            ),
            PromptTemplate(
                name="translation",
                template=(
                    "Translate the following text from {source_language} to {target_language}. "
                    "Maintain the original tone and meaning.\n\n"
                    "Text:\n{text}"
                ),
                description="Language translation",
                variables=["source_language", "target_language", "text"],
            ),
            PromptTemplate(
                name="few_shot_learning",
                template=(
                    "Here are some examples:\n\n"
                    "{examples}\n\n"
                    "Now, apply the same pattern to:\n{input}"
                ),
                description="Few-shot learning pattern",
                variables=["examples", "input"],
            ),
        ]

        for template in defaults:
            self.templates[template.name] = template

        logger.info("Default templates loaded", count=len(defaults))

    def add_template(self, template: PromptTemplate) -> None:
        """Add a new template."""
        self.templates[template.name] = template
        logger.info("Template added", template_name=template.name)

    def get_template(self, name: str) -> PromptTemplate | None:
        """Get a template by name."""
        return self.templates.get(name)

    def remove_template(self, name: str) -> bool:
        """Remove a template by name."""
        if name in self.templates:
            del self.templates[name]
            logger.info("Template removed", template_name=name)
            return True
        return False

    def list_templates(self) -> list[str]:
        """List all template names."""
        return list(self.templates.keys())

    def render_template(self, name: str, **kwargs) -> str:
        """Render a template with provided variables."""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template not found: {name}")

        return template.render(**kwargs)

    def export_templates(self, filepath: str) -> None:
        """Export all templates to a JSON file."""
        try:
            data = {name: template.to_dict() for name, template in self.templates.items()}

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

            logger.info("Templates exported", filepath=filepath)
        except Exception as e:
            logger.error("Template export failed", error=str(e))
            raise

    def import_templates(self, filepath: str) -> None:
        """Import templates from a JSON file."""
        try:
            with open(filepath) as f:
                data = json.load(f)

            for name, template_data in data.items():
                template = PromptTemplate(
                    name=template_data["name"],
                    template=template_data["template"],
                    description=template_data.get("description"),
                    variables=template_data.get("variables", []),
                    metadata=template_data.get("metadata", {}),
                )
                self.templates[name] = template

            logger.info("Templates imported", filepath=filepath, count=len(data))
        except Exception as e:
            logger.error("Template import failed", error=str(e))
            raise


class PromptEngineer:
    """Utilities for prompt engineering and optimization."""

    @staticmethod
    def add_context(prompt: str, context: str) -> str:
        """Add context to a prompt."""
        return f"Context:\n{context}\n\n{prompt}"

    @staticmethod
    def add_examples(prompt: str, examples: list[dict[str, str]]) -> str:
        """Add few-shot examples to a prompt."""
        examples_text = "\n\n".join(
            [
                f"Example {i + 1}:\nInput: {ex['input']}\nOutput: {ex['output']}"
                for i, ex in enumerate(examples)
            ],
        )

        return f"{examples_text}\n\n{prompt}"

    @staticmethod
    def add_constraints(prompt: str, constraints: list[str]) -> str:
        """Add constraints to a prompt."""
        constraints_text = "\n".join([f"- {c}" for c in constraints])
        return f"{prompt}\n\nConstraints:\n{constraints_text}"

    @staticmethod
    def add_output_format(prompt: str, format_description: str) -> str:
        """Specify output format in a prompt."""
        return f"{prompt}\n\nOutput format:\n{format_description}"

    @staticmethod
    def chain_of_thought(prompt: str) -> str:
        """Add chain-of-thought prompting."""
        return f"{prompt}\n\nLet's approach this step by step:"

    @staticmethod
    def role_based(role: str, task: str) -> str:
        """Create a role-based prompt."""
        return f"You are {role}. {task}"

    @staticmethod
    def temperature_guidance(task_type: str) -> float:
        """Suggest temperature based on task type."""
        temperatures = {"creative": 0.9, "balanced": 0.7, "factual": 0.3, "deterministic": 0.0}
        return temperatures.get(task_type.lower(), 0.7)
