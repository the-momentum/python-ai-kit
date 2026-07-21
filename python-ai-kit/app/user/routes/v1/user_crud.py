from typing import Annotated
from uuid import UUID

from app.config import settings
from app.database import AsyncDbSession
from app.schemas import FilterParams
from app.user.schemas import UserCreate, UserRead, UserUpdate
from app.user.services import user_service
from app.utils.api_utils import format_response
from fastapi import APIRouter, Query, Request, status

router = APIRouter()
user_rels = [
    {"rel": "test", "method": "GET", "endpoint": "/test"},
]


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@format_response(extra_rels=user_rels, status_code=status.HTTP_201_CREATED)
async def create_user(request: Request, user: UserCreate, session: AsyncDbSession):
    return await user_service.create(session, user)


@router.get("/{user_id}", response_model=UserRead)
@format_response(extra_rels=user_rels)
async def get_user(request: Request, user_id: UUID, session: AsyncDbSession):
    return await user_service.get(session, user_id)


@router.get("/", response_model=list[UserRead])
@format_response(extra_rels=user_rels)
async def get_users(
    request: Request,
    session: AsyncDbSession,
    # pagination
    page: Annotated[int, Query()] = 1,
    limit: Annotated[int, Query()] = settings.paging_limit,
    sort_by: Annotated[str | None, Query()] = None,
    # user-specific filters
    username: Annotated[str | None, Query(description="Filter by username")] = None,
    email: Annotated[str | None, Query(description="Filter by email")] = None,
    created_after: Annotated[
        str | None, Query(description="Filter by creation date (ISO format)")
    ] = None,
):
    filters = {}
    if username:
        filters["username"] = username
    if email:
        filters["email"] = email
    if created_after:
        filters["created_at"] = created_after

    filter_params = FilterParams(
        filters=filters, page=page, limit=limit, sort_by=sort_by
    )

    return await user_service.get_all(session, filter_params)


@router.put("/{user_id}", response_model=UserRead)
@format_response(extra_rels=user_rels)
async def update_user(
    request: Request, user_id: UUID, user: UserUpdate, session: AsyncDbSession
):
    return await user_service.update(session, user_id, user)


@router.delete("/{user_id}", response_model=UserRead)
@format_response(extra_rels=user_rels)
async def delete_user(request: Request, user_id: UUID, session: AsyncDbSession):
    return await user_service.delete(session, user_id)
