# tool_registry.py - Pydantic AI version
from enum import Enum
from typing import Any, Callable
from app.agent.tools.dateutils import DATEUTILS_TOOLS
# from app.agent.tools.query_engines import QUERY_ENGINE_TOOLS
from app.schemas.agent import AgentMode


class Toolpacks(Enum):
    GENERAL = "general"
    UTILS = "dateutils"
    # QUERY_ENGINES = "query_engines"


class ToolManager:
    toolpacks: dict[Toolpacks, list[Callable[..., Any]]] = {
        Toolpacks.GENERAL: [],
        Toolpacks.UTILS: DATEUTILS_TOOLS,
        # Toolpacks.QUERY_ENGINES: QUERY_ENGINE_TOOLS,
    }
    
    mapping: dict[AgentMode, list[Toolpacks]] = {
        AgentMode.GENERAL: [Toolpacks.GENERAL, Toolpacks.UTILS],
    }
    
    def get_toolpack(self, agent_mode: AgentMode) -> list[Callable[..., Any]]:
        tool_list = []
        
        required_toolpacks = self.mapping.get(agent_mode, [])
        
        for toolpack in required_toolpacks:
            tools = self.toolpacks.get(toolpack, [])
            tool_list.extend(tools)
        
        return tool_list


tool_manager = ToolManager()