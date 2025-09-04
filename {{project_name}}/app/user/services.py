from logging import getLogger

from app.repositories import CrudRepository
from app.services import AppService
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate

logger = getLogger(__name__)


class UserRepository(CrudRepository[User, UserCreate, UserUpdate]):
    pass


class UserService(AppService[UserRepository, User, UserCreate, UserUpdate]):
    pass


user_service = UserService(UserRepository, User, logger)
