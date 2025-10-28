from pydantic_graph import Graph

from app.agent.workflows.nodes import (
    StartNode,
    PDFNode,
    GuardrailsNode
)
# from app.agent.workflows.nodes.guardrails import GuardrailsNode


pdf_workflow = Graph(
    nodes=(StartNode, PDFNode, GuardrailsNode),
    name="PDFWorkflow"
)