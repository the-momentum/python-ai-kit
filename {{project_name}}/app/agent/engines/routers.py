from dataclasses import dataclass
from typing import Type
from pydantic import BaseModel

from app.agent.engines.agent_base import BaseAgent, BaseAgentDeps
from app.agent.prompts.worker_prompts import get_router_instructions
from app.config import settings


@dataclass
class RouterDeps(BaseAgentDeps):
    """Dependencies for the router."""
    pass


class RoutingResponse(BaseModel):
    route: int
    reasoning: str


class GenericRouter(BaseAgent):
    """Generic message routing using Pydantic AI structured output."""
    
    def __init__(self, routing_prompt: str | None = None, deps_type: Type[BaseAgentDeps] = RouterDeps, **kwargs):
        instructions = routing_prompt or get_router_instructions
        super().__init__(deps_type=deps_type, output_type=RoutingResponse, instructions=instructions, **kwargs)

    async def route(self, message: str, api_key: str | None = None, logging: bool = False) -> RoutingResponse:
        """Route message and return classification.

        Args:
            message: Message to classify
            api_key: API key for the model (unused, kept for compatibility)
            logging: Whether to log the routing decision

        Returns:
            RoutingResponse with route and reasoning
        """
        deps = RouterDeps(language=self.language)
        result = await self.agent.run(user_prompt=message, deps=deps)
        routing = result.output

        if logging or self.verbose:
            print(routing.route, routing.reasoning)

        return routing