import asyncio
from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.tools import FunctionTool
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import BasicMCPClient
from llama_index.tools.mcp.base import McpToolSpec
from app.config import settings


class AgentManager:
    def __init__(self):
        self.agent: FunctionAgent | None = None
        self.agent_context: Context | None = None
        self.llm: OpenAI | None = None
        self.tools: list[FunctionTool] | None = None
        self._initialized = False
    
    def get_local_client(self) -> BasicMCPClient:
        return BasicMCPClient(settings.mcp_url)
    
    async def initialize(self, model: str = settings.model, system_prompt: str | None = None):
        if self._initialized:
            return
        
        self.llm = OpenAI(model=model, api_key=settings.api_key)
        self.tools = await self._get_tools()
        
        if system_prompt is None:
            system_prompt = "You are an AI assistant to help the user as best as you can. You can use the tools provided to you to help the user."
        
        self.agent = await self._create_agent(system_prompt)
        self.agent_context = Context(self.agent)
        self._initialized = True
    
    async def _get_tools(self) -> list[FunctionTool]:
        mcp_tool = McpToolSpec(client=self.get_local_client())
        tools = await mcp_tool.to_tool_list_async()
        
        # import pprint
        # print("\ntools[0].metadata.fn_schema.model_json_schema()")
        # print("=" * 50)
        # pprint.pprint(tools[0].metadata.fn_schema.model_json_schema())
        
        return tools
    
    async def _create_agent(self, system_prompt: str) -> FunctionAgent:
        return FunctionAgent(
            name="Agent",
            description="An agent that can work with Our Database software.",
            tools=self.tools,
            llm=self.llm,
            system_prompt=system_prompt,
        )
    
    async def handle_message(self, message: str, verbose: bool = False) -> str:
        if not self._initialized:
            raise RuntimeError("Agent not initialized. Call initialize() first.")
        
        if self.agent is None or self.agent_context is None:
            raise RuntimeError("Agent or context is None")
        
        handler = self.agent.run(message, ctx=self.agent_context)
        
        async for event in handler.stream_events():
            if verbose and isinstance(event, ToolCall):
                print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
            elif verbose and isinstance(event, ToolCallResult):
                print(f"Tool {event.tool_name} returned {event.tool_output}")
        
        response = await handler
        return str(response)
    
    def is_initialized(self) -> bool:
        return self._initialized
    
    def get_tools_info(self) -> list[dict]:
        if not self._initialized or self.tools is None:
            return []
        
        return [
            {
                "name": tool.metadata.name,
                "description": tool.metadata.description,
                "schema": tool.metadata.fn_schema.model_json_schema() if hasattr(tool.metadata, 'fn_schema') else None
            }
            for tool in self.tools
        ]


agent_manager = AgentManager()


async def get_tools() -> list[FunctionTool]:
    if not agent_manager.is_initialized():
        await agent_manager.initialize()
    return agent_manager.tools or []

async def get_agent(llm: OpenAI, tools: list[FunctionTool], system_prompt: str) -> FunctionAgent:
    if not agent_manager.is_initialized():
        await agent_manager.initialize()
    return agent_manager.agent or agent_manager._create_agent(system_prompt)

async def handle_user_message(message_content: str, agent: FunctionAgent, agent_context: Context, verbose: bool = False) -> str:
    return await agent_manager.handle_message(message_content, verbose)


async def main():
    await agent_manager.initialize()
    
    while True:
        user_input = input("Enter your message: ")
        if user_input == "exit":
            break
        print("User: ", user_input)
        response = await agent_manager.handle_message(user_input, verbose=True)
        print("Agent: ", response)


if __name__ == "__main__":
    asyncio.run(main())