from dataclasses import dataclass
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from app.schemas.agent import TaskType
from app.agent.static.default_msgs import REFUSAL_GENERIC


@dataclass
class StartNode(BaseNode[WorkflowState, dict, str]):
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'ClassifyNode':
        ctx.state.current_message = ctx.deps['message']
        return ClassifyNode()


@dataclass
class ClassifyNode(BaseNode[WorkflowState, dict, str]):
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'GenerateNode | RefuseNode':
        router = ctx.deps['router']
        classification = await router.route(ctx.state.current_message)
        
        if classification.route == TaskType.refuse:
            ctx.state.set_refusal(ctx.state.current_message, classification.reasoning)
            return RefuseNode()
        
        ctx.state.task_type = TaskType(classification.route)
        return GenerateNode()


@dataclass
class GenerateNode(BaseNode[WorkflowState, dict, str]):
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'GuardrailsNode':
        agent = ctx.deps['agent']
        response = await agent.generate_response(ctx.state.current_message, [])
        ctx.state.generated_response = str(response.output)
        return GuardrailsNode()


@dataclass
class GuardrailsNode(BaseNode[WorkflowState, dict, str]):
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> End[str]:
        guardrails = ctx.deps['guardrails']
        result = await guardrails.refformat(ctx.state.generated_response)
        return End(result)


@dataclass
class RefuseNode(BaseNode[WorkflowState, dict, str]):
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> End[str]:
        language = ctx.deps.get('language', 'english')
        response = REFUSAL_GENERIC[language].format(
            refusal_reason=ctx.state.refusal_info.refusal_reason
        )
        return End(response)


user_assistant_graph = Graph(
    nodes=(StartNode, ClassifyNode, GenerateNode, GuardrailsNode, RefuseNode),
    name="UserAssistantWorkflow"
)