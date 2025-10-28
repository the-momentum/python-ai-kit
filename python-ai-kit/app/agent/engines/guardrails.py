from dataclasses import dataclass
from typing import Type

from app.agent.engines.agent_base import BaseAgent, BaseAgentDeps
from app.agent.prompts.worker_prompts import get_guardrails_instructions


@dataclass
class GuardrailsDeps(BaseAgentDeps):
    """Dependencies for the guardrails."""
    pass


class OutputReformatterWorker(BaseAgent):
    """Output reformatter using Pydantic AI."""
    
    def __init__(self, deps_type: Type[BaseAgentDeps] = GuardrailsDeps, **kwargs):
        super().__init__(deps_type=deps_type, instructions=get_guardrails_instructions, **kwargs)

    async def refformat(self, message: str, api_key: str | None = None, soft_word_limit: int = 250) -> str:
        """Reformat and validate output message.
        
        Args:
            message: Message to reformat
            api_key: API key for the model (unused, kept for compatibility)
            soft_word_limit: Maximum word count
            
        Returns:
            Reformatted message
        """
        if self.verbose:
            print(f"Formatting: \n -------- \n *Input* -> {message}")
        
        deps = GuardrailsDeps(language=self.language)
        
        result = await self.agent.run(
            user_prompt=message,
            deps=deps,
        )
        
        formatted_message = str(result.output)
        
        if self.verbose:
            print(f"\n *Output* -> {formatted_message}")
        
        return formatted_message