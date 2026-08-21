from uuid import UUID

from app.utils.exceptions import AppError


class UserInactiveError(AppError):
    """User has had no activity in the last 30 days (403)."""

    status_code: int = 403

    def __init__(self, user_id: UUID) -> None:
        super().__init__(message=f"User {user_id} is inactive", status_code=self.status_code)
