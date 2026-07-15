
import mlflow

from app.config import settings


def init_tracing() -> None:
    """Enable MLflow tracing when configured."""
    if not settings.MLFLOW_TRACING_ENABLED:
        return

    mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(settings.MLFLOW_EXPERIMENT)
    mlflow.pydantic_ai.autolog()
