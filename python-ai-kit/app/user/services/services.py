from logging import Logger, getLogger

from app.repositories import CrudRepository
from app.services import AppService
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate

from .activity_mixin import ActivityMixin

logger = getLogger(__name__)


class UserRepository(CrudRepository[User, UserCreate, UserUpdate]):
    pass


class UserService(AppService[UserRepository, User, UserCreate, UserUpdate], ActivityMixin):
    def __init__(
        self, 
        crud_model: type[UserRepository], 
        model: type[User], 
        log: Logger, 
        **kwargs
    ) -> None:
        super().__init__(crud_model, model, log, **kwargs)


user_service = UserService(UserRepository, User, logger)
