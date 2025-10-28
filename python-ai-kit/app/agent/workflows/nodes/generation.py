from dataclasses import dataclass
from pydantic_graph import BaseNode, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from .guardrails import GuardrailsNode


@dataclass
class GenerateNode(BaseNode[WorkflowState, dict, str]):
    """Generate response using main agent."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'GuardrailsNode':
        agent = ctx.deps['agent']
        chat_history = ctx.deps.get('chat_history', [])
        response = await agent.generate_response(
            ctx.state.current_message, 
            chat_history
        )
        ctx.state.generated_response = str(response.output)
        return GuardrailsNode()
