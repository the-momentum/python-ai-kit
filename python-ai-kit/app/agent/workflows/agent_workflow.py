from pydantic_graph import GraphBuilder

from app.agent.workflows.generation_events import WorkflowState
from app.agent.workflows.nodes import (
    ClassifyNode,
    GenerateNode,
    GuardrailsNode,
    RefuseNode,
    StartNode,
    TranslateNode,
)

builder = GraphBuilder(
    name="UserAssistantWorkflow",
    state_type=WorkflowState,
    deps_type=dict,
    output_type=str,
)
builder.add(builder.edge_from(builder.start_node).to(StartNode))
for node in (StartNode, ClassifyNode, GenerateNode, GuardrailsNode, TranslateNode, RefuseNode):
    builder.add(builder.node(node))

user_assistant_graph = builder.build()
