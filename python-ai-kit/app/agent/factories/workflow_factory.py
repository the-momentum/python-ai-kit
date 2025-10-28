from app.agent.agent_manager import AgentManager
from app.agent.engines.routers import GenericRouter
from app.agent.engines.guardrails import OutputReformatterWorker
from app.agent.engines.react_agent import ReasoningAgent
from app.agent.engines.translators import SimpleTranslatorWorker
from app.config import settings
from pydantic_ai import UsageLimits


class WorkflowAgentFactory:
    """Factory for creating configured AgentManager instances."""
    
    @staticmethod
    async def create_manager(
        use_mcp: bool = False, 
        mcp_urls: list[str] | None = None,
        language: str = "english"
    ) -> AgentManager:
        """Create AgentManager with all workflow agents including translator.
        
        Args:
            use_mcp: Whether to enable MCP servers
            mcp_urls: List of MCP server URLs (if None and use_mcp=True, uses settings.mcp_urls)
            language: Language for all agents
            
        Returns:
            Configured AgentManager instance
        """
        manager = AgentManager()
        
        final_mcp_urls = mcp_urls if mcp_urls is not None else (settings.mcp_urls if use_mcp else [])
        
        usage_limits = None
        if any([settings.max_output_tokens, settings.max_input_tokens, settings.max_requests]):
            usage_limits = UsageLimits(
                output_tokens_limit=settings.max_output_tokens,
                input_tokens_limit=settings.max_input_tokens,
                request_limit=settings.max_requests,
            )
        
        manager.register('router', GenericRouter,
            verbose=settings.debug_mode,
            api_key=settings.api_key)
        
        manager.register('agent', ReasoningAgent,
            verbose=settings.debug_mode,
            api_key=settings.api_key,
            language=language,
            mcp_urls=final_mcp_urls,
            usage_limits=usage_limits)
        
        manager.register('guardrails', OutputReformatterWorker,
            verbose=settings.debug_mode,
            api_key=settings.api_key,
            language=language,
            usage_limits=usage_limits)
        
        manager.register('translator', SimpleTranslatorWorker,
            verbose=settings.debug_mode,
            target_language=language,
            usage_limits=usage_limits)
        
        await manager.initialize()
        return manager
