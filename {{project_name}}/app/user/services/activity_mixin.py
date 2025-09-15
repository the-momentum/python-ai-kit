from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import Depends

from app.user.repositories import ActivityRepository
from app.utils.exceptions import handle_exceptions

if TYPE_CHECKING:
    from app.user.services import UserService

class ActivityMixin:
    def __init__(self, activity_repository: ActivityRepository = Depends(), **kwargs):
        self.activity_repository = activity_repository
        super().__init__(**kwargs)

    @handle_exceptions
    def is_user_active(self: "UserService", object_id: UUID) -> bool:
        self.logger.info(f"Checking if user with ID: {object_id} is active.")
        return self.activity_repository.is_user_active(object_id)