import inspect

import mlflow
import pydantic_ai
import pydantic_ai.mcp

from app.config import settings


def init_tracing() -> None:
    """Enable MLflow tracing when configured."""
    if not settings.MLFLOW_TRACING_ENABLED:
        return

    # mlflow (<= 3.14) instruments pydantic-ai v1; bridge the v2 API differences
    # below. Drop both workarounds once mlflow supports pydantic-ai v2 natively.

    # v1's MCPServer became MCPToolset in v2 (same call_tool/list_tools
    # interface). Alias it so MCP tool calls are traced and span types resolve
    # to LLM/AGENT/TOOL instead of UNKNOWN.
    if not hasattr(pydantic_ai.mcp, "MCPServer"):
        pydantic_ai.mcp.MCPServer = pydantic_ai.mcp.MCPToolset  # ty: ignore[unresolved-attribute]

    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT)
    mlflow.pydantic_ai.autolog()

    # autolog patches Agent.__init__ to inject instrument=True, a kwarg removed
    # in pydantic-ai v2 — every Agent(...) would raise TypeError. Undo that
    # patch and use v2's global switch, which has the same effect.
    pydantic_ai.Agent.__init__ = inspect.unwrap(pydantic_ai.Agent.__init__)
    pydantic_ai.Agent.instrument_all()
 