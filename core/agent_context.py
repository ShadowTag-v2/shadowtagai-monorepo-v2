import contextvars
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid

@dataclass
class AgentContext:
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cwd_override: Optional[str] = None
    role: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)

# The global context variable that holds the current agent's context.
# Since contextvars are natively supported by asyncio, any async sub-tasks
# spawned by an agent will automatically inherit its specific ContextVar state.
current_agent_context: contextvars.ContextVar[AgentContext] = contextvars.ContextVar(
    "current_agent_context", default=AgentContext()
)

def get_agent_context() -> AgentContext:
    """Returns the current agent's context."""
    return current_agent_context.get()

def set_agent_context(context: AgentContext) -> contextvars.Token:
    """Sets the current agent's context and returns a token to reset it later."""
    return current_agent_context.set(context)

def reset_agent_context(token: contextvars.Token) -> None:
    """Resets the context back to its previous state."""
    current_agent_context.reset(token)

def get_current_cwd() -> Optional[str]:
    """Helper to get the current CWD for the active agent."""
    return current_agent_context.get().cwd_override

def set_current_cwd(path: str) -> None:
    """Updates the CWD for the active agent."""
    ctx = current_agent_context.get()
    ctx.cwd_override = path
    # ContextVars hold references, so modifying the dataclass updates the state
    # for all coroutines sharing this context.
