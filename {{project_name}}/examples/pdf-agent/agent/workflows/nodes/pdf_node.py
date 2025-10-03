from dataclasses import dataclass

from pydantic_ai.messages import ModelResponse, ModelRequest
from pydantic_graph import BaseNode, GraphRunContext, End

from app.agent.workflows.generation_events import WorkflowState
from .guardrails import GuardrailsNode


@dataclass
class PDFNode(BaseNode[WorkflowState, dict, str]):
    """Node that uses your custom agent."""

    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'GuardrailsNode':
        pdf_agent = ctx.deps['pdf_agent']
        pdf_path = ctx.deps.get('pdf_path', 'example.pdf')
        chat_history = ctx.deps.get('chat_history', [])

        result = await pdf_agent.process_request(
            ctx.state.current_message,
            chat_history,
            pdf_path
        )

        ctx.state.generated_response = str(result.output)

        # finish workflow
        return GuardrailsNode()