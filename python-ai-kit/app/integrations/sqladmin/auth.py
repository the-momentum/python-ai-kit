import hashlib
import hmac
from datetime import datetime, timezone
from functools import lru_cache

from fastapi import Request
from pydantic import SecretStr

from sqladmin.authentication import AuthenticationBackend
from app.config import settings

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
            token, exp = self._generate_token_with_expiration()
            request.session.update({"token": token, "exp": exp})
            return True

        return False

    def _generate_token_with_expiration(
        self,
        expiration_time: float | None = None,
    ) -> tuple[str, float]:
        now_ts = datetime.now(timezone.utc).timestamp()
        exp = expiration_time or (now_ts + self.TOKEN_TTL)
        token = self._generate_token(str(exp))

        return token, exp

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        exp = request.session.get("exp")

        if not token or not exp:
            return False

        # check if token is expired
        if datetime.now(timezone.utc).timestamp() > exp:
            return False

        # compare tokens
        expected_token, _ = self._generate_token_with_expiration(expiration_time=exp)

        return hmac.compare_digest(token, expected_token)

    def _validate_credentials(self, username: str, password: str) -> bool:
        return self._are_admin_credentials_valid(username, password)

    def _generate_token(self, msg: str) -> str:
        return hmac.new(
            self._secret_key,
            msg.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _are_admin_credentials_valid(self, username: str, password: str) -> bool:
        is_valid_username: bool = hmac.compare_digest(
            username.encode(),
            settings.SQLADMIN_USER.encode(),
        )
        is_valid_password: bool = hmac.compare_digest(
            password.encode(),
            self.VALID_PASSWORD.encode(),
        )
        return is_valid_username and is_valid_password

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
