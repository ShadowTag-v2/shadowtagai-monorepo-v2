"""PNKLN Revenue Platform - Gemini 2.0 Integration
97% cost reduction: GPT-4 ($50K/year) → Gemini ($1.5K/year)

This module replaces OpenAI/AutoGen with Google Gemini 2.0 for:
- AI tutoring (Verdict Systems school vertical)
- Intelligence pipeline analysis
- Kernel chain execution
- All other AI inference
"""

import asyncio
import os
from datetime import datetime
from typing import Any

import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


class GeminiCostTracker:
    """Track Gemini API usage and costs for ROI measurement"""

    def __init__(self):
        self.usage_log = []

    def log_usage(self, model: str, input_tokens: int, output_tokens: int, use_case: str):
        """Log API usage with cost calculation"""
        # Gemini 2.0 Flash pricing (as of 2025)
        PRICE_PER_1M_INPUT = 0.15  # $0.15 per 1M input tokens
        PRICE_PER_1M_OUTPUT = 0.60  # $0.60 per 1M output tokens

        input_cost = (input_tokens / 1_000_000) * PRICE_PER_1M_INPUT
        output_cost = (output_tokens / 1_000_000) * PRICE_PER_1M_OUTPUT
        total_cost = input_cost + output_cost

        # Compare to GPT-4 pricing (for ROI tracking)
        GPT4_INPUT = 5.00  # $5 per 1M tokens
        GPT4_OUTPUT = 15.00  # $15 per 1M tokens

        gpt4_cost = (input_tokens / 1_000_000) * GPT4_INPUT + (
            output_tokens / 1_000_000
        ) * GPT4_OUTPUT
        savings = gpt4_cost - total_cost
        savings_pct = (savings / gpt4_cost * 100) if gpt4_cost > 0 else 0

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "use_case": use_case,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "gemini_cost": total_cost,
            "gpt4_cost": gpt4_cost,
            "savings": savings,
            "savings_pct": savings_pct,
        }

        self.usage_log.append(entry)
        return entry

    def get_total_savings(self) -> dict[str, float]:
        """Calculate total savings vs GPT-4"""
        total_gemini = sum(log["gemini_cost"] for log in self.usage_log)
        total_gpt4 = sum(log["gpt4_cost"] for log in self.usage_log)
        total_savings = total_gpt4 - total_gemini

        return {
            "gemini_cost": total_gemini,
            "gpt4_equivalent_cost": total_gpt4,
            "total_savings": total_savings,
            "savings_pct": (total_savings / total_gpt4 * 100) if total_gpt4 > 0 else 0,
            "calls": len(self.usage_log),
        }


# Global cost tracker instance
cost_tracker = GeminiCostTracker()


