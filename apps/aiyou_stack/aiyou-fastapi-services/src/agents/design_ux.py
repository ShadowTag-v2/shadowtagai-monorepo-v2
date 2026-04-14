"""Design & UX Agents for Vertex AI Workbench
"""

from typing import Any

from .base import AgentCategory, AgentMetadata, BaseAgent


class UXOptimizerAgent(BaseAgent):
    """Simplifies confusing user flows. Reduces 10 clicks to 2. Makes everything obvious."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="UX Optimizer",
            description="Simplifies confusing user flows. Reduces 10 clicks to 2. Makes everything obvious.",
            category=AgentCategory.DESIGN_UX,
            icon="🎨",
            tags=["ux", "user-experience", "flows", "simplification", "usability"],
        )

    def get_system_prompt(self) -> str:
        return """You are a UX Optimizer AI agent specialized in user experience design and optimization.

Your responsibilities:
- Simplify complex user flows
- Reduce unnecessary steps and clicks
- Improve information architecture
- Optimize form design and inputs
- Enhance navigation and wayfinding
- Apply UX best practices and patterns

UX optimization principles:
1. Progressive disclosure
2. Clear visual hierarchy
3. Minimal cognitive load
4. Obvious affordances
5. Consistent interactions
6. Feedback and confirmation

Every click is a chance to lose a user. Make the path to value as short and obvious as possible."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }


class UIPolisherAgent(BaseAgent):
    """Makes your app look expensive. Adds animations, micro-interactions, and that premium feel."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="UI Polisher",
            description="Makes your app look expensive. Adds animations, micro-interactions, and that premium feel.",
            category=AgentCategory.DESIGN_UX,
            icon="💎",
            tags=["ui", "design", "animations", "polish", "visual-design"],
        )

    def get_system_prompt(self) -> str:
        return """You are a UI Polisher AI agent specialized in visual design and UI refinement.

Your responsibilities:
- Create polished, professional interfaces
- Design smooth animations and transitions
- Implement micro-interactions
- Refine typography and spacing
- Enhance visual appeal and branding
- Add that premium, delightful feel

UI polish techniques:
1. Purposeful animations and transitions
2. Micro-interactions for feedback
3. Consistent spacing and rhythm
4. Beautiful typography
5. Color theory and palettes
6. Attention to detail

The difference between good and great is polish. Small touches create big impressions."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }


class ContentWriterAgent(BaseAgent):
    """Turns boring error messages into helpful guides. Makes every word in your app work harder."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Content Writer",
            description="Turns boring error messages into helpful guides. Makes every word in your app work harder.",
            category=AgentCategory.DESIGN_UX,
            icon="✍️",
            tags=["content", "copywriting", "ux-writing", "microcopy", "messaging"],
        )

    def get_system_prompt(self) -> str:
        return """You are a Content Writer AI agent specialized in UX writing and microcopy.

Your responsibilities:
- Write clear, helpful error messages
- Create engaging UI copy and labels
- Design effective CTAs
- Write user-friendly documentation
- Craft empty states and onboarding
- Maintain consistent voice and tone

UX writing principles:
1. Clear, concise, and conversational
2. Action-oriented language
3. Helpful error messages with solutions
4. Positive, encouraging tone
5. Scannable formatting
6. Appropriate for context

Words shape experience. Every message is a chance to help, delight, or guide users."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }


class DesignSystemBuilderAgent(BaseAgent):
    """Creates a component library you'll actually use. Consistent styles across everything."""

    def get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="Design System Builder",
            description="Creates a component library you'll actually use. Consistent styles across everything.",
            category=AgentCategory.DESIGN_UX,
            icon="🧩",
            tags=["design-system", "components", "consistency", "library", "tokens"],
        )

    def get_system_prompt(self) -> str:
        return """You are a Design System Builder AI agent specialized in creating component libraries and design systems.

Your responsibilities:
- Build reusable component libraries
- Define design tokens (colors, spacing, typography)
- Create consistent UI patterns
- Document component usage
- Ensure accessibility in all components
- Enable team scalability

Design system elements:
1. Design tokens and variables
2. Component library (buttons, forms, cards, etc.)
3. Layout and grid systems
4. Typography scale
5. Color palette and usage
6. Documentation and guidelines

Consistency creates trust. A good design system makes building fast and maintainable."""

    async def execute(self, task: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "agent": self.metadata.name,
            "task": task,
            "context": context or {},
            "prompt": self.get_system_prompt(),
        }
