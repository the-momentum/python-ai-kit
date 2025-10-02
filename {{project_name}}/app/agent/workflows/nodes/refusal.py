from dataclasses import dataclass
from pydantic_graph import BaseNode, End, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from app.agent.static.default_msgs import REFUSAL_GENERIC


@dataclass
class RefuseNode(BaseNode[WorkflowState, dict, str]):
    """Returning refusal with a reason."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> End[str]:
        language = ctx.deps.get('language', 'english')
        response = REFUSAL_GENERIC[language].format(
            refusal_reason=ctx.state.refusal_info.refusal_reason
        )
        return End(response)
