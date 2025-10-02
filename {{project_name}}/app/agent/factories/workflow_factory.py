from app.agent.agent_manager import AgentManager
from app.agent.engines.routers import GenericRouter
from app.agent.engines.guardrails import OutputReformatterWorker
from app.agent.engines.react_agent import ReasoningAgent
from app.agent.engines.translators import SimpleTranslatorWorker
from app.config import settings


class WorkflowAgentFactory:
    """Factory for creating configured AgentManager instances."""
    
    @staticmethod
    async def create_manager(
        use_mcp: bool = False, 
        mcp_url: str | None = None,
        target_language: str = "english"
    ) -> AgentManager:
        """Create AgentManager with all workflow agents including translator.
        
        Args:
            use_mcp: Whether to enable MCP server
            mcp_url: MCP server URL (if None and use_mcp=True, uses settings.mcp_url)
            target_language: Default target language for translator
            
        Returns:
            Configured AgentManager instance
        """
        manager = AgentManager()
        
        final_mcp_url = mcp_url if mcp_url is not None else (settings.mcp_url if use_mcp else None)
        
        manager.register('router', GenericRouter,
            verbose=settings.debug_mode,
            api_key=settings.api_key)
        
        manager.register('agent', ReasoningAgent,
            verbose=settings.debug_mode,
            api_key=settings.api_key,
            language=settings.default_language,
            mcp_url=final_mcp_url)
        
        manager.register('guardrails', OutputReformatterWorker,
            verbose=settings.debug_mode,
            api_key=settings.api_key,
            language=settings.default_language)
        
        manager.register('translator', SimpleTranslatorWorker,
            verbose=settings.debug_mode,
            target_language=target_language)
        
        await manager.initialize()
        return manager
