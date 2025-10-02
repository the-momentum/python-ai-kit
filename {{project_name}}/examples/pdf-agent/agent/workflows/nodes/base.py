from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from app.agent.workflows.nodes.pdf_node import PDFNode

@dataclass
class StartNode(BaseNode[WorkflowState, dict, str]):
    """Init state with user message."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'PDFNode':
        ctx.state.current_message = ctx.deps['message']
        ctx.state.pdf_path = ctx.deps['pdf_path']
        ctx.state.chat_history = ctx.deps['chat_history']
        return PDFNode()
