# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""FastAPI integration example for Vertex AI Agents
Demonstrates how to build an API service using the agents
"""

import os
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent_registry import get_agent, get_agents_by_category, get_all_agents, search_agents

# Initialize FastAPI app
app = FastAPI(
    title="Vertex AI Agents API",
    description="API service for accessing and using Vertex AI Agents",
    version="1.0.0",
)


# Request/Response models
class ChatRequest(BaseModel):
    agent_id: str
    message: str
    temperature: float | None = None
    max_tokens: int | None = None


class ChatResponse(BaseModel):
    agent_id: str
    agent_name: str
    response: str


class AgentInfo(BaseModel):
    id: str
    name: str
    category: str
    description: str
    icon: str
    capabilities: list[str]
    example_prompts: list[str]


class SearchRequest(BaseModel):
    keyword: str


# API Endpoints


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Vertex AI Agents API",
        "version": "1.0.0",
        "total_agents": len(get_all_agents()),
        "endpoints": {
            "agents": "/agents",
            "agent_detail": "/agents/{agent_id}",
            "categories": "/categories",
            "search": "/search",
            "chat": "/chat",
        },
    }


@app.get("/agents", response_model=list[AgentInfo])
async def list_agents():
    """List all available agents"""
    agents = get_all_agents()
    return [
        AgentInfo(
            id=agent.id,
            name=agent.name,
            category=agent.category,
            description=agent.description,
            icon=agent.icon,
            capabilities=agent.capabilities,
            example_prompts=agent.example_prompts,
        )
        for agent in agents
    ]


@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent_detail(agent_id: str):
    """Get details for a specific agent"""
    agent = get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    return AgentInfo(
        id=agent.id,
        name=agent.name,
        category=agent.category,
        description=agent.description,
        icon=agent.icon,
        capabilities=agent.capabilities,
        example_prompts=agent.example_prompts,
    )


@app.get("/categories/{category_id}", response_model=list[AgentInfo])
async def get_category_agents(category_id: str):
    """Get all agents in a specific category"""
    agents = get_agents_by_category(category_id)
    if not agents:
        raise HTTPException(status_code=404, detail=f"No agents found in category '{category_id}'")

    return [
        AgentInfo(
            id=agent.id,
            name=agent.name,
            category=agent.category,
            description=agent.description,
            icon=agent.icon,
            capabilities=agent.capabilities,
            example_prompts=agent.example_prompts,
        )
        for agent in agents
    ]


@app.post("/search", response_model=list[AgentInfo])
async def search(request: SearchRequest):
    """Search for agents by keyword"""
    results = search_agents(request.keyword)
    return [
        AgentInfo(
            id=agent.id,
            name=agent.name,
            category=agent.category,
            description=agent.description,
            icon=agent.icon,
            capabilities=agent.capabilities,
            example_prompts=agent.example_prompts,
        )
        for agent in results
    ]


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with a specific agent"""
    # Get the agent
    agent = get_agent(request.agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_id}' not found")

    # In a real implementation, you would call Vertex AI here
    # For now, return a mock response
    mock_response = (
        f"This is a mock response from {agent.name}. "
        f"In production, this would use Vertex AI with the agent's system prompt."
    )

    return ChatResponse(agent_id=agent.id, agent_name=agent.name, response=mock_response)


@app.get("/categories")
async def list_categories():
    """List all available categories"""
    from agent_registry import get_all_categories

    categories = get_all_categories()
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "icon": cat.icon,
            "agent_count": len(cat.agents),
        }
        for cat in categories
    ]


# Run the app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
