from app.agent.factories.workflow_factory import WorkflowAgentFactory
from app.agent.engines.pdf_agent import PDFAgent
from app.agent.agent_manager import AgentManager


class PDFFactory:
    """Factory for your custom workflow."""

    @staticmethod
    async def create_manager(pdf_path: str = "default") -> AgentManager:
        # Start with base agents
        manager = await WorkflowAgentFactory.create_manager()

        # Add your custom agent
        manager.register('pdf_agent', PDFAgent,
                         pdf_path=pdf_path,
                         verbose=True)

        await manager.initialize()
        return manager