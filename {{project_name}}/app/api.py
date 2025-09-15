from fastapi import APIRouter

from app.user.routes import user_crud_router_v1
from app.utils.healthcheck import healthcheck_router

head_router = APIRouter()

head_router.include_router(healthcheck_router, prefix="/health", tags=["health"])
head_router.include_router(user_crud_router_v1, prefix="/users", tags=["users"])
