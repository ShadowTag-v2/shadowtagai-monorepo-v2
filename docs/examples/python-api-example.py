"""
Python API Usage Examples for Wealth Acceleration Agent

This file demonstrates how to interact with the Wealth Acceleration FastAPI service
using Python's requests library and async/await patterns.
"""

import asyncio
import json

import aiohttp
import requests

# =============================================================================
# Helper Functions
# =============================================================================

def stream_response(url: str, data: dict):
    """
    Stream response from API endpoint and print in real-time

    Args:
        url: API endpoint URL
        data: Request payload
    """
    response = requests.post(url, json=data, stream=True)
    response.raise_for_status()

    for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
        if chunk:
            print(chunk, end="", flush=True)
    print("\n")


async def async_stream_response(url: str, data: dict):
    """
    Async version of stream_response

    Args:
        url: API endpoint URL
        data: Request payload
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response.raise_for_status()
            async for chunk in response.content.iter_any():
                if chunk:
                    print(chunk.decode('utf-8'), end="", flush=True)
    print("\n")


# =============================================================================
# Example 1: Basic Monetization Strategy Analysis
# =============================================================================

def example1_monetization_strategy():
    """Complete monetization strategy analysis"""
    print("=== Example 1: Monetization Strategy Analysis ===\n")

    url = "http://localhost:8000/analyze/monetization"
    data = {
        "business_context": {
            "niche": "SaaS founders",
            "current_monthly_revenue": 15000,
            "audience_size": 50000,
            "engagement_level": "high",
            "revenue_streams": ["consulting", "courses"],
            "platforms": ["Twitter", "LinkedIn", "Newsletter"],
            "additional_context": "Launching a new cohort-based course next month"
        },
        "focus_areas": ["pricing", "conversion", "LTV"]
    }

    stream_response(url, data)


# =============================================================================
# Example 2: Funnel Analysis
# =============================================================================

def example2_funnel_analysis():
    """Analyze conversion funnel"""
    print("\n=== Example 2: Funnel Analysis ===\n")

    url = "http://localhost:8000/analyze/funnel"
    data = {
        "business_context": {
            "niche": "Marketing consultants",
            "current_monthly_revenue": 8000,
            "audience_size": 20000,
            "engagement_level": "medium"
        },
        "funnel_stages": [
            {
                "name": "Blog/Content",
                "visitors": 15000,
                "conversions": 3000,
                "revenue": 0
            },
            {
                "name": "Lead Magnet Page",
                "visitors": 3000,
                "conversions": 1200,
                "revenue": 0
            },
            {
                "name": "Email Nurture",
                "visitors": 1200,
                "conversions": 300,
                "revenue": 0
            },
            {
                "name": "Sales Page",
                "visitors": 300,
                "conversions": 45,
                "revenue": 22365
            },
            {
                "name": "Customers",
                "visitors": 45,
                "conversions": 0,
                "revenue": 0
            }
        ]
    }

    stream_response(url, data)


# =============================================================================
# Example 3: Pricing Evaluation
# =============================================================================

def example3_pricing_evaluation():
    """Evaluate pricing strategy"""
    print("\n=== Example 3: Pricing Evaluation ===\n")

    url = "http://localhost:8000/analyze/pricing"
    data = {
        "business_context": {
            "niche": "Fitness coaches",
            "current_monthly_revenue": 12000
        },
        "product_type": "course",
        "current_price": 197,
        "cost_to_deliver": 25,
        "monthly_customers": 25,
        "market_position": "mid-market"
    }

    stream_response(url, data)


# =============================================================================
# Example 4: Revenue Projections
# =============================================================================

def example4_revenue_projections():
    """Calculate revenue projections"""
    print("\n=== Example 4: Revenue Projections ===\n")

    url = "http://localhost:8000/analyze/projections"
    data = {
        "business_context": {
            "niche": "Content creators",
            "current_monthly_revenue": 5000,
            "audience_size": 25000,
            "engagement_level": "high"
        },
        "current_monthly_revenue": 5000,
        "current_audience_size": 25000,
        "monthly_audience_growth": 15,
        "current_conversion_rate": 1.5,
        "projection_months": 12
    }

    stream_response(url, data)


# =============================================================================
# Example 5: Customer LTV Calculation
# =============================================================================

def example5_ltv_calculation():
    """Calculate customer lifetime value"""
    print("\n=== Example 5: LTV Calculation ===\n")

    url = "http://localhost:8000/analyze/ltv"
    data = {
        "business_context": {
            "niche": "E-commerce store owners",
            "current_monthly_revenue": 20000,
            "revenue_streams": ["courses", "software", "membership"]
        },
        "average_order_value": 297,
        "purchase_frequency": 3.5,
        "customer_lifespan": 2.5,
        "gross_margin": 85
    }

    stream_response(url, data)


# =============================================================================
# Example 6: Market Opportunity Assessment
# =============================================================================

def example6_opportunity_assessment():
    """Assess market opportunities"""
    print("\n=== Example 6: Opportunity Assessment ===\n")

    url = "http://localhost:8000/analyze/opportunities"
    data = {
        "niche": "Indie hackers",
        "audience_size": 15000,
        "engagement": "high",
        "current_revenue": 3000,
        "potential_revenue_streams": [
            "courses",
            "coaching",
            "software",
            "membership",
            "affiliate",
            "sponsorship"
        ]
    }

    stream_response(url, data)


# =============================================================================
# Example 7: Custom Analysis
# =============================================================================

def example7_custom_analysis():
    """Custom strategic analysis"""
    print("\n=== Example 7: Custom Analysis ===\n")

    url = "http://localhost:8000/analyze"
    data = {
        "business_context": {
            "niche": "B2B SaaS",
            "current_monthly_revenue": 50000,
            "audience_size": 100000,
            "engagement_level": "medium",
            "revenue_streams": ["SaaS subscriptions", "enterprise contracts", "consulting"],
            "additional_context": """
                Current situation:
                - MRR: $50K (80% from small businesses, 20% from enterprise)
                - Churn: 8% monthly
                - CAC: $450
                - LTV: $1,200
                - Team: 8 people
                - Main challenge: Want to move upmarket to enterprise
            """
        },
        "prompt": """
            I want to transition from serving small businesses ($99-299/month)
            to enterprise ($2K-10K/month).

            I need you to:
            1. Analyze whether this transition makes sense
            2. Design a dual-track monetization strategy
            3. Map out product/positioning changes needed
            4. Calculate the economics
            5. Identify biggest risks
            6. Give me a 90-day roadmap
            7. Challenge me with ONE thing to do this week

            Be brutally honest about whether this is the right move.
        """
    }

    stream_response(url, data)


# =============================================================================
# Example 8: Async Usage with aiohttp
# =============================================================================

async def example8_async_usage():
    """Demonstrate async API usage"""
    print("\n=== Example 8: Async API Usage ===\n")

    url = "http://localhost:8000/analyze/monetization"
    data = {
        "business_context": {
            "niche": "Online educators",
            "current_monthly_revenue": 7500,
            "audience_size": 30000,
            "engagement_level": "medium"
        }
    }

    await async_stream_response(url, data)


# =============================================================================
# Example 9: Batch Processing Multiple Requests
# =============================================================================

async def example9_batch_processing():
    """Process multiple analysis requests concurrently"""
    print("\n=== Example 9: Batch Processing ===\n")

    tasks = []

    # Create multiple analysis tasks
    analyses = [
        {
            "url": "http://localhost:8000/analyze/pricing",
            "data": {
                "product_type": "course",
                "current_price": 497,
                "cost_to_deliver": 50,
                "monthly_customers": 20,
                "market_position": "premium"
            }
        },
        {
            "url": "http://localhost:8000/analyze/ltv",
            "data": {
                "average_order_value": 497,
                "purchase_frequency": 2,
                "customer_lifespan": 3,
                "gross_margin": 90
            }
        }
    ]

    # Run analyses concurrently
    for analysis in analyses:
        tasks.append(async_stream_response(analysis["url"], analysis["data"]))

    await asyncio.gather(*tasks)


# =============================================================================
# Example 10: Error Handling
# =============================================================================

def example10_error_handling():
    """Demonstrate error handling"""
    print("\n=== Example 10: Error Handling ===\n")

    url = "http://localhost:8000/analyze/pricing"

    # Invalid data (missing required fields)
    invalid_data = {
        "product_type": "course",
        # Missing other required fields
    }

    try:
        response = requests.post(url, json=invalid_data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")


# =============================================================================
# Example 11: Health Check and Service Discovery
# =============================================================================

def example11_service_discovery():
    """Check service health and available endpoints"""
    print("\n=== Example 11: Service Discovery ===\n")

    # Health check
    health_response = requests.get("http://localhost:8000/health")
    print("Health Check:", health_response.json())
    print()

    # Get available endpoints
    root_response = requests.get("http://localhost:8000/")
    print("Available Endpoints:", json.dumps(root_response.json(), indent=2))


# =============================================================================
# Example 12: Complete Workflow
# =============================================================================

def example12_complete_workflow():
    """
    Complete workflow: Analyze → Identify Opportunities → Project Growth
    """
    print("\n=== Example 12: Complete Analysis Workflow ===\n")

    business_context = {
        "niche": "Digital marketing agencies",
        "current_monthly_revenue": 25000,
        "audience_size": 75000,
        "engagement_level": "high",
        "revenue_streams": ["consulting", "done-for-you"],
        "platforms": ["LinkedIn", "Newsletter", "Podcast"]
    }

    print("\n--- Phase 1: Monetization Strategy ---\n")
    stream_response(
        "http://localhost:8000/analyze/monetization",
        {"business_context": business_context}
    )

    print("\n--- Phase 2: Opportunity Assessment ---\n")
    stream_response(
        "http://localhost:8000/analyze/opportunities",
        {
            "niche": business_context["niche"],
            "audience_size": business_context["audience_size"],
            "engagement": business_context["engagement_level"],
            "current_revenue": business_context["current_monthly_revenue"],
            "potential_revenue_streams": [
                "courses",
                "software",
                "membership",
                "affiliate"
            ]
        }
    )

    print("\n--- Phase 3: Revenue Projections ---\n")
    stream_response(
        "http://localhost:8000/analyze/projections",
        {
            "business_context": business_context,
            "current_monthly_revenue": business_context["current_monthly_revenue"],
            "current_audience_size": business_context["audience_size"],
            "monthly_audience_growth": 8,
            "current_conversion_rate": 1.2,
            "projection_months": 12
        }
    )


# =============================================================================
# Main execution
# =============================================================================

def main():
    """Run examples"""
    print("Wealth Acceleration Agent - Python API Examples")
    print("=" * 60)
    print()
    print("Make sure the FastAPI server is running:")
    print("  cd src && uvicorn api.routes:app --reload --port 8000")
    print()
    print("=" * 60)
    print()

    # Run synchronous examples
    # Uncomment the ones you want to try:

    # example1_monetization_strategy()
    # example2_funnel_analysis()
    # example3_pricing_evaluation()
    # example4_revenue_projections()
    # example5_ltv_calculation()
    # example6_opportunity_assessment()
    # example7_custom_analysis()
    # example10_error_handling()
    # example11_service_discovery()
    # example12_complete_workflow()

    # Run async examples
    # asyncio.run(example8_async_usage())
    # asyncio.run(example9_batch_processing())

    print("\nTo run these examples:")
    print("1. Start the FastAPI server: cd src && uvicorn api.routes:app --reload")
    print("2. Set ANTHROPIC_API_KEY environment variable")
    print("3. Uncomment the example you want to run")
    print("4. Run: python docs/examples/python-api-example.py")


if __name__ == "__main__":
    main()
