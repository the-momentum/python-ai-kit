from pydantic_graph import Graph

from app.agent.workflows.nodes import (
    StartNode,
    ClassifyNode,
    GenerateNode,
    GuardrailsNode,
    TranslateNode,
    RefuseNode,
)


user_assistant_graph = Graph(
    nodes=(StartNode, ClassifyNode, GenerateNode, GuardrailsNode, TranslateNode, RefuseNode),
    name="UserAssistantWorkflow"
)