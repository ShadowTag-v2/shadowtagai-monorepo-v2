"""
AI Agent for Support Builder using Anthropic Claude API.

This agent provides intelligent customer support responses,
suggesting relevant FAQs and help articles.
"""

from collections.abc import AsyncGenerator

from anthropic import AsyncAnthropic

from src.config import settings


class SupportBuilderAgent:
    """
    AI agent for customer support using Claude.

    This agent analyzes user queries and generates helpful responses,
    while also identifying relevant FAQs and documentation.
    """

    def __init__(self):
        """Initialize the support builder agent."""
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.default_model = "claude-3-sonnet-20240229"
        self.default_system_prompt = """You are a helpful customer support assistant.

Your role is to:
1. Provide clear, concise, and accurate answers to customer questions
2. Be empathetic and professional
3. Guide users to relevant FAQs and documentation when appropriate
4. Suggest escalation to human support for complex issues
5. Focus on resolving customer issues efficiently

Guidelines:
- Keep responses concise but comprehensive
- Use a friendly, professional tone
- Ask clarifying questions when needed
- Admit when you don't know something
- Prioritize customer satisfaction
"""

    async def generate_response(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate a response to a user message using Claude.

        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            system_prompt: Custom system prompt (optional)
            model: Claude model to use (optional)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response

        Returns:
            AI-generated response string
        """
        # Build messages list
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        # Use custom or default system prompt
        system = system_prompt or self.default_system_prompt

        # Use custom or default model
        model_to_use = model or self.default_model

        try:
            response = await self.client.messages.create(
                model=model_to_use,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=messages,
            )

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return "I apologize, but I couldn't generate a response. Please try again."

        except Exception as e:
            print(f"Error generating response: {e}")
            return "I'm experiencing technical difficulties. Please try again later."

    async def stream_response(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
        system_prompt: str | None = None,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response to a user message using Claude.

        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages
            system_prompt: Custom system prompt (optional)
            model: Claude model to use (optional)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response

        Yields:
            Chunks of the AI-generated response
        """
        # Build messages list
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        # Use custom or default system prompt
        system = system_prompt or self.default_system_prompt

        # Use custom or default model
        model_to_use = model or self.default_model

        try:
            async with self.client.messages.stream(
                model=model_to_use,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            print(f"Error streaming response: {e}")
            yield "I'm experiencing technical difficulties. Please try again later."

    async def analyze_query_intent(
        self,
        user_message: str,
        categories: list[str],
    ) -> dict[str, any]:
        """
        Analyze user query to determine intent and relevant categories.

        Args:
            user_message: The user's message
            categories: Available FAQ/article categories

        Returns:
            Dictionary with intent analysis results
        """
        analysis_prompt = f"""Analyze this customer support query and provide:
1. The primary intent (question, complaint, request, feedback)
2. Relevant categories from this list: {", ".join(categories)}
3. Urgency level (low, medium, high)
4. Whether it likely needs human escalation (yes/no)

Query: {user_message}

Respond in this exact format:
Intent: [intent]
Categories: [category1, category2]
Urgency: [level]
Escalate: [yes/no]
Reasoning: [brief explanation]
"""

        try:
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",  # Use faster model for analysis
                max_tokens=256,
                temperature=0.3,  # Lower temperature for more consistent analysis
                messages=[{"role": "user", "content": analysis_prompt}],
            )

            if response.content and len(response.content) > 0:
                analysis_text = response.content[0].text
                return self._parse_intent_analysis(analysis_text)

        except Exception as e:
            print(f"Error analyzing query intent: {e}")

        # Return default analysis on error
        return {
            "intent": "question",
            "categories": [],
            "urgency": "medium",
            "escalate": False,
            "reasoning": "Unable to analyze",
        }

    def _parse_intent_analysis(self, analysis_text: str) -> dict[str, any]:
        """Parse the intent analysis response."""
        result = {
            "intent": "question",
            "categories": [],
            "urgency": "medium",
            "escalate": False,
            "reasoning": "",
        }

        lines = analysis_text.strip().split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key == "intent":
                    result["intent"] = value.lower()
                elif key == "categories":
                    # Parse comma-separated categories
                    categories = [c.strip() for c in value.strip("[]").split(",")]
                    result["categories"] = [c for c in categories if c]
                elif key == "urgency":
                    result["urgency"] = value.lower()
                elif key == "escalate":
                    result["escalate"] = value.lower() == "yes"
                elif key == "reasoning":
                    result["reasoning"] = value

        return result

    async def generate_faq_suggestion_keywords(
        self,
        user_message: str,
    ) -> list[str]:
        """
        Generate keywords for FAQ search based on user message.

        Args:
            user_message: The user's message

        Returns:
            List of search keywords
        """
        keyword_prompt = f"""Extract 3-5 key search terms from this customer query that would help find relevant FAQs.
Focus on the core topic, not question words.

Query: {user_message}

Return only the keywords separated by commas, nothing else.
"""

        try:
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.3,
                messages=[{"role": "user", "content": keyword_prompt}],
            )

            if response.content and len(response.content) > 0:
                keywords_text = response.content[0].text.strip()
                keywords = [k.strip() for k in keywords_text.split(",")]
                return [k for k in keywords if k]

        except Exception as e:
            print(f"Error generating keywords: {e}")

        # Fallback: extract significant words from user message
        words = user_message.lower().split()
        # Filter out common question words
        stop_words = {"what", "how", "when", "where", "why", "who", "is", "are", "the", "a", "an"}
        return [w for w in words if w not in stop_words][:5]


# Global agent instance
support_agent = SupportBuilderAgent()
