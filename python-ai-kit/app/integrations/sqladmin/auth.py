from functools import lru_cache

from app.config import settings
from fastapi import Request
from pydantic import SecretStr

from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # Validate username/password credentials
        if username == settings.SQLADMIN_USER and password == self.VALID_PASSWORD:
            request.session.update({"token": self.TOKEN})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(
        self, request: Request
    ) -> bool:  # validates each incoming request
        token = request.session.get("token")
        return token == self.TOKEN

    @property
    def VALID_PASSWORD(self):
        if isinstance(settings.SQLADMIN_PASSWORD, SecretStr):
            return settings.SQLADMIN_PASSWORD.get_secret_value()
        return settings.SQLADMIN_PASSWORD

    @property
    def TOKEN(self):
        if isinstance(settings.SQLADMIN_TOKEN, SecretStr):
            return settings.SQLADMIN_TOKEN.get_secret_value()
        return settings.SQLADMIN_TOKEN


@lru_cache()
def _get_sqladmin_auth_backend() -> AdminAuth:
    if isinstance(settings.SQLADMIN_SECRET_KEY, SecretStr):
        secret = settings.SQLADMIN_SECRET_KEY.get_secret_value()
    else:
        secret = settings.SQLADMIN_SECRET_KEY

    return AdminAuth(secret_key=secret)


admin_authentication_backend = _get_sqladmin_auth_backend()
