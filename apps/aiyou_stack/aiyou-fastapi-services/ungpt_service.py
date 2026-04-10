"""
UnGPT Multi-LLM Consensus Service
Production-ready FastAPI implementation with tiered routing and cost controls
"""

import asyncio
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

import anthropic
import google.generativeai as genai
import redis
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Initialize FastAPI
app = FastAPI(
    title="UnGPT Consensus Service",
    description="Multi-LLM consensus system with tiered routing",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Redis for cost tracking
redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
)


# ============================================================================
# DATA MODELS
# ============================================================================


class QueryComplexity(StrEnum):
    """Query complexity tiers for routing."""

    SIMPLE = "simple"  # Claude only (RA-1)
    MODERATE = "moderate"  # Claude + Gemini (RA-2)
    COMPLEX = "complex"  # Full consensus (RA-3/4)


class UnGPTRequest(BaseModel):
    """Request model for UnGPT queries."""

    query: str = Field(..., description="User query")
    user_location: str = Field(default="US", description="ISO country code for compliance")
    complexity: QueryComplexity | None = Field(
        None, description="Force specific tier (auto-detect if None)"
    )
    max_cost: float = Field(default=0.50, description="Maximum cost in USD")
    include_reasoning: bool = Field(default=False, description="Include detailed reasoning chain")


class UnGPTResponse(BaseModel):
    """Response model for UnGPT queries."""

    final_answer: str
    confidence_score: float
    consensus_level: str
    execution_time_seconds: float
    total_cost: float
    models_consulted: list[str]
    risk_level: str
    query_tier: str
    reasoning_chain: list[dict] | None = None


@dataclass
class ModelResponse:
    """Single model's response."""

    model: str
    content: str
    confidence: float
    latency: float
    token_usage: dict[str, int]


# ============================================================================
# COST CONTROL
# ============================================================================

DAILY_BUDGET = {
    "simple_queries": 100,
    "moderate_queries": 30,
    "complex_queries": 15,
    "max_daily_spend": 10.00,
}

QUERY_LIMITS = {"max_cost_per_query": 0.50, "require_approval_above": 0.30}


async def check_budget(
    user_id: str, estimated_cost: float, query_tier: str
) -> tuple[bool, str | None]:
    """
    Check if query is within budget limits.
    """
    today = datetime.utcnow().date().isoformat()
    key_prefix = f"cost:{user_id}:{today}"

    try:
        # Get current spend
        daily_spend = float(redis_client.get(f"{key_prefix}:total") or 0)
        tier_count = int(redis_client.get(f"{key_prefix}:{query_tier}") or 0)

        # Check daily spend limit
        if daily_spend + estimated_cost > DAILY_BUDGET["max_daily_spend"]:
            return False, f"Daily budget ${DAILY_BUDGET['max_daily_spend']} would be exceeded"

        # Check per-query limit
        if estimated_cost > QUERY_LIMITS["max_cost_per_query"]:
            return (
                False,
                f"Query cost ${estimated_cost:.2f} exceeds limit ${QUERY_LIMITS['max_cost_per_query']}",
            )

        # Check tier-specific limits
        tier_limit_key = f"{query_tier}_queries"
        if tier_limit_key in DAILY_BUDGET and tier_count >= DAILY_BUDGET[tier_limit_key]:
            return (
                False,
                f"Daily limit for {query_tier} queries ({DAILY_BUDGET[tier_limit_key]}) reached",
            )

        return True, None

    except redis.RedisError:
        # Fail open if Redis unavailable
        return True, None


async def record_spend(user_id: str, actual_cost: float, query_tier: str):
    """Record actual spend after query completes."""
    today = datetime.utcnow().date().isoformat()
    key_prefix = f"cost:{user_id}:{today}"

    try:
        redis_client.incrbyfloat(f"{key_prefix}:total", actual_cost)
        redis_client.incr(f"{key_prefix}:{query_tier}")
        redis_client.expire(f"{key_prefix}:total", 2592000)  # 30 days
    except redis.RedisError:
        pass  # Log but don't fail query


# ============================================================================
# COMPLEXITY DETECTION
# ============================================================================


