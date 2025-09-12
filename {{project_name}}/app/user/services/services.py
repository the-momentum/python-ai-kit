from logging import getLogger

from app.repositories import CrudRepository
from app.services import AppService
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate

from .activity_mixin import ActivityMixin

logger = getLogger(__name__)


class UserRepository(CrudRepository[User, UserCreate, UserUpdate]):
    pass


class UserService(AppService[UserRepository, User, UserCreate, UserUpdate], ActivityMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


user_service = UserService(UserRepository, User, logger)
