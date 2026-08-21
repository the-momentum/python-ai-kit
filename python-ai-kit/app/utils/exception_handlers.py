from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.utils.exceptions import AppError, AppErrorResponse, UnprocessableEntityError


def to_error_response(exc: AppError) -> JSONResponse:
    """Serialize an AppError to the one error body shape used across the API."""
    body = AppErrorResponse(message=exc.message, status_code=exc.status_code, errors=exc.errors)
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
        # jsonable_encoder is required here: pydantic puts raw exception objects in `ctx`.
        return to_error_response(
            UnprocessableEntityError(message="Request validation failed", errors={"fields": exc.errors()}),
        )