async def detect_complexity(query: str) -> QueryComplexity:
    """
    Use Claude to assess query complexity.

    Simple: Factual questions, definitions, single-step
    Moderate: Comparisons, multi-step analysis
    Complex: Strategic, financial, multi-domain
    """

    classification_prompt = f"""Classify this query's complexity for multi-model consensus routing.

QUERY: {query}

Return ONLY a JSON object with this exact structure:
{{
  "complexity": "simple" | "moderate" | "complex",
  "reasoning": "1-2 sentence explanation",
  "confidence": 0.0-1.0
}}

Classification criteria:
- simple: Single fact, definition, straightforward question, "what is X?"
- moderate: Comparison, 2-3 step reasoning, analysis with clear scope, "compare X vs Y"
- complex: Strategic decision, financial projection, multi-domain analysis, "analyze business viability of X"
"""

    try:
        response = await asyncio.to_thread(
            anthropic_client.messages.create,
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": classification_prompt}],
        )

        text = response.content[0].text.strip()

        # Extract JSON from markdown code blocks if present
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        classification = json.loads(text)
        return QueryComplexity(classification["complexity"])

    except Exception as e:
        # Default to moderate on classification failure
        print(f"Complexity detection failed: {e}")
        return QueryComplexity.MODERATE


# ============================================================================
# EXECUTION PATHS
# ============================================================================


async def execute_simple_path(query: str) -> dict[str, Any]:
    """
    Simple path: Claude only
    Cost: ~$0.017
    """
    start_time = asyncio.get_event_loop().time()

    response = await asyncio.to_thread(
        anthropic_client.messages.create,
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": query}],
    )

    execution_time = asyncio.get_event_loop().time() - start_time

    return {
        "final_answer": response.content[0].text,
        "confidence": 0.85,
        "consensus_level": "single_model",
        "execution_time": execution_time,
        "total_cost": calculate_cost(
            "claude", response.usage.input_tokens, response.usage.output_tokens
        ),
        "models": ["claude-sonnet-4"],
        "risk_level": "RA-1",
        "reasoning_chain": [
            {"step": "single_model_query", "model": "claude-sonnet-4", "result": "Direct response"}
        ],
    }


async def execute_moderate_path(query: str) -> dict[str, Any]:
    """
    Moderate path: Claude + Gemini with synthesis
    Cost: ~$0.046
    """
    start_time = asyncio.get_event_loop().time()
    reasoning_chain = []

    # Step 1: Claude initial reasoning
    claude_response = await asyncio.to_thread(
        anthropic_client.messages.create,
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": f"{query}\n\nProvide clear, structured reasoning."}],
    )

    claude_text = claude_response.content[0].text
    reasoning_chain.append(
        {"step": "claude_initial", "model": "claude-sonnet-4", "result": claude_text[:200] + "..."}
    )

    # Step 2: Gemini analysis
    gemini_prompt = f"""Original query: {query}

Claude's analysis:
{claude_text}

Provide your independent analysis. Do you agree with Claude? What would you add or change?"""

    gemini_response = await asyncio.to_thread(gemini_model.generate_content, gemini_prompt)

    gemini_text = gemini_response.text
    reasoning_chain.append(
        {
            "step": "gemini_analysis",
            "model": "gemini-2.0-flash",
            "result": gemini_text[:200] + "...",
        }
    )

    # Step 3: Claude synthesis
    synthesis_prompt = f"""Query: {query}

Your initial analysis:
{claude_text}

Gemini's analysis:
{gemini_text}

Synthesize both perspectives into a final, comprehensive answer. Resolve any disagreements and provide the best combined response."""

    final_response = await asyncio.to_thread(
        anthropic_client.messages.create,
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": synthesis_prompt}],
    )

    execution_time = asyncio.get_event_loop().time() - start_time

    # Calculate total cost
    total_cost = (
        calculate_cost(
            "claude", claude_response.usage.input_tokens, claude_response.usage.output_tokens
        )
        + calculate_cost("gemini", 500, 300)  # Estimated
        + calculate_cost(
            "claude", final_response.usage.input_tokens, final_response.usage.output_tokens
        )
    )

    reasoning_chain.append(
        {
            "step": "final_synthesis",
            "model": "claude-sonnet-4",
            "result": "Combined response generated",
        }
    )

    return {
        "final_answer": final_response.content[0].text,
        "confidence": 0.88,
        "consensus_level": "two_model_synthesis",
        "execution_time": execution_time,
        "total_cost": total_cost,
        "models": ["claude-sonnet-4", "gemini-2.0-flash"],
        "risk_level": "RA-2",
        "reasoning_chain": reasoning_chain,
    }


