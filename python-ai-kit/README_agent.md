# Agent Framework

A flexible, extensible framework for building AI agent workflows using Pydantic AI and pydantic-graph.

## ⚙️ Configuration

First, install the project dependencies:

```bash
uv sync
```

Then, create a `.env` file in the project root with your API key:

```bash
# Create .env file
echo "API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual API key for the LLM provider you're using.

## 🏗️ Architecture Overview

This framework provides building blocks for creating custom AI agent workflows:

- **AgentManager** - Registry for managing agents and workers
- **BaseAgent** - Base class for creating custom agents
- **Workflow Nodes** - Reusable workflow components
- **WorkflowAgentFactory** - Pre-configured agent factory
- **Graphs** - Composable workflow definitions

## 🚀 Quick Start

### Basic Usage

```python
from app.agent.factories.workflow_factory import WorkflowAgentFactory
from app.agent.workflows.agent_workflow import user_assistant_graph
from app.agent.workflows.nodes import StartNode
from app.agent.workflows.generation_events import WorkflowState

# Create manager with all agents
manager = await WorkflowAgentFactory.create_manager()

# Run workflow
result = await user_assistant_graph.run(
    start_node=StartNode(),
    state=WorkflowState(),
    deps=manager.to_deps(
        message="Hello, how are you?",
        language="english"
    )
)

print(result.output)
```

## 🔧 Building Custom Solutions

### 1. Creating Custom Agents

Create custom agents by inheriting from `BaseAgent`:

```python
# app/agent/engines/my_custom_agent.py
from dataclasses import dataclass

from pydantic_ai import RunContext

from app.agent.engines.agent_base import BaseAgent, BaseAgentDeps

@dataclass
class MyAgentDeps(BaseAgentDeps):
    """Custom dependencies for your agent."""
    custom_param: str = "default_value"

class MyCustomAgent(BaseAgent):
    """Your custom agent with specific functionality."""
    
    def __init__(self, custom_setting: str = "default", **kwargs):
        self.custom_setting = custom_setting
        super().__init__(
            deps_type=MyAgentDeps,
            instructions="You are a specialized agent that...",
            **kwargs
        )
        
        @self.agent.instructions
        def add_custom_context(ctx: RunContext[MyAgentDeps]) -> str:
            return f"Use this custom parameter: {ctx.deps.custom_param}"
    
    async def process_request(self, query: str, custom_param: str) -> str:
        """Your custom processing logic."""
        deps = MyAgentDeps(language=self.language, custom_param=custom_param)
        result = await self.agent.run(user_prompt=query, deps=deps)
        return str(result.output)
```

### 2. Creating Workflow Nodes

Create nodes for your custom agents:

```python
# app/agent/workflows/nodes/my_custom_node.py
from dataclasses import dataclass

from pydantic_graph import BaseNode, GraphRunContext

from app.agent.workflows.generation_events import WorkflowState
from .next_node import NextNode  # Import next node

@dataclass
class MyCustomNode(BaseNode[WorkflowState, dict, str]):
    """Node that uses your custom agent."""
    
    async def run(self, ctx: GraphRunContext[WorkflowState, dict]) -> 'NextNode | End[str]':
        my_agent = ctx.deps['my_custom_agent']
        custom_param = ctx.deps.get('custom_param', 'default')
        
        result = await my_agent.process_request(
            ctx.state.current_message,
            custom_param
        )
        
        # Store result for next node or return directly
        ctx.state.generated_response = result
        return NextNode()  # or End(result) to finish workflow
```

### 3. Creating Custom Workflows

Build workflows using your custom nodes:

```python
# app/agent/workflows/my_custom_workflow.py
from pydantic_graph import Graph

from app.agent.workflows.nodes import StartNode, ClassifyNode
from app.agent.workflows.nodes.my_custom_node import MyCustomNode
from app.agent.workflows.nodes.guardrails import GuardrailsNode

my_custom_workflow = Graph(
    nodes=(StartNode, ClassifyNode, MyCustomNode, GuardrailsNode),
    name="MyCustomWorkflow"
)
```

### 4. Creating Custom Factories

Create factories for your specific use cases:

```python
# app/agent/factories/my_custom_factory.py
from app.agent.factories.workflow_factory import WorkflowAgentFactory
from app.agent.engines.my_custom_agent import MyCustomAgent

class MyCustomFactory:
    """Factory for your custom workflow."""
    
    @staticmethod
    async def create_manager(custom_setting: str = "default") -> AgentManager:
        # Start with base agents
        manager = await WorkflowAgentFactory.create_manager()
        
        # Add your custom agent
        manager.register('my_custom_agent', MyCustomAgent,
            custom_setting=custom_setting,
            verbose=True)
        
        await manager.initialize()
        return manager
```

### 5. Using Your Custom Solution

```python
# Your application code
from app.agent.factories.my_custom_factory import MyCustomFactory
from app.agent.workflows.my_custom_workflow import my_custom_workflow
from app.agent.workflows.nodes import StartNode
from app.agent.workflows.generation_events import WorkflowState

async def main():
    # Create manager with your custom agents
    manager = await MyCustomFactory.create_manager(custom_setting="my_value")
    
    # Run your custom workflow
    result = await my_custom_workflow.run(
        start_node=StartNode(),
        state=WorkflowState(),
        deps=manager.to_deps(
            message="Process this with my custom agent",
            language="english",
            custom_param="special_value"
        )
    )
    
    print(result.output)
```

## 📚 Available Building Blocks

### Pre-built Agents

- **GenericRouter** - Message classification and routing
- **ReasoningAgent** - Main conversational agent
- **OutputReformatterWorker** - Response formatting and validation
- **SimpleTranslatorWorker** - Text translation

### Pre-built Nodes

- **StartNode** - Workflow entry point
- **ClassifyNode** - Task classification
- **GenerateNode** - Response generation
- **TranslateNode** - Text translation
- **GuardrailsNode** - Response formatting
- **RefuseNode** - Refusal handling

### Pre-built Workflows

- **user_assistant_graph** - Complete chat workflow with all features

## 🛠️ Advanced Customization

### Adding Tools to Agents

```python
class MyAgentWithTools(BaseAgent):
    def __init__(self, **kwargs):
        # Define your tools
        tools = [
            # Add your custom tools here
        ]
        
        super().__init__(
            tool_list=tools,
            instructions="You have access to these tools...",
            **kwargs
        )
```

### Custom Prompts

```python
class MyAgentWithCustomPrompts(BaseAgent):
    def __init__(self, **kwargs):
        custom_instructions = """
        You are a specialized agent with specific instructions.
        Always follow these guidelines:
        1. Be helpful and accurate
        2. Use the provided tools when needed
        3. Respond in the requested language
        """
        
        super().__init__(
            instructions=custom_instructions,
            **kwargs
        )
```

### Custom Dependencies

```python
@dataclass
class MyComplexDeps(BaseAgentDeps):
    user_id: str
    session_data: dict
    custom_config: str = "default"

class MyComplexAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(
            deps_type=MyComplexDeps,
            **kwargs
        )
```

## 🚀 Examples

Check the `examples/` directory for complete working examples.

---

This project was generated from the [Python AI Kit](https://github.com/the-momentum/python-ai-kit).
