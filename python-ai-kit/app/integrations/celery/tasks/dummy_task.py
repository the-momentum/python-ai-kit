import asyncio
import logging

from sqlalchemy import select

from app.database import adb_session_ctx, db_session_ctx
from celery import shared_task

log = logging.getLogger(__name__)


@shared_task
def dummy_task() -> None:
    log.info("Task performed")


@shared_task
def sync_db_task() -> int:
    """PREFERRED pattern — plain sync session, no event loop.

    Use `db_session_ctx()` (sync context manager over `SyncSessionLocal`) and
    build queries with SQLAlchemy 2.0 style: `select(...)` + `session.execute(...)`.
    No `await` anywhere. Commit with `session.commit()` when you write.
    """
    with db_session_ctx() as session:
        result = session.execute(select(1)).scalar_one()
        log.info("sync_db_task: db ping -> %s", result)
        return result


@shared_task
def async_wrapped_task() -> int:
    """FALLBACK pattern — reuse async services/repositories from a sync task.

    When the logic already lives in async code and duplicating it in sync is not
    worth it, drive the coroutine with `asyncio.run(...)`. Open the async session
    with `adb_session_ctx()` (NOT the FastAPI-injected `AsyncDbSession`).

    `asyncio.run` creates and tears down a fresh event loop per call — correct
    for a sync Celery worker, which has no running loop of its own.
    """

    async def _run() -> int:
        async with adb_session_ctx() as session:
            result = await session.execute(select(1))
            return result.scalar_one()

    ping = asyncio.run(_run())
    log.info("async_wrapped_task: db ping -> %s", ping)
    return ping
