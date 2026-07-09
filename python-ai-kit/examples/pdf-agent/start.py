import asyncio

from app.agent.factories.pdf_factory import PDFFactory  # ty: ignore[unresolved-import]
from app.agent.workflows.pdf_workflow import pdf_workflow  # ty: ignore[unresolved-import]

from app.agent.workflows.generation_events import WorkflowState
from app.agent.workflows.nodes import StartNode


async def main() -> None:
    # Create manager with your custom agents
    manager = await PDFFactory.create_manager(pdf_path="example.pdf")

    while True:
        message = await asyncio.to_thread(input, "$ ")
        result = await pdf_workflow.run(
            inputs=StartNode(),
            state=WorkflowState(),
            deps=manager.to_deps(
                message=message,
                language="english",
                pdf_path="example.pdf",
                chat_history=[],
            ),
        )
        print("\n", result, "\n")


asyncio.run(main())