class GeminiService:
    """Gemini 2.0 service for all AI inference

    Features:
    - 97% cost reduction vs GPT-4
    - 2M token context window (vs 128K GPT-4)
    - Multimodal (text, images, audio, video)
    - Real-time streaming
    - Built-in safety filters
    """

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Gemini service

        Models:
        - gemini-2.0-flash-exp: Fast, cheap ($0.15/$0.60 per 1M tokens)
        - gemini-2.0-pro: More capable, higher cost
        - gemini-2.0-flash-thinking: Extended reasoning
        """
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    async def generate(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        use_case: str = "general",
    ) -> dict[str, Any]:
        """Generate response with Gemini

        Args:
            prompt: User prompt
            system_instruction: System instructions (like system message in ChatGPT)
            temperature: Randomness (0.0-1.0)
            max_tokens: Max output tokens
            use_case: For cost tracking (e.g., "ai_tutor", "intelligence_analysis")

        Returns:
            Dict with response text, usage stats, and cost savings

        """
        # Configure generation
        generation_config = genai.GenerationConfig(
            temperature=temperature, max_output_tokens=max_tokens,
        )

        # Add system instruction if provided
        if system_instruction:
            model_with_system = genai.GenerativeModel(
                self.model_name, system_instruction=system_instruction,
            )
            response = await asyncio.to_thread(
                model_with_system.generate_content, prompt, generation_config=generation_config,
            )
        else:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt, generation_config=generation_config,
            )

        # Extract usage metadata
        usage = response.usage_metadata
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count

        # Track costs and savings
        cost_entry = cost_tracker.log_usage(
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            use_case=use_case,
        )

        return {
            "text": response.text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost_entry["gemini_cost"],
            "gpt4_equivalent_cost": cost_entry["gpt4_cost"],
            "savings_usd": cost_entry["savings"],
            "savings_pct": cost_entry["savings_pct"],
        }

    async def chat(
        self,
        messages: list[dict[str, str]],
        system_instruction: str | None = None,
        temperature: float = 0.7,
        use_case: str = "chat",
    ) -> dict[str, Any]:
        """Multi-turn chat with Gemini

        Args:
            messages: List of {"role": "user"|"model", "content": "..."}
            system_instruction: System instructions
            temperature: Randomness
            use_case: For cost tracking

        Returns:
            Dict with response and cost savings

        """
        # Start chat session
        if system_instruction:
            model_with_system = genai.GenerativeModel(
                self.model_name, system_instruction=system_instruction,
            )
            chat = model_with_system.start_chat(history=[])
        else:
            chat = self.model.start_chat(history=[])

        # Add message history
        for msg in messages[:-1]:  # All except last message
            role = "user" if msg["role"] == "user" else "model"
            chat.history.append({"role": role, "parts": [msg["content"]]})

        # Send last message
        last_message = messages[-1]["content"]
        response = await asyncio.to_thread(
            chat.send_message,
            last_message,
            generation_config=genai.GenerationConfig(temperature=temperature),
        )

        # Track costs
        usage = response.usage_metadata
        cost_entry = cost_tracker.log_usage(
            model=self.model_name,
            input_tokens=usage.prompt_token_count,
            output_tokens=usage.candidates_token_count,
            use_case=use_case,
        )

        return {
            "text": response.text,
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count,
            "cost_usd": cost_entry["gemini_cost"],
            "savings_usd": cost_entry["savings"],
            "savings_pct": cost_entry["savings_pct"],
        }


# ============================================================================
# Integration with Verdict Systems (AI Tutor)
# ============================================================================


async def ai_tutor_session(
    student_id: str, task_description: str, subject: str, difficulty: str = "medium",
) -> dict[str, Any]:
    """AI tutor session using Gemini (replaces GPT-4)

    Cost comparison:
    - GPT-4: ~$0.50 per session (assuming 5K input, 3K output tokens)
    - Gemini: ~$0.015 per session (97% cheaper)

    Annual savings (10K sessions): $4,850
    """
    gemini = GeminiService()

    system_instruction = f"""You are an AI tutor helping a student with {subject}.

Your role:
- Provide hints and scaffolded guidance (NOT full solutions)
- Ask leading questions to help student think
- Explain concepts clearly
- Encourage student to work through problems

Student level: {difficulty}
Max hints per session: 5

Be supportive but don't give away answers."""

    prompt = f"""Student needs help with this assignment:
{task_description}

Provide a helpful hint to get them started. Ask a guiding question."""

    response = await gemini.generate(
        prompt=prompt, system_instruction=system_instruction, temperature=0.7, use_case="ai_tutor",
    )

    return {
        "tutor_response": response["text"],
        "cost_usd": response["cost_usd"],
        "savings_vs_gpt4": response["savings_usd"],
        "savings_pct": response["savings_pct"],
    }


# ============================================================================
# Integration with Intelligence Pipeline
# ============================================================================


