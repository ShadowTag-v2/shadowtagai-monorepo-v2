"""Agent service for orchestrating agent execution."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from ..agents import GrowthEngineerAgent
from ..models.agent_models import (
    Agent,
    AgentExecution,
    AgentResult,
    AgentTool,
    AgentType,
    ExecutionStatus,
)
from .growth_tools import GROWTH_TOOLS


class AgentService:
    """Service for managing and executing agents."""

    def __init__(self, db: Session | None = None):
        """Initialize the agent service.

        Args:
            db: Optional database session

        """
        self.db = db
        self.agents = {
            "growth_engineer": GrowthEngineerAgent(),
        }
        self.tools = GROWTH_TOOLS

    def get_agent(self, agent_id: str) -> Any | None:
        """Get an agent by ID.

        Args:
            agent_id: The agent ID

        Returns:
            The agent instance or None

        """
        return self.agents.get(agent_id)

    def list_agents(self) -> dict[str, Any]:
        """List all available agents.

        Returns:
            Dictionary of agent metadata

        """
        return {agent_id: agent.get_metadata() for agent_id, agent in self.agents.items()}

    async def execute_agent(
        self,
        agent_id: str,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute an agent with a task.

        Args:
            agent_id: The agent ID
            task: The task to execute
            context: Optional context for the task

        Returns:
            The execution result

        """
        # Get the agent
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")

        # Create execution record
        execution_id = str(uuid.uuid4())
        execution = None

        if self.db:
            execution = AgentExecution(
                id=execution_id,
                agent_id=agent_id,
                task=task,
                context=context or {},
                status=ExecutionStatus.RUNNING,
                started_at=datetime.utcnow(),
            )
            self.db.add(execution)
            self.db.commit()

        try:
            # Execute the agent
            result = await agent.execute(task, context)

            # Update execution status
            if self.db and execution:
                execution.status = ExecutionStatus.COMPLETED
                execution.completed_at = datetime.utcnow()
                execution.duration_seconds = int(
                    (execution.completed_at - execution.started_at).total_seconds(),
                )

                # Store result
                agent_result = AgentResult(
                    id=str(uuid.uuid4()),
                    execution_id=execution_id,
                    result_type="text",
                    content=str(result),
                    metadata={},
                )
                self.db.add(agent_result)
                self.db.commit()

            return {
                "execution_id": execution_id,
                "agent_id": agent_id,
                "status": "completed",
                "result": result,
                "error": None,
            }

        except Exception as e:
            # Update execution status to failed
            if self.db and execution:
                execution.status = ExecutionStatus.FAILED
                execution.completed_at = datetime.utcnow()
                execution.error = str(e)
                self.db.commit()

            return {
                "execution_id": execution_id,
                "agent_id": agent_id,
                "status": "failed",
                "result": None,
                "error": str(e),
            }

    def get_execution_history(
        self,
        agent_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Get execution history for an agent.

        Args:
            agent_id: The agent ID
            limit: Maximum number of executions to return
            offset: Number of executions to skip

        Returns:
            Dictionary containing execution history

        """
        if not self.db:
            return {
                "executions": [],
                "total": 0,
                "page": 0,
                "page_size": limit,
            }

        # Query executions
        query = self.db.query(AgentExecution).filter(AgentExecution.agent_id == agent_id)
        total = query.count()
        executions = (
            query.order_by(AgentExecution.started_at.desc()).limit(limit).offset(offset).all()
        )

        return {
            "executions": [
                {
                    "execution_id": execution.id,
                    "agent_id": execution.agent_id,
                    "task": execution.task,
                    "status": execution.status.value,
                    "started_at": execution.started_at.isoformat(),
                    "completed_at": (
                        execution.completed_at.isoformat() if execution.completed_at else None
                    ),
                    "duration_seconds": execution.duration_seconds,
                    "error": execution.error,
                }
                for execution in executions
            ],
            "total": total,
            "page": offset // limit,
            "page_size": limit,
        }

    def get_agent_tools(self, agent_id: str) -> dict[str, Any]:
        """Get available tools for an agent.

        Args:
            agent_id: The agent ID

        Returns:
            Dictionary of tools

        """
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found")

        # Get tools from agent's allowed_tools
        allowed_tools = agent.allowed_tools
        available_tools = {}

        for tool_name in allowed_tools:
            if tool_name in self.tools:
                tool_info = self.tools[tool_name]
                available_tools[tool_name] = {
                    "name": tool_name,
                    "description": tool_info.get("description", ""),
                    "input_schema": tool_info.get("input_schema", {}),
                }

        return {"tools": available_tools}

    def execute_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool directly.

        Args:
            tool_name: The tool name
            args: The tool arguments

        Returns:
            The tool result

        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")

        tool_info = self.tools[tool_name]
        tool_function = tool_info["function"]

        try:
            result = tool_function(args)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def initialize_agents_in_db(self):
        """Initialize agent records in the database."""
        if not self.db:
            return

        for agent_id, agent in self.agents.items():
            # Check if agent already exists
            existing_agent = self.db.query(Agent).filter(Agent.id == agent_id).first()
            if existing_agent:
                continue

            # Create agent record
            metadata = agent.get_metadata()
            agent_record = Agent(
                id=agent_id,
                name=metadata["name"],
                agent_type=AgentType.GROWTH_ENGINEER,  # Map based on agent_id
                description="Growth engineering specialist",
                system_prompt=agent.system_prompt,
                allowed_tools=metadata["allowed_tools"],
                metadata=metadata,
            )
            self.db.add(agent_record)

            # Create tool records
            for tool_name in metadata["allowed_tools"]:
                if tool_name in self.tools:
                    tool_info = self.tools[tool_name]
                    tool_record = AgentTool(
                        id=str(uuid.uuid4()),
                        agent_id=agent_id,
                        tool_name=tool_name,
                        tool_description=tool_info.get("description", ""),
                        input_schema=tool_info.get("input_schema", {}),
                        metadata={},
                    )
                    self.db.add(tool_record)

        self.db.commit()
