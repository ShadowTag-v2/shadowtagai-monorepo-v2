# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field, field_validator


class CodeExecutionRequest(BaseModel):
    """Request model for code execution."""

    code: str = Field(
        ...,
        description="Python code to execute",
        min_length=1,
        max_length=10000,
    )
    timeout: int | None = Field(
        default=None,
        description="Execution timeout in seconds (uses default if not specified)",
        ge=1,
        le=60,
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate code input."""
        dangerous_patterns = [
            "import os",
            "import sys",
            "import subprocess",
            "__import__",
            "eval(",
            "exec(",
            "compile(",
        ]

        v_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in v_lower:
                raise ValueError(f"Code contains potentially dangerous pattern: {pattern}")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "print('Hello, World!')\nresult = 2 + 2\nprint(f'Result: {result}')",
                    "timeout": 10,
                },
            ],
        },
    }


class CodeExecutionResponse(BaseModel):
    """Response model for code execution."""

    success: bool = Field(..., description="Whether execution was successful")
    output: str = Field(default="", description="Standard output from execution")
    error: str | None = Field(
        default=None,
        description="Error message if execution failed",
    )
    execution_time: float = Field(
        default=0.0,
        description="Execution time in seconds",
    )
    memory_used_mb: float = Field(
        default=0.0,
        description="Memory used in megabytes",
    )
    cpu_percent: float = Field(
        default=0.0,
        description="CPU usage percentage",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "output": "Hello, World!\nResult: 4\n",
                    "error": None,
                    "execution_time": 0.05,
                    "memory_used_mb": 12.5,
                    "cpu_percent": 15.2,
                },
            ],
        },
    }


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy", description="Service health status")
    version: str = Field(..., description="Application version")
    sandbox_enabled: bool = Field(..., description="Whether sandboxing is enabled")


class SandboxStatsResponse(BaseModel):
    """Sandbox statistics response."""

    total_executions: int = Field(
        default=0,
        description="Total number of executions",
    )
    successful_executions: int = Field(
        default=0,
        description="Number of successful executions",
    )
    failed_executions: int = Field(
        default=0,
        description="Number of failed executions",
    )
    average_execution_time: float = Field(
        default=0.0,
        description="Average execution time in seconds",
    )
    average_memory_usage: float = Field(
        default=0.0,
        description="Average memory usage in MB",
    )
