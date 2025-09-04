from collections.abc import Iterator
from datetime import datetime
from typing import Annotated, TypeVar

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import DateTime, Engine, String, create_engine, inspect
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    declared_attr,
    mapped_column,
    sessionmaker,
)

from app.config import settings

engine = create_engine(
    settings.db_uri,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
)

T = TypeVar("T")

Indexed = Annotated[T, mapped_column(index=True)]
PrimaryKey = Annotated[T, mapped_column(primary_key=True)]
Unique = Annotated[T, mapped_column(unique=True)]
UniqueIndex = Annotated[T, mapped_column(index=True, unique=True)]

type datetime_tz = Annotated[datetime, "datetime-timezone-aware"]
type email = Annotated[EmailStr, "email-validated"]


def _prepare_sessionmaker(engine: Engine) -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


class BaseDbModel(DeclarativeBase):
    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    @property
    def id_str(self) -> str:
        return f"{inspect(self).identity[0]}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id_str})>"

    type_annotation_map = {
        str: String,
        email: String,
        datetime_tz: DateTime(timezone=True),
    }


SessionLocal = _prepare_sessionmaker(engine)


def _get_db_dependency() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    except Exception as exc:
        db.rollback()
        raise exc
    finally:
        db.close()


DbSession = Annotated[Session, Depends(_get_db_dependency)]
