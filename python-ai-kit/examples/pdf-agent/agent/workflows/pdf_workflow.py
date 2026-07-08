from pydantic_graph import GraphBuilder

from app.agent.workflows.generation_events import WorkflowState
from app.agent.workflows.nodes import (
    GuardrailsNode,
    PDFNode,  # ty: ignore[unresolved-import]
    StartNode,
)

builder = GraphBuilder(
    name="PDFWorkflow",
    state_type=WorkflowState,
    deps_type=dict,
    output_type=str,
)
builder.add(builder.edge_from(builder.start_node).to(StartNode))
for node in (StartNode, PDFNode, GuardrailsNode):
    builder.add(builder.node(node))

pdf_workflow = builder.build()
