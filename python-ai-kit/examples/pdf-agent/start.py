import asyncio

from app.agent.factories.pdf_factory import PDFFactory
from app.agent.workflows.pdf_workflow import pdf_workflow
from app.agent.workflows.nodes import StartNode
from app.agent.workflows.generation_events import WorkflowState


async def main():
    # Create manager with your custom agents
    manager = await PDFFactory.create_manager(pdf_path="example.pdf")

    while True:
        result = await pdf_workflow.run(
            start_node=StartNode(),
            state=WorkflowState(),
            deps=manager.to_deps(
                message=input("$ "),
                language="english",
                pdf_path="example.pdf",
                chat_history=[],
            )
        )
        print('\n', result.output, '\n')


asyncio.run(main())