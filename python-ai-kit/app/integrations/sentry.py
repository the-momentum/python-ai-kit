import sentry_sdk

from app.config import settings


def init_sentry() -> None:
    if settings.SENTRY_ENABLED:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENV,
            include_local_variables=False,
            traces_sample_rate=settings.SENTRY_SAMPLES_RATE,
        )
