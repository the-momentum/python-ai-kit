from pydantic_ai import Agent, RunContext
from pydantic_ai.result import RunResult

from app.agent.prompts.worker_prompts import TEXT_TRANSLATOR_INSTRUCTIONS
from app.schemas.language import Language


class SimpleTranslatorWorker:
    """Simple translator using Pydantic AI."""
    
    def __init__(
        self,
        llm_vendor: str = "openai",
        llm_model: str = "gpt-4o-mini",
        timeout: int = 360,
        language: Language = Language.EN,
        system_prompt: str | None = None,
        verbose: bool = False,
    ) -> None:
        self.target_language = language
        self.verbose = verbose
        
        instructions = system_prompt or TEXT_TRANSLATOR_INSTRUCTIONS
        model_string = f"{llm_vendor}:{llm_model}"
        
        self.agent = Agent(
            model=model_string,
            instructions=instructions,
            deps_type=Language,
        )
        
        @self.agent.instructions
        def add_target_language(ctx: RunContext[Language]) -> str:
            return f"Please translate the following text into {ctx.deps.value} language."

    def translate(
        self, 
        query: str, 
        language: Language | None = None
    ) -> str:
        target = language or self.target_language
        
        if self.verbose:
            print(f"Translating to {target.value}: {query}")
        
        result = self.agent.run_sync(
            message=query,
            deps=target,
        )
        
        if self.verbose:
            print(f"Translation result: {result.output}")
        
        return str(result.output)