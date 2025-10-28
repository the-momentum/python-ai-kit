from dataclasses import dataclass
from pydantic_ai import RunContext

from app.agent.engines.agent_base import BaseAgent, BaseAgentDeps
from app.agent.prompts.worker_prompts import TEXT_TRANSLATOR_INSTRUCTIONS


@dataclass
class TranslatorDeps(BaseAgentDeps):
    """Dependencies for translator with target language."""
    target_language: str = "english"


class SimpleTranslatorWorker(BaseAgent):
    """Simple translator using Pydantic AI, supporting any language as string."""
    
    def __init__(
        self,
        target_language: str = "english",
        system_prompt: str | None = None,
        **kwargs
    ):
        self.target_language = target_language
        
        instructions = system_prompt or TEXT_TRANSLATOR_INSTRUCTIONS
        super().__init__(
            deps_type=TranslatorDeps,
            instructions=instructions,
            **kwargs
        )
        
        @self.agent.instructions
        def add_target_language(ctx: RunContext[TranslatorDeps]) -> str:
            return f"Please translate the following text into {ctx.deps.target_language} language."

    async def translate(
        self, 
        query: str, 
        language: str | None = None
    ) -> str:
        """Translate text to any language.
        
        Args:
            query: Text to translate
            language: Target language (e.g. "polish", "angielski", "español", "中文")
                     If None, uses target_language from constructor
        
        Returns:
            Translated text
        """
        target = language or self.target_language
        
        if self.verbose:
            print(f"Translating to {target}: {query}")
        
        deps = TranslatorDeps(language=self.language, target_language=target)
        
        result = await self.agent.run(
            user_prompt=query,
            deps=deps,
        )
        
        if self.verbose:
            print(f"Translation result: {result.output}")
        
        return str(result.output)