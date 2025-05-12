from typing import Type, Sequence

from sqlalchemy import select, func, join, tuple_

from bounded_contexts.pets_domain.entities import PetSight, Pet
from bounded_contexts.pets_domain.repositories.pets_sight_repository import (
    PetsSightRepository,
)
from infrastructure.uow_abstraction.unit_of_work_module import Session


class AlchemyPetsSightRepository(PetsSightRepository):
    def __init__(self) -> None:
        self.model: Type[PetSight] = PetSight
        self.pet_model: Type[Pet] = Pet

    async def add_pet_sight(self, session: Session, pet_sight: PetSight) -> None:
        session.add(pet_sight)
        await session.flush([pet_sight])

    async def get_pet_sight_by_id(
        self, session: Session, entity_id: str
    ) -> PetSight | None:
        query = select(self.model).where(
            self.model.entity_id == entity_id,  # type: ignore
        )

        result = await session.execute(query)
        return result.scalars().first()

    async def get_pet_sights(
        self,
        session: Session,
        limit: int | None = None,
        offset: int | None = 0,
        pet_id: str | None = None,
        lost: bool | None = None,
    ) -> Sequence[PetSight]:
        query = select(self.model).select_from(
            join(self.model, self.pet_model, self.model.pet_id == self.pet_model.entity_id)  # type: ignore
        )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        if pet_id:
            query = query.where(self.model.pet_id == pet_id)  # type: ignore

        if lost is not None:
            query = query.where(self.pet_model.lost == lost)  # type: ignore

        query = query.order_by(self.model.created_at)  # type: ignore

        result = await session.execute(query)
        return result.scalars().all()

    async def count_pet_sights(
        self, session: Session, pet_id: str | None = None, lost: bool | None = None
    ) -> int:
        query = (
            func.count()
            .select()
            .select_from(
                join(self.model, self.pet_model, self.model.pet_id == self.pet_model.entity_id)  # type: ignore
            )
        )

        if pet_id:
            query = query.where(self.model.pet_id == pet_id)  # type: ignore

        if lost is not None:
            query = query.where(self.pet_model.lost == lost)  # type: ignore

        result = await session.execute(query)
        return result.scalar()  # type: ignore

    async def get_most_recent_lost_pet_sights(
        self, session: Session, limit: int | None = None, offset: int | None = 0
    ) -> Sequence[PetSight]:
        subquery = select(
            self.model.pet_id,  # type: ignore
            func.max(self.model.created_at),  # type: ignore
        ).group_by(
            self.model.pet_id  # type: ignore
        )

        query = (
            select(self.model)
            .select_from(
                join(self.model, self.pet_model, self.model.pet_id == self.pet_model.entity_id)  # type: ignore
            )
            .where(
                tuple_(self.model.pet_id, self.model.created_at).in_(subquery),  # type: ignore
            )
            .filter(self.pet_model.lost.is_(True))  # type: ignore
            .order_by(self.model.created_at)  # type: ignore
        )

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        query = query.order_by(self.model.created_at)  # type: ignore

        result = await session.execute(query)

        # Get the most recent records per pet
        return result.scalars().all()

    async def count_most_recent_lost_pet_sights(self, session: Session) -> int:
        # Query to retrieve the most recent records per pet
        subquery = select(  # type: ignore
            self.model.pet_id,  # type: ignore
            func.max(self.model.created_at),  # type: ignore
        ).group_by(
            self.model.pet_id  # type: ignore
        )

        query = (
            func.count()
            .select()
            .select_from(
                join(self.model, self.pet_model, self.model.pet_id == self.pet_model.entity_id)  # type: ignore
            )
            .where(
                tuple_(self.model.pet_id, self.model.created_at).in_(subquery),  # type: ignore
            )
            .filter(self.pet_model.lost.is_(True))  # type: ignore
        )

        result = await session.execute(query)

        return result.scalar()  # type: ignore

    async def delete(self, session: Session, pet_sights: Sequence[PetSight]) -> None:
        for pet_sight in pet_sights:
            await session.delete(pet_sight)
        await session.flush()
