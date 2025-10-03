# MCP Server

This project provides a Model Context Protocol (MCP) server built with FastMCP, enabling seamless integration with AI assistants and language models.

## Overview

MCP (Model Context Protocol) is a standard for connecting AI assistants to external data sources and tools. This server implements MCP using FastMCP, a Python framework that simplifies MCP server development.

## Features

- **FastMCP Integration**: Built on FastMCP for easy tool and resource management
- **Modular Architecture**: Organized tool structure with separate modules
- **Type Safety**: Full Pydantic integration for robust data validation
- **Easy Extension**: Simple pattern for adding new tools and capabilities

## Project Structure

```
app/mcp/
├── __init__.py
├── mcp.py              # Main MCP router configuration
└── tools/
    ├── __init__.py
    └── hello.py        # Example tool implementation
```

## Getting Started

### Installation

```bash
# Install dependencies
uv sync
```

### Running the Server

```bash
# stdio transport
uv run fastmcp run app/main.py

# http transport
uv run fastmcp run app/main.py --transport http --port 8888
# choose any free port, default is 8000
```

### Adding New Tools

1. Create a new tool module in `app/mcp/tools/`
2. Define your tool using FastMCP decorators and add descriptive docstrings
3. Mount the tool router in `app/mcp/mcp.py`

Example tool implementation:

```python
from fastmcp import FastMCP

tool_router = FastMCP(name="My Tool")

@tool_router.tool
def my_tool(param: str) -> str:
    """Description of what this tool does."""
    return f"Result: {param}"
```

## Configuration

The server uses Pydantic settings for configuration. Key settings can be configured through environment variables or a `.env` file.

## Dependencies

- **FastMCP**: Core MCP framework
- **Pydantic**: Data validation and settings management

## Integration

This MCP server can be integrated with various AI assistants and language models that support the MCP protocol, providing them with access to your custom tools and data sources. **We suggest to use HTTP transport for AI agents integrations**.