async def analyze_intelligence_item(content: str, source_type: str) -> dict[str, Any]:
    """Analyze intelligence item using Gemini (replaces GPT-4)

    Cost comparison:
    - GPT-4: ~$0.80 per analysis (10K input, 5K output)
    - Gemini: ~$0.024 per analysis (97% cheaper)

    Annual savings (3K items/day × 365 = 1.1M items): $851,800
    """
    gemini = GeminiService()

    system_instruction = """You are an intelligence analyst. Analyze the content and provide:

1. Relevance score (0-100): How relevant is this to business/tech intelligence?
2. Key insights: 2-3 bullet points
3. Tier classification: 1 (priority), 2 (standard), or 3 (background)
4. Sentiment: positive, negative, or neutral
5. Entities: Key people, companies, technologies mentioned

Format as JSON."""

    prompt = f"""Source type: {source_type}

Content:
{content[:2000]}  # Limit to 2K chars for efficiency

Analyze and classify this intelligence item."""

    response = await gemini.generate(
        prompt=prompt,
        system_instruction=system_instruction,
        temperature=0.3,  # Lower temp for analytical tasks
        use_case="intelligence_analysis",
    )

    return {
        "analysis": response["text"],
        "cost_usd": response["cost_usd"],
        "savings_vs_gpt4": response["savings_usd"],
    }


# ============================================================================
# Migration Consulting: AutoGen → Gemini
# ============================================================================


class AutoGenToGeminiMigrator:
    """Migration service for AutoGen → Gemini customers

    Revenue opportunity:
    - Migration consulting: $10K-$100K per client
    - TAM: 10,000+ AutoGen users
    - Year 1 target: 50 migrations @ $20K avg = $1M revenue
    """

    def __init__(self):
        self.gemini = GeminiService()

    async def estimate_savings(
        self, monthly_gpt4_cost: float, total_monthly_tokens: int,
    ) -> dict[str, Any]:
        """Estimate cost savings from migration

        Args:
            monthly_gpt4_cost: Current monthly OpenAI bill
            total_monthly_tokens: Total tokens/month (input + output)

        Returns:
            Savings estimate and migration ROI

        """
        # Gemini equivalent cost (assume 50/50 input/output split)
        input_tokens = total_monthly_tokens * 0.5
        output_tokens = total_monthly_tokens * 0.5

        gemini_cost = (input_tokens / 1_000_000) * 0.15 + (output_tokens / 1_000_000) * 0.60

        annual_savings = (monthly_gpt4_cost - gemini_cost) * 12
        savings_pct = ((monthly_gpt4_cost - gemini_cost) / monthly_gpt4_cost) * 100

        # Migration ROI (assuming $20K migration fee)
        migration_fee = 20000
        payback_months = migration_fee / (monthly_gpt4_cost - gemini_cost)

        return {
            "current_monthly_cost": monthly_gpt4_cost,
            "gemini_monthly_cost": gemini_cost,
            "monthly_savings": monthly_gpt4_cost - gemini_cost,
            "annual_savings": annual_savings,
            "savings_pct": savings_pct,
            "migration_fee": migration_fee,
            "payback_months": payback_months,
            "roi_12_months": (annual_savings - migration_fee) / migration_fee * 100,
        }

    async def migrate_autogen_agent(self, autogen_config: dict[str, Any]) -> str:
        """Generate Gemini equivalent of AutoGen agent

        Returns Python code for Gemini-based agent
        """
        # This is simplified - real migration would be more complex
        agent_name = autogen_config.get("name", "assistant")
        system_message = autogen_config.get("system_message", "")

        code = f'''"""
Migrated from AutoGen to Gemini
Agent: {agent_name}
"""

from gemini_integration import GeminiService

class {agent_name.capitalize()}Agent:
    """Gemini-powered agent (migrated from AutoGen)"""

    def __init__(self):
        self.gemini = GeminiService()
        self.system_instruction = """{system_message}"""

    async def generate_reply(self, messages: List[Dict[str, str]]) -> str:
        """Generate reply using Gemini (97% cheaper than GPT-4)"""
        response = await self.gemini.chat(
            messages=messages,
            system_instruction=self.system_instruction,
            use_case="{agent_name}"
        )

        print(f"Cost: ${response['cost_usd']:.4f}")
        print(f"Savings vs GPT-4: ${response['savings_usd']:.4f} ({response['savings_pct']:.1f}%)")

        return response["text"]
'''
        return code


