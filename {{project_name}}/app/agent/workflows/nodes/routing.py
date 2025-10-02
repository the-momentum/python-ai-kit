from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from app.schemas.agent import TaskType
from .generation import GenerateNode
from .refusal import RefuseNode
from .translation import TranslateNode


@dataclass
class ClassifyNode(BaseNode[WorkflowState, dict, str]):
    """Classify task type."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'GenerateNode | RefuseNode | TranslateNode':        
        router = ctx.deps['router']
        classification = await router.route(ctx.state.current_message)
        
        if classification.route == TaskType.refuse:
            ctx.state.set_refusal(ctx.state.current_message, classification.reasoning)
            return RefuseNode()
        
        ctx.state.task_type = TaskType(classification.route)
        
        if classification.route == TaskType.translate:
            return TranslateNode()
        
        return GenerateNode()
