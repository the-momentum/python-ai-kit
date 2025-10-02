from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState


@dataclass
class GuardrailsNode(BaseNode[WorkflowState, dict, str]):
    """Format and validate generated response."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> End[str]:
        guardrails = ctx.deps['guardrails']
        result = await guardrails.refformat(ctx.state.generated_response)
        return End(result)
