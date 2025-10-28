from uuid import UUID
from datetime import datetime, timedelta, timezone

from app.user.models import User
from app.database import DbSession

class ActivityRepository:
    def is_user_active(self, db_session: DbSession, object_id: UUID) -> bool:
        return db_session.query(User).filter(User.id == object_id).filter(User.updated_at > datetime.now(timezone.utc) - timedelta(days=30)).all()
