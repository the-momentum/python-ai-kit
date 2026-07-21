from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.database import AsyncDbSession
from app.user.models import User
from sqlalchemy import exists, select


class ActivityRepository:
    async def is_user_active(self, db_session: AsyncDbSession, object_id: UUID) -> bool:
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = select(
            exists().where(User.id == object_id).where(User.updated_at > cutoff)
        )
        return bool(await db_session.scalar(stmt))
