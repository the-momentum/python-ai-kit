from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from .routing import ClassifyNode


@dataclass
class StartNode(BaseNode[WorkflowState, dict, str]):
    """Init state with user message."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'ClassifyNode':
        ctx.state.current_message = ctx.deps['message']
        return ClassifyNode()
