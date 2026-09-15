from collections.abc import Callable
from functools import singledispatch, wraps
from inspect import iscoroutinefunction
from typing import Any, ParamSpec, TypeVar
from uuid import UUID

from psycopg.errors import IntegrityError as PsycopgIntegrityError
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError as SQLAIntegrityError

UNSAFE_VALIDATION_ERROR_TYPES = {"value_error", "assertion_error"}


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
        *,
        status_code: int | None = None,
        errors: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = type(self).status_code if status_code is None else status_code
        self.errors = errors
        self.headers = headers

    def __str__(self) -> str:
        return self.message


class AppErrorResponse(BaseModel):
    """JSON body for an `AppError` (also documents the error shape in OpenAPI).

    Headers and status code live on the HTTP response itself, not in the body, so they are
    intentionally omitted here.
    """

    message: str
    errors: dict[str, Any] | None = None


class ValidationErrorDetail(BaseModel):
    """Safe subset of pydantic's `ErrorDetails`: drops `input`/`ctx`, omits `msg` for unsafe error types."""

    type: str
    loc: tuple[int | str, ...]
    msg: str | None = None


class ValidationErrors(BaseModel):
    """`errors` payload of a 422."""

    fields: list[ValidationErrorDetail]


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


class MultipleResultsFoundError(AppError):
    """More rows matched than the single result expected — a data integrity problem, not a
    client mistake, hence 5xx. Its message names the model and row count, so it is logged
    rather than returned; see `to_error_response`.
    """

    status_code = 500

    def __init__(self, model: type, count: int) -> None:
        super().__init__(message=f"Found {count} instances of {model.__name__} when only one was expected")


VALIDATION_ERROR_RESPONSE: dict[int | str, dict[str, Any]] = {
    UnprocessableEntityError.status_code: {
        "model": ValidationErrorResponse,
        "description": UnprocessableEntityError.__doc__,
    },
}


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
def _(_: SQLAIntegrityError | PsycopgIntegrityError, entity: str) -> AppError:
    return BadRequestError(
        message=f"{entity.capitalize()} entity already exists.",
        errors={"code": "duplicate_entry"},
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
    if iscoroutinefunction(func):
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
