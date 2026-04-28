# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Database Expert Agent - AI-powered database optimization specialist

This agent uses Claude Agent SDK to provide expert database analysis,
query optimization, schema design, and performance tuning recommendations.
"""

from collections.abc import AsyncGenerator
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, query, tool

from app.tools.database_tools import (
    IndexOptimizer,
    PerformanceAnalyzer,
    QueryAnalyzer,
    SchemaAnalyzer,
)


# Define custom tools for the Database Expert agent
@tool
def analyze_sql_query(sql_query: str) -> dict[str, Any]:
    """Analyze a SQL query for optimization opportunities.

    Args:
        sql_query: The SQL query string to analyze

    Returns:
        Dictionary containing query analysis, issues, and optimization suggestions

    """
    analyzer = QueryAnalyzer()
    analysis = analyzer.analyze_query(sql_query)

    return {
        "success": True,
        "analysis": analysis,
        "summary": f"Query type: {analysis['query_type']}, "
        f"Complexity: {analysis['complexity']}, "
        f"Issues found: {len(analysis['issues'])}",
    }


@tool
def suggest_query_indexes(sql_query: str, schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Suggest indexes for a SQL query.

    Args:
        sql_query: The SQL query to analyze
        schema: Optional schema information

    Returns:
        Dictionary with index suggestions

    """
    optimizer = IndexOptimizer()
    suggestions = optimizer.suggest_indexes(sql_query, schema)

    return {
        "success": True,
        "suggestions": suggestions,
        "count": len(suggestions),
        "summary": f"Found {len(suggestions)} index optimization opportunities",
    }


@tool
def analyze_database_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Analyze database schema for optimization opportunities.

    Args:
        schema: Database schema information in the format:
            {
                "table_name": {
                    "columns": [{"name": "col1", "type": "VARCHAR(255)", "nullable": True}],
                    "indexes": [{"name": "idx_name", "columns": ["col1"]}],
                    "row_count": 1000000
                }
            }

    Returns:
        Dictionary with schema analysis and recommendations

    """
    analyzer = SchemaAnalyzer()
    analysis = analyzer.analyze_schema(schema)

    return {
        "success": True,
        "analysis": analysis,
        "summary": f"Analyzed {len(schema)} tables, "
        f"Found {len(analysis['issues'])} issues, "
        f"{len(analysis['recommendations'])} recommendations",
    }


@tool
def estimate_query_performance(
    sql_query: str,
    row_count: int,
    has_indexes: bool = True,
) -> dict[str, Any]:
    """Estimate query execution time and provide performance recommendations.

    Args:
        sql_query: SQL query to analyze
        row_count: Number of rows in the table(s)
        has_indexes: Whether appropriate indexes exist

    Returns:
        Performance estimation and recommendations

    """
    query_analyzer = QueryAnalyzer()
    perf_analyzer = PerformanceAnalyzer()

    analysis = query_analyzer.analyze_query(sql_query)
    estimation = perf_analyzer.estimate_query_time(analysis["complexity"], row_count, has_indexes)

    return {
        "success": True,
        "estimation": estimation,
        "query_analysis": analysis,
        "summary": f"Estimated time: {estimation['estimated_time_readable']} - "
        f"{estimation['recommendation']}",
    }


class DatabaseExpert:
    """Database Expert Agent - specializes in database optimization and performance tuning"""

    SYSTEM_PROMPT = """You are a Database Expert - a specialized AI assistant focused on database optimization,
performance tuning, and scalable schema design.

Your expertise includes:
- Query optimization: Analyzing and improving SQL queries that take too long
- Schema design: Creating efficient database schemas that scale to millions of records
- Performance tuning: Identifying bottlenecks and suggesting performance improvements
- Index optimization: Recommending appropriate indexes for better query performance
- Database architecture: Advising on database design patterns and best practices
- Migration planning: Helping design and optimize database migrations

You have access to specialized tools for analyzing queries, schemas, and performance metrics.

When helping users:
1. Ask clarifying questions about their database environment (PostgreSQL, MySQL, MongoDB, etc.)
2. Use the available tools to analyze their queries and schemas
3. Provide specific, actionable recommendations with examples
4. Explain the reasoning behind your suggestions
5. Consider both performance and maintainability in your recommendations
6. Prioritize the most impactful optimizations first

