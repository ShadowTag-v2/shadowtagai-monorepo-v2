"""Response models for the Database Expert API"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class QueryAnalysisResponse(BaseModel):
    """Response model for query analysis"""

    success: bool
    query: str
    analysis: dict[str, Any]
    index_suggestions: list[dict[str, Any]] | None = None
    expert_recommendations: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "query": "SELECT * FROM users WHERE email LIKE '%@gmail.com'",
                    "analysis": {
                        "query_type": "SELECT",
                        "complexity": 45,
                        "issues": [
                            "Using SELECT * - retrieves all columns",
                            "Leading wildcard in LIKE - prevents index usage",
                        ],
                        "suggestions": [
                            "Specify only needed columns to reduce data transfer",
                            "Avoid leading wildcards or use full-text search",
                        ],
                    },
                    "expert_recommendations": "This query has several performance issues...",
                }
            ]
        }
    )


class SchemaAnalysisResponse(BaseModel):
    """Response model for schema analysis"""

    success: bool
    analysis: dict[str, Any]
    summary: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "analysis": {
                        "tables": {
                            "users": {
                                "name": "users",
                                "recommendations": [
                                    "Add index on users.email for better lookup performance",
                                ],
                                "issues": [],
                                "stats": {
                                    "column_count": 10,
                                    "index_count": 2,
                                    "row_count": 5000000,
                                    "estimated_size_mb": 512.5,
                                },
                            },
                        },
                    },
                    "summary": "Analyzed 1 tables, Found 0 issues, 1 recommendations",
                }
            ]
        }
    )


class SchemaDesignResponse(BaseModel):
    """Response model for schema design"""

    success: bool
    requirements: str
    scale: str | None
    design: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "requirements": "E-commerce platform with users, products, orders",
                    "scale": "10 million users",
                    "design": "Here's the recommended schema design...",
                }
            ]
        }
    )


class IndexSuggestionResponse(BaseModel):
    """Response model for index suggestions"""

    success: bool
    suggestions: list[dict[str, Any]]
    count: int
    summary: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "suggestions": [
                        {
                            "type": "single_column",
                            "columns": ["status"],
                            "reason": "Used in WHERE clause",
                            "priority": "high",
                        },
                    ],
                    "count": 1,
                    "summary": "Found 1 index optimization opportunities",
                }
            ]
        }
    )


class PerformanceEstimationResponse(BaseModel):
    """Response model for performance estimation"""

    success: bool
    estimation: dict[str, Any]
    query_analysis: dict[str, Any]
    summary: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "estimation": {
                        "estimated_time_ms": 250.5,
                        "estimated_time_readable": "250.50ms",
                        "recommendation": "Acceptable performance",
                    },
                    "query_analysis": {"query_type": "SELECT", "complexity": 25},
                    "summary": "Estimated time: 250.50ms - Acceptable performance",
                }
            ]
        }
    )


class ChatResponse(BaseModel):
    """Response model for chat"""

    success: bool
    message: str
    response: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "message": "How can I optimize this query?",
                    "response": "Based on the query you provided, here are my recommendations...",
                }
            ]
        }
    )


class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = False
    error: str
    details: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": False,
                    "error": "Invalid SQL query",
                    "details": "Query parsing failed at line 1",
                }
            ]
        }
    )


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    agent: str

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"status": "healthy", "version": "0.1.0", "agent": "Database Expert"}]
        }
    )
