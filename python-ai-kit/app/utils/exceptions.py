import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from functools import singledispatch, wraps
from typing import Any, ParamSpec, TypeVar
from uuid import UUID

from fastapi.exceptions import HTTPException, RequestValidationError
from psycopg.errors import IntegrityError as PsycopgIntegrityError
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError as SQLAIntegrityError


@dataclass
class AppError(Exception):
    """Base application error — presentation-ready: it carries its own HTTP status, optional
    field-level `errors`, and response `headers`.

    Domain modules subclass this. It is serialized by the global `AppError` handler in
    `app/main.py`, NOT translated by `handle_exception` below — the default `handle_exception`
    simply re-raises unknown types, so an AppError raised inside a `@handle_exceptions`-wrapped
    service still propagates untouched to that global handler.
    """

    message: str
    status_code: int = 400
    errors: dict[str, Any] | None = None
    headers: dict[str, str] | None = None

    def __str__(self) -> str:
        return self.message


class AppErrorResponse(BaseModel):
    """JSON body for an `AppError` (also documents the error shape in OpenAPI).

    Headers live on the HTTP response, not in the body, so they are intentionally omitted here.
    """

    message: str
    status_code: int
    errors: dict[str, Any] | None = None


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
def handle_exception(exc: Exception, _: str) -> HTTPException:
    raise exc


@handle_exception.register
def _(exc: SQLAIntegrityError | PsycopgIntegrityError, entity: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=f"{entity.capitalize()} entity already exists. Details: {exc.args[0]}",
    )


@handle_exception.register
def _(exc: ResourceNotFoundError, _: str) -> HTTPException:
    return HTTPException(status_code=404, detail=exc.detail)


@handle_exception.register
def _(exc: AttributeError, entity: str) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=f"{entity.capitalize()} doesn't support attribute or method. Details: {exc.args[0]} ",
    )


@handle_exception.register
def _(exc: RequestValidationError, _: str) -> HTTPException:
    err_args = exc.args[0][0]
    return HTTPException(
        status_code=400,
        detail=f"{err_args['msg']} - {err_args['ctx']['error']}",
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
