from dataclasses import dataclass

from app.agent.workflows.nodes.pdf_node import PDFNode  # ty: ignore[unresolved-import]
from pydantic_graph import BaseNode, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState


@dataclass
class StartNode(BaseNode[WorkflowState, dict, str]):
    """Init state with user message."""

    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> "PDFNode":
        ctx.state.current_message = ctx.deps["message"]
        return PDFNode()
