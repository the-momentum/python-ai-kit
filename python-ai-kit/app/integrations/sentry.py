from logging import Logger
from typing import Any, Literal

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from app.config import settings


def init_sentry() -> None:
    if settings.SENTRY_ENABLED:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENV,
            traces_sample_rate=settings.SENTRY_SAMPLES_RATE,
            integrations=[
                # Log records stay breadcrumbs only — `logger.error` never creates a Sentry event.
                # Report caught exceptions explicitly with `log_and_capture_error`.
                LoggingIntegration(event_level=None),
            ],
        )


def log_and_capture_error(
    exception: Exception,
    *,
    logger: Logger,
    message: str,
    level: Literal["debug", "info", "warning", "error", "critical"] = "error",
    extra: dict[str, Any] | None = None,
) -> None:
    """
    Log a caught exception and report it to Sentry.

    Use for exceptions that are handled gracefully (batch loops, task error returns)
    but must still be visible in monitoring. Don't use it when the exception is
    re-raised — it would be reported twice.

    Example:
        except Exception as error:
            log_and_capture_error(
                error, logger=logger, message=f"Failed {item.id}: {error}", extra={"item_id": item.id}
            )
            continue
    """
    log_func = getattr(logger, level)
    log_func(message, exc_info=exception)

    with sentry_sdk.new_scope() as scope:
        if extra:
            scope.set_context("extra", extra)
        sentry_sdk.capture_exception(exception)
