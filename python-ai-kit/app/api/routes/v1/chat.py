import asyncio
import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.agent.factories.workflow_factory import WorkflowAgentFactory
from app.agent.workflows.agent_workflow import user_assistant_graph
from app.agent.workflows.nodes import StartNode
from app.agent.workflows.generation_events import WorkflowState
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    use_mcp: bool = Field(default=settings.mcp_enabled, description="Enable MCP server integration")
    mcp_urls: list[str] | None = Field(default=None, description="List of MCP server URLs")


class ChatResponse(BaseModel):
    response: str
    error: str | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint using workflow with AgentManager factory."""
    logger.info(f"Received chat request: {request.message[:50]}... (MCP: {request.use_mcp})")
    
    try:
        mcp_urls = request.mcp_urls if request.use_mcp else None
        
        manager = await WorkflowAgentFactory.create_manager(
            use_mcp=request.use_mcp,
            mcp_urls=mcp_urls,
            language=settings.default_language
        )
        
        initial_state = WorkflowState()
        
        result = await asyncio.wait_for(
            user_assistant_graph.run(
                start_node=StartNode(),
                state=initial_state,
                deps=manager.to_deps(
                    message=request.message,
                    language=settings.default_language
                )
            ),
            timeout=settings.timeout
        )
        
        logger.info("Chat request processed successfully")
        return ChatResponse(response=result.output)
        
    except asyncio.TimeoutError:
        logger.error("Chat request timeout")
        return ChatResponse(
            response="",
            error="Request timeout. Please try again."
        )
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        return ChatResponse(
            response="",
            error=f"An error occurred: {str(e)}"
        )