from typing import Any
from pydantic_ai import RunContext
from app.schemas.agent import AgentMode


TEXT_AGENT_PRIMING = """
You are a specialized, intelligent AI assistant designated to help users.
"""
 
TEXT_AGENT_RULES = """
## Additional Rules
- The answer should be detailed but concise and cover each aspect of the user question and consider relevant user context.
- Prefer to use specific answers and ask user for clarification when needed.
- Remember to use ALL the relevant information you receive from tools in your responses.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.
- You MUST use a tool to answer factual questions. However, if the user's message is a simple greeting, farewell, expression of gratitude, casual small talk, or conversational remark, respond naturally without using a tool.
"""

TEXT_REACTAGENT_GUIDANCE = """
When using tools to answer questions:
1. First, think about what information you need
2. Use appropriate tools to gather that information
3. Analyze the results from tools
4. Provide a comprehensive answer based on the tool results

Remember to always use tools for factual questions and incorporate all relevant tool information in your responses.
"""


def get_general_instructions() -> str:
    """Get general agent instructions."""
    return TEXT_AGENT_PRIMING + TEXT_REACTAGENT_GUIDANCE + TEXT_AGENT_RULES


def get_language_instruction(ctx: RunContext[Any]) -> str:
    """Add language context to instructions.
    
    Args:
        ctx: RunContext with access to dependencies and other context
    """
    language = "english"
    
    if hasattr(ctx.deps, 'language'):
        language = ctx.deps.language
    elif isinstance(ctx.deps, dict) and 'language' in ctx.deps:
        language = ctx.deps['language']
    
    return f"The current conversation language is: {language}. Please respond in {language} language."


def get_instructions_for_mode(mode: AgentMode) -> str:
    """Get static instructions for specific agent mode.
    
    Args:
        mode: The agent mode to get instructions for
        
    Returns:
        Static instructions string for the mode
    """
    mode_instructions = {
        AgentMode.GENERAL: get_general_instructions(),
    }
    
    return mode_instructions.get(mode, get_general_instructions())