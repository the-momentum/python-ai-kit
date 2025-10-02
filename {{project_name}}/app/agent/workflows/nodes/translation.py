from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from .guardrails import GuardrailsNode


@dataclass
class TranslateNode(BaseNode[WorkflowState, dict, str]):
    """Node that translates text to target language."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'GuardrailsNode':
        
        translator = ctx.deps['translator']
        target_lang = ctx.deps.get('target_language', 'english')
        
        result = await translator.translate(
            ctx.state.current_message,
            target_lang
        )
        
        ctx.state.generated_response = result
        return GuardrailsNode()
