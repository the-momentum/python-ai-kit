from pydantic import BaseModel
from logging import Logger
from uuid import UUID

from app.database import AsyncDbSession, BaseDbModel
from app.repositories import CrudRepository
from app.schemas import FilterParams
from app.utils.exceptions import ResourceNotFoundError, handle_exceptions


class AppService[
    CrudModelType: CrudRepository,
    ModelType: BaseDbModel,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
]:
    """Class to prepare CrudRepository to being used by API views."""

    def __init__(
        self,
        crud_model: type[CrudModelType],
        model: type[ModelType],
        log: Logger,
        **kwargs,
    ):
        self.crud = crud_model(model)
        self.name = self.crud.model.__name__.lower()
        self.logger = log
        super().__init__(**kwargs)

    @handle_exceptions
    async def create(
        self, db_session: AsyncDbSession, creator: CreateSchemaType, commit: bool = True
    ) -> ModelType:
        creation = await self.crud.create(db_session, creator, commit=commit)
        self.logger.info("Created %s with ID: %s", self.name, creation.id)
        return creation

    @handle_exceptions
    async def create_many(
        self,
        db_session: AsyncDbSession,
        creators: list[CreateSchemaType],
        commit: bool = True,
    ) -> list[ModelType]:
        creations = await self.crud.create_many(db_session, creators, commit=commit)
        self.logger.debug(f"Created {len(creations)} {self.name}(s).")
        return creations

    @handle_exceptions
    async def get(
        self,
        db_session: AsyncDbSession,
        object_id: UUID | int,
        raise_404: bool = False,
        print_log: bool = True,
    ) -> ModelType | None:
        if not (fetched := await self.crud.get(db_session, object_id)) and raise_404:
            raise ResourceNotFoundError(self.name, object_id)

        if fetched and print_log:
            self.logger.info(f"Fetched {self.name} with ID: {fetched.id}.")
        elif not fetched:
            self.logger.info(f"{self.name} with ID: {object_id} not found.")

        return fetched

    @handle_exceptions
    async def get_from_ids(
        self,
        db_session: AsyncDbSession,
        ids_of_objects: list[UUID] | list[int],
        raise_404: bool = False,
        print_log: bool = True,
    ) -> list[ModelType]:
        if (
            not (
                fetched := await self.crud.get_from_ids(
                    db_session, ids_of_objects=ids_of_objects
                )
            )
            and raise_404
        ):
            raise ResourceNotFoundError(self.name)

        if fetched and print_log:
            self.logger.info(
                "Fetched %i objects of instance %s with IDs: %s",
                len(fetched),
                self.crud.model,
                ids_of_objects,
            )
        elif not fetched:
            self.logger.info(
                "Objects of instance %s with IDs: %s could not found",
                self.crud.model,
                ids_of_objects,
            )

        return fetched

    @handle_exceptions
    async def get_all(
        self,
        db_session: AsyncDbSession,
        filter_params: FilterParams,
        raise_404: bool = False,
    ) -> list[ModelType]:
        filter_params.validate_against_model(self.crud.model)

        offset = (filter_params.page - 1) * filter_params.limit

        fetched = await self.crud.get_all(
            db_session,
            filters=filter_params.filters,
            offset=offset,
            limit=filter_params.limit,
            sort_by=filter_params.sort_by,
            descending=filter_params.sort_order == "desc",
        )

        if not fetched and raise_404:
            raise ResourceNotFoundError(self.name)

        self.logger.info(
            f"Fetched {len(fetched)} {self.name}s. Filters: {filter_params.filters}."
        )

        return fetched

    @handle_exceptions
    async def update(
        self,
        db_session: AsyncDbSession,
        object_id: UUID | int,
        updater: UpdateSchemaType,
        raise_404: bool = False,
        commit: bool = True,
    ) -> ModelType | None:
        if originator := await self.get(
            db_session, object_id, print_log=False, raise_404=raise_404
        ):
            fetched = await self.crud.update(
                db_session, originator, updater, commit=commit
            )
            self.logger.info(f"Updated {self.name} with ID: {fetched.id}.")
            return fetched
        return None

    @handle_exceptions
    async def delete(
        self,
        db_session: AsyncDbSession,
        object_id: UUID | int,
        raise_404: bool = False,
        commit: bool = True,
    ) -> ModelType | None:
        if originator := await self.get(
            db_session, object_id, print_log=False, raise_404=raise_404
        ):
            deleted = await self.crud.delete(db_session, originator, commit=commit)
            self.logger.info(f"Deleted {self.name} with ID: {deleted.id}.")
            return deleted
        return None

    @handle_exceptions
    async def delete_many(
        self,
        db_session: AsyncDbSession,
        ids_of_objects: list[UUID] | list[int],
        batch_size: int = 50,
        commit: bool = True,
    ) -> int:
        if not ids_of_objects:
            return 0

        batches = [
            ids_of_objects[i : i + batch_size]
            for i in range(0, len(ids_of_objects), batch_size)
        ]

        sum_deleted = 0
        for batch in batches:
            num_deleted = await self.crud.delete_many(
                db_session=db_session, ids_of_objects=batch, commit=False
            )

            self.logger.info(
                "Deleted %i items of type %s with ids: %s. ",
                num_deleted,
                self.crud.model.__name__,
                batch,
            )

            sum_deleted += num_deleted

        if commit:
            await db_session.commit()

        return sum_deleted
