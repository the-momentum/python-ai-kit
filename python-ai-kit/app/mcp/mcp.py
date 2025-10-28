from fastmcp import FastMCP

from app.mcp.tools import hello

mcp_router = FastMCP(name="Main MCP")

mcp_router.mount(hello.hello_router)