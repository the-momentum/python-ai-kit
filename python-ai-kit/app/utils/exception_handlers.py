from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.exceptions import (
    UNSAFE_VALIDATION_ERROR_TYPES,
    AppError,
    AppErrorResponse,
    UnprocessableEntityError,
    ValidationErrorDetail,
)

logger = getLogger(__name__)

SERVER_ERROR_MESSAGE = "Internal server error"


def to_error_response(exc: AppError) -> JSONResponse:
    """Serialize an AppError to the one error body shape used across the API."""
    # 5xx detail may name tables or models, so it is logged (and picked up by Sentry) not returned.
    if exc.status_code >= 500:
        logger.error("Server error: %s", exc.message, exc_info=exc)
        body = AppErrorResponse(message=SERVER_ERROR_MESSAGE)
    else:
        body = AppErrorResponse(message=exc.message, errors=exc.errors)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(body, exclude_none=True),
        headers=exc.headers,
    )


def add_exception_handlers(api: FastAPI) -> None:
    """Register the handlers that give every API error the same JSON body."""

    @api.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        return to_error_response(exc)

    @api.exception_handler(RequestValidationError)
    async def request_validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            ValidationErrorDetail(
                type=error["type"],
                loc=error["loc"],
                msg=None if error["type"] in UNSAFE_VALIDATION_ERROR_TYPES else error["msg"],
            )
            for error in exc.errors()
        ]
        return to_error_response(
            UnprocessableEntityError(message="Request validation failed", errors={"fields": fields}),
        )
