import inspect
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

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

    pydantic_ai.Agent.__init__ = inspect.unwrap(pydantic_ai.Agent.__init__)
    pydantic_ai.Agent.instrument_all()


class _NoopSpan:
    """Stands in for a live span when tracing is disabled."""

    def set_outputs(self, outputs: Any) -> None:
        pass


@contextmanager
def trace_chat(message: str) -> Iterator[Any]:
    """Parent span grouping all agent runs of one request into a single trace.

    Records the user message as the trace request; call ``set_outputs`` on the
    yielded span to record the response. Without a parent span, every
    Agent.run() inside the workflow graph becomes its own root span, so one
    chat request shows up as several separate traces.
    """
    if not settings.MLFLOW_TRACING_ENABLED:
        yield _NoopSpan()
        return
    with mlflow.start_span("chat", span_type="CHAIN") as span:
        span.set_inputs({"message": message})
        yield span
