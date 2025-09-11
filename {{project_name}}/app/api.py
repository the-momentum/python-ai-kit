from fastapi import APIRouter

from app.user.views import router as user_router
from app.utils.healthcheck import healthcheck_router

head_router = APIRouter()

head_router.include_router(healthcheck_router, prefix="/health", tags=["health"])
head_router.include_router(user_router, prefix="/users", tags=["users"])
