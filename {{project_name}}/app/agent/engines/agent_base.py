from abc import ABC
from dataclasses import dataclass
from typing import Any, Type
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.messages import ModelMessage
from pydantic_ai.result import AgentRunResult
from pydantic_ai.mcp import MCPServerStreamableHTTP

from app.config import settings
from app.utils.llm_vendor import set_api_key_for_vendor


@dataclass
class BaseAgentDeps:
    """Base dependencies for agents including language."""
    language: str


class BaseAgent(ABC):
    """Base class for all Pydantic AI agents with common functionality."""
    
    def __init__(
        self,
        llm_vendor: str = settings.ai_provider,
        llm_model: str = settings.model,
        timeout: int = settings.timeout,
        tool_list: list[Any] = None,
        language: str = settings.default_language,
        system_prompt: str | None = None,
        verbose: bool = False,
        api_key: str | None = settings.api_key,
        deps_type: Type[BaseAgentDeps] = BaseAgentDeps,
        output_type: Any = None,
        instructions: str | None = None,
        mcp_urls: list[str] | None = None,
        usage_limits: UsageLimits | None = None,
        **kwargs
    ) -> None:
        self.language = language
        self.verbose = verbose
        self.chat_history: list[ModelMessage] = []
        self.mcp_urls = mcp_urls or []
        self.usage_limits = usage_limits
        
        set_api_key_for_vendor(llm_vendor, api_key)
        
        final_instructions = system_prompt or instructions
        model_string = f"{llm_vendor}:{llm_model}"
        
        toolsets = []
        if self.mcp_urls:
            for mcp_url in self.mcp_urls:
                try:
                    if not mcp_url.startswith(('http://', 'https://')):
                        if self.verbose:
                            print(f"Invalid MCP URL format: {mcp_url}")
                        continue
                    
                    mcp_server = MCPServerStreamableHTTP(mcp_url)
                    toolsets.append(mcp_server)
                    if self.verbose:
                        print(f"MCP server enabled: {mcp_url}")
                except Exception as e:
                    if self.verbose:
                        print(f"Failed to initialize MCP server {mcp_url}: {e}")
                    continue
        
        agent_kwargs = {
            'model': model_string,
            'tools': tool_list or [],
            'deps_type': deps_type,
        }
        if toolsets:
            agent_kwargs['toolsets'] = toolsets
        if final_instructions:
            agent_kwargs['instructions'] = final_instructions
        if output_type is not None:
            agent_kwargs['output_type'] = output_type
            
        self.agent = Agent(**agent_kwargs)
        
        @self.agent.instructions
        def add_language_context(ctx: RunContext[BaseAgentDeps]) -> str:
            return f"Please respond in {ctx.deps.language} language."


    async def generate_response(
        self,
        query: str,
        chat_history: list[ModelMessage],
    ) -> AgentRunResult:
        """Generate response using Pydantic AI agent."""
        deps = BaseAgentDeps(language=self.language)
        
        run_kwargs = {
            'user_prompt': query,
            'message_history': chat_history,
            'deps': deps,
        }
        
        if self.usage_limits:
            run_kwargs['usage_limits'] = self.usage_limits
        
        result = await self.agent.run(**run_kwargs)
        
        if self.verbose:
            print(f"Usage: {result.usage()}")
        
        return result