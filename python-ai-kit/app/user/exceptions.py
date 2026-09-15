from app.utils.exceptions import AppError


class UserInactiveError(AppError):
    """User has had no activity in the last 30 days."""

    status_code = 403

    def __init__(self) -> None:
        super().__init__(message="User is inactive", errors={"code": "user_inactive"})
