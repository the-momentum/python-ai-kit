from typing import Any, cast
from uuid import UUID

from app.database import AsyncDbSession, BaseDbModel
from app.utils.exceptions import MultipleResultsFoundError
from pydantic import BaseModel
from sqlalchemy import delete, select


class CrudRepository[
    ModelType: BaseDbModel,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
]:
    """Class to manage database operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def create(
        self, db_session: AsyncDbSession, creator: CreateSchemaType, commit: bool = True
    ) -> ModelType:
        creation_data = creator.model_dump()
        creation = self.model(**creation_data)
        db_session.add(creation)
        if commit:
            await db_session.commit()
            await db_session.refresh(creation)
        else:
            await db_session.flush()

        return creation

    async def create_many(
        self,
        db_session: AsyncDbSession,
        creators: list[CreateSchemaType],
        commit: bool = True,
    ) -> list[ModelType]:
        creations = [self.model(**creator.model_dump()) for creator in creators]
        db_session.add_all(creations)
        if commit:
            await db_session.commit()
            for creation in creations:
                await db_session.refresh(creation)
        else:
            await db_session.flush()

        return creations

    async def get(
        self, db_session: AsyncDbSession, object_id: UUID | int
    ) -> ModelType | None:
        stmt = select(self.model).where(getattr(self.model, "id") == object_id)

        result = await db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_from_ids(
        self,
        db_session: AsyncDbSession,
        ids_of_objects: list[UUID] | list[int],
    ) -> list[ModelType]:
        stmt = select(self.model).where(getattr(self.model, "id").in_(ids_of_objects))

        results = await db_session.execute(stmt)

        return cast(list[ModelType], results.scalars().all())

    async def get_all(
        self,
        db_session: AsyncDbSession,
        filters: dict[str, Any],
        offset: int | None = None,
        limit: int | None = None,
        sort_by: str | None = None,
        descending: bool = True,
    ) -> list[ModelType]:
        stmt = select(self.model)

        for field, value in filters.items():
            if value is not None:
                stmt = stmt.filter(getattr(self.model, field) == value)

        if sort_by:
            column = getattr(self.model, sort_by, None)
            if column:
                stmt = (
                    stmt.order_by(column.desc())
                    if descending
                    else stmt.order_by(column.asc())
                )

        if offset:
            stmt = stmt.offset(offset)

        if limit:
            stmt = stmt.limit(limit)

        results = await db_session.execute(stmt)

        return cast(list[ModelType], results.scalars().all())

    async def get_filtered_scalar(
        self,
        db_session: AsyncDbSession,
        filters: dict[str, Any],
    ) -> ModelType | None:
        results = await self.get_all(
            db_session=db_session, filters=filters, offset=None, limit=2, sort_by=None
        )
        if results:
            if len(results) == 1:
                return results[0]
            raise MultipleResultsFoundError(
                f"Found {len(results)} instances of {self.model} when only one was expected",
            )
        return None

    async def update(
        self,
        db_session: AsyncDbSession,
        originator: ModelType,
        updater: UpdateSchemaType,
        commit: bool = True,
    ) -> ModelType:
        updater_data = updater.model_dump(exclude_none=True)
        for field_name, field_value in updater_data.items():
            setattr(originator, field_name, field_value)

        db_session.add(originator)

        if commit:
            await db_session.commit()
            await db_session.refresh(originator)

        return originator

    async def delete(
        self,
        db_session: AsyncDbSession,
        originator: ModelType,
        commit: bool = True,
    ) -> ModelType:
        await db_session.delete(originator)
        if commit:
            await db_session.commit()
        return originator

    async def delete_many(
        self,
        db_session: AsyncDbSession,
        ids_of_objects: list[UUID] | list[int],
        commit: bool = True,
    ) -> int:
        """
        Delete multiple objects by their IDs.
        Returns the number of deleted rows.
        """
        stmt = delete(self.model).where(getattr(self.model, "id").in_(ids_of_objects))
        result = await db_session.execute(stmt)
        if commit:
            await db_session.commit()

        return result.rowcount or 0  # type: ignore