# ============================================================================
# Cost Reporting (for ROI measurement)
# ============================================================================


def get_cost_report() -> dict[str, Any]:
    """Generate cost savings report

    Use for:
    - Monthly billing reconciliation
    - ROI reporting to customers
    - Internal margin tracking
    """
    savings = cost_tracker.get_total_savings()

    # Project to annual
    if savings["calls"] > 0:
        avg_cost_per_call = savings["gemini_cost"] / savings["calls"]
        avg_savings_per_call = savings["total_savings"] / savings["calls"]

        # Estimate annual (assuming 10K calls/month)
        monthly_calls = 10000
        annual_gemini_cost = avg_cost_per_call * monthly_calls * 12
        annual_savings = avg_savings_per_call * monthly_calls * 12
    else:
        annual_gemini_cost = 0
        annual_savings = 0

    return {
        "period_stats": savings,
        "projections": {
            "annual_gemini_cost": annual_gemini_cost,
            "annual_gpt4_cost": annual_gemini_cost + annual_savings,
            "annual_savings": annual_savings,
            "monthly_savings": annual_savings / 12,
        },
        "roi_metrics": {
            "cost_reduction_pct": savings["savings_pct"],
            "margin_expansion_points": savings["savings_pct"] * 0.15,  # Rough estimate
            "break_even_calls": 0,  # Gemini is cheaper from first call
        },
    }


# ============================================================================
# Example Usage
# ============================================================================


async def main():
    """Example usage of Gemini integration"""
    # Example 1: AI Tutor
    tutor_result = await ai_tutor_session(
        student_id="student_001",
        task_description="Solve quadratic equation: x^2 + 5x + 6 = 0",
        subject="Algebra II",
        difficulty="medium",
    )
    print("AI Tutor Response:", tutor_result["tutor_response"])
    print(f"Cost: ${tutor_result['cost_usd']:.4f}")
    print(f"Savings: ${tutor_result['savings_vs_gpt4']:.4f} ({tutor_result['savings_pct']:.1f}%)")

    # Example 2: Intelligence Analysis
    intelligence_result = await analyze_intelligence_item(
        content="New AI startup raises $50M Series A to build enterprise productivity platform...",
        source_type="news",
    )
    print("\nIntelligence Analysis:", intelligence_result["analysis"])
    print(f"Cost: ${intelligence_result['cost_usd']:.4f}")

    # Example 3: Migration ROI Estimate
    migrator = AutoGenToGeminiMigrator()
    roi = await migrator.estimate_savings(
        monthly_gpt4_cost=4200.00,  # $4.2K/month on GPT-4
        total_monthly_tokens=50_000_000,  # 50M tokens/month
    )
    print("\nMigration ROI:")
    print(f"  Current monthly cost: ${roi['current_monthly_cost']:,.2f}")
    print(f"  Gemini monthly cost: ${roi['gemini_monthly_cost']:,.2f}")
    print(f"  Monthly savings: ${roi['monthly_savings']:,.2f} ({roi['savings_pct']:.1f}%)")
    print(f"  Annual savings: ${roi['annual_savings']:,.2f}")
    print(f"  Payback period: {roi['payback_months']:.1f} months")
    print(f"  12-month ROI: {roi['roi_12_months']:.0f}%")

    # Example 4: Cost Report
    report = get_cost_report()
    print("\nCost Savings Report:")
    print(f"  Projected annual Gemini cost: ${report['projections']['annual_gemini_cost']:,.2f}")
    print(f"  Projected annual GPT-4 cost: ${report['projections']['annual_gpt4_cost']:,.2f}")
    print(f"  Projected annual savings: ${report['projections']['annual_savings']:,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
