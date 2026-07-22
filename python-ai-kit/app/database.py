from contextlib import asynccontextmanager
from typing import Annotated, AsyncIterator
from uuid import UUID

from app.config import settings
from app.utils.mappings_meta import AutoRelMeta
from fastapi import Depends
from sqlalchemy import UUID as SQL_UUID
from sqlalchemy import Text, inspect
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
)


class BaseDbModel(DeclarativeBase, metaclass=AutoRelMeta):
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    @property
    def id_str(self) -> str:
        return f"{inspect(self).identity[0]}"

    def __repr__(self) -> str:
        mapper = inspect(self.__class__)
        fields = [
            f"{col.key}={repr(getattr(self, col.key, None))}" for col in mapper.columns
        ]
        return f"<{self.__class__.__name__}({', '.join(fields)})>"

    type_annotation_map = {
        str: Text,
        UUID: SQL_UUID,
    }


async_engine = create_async_engine(
    settings.db_async_uri,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
)


def _prepare_async_sessionmaker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(
        autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )


AsyncSessionLocal = _prepare_async_sessionmaker(async_engine)


async def _get_async_db_dependency() -> AsyncIterator[AsyncSession]:
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as exc:
        await session.rollback()
        raise exc
    finally:
        await session.close()


adb_session_ctx = asynccontextmanager(_get_async_db_dependency)
AsyncDbSession = Annotated[AsyncSession, Depends(_get_async_db_dependency)]