Always be practical and consider real-world constraints like:
- Production system limitations
- Migration complexity
- Development team capacity
- Business requirements

Your goal is to fix those queries that take 30 seconds and design schemas that scale to millions.
"""

    def __init__(self, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize the Database Expert agent

        Args:
            model: Claude model to use for the agent

        """
        self.model = model
        self.tools = [
            analyze_sql_query,
            suggest_query_indexes,
            analyze_database_schema,
            estimate_query_performance,
        ]

    async def chat(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Chat with the Database Expert agent

        Args:
            user_message: User's message/question
            conversation_history: Optional conversation history

        Yields:
            Response chunks from the agent

        """
        # Build conversation messages
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})

        # Configure agent options
        options = ClaudeAgentOptions(
            system_prompt=self.SYSTEM_PROMPT,
            model=self.model,
            tools=self.tools,
            max_tokens=4096,
        )

        # Stream responses from the agent
        async for message in query(prompt=user_message, options=options):
            yield message

    async def analyze_query(self, sql_query: str) -> dict[str, Any]:
        """Analyze a SQL query with expert recommendations

        Args:
            sql_query: SQL query to analyze

        Returns:
            Complete analysis with expert recommendations

        """
        result = {"query": sql_query, "analysis": {}, "recommendations": []}

        # Perform technical analysis
        analyzer = QueryAnalyzer()
        result["analysis"] = analyzer.analyze_query(sql_query)

        # Get index suggestions
        optimizer = IndexOptimizer()
        result["index_suggestions"] = optimizer.suggest_indexes(sql_query)

        # Build expert prompt for Claude
        prompt = f"""Analyze this SQL query and provide expert optimization recommendations:

Query:
```sql
{sql_query}
```

Technical Analysis:
- Query Type: {result["analysis"]["query_type"]}
- Complexity Score: {result["analysis"]["complexity"]}
- Issues: {", ".join(result["analysis"]["issues"]) if result["analysis"]["issues"] else "None detected"}
- Joins: {result["analysis"]["joins"]["count"]} ({", ".join(result["analysis"]["joins"]["types"]) if result["analysis"]["joins"]["types"] else "none"})
- Subqueries: {result["analysis"]["subqueries"]}

Please provide:
1. Overall assessment of the query
2. Specific optimization recommendations
3. Potential performance impact of each recommendation
4. Example optimized query if applicable
"""

        # Get expert analysis from Claude
        options = ClaudeAgentOptions(
            system_prompt=self.SYSTEM_PROMPT,
            model=self.model,
            max_tokens=2048,
        )

        expert_analysis = ""
        async for message in query(prompt=prompt, options=options):
            expert_analysis += message

        result["expert_recommendations"] = expert_analysis

        return result

    async def design_schema(
        self,
        requirements: str,
        expected_scale: str | None = None,
    ) -> dict[str, Any]:
        """Get expert schema design recommendations

        Args:
            requirements: Description of schema requirements
            expected_scale: Expected data scale (e.g., "millions of users", "billions of events")

        Returns:
            Schema design recommendations

        """
        prompt = f"""Design an optimized database schema for the following requirements:

Requirements:
{requirements}

{f"Expected Scale: {expected_scale}" if expected_scale else ""}

Please provide:
1. Recommended table structure with columns and data types
2. Primary and foreign key relationships
3. Recommended indexes for performance
4. Partitioning strategy if applicable for scale
5. Any additional optimization considerations
"""

        options = ClaudeAgentOptions(
            system_prompt=self.SYSTEM_PROMPT,
            model=self.model,
            max_tokens=4096,
        )

        design_recommendations = ""
        async for message in query(prompt=prompt, options=options):
            design_recommendations += message

        return {
            "requirements": requirements,
            "scale": expected_scale,
            "design": design_recommendations,
        }


# Convenience function to create Database Expert instance
def create_database_expert(model: str = "claude-sonnet-4-5-20250929") -> DatabaseExpert:
    """Create a Database Expert agent instance

    Args:
        model: Claude model to use

    Returns:
        DatabaseExpert instance

    """
    return DatabaseExpert(model=model)
