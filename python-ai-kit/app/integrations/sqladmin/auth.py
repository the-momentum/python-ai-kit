import hashlib
import hmac
from datetime import datetime, timezone
from functools import lru_cache

from app.config import settings
from fastapi import Request
from pydantic import SecretStr

from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key)
        self._secret_key = (
            secret_key.encode() if isinstance(secret_key, str) else secret_key
        )

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if self._validate_credentials(str(username), str(password)):
            current_token = self._get_current_token()
            request.session.update({"token": current_token})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False

        current_token = self._get_current_token()

        return hmac.compare_digest(token, current_token)

    def _validate_credentials(self, username: str, password: str) -> bool:
        return username == settings.SQLADMIN_USER and password == self.VALID_PASSWORD

    def _get_current_token(self) -> str:
        current_time = datetime.now(timezone.utc)
        time_slot = self._get_time_slot(current_time)
        return self._generate_token(time_slot)

    def _generate_token(self, time_slot: str) -> str:
        return hmac.new(
            self._secret_key, time_slot.encode(), hashlib.sha256
        ).hexdigest()

    def _get_time_slot(self, dt: datetime) -> str:
        if self.TOKEN_TTL <= 0:
            return dt.isoformat()

        timestamp = int(dt.timestamp())
        slot_number = timestamp // self.TOKEN_TTL
        return str(slot_number)

    @property
    def VALID_PASSWORD(self) -> str:  # noqa: N802
        if isinstance(settings.SQLADMIN_PASSWORD, SecretStr):
            return settings.SQLADMIN_PASSWORD.get_secret_value()
        return settings.SQLADMIN_PASSWORD

    @property
    def TOKEN_TTL(self) -> int:  # noqa: N802
        ttl = getattr(settings, "SQLADMIN_TOKEN_TTL", 3600)
        if ttl < 0:
            ttl = 3600
        return ttl


@lru_cache()
def _get_sqladmin_auth_backend() -> AdminAuth:
    if isinstance(settings.SQLADMIN_SECRET_KEY, SecretStr):
        secret = settings.SQLADMIN_SECRET_KEY.get_secret_value()
    else:
        secret = settings.SQLADMIN_SECRET_KEY

    return AdminAuth(secret_key=secret)


admin_authentication_backend = _get_sqladmin_auth_backend()
