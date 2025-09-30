from app.agent.engines.react_agent import ReasoningAgent
from app.config import settings


class AgentManager:
    """Centralized agent manager for both GUI and API usage."""
    
    def __init__(self):
        self.agent: ReasoningAgent | None = None
        self._initialized = False
        self._current_mcp_setting = None
    
    async def initialize(self, use_mcp: bool | None = None, mcp_url: str | None = None):
        """Initialize the agent with optional MCP configuration."""
        if self._initialized and self._current_mcp_setting == use_mcp:
            return
        
        if use_mcp is None:
            use_mcp = settings.mcp_enabled
        
        final_mcp_url = mcp_url if mcp_url is not None else (settings.mcp_url if use_mcp else None)
        
        self.agent = ReasoningAgent(
            verbose=settings.debug_mode,
            api_key=settings.api_key,
            language=settings.default_language,
            mcp_url=final_mcp_url
        )
        
        self._initialized = True
        self._current_mcp_setting = use_mcp
    
    async def handle_message(self, message: str) -> str:
        """Handle a message and return the response."""
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        result = await self.agent.generate_response(
            query=message,
            chat_history=self.agent.chat_history
        )
        
        from pydantic_ai.messages import UserPromptPart, TextPart, ModelRequest, ModelResponse
        user_message = ModelRequest(parts=[UserPromptPart(content=message)])
        self.agent.chat_history.append(user_message)
        
        assistant_message = ModelResponse(parts=[TextPart(content=result.output)])
        self.agent.chat_history.append(assistant_message)
        
        return result.output
    
    def is_initialized(self) -> bool:
        """Check if the agent is initialized."""
        return self._initialized
    
    async def close(self):
        """Close the agent and clear chat history."""
        if self.agent:
            self.agent.chat_history = []
        self._initialized = False
        self._current_mcp_setting = None
    
    def get_agent(self) -> ReasoningAgent  | None:
        """Get the current agent instance."""
        return self.agent


agent_manager = AgentManager()
