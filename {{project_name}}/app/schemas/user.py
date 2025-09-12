from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import AwareDatetime, BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    username: str
    email: EmailStr
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserRead(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc), init=False)
