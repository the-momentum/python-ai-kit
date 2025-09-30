from dataclasses import dataclass

from app.agent.engines.agent_base import BaseAgent, BaseAgentDeps
from app.agent.prompts.agent_prompts import get_instructions_for_mode
from app.schemas.agent import AgentMode


@dataclass
class ReasoningAgentDeps(BaseAgentDeps):
    """Dependencies for the reasoning agent."""
    pass


class ReasoningAgent(BaseAgent):
    """Pydantic AI equivalent of LlamaIndex ReActAgent."""
    
    def __init__(
        self, 
        deps_type: type[BaseAgentDeps] = ReasoningAgentDeps,
        **kwargs
    ):
        instructions = get_instructions_for_mode(AgentMode.GENERAL)
        super().__init__(
            deps_type=deps_type, 
            instructions=instructions,
            **kwargs
        )
