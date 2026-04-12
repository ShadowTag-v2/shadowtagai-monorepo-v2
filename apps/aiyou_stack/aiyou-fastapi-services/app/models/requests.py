"""
Request models for the Database Expert API
"""

from typing import Any

from pydantic import BaseModel, Field


class QueryAnalysisRequest(BaseModel):
    """Request model for query analysis"""

    sql_query: str = Field(..., description="SQL query to analyze", min_length=1)
    row_count: int | None = Field(None, description="Number of rows in table(s)", ge=0)
    has_indexes: bool = Field(True, description="Whether appropriate indexes exist")

    class Config:
        json_schema_extra = {
            "example": {
                "sql_query": "SELECT * FROM users WHERE email LIKE '%@gmail.com'",
                "row_count": 1000000,
                "has_indexes": False,
            }
        }


class SchemaAnalysisRequest(BaseModel):
    """Request model for schema analysis"""

    schema: dict[str, Any] = Field(..., description="Database schema to analyze")

    class Config:
        json_schema_extra = {
            "example": {
                "schema": {
                    "users": {
                        "columns": [
                            {"name": "id", "type": "BIGINT", "primary_key": True},
                            {"name": "email", "type": "VARCHAR(255)", "nullable": False},
                            {"name": "created_at", "type": "TIMESTAMP", "nullable": False},
                        ],
                        "indexes": [{"name": "idx_email", "columns": ["email"]}],
                        "row_count": 5000000,
                    }
                }
            }
        }


class SchemaDesignRequest(BaseModel):
    """Request model for schema design"""

    requirements: str = Field(..., description="Schema requirements description", min_length=10)
    expected_scale: str | None = Field(None, description="Expected data scale")
    database_type: str | None = Field("postgresql", description="Target database type")

    class Config:
        json_schema_extra = {
            "example": {
                "requirements": "E-commerce platform with users, products, orders, and reviews",
                "expected_scale": "10 million users, 100 million orders",
                "database_type": "postgresql",
            }
        }


class IndexSuggestionRequest(BaseModel):
    """Request model for index suggestions"""

    sql_query: str = Field(..., description="SQL query to analyze for indexes", min_length=1)
    schema: dict[str, Any] | None = Field(None, description="Optional schema information")

    class Config:
        json_schema_extra = {
            "example": {
                "sql_query": "SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id WHERE o.status = 'pending' ORDER BY o.created_at DESC"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat with Database Expert"""

    message: str = Field(..., description="User message", min_length=1)
    conversation_history: list[dict[str, str]] | None = Field(
        None, description="Conversation history"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "How can I optimize a query that's doing a full table scan on a 10 million row table?",
                "conversation_history": [
                    {"role": "user", "content": "Hello, I need help with database optimization"},
                    {
                        "role": "assistant",
                        "content": "Hello! I'd be happy to help with database optimization. What specific issues are you experiencing?",
                    },
                ],
            }
        }


class PerformanceEstimationRequest(BaseModel):
    """Request model for performance estimation"""

    sql_query: str = Field(..., description="SQL query to estimate", min_length=1)
    row_count: int = Field(..., description="Number of rows in table(s)", ge=1)
    has_indexes: bool = Field(True, description="Whether appropriate indexes exist")

    class Config:
        json_schema_extra = {
            "example": {
                "sql_query": "SELECT COUNT(*) FROM orders WHERE status = 'pending' AND created_at > NOW() - INTERVAL '30 days'",
                "row_count": 50000000,
                "has_indexes": True,
            }
        }
