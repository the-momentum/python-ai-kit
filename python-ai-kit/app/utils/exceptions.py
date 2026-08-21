import asyncio
from collections.abc import Callable
from functools import singledispatch, wraps
from typing import Any, ParamSpec, TypeVar
from uuid import UUID

from psycopg.errors import IntegrityError as PsycopgIntegrityError
from pydantic import BaseModel
from pydantic_core import ErrorDetails
from sqlalchemy.exc import IntegrityError as SQLAIntegrityError


class AppError(Exception):
    """Base application error — presentation-ready: it carries its own HTTP status, optional
    field-level `errors`, and response `headers`.

    Every error this API returns is an AppError: domain modules subclass it, and
    `handle_exception` below converts infrastructure exceptions into it. A single handler
    (see `app/utils/exception_handlers.py`) serializes all of them to `AppErrorResponse`, so
    clients only ever parse one error shape.

    Subclasses with a fixed status only need to override the `status_code` class attribute.
    """

    status_code: int = 400

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        errors: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.errors = errors
        self.headers = headers

    def __str__(self) -> str:
        return self.message


class AppErrorResponse(BaseModel):
    """JSON body for an `AppError` (also documents the error shape in OpenAPI).

    Headers live on the HTTP response, not in the body, so they are intentionally omitted here.
    """

    message: str
    status_code: int
    errors: dict[str, Any] | None = None


class ValidationErrors(BaseModel):
    """`errors` payload of a 422 — pydantic's own report, passed through untouched."""

    fields: list[ErrorDetails]


class ValidationErrorResponse(AppErrorResponse):
    """422 body: the same envelope as any other error, with `errors` typed for OpenAPI."""

    errors: ValidationErrors


class BadRequestError(AppError):
    """Request cannot be fulfilled as sent."""

    status_code = 400


class NotFoundError(AppError):
    """Requested resource does not exist."""

    status_code = 404


class UnprocessableEntityError(AppError):
    """Request body or parameters failed validation."""

    status_code = 422


VALIDATION_ERROR_RESPONSE: dict[int | str, dict[str, Any]] = {
    UnprocessableEntityError.status_code: {
        "model": ValidationErrorResponse,
        "description": UnprocessableEntityError.__doc__,
    },
}


class MultipleResultsFoundError(Exception):
    pass


class ResourceNotFoundError(Exception):
    def __init__(self, entity_name: str, entity_id: int | UUID | None = None):
        self.entity_name = entity_name
        if entity_id:
            self.detail = f"{entity_name.capitalize()} with ID: {entity_id} not found."
        else:
            self.detail = f"{entity_name.capitalize()} not found."


@singledispatch
def handle_exception(exc: Exception, _: str) -> AppError:
    raise exc


@handle_exception.register
def _(exc: SQLAIntegrityError | PsycopgIntegrityError, entity: str) -> AppError:
    return BadRequestError(
        message=f"{entity.capitalize()} entity already exists.",
        errors={"detail": str(exc.args[0])},
    )


@handle_exception.register
def _(exc: ResourceNotFoundError, _: str) -> AppError:
    return NotFoundError(message=exc.detail)


@handle_exception.register
def _(exc: AttributeError, entity: str) -> AppError:
    return BadRequestError(
        message=f"{entity.capitalize()} doesn't support attribute or method.",
        errors={"detail": str(exc.args[0])},
    )


P = ParamSpec("P")
T = TypeVar("T")


def handle_exceptions(func: Callable[P, T]) -> Callable[P, T]:
    if asyncio.iscoroutinefunction(func):
        # async case
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as exc:
                entity_name = getattr(args[0], "name", "unknown") if args else "unknown"
                raise handle_exception(exc, entity_name) from exc

        return async_wrapper  # ty: ignore[invalid-return-type]

    @wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            entity_name = getattr(args[0], "name", "unknown") if args else "unknown"
            raise handle_exception(exc, entity_name) from exc

    return sync_wrapper
