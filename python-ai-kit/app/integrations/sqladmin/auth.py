from functools import lru_cache

from app.config import settings
from fastapi import Request

from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # Validate username/password credentials
        if (
            username == settings.SQLADMIN_USER
            and password == settings.SQLADMIN_PASSWORD
        ):
            request.session.update({"token": settings.SQLADMIN_TOKEN})

            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        return token == settings.SQLADMIN_TOKEN


@lru_cache()
def _get_sqladmin_auth_backend() -> AdminAuth:
    return AdminAuth(secret_key=settings.SQLADMIN_SECRET_KEY)


admin_authentication_backend = _get_sqladmin_auth_backend()
