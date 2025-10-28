from app.agent.engines.routers import GenericRouter
from app.agent.engines.guardrails import OutputReformatterWorker
from app.agent.agent_manager import agent_manager
from app.config import settings


async def get_workflow_dependencies(mcp_url: str | None = None):
    """Get dependencies needed for the workflow"""
    use_mcp = mcp_url is not None
    await agent_manager.initialize(use_mcp=use_mcp, mcp_url=mcp_url)
    
    router = GenericRouter(
        verbose=settings.debug_mode,
        api_key=settings.api_key
    )
    guardrails = OutputReformatterWorker(
        verbose=settings.debug_mode,
        api_key=settings.api_key,
        language=settings.default_language
    )
    
    return {
        'router': router,
        'agent': agent_manager.get_agent(),
        'guardrails': guardrails,
        'language': settings.default_language
    }
