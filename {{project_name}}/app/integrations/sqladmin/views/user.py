from app.integrations.sqladmin.base_view import BaseAdminView
from app.user.models import User
from app.user.schemas import UserCreate, UserUpdate


class UserAdminView(
    BaseAdminView,
    model=User,
    create_schema=UserCreate,
    update_schema=UserUpdate
    # column={
    #     "searchable": ["username", "email"],
    #     "sortable": ["username", "email", "created_at", "updated_at"]
    # },
    # form={
    #     "create_rules": ["username", "email"],
    #     "edit_rules": ["username", "email"]
    # }
):
    pass

