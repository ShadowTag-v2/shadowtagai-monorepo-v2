from pydantic import BaseModel, ConfigDict


class AIAgentCreate(BaseModel):
    name: str
    system_prompt: str | None = None


class AIAgentResponse(BaseModel):
    id: int
    name: str
    system_prompt: str | None = None
    workspace_id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str
    model: str = "gemini/gemini-3.1-pro"


class ChatResponse(BaseModel):
    reply: str
