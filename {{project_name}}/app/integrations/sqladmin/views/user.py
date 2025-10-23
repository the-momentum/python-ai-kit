from app.integrations.sqladmin.base_view import BaseAdminView
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate


class UserAdminView(
    BaseAdminView,
    model=User,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    column={
        "searchable": ["username", "email"]
    }
):
    pass
