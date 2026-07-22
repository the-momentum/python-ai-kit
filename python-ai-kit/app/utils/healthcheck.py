from app.database import AsyncDbSession, async_engine
from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.pool import QueuePool

healthcheck_router = APIRouter()


def get_pool_status() -> dict[str, str]:
    """Get connection pool status for monitoring."""
    pool = async_engine.pool
    if not isinstance(pool, QueuePool):
        return {"pool_type": type(pool).__name__}
    return {
        "max_pool_size": str(pool.size()),
        "connections_ready_for_reuse": str(pool.checkedin()),
        "active_connections": str(pool.checkedout()),
        "overflow": str(pool.overflow()),
    }


@healthcheck_router.get("/db")
async def database_health(db: AsyncDbSession) -> dict[str, str | dict[str, str]]:
    """Database health check endpoint."""
    try:
        # Test connection
        await db.execute(text("SELECT 1"))

        pool_status = get_pool_status()
        return {
            "status": "healthy",
            "pool": pool_status,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
        }