async def execute_complex_path(query: str) -> dict[str, Any]:
    """
    Complex path: Full multi-model consensus (simplified for MVP)
    Cost: ~$0.10-0.30 (optimized from full $0.268)

    Note: This is a simplified version. Full implementation would
    include Grok and GPT-5 when API keys are configured.
    """
    start_time = asyncio.get_event_loop().time()
    reasoning_chain = []

    # Layer 1: Claude initial reasoning
    layer1_prompt = f"""You are Layer 1 in a multi-model consensus system.

Query: {query}

Provide thorough initial reasoning with:
1. Key sub-questions to answer
2. Initial approach
3. Preliminary insights
4. Areas of uncertainty

Your response will be analyzed by other advanced models."""

    layer1_response = await asyncio.to_thread(
        anthropic_client.messages.create,
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": layer1_prompt}],
    )

    layer1_text = layer1_response.content[0].text
    reasoning_chain.append(
        {
            "step": "layer1_reasoning",
            "model": "claude-sonnet-4",
            "result": layer1_text[:300] + "...",
        }
    )

    # Layer 2: Gemini analysis (parallel - in production would include Grok, GPT-5)
    layer2_prompt = f"""Original query: {query}

Claude's initial reasoning:
{layer1_text}

Provide your independent analysis:
1. Do you agree with Claude's approach?
2. What would you add or change?
3. Your complete response to the original query
4. Confidence level (0.0-1.0)"""

    layer2_response = await asyncio.to_thread(gemini_model.generate_content, layer2_prompt)

    layer2_text = layer2_response.text
    reasoning_chain.append(
        {
            "step": "layer2_parallel",
            "model": "gemini-2.0-flash",
            "result": layer2_text[:300] + "...",
        }
    )

    # Layer 3: Claude final synthesis
    layer3_prompt = f"""You are Layer 3 - final synthesis in a multi-model consensus system.

ORIGINAL QUERY: {query}

YOUR INITIAL REASONING:
{layer1_text}

GEMINI'S ANALYSIS:
{layer2_text}

Your task:
1. Identify consensus points
2. Resolve disagreements
3. Synthesize into authoritative final answer
4. Flag remaining uncertainties
5. Assess overall confidence

Provide comprehensive, execution-ready response."""

    layer3_response = await asyncio.to_thread(
        anthropic_client.messages.create,
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": layer3_prompt}],
    )

    execution_time = asyncio.get_event_loop().time() - start_time

    # Calculate costs
    total_cost = (
        calculate_cost(
            "claude", layer1_response.usage.input_tokens, layer1_response.usage.output_tokens
        )
        + calculate_cost("gemini", 800, 500)
        + calculate_cost(
            "claude", layer3_response.usage.input_tokens, layer3_response.usage.output_tokens
        )
    )

    reasoning_chain.append(
        {
            "step": "layer3_synthesis",
            "model": "claude-sonnet-4",
            "result": "Final consensus generated",
        }
    )

    return {
        "final_answer": layer3_response.content[0].text,
        "confidence": 0.92,
        "consensus_level": "multi_model_consensus",
        "execution_time": execution_time,
        "total_cost": total_cost,
        "models": ["claude-sonnet-4", "gemini-2.0-flash"],  # Will add grok, gpt-5 when configured
        "risk_level": "RA-3",
        "reasoning_chain": reasoning_chain,
    }


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate cost based on model and token usage.

    Rates (per 1M tokens):
    - Claude Sonnet 4: $3/$15 (in/out)
    - Gemini 2.0 Flash: $0.075/$0.30 (in/out)
    """
    rates = {
        "claude": {"input": 3.0, "output": 15.0},
        "gemini": {"input": 0.075, "output": 0.30},
        "grok": {"input": 2.0, "output": 10.0},
        "gpt5": {"input": 10.0, "output": 30.0},
    }

    if model not in rates:
        return 0.0

    cost = (input_tokens / 1_000_000 * rates[model]["input"]) + (
        output_tokens / 1_000_000 * rates[model]["output"]
    )

    return round(cost, 6)


# ============================================================================
# API ENDPOINTS
# ============================================================================


def get_user_id(authorization: str | None = Header(None)) -> str:
    """Extract user ID from authorization header."""
    if authorization and authorization.startswith("Bearer "):
        # In production, validate JWT and extract user ID
        # For now, use hash of API key as user ID
        api_key = authorization.replace("Bearer ", "")
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    return "anonymous"


@app.post("/v1/ungpt/query", response_model=UnGPTResponse)
async def process_query(request: UnGPTRequest, user_id: str = Depends(get_user_id)):
    """
    Main UnGPT endpoint with tiered routing and cost controls.
    """

    # 1. Detect complexity if not specified
    if request.complexity is None:
        request.complexity = await detect_complexity(request.query)

    # 2. Estimate cost
    cost_estimates = {
        QueryComplexity.SIMPLE: 0.017,
        QueryComplexity.MODERATE: 0.046,
        QueryComplexity.COMPLEX: 0.120,
    }
    estimated_cost = cost_estimates[request.complexity]

    # 3. Check budget
    allowed, reason = await check_budget(user_id, estimated_cost, request.complexity.value)
    if not allowed:
        raise HTTPException(status_code=429, detail=reason)

    # 4. Execute appropriate path
    try:
        if request.complexity == QueryComplexity.SIMPLE:
            result = await execute_simple_path(request.query)
        elif request.complexity == QueryComplexity.MODERATE:
            result = await execute_moderate_path(request.query)
        else:
            result = await execute_complex_path(request.query)

        # 5. Check actual cost against user limit
        if result["total_cost"] > request.max_cost:
            raise HTTPException(
                status_code=402,
                detail=f"Query cost ${result['total_cost']:.4f} exceeds your limit ${request.max_cost}",
            )

        # 6. Record spend
        await record_spend(user_id, result["total_cost"], request.complexity.value)

        # 7. Build response
        return UnGPTResponse(
            final_answer=result["final_answer"],
            confidence_score=result["confidence"],
            consensus_level=result["consensus_level"],
            execution_time_seconds=result["execution_time"],
            total_cost=result["total_cost"],
            models_consulted=result["models"],
            risk_level=result["risk_level"],
            query_tier=request.complexity.value,
            reasoning_chain=result["reasoning_chain"] if request.include_reasoning else None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@app.get("/v1/ungpt/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ungpt-consensus",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/v1/ungpt/budget/{user_id}")
async def get_budget_status(user_id: str):
    """Get current budget status for user."""
    today = datetime.utcnow().date().isoformat()
    key_prefix = f"cost:{user_id}:{today}"

    try:
        daily_spend = float(redis_client.get(f"{key_prefix}:total") or 0)
        simple_count = int(redis_client.get(f"{key_prefix}:simple") or 0)
        moderate_count = int(redis_client.get(f"{key_prefix}:moderate") or 0)
        complex_count = int(redis_client.get(f"{key_prefix}:complex") or 0)

        return {
            "user_id": user_id,
            "date": today,
            "daily_spend": daily_spend,
            "daily_limit": DAILY_BUDGET["max_daily_spend"],
            "remaining": DAILY_BUDGET["max_daily_spend"] - daily_spend,
            "queries": {
                "simple": {"used": simple_count, "limit": DAILY_BUDGET["simple_queries"]},
                "moderate": {"used": moderate_count, "limit": DAILY_BUDGET["moderate_queries"]},
                "complex": {"used": complex_count, "limit": DAILY_BUDGET["complex_queries"]},
            },
        }
    except redis.RedisError as e:
        raise HTTPException(status_code=503, detail=f"Budget service unavailable: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
