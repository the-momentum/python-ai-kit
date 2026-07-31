from contextlib import asynccontextmanager, contextmanager
from typing import Annotated, AsyncIterator, Iterator, TypedDict
from uuid import UUID

from fastapi import Depends
from sqlalchemy import UUID as SQL_UUID
from sqlalchemy import Engine, Text, create_engine, inspect
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    declared_attr,
    sessionmaker,
)

from app.config import settings
from app.utils.mappings_meta import AutoRelMeta


class BaseDbModel(DeclarativeBase, metaclass=AutoRelMeta):
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        return cls.__name__.lower()

    @property
    def id_str(self) -> str:
        return f"{inspect(self).identity[0]}"

    def __repr__(self) -> str:
        mapper = inspect(self.__class__)
        fields = [f"{col.key}={repr(getattr(self, col.key, None))}" for col in mapper.columns]
        return f"<{self.__class__.__name__}({', '.join(fields)})>"

    type_annotation_map = {
        str: Text,
        UUID: SQL_UUID,
    }


# TODO: export engine config to global settings
class DbEngineConfig(TypedDict):
    pool_pre_ping: bool
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int


db_engine_config: DbEngineConfig = {
    "pool_pre_ping": True,
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
}

async_engine = create_async_engine(settings.db_async_uri, **db_engine_config)
sync_engine = create_engine(settings.db_uri, **db_engine_config)


def _prepare_async_sessionmaker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


def _prepare_sessionmaker(engine: Engine) -> sessionmaker:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


AsyncSessionLocal = _prepare_async_sessionmaker(async_engine)
SyncSessionLocal = _prepare_sessionmaker(sync_engine)


async def _get_async_db_dependency() -> AsyncIterator[AsyncSession]:
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as exc:
        await session.rollback()
        raise exc
    finally:
        await session.close()


def _get_db_dependency() -> Iterator[Session]:
    session = SyncSessionLocal()
    try:
        yield session
    except Exception as exc:
        session.rollback()
        raise exc
    finally:
        session.close()


adb_session_ctx = asynccontextmanager(_get_async_db_dependency)
AsyncDbSession = Annotated[AsyncSession, Depends(_get_async_db_dependency)]

db_session_ctx = contextmanager(_get_db_dependency)
SyncDbSession = Annotated[Session, Depends(_get_db_dependency)]
