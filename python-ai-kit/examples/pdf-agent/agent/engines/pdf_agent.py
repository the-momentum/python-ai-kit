from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic_ai import RunContext
from pydantic_ai.messages import ModelRequest, ModelResponse

from app.agent.engines.agent_base import BaseAgent, BaseAgentDeps
from app.agent.tools.get_pdf import get_pdf_text


@dataclass
class PDFAgentDeps(BaseAgentDeps):
    """Custom dependencies for your agent."""
    pdf_path: Path | str = "example.pdf",


class PDFAgent(BaseAgent):
    """Your custom agent with specific functionality."""

    def __init__(self, custom_setting: str = "default", **kwargs):
        self.custom_setting = custom_setting
        super().__init__(
            deps_type=PDFAgentDeps,
            instructions="You are a specialized agent that extracts information from PDF files.",
            **kwargs
        )

        @self.agent.tool
        def get_pdf(ctx: RunContext[PDFAgentDeps]) -> dict[str, Any]:
            """
                Get pdf from path specified by user
            """
            return get_pdf_text(pdf_path=ctx.deps.pdf_path)


        @self.agent.instructions
        def add_custom_context(ctx: RunContext[PDFAgentDeps]) -> str:
            return f"Use the pdf path: {ctx.deps.pdf_path}"

    async def process_request(self,
                              query: str,
                              chat_history: list[ModelRequest | ModelResponse],
                              pdf_path: str):
        """Your custom processing logic."""
        deps = PDFAgentDeps(language=self.language, pdf_path=pdf_path)
        result = await self.agent.run(user_prompt=query, message_history=chat_history, deps=deps)
        return result

