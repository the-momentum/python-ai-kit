from uuid import UUID

from sqlalchemy.orm import Mapped

from app.database import BaseDbModel, PrimaryKey, Unique, UniqueIndex, datetime_tz, email


class User(BaseDbModel):
    id: Mapped[PrimaryKey[UUID]]
    username: Mapped[UniqueIndex[str]]
    email: Mapped[Unique[email]]
    created_at: Mapped[datetime_tz]
    updated_at: Mapped[datetime_tz]
